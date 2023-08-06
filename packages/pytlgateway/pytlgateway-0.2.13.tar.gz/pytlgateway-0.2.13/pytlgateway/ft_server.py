from datetime import datetime, timezone
import os
import queue
import threading
import time
import json
import requests
import signal
import sys
import traceback
import getopt
import argparse

from pymongo import MongoClient, ASCENDING, DESCENDING
from utils import decode_ft_flag, decode_exchange_id, send_to_user
from logger import Logger
# websocket-client

import websocket
from websocket import WebSocketApp, ABNF



try:
    import thread
except ImportError:
    import _thread as thread

LL9 = 1000000000


class FtServer(object):
    
    def __init__(self, config_filename, endtime):
        self.load_ft_setting(config_filename)
        super(FtServer, self).__init__()
        self.logger = Logger.get_logger(self.logname, self.log_file_path)
        self.gen_local_id()
        self.reconnect_count = 0
        self.ws = None
        self.endtime = endtime

        try:
            self.db_client = {}
            self.order_info_db = {}
            self.tradelog_db = {}
            for acc in self.accounts_run:
                self.db_client[acc] = MongoClient(
                    self.mongo_host[acc], self.mongo_port[acc], connectTimeoutMS=10000)
                db_client = self.db_client[acc]
                if self.tradingaccount_user[acc] != '' and self.tradingaccount_pwd[acc] != '':
                    db_client["tradingAccount"].authenticate(
                        self.tradingaccount_user[acc], self.tradingaccount_pwd[acc], mechanism='SCRAM-SHA-1')
                self.order_info_db[acc] = db_client["tradingAccount"]
                
                if self.tradinglog_user[acc] != '' and self.tradinglog_pwd[acc] != '':
                    db_client["tradingLog"].authenticate(
                        self.tradinglog_user[acc], self.tradinglog_pwd[acc], mechanism='SCRAM-SHA-1')
                db_client.server_info()
                self.tradelog_db[acc] = db_client["tradingLog"] 

        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list,msg=err)
            self.logger.error(f'[init] DB_connect_failed! (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            exit()

        
        #test for req_position
        self.db_client_test = MongoClient("127.0.0.1", 27017, connectTimeoutMS=10000)
        self.test_trading_account = self.db_client_test['tradingAccount']

        self.get_account_info()

        self.buy_orderlock = threading.Lock()
        self.sell_orderlock = threading.Lock()
        self.cancel_orderlock = threading.Lock()
        self.buy_order_dbids = []
        self.sell_order_dbids = []
        self.cancel_order_dbids = []
        self.sids = []
        self.cancel_order_ids = []
        self.broker_id = {}
        # db_id: 数据库的_id,
        # sid：算法单的母单id
        # oid: 生成的oid,唯一对应每个下单成功的order
        # ref 返回的data id

        self.sid_to_traded = {}
        self.oid_to_traded = {}
        self.oid_to_traded_money = {}

        self.db_id_to_oid = {}
        self.oid_to_sid = {}
        # self.sid_to_oid = {} sid可对应多个oid

        self.oid_to_ref = {}
        self.ref_to_oid = {}

        self.sid_to_req = {}
        self.oid_to_req = {}

        self.token = ""
        self.date_change_token = True

        self.is_stopped = False

    def load_ft_setting(self, config_filename):
        try:
            #f = open(config_filename, encoding="utf-8")
            f = open(config_filename, encoding='gbk')
            setting = json.load(f)

            self.socket_url = setting['websocket_url']
            self.login_url = setting['login_url']
            path = setting['log_filepath']
            self.log_file_path = path.replace('/', '\\')
            self.ft_tradecsv_path = setting['ft_tradecsv_path'].replace('/', '\\')
            self.upload_mudan_url = setting['upload_mudan_url']
            self.url_list = setting.get('url_list')
            self.cancel_url = setting['cancel_url']
            # self.log_accountname = setting['ACCOUNT_NAME'] #用于tradinglog数据库,order/trade
            # 产品名称，用于获取tg_name和account_name
            self.req_position_open = setting['req_position_open'] #设置同步持仓的时间
            self.req_position_close = setting['req_position_close']
            #self.tgname = setting['tg_name']
            # self.target_accountname = self.tgname + '@' + self.log_accountname #下单时用

            self.logname = setting['logname']
            self.scan_interval = setting['scan_interval']

            #get config by product
            self.accounts_config = setting['accounts']
            self.accounts_run = setting['run'] #0 zhongxincats1 1 huaxin ...

            self.config = {}
            self.account_id = {}
            self.product_names = {}
            self.log_account_names = {}
            self.tgnames = {}
            self.mongo_host = {}
            self.mongo_port = {}
            self.tradingaccount_user = {}
            self.tradingaccount_pwd = {}
            self.tradinglog_user = {}
            self.tradinglog_pwd = {}
            self.target_account_names = {}
            self.target_account_names_to_acc = {}
            for acc in self.accounts_run:
                self.config[acc] = setting['accounts'][acc]
                config = self.config[acc]
                self.account_id[acc] = config['account_id']
                self.product_names[acc] = config['product_name']
                self.log_account_names[acc] = config['account_name']
                self.tgnames[acc] = config['equity_tg_name']
                self.target_account_names[acc] = config['equity_tg_name'] + "@" + config['account_name']
                self.target_account_names_to_acc[self.target_account_names[acc]] = acc
                self.mongo_host[acc] = config['mongoHost']
                self.mongo_port[acc] = config['mongoPort']
                datadbuser = config['databaseUser']
                self.tradingaccount_user[acc] = datadbuser['tradingAccount']['user']
                self.tradingaccount_pwd[acc] = datadbuser['tradingAccount']['password']
                self.tradinglog_user[acc] = datadbuser['tradingLog']['user']
                self.tradinglog_pwd[acc] = datadbuser['tradingLog']['password']
            
        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            print(f"load config failed! (exception){err}")
            exit(0)

    #not use
    def get_account_info(self):
        for acc in self.accounts_run:
            product_name = self.product_names[acc]
            query = {"product_name": product_name}
            account_info_collection = self.order_info_db[acc]['account_info']
            account_info = account_info_collection.find_one(query)
            if account_info == None:
                self.logger.error(
                    f"[get_account_info] can't_find_account_info (product_name){product_name}")
                continue
            tgname = account_info['equity_tg_name']
            self.tgnames[acc] = tgname
            log_accountname = account_info['account_name']
            self.log_account_names[acc] = log_accountname
            target_accountname = tgname + '@' + log_accountname
            self.target_account_names[acc] = target_accountname # 下单时用self
            self.logger.info(
                f"[get_account_info] (tg_name){self.tgnames} (logacc_name){self.log_account_names} (target_accountnames){self.target_account_names}")
            
    def date_change(self):
        try:
            while not self.is_stopped:
                time_now = datetime.now()
                req_position_count = 1
                _dt_endtime = datetime.strptime(self.endtime, "%H:%M")
                dt_endtime = datetime.combine(time_now, _dt_endtime.time())
                if time_now > dt_endtime:
                    self.req_position()
                    msg = f"[date_change] close (now){time_now}"
                    send_to_user(logger=self.logger, url_list=self.url_list,msg=msg)
                    self.ft_close()
                else:
                    req_position_count += 1
                    if req_position_count % 60 == 0:
                        self.req_position()
                    self.logger.info(f"[date_change] not_closed (now){time_now}")
                time.sleep(60)
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list,msg=err)
            self.logger.error(f'[date_change] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    
    def ft_close(self):
        self.is_stopped = True
        self.ws.close()
        print (f"[ft_close] (close_time){self.endtime}")
        self.logger.info(f"[ft_close] (close_time){self.endtime}")

        msg= f"[ft_close] (close_time){self.endtime}"
        send_to_user(logger=self.logger, url_list=self.url_list,msg=msg)

        os._exit(0)

    def req_position(self):
        try:
            for acc in self.accounts_run:
                target_account_name = self.target_account_names[acc]
                account_id = self.account_id[acc]
                product_name = self.product_names[acc]
                broker_id = self.broker_id[account_id]
                url = f'http://127.0.0.1:11356/api/get_position_by_acc?broker_id={broker_id}&acc_id={account_id}&token={self.token}'
                r = requests.get(url)
                data = r.json()
                self.logger.info(f"[req_position] (url){url} (data){data}")
                #将持仓结果计入ft_position数据库
                if data['code'] == 0:
                    if len(data['data']) > 0:
                        ft_position_collection = self.order_info_db[acc]['ft_position']
                        remove = ft_position_collection.delete_many({'trade_acc': account_id})
                        self.logger.info(f"[req_position] delete_old_position_info (remove){remove} ")
                        for pos in data['data']:
                            trade_acc = pos['trade_acc']
                            ticker = pos['stock_code']
                            total_vol = pos['total_vol']
                            avail_vol = pos['avail_vol']
                            lock_vol = pos['lock_vol']
                            exchange = decode_exchange_id(pos['exchange_id']) 
                            position_db_msg = {
                                'trade_acc' : trade_acc,
                                'ticker' : ticker,
                                'total_vol' : total_vol,
                                'avail_vol' : avail_vol,
                                'lock_vol' : lock_vol,
                                'update_time' : datetime.now(timezone.utc),
                                'exchange' : exchange,
                                'target_account_name': target_account_name
                            }
                            query = {'ticker' : ticker, 'trade_acc' : trade_acc, 'target_account_name' : target_account_name}
                            res = ft_position_collection.replace_one(query, position_db_msg, True)
                            self.logger.info(f"[req_position] save_position_info (res){res} (position_db_msg){position_db_msg}")
                else:
                    self.logger.error(f"[req_position] failed (error_msg){data}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list,msg=err)
            self.logger.error(f'[req_position] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    # webserver

    def on_message(self, ws, message):
        try:
            self.logger.info(f'[on_message] (msg){message}')
            data = json.loads(message)
            if (data['topic'] == 'Ping'):
                self.pong(data)
            elif (data['topic'] == 'Zidan'):
                self.on_zidan_message(data)
            elif (data['topic'] == 'Mudan'):
                self.on_mudan_message(data)
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list,msg=err)
            self.logger.error(f'[on_message] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def pong(self, data):
        text = {"topic": "Pong", "data": int(data["data"])}
        _text = json.dumps(text)
        self.ws.send(_text)
        self.logger.info(f"[on_ping] send (pong){_text}")

    #rtn_trade, 如果trade_vol等于entrust_vol, 再update_order_filled
    def on_zidan_message(self, data):
        '''
        enum status:
        子单状态 0:初始化 未完成 1:报单插入柜台成功 2:部成 3:部撤 4:全成  5:全撤 6:错单 7废单 
        '''

        try:
            msg = data['data']
            if msg['status'] > 5:  # 错/废单
                self.logger.error(
                    f"[on_zidan_message] error (ec){msg['status']} (errmsg){msg['status_msg']}")
                return
            elif msg['status'] == 5:  # 撤单
                self.logger.warning(
                    f"[on_zidan_message] canceled (ec){msg['status']} (errormsg){msg['status_msg']}")
                return
            elif msg['status'] <= 2:
                self.logger.info(f"[on_zidan_message] not_finished (msg){msg}")
                return
            elif msg['status'] == 4 or msg['status'] == 3:  # 只关注子单全成/部撤
                ref = msg['strategy_order_id']
                if ref not in self.ref_to_oid:
                    self.logger.warning(
                        f"[on_zidan_message] can'tfind_oid (data){data}")
                    return
                oid = self.ref_to_oid[ref]

                if oid not in self.oid_to_sid:
                    self.logger.warning(
                        f"[on_zidan_message] can'tfind_sid (data){data}")
                    return
                sid = self.oid_to_sid[oid]

                if oid not in self.oid_to_req:
                    self.logger.warning(
                        f"[on_zidan_message] can'tfind_req (sid){sid}")
                    return
                order = self.oid_to_req[oid]
                target_account_name = order['target_account_name']
                acc = self.target_account_names_to_acc[target_account_name]
                #self.logger.info(f"[on_zidan_message] before_side_defination")
                target_type = order['bs_flag']
                #self.logger.info(f"[on_zidan_message] after_side_defination")
                # 计算订单成交量
                if sid not in self.sid_to_traded:
                    if target_type == 'buy':
                        self.sid_to_traded[sid] = msg['trade_vol']
                    elif target_type == 'sell':
                        self.sid_to_traded[sid] = 0
                        self.sid_to_traded[sid] -= msg['trade_vol']
                elif target_type == 'buy':
                    self.sid_to_traded[sid] += msg['trade_vol']
                elif target_type == 'sell':
                    self.sid_to_traded[sid] -= msg['trade_vol']

                if oid not in self.oid_to_traded:
                    if target_type == 'buy':
                        self.oid_to_traded[oid] = msg['trade_vol']
                    elif target_type == 'sell':
                        self.oid_to_traded[oid] = 0
                        self.oid_to_traded[oid] -= msg['trade_vol']
                elif target_type == 'buy':
                    self.oid_to_traded[oid] += msg['trade_vol']
                elif target_type == 'sell':
                    self.oid_to_traded[oid] -= msg['trade_vol']
                # 计算成交总价
                amt = msg['trade_vol'] * msg['trade_price']


                if oid not in self.oid_to_traded_money:
                    if target_type == 'buy':
                        self.oid_to_traded_money[oid] = amt
                    elif target_type == 'sell':
                        self.oid_to_traded_money[oid] -= amt
                elif target_type == 'buy':
                    self.oid_to_traded_money[oid] += amt
                elif target_type == 'sell':
                    self.oid_to_traded_money[oid] -= amt

                ms = int(msg['update_tm'] / 1000) % 1000
                update_tm = float(msg['update_tm'] / 1000)
                local_id = msg['local_id']
                trade_time = datetime.utcfromtimestamp(update_tm)

                trade_ref = local_id
                order_info_collection = self.order_info_db[acc]['ft_order']
                query = {"oid": oid}
                update_target = order_info_collection.find_one(query)
                if not update_target == None:
                    local_ids = []
                    local_ids = update_target['local_ids']
                    if local_id in local_ids:
                        self.logger.warning(f"[rtn_trade] local_id duplicated! (msg){msg}")
                        return
                    local_ids.append(local_id)
                    new_data = {
                        'local_ids' : local_ids,
                        "traded_vol" : self.oid_to_traded[oid],
                        "traded_amt" : self.oid_to_traded_money[oid]
                    }
                    new_data_for_update =  {"$set": new_data}
                    res = order_info_collection.update_one(query, new_data_for_update)
                    self.logger.info(f"[zidan_message] update_ft_order (res){res} (local_ids){local_ids}")
                else:
                    self.logger.warning(f"[on_zidan_message] update_target_not_exist (oid){oid}")
                
                exchange = decode_exchange_id(msg['exchange_id'])
                self.oid_to_req[oid]['exchange_id'] = exchange
                ticker = msg['stock_code']
                trade_vol = msg['trade_vol']
                traded_price = msg['trade_price']
                db_side = msg['bs_flag']
                entrust_vol = int(order['order_vol'])
                log_accountname = order['log_accountname']

                tg_name = self.tgnames[acc]
                db_msg = {
                    "trade_ref": trade_ref,  # broker 端的交易回报 id
                    "oid": oid,
                    "tg_name": tg_name,
                    "exchange": exchange,
                    "ticker": ticker,
                    "traded_vol": trade_vol,
                    "traded_price": traded_price,
                    "order_type": 215,
                    "side": db_side,  # 对应 tlclient.trader.constant 包 Side
                    "entrust_vol": entrust_vol,
                    "entrust_price": 0,  # 算法单没有
                    "dbTime": datetime.now(timezone.utc),
                    "sid": sid,  # 对应订单中的 sid
                    "commission": 0,  # 没有
                    "trade_time": trade_time,  # 具体交易时间
                    "accountName":  log_accountname,  # 对应 account_info.account_name
                }
                #db_msg_json = json.dumps(db_msg)
                trade_collection = self.tradelog_db[acc]['trade']
                db_res = trade_collection.insert_one(db_msg)
                self.logger.info(
                    f"[rtn_trade] (db_res){db_res} (db_msg){db_msg} (traded_vol){trade_vol} (traded_price){traded_price}")
                # 更新持仓
                self.update_position(msg, order, sid, oid, db_side, amt)

                if (abs(self.oid_to_traded[oid]) == entrust_vol):
                    self.update_order_filled(msg, sid, oid)

                ft_trade_collection = self.order_info_db[acc]['ft_trade']
                trade_db_msg = {
                    "oid" : oid,
                    "exchange_id" : msg['exchange_id'],
                    "ticker": ticker,
                    "traded_vol": trade_vol,
                    "traded_price": traded_price,
                    "entrust_vol": entrust_vol,
                    "sid" : sid,
                    "order_type": 215,
                    "side": db_side,
                    "local_id" : local_id,
                    "mudan_id" : ref,
                    "update_tm" : msg['update_tm']
                }
                ft_trade_query = {"local_id": local_id}
                res = ft_trade_collection.replace_one(ft_trade_query, trade_db_msg, True)
                self.logger.info(f"[zidan_message] update_ft_trade (res){res} (local_id){local_id}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list,msg=err)
            self.logger.error(f'[on_zidan_message] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)


    def update_position(self, msg, order, sid , oid, side, trade_amt):
        try:
            target_accountname = order['target_account_name']
            acc = self.target_account_names_to_acc[target_accountname]
            query = {'sid': sid, 'accountName': target_accountname}
            position_collection = self.order_info_db[acc]['EquityPosition']
            position = position_collection.find_one(query)
            if position == None and msg['trade_vol'] > 0:
                if oid not in self.oid_to_req:
                    self.logger.warning(
                        f"[update_position] can't_find_req (sid){sid} (oid){oid}")
                    return
                if oid not in self.oid_to_traded:
                    self.logger.error(f"[update_position]no trade_vol (sid){sid}")
                    return
                td_trade_vol = self.oid_to_traded[oid]

                amt = self.oid_to_traded_money[oid]

                ticker = order['stock_code']
                yd_pos = 0
                mkt_value = amt
                cost = amt / td_trade_vol
                update_time = datetime.now(timezone.utc)
                exchange = order['exchange_id']

                position_msg = {
                    "ticker": ticker,
                    "cost": cost,  # 成本价
                    "td_pos_long": td_trade_vol,  # 今仓
                    "yd_pos_long": yd_pos,  # 昨仓（可卖），挂止盈单后为0, use yd_pos_long 作为可卖
                    "td_pos_short": 0,
                    "yd_pos_short": 0,
                    "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                    "actual_yd_pos_long": yd_pos,  # 实际的昨仓
                    "enter_date": update_time,
                    "holding_days": 0,  # 持仓时间（交易日累计）
                    "mkt_value": mkt_value,  # 市值
                    "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
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
                yd_pos = position['actual_yd_pos_long']
                yd_pos_long = position['yd_pos_long']
                amt = trade_amt
                if side == 1:
                    td_trade_vol = position['actual_td_pos_long'] + msg['trade_vol']
                    mkt_value = position['mkt_value'] + amt
                elif side == 2 :
                    td_trade_vol = position['actual_td_pos_long'] - msg['trade_vol']
                    yd_pos_long -= msg['trade_vol']
                    mkt_value = position['mkt_value'] - amt
                
                order = self.oid_to_req[oid]
                ticker = order['stock_code']
                
                cost = 0
                total_vol = td_trade_vol + yd_pos
                if not total_vol == 0:
                    cost = mkt_value / total_vol
                update_time = datetime.now(timezone.utc)
                accountName = order['tgname'] + '@' + order['log_accountname']
                exchange = order['exchange_id']
                enter_time = position['enter_date']
                holding_days = position['holding_days']
                position_msg = {
                    "ticker": ticker,
                    "cost": cost,  # 成本价
                    "td_pos_long": td_trade_vol,  # 今仓
                    "yd_pos_long": yd_pos_long,  # 昨仓（可卖），挂止盈单后为0
                    "td_pos_short": 0,
                    "yd_pos_short": 0,
                    "actual_td_pos_long": td_trade_vol,  # 实际的今仓
                    "actual_yd_pos_long": yd_pos,  # 实际的昨仓
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
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[update_position] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def update_order_filled(self, data, sid, oid):
        try:
            order = self.oid_to_req[oid]
            traded = self.oid_to_traded[oid]
            amt = self.oid_to_traded_money[oid]
            exchange = decode_exchange_id(data['exchange_id'])
            price = 0
            if traded != 0:
                price = amt / traded

            id = oid
            entrust_vol = int(order['order_vol'])
            start_time = order['begin_time']
            end_time = order['end_time']
            order_type = order['order_type']
            tgname = order['tgname']
            log_accountname = order['log_accountname']
            target_account_name = order['target_account_name']
            acc = self.target_account_names_to_acc[target_account_name]
            db_msg = {
                "_id": id,
                "tg_name": tgname,  # 对应 account_info._id
                # 对应 tlclient.trader.constant 包 ExchangeID
                "exchange": exchange,
                "target_type": order['bs_flag'],    # 'buy' | 'sell' | 'limit_sell'
                "volume": entrust_vol,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": 215,  # algotype:200,目前没有其他的
                "ticker": data['stock_code'],
                "sid": sid,  # target中对应的 母单sid
                "accountName": log_accountname,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_type,  # 此柜台不使用下单时要求的算法
                    "start_time": start_time,
                    "end_time": end_time
                },
                "status": "filled",  # 'active' | 'filled' | 'canceled'
                "filled_vol": traded,  # 实际成交的 volume
                "dbTime": datetime.now(timezone.utc),

            }
            query = {'_id': id}
            #res = self.order_collection.insert_one(db_msg)
            order_collection = self.tradelog_db[acc]['order']
            res = order_collection.replace_one(
                query, db_msg, True)  # 覆盖之前的order记录，修改状态
            #db_msg_json = json.dumps(db_msg)
            self.logger.info(
                f"[on_rtn_filled_order] order_filled (db_res){res} (msg){db_msg}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[update_order_filled] DB_connect_failed! (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def on_mudan_message(self, data):  # no use
        self.logger.info(f"[on_mudan_message] (mudan){data}")

    def on_error(self, ws, error):
        self.logger.error(
            f"[on_error] disconnect (type){type(error)} (msg){error}")
        if type(error) == ConnectionRefusedError or type(error) == ConnectionAbortedError or type(error) == ConnectionResetError or type(error) == websocket._exceptions.WebSocketConnectionClosedException:
            self.reconnect_count += 1
            self.logger.info(f"[on_error] 正在尝试第{self.reconnect_count}次重连")
            send_to_user(logger=self.logger, url_list=self.url_list, msg=error)
            if self.reconnect_count < 100:
                self.ws.close()
                t = threading.Thread(target=self.run_socket)
                t.setDaemon(True)
                t.start()

        else:
            self.logger.error(
                f"[on_error] other_error! (type){type(error)} (msg){error}")

    def gen_local_id(self):
        self.id_base = 1577779200 * LL9
        self.sp = time.time_ns()
        self.local_id = self.sp - self.id_base

    def gen_order_id(self):
        self.local_id += 1
        return self.local_id

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.warning(
            f'[on_close] (close_status_code){close_status_code} (close_msg){close_msg}')

    # no use
    def on_ping(self, ws, message):
        print("ping time:%s" % time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()))
        print(f"ping message: {message} ")

    def join(self):
        while self.is_stopped == False:
            time.sleep(0.01)
            if self.is_stopped:
                self.logger.info(
                    "[close] main thread is stopped,active_orders message will lose")
                break

    def start(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.login()
        self.req_position()
        self.monitor()

    def signal_handler(self, signum=None, frame=None):
        self.is_stopped = True

    def monitor(self):
        ts = [
            threading.Thread(target=self.monitor_algo_order_insert),
            threading.Thread(target=self.monitor_cancel_order),
            threading.Thread(target=self.run_socket),
            threading.Thread(target=self.date_change),
        ]
        for t in ts:
            t.setDaemon(True)
            t.start()

    def login(self):
        try:
            cookies = {'Cookie': 'xxxxx'}
            r = requests.get(self.login_url, cookies=cookies)
            data = r.json()

            self.token = data['data']['token']
            accs = data['data']['accs']
            self.logger.info(f"[login] logged (token){self.token} (data){data}")
            for myacc in accs:
                trade_acc = myacc['trade_acc']
                self.broker_id[trade_acc] = myacc['broker_id']
                self.logger.info(f"(trade_acc){trade_acc} broker_id{self.broker_id[trade_acc]}")
            
            _msg = f"[login] logged (token){self.token} (data){data}"
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
                
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[login] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            exit(0)

    def on_open(self, ws):
        self.logger.info(f"[on_open] (ws){ws}")
        t = threading.Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    def run(self):
        while self.is_stopped == False:
            time.sleep(3)
            text = {"topic": "Pong", "data": int(time.time()*1000)} #毫秒时间戳
            _text = json.dumps(text)
            self.ws.send(_text)
            self.logger.info(f"[on_ping] send (pong_running){_text}")
            print ("running")
    # no use
    def on_pong(self, ws, message):
        print("####### on_pong #######")
        print("pong time:%s" % time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()))
        print("pong message:%s" % message)

    def run_socket(self):
        websocket.enableTrace(True)  # 开启运行状态追踪。debug 的时候最好打开他，便于追踪定位问题。
        url = self.socket_url + self.token
        self.ws = WebSocketApp(url,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close,
                               on_ping=self.on_ping,
                               on_pong=self.on_pong)
        self.ws.on_open = self.on_open
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()
        except:
            self.ws.close()

    def monitor_algo_order_insert(self):
        try:
            while not self.is_stopped:
                for acc in self.accounts_run: 
                    target_accountname = self.target_account_names[acc]
                    buy_query = {"accountName": target_accountname}
                    with self.sell_orderlock:
                        buy_targets = self.order_info_db[acc]["target"].find(buy_query)
                        if buy_targets.count() == 0:
                            self.logger.warning("[monitor_buy_order] no_buy_target")
                            continue
                        for target in buy_targets:
                            if target['_id'] not in self.buy_order_dbids:
                                self.buy_order_dbids.append(target['_id'])
                                self.req_buy_order_insert(target)
                for acc in self.accounts_run:
                    target_accountname = self.target_account_names[acc]
                    sell_query = {"accountName": target_accountname}
                    with self.sell_orderlock:
                        sell_targets = self.order_info_db[acc]["sell_target"].find(sell_query)
                        if sell_targets.count() == 0:
                            self.logger.warning(
                                "[monitor_sell_order] no_sell_target")
                            continue
                        for sell_target in sell_targets:
                            if sell_target['_id'] not in self.sell_order_dbids:
                                self.sell_order_dbids.append(sell_target['_id'])
                                self.req_sell_order_insert(sell_target)
                time.sleep(self.scan_interval)
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[monitor_algo_order_insert] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)



    def req_buy_order_insert(self, obj: dict):
        try:
            target_account_name = obj['accountName']
            acc = self.target_account_names_to_acc[target_account_name]
            account_id = self.account_id[acc]

            
            sid = str(obj['sid'])
            vol = int(obj["volume"])
            basket_name = sid
            #order_vol = (str)(obj["volume"])

            order_vol = f'{vol:d}'
            int_stock_code = int(obj['ticker'])
            stock_code = f'{int_stock_code:06d}'

            begin_time = obj['executionPlan']["start_time"].replace(':', '')
            end_time = obj['executionPlan']["end_time"].replace(':', '')

            ft_flag = 'buy'
            row = [stock_code, ft_flag, order_vol, begin_time,
                   end_time, account_id, basket_name]
            order_dict = {}
            order_dict["basket_name"] = basket_name
            order_dict['order_vol'] = order_vol
            order_dict['stock_code'] = stock_code
            order_dict['begin_time'] = begin_time
            order_dict['end_time'] = end_time
            order_dict['bs_flag'] = ft_flag
            order_dict['trade_acc'] = account_id

            mudans = [order_dict]
            out = {"mudans": mudans, "token": self.token}
            data = json.dumps(out)
            r = requests.post(self.upload_mudan_url, json=out)

            
            text = r.text
            data = json.loads(text)
            
            if data['code'] != 0:
                self.logger.error(
                    f"[on_buy_req_insert] insert_msg_send_failed (errcode){data['code']} (err_msg){data['data']}")
                order_msg = order_dict
                order_msg['sid'] = sid
                order_msg['status'] = 'rejected'
                self.insert_ft_proposed_target(acc, sid, order_msg)
                
                acc = self.target_account_names_to_acc[target_account_name]
                target_collection =  self.order_info_db[acc]['target']
                delete_query = {
                    'accountName' : target_account_name,
                    'sid' : sid,
                    'ticker' : stock_code,
                    'volume' : vol
                }
                delete_res = target_collection.delete_one(delete_query)
                self.logger.info(f"[on_req_buy_order] delete (target){obj}")
                return
            db_id = obj['_id']
            ref = data['data'][0]['id']
            status = data['data'][0]['status']
            err_msg = data['data'][0]['status_msg']
            
            
            order_type = obj['executionPlan']["order_type"]
            order_dict['order_type'] = order_type
            exchange = decode_exchange_id(data['data'][0]['exchange_id'])
            order_dict['exchange_id'] = exchange
            order_dict['target_account_name'] = target_account_name
            tgname = target_account_name.split('@', 1)[0]
            order_dict['tgname'] = tgname
            log_accountname = target_account_name.split('@', 1)[1]
            order_dict['log_accountname'] = log_accountname
            order_dict['begin_time'] = obj['executionPlan']["start_time"]
            order_dict['end_time'] = obj['executionPlan']["end_time"]
            ft_proposed_target_collection = self.order_info_db[acc]['ft_proposed_target']
            '''
            返回母单状态：
            1启动 2暂停 3完成 4取消 6废单
            
            '''
            
            if status >= 4:
                self.logger.error(
                    f"[req_buy_order_insert] insert_order_failed! (order){data} (err_msg){err_msg}")
                order_msg = order_dict
                order_msg['sid'] = sid
                order_msg['status'] = 'rejected'
                self.insert_ft_proposed_target(acc, sid, order_msg)
                
                acc = self.target_account_names_to_acc[target_account_name]
                target_collection =  self.order_info_db[acc]['target']
                delete_query = {
                    'accountName' : target_account_name,
                    'sid' : sid,
                    'ticker' : stock_code,
                    'volume' : vol
                }
                delete_res = target_collection.delete_one(delete_query)
                self.logger.info(f"[on_req_buy_order] delete (target){obj}")
                return
            else:
                oid = self.gen_order_id()
                
                self.sid_to_traded[sid] = 0
                self.oid_to_traded[oid] = 0
                self.oid_to_traded_money[oid] = 0
                self.oid_to_ref[oid] = ref
                self.sids.append(sid)

                
                self.sid_to_req[sid] = order_dict
                self.oid_to_req[oid] = order_dict
                self.oid_to_sid[oid] = sid
                self.db_id_to_oid[db_id] = oid
                ft_local_ids = []
                self.ref_to_oid[ref] = oid
                
                self.logger.info(
                    f"[on_req_order_insert] order_insert_success! (response){text} (ref){ref}")
                self.rtn_order_insert(sid, oid, exchange)
                #ft_order用于恢复
                ft_order_collection = self.order_info_db[acc]['ft_order']
                db_msg = {
                    "oid" : oid,
                    "sid" : sid,
                    "mudan_id" : ref,
                    "local_ids" : ft_local_ids,
                    'log_accountname' : log_accountname,
                    "traded_vol" : 0,
                    "traded_amt" : 0,
                    "order_msg": order_dict
                }
                query = {"oid": oid}
                res = ft_order_collection.replace_one(query, db_msg, True)
                self.logger.info(f"[on_req_order_insert] insert_ft_order_info (res){res} (msg){db_msg}")
                
                order_msg = order_dict
                order_msg['sid'] = sid
                order_msg['status'] = 'inserted'
                self.insert_ft_proposed_target(acc,sid,order_msg)
                
                acc = self.target_account_names_to_acc[target_account_name]
                target_collection =  self.order_info_db[acc]['target']
                delete_query = {
                    'accountName' : target_account_name,
                    'sid' : sid,
                    'ticker' : stock_code,
                    'volume' : vol
                }
                delete_res = target_collection.delete_one(delete_query)
                self.logger.info(f"[on_req_buy_order] delete (target){obj}")
            
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[req_buy_order_insert] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    
    def insert_ft_proposed_target(self, acc, sid, order_msg:dict):
        try:
            ft_proposed_target_collection = self.order_info_db[acc]['ft_proposed_target']
            insert_query = {'sid' : sid, 'target_account_name': order_msg['target_account_name']}
            insert_res = ft_proposed_target_collection.replace_one(insert_query, order_msg, True)
            self.logger.info(f"[on_req_buy_order_insert] ft_proposed_target_collection (insert_res){insert_res} (order_msg){order_msg}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[insert_ft_proposed_target] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def rtn_order_insert(self, sid, oid, exchange):
        try:
            
            if oid not in self.oid_to_req:
                self.logger.warning(
                    "[rtn_order_insert] can't_find_req (oid){oid}")
                return
            order_dict = self.oid_to_req[oid]
            filled_vol = self.oid_to_traded[oid]
            amt = self.oid_to_traded_money[oid]
            
            target_type = order_dict['bs_flag']
            volume = int(order_dict['order_vol'])
            id = oid
            price = 0
            if not filled_vol == 0:
                price = amt / filled_vol
            tgname = order_dict['tgname']
            log_accountname = order_dict['log_accountname']
            target_account_name = order_dict['target_account_name']
            acc = self.target_account_names_to_acc[target_account_name]
            price = 0
            db_msg = {
                "_id": id,
                "tg_name": tgname,  # 对应 account_info._id
                "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
                "target_type": target_type,  # 'buy' | 'sell' | 'limit_sell'
                "volume": volume,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": 215,  # algotype:200,目前没有其他的
                "ticker": order_dict['stock_code'],
                "sid": sid,  # target中对应的 母单sid
                "accountName":  log_accountname,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_dict['order_type'],
                    "start_time": order_dict['begin_time'],
                    "end_time": order_dict['end_time']
                },
                "status": "active",  # 'active' | 'filled' | 'canceled'
                "filled_vol": filled_vol,  # 实际成交的 volume
                "dbTime": datetime.now(timezone.utc)  # 入库时间
            }
            order_collection = self.tradelog_db[acc]['order']
            res = order_collection.insert_one(db_msg)
            #db_msg_json = json.dumps(db_msg)
            self.logger.info(
                f"[rtn_order_inserted] order_inserted (db_res){res} (db_msg){db_msg}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[rtn_order_insert] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    #not use
    def monitor_sell_order(self):
        try:
            while not self.is_stopped:
                for target_accountname in self.target_accountnames:
                    query = {"accountName": target_accountname}
                    with self.sell_orderlock:
                        sell_targets = self.orderinfo_db["sell_target"].find(query)
                        if sell_targets.count() == 0:
                            self.logger.warning(
                                "[monitor_sell_order] no_sell_target")
                            continue
                        for sell_target in sell_targets:
                            if sell_target['_id'] not in self.cancel_order_dbids:
                                self.cancel_order_dbids.append(sell_target['_id'])
                                self.req_sell_order_insert(sell_target)
                        result = self.orderinfo_db["sell_target"].delete_many(query)
                        self.logger.info(
                            f"[monitor_sell_order] delete{result.deleted_count}messages_by(query){query}")
                time.sleep(self.scan_interval)
        except Exception as e:
                err = traceback.format_exc()
                send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
                self.logger.error(f'[rtn_order_insert] (exception){err}')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
                
    def req_sell_order_insert(self, obj: dict):
        try:
            target_account_name = obj['accountName']
            acc = self.target_account_names_to_acc[target_account_name]
            account_id = self.account_id[acc]
            
            order_dict = {}
            sid = str(obj['sid'])
            vol = int(obj["volume"])
            order_vol = f'{vol:d}'
            int_stock_code = int(obj['ticker'])
            stock_code = f'{int_stock_code:06d}'
            begin_time = obj['executionPlan']["start_time"].replace(':', '')
            end_time = obj['executionPlan']["end_time"].replace(':', '')
            ft_flag = 'sell'
            basket_name = sid
            order_dict["basket_name"] = basket_name
            order_dict['order_vol'] = order_vol
            order_dict['stock_code'] = stock_code
            order_dict['begin_time'] = begin_time
            order_dict['end_time'] = end_time
            order_dict['bs_flag'] = ft_flag
            order_dict['trade_acc'] = account_id
            mudans = [order_dict]
            out = {"mudans": mudans, "token": self.token}

            data = json.dumps(out)
            r = requests.post(self.upload_mudan_url, json=out)

            text = r.text
            data = json.loads(text)
            
            order_type = obj['executionPlan']["order_type"]
            order_dict['order_type'] = order_type
            exchange = decode_exchange_id(data['data'][0]['exchange_id'])
            order_dict['target_account_name'] = target_account_name
            order_dict['exchange_id'] = exchange
            tgname = target_account_name.split('@', 1)[0]
            order_dict['tgname'] = tgname
            log_accountname = target_account_name.split('@', 1)[1]
            order_dict['log_accountname'] = log_accountname
            order_dict['begin_time'] = obj['executionPlan']["start_time"]
            order_dict['end_time'] = obj['executionPlan']["end_time"]
            ft_proposed_target_collection = self.order_info_db[acc]['ft_proposed_target']

            if data['code'] != 0:
                self.logger.error(
                    f"[on_req_sell_insert] insert_msg_send_failed (errcode){data['code']} (err_msg){data['data']}")
                order_msg = order_dict
                order_msg['sid'] = sid
                order_msg['status'] = 'rejected'
                self.insert_ft_proposed_target(acc, sid, order_msg)
                
                acc = self.target_account_names_to_acc[target_account_name]
                target_collection =  self.order_info_db[acc]['sell_target']
                delete_query = {
                    'accountName' : target_account_name,
                    'sid' : sid,
                    'ticker' : stock_code,
                    'volume' : vol
                }
                delete_res = target_collection.delete_one(delete_query)
                self.logger.info(f"[on_req_buy_order] delete (target){obj}")
                return

            db_id = obj['_id']
            
            ref = data['data'][0]['id']
            status = data['data'][0]['status']
            err_msg = data['data'][0]['status_msg']
            if status >= 4:
                self.logger.error(
                    f"[req_sell_order_insert] order_insert_failed! (err_msg){err_msg}")
                order_msg = order_dict
                order_msg['sid'] = sid
                order_msg['status'] = 'rejected'
                self.insert_ft_proposed_target(acc, sid, order_msg)
                
                acc = self.target_account_names_to_acc[target_account_name]
                target_collection =  self.order_info_db[acc]['sell_target']
                delete_query = {
                    'accountName' : target_account_name,
                    'sid' : sid,
                    'ticker' : stock_code,
                    'volume' : vol
                }
                delete_res = target_collection.delete_one(delete_query)
                self.logger.info(f"[on_req_sell_order] delete (target){obj}")
                return
            oid = self.gen_order_id()
            self.sid_to_traded[sid] = 0
            self.oid_to_traded[oid] = 0
            self.oid_to_traded_money[oid] = 0
            self.sids.append(sid)

            self.sid_to_req[sid] = order_dict
            self.oid_to_req[oid] = order_dict
            self.oid_to_ref[oid] = ref
            self.oid_to_sid[oid] = sid
            self.db_id_to_oid[db_id] = oid
            if ref in self.ref_to_oid:
                self.logger.error(f"[req_sell_order_insert] trade_ref_exist! (trade_ref){ref}")
                return
            self.ref_to_oid[ref] = oid
            self.logger.info(
                f"[on_req_order_insert] order_inserted (response){text} (order_ref){ref}")
            
            self.rtn_order_insert(sid, oid, exchange)
            
            #ft_order用于恢复
            ft_local_ids = []
            collection = self.order_info_db[acc]['ft_order']
            db_msg = {
                "oid" : oid,
                "sid" : sid,
                "mudan_id" : ref,
                "local_ids" : ft_local_ids,
                "log_accountname" : log_accountname,
                "traded_vol" : 0,
                "traded_amt" : 0,
                "order_msg": order_dict
            }
            query = {"oid": oid}
            res = collection.replace_one(query, db_msg, True)
            self.logger.info(f"[on_req_order_insert] insert_ft_order_info (res){res} (msg){db_msg}")
            
            
            order_msg = order_dict
            order_msg['sid'] = sid
            order_msg['status'] = 'inserted'
            self.insert_ft_proposed_target(acc, sid, order_msg)
            #delete sell_target
            acc = self.target_account_names_to_acc[target_account_name]
            target_collection =  self.order_info_db[acc]['sell_target']
            delete_query = {
                'accountName' : target_account_name,
                'sid' : sid,
                'ticker' : stock_code,
                'volume' : vol
            }
            delete_res = target_collection.delete_one(delete_query)
            self.logger.info(f"[on_req_buy_order] delete (target){obj}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[req_sell_order_insert] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def monitor_cancel_order(self):
        try:
            while not self.is_stopped:
                for acc in self.accounts_run:
                    target_accountname = self.target_account_names[acc]
                    query = {"accountName": target_accountname}
                    print(query)
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
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[monitor_cancel_order] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def rtn_order_canceled(self, oid, sid):
        try:
            if oid not in self.oid_to_req:
                self.logger.warning(
                    f"[rtn_order_canceled] can't_find_req (oid){oid}")
                return

            id = oid
            order_dict = self.oid_to_req[oid]
            filled_vol = self.oid_to_traded[oid]
            exchange = order_dict['exchange_id']
            target_type = order_dict['bs_flag']
            volume = order_dict['order_vol']
            amt = self.oid_to_traded_money[oid]
            tgname = order_dict['tgname']
            log_accountname = order_dict['log_accountname']
            target_account_name = order_dict['target_account_name']
            acc = self.target_account_names_to_acc[target_account_name]
            price = 0
            if not filled_vol == 0:
                price = amt / filled_vol

            sp = int(time.time()*1000) % 1000
            now = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

            db_msg = {
                "_id": id,
                "tg_name": tgname,  # 对应 account_info._id
                "exchange": exchange,  # 对应 tlclient.trader.constant 包 ExchangeID
                "target_type": target_type,  # 'buy' | 'sell' | 'limit_sell'
                "volume": volume,  # 订单的volume
                "price": price,  # 实际成交均价
                "order_type": 215,  # algotype:200,目前没有其他的
                "ticker": order_dict['stock_code'],
                "sid": sid,  # target中对应的 母单sid
                "accountName": log_accountname,  # 对应 account_info.account_name
                "algo_args": {  # 具体的算法参数
                    "order_type": order_dict['order_type'],
                    "start_time": order_dict['begin_time'],
                    "end_time": order_dict['end_time']
                },
                "status": "canceled",  # 'active' | 'filled' | 'canceled'
                "filled_vol": filled_vol,  # 实际成交的 volume
                "dbTime": datetime.now(timezone.utc),
            }

            query = {'_id': id}
            order_collection = self.tradelog_db[acc]['order']
            res = order_collection.replace_one(
                query, db_msg, True)  # 覆盖之前的order记录，修改状态
            #res = self.order_collection.insert_one(db_msg)
            #db_msg_json = json.dumps(db_msg)
            self.logger.info(
                f"[rtn_order_canceled] order_canceled (db_res){res} (db_msg){db_msg}")
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[rtn_order_cancel] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            

    def req_cancel_order(self, obj: dict):
        try:
            req = {}
            req['token'] = self.token
            req['mudan_op_type'] = 4
            oid = obj['oid']

            if oid not in self.oid_to_ref:
                self.logger.error(
                    f"[req_cancel_order] can't_find_ref (oid){oid}")

            else:
                mudan_id = self.oid_to_ref[oid]
                req['mudan_id'] = [mudan_id]
                r = requests.post(self.cancel_url, json=req)
                data = json.loads(r.text)
                if data['code'] == 0:
                    sid = self.oid_to_sid[oid]
                    self.logger.info(
                        f"[cancel order] cancel_order_inserted (res){r.json()}")
                    self.rtn_order_canceled(oid, sid)
            origin_req = self.oid_to_req[oid]
            target_account_name = origin_req['target_account_name']
            acc = self.target_account_names_to_acc[target_account_name]
            target_collection =  self.order_info_db[acc]['cancel_target']
            delete_query = {
                'accountName' : target_account_name,
                'oid' : oid
            }
            delete_res = target_collection.delete_one(delete_query)
            self.logger.info(f"[on_req_buy_order] delete (target){obj}")
            # cancel success 所以回rtn_order,实际什么时候撤单不确定
        except Exception as e:
            err = traceback.format_exc()
            send_to_user(logger=self.logger, url_list=self.url_list, msg=err)
            self.logger.error(f'[req_cancel_order] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)


if __name__ == "__main__":
    
    description = "ft_server,get target from mongodb and serve feitu"    
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('-e' , '--end_time', dest='end_time', default='15:30')
    _file_name = "C:\\Users\\Administrator\\Desktop\\ft_batandjson\\ft_setting.json"
    parser.add_argument('-p', '--config_filename', dest= 'config_filename', default= _file_name)
    
    args = parser.parse_args()
    print (f"(args){args}")
    
    td = FtServer(args.config_filename, args.end_time)
    td.start()

    td.join()