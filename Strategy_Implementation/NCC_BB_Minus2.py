# -*- coding: utf-8 -*-
"""
Created on Thu May  7 20:12:49 2020

@author: Spectre
"""

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
access_token='UqoLEW8pVgF17M4oYTXul1RHEtK2leUI'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='UqoLEW8pVgF17M4oYTXul1RHEtK2leUI'

kite.set_access_token(access_token)

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
cash_stocks2=cash_map2['0'].values.tolist()
cash_stocks2=[stock for stock in cash_stocks2 if str(stock) !='nan']
cash_stocks2=[int(stock) for stock in cash_stocks2]

cash_stocks+=cash_stocks2

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]

cf_map=pd.read_csv("Cash_Fut_Mapper.csv")
cf_map_bse=pd.read_csv("Cash_Fut_Mapper_Bse.csv")
cf_map=cf_map.append(cf_map_bse)

lot_sizes=pd.read_csv("Lot_sizes.csv")
lot_sizes.set_index(lot_sizes.columns[0],inplace=True)
#lot_sizes.columns=['Size']
lot_sizes=lot_sizes.to_dict()
lot_sizes=lot_sizes['0']

kws = KiteTicker(api_key, access_token)
num_ticks=10

tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
trade=0
status=kite.TRANSACTION_TYPE_SELL

b=0
s=0
cur_time=time.time()
count=0

def on_ticks(ws, ticks):  # noqa
    #logging.info("Ticks: {}".format(ticks))
    #global row_no
    #pprint(ticks)
    #pdb.set_trace()
    
    #x=time.time()

    for tick in ticks:
        
        #pdb.set_trace()
        ltpb = tick['depth']['buy'][0]['price']
        ltps = tick['depth']['sell'][0]['price']
        #time = ticks[0]['timestamp']
        #print(ltpb,ltps)
        #num_ticks=1 if status==kite.TRANSACTION_TYPE_BUY else 0
        #pdb.set_trace()
        order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol="NCC20JULFUT",
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=lot_sizes[tick['instrument_token']],
                product=kite.PRODUCT_NRML,
                order_type=kite.ORDER_TYPE_LIMIT,
                validity=kite.VALIDITY_IOC,
                price=ltpb-num_ticks*0.05)
        
        """
        if s==0:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="NCC",
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=1,
                product=kite.PRODUCT_CNC,
                order_type=kite.ORDER_TYPE_LIMIT,
                validity=kite.VALIDITY_IOC,
                price=ltps+0.05*num_ticks)
        if (len(kite.order_trades(order_id))>0):
            print("Sell exec")
            #pdb.set_trace()
            s=1
        else:
            print("Buy can")
        
        if b==0:
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="NCC",
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                quantity=1,
                product=kite.PRODUCT_CNC,
                order_type=kite.ORDER_TYPE_LIMIT,
                validity=kite.VALIDITY_IOC,
                price=ltpb-0.05*num_ticks)
        
        if (len(kite.order_trades(order_id))>0):
            print("Order exec")
            #pdb.set_trace()
            b=1
        else:
            #kws.stop()
            print("Order can")
        """
        #count+=1
        if time.time()-cur_time>120:
            print("Times up")
            kws.stop()
            
        
        
        

def on_connect(ws, response):  # noqa
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe([11672322])

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, [11672322])
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

kws.connect(threaded=True)

#tf.to_csv("3_3.15_23_6_tf.csv")
#all_ts.to_csv("3_3.15_23_6_all_ts.csv")
