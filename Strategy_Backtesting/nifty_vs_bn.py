# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 15:04:17 2020

@author: Spectre
"""

from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote
from datetime import timedelta

import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt

ind='NIFTY'
ind2='BANKNIFTY'

year=2020
month=4

expiry=max([i for i in get_expiry_date(year=year, month=month)])

prev_year=2020
prev_month=month-1

nifty=get_history(symbol=ind,start=date(prev_year,prev_month,20),
            end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
bn=get_history(symbol=ind2,start=date(prev_year,prev_month,20),
            end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)

nifty['bn']=bn['Close']
nifty['n_ret']=nifty['Close']/nifty['Close'].shift(1)-1
nifty['bn_ret']=nifty['bn']/nifty['bn'].shift(1)-1

def get_nifty_bn_ratio_data(year_start,year_end,month_start,month_end):
    nift=pd.DataFrame()
    bnift=pd.DataFrame()
    for year in range(year_start,year_end+1):
        for month in range(month_start,13):
            if year==year_end and month>month_end:
                break
            expiry=max([i for i in get_expiry_date(year=year, month=month)])
            #prev_year=2020
            prev_month=month-1 if month!=1 else 12
            prev_year=year if month!=1 else year-1
            
            nifty=get_history(symbol=ind,start=date(prev_year,prev_month,24),
                        end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
            bn=get_history(symbol=ind2,start=date(prev_year,prev_month,24),
                        end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
            nift=nift.append(nifty)
            bnift=bnift.append(bn)
        
    nift.reset_index(inplace=True)
    bnift.reset_index(inplace=True)
    nift=nift.drop_duplicates('Date')
    bnift=bnift.drop_duplicates('Date')
    cols_of_interest=['Open','High','Low','Close']
    ratios=nift[cols_of_interest]/bnift[cols_of_interest]
    ratios.index=nift['Date']
    return nift,bnift,ratios

nift_old,bnift_old,ratios_old=get_nifty_bn_ratio_data(2000,2020,1,2)

plt.plot(total_ratios['Close'])
plt.title('Ratio of Nifty to BankNifty')
plt.xlabel("Year")
plt.ylabel("Ratio")
    
nifty['bn']=bn['Close']
nifty['n_ret']=nifty['Close']/nifty['Close'].shift(1)-1
nifty['bn_ret']=nifty['bn']/nifty['bn'].shift(1)-1

"""
plt.plot(nifty.reset_index()['Date'].str.split('-')[-2:],nifty['Close']/nifty['Close'].shift(1)-1)

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)
ax.plot(nifty.reset_index()['Date'],nifty[['n_ret','bn_ret']])
ax.legend()
"""

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)
ax.plot(nifty.reset_index()['Date'],nifty['n_ret'],label='Nifty_ret')
ax.plot(nifty.reset_index()['Date'],nifty['bn_ret'],label='BankNifty_ret')
ax.legend()
