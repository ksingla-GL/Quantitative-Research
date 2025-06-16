# -*- coding: utf-8 -*-
"""
Created on Wed May  6 11:19:34 2020

@author: Spectre
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

os.chdir("C:/Users/Spectre/Desktop/FnO_Data")

sp=pd.read_csv("S&P500_Daily.csv")
nift=pd.read_csv("^NSEI.csv")

agg=sp.merge(nift,on='Date',how='inner',suffixes=['_sp','_nift'])
agg=agg.iloc[-20:]
agg['sp_ret']=agg['Close_sp']/agg['Close_sp'].shift(1)-1
agg['nift_ret']=agg['Close_nift']/agg['Close_nift'].shift(1)-1

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)
ax.plot(agg['Date'],agg['nift_ret'],label='Nifty_ret')
ax.plot(agg['Date'],agg['sp_ret'],label='SP500_ret')
ax.legend()