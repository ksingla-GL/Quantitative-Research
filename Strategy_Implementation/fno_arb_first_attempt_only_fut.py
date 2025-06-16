# -*- coding: utf-8 -*-
"""
Created on Thu May  7 20:12:49 2020

@author: Spectre
"""

from bs4 import BeautifulSoup as bs

URL="https://zerodha.com/margin-calculator/SPAN/"
#page = urllib.urlopen(quote_page)
    
import requests 
r = requests.get(URL) 
#print(r.content) 

soup = bs(r.content, 'html5lib') 
childs=list(soup.children)
l2=list(childs[1])
ptags=soup.find_all('p')
texts=[]

for i in range(len(ptags)):
    string=ptags[i].get_text()
    string=string.replace('\n','')
    string=string.replace('\t','')
    texts.append(string)

bans=texts[4].split(',')
for i in range(len(bans)):
    bans[i]=bans[i].replace(' ','')

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import numpy as np
import os
from pprint import pprint
import logging
import xlwings as xw
import datetime
import pdb
import time

os.chdir("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb")

global kws,kite

api_key='zbpdticsjg24dbos'
api_secret='s6agrieo5hmdrkkz19kfyd5uurxfccml'
access_token='h4e01pVE1pQohWIzi0jrsEXoDJKGXbPy'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='NG08HjJg6P0DmM67uel2ffCf3638Eljt'

"""
KRT=kite.generate_session(request_token,api_secret)
kite.set_access_token(KRT['access_token'])
access_token=KRT['access_token']
"""

kite.set_access_token(access_token)
cur_pos=[pos['instrument_token'] for pos in kite.positions()['net'] if pos['quantity']!=0] 
cur_futs=[holding['instrument_token'] for holding in kite.holdings()]
cur_pos+=cur_futs

cash_map=pd.read_csv("Cash_Map.csv")
cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[stock for stock in cash_stocks if stock not in bans]
cash_stocks=[int(stock) for stock in cash_stocks]

cash_map2=pd.read_csv("Cash_Map_BSE.csv")
cash_map2=cash_map2.dropna()
cash_stocks2=cash_map2['0'].values.tolist()
cash_stocks2=[stock for stock in cash_stocks2 if str(stock) !='nan']
cash_stocks2=[stock for stock in cash_stocks2 if stock not in bans]
cash_stocks2=[int(stock) for stock in cash_stocks2]

#cash_stocks+=cash_stocks2

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]

cf_map=pd.read_csv("Cash_Fut_Mapper.csv")
#cf_map_bse=pd.read_csv("Cash_Fut_Mapper_Bse.csv")
#cf_map=cf_map.append(cf_map_bse)
lot_sizes=pd.read_csv("Lot_sizes.csv")
lot_sizes.set_index(lot_sizes.columns[0],inplace=True)
#lot_sizes.columns=['Size']
lot_sizes=dict(lot_sizes['0'])

kws = KiteTicker(api_key, access_token)

cash_sym=cash_map.loc[cash_map[cash_map.columns[1]]==2730497,cash_map.columns[0]].values[0]
fut_sym=fut_map.loc[fut_map[fut_map.columns[1]]==11676162,fut_map.columns[0]].values[0]

tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
def on_ticks(ws, ticks):  # noqa

    #times = time.time()
    all_ticks={}
    num_ticks=1
    
    global cur_pos
    
    for tick in ticks:
        
        #pdb.set_trace()
        ltpb = tick['depth']['buy'][0]['price']
        ltps = tick['depth']['sell'][0]['price']
        token=tick['instrument_token']
        
        all_ticks[token]=ltpb        
        #print(ltpb,ltps)
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            all_ticks[token]=ltps
                        
        elif token in cf_map['Fut Symbol'].values and cf_map.loc[cf_map['Fut Symbol']==\
        token,'Cash Symbol'].values[0] in all_ticks:
            #print(ltpb,ltps)
            #pdb.set_trace()
            all_ticks[token]=ltpb
            token2=cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].values[0]
            cash_price=all_ticks[token2]          
            #all_ts.loc[len(all_ts)]=[times,token2,token,cash_price,ltpb]
            #print(cash_price,ltpb)

            if ltpb-cash_price>0.0045*ltpb:
                #tf.loc[len(tf)]=[times,token2,token,cash_price,ltpb]
                #print("Fut Trade")
                #kws.stop()
                pdb.set_trace()
                
                if token not in cur_pos and token2 not in cur_pos and \
                kite.margins()['equity']['net']>lot_sizes[token]*1.3*ltpb:
                    order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=kite.EXCHANGE_NFO,
                    tradingsymbol=fut_sym,
                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                    quantity=lot_sizes[token],
                    product=kite.PRODUCT_NRML,
                    order_type=kite.ORDER_TYPE_LIMIT,
                    validity=kite.VALIDITY_IOC,
                    price=ltpb+0.05*num_ticks)
                        
                    stat=kite.order_history(order_id)[-1]['status']
                    while (stat!='COMPLETE' and stat!='CANCELLED'):
                        stat=kite.order_history(order_id)[-1]['status']
                        print(stat)
                        
                    if stat=='COMPLETE':
                        order_id = kite.place_order(
                        variety=kite.VARIETY_REGULAR,
                        exchange=kite.EXCHANGE_NSE,
                        tradingsymbol=cash_sym,
                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                        quantity=lot_sizes[token2],
                        product=kite.PRODUCT_CNC,
                        order_type=kite.ORDER_TYPE_LIMIT,
                        validity=kite.VALIDITY_DAY,
                        price=cash_price)
                        print("Fut Trade")
                        stat=kite.order_history(order_id)[-1]['status']
                        while (stat!='COMPLETE' and stat!='CANCELLED'):
                            stat=kite.order_history(order_id)[-1]['status']
                            print(stat)
                        if stat=='COMPLETE':
                            print("Both orders executed")
                        else:
                            print("WATCH OUT!!!CASH FAILED")
                        cur_pos+=token
                        cur_pos+=token2
                    else:
                        print("Fut Order can")
                else:
                    print("Stopped")
    #print("Time Elapsed:"+str(time.time()-times))

def on_connect(ws, response):  # noqa
    ws.subscribe([2730497,11676162])
    ws.set_mode(ws.MODE_FULL, [2730497,11676162])
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

kws.connect()