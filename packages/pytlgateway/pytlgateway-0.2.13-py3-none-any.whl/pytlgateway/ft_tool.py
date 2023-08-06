from datetime import datetime, timezone
import os
import csv
from collections import namedtuple
import json
import time
import sys
import traceback
import getopt
import argparse
from pathlib import Path
import requests
import pandas as pd

from pymongo import MongoClient, ASCENDING, DESCENDING
from utils import decode_ft_flag,  decode_exchange_id, send_to_user
from logger import Logger


class FtTool(object): 
    
    def __init__(self, config_filename, update_trade_date, sync_pos, sync_trade, sync_add, sync_trade_in_trading, sync_pos_in_trading):
        self.load_ft_setting(config_filename)
        self.logger = Logger.get_logger(self.logname, self.log_file_path)
        self.update_trade_date = update_trade_date
        self.sync_pos = sync_pos
        self.sync_trade = sync_trade
        self.sync_add = sync_add
        self.sync_trade_in_trading = sync_trade_in_trading
        self.sync_pos_in_trading = sync_pos_in_trading
        
        try:
            self.db_client = {}
            self.order_info_db = {}
            self.tradelog_db = {}
            dbClient = MongoClient(self.dash_host, self.dash_port, connectTimeoutMS=10000, connect=False)
            dbClient['dashboard'].authenticate(self.dash_user, self.dash_pwd, mechanism='SCRAM-SHA-1') 
            self.db_dashboard = dbClient['dashboard']

            for acc in self.accounts_run:
                self.db_client[acc] = MongoClient(
                    self.mongo_host[acc], self.mongo_port[acc], connectTimeoutMS=10000, socketTimeoutMS = 3000)
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
                
            #for test
            #self.db_client = MongoClient()
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[init] DB_connect_failed! (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            exit()

        
        #test for req_position
        #self.db_client_test = MongoClient("127.0.0.1", 27017, connectTimeoutMS=10000)
        #self.test_trading_account = self.db_client_test['tradingAccount']

        self.get_acccount_info()
    
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
            self.ft_zidan_message_path = setting['ft_zidan_message_path'].replace('/', '\\')
            self.upload_mudan_url = setting['upload_mudan_url']
            self.url_list = setting.get('url_list')
            self.cancel_url = setting['cancel_url']
            # self.log_accountname = setting['ACCOUNT_NAME'] #用于tradinglog数据库,order/trade
            # 产品名称，用于获取tg_name和account_name
            self.sync_position_open = setting['sync_position_open'] #设置同步持仓的时间
            self.sync_position_close = setting['sync_position_close']
            #self.tgname = setting['tg_name']
            # self.target_accountname = self.tgname + '@' + self.log_accountname #下单时用

            self.logname = setting['logname']
            self.scan_interval = setting['scan_interval']
            
            #get config by product
            self.accounts_config = setting['accounts']
            self.accounts_run = setting['run'] #0 zhongxincats1 1 huaxin ...
            
            self.dashboard = setting['daily_equity_position']
            self.dash_host = self.dashboard['mongoHost']
            self.dash_port = self.dashboard['mongoPort']
            self.dash_user = self.dashboard['user']
            self.dash_pwd = self.dashboard['password']
            
            self.config = {}
            self.account_id = {}
            self.account_id_to_acc = {}
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
                self.account_id_to_acc[self.account_id[acc]] = acc
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

    def get_acccount_info(self):
        try:
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
        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.error(f'[get_account_info] (exception){err}')
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)


    def start(self):
        
        #trade_export_path = r'C:\Users\Administrator\Downloads\ft_client_win_1.6.4\ft_client_win\export\20221201\20221201_326000024361_trade.csv'
        if self.sync_trade == True:
            self.logger.info(f"in get_trade")
            self.get_trade_from_csv()
            _msg = "[get_trade_from_csv] executed"
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)

        if self.sync_trade_in_trading == True:
            self.get_trade_from_csv_in_trading()
            _msg = "[get_trade_from_csv_in_trading] executed"
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        
        if self.sync_pos == True:
            self.date_change()
            _msg = "[date_change] executed"
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        
        if self.sync_add == True:
            self.sync_position_add()
            _msg = "[sync_add] executed"   
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        
        if self.sync_pos_in_trading == True:
            self.restore_pos()
            self.get_update_position_from_csv()
            _msg = "[sync_pos_in_trading] executed"
            send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
        
    def get_trade_from_csv(self):
        try:
            #delete old trade msgs
            for acc in self.accounts_run:
                ft_sync_trade_collection = self.order_info_db[acc]['ft_sync_trade']
                del_res = ft_sync_trade_collection.delete_many({})
                self.logger.info(f"deleted {del_res.deleted_count}tf_sync_trade_msg")
            #trade_collection = self.test_trading_log['trade'] #测试数据库
            for acc in self.accounts_run:
                
                dt = datetime.now()
                date = dt.strftime("%Y%m%d")
                if not self.update_trade_date == date:
                    date = self.update_trade_date
                    int_date = int(self.update_trade_date)
                    int_day = int(int_date%100) 
                    int_month = int((int_date/100)%100) 
                    int_year = int(int_date/10000)
                    filter_time_array = datetime(year=int_year,month=int_month,day=int_day)
                else:
                    filter_time_array = datetime.today().replace(hour=0,minute=0,second=0)
                account_id = self.account_id[acc]
                path = self.ft_tradecsv_path + f'{date}\\{date}_{account_id}_trade.csv'
                #path = f"C:\\Users\\Administrator\\Downloads\\ft_client_win_1.8.0\\ft_client_win\\export\\{date}\\{date}_{account_id}_trade.csv"
                trade_collection = self.tradelog_db[acc]['trade']
                ft_order_collection = self.order_info_db[acc]['ft_order']
                ft_sync_trade_collection = self.order_info_db[acc]['ft_sync_trade']
                #del_res = ft_sync_trade_collection.delete_many({})
                #self.logger.info(f"deleted {del_res.deleted_count}tf_sync_trade_msg")
                self.logger.info(f"[get_trade_from_csv] get_trade_msg_from(path){path}")
                with open(path, encoding='gbk')as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    Row = namedtuple('Row', headers)
                    for row in reader:
                        row = Row(*row)
                        traded_vol = int(row.成交数量)
                        traded_price = float(row.成交价格)
                        int_ticker = int(row.股票代码)
                        ticker = f'{int_ticker:06d}'
                        mudan_id = int(row.母单编号)
                        query_for_exchange = {"ticker": ticker}
                        exchange = 0
                        target = self.order_info_db[acc]['ft_position'].find_one(query_for_exchange)
                        #self.logger.info(f"(target){target}")
                        if not target == None:
                            exchange = target['exchange']
                        if traded_vol > 0:
                            local_id = str(row.本地编号)
                            origin_order_query = {"mudan_id" : mudan_id}
                            target = ft_order_collection.find_one(origin_order_query)
                            oid = 0
                            sid = "" # f"[PR_Ver_1_0_1_HX]{row.股票代码}T20221125"
                            entrust_vol = 0
                            side = 0
                            accountName = ""
                            order_type = 215
                            if not target == None:
                                oid = target['oid']
                                sid = target['sid']
                                entrust_vol =  int(target['order_msg']['order_vol'])
                                bs_flag = target['order_msg']['bs_flag']
                                if bs_flag == 'buy':
                                    side = 1
                                elif bs_flag == 'sell':
                                    side = 2
                                accountName = target['order_msg']['log_accountname']
                                #order_type = target['order_msg']['order_type']
                            timerow = row.委托时间
                            timearray = time.strptime(timerow, "%Y-%m-%d %H:%M:%S")
                            dt = datetime.fromtimestamp(time.mktime(timearray), timezone.utc)
                            
                            trade_msg = {
                                "trade_ref": local_id, # broker 端的交易回报 id
                                "oid": oid,
                                "ticker": ticker,
                                "exchange" : exchange,
                                "traded_vol": traded_vol,
                                "traded_price": traded_price,
                                "order_type": order_type,
                                "side": side,  # 对应 tlclient.trader.constant 包 Side 
                                "entrust_vol": entrust_vol,
                                "entrust_price": 0,
                                "dbTime":datetime.now(timezone.utc),
                                "sid": sid, # 对应订单中的 sid
                                "commission": 0,
                                "trade_time": dt,
                                "accountName": accountName, # 对应 account_info.account_name
                                }
                            
                            query = {"trade_ref" : local_id , "accountName" : accountName, "trade_time": { "$gt": filter_time_array}}

                            if trade_collection.find_one(query) == None:
                                res = trade_collection.replace_one(query, trade_msg, True)
                                self.logger.info(f"[get_trade_from_csv] (res){res} (trade_msg){trade_msg}")
                                if ft_sync_trade_collection.find_one(query) == None:
                                    res = ft_sync_trade_collection.replace_one(query, trade_msg, True)
                                    self.logger.info(f"[get_trade_from_csv] ft_sync_trade(res){res} (trade_msg){trade_msg}")
                            else:
                                self.logger.info(f"[get_trade_from_csv] (trade_ref){local_id}exist (trade_msg){trade_msg}")                                
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[get_trade_from_csv] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def get_trade_from_csv_in_trading(self):
        try:
            csv_path =  Path(self.ft_zidan_message_path)
            for acc in self.accounts_run:
                product_name = self.product_names[acc]
                trade_acc = self.account_id[acc]
                #for test

                """
                if product_name == "指增1号-华鑫":
                    product_name = "华鑫API测试"
                elif product_name == "反脆弱1号":
                    product_name = "盖亚青柯cats测试"
                """
                #TODO don't use hard code like this
                if product_name == "指增1号-华鑫":
                    product_name = "盖亚青柯指增1号"
                path_head = product_name + '_' + trade_acc
                for file in csv_path.glob("*.csv"):
                    if file.stem.startswith(path_head):
                        trade_collection = self.tradelog_db[acc]['trade']
                        ft_order_collection = self.order_info_db[acc]['ft_order']
                        ft_sync_trade_collection = self.order_info_db[acc]['ft_sync_trade']
                        del_res = ft_sync_trade_collection.delete_many({})
                        self.logger.info(f"[get_trade_from_csv_in_trading] deleted {del_res.deleted_count}tf_sync_trade_msg")
                        self.logger.info(f"[get_trade_from_csv_in_trading] get_trade_msg_from(path){file.name}")
                        with open(file, encoding='utf-8-sig') as f:
                            reader = csv.reader(f)
                            headers = next(reader)
                            Row = namedtuple('Row', headers)
                            for row in reader:
                                row = Row(*row)
                                if str(row.报单状态) == "全部成交" or str(row.报单状态) == "部分撤单":
                                    traded_vol = int(row.成交数量)
                                    traded_price = float(row.成交均价)
                                    int_ticker = int(row.证券代码)
                                    ticker = f'{int_ticker:06d}'
                                    mudan_id = int(row.母单ID)
                                    query_for_exchange = {"ticker": ticker}
                                    exchange = 0
                                    target = self.order_info_db[acc]['ft_position'].find_one(query_for_exchange)
                                    #self.logger.info(f"(target){target}")
                                    if not target == None:
                                        exchange = target['exchange']
                                    if traded_vol > 0:
                                        local_id = str(row.子单编号)
                                        origin_order_query = {"mudan_id" : mudan_id}
                                        target = ft_order_collection.find_one(origin_order_query)
                                        oid = 0
                                        sid = "" # f"[PR_Ver_1_0_1_HX]{row.股票代码}T20221125"
                                        entrust_vol = 0
                                        side = 0
                                        accountName = ""
                                        order_type = 215
                                        if not target == None:
                                            oid = target['oid']
                                            sid = target['sid']
                                            entrust_vol =  int(target['order_msg']['order_vol'])
                                            bs_flag = target['order_msg']['bs_flag']
                                            if bs_flag == 'buy':
                                                side = 1
                                            elif bs_flag == 'sell':
                                                side = 2
                                            accountName = target['order_msg']['log_accountname']
                                            #order_type = target['order_msg']['order_type']
                                        _dt = datetime.now()
                                        _date = _dt.strftime("%Y-%m-%d")
                                        timerow = row.委托时间
                                        _timestamp = _date + ' ' + timerow
                                        timearray = time.strptime(_timestamp, "%Y-%m-%d %H:%M:%S")
                                        dt = datetime.fromtimestamp(time.mktime(timearray), timezone.utc)

                                        trade_msg = {
                                            "trade_ref": local_id, # broker 端的交易回报 id
                                            "tg_name": target['order_msg']['target_account_name'].split('@')[0],
                                            "oid": oid,
                                            "ticker": ticker,
                                            "exchange" : exchange,
                                            "traded_vol": traded_vol, 
                                            "traded_price": traded_price,
                                            "order_type": order_type, 
                                            "side": side,  # 对应 tlclient.trader.constant 包 Side 
                                            "entrust_vol": entrust_vol,
                                            "entrust_price": 0,
                                            "dbTime":datetime.now(timezone.utc),
                                            "sid": sid, # 对应订单中的 sid
                                            "commission": 0,
                                            "trade_time": dt,
                                            "accountName": accountName, # 对应 account_info.account_name
                                            }
                                        filter_time_array = datetime.today().replace(hour=0,minute=0,second=0)
                                        query = {"trade_ref" : local_id , "accountName" : accountName, "trade_time": { "$gt": filter_time_array}}

                                        if trade_collection.find_one(query) == None:
                                            res = trade_collection.replace_one(query, trade_msg, True)
                                            self.logger.info(f"[get_trade_from_csv_in_trading] (res){res} (trade_msg){trade_msg}")
                                            if ft_sync_trade_collection.find_one(query) == None:
                                                res = ft_sync_trade_collection.replace_one(query, trade_msg, True)
                                                self.logger.info(f"[get_trade_from_csv_in_trading] ft_sync_trade(res){res} (trade_msg){trade_msg}")
                                        else:
                                            self.logger.info(f"[get_trade_from_csv_in_trading] (trade_ref){local_id}exist (trade_msg){trade_msg}")
                        os.remove(file)
                        self.logger.info(f"[get_trade_from_csv_in_trading] delete_csv (file_name){file.name}")
            
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[get_trade_from_csv_in_trading] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def date_change(self):
        try:
                dt = datetime.now()
                self.logger.info(f"(dt){dt.hour}")
                if dt.hour <= self.sync_position_open and self.sync_pos == True:
                    self.logger.info("[date_change] date_change_open")
                    self.sync_position()
                    self.update_position_date_open()
                elif dt.hour < self.sync_position_close and dt.hour > self.sync_position_open:
                    self.logger.info("[date_change] date_not_change")
                    self.sync_position()
                elif dt.hour >= self.sync_position_close and self.sync_pos == True:
                    self.logger.info("[date_change] date_change_close")
                    self.sync_position()
                    self.update_position_date_close()
                                            
                else:
                    self.logger.info("[date_change] date_not_change")
                    return
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[date_change] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def sync_position_add(self):
        try:
            for acc in self.accounts_run:
                trade_today_collection = self.order_info_db[acc]['ft_sync_trade']
                equity_position_collection = self.order_info_db[acc]['EquityPosition']
                account_name = self.target_account_names[acc]
                positions_query = {'accountName': account_name}
                equity_positions = equity_position_collection.find(positions_query)
                if equity_positions.count() == 0:
                    self.logger.error("[sync_position_add] find_nothing_in_equityposition")
                else:
                    for position in equity_positions:
                        sid = position['sid']
                        if sid.startswith('[ADD]'):
                            ticker = position['ticker']
                            sync_trade_query = {'ticker' : ticker}
                            sid_to_traded_vol = {}
                            sync_trades = trade_today_collection.find(sync_trade_query)
                            """
                            if not sync_trades.count() == 0:
                                for sync_trade in sync_trades:
                                    trade_sid = sync_trade['sid']
                                    sid_to_traded_vol[trade_sid] = 0
                                    vol = sid_to_traded_vol[trade_sid]
                                    if sync_trade['side'] == 1:
                                        vol += sync_trade['traded_vol']
                                    elif sync_trade['side'] == 2:
                                        vol -= sync_trade['traded_vol']
                                for key,value in sid_to_traded_vol.items():
                                    position_sid = key
                                    position_yd_vol = value
                                    query_by_sid = {'sid': position_sid}
                                    one_trade = trade_today_collection.find_one(query_by_sid)
                                    exchange = one_trade['exchange']
                                    position_for_update = equity_position_collection.find_one(query_by_sid)
                                    if position_for_update is not None:
                                        #yd_pos_long = position_for_update['yd_pos_long'] + position_yd_vol
                                        actual_yd_pos_long = position_for_update['actual_yd_pos_long'] + position_yd_vol
                                        data_to_update ={
                                            'yd_pos_long' : actual_yd_pos_long,
                                            'actual_yd_pos_long' : actual_yd_pos_long
                                        }
                                        new_data = {"$set": data_to_update}
                                        res = equity_position_collection.update_one(query_by_sid, new_data)
                                        self.logger.info(f"[sync_position_add] update_success (res){res}")
                                    else:
                                        self.add_position_for_add(acc, exchange = exchange, ticker = ticker, td_vol = 0, yd_vol = position_yd_vol, accountName = account_name, sid = position_sid)
                                query_for_delete_add = {'sid' : sid , 'accountName' : account_name}
                                equity_position_collection.delete_one(query_for_delete_add)
                                self.logger.info(f"delete_position (sid){sid}")
                            """

                            #找不到sync_trade 直接将add持仓分到所有持仓上
                            self.logger.info("[sync_position_add] nothing")
                            #yd_pos_long = position['yd_pos_long']
                            actual_yd_pos_long = position['actual_yd_pos_long']
                            if actual_yd_pos_long > 0:
                                query_positions = {'accountName': account_name, 'ticker': ticker, 'sid' :  {'$ne' : sid}}
                                position_for_update = equity_position_collection.find_one(query_positions)
                                if position_for_update == None:
                                    self.logger.warning("[sync_position_add] one_pos")
                                else:
                                    #yd_pos_long = position_for_update['yd_pos_long'] + actual_yd_pos_long
                                    actual_yd_pos_long = position_for_update['actual_yd_pos_long'] + actual_yd_pos_long
                                    _id = position_for_update['_id']
                                    _query = {'_id': _id}
                                    data_to_update ={
                                        'yd_pos_long' : actual_yd_pos_long,
                                        'actual_yd_pos_long' : actual_yd_pos_long
                                    }
                                    new_data = {"$set": data_to_update}
                                    res = equity_position_collection.update_one(_query, new_data)
                                    #delete add
                                    query_for_delete_add = {'sid' : sid , 'accountName' : account_name}
                                    equity_position_collection.delete_one(query_for_delete_add)
                                    self.logger.info(f"delete_position (sid){sid}")
                            elif actual_yd_pos_long < 0:
                                query_positions = {'accountName': account_name, 'ticker': ticker, 'sid' : {'$ne' : sid}}
                                ticker_positions = equity_position_collection.find(query_positions)
                                if ticker_positions.count() > 0:
                                    for ticker_position in ticker_positions:
                                        ticker_yd = ticker_position['actual_yd_pos_long']
                                        ticker_sid = ticker_position['sid']
                                        if ticker_yd <= 0 or ticker_sid.startswith('[ADD]'):
                                            continue
                                        pos =  ticker_yd + actual_yd_pos_long
                                        _id = ticker_position['_id']
                                        if pos >= 0 :
                                            data_to_update ={
                                                                'yd_pos_long' : pos,
                                                                'actual_yd_pos_long' : pos
                                                            }
                                            new_data = {"$set": data_to_update}
                                            query_to_update = {'_id': _id}
                                            res = equity_position_collection.update_one(query_to_update, new_data)
                                            self.logger.info(f"[sync_position_add] update_success (res){res}")

                                            query_for_delete_add = {'sid' : sid , 'accountName' : account_name}
                                            equity_position_collection.delete_one(query_for_delete_add)
                                            self.logger.info(f"delete_position (sid){sid}")
                                            break
                                        elif pos < 0:
                                            data_to_update ={
                                                                'yd_pos_long' : 0,
                                                                'actual_yd_pos_long' : 0
                                                            }
                                            new_data = {"$set": data_to_update}
                                            query_to_update = {'_id': _id}
                                            res = equity_position_collection.update_one(query_to_update, new_data)
                                            self.logger.info(f"[sync_position_add] update_to_0 (res){res}")
                                            actual_yd_pos_long = pos
                                            #yd_pos_long = pos
                                                
                                query_for_delete_add = {'sid' : sid , 'accountName' : account_name}
                                equity_position_collection.delete_one(query_for_delete_add)
                                self.logger.info(f"delete_position (sid){sid}")
                            
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[sync_position_for_add] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)                      
                            
            
    def add_position_for_add(self, acc, exchange, ticker, td_vol, yd_vol, accountName, sid):
        try:
            collection = self.order_info_db[acc]['EquityPosition']
            #collection = self.test_trading_account['EquityPosition']
            #exchange = int(pos['exchange'])
            order_collection = self.order_info_db[acc]['ft_order']
    
            total_vol = td_vol + yd_vol
            self.logger.warning(
                f'[add_position_for_debug] add_position (ticker){ticker} (total_vol){total_vol}')
            record = {}
            record['accountName'] = accountName
            record['ticker'] = ticker
            record['yd_pos_long'] = yd_vol
            record['yd_pos_short'] = 0
            record['td_pos_long'] = td_vol
            record['td_pos_short'] = 0
            record['actual_td_pos_long'] = td_vol
            record['actual_yd_pos_long'] = yd_vol
            # 持仓平均成本 非凸只返回仓位,无法计算cost,和market_value
            record['cost'] = 0
            record['mkt_value'] = 0
            record['enter_date'] = datetime.now(timezone.utc)
            record['holding_days'] = 0
            record['sid'] = sid
            record['exchange'] = exchange
            filter = {'sid' : record['sid'], 'accountName' : accountName}
            res = collection.replace_one(filter, record, True) 
            self.logger.info(f"[add_position_for_debug] (res){res} (msg){record}")
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[add_position_for_add] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)          

    def update_position_date_open(self):
        for acc in self.accounts_run:
            collection = self.order_info_db[acc]['EquityPosition']
            target_accountname = self.target_account_names[acc]
            targets_query = {'accountName' : target_accountname}
            targets = collection.find(targets_query)
            self.logger.info(f"now (target_account_name){target_accountname}")
            if targets.count() == 0:
                continue
            for position in targets:
                        self.logger.info(f"goes in (position){position}")
                        sid = position['sid']
                        query = {'sid' : sid, 'accountName' : target_accountname}
                        holdingdays = position['holding_days']
                        yd_pos = position['actual_td_pos_long'] + position['actual_yd_pos_long']
                        td_pos = 0
                        change = {
                                        'holding_days': holdingdays,
                                        'yd_pos_long': yd_pos,
                                        'td_pos_long': td_pos,
                                        'actual_yd_pos_long': yd_pos,
                                        'actual_td_pos_long': td_pos
                                    }
                        new_data = {"$set": change}
                        res = collection.update_one(
                                                query, new_data, True)
                        self.logger.info(f"[date_change_open] (res){res} (change){change}")
    
    def update_position_date_close(self):
        for acc in self.accounts_run:
            collection = self.order_info_db[acc]['EquityPosition']
            target_accountname = self.target_account_names[acc]
            targets_query = {'accountName' : target_accountname}
            targets = collection.find(targets_query)
            if targets.count() == 0:
                continue
            for position in targets:
                    sid = position['sid']
                    query = {'sid' : sid, 'accountName': target_accountname}
                    holdingdays = position['holding_days'] + 1
                    yd_pos = position['actual_td_pos_long'] + position['actual_yd_pos_long']
                    td_pos = 0
                            
                    change = {
                                        'holding_days': holdingdays,
                                        'yd_pos_long': yd_pos,
                                        'td_pos_long': td_pos,
                                        'actual_yd_pos_long': yd_pos,
                                        'actual_td_pos_long': td_pos
                                    }
                    new_data = {"$set": change}
                    res = collection.update_one(
                                                query, new_data, True)
                    self.logger.info(f"[date_change_close] (res){res} (sid){sid} (change){change}")

    def sync_position(self):
        try:
            for acc in self.accounts_run:
                ft_position_collection =  self.order_info_db[acc]['ft_position']
                account_id = self.account_id[acc]
                all_position_query = {"trade_acc": account_id}
                targets = ft_position_collection.find(all_position_query)

                if targets.count() > 0:
                    for pos in targets:
                        ticker = pos['ticker']
                        total_vol = pos['total_vol']
                        yd_vol = pos['avail_vol']
                        td_vol = total_vol - yd_vol
                        lock_vol = pos['lock_vol']
                        accountName = self.target_account_names[acc]
                        query = {'ticker': ticker, 'accountName': accountName}
                        EquityPosition_targets = self.order_info_db[acc]['EquityPosition'].find(query)
                        if EquityPosition_targets.count() == 0 and not pos['ticker'] == '' and not total_vol == 0:
                            self.add_position_for_new_order(acc, pos, ticker, td_vol, yd_vol, accountName)
                        elif not pos['ticker'] == '':
                            td_vol_indb = 0
                            yd_vol_indb = 0
                            if EquityPosition_targets.count() == 1: #在同一ticker只有一单时可自动处理，否则需要前往数据库手动处理 
                                target_to_update = self.order_info_db[acc]['EquityPosition'].find_one(query)
                                td_vol_indb = target_to_update['actual_td_pos_long']
                                yd_vol_indb = target_to_update['actual_yd_pos_long']
                                total_vol_indb = td_vol_indb + yd_vol_indb
                                if  not total_vol == total_vol_indb:
                                        self.update_position(target_to_update ,acc, pos, ticker, td_vol, yd_vol, accountName)
                            else:
                                for target in EquityPosition_targets:
                                    sid = target['sid']
                                    td_vol_indb += target['actual_td_pos_long']
                                    yd_vol_indb += target['actual_yd_pos_long']
                                    self.logger.info(f"[sync_position] (ticker){ticker} (yd_vol_indb){yd_vol_indb} (td_vol_indb){td_vol_indb}")
                                total_vol_indb = td_vol_indb + yd_vol_indb
                                if  not total_vol == total_vol_indb: #在同一ticker只有一单时可自动处理，否则需要前往数据库手动处理
                                    sync_td_vol = td_vol - td_vol_indb
                                    sync_yd_vol = yd_vol - yd_vol_indb 
                                    self.add_position_for_debug(acc, pos, ticker, sync_td_vol, sync_yd_vol ,accountName)
                else:
                    self.logger.warning(f"[sync_position]can't_find_positions (trade_acc){account_id}")
                                
                self.logger.info(f"[sync_position] sync_position_finished (trade_acc){account_id}")
            
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[sync_position] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def update_position(self, target, acc, pos, ticker, td_vol, yd_vol,accountName):
        try:
            collection = self.order_info_db[acc]['EquityPosition']
            sid = target['sid']
            update_filter = {'sid': sid, 'accountName' : accountName}
            update_record = {
                'td_pos_long': td_vol,
                "yd_pos_long": yd_vol,
                'actual_td_pos_long' : td_vol,
                'actual_yd_pos_long' : yd_vol
            }
            new_data = {"$set": update_record}
            res = collection.update_one(update_filter, new_data)
            self.logger.info(f"[update_position] (res){res} (sid){sid} (msg){update_record}")

        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[update_position] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            
    def add_position_for_new_order(self, acc, pos, ticker, td_vol, yd_vol, accountName):
        try:
            sid = '[ADD]' + self.generate_sid(ticker)
            collection_for_sid =  self.order_info_db[acc]['ft_proposed_target']
            query_for_find_sid = {"stock_code": ticker, "target_account_name": accountName}
            new_target = collection_for_sid.find_one(query_for_find_sid)
            if not new_target == None:
                sid = new_target['sid']

            collection = self.order_info_db[acc]['EquityPosition']
            #collection = self.test_trading_account['EquityPosition']
            exchange = int(pos['exchange'])
            order_collection = self.order_info_db[acc]['ft_order']
    
            total_vol = td_vol + yd_vol
            self.logger.warning(
                f'[add_position_for_new_order] add_position (ticker){ticker} (total_vol){total_vol}')
            record = {}
            record['accountName'] = accountName
            record['ticker'] = ticker
            record['yd_pos_long'] = yd_vol
            record['yd_pos_short'] = 0
            record['td_pos_long'] = td_vol
            record['td_pos_short'] = 0
            record['actual_td_pos_long'] = td_vol
            record['actual_yd_pos_long'] = yd_vol
            # 持仓平均成本 非凸只返回仓位,无法计算cost,和market_value
            record['cost'] = 0
            record['mkt_value'] = 0
            record['enter_date'] = datetime.now(timezone.utc)
            record['holding_days'] = 0 
            record['sid'] = sid
            record['exchange'] = exchange
            filter = {'sid' : record['sid'], 'accountName': accountName}
            res = collection.replace_one(filter, record, True) 
            self.logger.info(f"[add_position_for_new_order] (res){res} (msg){record}")
            
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[add_position_for_new_order] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def add_position_for_debug(self, acc, pos, ticker, td_vol, yd_vol, accountName):
        try:
            collection = self.order_info_db[acc]['EquityPosition']
            #collection = self.test_trading_account['EquityPosition']
            exchange = int(pos['exchange'])
            order_collection = self.order_info_db[acc]['ft_order']
    
            total_vol = td_vol + yd_vol
            self.logger.warning(
                f'[add_position_for_debug] add_position (ticker){ticker} (total_vol){total_vol}')
            record = {}
            record['accountName'] = accountName
            record['ticker'] = ticker
            record['yd_pos_long'] = yd_vol
            record['yd_pos_short'] = 0
            record['td_pos_long'] = td_vol
            record['td_pos_short'] = 0
            record['actual_td_pos_long'] = td_vol
            record['actual_yd_pos_long'] = yd_vol
            # 持仓平均成本 非凸只返回仓位,无法计算cost,和market_value
            record['cost'] = 0
            record['mkt_value'] = 0
            record['enter_date'] = datetime.now(timezone.utc)
            record['holding_days'] = 0 
            record['sid'] = '[ADD]' + self.generate_sid(ticker)
            record['exchange'] = exchange
            filter = {'sid' : record['sid'], 'accountName': accountName}
            res = collection.replace_one(filter, record, True) 
            self.logger.info(f"[add_position_for_debug] (res){res} (msg){record}")
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[add_position_for_debug] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def update_position_with_record(self, trade_vol, order, sid , side, trade_amt, trade_price):
        try:
            target_accountname = order['target_account_name']
            acc = self.target_account_names_to_acc[target_accountname]
            query = {'sid': sid, 'accountName': target_accountname}
            position_collection = self.order_info_db[acc]['EquityPosition']
            position = position_collection.find_one(query)
            if position is None and trade_vol > 0:
                td_trade_vol = trade_vol

                amt = trade_amt

                ticker = order['stock_code']
                yd_pos = 0
                mkt_value = amt
                cost = trade_price
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
            elif not position is None and trade_vol > 0:
                #print(position)
                yd_pos = position['actual_yd_pos_long']
                yd_pos_long = position['yd_pos_long']
                td_trade_vol = position['actual_td_pos_long']
                mkt_value = position['mkt_value']
                amt = trade_amt
                if side == 1:
                    td_trade_vol = position['actual_td_pos_long'] + trade_vol
                    mkt_value = position['mkt_value'] + amt
                elif side == 2 :
                    td_trade_vol = position['actual_td_pos_long'] - trade_vol
                    yd_pos_long -= trade_vol
                    mkt_value = position['mkt_value'] - amt
                else:
                    self.logger.error(f"[update_position] side not supported")
                
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
            self.logger.error(f'[update_position_with_csv] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def get_update_position_from_csv(self):
        try:
            csv_path = Path(self.ft_zidan_message_path)
            for acc in self.accounts_run:
                ft_order_collection = self.order_info_db[acc]['ft_order']
                
                record_list = []
                product_name = self.product_names[acc]
                trade_acc = self.account_id[acc]
                #TODO don't use hard code like this 
                if product_name == "指增1号-华鑫":
                    product_name = "盖亚青柯指增1号"
                path_head = product_name + '_' + trade_acc + '_母单'
                for file in csv_path.glob("*.csv"):
                    print(f"[get_update_position_from_csv] {file}")
                    if file.stem.startswith(path_head):
                        with open(file, encoding='utf-8-sig') as f:
                            reader = csv.reader(f)
                            headers = next(reader)
                            Row = namedtuple('Row', headers)
                            for row in reader:
                                row = Row(*row)
                                side = 0
                                traded_vol = int(row.成交数量)
                                traded_price = float(row.成交均价)
                                if row.买卖标识 == '买入':
                                    side = 1
                                elif row.买卖标识 == '卖出':
                                    side = 2
                                int_ticker = int(row.证券代码)
                                ticker = f'{int_ticker:06d}'
                                mudan_id = int(row.母单编号)
                                origin_order_query = {"mudan_id" : mudan_id}
                                order_target = ft_order_collection.find_one(origin_order_query)
                                order = order_target['order_msg']
                                sid = row.所属篮子
                                target_account_name = self.target_account_names[acc]
                                #oid = order_target['oid']
                                trade_amt = traded_vol * traded_price
                                self.update_position_with_record(traded_vol, order, sid, side, trade_amt, traded_price)
                        os.remove(file)
                        self.logger.info(f"[get_position_from_csv_in_trading] delete_csv (file_name){file.name}")
            
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[get_update_position_from_csv] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    
    def restore_pos(self):
        try:
            for acc in self.accounts_run:
                db_tradingaccount = self.order_info_db[acc]
                log_accountname = self.log_account_names[acc]
                today = datetime.today()
                date_str = today.strftime('%Y-%m-%d')
                df = pd.DataFrame(list(self.db_dashboard['daily_equity_position'].find(
                    {'account_name': log_accountname, 'date': date_str, 'time': 'open'}
                )))
                df = df.rename(columns={'tg_name': 'accountName'}).drop(columns=['date', 'time', 'created_at', 'account_name'])
                df[['enter_date', 'update_date', 'hedgeInstrument']] = df[['enter_date', 'update_date', 'hedgeInstrument']].astype(object).where(df[['enter_date', 'update_date', 'hedgeInstrument']].notnull(), None)
                db_tradingaccount['EquityPosition'].delete_many(
                    {'accountName': {'$regex': log_accountname}}
                )

                db_tradingaccount['EquityPosition'].insert_many(df.to_dict('records'))
                print("[restore_pos] restored acc:{acc}")
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(f'[restore_pos] (exception){err}')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)

    def generate_sid(self, ticker, exchange=None) -> str:
        sid = str(int(datetime.today().timestamp())) + '[T]' + ticker
        if exchange is not None:
            sid += '[E]' + str(exchange)
        return sid


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.') 

if __name__ == "__main__":

    description = "sync trade,pos,add for ftsever"
    parser = argparse.ArgumentParser(description=description)

    _file_name = "C:\\Users\\Administrator\\Desktop\\ft_batandjson\\ft_fix_setting.json"
    _date = datetime.now().strftime("%Y%m%d")
    parser.add_argument('-m', '--config_filename', dest='config_filename', type=str, default=_file_name)
    parser.add_argument('-e', '--trade_date', dest='update_trade_date', type=str, default=_date)
    parser.add_argument('-t', '--sync_trade', dest='sync_trade', type=str2bool, default='T')
    parser.add_argument('-p', '--sync_pos', dest='sync_pos', type=str2bool, default='T')
    parser.add_argument('-a', '--sync_add', dest='sync_add', type=str2bool, default='F')
    parser.add_argument('-i', '--sync_trade_in_trading', dest='sync_trade_in_trading',type=str2bool, default='F')
    parser.add_argument('-s', '--sync_pos_in_trading', dest='sync_pos_in_trading',type=str2bool, default='F')

    args = parser.parse_args()
    print (f"(args){args}")

    td = FtTool(args.config_filename, args.update_trade_date, args.sync_pos, args.sync_trade, args.sync_add, args.sync_trade_in_trading, args.sync_pos_in_trading)

    td.start()