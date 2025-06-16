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
access_token='PmdsQbsjiEg5LcXP1NAb6twCvxOqeMLC'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='1SN45O39tHkEwskBY1NeRsNuyO2xxTNx'

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

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]

cf_map=pd.read_csv("Cash_Fut_Mapper.csv")

kws = KiteTicker(api_key, access_token)


tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
def on_ticks(ws, ticks):  # noqa
    #logging.info("Ticks: {}".format(ticks))
    global row_no
    #pprint(ticks)
    #pdb.set_trace()
    times = time.time()
    all_ticks={}
    
    #x=time.time()
    for tick in ticks:
        
        #pdb.set_trace()
        ltpb = tick['depth']['buy'][0]['price']
        ltps = tick['depth']['sell'][0]['price']
        token=tick['instrument_token']
        #time = ticks[0]['timestamp']
        
        all_ticks[token]=ltpb
        #print(ltpb,ltps)
        #"""
        #pdb.set_trace()
        
        
        
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            all_ticks[token]=ltps
            fut_price=all_ticks[cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]]
            
            
            all_ts.loc[len(all_ts)]=[times,token,\
            cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltps,fut_price]
            #print("Diff="+str(ltpb-fut_price))
            if fut_price-ltps>0.005*ltps:
                #print("Cash Symbol:"+str(token)+" is an opportunity at "+str(times))
                #print("Diff="+str(ltpb-fut_price))
                tf.loc[len(tf)]=[times,token,\
                cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltps,fut_price]
                #print("Cash Trade")
            #cf_map.loc[cf_map['Cash Symbol']==token]=np.nan
        
        elif token in cf_map['Fut Symbol'].values and cf_map.loc[cf_map['Fut Symbol']==\
        token,'Cash Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            all_ticks[token]=ltpb
            cash_price=all_ticks[cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0]]
            
            all_ts.loc[len(all_ts)]=[times,cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0],token,cash_price,ltpb]
            #print("Diff="+str(ltpb-cash_price))
            if ltpb-cash_price>0.005*ltpb:
                #print("Fut Symbol:"+str(token)+" is an opportunity at "+str(times))
                tf.loc[len(tf)]=[times,cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0],token,cash_price,ltpb]
               # print("Fut Trade")
            #cf_map.loc[cf_map['Fut Symbol']==token]=np.nan
        #pdb.set_trace()

        #"""
    #print("Time Elapsed:"+str(time.time()-times))

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
