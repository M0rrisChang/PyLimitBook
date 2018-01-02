import redis
import pickle
import os

print ("============,", os.environ['REDIS_HOST'])
rs = redis.Redis(host=os.environ['REDIS_HOST'], port=6379, db=0)
rs.set("defaultglobal_trade_id", 0)


# get from redis and unpickle
#unpacked_object = pickle.loads(rs.get('c'))

def put_default(pair):
    if rs.get(pair+"global_trade_id") is None:
        rs.set(pair + "global_trade_id", 0)

def get_bid_by_id(userid, pop=True, pair = "default"):
    l = rs.lrange(pair + "bid_uid", 0, -1)
    for i in l:
        if int(i) == userid:
            price = rs.get(pair + "bid_price_%d" %(userid))
            amount = rs.get(pair + "bid_amount_%d" %(userid))
            timestamp = rs.get(pair + "bid_timestamp_%d" %(userid))
            ## delete it
            if pop:
                rs.lrem(pair+ "bid_uid", i)
                rs.delete(pair + "bid_price_%d" %(userid))
                rs.delete(pair + "bid_amount_%d" %(userid))
                rs.delete(pair + "bid_timestamp_%d" %(userid))
            return Bid(price, amount, userid, timestamp, pair)
    return None

def get_ask_by_id(userid, pop=True, pair = "default"):
    l = rs.lrange(pair + "ask_uid", 0, -1)
    for i in l:
        if int(i) == userid:
            price = rs.get(pair + "ask_price_%d" %(userid))
            amount = rs.get(pair + "ask_amount_%d" %(userid))
            timestamp = rs.get(pair + "ask_timestamp_%d" %(userid))
            if pop:
                ## delete it
                rs.lrem(pair + "ask_uid", i)
                rs.delete(pair + "ask_price_%d" %(userid))
                rs.delete(pair + "ask_amount_%d" %(userid))
                rs.delete(pair + "ask_timestamp_%d" %(userid))
            return Ask(price, amount, userid, timestamp, pair)
    return None


class Trade(object):
    def __init__(self, price, amount, id1, id2, trade_id, pair):
        self.price = int(price)
        self.amount = int(amount)
        self.trade_id = int(trade_id)
        self.id1 = int(id1)
        self.id2 = int(id2)
        self.pair = pair

    def save_to_db(self):
        rs.lpush(self.pair + "trade_id", self.trade_id)
        rs.hset(self.pair + "trade_id1", self.trade_id, self.id1)
        rs.hset(self.pair + "trade_id2", self.trade_id, self.id2)
        rs.hset(self.pair + "trade_amount", self.trade_id, self.amount)
        rs.hset(self.pair + "trade_price", self.trade_id, self.price)

    def to_dict(self):
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        d["timestamp"] = self.trade_id
        d["pair"] = self.pair
        return d


class Bid(object):
    def __init__(self, price, amount, userid, timestamp, pair = "default"):
        self.price = int(price)
        self.userid = int(userid)
        self.timestamp = int(timestamp)
        self.amount = int(amount)
        self.pair = pair

    def save_to_db(self):
        rs.lpush(self.pair + "bid_uid", self.userid)
        rs.set(self.pair + "bid_price_%d" %(self.userid), self.price)
        rs.set(self.pair + "bid_amount_%d" %(self.userid), self.amount)
        rs.set(self.pair + "bid_timestamp_%d" %(self.userid), self.timestamp)

    def to_dict(self):
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        d["pair"] = self.pair
        return d

class Ask(object):
    def __init__(self, price, amount, userid, timestamp, pair = "default"):
        self.price = int(price)
        self.userid = int(userid)
        self.timestamp = int(timestamp)
        self.amount = int(amount)
        self.pair = pair

    def save_to_db(self):
        rs.lpush(self.pair + "ask_uid", self.userid)
        rs.set(self.pair + "ask_price_%d" %(self.userid), self.price)
        rs.set(self.pair + "ask_amount_%d" %(self.userid), self.amount)
        rs.set(self.pair + "ask_timestamp_%d" %(self.userid), self.timestamp)


    def to_dict(self):
        d = {}
        d["price"] =  self.price
        d["amount"] = self.amount
        d["pair"] = self.pair
        return d


def new_bid(price, amount, userid, timestamp, pair = "default"):
    bid = get_bid_by_id(int(userid), pair=pair)
    if bid != None:
        print("there's same tic exist")
    bid = Bid(price, amount, userid, timestamp, pair)
    if amount != 0 and price != 0:
        bid.save_to_db()
    else:
        print("rm ask", userid)

def new_ask(price, amount, userid, timestamp, pair = "default"):
    print("=====================new_ask===========\n", userid)
    ask = get_ask_by_id(int(userid), pair=pair)
    if ask != None:
        print("there's same tic exist")
    ask = Ask(price, amount, int(userid), timestamp, pair)
    if amount != 0 and price != 0:
        ask.save_to_db()
    else:
        print("rm ask", userid)

def get_high_ask(pair = "default"):
    if rs.llen(pair + "ask_uid")==0:
        return None
    unpacked_object = get_ask_by_id(int(rs.sort(pair + "ask_uid", by=pair + 'ask_price_*', desc=True)[0]), False, pair)
    return unpacked_object

def get_low_bid(pair = "default"):
    if rs.llen(pair + "bid_uid")==0:
        return None

    unpacked_object = get_bid_by_id(int(rs.sort(pair + "bid_uid", by=pair + 'bid_price_*')[0]), False, pair)
    return unpacked_object

def get_asks(count, pair = "default"):
    r = []
    #if rs.llen("ask_uid")<count:
    #    return False
    l = rs.sort(pair + "ask_uid", by=pair + 'ask_price_*', desc=True)[0:count]
    for i in l:
        unpacked_object = get_ask_by_id(int(i), False, pair)
        r.append(unpacked_object)
    return r

def get_bids(count, pair = "default"):
    r = []
    l = rs.sort(pair + "bid_uid", by=pair + 'bid_price_*')[0:count]
    for i in l:
        unpacked_object = get_bid_by_id(int(i), False, pair)
        r.append(unpacked_object)
    return r

def new_deal(price, amount, id1, id2, trade_id, pair = "default"):
    deal = Trade(price, amount, id1, id2, trade_id, pair)
    deal.save_to_db()
    print(price, amount, id1, id2, pair)
    return True

def get_deals(num, pair = "default"):
    r = []
    l = rs.lrange(pair + "trade_id", 0, num-1)
    for i in l:
        id1 = rs.hget(pair + "trade_id1", int(i))
        id2 = rs.hget(pair + "trade_id2", int(i))
        amount = rs.hget(pair + "trade_amount", int(i))
        price = rs.hget(pair + "trade_price", int(i))
        r.append(Trade(price, amount, id1, id2, int(i), pair))
    return r

def match(pair = "default"):
    try:
        ask = get_high_ask(pair)
        bid = get_low_bid(pair)
        if ask.price >= bid.price:
            deal_price = bid.price
            if ask.amount > bid.amount:
                deal_amount = int(bid.amount)
            else:
                deal_amount = int(ask.amount)
            if new_deal(deal_price, deal_amount, ask.userid, bid.userid, int(rs.get(pair + "global_trade_id")), pair):
                rs.set(pair + "global_trade_id", int(rs.get(pair + "global_trade_id")) + 1)

            new_bid(bid.price, int(bid.amount)-deal_amount, bid.userid, bid.timestamp, pair)
            new_ask(ask.price, int(ask.amount)-deal_amount, ask.userid, ask.timestamp, pair)
            ## match
            return True
        return False
    except Exception as e:
        print(e)
        return False
