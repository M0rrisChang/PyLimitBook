from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.views import status
from datetime import datetime
from django.shortcuts import render

import json
import time


from .red import new_bid, new_ask, match, get_bids, get_asks, get_deals, put_default






def get_timestamp():
    timestamp = time.time()
    print('timestamp:', timestamp)
    return timestamp


def handling_click(request, timestamp, _type, pair):

    print('handling click')
    price = request.GET.get('price')
    pair = request.GET.get('pair')
    print(pair)
    print('get price:', price)
    amount = request.GET.get('amount')
    print('get amount:', amount)
    user_id = request.GET.get('user_id')
    print('get user_id:', user_id)


    data = {
        'price': str(price),
        'timestamp': str(timestamp),
        'amount': str(amount)
    }
    if _type == 'bid':
        print(price, amount, user_id, timestamp)
        new_bid(price, amount, user_id, timestamp, pair)
        data['type'] = 'bid'
    else:  # == ask
        new_ask(price, amount, user_id, timestamp, pair)
        data['type'] = 'ask'

    print("match")
    ret = match(pair)
    print("match")

    return data


def home(request):
    timestamp = get_timestamp()
    if(request.GET.get('pair')):
        pair = request.GET.get('pair')
    else:
        pair = 'XMRUSD'
    print('get shit:', request.GET.get('ask'))

    match_data = {}
    if(request.GET.get('ask')):
        _type = 'ask'
        data = handling_click(request, timestamp, _type, pair)
        print('handling asks..')
        if match(pair):
            match_data = {
                'price': request.GET.get('price'),
                'amount': request.GET.get('amount')
            }
    elif(request.GET.get('bid')):
        _type = 'bid'
        data = handling_click(request, timestamp, _type, pair)
        if match(pair):
            match_data = {
                'price': request.GET.get('price'),
                'amount': request.GET.get('amount')
            }
        print('handling bid..')
    elif(request.GET.get('category')):
        _type = 'category'
        pair = request.GET.get('category')
        put_default(pair)

    bids = []
    asks = []
    trades = []
    print("pair", pair)
    if get_bids(5, pair):
        _bids = get_bids(5, pair)
        for b in _bids:
           bid = {
               'price': b.price,
               'amount': b.amount
           }
           bids.append(bid)
        while len(bids) < 5:
            bids.append({})
    else:
        print('get no bids')

        bids = [{},{},{},{},{}]

    if get_asks(5, pair):
        _asks = get_asks(5, pair)
        for a in _asks:
            ask = {
                'price': a.price,
                'amount': a.amount
            }
            asks.append(ask)
        print("===========", asks)
        while len(asks) < 5:
            asks.append({})
    else:
        print(pair)
        asks = [{},{},{},{},{}]

    if get_deals(5, pair):
        _trades = get_deals(5, pair)
        for t in _trades:
            trade = {
                'price': t.price,
                'amount': t.amount,
                'timestamp': t.trade_id
            }
            trades.append(trade)
        while len(trades) < 5:
            trades.append({})
    else:
        trades = [{},{},{},{},{}]

    print('b:', bids)
    print('a:', asks)
    print('t:', trades)
    table = bids + asks + trades
    print('table15:', table)
    table.append(match_data)

    return render(request, 'home.html', {
        'data': json.dumps(table),
        'pair': pair,
    })
