# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 13:44:22 2018

@author: Spectre
"""

import pandas as pd
import numpy as np
import os

for file in os.listdir(os.curdir):
    
    df=pd.read_csv(file)
    new_df=pd.DataFrame()
    dates=df['Date'].unique()
    for day in dates:
        o=df['Open'].loc[df['Date']==day].iloc[0]
        h=df['High'].loc[df['Date']==day].max()
        l=df['Low'].loc[df['Date']==day].min()
        c=df['Close'].loc[df['Date']==day].iloc[-1]
        v=df['Volume '].loc[df['Date']==day].sum()
        new_df=new_df.append([[day,o,h,l,c,v]])
    new_df.columns=['Date','Open','High','Low','Close','Volume']
