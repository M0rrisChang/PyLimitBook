import redis
import pickle

rs = redis.Redis(host='127.0.0.1', port=6379, db=0)
global_trade_id = 0

# get from redis and unpickle
#unpacked_object = pickle.loads(rs.get('c'))


def get_bid_by_id(userid, pop=True):
    l = rs.lrange("bid_uid", 0, -1)
    for i in l:
        if int(i) == userid:
            price = rs.get("bid_price_%d" %(userid))
            amount = rs.get("bid_amount_%d" %(userid))
            timestamp = rs.get("bid_timestamp_%d" %(userid))
            ## delete it
            if pop:
                rs.lrem("bid_uid", i)
                rs.delete("bid_price_%d" %(userid))
                rs.delete("bid_amount_%d" %(userid))
                rs.delete("bid_timestamp_%d" %(userid))
            return Bid(price, amount, userid, timestamp)
    return None

def get_ask_by_id(userid, pop=True):
    l = rs.lrange("ask_uid", 0, -1)
    for i in l:
        if int(i) == userid:
            price = rs.get("ask_price_%d" %(userid))
            amount = rs.get("ask_amount_%d" %(userid))
            timestamp = rs.get("ask_timestamp_%d" %(userid))
            if pop:
                ## delete it
                rs.lrem("ask_uid", i)
                rs.delete("ask_price_%d" %(userid))
                rs.delete("ask_amount_%d" %(userid))
                rs.delete("ask_timestamp_%d" %(userid))
            return Ask(price, amount, userid, timestamp)
    return None


class Trade(object):
    def __init__(self, price, amount, id1, id2, trade_id):
        self.price = int(price)
        self.amount = int(amount)
        self.trade_id = int(trade_id)
        self.id1 = int(id1)
        self.id2 = int(id2)

    def save_to_db(self):
        rs.lpush("trade_id", self.trade_id)
        rs.hset("trade_id1", self.trade_id, self.id1)
        rs.hset("trade_id2", self.trade_id, self.id2)
        rs.hset("trade_amount", self.trade_id, self.amount)
        rs.hset("trade_price", self.trade_id, self.price)

    def to_dict():
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        d["timestamp"] = self.trade_id
        return d


class Bid(object):
    def __init__(self, price, amount, userid, timestamp):
        self.price = int(price)
        self.userid = int(userid)
        self.timestamp = int(timestamp)
        self.amount = int(amount)

    def save_to_db(self):
        rs.lpush("bid_uid", self.userid)
        rs.set("bid_price_%d" %(self.userid), self.price)
        rs.set("bid_amount_%d" %(self.userid), self.amount)
        rs.set("bid_timestamp_%d" %(self.userid), self.timestamp)

    def to_dict():
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        return d

class Ask(object):
    def __init__(self, price, amount, userid, timestamp):
        self.price = int(price)
        self.userid = int(userid)
        self.timestamp = int(timestamp)
        self.amount = int(amount)

    def save_to_db(self):
        rs.lpush("ask_uid", self.userid)
        rs.set("ask_price_%d" %(self.userid), self.price)
        rs.set("ask_amount_%d" %(self.userid), self.amount)
        rs.set("ask_timestamp_%d" %(self.userid), self.timestamp)


    def to_dict():
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        return d



def new_bid(price, amount, userid, timestamp):
    bid = get_bid_by_id(userid)
    if bid != None:
        print("there's same tic exist")
    bid = Bid(price, amount, userid, timestamp)
    if amount != 0 and price != 0:
        bid.save_to_db()
    else:
        print("rm ask", userid)

def new_ask(price, amount, userid, timestamp):
    ask = get_ask_by_id(userid)
    if ask != None:
        print("there's same tic exist")
    ask = Ask(price, amount, userid, timestamp)
    if amount != 0 and price != 0:
        ask.save_to_db()
    else:
        print("rm ask", userid)

def get_high_ask():
    if rs.llen("ask_uid")==0:
        return None
    unpacked_object = get_ask_by_id(int(rs.sort("ask_uid", by='ask_price_*', desc=True)[0]), False)
    return unpacked_object

def get_low_bid():
    if rs.llen("bid_uid")==0:
        return None

    unpacked_object = get_bid_by_id(int(rs.sort("bid_uid", by='bid_price_*')[0]), False)
    return unpacked_object

def get_asks(count):
    r = []
    if rs.llen("ask_uid")<count:
        return False
    l = rs.lrange("ask_uid", 0, count-1)
    for i in l:
        unpacked_object = get_ask_by_id(int(i), False)
        r.append(unpacked_object)
    return r

def get_bids(count):
    r = []
    l = rs.lrange("bid_uid", 0, count-1)
    for i in l:
        unpacked_object = get_bid_by_id(int(i), False)
        r.append(unpacked_object)
    return r

def new_deal(price, amount, id1, id2, trade_id):
    deal = Trade(price, amount, id1, id2, trade_id)
    deal.save_to_db()
    print(price, amount, id1, id2)
    return True

def get_deals(num):
    r = []
    l = rs.lrange("trade_id", 0, num-1)
    for i in l:
        id1 = rs.hget("trade_id1", int(i))
        id2 = rs.hget("trade_id1", int(i))
        amount = rs.hget("trade_id1", int(i))
        price = rs.hget("trade_id1", int(i))
        r.append(Trade(price, amount, id1, id2, int(i)))
    return r

def match():
    try:
        ask = get_high_ask()
        bid = get_low_bid()
        if ask.price >= bid.price:
            deal_price = bid.price
            if ask.amount > bid.amount:
                deal_amount = int(bid.amount)
            else:
                deal_amount = int(ask.amount)
            if new_deal(deal_price, deal_amount, ask.userid, bid.userid, int(rs.get("global_trade_id"))):
                rs.set("global_trade_id", int(rs.get("global_trade_id")) + 1)

            new_bid(bid.price, int(bid.amount)-deal_amount, bid.userid, bid.timestamp)
            new_ask(ask.price, int(ask.amount)-deal_amount, ask.userid, ask.timestamp)
            ## match
            return True
        return False
    except Exception as e:
        print(e)
        return False
