# -*- coding: utf-8 -*-
"""
Created on Tue May  5 16:09:00 2020

@author: Spectre
"""

import pandas as pd
import numpy as np
import os
import pdb

os.chdir("C:/Users/Spectre/Desktop/FnO_Data/Tradehull")

"""Hyperparameters"""
num_misses_ok=30
discount_thresh=0.03

disc_tracker={}
for file in os.listdir("1minute/"):
    #print(file)
    fut=pd.read_excel("1minute/"+file)
    stock=file.split("20APR")[0]
    try:
        cash=pd.read_excel("minutex/"+stock+"_minute.xlsx")
    except:
        continue
    fut['check']=fut['volume']!=0
    fut['check']=fut['check'].rolling(window=num_misses_ok).max()
    
    bads=fut.loc[fut['check']==0]
    print(stock+" data starts at "+str(bads['date'].iloc[-1]))
    
    fut=fut.loc[fut['date']>bads['date'].iloc[-1]]
    cash=cash.loc[cash['date']>=fut['date'].iloc[0]]
    
    agg=fut.merge(cash,on='date',how='left',suffixes=['_fut','_cash'])
    agg['check']=np.where((agg['close_cash']-agg['close_fut'])/agg['close_cash']>discount_thresh,1,0)
    agg['check']=np.where((agg['low_cash']-agg['low_fut'])/agg['low_cash']>discount_thresh,1,0)
    agg['check']=np.where((agg['high_cash']-agg['high_fut'])/agg['high_cash']>discount_thresh,1,0)
    agg['check']=np.where((agg['open_cash']-agg['open_fut'])/agg['open_cash']>discount_thresh,1,0)
    
    if len(agg.loc[(agg['check']==1)&(agg['volume_fut']>0)])>100:
        disc_tracker[stock]=agg.loc[(agg['check']==1)&(agg['volume_fut']>0)]
    #pdb.set_trace()