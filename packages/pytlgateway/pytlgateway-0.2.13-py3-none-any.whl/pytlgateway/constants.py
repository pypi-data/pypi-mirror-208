

class ORDER_SIDE:
    BUY  = 1
    SELL = 2
    MB =  11 #融资买入
    RS =  22 #卖券还款
    SS =  12 #融券卖出
    RB =  21 #买券还券

    
class DATA_STATUS:
    UNSUBMITTED : 0 #初始化未完成
    SUBMITTED : 1   #报单插入柜台成功
    STOP : 2 #暂停
    FILLED : 3 #完成
    CANCELLED : 4 #取消
    FAILED : 6 #错单废单