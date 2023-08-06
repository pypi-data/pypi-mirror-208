from datetime import datetime
import sys
import os

from constants import ORDER_SIDE, Side



#没有融券
def decode_atx_side(side):
    rtn_trade_side = 0
    if side == 1:
        rtn_trade_side = 1
    elif side == 2:
        rtn_trade_side = 2
    elif side == 5:
        rtn_trade_side = 3
    return rtn_trade_side

def decode_atx_target_type(side):
    f_side = 0
    if side in [1,5]:
        return 1
    elif side == 2:
        return 2

def decode_atx_status(status):
    new_status = ""
    if status == 0:
        new_status = 'active'
    elif status == 2:
        new_status = 'filled'
    elif status == 4:
        new_status = 'canceled'
    return new_status

def side_to_target_type(side):
    target_type = ""
    if side in [1,5]:
        target_type = "buy"
    elif side == 2:
        target_type = "sell"
    return target_type

def decode_exchange_id(exchange):
    exchange = 0
    if exchange == 'SH':
        exchange = 101        #EXCHANGE_SSE 
    elif exchange == 'SZ':
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
    return datetime.today().stratxime('%Y-%m-%d')

def get_digit_from_env(env_name, default_num):
    num = str(os.environ.get(env_name))
    return int(num) if num.isdigit() else default_num

def get_log_given_path(path):
    dirs = os.path.join(path)
    return path

def decode_ordtype(order_type:str):
    ord_type = -1
    mapping = {
        'kf_twap_plus': 101,
        'kf_vwap_plus': 102,
        'kf_twap_core': 103,
        'kf_vwap_core': 104,
        'kf_pov_core': 105,
        'kf_t0': 106,
        'kf_passthru': 201,
        'ft_vwap_ai': 202,
        'ft_twap_ai': 203,
        'ft_vwap_ai_plus': 204,
        'ft_twap_ai_plus': 205
    }
    ord_type = mapping.get(order_type, -1)
    return ord_type
