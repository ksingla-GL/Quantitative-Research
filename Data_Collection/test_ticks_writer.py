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

global kws,kite,row_no

api_key='zbpdticsjg24dbos'
api_secret='s6agrieo5hmdrkkz19kfyd5uurxfccml'
access_token='nQ7phj6BpSMAemH8ywVcvPh0KE4MMOeZ'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='73gjLHkT6acSu55k2QwmYZg4HoPJKWMl'


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

kws = KiteTicker(api_key, access_token)

wb = xw.Book('All_stocks_ticks_data.xlsx')
cash_sheet = wb.sheets['Cash']
fut_sheet = wb.sheets['Fut']
crow_no = 2
frow_no = 2

tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
def on_ticks(ws, ticks):  # noqa
    
    global crow_no
    global frow_no
    
    times = time.time()
    all_ticks={}
    
    for tick in ticks:
        
        #pdb.set_trace()
        ltpb = tick['depth']['buy'][0]['price']
        ltps = tick['depth']['sell'][0]['price']
        token=tick['instrument_token']
        #time = ticks[0]['timestamp']
        
        all_ticks[token]=ltpb
        
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            all_ticks[token]=ltps
            fut_price=all_ticks[cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]]
            
            """
            all_ts.loc[len(all_ts)]=[times,token,\
            cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltps,fut_price]
            """
            cash_sheet.range('A'+str(crow_no)).value=times
            cash_sheet.range('B'+str(crow_no)).value=token
            cash_sheet.range('C'+str(crow_no)).value=cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]
            cash_sheet.range('D'+str(crow_no)).value=ltps
            cash_sheet.range('E'+str(crow_no)).value=fut_price
            crow_no+=1
            
        elif token in cf_map['Fut Symbol'].values and cf_map.loc[cf_map['Fut Symbol']==\
        token,'Cash Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            all_ticks[token]=ltpb
            cash_price=all_ticks[cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0]]
            
            """
            all_ts.loc[len(all_ts)]=[times,cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0],token,cash_price,ltpb]
            """
            
            fut_sheet.range('A'+str(frow_no)).value=times
            fut_sheet.range('B'+str(frow_no)).value=cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0]
            fut_sheet.range('C'+str(frow_no)).value=token
            fut_sheet.range('D'+str(frow_no)).value=cash_price
            fut_sheet.range('E'+str(frow_no)).value=ltpb
            
            frow_no+=1

        #"""
    print("Time Elapsed:"+str(time.time()-times))

def on_connect(ws, response):  # noqa
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(cash_stocks+fut_stocks)

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, cash_stocks+fut_stocks)
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

kws.connect(threaded=True)
