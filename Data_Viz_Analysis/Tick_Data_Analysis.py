# -*- coding: utf-8 -*-
"""
Created on Thu May 14 18:10:30 2020

@author: Spectre
"""

import pandas as pd
import numpy as np
import os
import pdb

os.chdir("C:/Users/Spectre/Desktop/Live_Data/Cash_Fut_Arb")

xl=pd.read_csv('Ticks_Trial.csv')

cash_map=pd.read_csv("Cash_Map_BSE.csv")
cash_stocks=cash_map['0'].values.tolist()
cash_stocks=[stock for stock in cash_stocks if str(stock) !='nan']
cash_stocks=[int(stock) for stock in cash_stocks]

fut_map=pd.read_csv("Fut_Map.csv")
fut_stocks=fut_map['0'].values.tolist()
fut_stocks=[stock for stock in fut_stocks if str(stock) !='nan']
fut_stocks=[int(stock) for stock in fut_stocks]

cash_fut={}
for stock in cash_map[cash_map.columns[0]]:
    if stock+'20MAYFUT' not in fut_map[fut_map.columns[0]].values or \
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]!=\
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]:
        continue
    cash_fut[int(cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0])]=\
    int(fut_map.loc[fut_map[fut_map.columns[0]]==stock+'20MAYFUT',fut_map.columns[1]].values[0])
    cash_fut[int(fut_map.loc[fut_map[fut_map.columns[0]]==stock+'20MAYFUT',fut_map.columns[1]].values[0])]=\
    int(cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0])

cash_fut=pd.DataFrame(columns=['Cash Symbol','Fut Symbol'])
for stock in cash_map[cash_map.columns[0]]:
    if stock+'20JUNFUT' not in fut_map[fut_map.columns[0]].values or \
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]!=\
    cash_map.loc[cash_map[cash_map.columns[0]]==stock,cash_map.columns[1]].values[0]:
        continue
    cash_fut.loc[len(cash_fut)]=[int(cash_map.loc[cash_map[cash_map.columns[0]]==stock,\
    cash_map.columns[1]].values[0]),int(fut_map.loc[fut_map[fut_map.columns[0]]==stock+\
                    '20JUNFUT',fut_map.columns[1]].values[0])]
    
cash_fut.to_csv("Cash_Fut_Mapper_Bse.csv")

anoms=[]
for time in np.unique(xl[xl.columns[0]]).tolist():
    x=xl.loc[xl[xl.columns[0]]==time]
    #pdb.set_trace()
    for tok1 in x[x.columns[1]].values:
        #tok1=int(xl[xl.columns[1]].values[0])
        if tok1 not in cash_fut or cash_fut[tok1] not in x[x.columns[1]].values:
            continue
        tok2=cash_fut[tok1]
        if x.loc[x[x.columns[1]]==tok2,'2'].values[0]-x.loc[x[x.columns[1]]==tok1,'2']\
        .values[0]>0.02*x.loc[x[x.columns[1]]==tok2,'2'].values[0]:
            print("Yes!")
            anoms.append([time,tok1,tok2])
        
