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
access_token='Ry4vtFWZUyIOajREVWvf94IdPAmXbcTf'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='useAbWpHk7mTBXbe89ZpA6696xGawPmj'

kite.set_access_token(access_token)
cur_pos=[pos['instrument_token'] for pos in kite.positions()['net']] 
cur_futs=[holding['instrument_token'] for holding in kite.holdings()]
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
for ban in bans:
    if ban in cash_map[cash_map.columns[0]].values:
        cash_map=cash_map.loc[cash_map[cash_map.columns[0]]!=ban]

cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[int(stock) for stock in cash_stocks]



cash_map2=pd.read_csv("Cash_Map_BSE.csv")
for ban in bans:
    if ban in cash_map2[cash_map2.columns[0]].values:
        cash_map2=cash_map2.loc[cash_map2[cash_map2.columns[0]]!=ban]
        
cash_map2=cash_map2.dropna()
cash_stocks2=cash_map2['0'].values.tolist()
cash_stocks2=[stock for stock in cash_stocks2 if str(stock) !='nan']
cash_stocks2=[int(stock) for stock in cash_stocks2]

#cash_stocks+=cash_stocks2

cash_stocks=[stock for stock in cash_stocks if stock not in bans]
cash_stocks=[stock for stock in cash_stocks if stock not in cur_pos]

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]
fut_stocks=[stock for stock in fut_stocks if stock not in cur_pos]

cf_map=pd.read_csv("Cash_Fut_Mapper.csv")
cf_map_bse=pd.read_csv("Cash_Fut_Mapper_Bse.csv")
cf_map=cf_map.append(cf_map_bse)

lot_sizes=pd.read_csv("Lot_sizes.csv")
lot_sizes.set_index(lot_sizes.columns[0],inplace=True)
lot_sizes.columns=['Size']
lot_sizes=dict(lot_sizes)

kws = KiteTicker(api_key, access_token)

tf=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
all_ts=pd.DataFrame(columns=['Time','Cash Sym','Fut Sym','CP','FP'])
def on_ticks(ws, ticks):  # noqa

    #pdb.set_trace()
    times = time.ctime()[-13:-5]
    all_ticks={}
    
    #x=time.time()
    for tick in ticks:      
        #pdb.set_trace()
        if 'depth' in tick:
            ltpb = tick['depth']['buy'][0]['price']
            ltps = tick['depth']['sell'][0]['price']
        else:
            continue
        token=tick['instrument_token']
        #time = ticks[0]['timestamp']
        
        all_ticks[token]=ltpb
        if token in cf_map['Cash Symbol'].values:
            all_ticks[token]=ltps
        
        if token in cf_map['Cash Symbol'].values and cf_map.loc[cf_map['Cash Symbol']==\
        token,'Fut Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            fut_price=all_ticks[cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0]]
            
            
            all_ts.loc[len(all_ts)]=[times,token,\
            cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltps,fut_price]
            #print("Diff="+str(ltpb-fut_price))
            if fut_price-ltps>0.01*ltps:
                #print("Cash Symbol:"+str(token)+" is an opportunity at "+str(times))
                #print("Diff="+str(ltpb-fut_price))
                tf.loc[len(tf)]=[times,token,\
                cf_map.loc[cf_map['Cash Symbol']==token,'Fut Symbol'].values[0],ltps,fut_price]
                #print("Cash Trade")
            #cf_map.loc[cf_map['Cash Symbol']==token]=np.nan
        
        elif token in cf_map['Fut Symbol'].values and cf_map.loc[cf_map['Fut Symbol']==\
        token,'Cash Symbol'].values[0] in all_ticks:
            #pdb.set_trace()
            cash_price=all_ticks[cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0]]
            
            all_ts.loc[len(all_ts)]=[times,cf_map.loc[cf_map['Fut Symbol']==token,'Cash Symbol'].\
            values[0],token,cash_price,ltpb]
            #print("Diff="+str(ltpb-cash_price))
            if ltpb-cash_price>0.01*ltpb:
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

#tf.to_csv("3_3.15_23_6_tf.csv")
#all_ts.to_csv("3_3.15_23_6_all_ts.csv")
