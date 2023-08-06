ENCODING = 'gb2312'
GATEWAY_NAME = 'atx'


class FILES:
    TASKS = 'OrderAlgo_'  #下单
    CANCEL = 'CancelOrderAlgo_' 
    ORDERS = 'ReportOrderAlgo_'
    TRADES = 'SubOrderAlgo_' 
    POSITIONS  = 'ReportPosition_'
    ACCOUNTS = 'ReportBalance_'

#Exchange in tlclient
class Exchange:
    EXCHANGE_UNSPECIFIED = 0
    EXCHANGE_TRADITIONAL = 100 # 表示传统金融
    EXCHANGE_SSE = 101       #  上海证券交易所
    EXCHANGE_SZE = 102


class OrderType:
    ORDER_TYPE_UNSPECIFIED = 0

    ORDER_TYPE_PLAIN_ORDER_PREFIX = 10
    ORDER_TYPE_ALGO_ORDER_PREFIX = 20
    ORDER_TYPE_BASKET_ORDER_PREFIX = 30

    ORDER_TYPE_PLAIN = 100  # 普通单
    ORDER_TYPE_LIMIT = 101  # 限价单
    ORDER_TYPE_MARKET = 102 # 市价单
    ORDER_TYPE_FAK = 103    # 立即成交且剩余撤销（深）
    ORDER_TYPE_FOK = 104    # 立即成交或全部撤销（深）
    ORDER_TYPE_ANY = 105
    ORDER_TYPE_FAK_BEST_5 = 106 # 最优五档立即成交剩余撤销（沪、深）
    ORDER_TYPE_FORWARD_BEST = 107 # 己方最优价（深）
    ORDER_TYPE_REVERSE_BEST = 108 # 对手最优价（深）
    ORDER_TYPE_BEST_5_OR_LIMIT = 109 # 最优五档立即成交剩余转限价（沪）

    ORDER_TYPE_ALGO = 200   # 算法单
    ORDER_TYPE_TWAP = 201   # TWAP算法单
    ORDER_TYPE_VWAP = 202
    ORDER_TYPE_ZC_SMART = 210
    ORDER_TYPE_KF_TWAP_PLUS = 211
    ORDER_TYPE_KF_VWAP_PLUS = 212
    ORDER_TYPE_JN_G_PXINLINE = 213
    ORDER_TYPE_VOLUME_INLINE = 214
    ORDER_TYPE_FT_AIWAP = 215

    ORDER_TYPE_BASKET = 300
    ORDER_TYPE_SINGLE_DAY_BASKET = 301

class EXCHANGE_TYPE:
    SSE = 'SH'
    SZE = 'SZ'


class ORDER_SIDE:
    BUY  = 1  # 股票买入, 或沪港通、深港通股票买入
    SELL = 2  # 股票卖出, 或沪港通、深港通股票卖出
    SIDE_SECURITIES_BUY = 3
    SIDE_FINANCING_SELL = 4
    SIDE_FINANCING_BUY = 5
    SIDE_SECURITIES_SELL = 6

class Side:
    SIDE_UNSPECIFIED = 0
    SIDE_BUY = 1               # 买(担保品买入)
    SIDE_SELL = 2              # 卖(担保品卖出)
    SIDE_FINANCING_BUY = 3     # 融资买入
    SIDE_FINANCING_SELL = 4    # 融券卖出
    SIDE_SECURITIES_BUY = 5    # 买券还券
    SIDE_SECURITIES_SELL = 6   # 卖券还款
    SIDE_SURSTK_TRANS = 7      # 余券划转
    SIDE_STOCK_REPAY_STOCK = 8 # 现券还券

class OrderStatus:
    ORDER_STATUS_UNSPECIFIED = 0
    ORDER_STATUS_UNKNOWN = 1               # 未知
    ORDER_STATUS_INIT = 10                 # 未报
    ORDER_STATUS_PROPOSED = 100            # 已报
    ORDER_STATUS_PENDING_PROPOSE = 101     # 待报
    ORDER_STATUS_PROPOSING = 102           # 正报
    ORDER_STATUS_RESPONDED = 200           # 已响应
    ORDER_STATUS_QUEUEING = 300            # 排队中
    ORDER_STATUS_NO_TRADE_QUEUEING = 301   # 未成交
    ORDER_STATUS_PART_TRADE_QUEUEING = 302 # 部分成交
    ORDER_STATUS_TO_CANCEL = 370           # 待撤销
    ORDER_STATUS_PENDING_MAX = 399

    ORDER_STATUS_REJECTED = 400            # 已拒绝
    ORDER_STATUS_REJECT_BY_ROUTER = 401    # 路由拒单
    ORDER_STATUS_REJECT_BY_GATEWAY = 402   # 网关拒单
    ORDER_STATUS_REJECT_BY_EXCHANGE = 403  # 交易所拒单
    ORDER_STATUS_REJECT_BY_RISK_MGR = 404  # 风控拒单
    ORDER_STATUS_CANCEL_FAILED = 405       # 撤单失败

    ORDER_STATUS_CANCELED = 600            # 已撤销
    ORDER_STATUS_NO_TRADE_CANCELED = 601   # 全部撤单
    ORDER_STATUS_PART_TRADE_CANCELED = 602 # 部成已撤
    ORDER_STATUS_ALL_TRADED = 700          # 全部成交

class SecurityType:
    SECURITY_TYPE_UNSPECIFIED = 0
    SECURITY_TYPE_TRADITIONAL = 100  # 表示传统金融
    SECURITY_TYPE_STOCK = 101        # 股票
    SECURITY_TYPE_FUTURE = 102       # 期货
    SECURITY_TYPE_BOND = 103         # 债券
    SECURITY_TYPE_STOCK_OPTION = 104 # 股票期权
    SECURITY_TYPE_FUND = 105         # 基金
    SECURITY_TYPE_TECH_STOCK = 106   # 科创板
    SECURITY_TYPE_INDEX = 107        # 指数
    SECURITY_TYPE_REPO = 108         # 逆回购
    SECURITY_TYPE_IPO = 109          # 新股申购

    SECURITY_TYPE_CRYPTO = 200       # 数字货币
    SECURITY_TYPE_C_SPOT = 201       # 现货
    SECURITY_TYPE_C_MARGIN = 202     # 现货杠杆
    SECURITY_TYPE_C_FUTURE = 203     # 交割合约
    SECURITY_TYPE_C_SWAP = 204       # 永续合约
    SECURITY_TYPE_C_OPTION = 205     # 期权


class AlgoType:
    ALGO_TYPE = 0
    FT_VWAP_PLUS  = 204 #ft