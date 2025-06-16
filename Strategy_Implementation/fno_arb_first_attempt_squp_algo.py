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
access_token='JqJs33e2FuSG8L7ExJ1TIKSdsDcrB2yC'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='UvIDYNW6S526bPdtply6T4Yode1QKx6c'

kite.set_access_token(access_token)
cur_pos=[pos['instrument_token'] for pos in kite.positions()['net'] if pos['quantity']!=0] 
cur_futs=[holding['instrument_token'] for holding in kite.holdings() if holding['t1_quantity']!=0]
cur_pos+=cur_futs

"""
KRT=kite.generate_session(request_token,api_secret)
kite.set_access_token(KRT['access_token'])
access_token=KRT['access_token']
"""

"""
wb = xw.Book('All_stocks_ticks_data.xlsx')
cash_sheet = wb.sheets['Cash']
fut_sheet = wb.sheets['Fut']
row_no = int(str(cash_sheet.used_range[-1]).split('$')[-1].replace('>',''))+1
"""
cash_map=pd.read_csv("Cash_Map.csv")
cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[int(stock) for stock in cash_stocks]

cash_map2=pd.read_csv("Cash_Map_BSE.csv")
cash_map2=cash_map2.dropna()
cash_map=cash_map.append(cash_map2)

cash_stocks2=cash_map2['0'].values.tolist()
cash_stocks2=[stock for stock in cash_stocks2 if str(stock) !='nan']
cash_stocks2=[int(stock) for stock in cash_stocks2]

#cash_stocks+=cash_stocks2

cash_stocks=[stock for stock in cash_stocks if stock not in bans]
#cash_stocks=[stock for stock in cash_stocks if stock in cur_pos]

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]
#fut_stocks=[stock for stock in fut_stocks if stock in cur_pos]

cf_map=pd.read_csv("Cash_Fut_Mapper.csv")
cf_map_bse=pd.read_csv("Cash_Fut_Mapper_Bse.csv")
cf_map=cf_map.append(cf_map_bse)

lot_sizes=pd.read_csv("Lot_sizes.csv")
lot_sizes.set_index(lot_sizes.columns[0],inplace=True)
lot_sizes=dict(lot_sizes['0'])

kws = KiteTicker(api_key, access_token)

tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])

num_ticks=10
def on_ticks(ws, ticks):  # noqa
    
    global cur_pos
    all_ticks={}   
    for tick in ticks:        
        #pdb.set_trace()
        ltpb = tick['depth']['buy'][0]['price']
        ltps = tick['depth']['sell'][0]['price']
        token=tick['instrument_token']
        
        all_ticks[token]=ltps
        
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            pdb.set_trace()
            token2=cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]
            cash_sym=cash_map.loc[cash_map[cash_map.columns[1]]==token,cash_map.columns[0]].values[0]
            fut_sym=fut_map.loc[fut_map[fut_map.columns[1]]==token2,fut_map.columns[0]].values[0]

            
            all_ticks[token]=ltpb
            fut_price=all_ticks[cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]]
            
            if ltpb-fut_price>0.0015*ltps:
                
                order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=kite.EXCHANGE_NFO,
                    tradingsymbol=fut_sym,
                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                    quantity=lot_sizes[token2],
                    product=kite.PRODUCT_NRML,
                    order_type=kite.ORDER_TYPE_LIMIT,
                    validity=kite.VALIDITY_IOC,
                    price=460.05)
                
                stat=kite.order_history(order_id)[-1]['status']
                while (stat!='COMPLETE' or stat!='CANCELLED'):
                    stat=kite.order_history(order_id)[-1]['status']
                    print(stat)
                if stat=='COMPLETE':
                    order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=kite.EXCHANGE_BSE,
                    tradingsymbol=cash_sym,
                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                    quantity=lot_sizes[token2],
                    product=kite.PRODUCT_CNC,
                    order_type=kite.ORDER_TYPE_MARKET,
                    validity=kite.VALIDITY_DAY)
                    print("Fut Trade")
                    print("Both orders executed")
                    cur_pos+=token
                    cur_pos+=token2
                else:
                    print("Fut Order can")
        
       
def on_connect(ws, response):  # noqa
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([1346049,11657474])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [1346049,11657474])
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

kws.connect()

#tf.to_csv("3_3.15_23_6_tf.csv")
#all_ts.to_csv("3_3.15_23_6_all_ts.csv")
