from datetime import datetime
import sys
import os

from constants import ORDER_SIDE
import requests
import traceback
import json

def to_ft_flags(side):
    ft_flags = ""
    if side == ORDER_SIDE.BUY:
        ft_flags = "buy"
    elif side == ORDER_SIDE.SELL:
        ft_flags = "sell"

    return ft_flags


def decode_ft_flag(flag):
    if flag == 1:
        side = ORDER_SIDE.BUY
    elif flag == 2:
        side == ORDER_SIDE.SELL
    
    return side



def decode_exchange_id(exchange_id):
    exchange = 0
    if exchange_id == 3553:
        exchange = 101        #EXCHANGE_SSE 
    elif exchange_id == 3554:
        exchange = 102        #EXCHANGE_SZE 
    
    return exchange
    
def get_log_default_path():
    # python2: linux2, python3: linux
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        dirs = "/shared/log"
    elif sys.platform == "win32":
        dirs = os.path.join(get_windows_first_disk() + "/tmp/linker/log")
    else:
        dirs = '.'

    return dirs

def get_today_date():
    return datetime.today().strftime('%Y-%m-%d')

def get_digit_from_env(env_name, default_num):
    num = str(os.environ.get(env_name))
    return int(num) if num.isdigit() else default_num

def get_log_given_path(path):
    dirs = os.path.join(path)
    return path

def send_to_user(logger, url_list, msg):
        try:
            if len(url_list) == 0:
                logger.info("[send_to_user] send_message_failed")
                return
            
            payload_message_feishu = {
                "msg_type": "text",
                "content": {
                    "text": msg
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload_message_dingding = {
                "msgtype": "text",
                "text": {"content": msg},
                "at": {
                    "atMobiles": [""],
                    "isAtAll": "false"  # @所有人 时为true，上面的atMobiles就失效了
                }
            }
            response = requests.request("POST", url_list[0], headers=headers, data=json.dumps(payload_message_feishu))
            data = response.json()
            logger.info(f"[send_to_user] (response){response} (data){data}")
            if len(url_list) > 1: 
                response_ding = requests.request("POST", url_list[1], headers=headers, data=json.dumps(payload_message_dingding))
                data_ding = response_ding.json()
                logger.info(f"[send_to_user] (response){response_ding} (data){data_ding}")
        except Exception as e:
            err = traceback.format_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            logger.error(f'[send_to_user] send_message_failed(exception){err}')