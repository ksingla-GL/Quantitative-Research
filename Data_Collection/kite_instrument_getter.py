# -*- coding: utf-8 -*-
"""
Created on Sat May  9 16:31:39 2020

@author: Spectre
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import numpy as np
import os
from pprint import pprint
import logging
import pdb
import pickle
import datetime

api_key='zbpdticsjg24dbos'
api_secret=''

kite=KiteConnect(api_key=api_key)
all_inst=kite.instruments()

""" 
ints=[]
for inst in all_inst:
    #pdb.set_trace()
    if inst['exchange']=='BSE' and inst['tick_size']>0:
        ints.append(inst)

       
exchs=[]
for inst in all_inst:
    #pdb.set_trace()
    if inst['exchange'] not in exchs:
        exchs.append(inst['exchange'])
"""

expiry=datetime.date(2020, 8, 27)
        
futs=[]
fut_maps={}
for inst in all_inst:
    if inst['exchange']=='NFO' and inst['instrument_type']=='FUT' and inst['expiry']==\
    expiry:
        futs.append(inst)
        fut_maps[inst['tradingsymbol']]=inst['instrument_token']
        
ops=[]
op_maps={}
for inst in all_inst:
    if inst['exchange']=='NFO' and inst['segment']=='NFO-OPT' and inst['expiry']==\
    expiry:
        ops.append(inst)
        if inst['name'] not in op_maps:
            op_maps[inst['name']]={}
        op_maps[inst['name']][inst['tradingsymbol']]=inst['instrument_token']
        
a_file = open("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Op_Map.pkl", "wb")
pickle.dump(op_maps, a_file)
a_file.close()

"""        
a_file = open("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Op_Map.pkl", "rb")
output = pickle.load(a_file)
#print(output)
"""

lot_sizes={}
for inst in all_inst:
    if inst['exchange']=='NFO' and inst['instrument_type']=='FUT' and inst['expiry']==\
    expiry:
        lot_sizes[inst['instrument_token']]=inst['lot_size']
        
pd.DataFrame.from_dict(lot_sizes,orient='index').to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Lot_sizes.csv")

mapper2=fut_maps.copy()        
for mapper in mapper2:
    if 'SEP' in str(mapper):
        del fut_maps[mapper]
        
pd.DataFrame.from_dict(fut_maps,orient='index').to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Fut_Map.csv")
     
cash={}
for sym in fut_maps:
    cash[sym.split('20')[0]]=''
    
for inst in all_inst:
    if inst['exchange']=='BSE' and inst['tradingsymbol'] in cash:
        cash[inst['tradingsymbol']]=inst['instrument_token']
        
pd.DataFrame.from_dict(cash,orient='index').to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Map_BSE.csv")

cash={}
for sym in fut_maps:
    cash[sym.split('20')[0]]=''

for inst in all_inst:
    if inst['exchange']=='NSE' and inst['tradingsymbol'] in cash:
        cash[inst['tradingsymbol']]=inst['instrument_token']
        

pd.DataFrame.from_dict(cash,orient='index').to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Map.csv")  

cash_map=pd.read_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Map_BSE.csv")
cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[int(stock) for stock in cash_stocks]

fut_map=pd.read_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]

cash_fut=pd.DataFrame(columns=['Cash Symbol','Fut Symbol'])
for stock in cash_map[cash_map.columns[0]]:
    if stock+'20AUGFUT' not in fut_map[fut_map.columns[0]].values or \
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]!=\
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]:
        continue
    cash_fut.loc[len(cash_fut)]=[int(cash_map.loc[cash_map[cash_map.columns[0]]==stock,\
    cash_map.columns[1]].values[0]),int(fut_map.loc[fut_map[fut_map.columns[0]]==stock+\
                    '20AUGFUT',fut_map.columns[1]].values[0])]
    
cash_fut.to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Fut_Mapper_Bse.csv")

cash_map=pd.read_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Map.csv")
cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[int(stock) for stock in cash_stocks]

cash_fut=pd.DataFrame(columns=['Cash Symbol','Fut Symbol'])
for stock in cash_map[cash_map.columns[0]]:
    if stock+'20AUGFUT' not in fut_map[fut_map.columns[0]].values or \
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]!=\
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]:
        continue
    cash_fut.loc[len(cash_fut)]=[int(cash_map.loc[cash_map[cash_map.columns[0]]==stock,\
    cash_map.columns[1]].values[0]),int(fut_map.loc[fut_map[fut_map.columns[0]]==stock+\
                    '20AUGFUT',fut_map.columns[1]].values[0])]
    
cash_fut.to_csv("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb/Cash_Fut_Mapper.csv")
