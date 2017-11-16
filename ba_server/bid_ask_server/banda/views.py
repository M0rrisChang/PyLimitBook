from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.views import status
from datetime import datetime
from django.shortcuts import render

import json
import time


from .red import new_bid, new_ask, match, get_bids, get_asks, get_deals






def get_timestamp():
    timestamp = time.time()
    print('timestamp:', timestamp)
    return timestamp


def handling_click(request, timestamp, _type):
    print('handling click')
    price = request.GET.get('price')
    amount = request.GET.get('amount')
    user_id = request.GET.get('user_id')

    #test
    price = 1 + timestamp
    amount = timestamp - 1
    user_id = timestamp - 2
    #test

    data = {
        'price': price,
        'timestamp': timestamp,
        'amount': amount
    }

    if _type == 'bid':
        new_bid(price, amount, user_id, timestamp)
        data['type'] = 'bid'
    else:  # == ask
        new_ask(price, amount, user_id, timestamp)
        data['type'] = 'ask'

    while match():
        print("to do sth..")

    return data


def home(request):
    timestamp = get_timestamp()
    print('get shit:', request.GET.get('ask'))
    if(request.GET.get('ask')):
        _type = 'ask'
        data = handling_click(request, timestamp, _type)
        print('handling asks..')
    elif(request.GET.get('bid')):
        _type = 'bid'
        data = handling_click(request, timestamp, _type)
        print('handling bid..')


    bids = []
    asks = []
    trades = []

    if get_bids(5):
        _bids = get_bids(5)
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
    if get_asks(5):
        _asks = get_asks(5)
        for a in _asks:
            ask = {
                'price': a.price,
                'amount': a.amount
            }
            asks.append(ask)
        while len(asks) < 5:
            asks.append({})
    else:
        asks = [{},{},{},{},{}]
    if get_deals(5):
        _trades = get_deals(5)
        for t in _trades:
            trade = {
                'price': t.price,
                'amount': t.amount,
                'timestamp': t.timestamp
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
    table = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}]
    print('table15:', table)

    return render(request, 'home.html', {
        'data': json.dumps(table)
    })

