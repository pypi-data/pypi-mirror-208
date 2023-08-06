from datetime import datetime, timezone, timedelta
import os
import queue
import threading
import time
import json
import signal
import sys
import traceback
import argparse
import csv
import dbf
import pathlib


from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient, ASCENDING, DESCENDING

from mongo_client_gateway import MongoClientTradeGateway
from constants import (ENCODING, FILES, GATEWAY_NAME, Exchange, OrderStatus, OrderType, SecurityType, Side)
from utils import (decode_atx_status,side_to_target_type, decode_exchange_id, decode_atx_side, decode_ordtype)
from logger import Logger


try:
    import thread
except ImportError:
    import _thread as thread

LL9 = 1000000000


class atxServer(MongoClientTradeGateway):
    def __init__(self, config_filename, endtime):
        MongoClientTradeGateway.__init__(self, config_filename, endtime)

        self.load_tg_setting(config_filename)
        self.order_lock = threading.Lock()
        self.trade_lock = threading.Lock()
        self.pos_lock = threading.Lock()
        self.acc_lock = threading.Lock()
        

        self.order_row_set = set()
        self.trade_row_set = set()
        self.pos_row_set = set()
        self.acc_row_set = set()
        self.cancel_row_set = set()

        self.insert_orders = {}
        
        self.oid_to_ref = {}
        self.sids = []
        self.oid_to_traded = {}
        self.oid_to_traded_money = {}
        
        self.sid_to_req = {}
        self.oid_to_req = {}
        self.oid_to_sid = {}
        self.oid_to_acc = {}
        self.db_id_to_oid = {}
        self.ref_to_oid = {}
        
        self.order_index = -1 #dbf文件当前index
        self.trade_index = -1
        self.oid_to_local_ids = {}
        
    def monitor(self):
        self.thread_pool.submit(self.monitor_algo_order_insert)
        self.thread_pool.submit(self.monitor_cancel_order_insert)
        self.thread_pool.submit(self.monitor_order_update)
        self.thread_pool.submit(self.monitor_trade_update)
        self.thread_pool.submit(self.date_change)
        #self.thread_pool.submit(self.monitor_pos_update)
        #self.thread_pool.submit(self.monitor_acc_update)
        
    def load_tg_setting(self, config_filename):
        try:
            #config_filename = os.path.join(config_path, 'atx_server_config.json')
            f = open(config_filename, encoding='gbk')
            setting = json.load(f)
            #self.insert_order_path = setting['insert_order_path'].replace('/', '\\')
            self.recv_msg_dir = setting['recv_msg_path'].replace('/', '\\')
    
        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            print(f"load config failed! (exception){err}")
            exit(0)
    
    
    def init_dbf_tables(self):

        cancel_filename = self.recv_msg_dir + '\\' + FILES.CANCEL + self.date + '.dbf'
        self.cancel_order_table = dbf.Table(filename=cancel_filename,codepage='utf8', on_disk=True)
        self.cancel_order_table.open(mode=dbf.READ_WRITE)
        self.logger.info(f"[init_dbf_tables open] (filename){cancel_filename}")
        #not use
        pos_filename = self.recv_msg_dir + '\\' + FILES.POSITIONS + self.date + '.dbf'
        
        self.position_order_table = dbf.Table(filename=pos_filename,codepage='utf8', on_disk=True)
        self.position_order_table.open(mode=dbf.READ_WRITE)
        self.pos_index = -1
        self.logger.info(f"[init_dbf_tables open] (filename){pos_filename}")
    
    @MongoClientTradeGateway.error_handler
    def str2bool(self, v:str):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    
    @MongoClientTradeGateway.error_handler
    def req_buy_order_insert(self, obj):
        
        target_account_name = obj['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        account_id = self.account_id[acc]
        
        oid = str(self.gen_order_id())
        sid = str(obj['sid'])
        vol =  int(obj["volume"])
        basket_name = sid
        #order_vol = (str)(obj["volume"])
        finacial_buy_s = obj["financingBuy"]
        side = -1
        if finacial_buy_s == True:
            side = 5
        else:
            side = 1

        order_vol = f'{vol:d}'
        int_stock_code = int(obj['ticker'])
        stock_code = f'{int_stock_code:06d}'
        
        if stock_code.startswith('00'):
            stock_code += '.SZ'
        elif stock_code.startswith('6'):
            stock_code += '.SH'
        else:
            stock_code += '.SZ'

        #algo_type
        #algo_type = obj['executionPlan']["order_type"]
        #algo_type_using = 204
        algo_type = decode_ordtype(obj['executionPlan']["order_type"])
        begin_time  = self.date + str(obj['executionPlan']["start_time"]).replace(':','') + "000"

        end_time = self.date + str(obj['executionPlan']["end_time"]).replace(':','') + "000"
        
        ExternalId = oid
        LimAction = 0  #涨跌停后不交易
        AftAction = 0  #时间结束后不交易
        
        trade_param = f"basket_id={oid}"

        insert_row = (ExternalId, account_id, stock_code, side, order_vol, algo_type, begin_time, end_time, LimAction, AftAction, trade_param)
        #insert_row = (ExternalId, client_name, stock_code, side, order_vol, algo_type_using, begin_time, end_time, LimAction, AftAction, trade_param)
        self.insert_order_table.append(insert_row)
            
        self.logger.info(f"[req_buy_order] insert_success (oid){oid} (sid){sid} (param){insert_row}")
        db_id = obj['_id']
        order_dict = {
            'oid' : oid,
            'sid' : sid,
            "db_id" : db_id,
            "ticker" : obj['ticker'],
            "side" : side,
            "volume" : order_vol,
            "accountName" : target_account_name,
            "order_type" : str(obj['executionPlan']["order_type"]),
            "start_time" : str(obj['executionPlan']["start_time"]),
            "end_time" : str(obj['executionPlan']["end_time"])
        }
        
        target_collection =  self.order_info_db[acc]['target']
        delete_query = {
                    '_id' : db_id
                }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(f"[on_req_buy_order] delete (target){obj}")
        
        atx_order_collection = self.order_info_db[acc]['atx_order']
        local_id_list = []
        db_msg = {
                    "oid" : oid,
                    "sid" : sid,
                    "traded_vol" : 0,
                    "traded_amt" : 0,
                    "local_ids" : local_id_list,
                    "order_msg": order_dict
                }
        query = {"oid": oid}
        res = atx_order_collection.replace_one(query, db_msg, True)
        self.logger.info(f"[on_req_order_insert] insert_atx_order_info (res){res} (msg){db_msg}")

        self.sids.append(sid)

        self.sid_to_req[sid] = order_dict
        self.oid_to_req[oid] = order_dict
        self.oid_to_sid[oid] = sid
        self.db_id_to_oid[db_id] = oid
        self.oid_to_acc[oid] = acc
        self.oid_to_traded[oid] = 0
        self.oid_to_traded_money[oid] = 0
        self.oid_to_local_ids[oid] = local_id_list

    @MongoClientTradeGateway.error_handler
    def req_sell_order_insert(self, obj):
        target_account_name = obj['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        account_id = self.account_id[acc]

        oid = str(self.gen_order_id())
        sid = str(obj['sid'])
        vol =  int(obj["volume"])
        #order_vol = (str)(obj["volume"])
        #finacial_buy_s = self.str2bool(str(obj["financingBuy"]))
        side = 2

        order_vol = f'{vol:d}'
        int_stock_code = int(obj['ticker'])
        stock_code = f'{int_stock_code:06d}'

        if stock_code.startswith('00'):
            stock_code += '.SZ'
        elif stock_code.startswith('51'):
            stock_code += '.SH'
        elif stock_code.startswith('6'):
            stock_code += '.SH'
        else:
            stock_code += '.SZ'

        #algo_type
        #algo_type = obj['executionPlan']["order_type"]
        algo_type = decode_ordtype(obj['executionPlan']["order_type"]) 
        algo_type_using = 204  #ft vwap plus
        begin_time  = self.date + str(obj['executionPlan']["start_time"]).replace(':','') + "000"

        end_time = self.date + str(obj['executionPlan']["end_time"]).replace(':','') + "000"

        ExternalId = oid
        LimAction = 0  #涨跌停后不交易
        AftAction = 0  #时间结束后不交易
        
        trade_param = f"basket_id={oid}"
        
        insert_row = (ExternalId, account_id, stock_code, side, order_vol, algo_type, begin_time, end_time, LimAction, AftAction, trade_param)
        self.insert_order_table.append(insert_row)

        self.logger.info(f"[req_sell_order] insert_success (oid){oid} (sid){sid} (param){insert_row}")
        db_id = obj['_id']
        order_dict = {
            'oid' : oid,
            'sid' : sid,
            "db_id" : db_id,
            "ticker" : obj['ticker'],
            "trade_acc" : acc,
            "side" : side,
            "volume" : order_vol,
            "accountName" : target_account_name,
            "order_type" : str(obj['executionPlan']["order_type"]),
            "start_time" : str(obj['executionPlan']["start_time"]),
            "end_time" : str(obj['executionPlan']["end_time"])
        }

        target_collection =  self.order_info_db[acc]['sell_target']
        delete_query = {
                    "_id" : db_id
                }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(f"[on_req_sell_order] delete (target){obj}")

        atx_order_collection = self.order_info_db[acc]['atx_order']
        local_id_list = []
        db_msg = {
                    "oid" : oid,
                    "sid" : sid,
                    "traded_vol" : 0,
                    "traded_amt" : 0,
                    "local_ids" : local_id_list,
                    "order_msg": order_dict
                }
        query = {"oid": oid}
        res = atx_order_collection.replace_one(query, db_msg, True)
        self.logger.info(f"[on_req_order_insert] insert_sell_order_info (res){res} (msg){db_msg}")

        self.sids.append(sid)
        self.sid_to_req[sid] = order_dict
        self.oid_to_req[oid] = order_dict
        self.oid_to_sid[oid] = sid
        self.db_id_to_oid[db_id] = oid
        self.oid_to_acc[oid] = acc
        self.oid_to_traded[oid] = 0
        self.oid_to_traded_money[oid] = 0
        self.oid_to_local_ids[oid] = local_id_list

    #order_insert 和 rtn_order 都在此获取
    #0 已报 #2 filled 全成 #4 canceled #8 rejected
    @MongoClientTradeGateway.error_handler
    def monitor_order_update(self):
        print ("[monitor_order_update]")
        while not self.is_stopped:
            with self.order_lock:
                order_filename = self.recv_msg_dir + '\\' + FILES.ORDERS + self.date + '.dbf'
                rtn_order_table = dbf.Table(filename=order_filename,codepage='utf8', on_disk=True)
                rtn_order_table.open(mode=dbf.READ_WRITE)
                self.order_index = -1
                if self.order_index == len(rtn_order_table)-1 or len(rtn_order_table) == 0:
                    self.logger.info(f"[monitor_order_update] not_change (len){len(rtn_order_table)}")
                    time.sleep(10)
                    continue
                else:
                    while rtn_order_table[self.order_index+1] is not rtn_order_table.last_record:
                        self.order_index += 1
                        record = rtn_order_table[self.order_index]
                        if record.OrdStatus == 8:
                            self.logger.warn(f"[monitor_order_update] order_rejected! (msg){str(record.Text).strip(' ')}")
                            #self.logger.warn(f"[monitor_order_update] order_rejected!")
                        elif record.OrdStatus in [0,2,4]:
                            self.update_order(record)
                        else:
                            self.logger.info("[monitor_order_update] order_not_finished_or_not_init")

                    if rtn_order_table.last_record.OrdStatus in [0,2,4]:
                        self.order_index += 1
                        self.update_order(rtn_order_table.last_record)
                rtn_order_table.close()
            time.sleep(20)
    
    @MongoClientTradeGateway.error_handler
    def update_order(self,record):
        oid = str(record.ExternalId).strip(' ')
        acc = ""
        sid = ""
        order_dict = {}
        mudan_id = str(record.QuoteId).strip(' ')
        if not oid in self.oid_to_acc: #shut_down or other problem
            trade_acc = str(record.ClientName).strip(' ')
            if trade_acc not in self.account_id_to_acc:
                self.logger.error(f"[update_order] can't_parse_trade_acc {trade_acc}")
                return
            acc = self.account_id_to_acc[trade_acc]
            order_info_collection = self.order_info_db[acc]['atx_order']
            query = {'oid' : oid}
            order_info_target = order_info_collection.find_one(query)
            if not order_info_target is None:
                order_dict = order_info_target['order_msg']
                sid = order_info_target['sid']
                self.oid_to_traded_money[oid] = 0
                self.oid_to_traded[oid] = 0
                self.oid_to_sid[oid] = sid
                self.oid_to_req[oid] = sid
                self.oid_to_ref[oid] = mudan_id
            else:
                self.logger.error(f"[update_order] can't_find_oid (oid){oid}")
                return
        else:
            acc = self.oid_to_acc[oid]
            order_dict = self.oid_to_req[oid]
            sid = self.oid_to_sid[oid]
        ticker = record.Symbol.split('.')[0]
        exchange = decode_exchange_id(str(record.Symbol.split('.')[1]).strip(' '))
        volume = record.OrderQty
        price = record.AvgPx

        tg_name = order_dict['accountName'].split('@')[0]
        accountName = order_dict['accountName'].split('@')[1]
        order_type = order_dict['order_type']
        start_time = order_dict['start_time']
        end_time = order_dict['end_time']

        target_type = side_to_target_type(order_dict['side'])
        filled_vol = record.CumQty
        status = decode_atx_status(record.OrdStatus)
        
        str_update_time = str(int(int(record.UpdateTime)/1000))
        update_time = datetime.strptime(str_update_time, "%Y%m%d%H%M%S")
        utc_update_time = update_time - timedelta(hours=8)

        self.oid_to_ref[oid] = mudan_id
        order_msg = {
                "_id": oid,
                "tg_name": tg_name,  # 对应 account_info._id
                # 对应 tlclient.trader.constant 包 ExchangeID
                "exchange": exchange,
                "target_type": target_type,    # 'buy' | 'sell' | 'limit_sell'
                "volume": volume,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": order_type,  # algotype:200,目前没有其他的
                "ticker": ticker,
                "sid": sid,  # target中对应的 母单sid
                "accountName": accountName,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_type,  # 此柜台不使用下单时要求的算法
                    "start_time": start_time,
                    "end_time": end_time
                },
                "status": status,  # 'active' | 'filled' | 'canceled'
                "filled_vol": filled_vol,  # 实际成交的 volume
                "dbTime": utc_update_time,
        }
        replace_collection = self.tradelog_db[acc]['order']
        query = {'sid':sid, '_id':oid}
        res = replace_collection.replace_one(query, order_msg, True)
        self.logger.info(f"[rtn_order] (res){res} (order_msg){order_msg}")
       
    
    @MongoClientTradeGateway.error_handler
    def monitor_algo_order_insert(self):
        while not self.is_stopped:
            print ("[monitor_algo_order_insert]")
            with self.buy_orderlock:
                insert_filename = self.recv_msg_dir + '\\' + FILES.TASKS + self.date + '.dbf'
                self.insert_order_table = dbf.Table(filename=insert_filename,codepage='utf8', on_disk=True)
                self.insert_order_table.open(mode=dbf.READ_WRITE)
                self.logger.info(f"[init_dbf_tables open] (filename){insert_filename}")
                for acc in self.accounts_run:
                    target_accountname = self.target_account_names[acc]
                    buy_query = {"accountName": target_accountname}
                    buy_targets = self.order_info_db[acc]["target"].find(buy_query)
                    if buy_targets.count() == 0:
                        self.logger.warning(f"[monitor_buy_order] no_buy_target (acc){acc}")
                        continue
                    for target in buy_targets:
                        if target['_id'] not in self.order_dbids:
                            self.order_dbids.append(target['_id'])
                            self.req_buy_order_insert(target)
                        else:
                            self.logger.warning(f"[monitor_algo_order_insert] _id_existed (_id){target['_id']}")
                for acc in self.accounts_run:
                    target_accountname = self.target_account_names[acc]
                    sell_query = {"accountName": target_accountname}
                    sell_targets = self.order_info_db[acc]["sell_target"].find(sell_query)
                    if sell_targets.count() == 0:
                        self.logger.warning(
                            f"[monitor_sell_order] no_sell_target (acc){acc}")
                        continue
                    for sell_target in sell_targets:
                        if sell_target['_id'] not in self.sell_order_dbids:
                            self.sell_order_dbids.append(sell_target['_id'])
                            self.req_sell_order_insert(sell_target)
                        else:
                            self.logger.warning(f"[monitor_algo_order_insert] _id_existed (_id){sell_target['_id']}")
            time.sleep(self.scan_interval)
    
    @MongoClientTradeGateway.error_handler
    def monitor_cancel_order_insert(self):
        while not self.is_stopped:
                for acc in self.accounts_run:
                    print ("[monitor_cancel_order_insert]")
                    target_accountname = self.target_account_names[acc]
                    query = {"accountName": target_accountname}
                    with self.cancel_orderlock:
                        cancel_targets = self.order_info_db[acc]["cancel_target"].find(
                            query)
                        if cancel_targets.count() == 0:
                            self.logger.warning(
                                "[monitor_cancel_order] no_cancel_info")
                            continue
                        for cancel_target in cancel_targets:
                            if cancel_target['_id'] not in self.cancel_order_ids:
                                self.cancel_order_ids.append(cancel_target['_id'])
                                self.req_cancel_order(cancel_target)
                time.sleep(self.scan_interval)

    @MongoClientTradeGateway.error_handler
    def req_cancel_order(self, cancel_target):
        oid = str(cancel_target['oid'])
        mudan_id = ""
        if oid not in self.oid_to_ref:
           self.logger.error("[req_cancel_order] can't_find_mudanid (oid){oid}")
           return
        mudan_id = self.oid_to_ref[oid]
        cxltype = 1
        row = [mudan_id, cxltype]
        self.cancel_order_table.append(row)
        
        origin_req = self.oid_to_req[oid]
        target_account_name = origin_req['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        target_collection =  self.order_info_db[acc]['cancel_target']
        delete_query = {
            'accountName' : target_account_name,
            'oid' : oid
            }
        delete_res = target_collection.delete_one(delete_query)
        self.logger.info(f"[on_req_cancel_order] delete (target){cancel_target}")
    
    #得到的数据 类似于子单的rtn_order
    @MongoClientTradeGateway.error_handler
    def monitor_trade_update(self):
        while not self.is_stopped:
            with self.trade_lock:
                trade_filename = self.recv_msg_dir + '\\' + FILES.TRADES + self.date + '.dbf'

                rtn_trade_table = dbf.Table(filename=trade_filename,codepage='utf8', on_disk=True)
                rtn_trade_table.open(mode=dbf.READ_WRITE)
                self.trade_index = -1
                if self.trade_index == len(rtn_trade_table)-1 or len(rtn_trade_table) == 0:
                    self.logger.info(f"[monitor_trade_update] not_change (len){len(rtn_trade_table)}")
                    time.sleep(30)
                    continue
                else:
                    while rtn_trade_table[self.trade_index+1] is not rtn_trade_table.last_record:
                        self.trade_index += 1
                        record = rtn_trade_table[self.trade_index]
                        if record.OrdStatus in [2,4]: #only need filled/canceled
                            self.on_trade_msg(record)
                        else:
                            self.logger.info(f"[monitor_trade_update] traded_nofinished (msg){record.Text}")

                    self.trade_index += 1
                    record = rtn_trade_table[self.trade_index]
                    if record.OrdStatus in [2,4]: #only need filled/canceled
                        self.on_trade_msg(record)
                    else:
                        self.logger.info(f"[monitor_trade_update] traded_nofinished (msg){record.Text}")
                    

                rtn_trade_table.close()
            time.sleep(30)

    @MongoClientTradeGateway.error_handler
    def on_trade_msg(self, record):
        if record.CumQty == 0 or record.AvgPx == 0:
            self.logger.warning(f"[on_trade_msg] nothing_traded (record){record}")
            return
        oid = str(record.ExternalId).strip(' ')
        mudan_id = str(record.QuoteId).strip(' ')
        acc = ""
        sid = ""
        order_dict = {}
        if not oid in self.oid_to_acc: #shut_down or other problem
            trade_acc = str(record.ClientName).strip(' ')
            acc = self.account_id_to_acc[trade_acc]
            order_info_collection = self.order_info_db[acc]['atx_order']
            query = {'oid' : oid}
            order_info_target = order_info_collection.find_one(query)

            if not order_info_target is None:
                order_dict = order_info_target['order_msg']
                sid = order_info_target['sid']
                self.oid_to_local_ids[oid] = order_info_target['local_ids']
                self.oid_to_traded[oid] = 0
                self.oid_to_traded_money[oid] = 0
                self.oid_to_sid[oid] = sid
                self.oid_to_req[oid] = order_dict
                self.oid_to_ref[oid] = mudan_id
            else:
                self.logger.error(f"[on_trade_msg] can't_find_oid (oid){oid}")
                return
        else:
            acc = self.oid_to_acc[oid]
            order_dict = self.oid_to_req[oid]
            sid = self.oid_to_sid[oid]
        _id = str(record.ClOrdId).strip(' ')
        if _id in self.oid_to_local_ids[oid]:
            self.logger.warning(f"[on_trade_msg] duplicate_trade_msg (record){record}")
            return
        else:
            self.oid_to_local_ids[oid].append(_id)
        trade_ref = str(record.OrderId).strip(' ') #外部委托编号，出现在这个位置主要是凑数
        ticker = str(record.Symbol).split('.')[0]
        exchange = decode_exchange_id(str(record.Symbol).split('.')[1].strip(' '))
        traded_vol = record.CumQty
        traded_price = record.AvgPx
        trade_amt = float(traded_price * traded_vol)
        order_type = record.OrdType
        target_type = decode_atx_side(record.Side)
        if target_type == 1 or target_type == 3:
            self.oid_to_traded_money[oid] += trade_amt
            self.oid_to_traded[oid] += traded_vol
        elif target_type == 2:
            self.oid_to_traded_money[oid] -= trade_amt
            self.oid_to_traded[oid] -= traded_vol
        entrust_vol = record.OrderQty
        #entrust_price = record.Price
        entrust_price = float(str(record.Price).strip(' '))
        dbTime = datetime.now(timezone.utc)
        
        commission = 0
        str_trade_time = str(int(int(record.UpdateTime)/1000))
        trade_time = datetime.strptime(str_trade_time, "%Y%m%d%H%M%S")
        utc_trade_time = trade_time - timedelta(hours=8)
        target_account_name = order_dict['accountName']
        acc = self.target_account_names_to_acc[target_account_name]
        log_accountname = order_dict['accountName'].split('@')[1]
        tg_name =  order_dict['accountName'].split('@')[0]
        

        side = decode_atx_side(record.Side)

        db_msg = {
                    "trade_ref": _id, # 用的是非凸的子单order_id 经测试之前用的trade_ref 经常为空
                    "oid": oid,
                    "tg_name": tg_name,
                    "exchange": exchange,
                    "ticker": ticker,
                    "traded_vol": traded_vol,
                    "traded_price": traded_price,
                    "order_type": order_type,
                    "side": side,  # 对应 tlclient.trader.constant 包 Side
                    "entrust_vol": entrust_vol,
                    "entrust_price": entrust_price,
                    "dbTime": dbTime,
                    "sid": sid,  # 对应订单中的 sid
                    "commission": 0,  # 没有
                    "trade_time": utc_trade_time,  # 具体交易时间
                    "accountName":  log_accountname,  # 对应 account_info.account_name
                }
        trade_collection = self.tradelog_db[acc]['trade']
        replace_trade_query = { "trade_ref": _id, "oid" : oid, "sid": sid, "accountName": log_accountname}
        db_res = trade_collection.replace_one(replace_trade_query, db_msg, True)
        self.logger.info(
            f"[rtn_trade] (db_res){db_res} (db_msg){db_msg} (traded_vol){traded_vol} (traded_price){traded_price}")
        self.update_position(traded_vol, order_dict, sid, oid, side, trade_amt,exchange)

        atx_order_collection = self.order_info_db[acc]['atx_order']
        atx_order_msg = {
                    "local_ids" : self.oid_to_local_ids[oid],
                }
        update_atx_order_msg = {"$set": atx_order_msg}
        query = {"oid": oid}
        res = atx_order_collection.update_one(query, update_atx_order_msg)
        self.logger.info(f"[on_trade_msg] update_atx_order_info (res){res} (msg){update_atx_order_msg}")

    @MongoClientTradeGateway.error_handler
    def update_position(self, traded_vol, order, sid , oid, side, trade_amt, exchange):
        target_accountname = order['accountName']
        acc = self.target_account_names_to_acc[target_accountname]

        query = {'sid': sid, 'accountName': target_accountname}
        position_collection = self.order_info_db[acc]['EquityPosition']
        position = position_collection.find_one(query)
        if position == None and traded_vol > 0:
            if oid not in self.oid_to_req:
                self.logger.warning(
                    f"[update_position] can't_find_req (sid){sid} (oid){oid}")
                return
            if oid not in self.oid_to_traded:
                self.logger.error(f"[update_position]no trade_vol (sid){sid}")
                return
            td_trade_vol = self.oid_to_traded[oid]

            amt = self.oid_to_traded_money[oid]

            ticker = order['ticker']
            yd_pos = 0
            mkt_value = amt
            cost = 0
            if not td_trade_vol == 0:
                cost = amt / td_trade_vol
            update_time = datetime.now(timezone.utc)

            position_msg = {
                "ticker": ticker,
                "cost": cost,  # 成本价
                "td_pos_long": td_trade_vol,  # 今仓
                "yd_pos_long": yd_pos,  # 昨仓（可卖），挂止盈单后为0
                "td_pos_short": 0,
                "yd_pos_short": 0,
                "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                "actual_yd_pos_long": yd_pos,  # 实际的昨仓
                "enter_date": update_time,
                "holding_days": 0,  # 持仓时间（交易日累计）
                "mkt_value": mkt_value,  # 市值
                "exchange": exchange,# 对应 tlclient.trader.constant 包 ExchangeID
                "sid": sid,  # 我们策略生成的id，需要根据实际下单情况维护各sid的持仓。
                # 格式: {account_info.tg_name}@{account_info.account_name}
                "accountName": target_accountname,
                "update_date": update_time,
            }
            query2 = {'sid': sid,
                        'accountName': target_accountname}
            res = position_collection.replace_one(query2, position_msg, True)
            self.logger.info(
                f"[update_position] (res){res} (msg){position_msg}")
        else:
            if oid not in self.oid_to_req:
                self.logger.warning(
                    f"[update_position] can't_find_req (sid){sid}")
                return
            if oid not in self.oid_to_traded:
                self.logger.error(f"[update_position]no trade_vol (sid){sid}")
                return
            actual_yd_pos = position['actual_yd_pos_long']
            amt = trade_amt
            yd_pos = position['yd_pos_long']
            if side == 1 or side == 3:
                td_trade_vol = position['actual_td_pos_long'] + traded_vol
                mkt_value = position['mkt_value'] + amt
            elif side == 2 :
                td_trade_vol = position['actual_td_pos_long'] - traded_vol
                mkt_value = position['mkt_value'] - amt
                yd_pos = yd_pos - traded_vol

            ticker = order['ticker']

            cost = 0
            total_vol = td_trade_vol + yd_pos
            if not total_vol == 0:
                cost = mkt_value / total_vol
            update_time = datetime.now(timezone.utc)
            accountName = order['accountName']
            enter_time = position['enter_date']
            holding_days = position['holding_days']
            position_msg = {
                "ticker": ticker,
                "cost": cost,  # 成本价
                "td_pos_long": td_trade_vol,  # 今仓
                "yd_pos_long": yd_pos,  # 昨仓（可卖），挂止盈单后为0
                "td_pos_short": 0,
                "yd_pos_short": 0,
                "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                "actual_yd_pos_long": actual_yd_pos,  # 实际的昨仓
                "enter_date": enter_time,
                "holding_days": holding_days,  # 持仓时间（交易日累计）
                "mkt_value": mkt_value,  # 市值
                "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
                "sid": sid,  # 我们策略生成的id，需要根据实际下单情况维护各sid的持仓。
                # 格式: {account_info.tg_name}@{account_info.account_name}
                "accountName": accountName,
                "update_date": update_time,
            }
            query = {'sid': sid,
                        'accountName': accountName}
            res = position_collection.replace_one(query, position_msg, True)
            self.logger.info(
                f"[update_position] (res){res} (msg){position_msg}")

    def start(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        _msg = f"[atx_login] atx_server_start (time){datetime.now()}"
        self.send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        self.init_dbf_tables()
        self.monitor()

    def close(self):
        self.insert_order_table.close()
        self.position_order_table.close()
        self.cancel_order_table.close()
        return super().close()
    
    def join(self):
        while self.is_stopped == False:
            time.sleep(0.01)
            if self.is_stopped:
                self.logger.info(
                    "[close] main thread is stopped,active_orders message will lose")
                self.close()

if __name__ == "__main__":

    sys.stdout.reconfigure(encoding='utf-8')
    description = "atx_server,get target from mongodb and serve atx"  
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-e' , '--end_time', dest='end_time', default='15:30')
    _config_filename = "C:/Users/Administrator/Desktop/atx_batandconfig/atx_server_config.json"
    parser.add_argument('-p', '--config_filepath', dest= 'config_filepath', default= _config_filename)

    args = parser.parse_args()
    print (f"(args){args}")

    td = atxServer(args.config_filepath, args.end_time)
    td.start()

    td.join()