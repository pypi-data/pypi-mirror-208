import sys
import argparse
import traceback
import json
from datetime import datetime

from mongo_client_gateway import MongoClientTradeGateway
from constants import (ENCODING, FILES, GATEWAY_NAME, Exchange, OrderStatus, OrderType, SecurityType, Side)

class AtxTool(MongoClientTradeGateway):
    def __init__(self, config_filename, sync_pos,  endtime):
        MongoClientTradeGateway.__init__(self, config_filename, endtime)
        self.update_trade_date = self.date
        self.sync_pos = sync_pos
        self.load_tool_setting(config_filename)

    def load_tool_setting(self, config_filename):
        try:
            #config_filename = os.path.join(config_path, 'atx_server_config.json')
            f = open(config_filename, encoding='gbk')
            setting = json.load(f)
            #self.recv_msg_dir = setting['recv_msg_path'].replace('/', '\\')
            self.sync_position_open = setting['sync_position_open']
            self.sync_position_close = setting['sync_position_close']

        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            print(f"load config failed! (exception){err}")
            exit(0)
    
    def start(self):
        
        if self.sync_pos == True:
            self.date_change()
            _msg = "[atx_tool_date_change] executed"
            self.send_to_user(logger=self.logger, url_list=self.url_list, msg=_msg)
    
    @MongoClientTradeGateway.error_handler
    def date_change(self):
        dt = datetime.now()
        self.logger.info(f"(dt){dt.hour}")
        if dt.hour <= self.sync_position_open and self.sync_pos == True:
            self.logger.info("[date_change] date_change_open")
            self.update_position_date_open()
        elif dt.hour < self.sync_position_close and dt.hour > self.sync_position_open:
            self.logger.info("[date_change] date_not_change")
        elif dt.hour >= self.sync_position_close and self.sync_pos == True:
            self.logger.info("[date_change] date_change_close")
            self.update_position_date_close()
        else:
            self.logger.info("[date_change] date_not_change")
            return


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
                    holding_days = position['holding_days'] + 1
                    yd_pos = position['actual_td_pos_long'] + position['actual_yd_pos_long']
                    td_pos = 0
                            
                    change = {
                                        'holding_days': holding_days,
                                        'yd_pos_long': yd_pos,
                                        'td_pos_long': td_pos,
                                        'actual_yd_pos_long': yd_pos,
                                        'actual_td_pos_long': td_pos
                                    }
                    new_data = {"$set": change}
                    res = collection.update_one(
                                                query, new_data, True)
                    self.logger.info(f"[date_change_close] (res){res} (sid){sid} (change){change}")

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

    description = "sync pos for atx_server"
    parser = argparse.ArgumentParser(description=description)

    _file_name = "C:\\Users\\Administrator\\Desktop\\atx_batandconfig\\atx_tool_setting.json"
    _date = datetime.now().strftime("%Y%m%d")
    parser.add_argument('-m', '--config_filename', dest='config_filename', type=str, default=_file_name)
    parser.add_argument('-p', '--date_change', dest='date_change', type=str2bool, default='T')
    end_time = "19:00"
    args = parser.parse_args()
    print (f"(args){args}")

    td = AtxTool(args.config_filename, args.date_change,end_time)

    td.start()