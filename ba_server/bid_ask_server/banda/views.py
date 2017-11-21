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
        new_bid(price, amount, user_id, timestamp)
        data['type'] = 'bid'
    else:  # == ask
        new_ask(price, amount, user_id, timestamp)
        data['type'] = 'ask'

    print("match")
    ret = match()
    print("match")

    return data


def home(request):
    timestamp = get_timestamp()
    print('get shit:', request.GET.get('ask'))

    match_data = {}
    if(request.GET.get('ask')):
        _type = 'ask'
        data = handling_click(request, timestamp, _type)
        print('handling asks..')
        if match():
            match_data = {
                'price': request.GET.get('price'),
                'amount': request.GET.get('amount')
            }
    elif(request.GET.get('bid')):
        _type = 'bid'
        data = handling_click(request, timestamp, _type)
        if match():
            match_data = {
                'price': request.GET.get('price'),
                'amount': request.GET.get('amount')
            }
        print('handling bid..')

    bids = []
    asks = []
    trades = []

    if get_bids(4):
        _bids = get_bids(4)
        print('bids:', _bids)
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

    if get_asks(4):
        _asks = get_asks(4)
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
    if get_deals(4):
        _trades = get_deals(4)
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
        'data': json.dumps(table)
    })

