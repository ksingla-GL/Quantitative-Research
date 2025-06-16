# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 22:59:05 2020

@author: Spectre
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May  7 20:12:49 2020

@author: Spectre
"""

from bs4 import BeautifulSoup as bs
import pickle
import pandas as pd
import itertools

a_file = open("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Op_Map.pkl", "rb")
output = pickle.load(a_file)
a_file.close()

insts={}
checker={}
strike_interval={}
negs=[]
uneqs=[]
revinsts={}

month='AUG'

for key in output:
    vals=sorted(output[key])
    nums=pd.Series(vals).str.split(month).str[1].str.replace('CE','').str.replace('PE','')
    
    nums=(pd.to_numeric(nums)*1000)
    nums=nums.sort_values()
    vals=pd.Series(vals).iloc[nums.index.values].tolist()

    try:
        if pd.Series(vals).str.len().min()!=pd.Series(vals).str.len().max():
            uneqs.append(key)
    except:
        continue
    
    vals1=pd.Series(vals)[pd.Series(vals).str.split(month).str[1].str.contains('CE')].tolist()
    vals2=pd.Series(vals)[pd.Series(vals).str.split(month).str[1].str.contains('PE')].tolist()
    
    for ind in range(0,len(vals1)-1):
        insts[output[key][vals1[ind]]]=output[key][vals1[ind+1]]
        checker[vals1[ind]]=vals1[ind+1]
        strike_interval[vals1[ind]]=float(vals1[ind+1].split(month)[1].replace('CE','').replace('PE',''))-float(vals1[ind].split(month)[1].replace('CE','').replace('PE',''))
        if strike_interval[vals1[ind]]<0:
            negs.append(key)
        revinsts[output[key][vals1[ind]]]=vals1[ind]
        revinsts[output[key][vals1[ind+1]]]=vals1[ind+1]
        
    for ind in range(len(vals2)-1,0,-1):
        #print(ind)
        insts[output[key][vals2[ind]]]=output[key][vals2[ind-1]]
        checker[vals2[ind]]=vals2[ind-1]
        strike_interval[vals2[ind]]=float(vals2[ind].split(month)[1].replace('CE','').replace('PE',''))-float(vals2[ind-1].split(month)[1].replace('CE','').replace('PE',''))
        if strike_interval[vals2[ind]]<0 and key not in negs:
            negs.append(key)
        revinsts[output[key][vals2[ind]]]=vals2[ind]
        revinsts[output[key][vals2[ind-1]]]=vals2[ind-1]
#print(output)

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
access_token='Urqh3pX29lecEEqh5WGt5Lvy3gA869LS'

kite=KiteConnect(api_key=api_key)
kite.login_url()
request_token='bzvhvKn1OU7Dxg5jMCj5nz6GB29ey0kZ'

kite.set_access_token(access_token)
#cur_pos=[pos['instrument_token'] for pos in kite.positions()['net']] 
#cur_futs=[holding['instrument_token'] for holding in kite.holdings()]
#cur_pos+=cur_futs

"""
KRT=kite.generate_session(request_token,api_secret)
kite.set_access_token(KRT['access_token'])
access_token=KRT['access_token']
"""

lot_sizes=pd.read_csv("Lot_sizes.csv")
lot_sizes.set_index(lot_sizes.columns[0],inplace=True)
lot_sizes.columns=['Size']
lot_sizes=dict(lot_sizes)

insts2=insts.copy()
for inst in insts:
    if revinsts[inst].split('20')[0] in bans:
        del insts2[inst]
insts=insts2.copy()

kws = KiteTicker(api_key, access_token)

tf=pd.DataFrame(columns=['Time','Lower Strike','Upper Strike','LS Price','US Price'])
all_ts=pd.DataFrame(columns=['Time','Lower Strike','Upper Strike','LS Buy','LS Sell','US Buy','US Sell'])
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
        """
        if revinsts[token].split('20')[0] in bans:
            continue
        """
        #time = ticks[0]['timestamp']
        
        all_ticks[token]=[ltpb,ltps]
        
        if token in insts and insts[token] in all_ticks:
            #pdb.set_trace()
            token2=insts[token]
            ltpb2,ltps2=all_ticks[token2]                     
            all_ts.loc[len(all_ts)]=[times,revinsts[token],revinsts[token2],ltpb,ltps,ltpb2,ltps2]
            #print("Diff="+str(ltpb-fut_price))
            if ltps<ltpb2 and ltps!=0.0 and ltps!=0 and ltpb2!=0.0 and ltpb2!=0:
                print("Buy "+str(revinsts[token])+" and sell "+str(revinsts[token2]))
                tf.loc[len(tf)]=[times,token,token2,ltps,ltpb2]
            
            elif ltpb-float(strike_interval[revinsts[token]])>ltps2 and ltpb!=0.0 and ltpb!=0 and ltps2!=0.0 and ltps2!=0:
                print("Sell "+str(revinsts[token])+" and buy "+str(revinsts[token2]))
                tf.loc[len(tf)]=[times,token,token2,ltpb,ltps2]

        #"""
    #print("Time Elapsed:"+str(time.time()-times))

def on_connect(ws, response):  # noqa
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(sorted(dict(itertools.islice(insts.items(), 500))))

    # Set RELIANCE to tick in `full` mode.
    ws.set_mode(ws.MODE_FULL, sorted(dict(itertools.islice(insts.items(), 500))))
    
def on_close(ws, code, reason):
    ws.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close=on_close

kws.connect(threaded=True)

#tf.to_csv("3_3.15_23_6_tf.csv")
#all_ts.to_csv("3_3.15_23_6_all_ts.csv")
