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
access_token='WqNY1B3Q4n11yN7g07uR5GYsIhFlYyY0'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='AmAJq9jQBmIGJHWqCm0EJApSYBQ2IwzB'

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
def on_ticks(ws, ticks):  # noqa
    #logging.info("Ticks: {}".format(ticks))
    global row_no
    #pprint(ticks)
    #pdb.set_trace()
    times = time.time()
    all_ticks={}
    
    #x=time.time()
    for tick in ticks:
        
        ltp = tick['last_price']
        token=tick['instrument_token']
        #time = ticks[0]['timestamp']
        
        print(ltp,times)
        #"""
        all_ticks[token]=ltp
        
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            fut_price=all_ticks[cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]]
            
            if fut_price-ltp>0.0055*ltp:
                #print("Cash Symbol:"+str(token)+" is an opportunity at "+str(times))
                tf.loc[len(tf)]=[times,token,\
                cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltp,fut_price]
                print("Cash Trade")
            #cf_map.loc[cf_map['Cash Symbol']==token]=np.nan
        
        elif token in cf_map['Fut Symbol'].values and cf_map.loc[cf_map['Fut Symbol']==\
        token,'Cash Symbol'].values[0] in all_ticks:
            cash_price=all_ticks[cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0]]
            if ltp-cash_price>0.0055*ltp:
                #print("Fut Symbol:"+str(token)+" is an opportunity at "+str(times))
                tf.loc[len(tf)]=[times,cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0],token,cash_price,ltp]
            #cf_map.loc[cf_map['Fut Symbol']==token]=np.nan

        #"""
    #print("Time Elapsed:"+str(time.time()-times))
            

"""
for tick in all_ticks:
    cash_sheet.range('A' + str(row_no)).value = tick[0]
    cash_sheet.range('B' + str(row_no)).value = tick[1]
    cash_sheet.range('C' + str(row_no)).value = tick[2]
    row_no = row_no + 1
"""

def on_connect(ws, response):  # noqa
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(cash_stocks+fut_stocks)

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_LTP, cash_stocks+fut_stocks)
    
def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.

kws.connect(threaded=True)


