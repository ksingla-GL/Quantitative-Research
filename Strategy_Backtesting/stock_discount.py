# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:35:24 2020

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

stock='ACC'

year=2020
if str(year) not in os.listdir():
    os.mkdir(str(year))
for month in range(4,5):
    savedir=str(year)+'/'+str(month)
    if str(month) not in os.listdir(str(year)+'/'):
        os.mkdir(savedir)
    else:
        continue
    expiry = max([i for i in get_expiry_date(year=year, month=month)])
    #prev_month=month-1 if month!=1 else 12
    #prev_year=year if month!=1 else year-1
    prev_month=month-1
    prev_year=year
    fut_prices=get_history(symbol=stock,start=date(prev_year,prev_month,1),
    end=pd.to_datetime(expiry),futures=True,index=False,expiry_date=expiry)
    """
    if len(fut_prices)==0:
        continue
    """
    fut_prices.to_csv(savedir+'/'+"Fut.csv")
    
    strike_0=(fut_prices['Underlying'].iloc[0]//100)*100
    if strike_0!=strike_0:
        strike_0=(fut_prices['Last'].iloc[0]//100)*100
    strike_max=int(strike_0+strike_0*2)
    strike_min=int(strike_0-strike_0*2)
    
    for op_type in ['PE','CE']:
        if op_type not in os.listdir(savedir+'/'):
            os.mkdir(savedir+'/'+op_type)
        for strike in range(strike_min,strike_max+50,50):
            if str(strike)+".csv" not in os.listdir(savedir+'/'+op_type+'/'):                     
                nifty_opt = get_history(symbol=stock,start=date(prev_year,prev_month,1),end=pd.to_datetime(expiry),index=False,option_type=op_type,strike_price=strike,expiry_date=pd.to_datetime(expiry))
                if len(nifty_opt)>0:
                    nifty_opt.to_csv(savedir+'/'+op_type+'/'+str(strike)+".csv")
                    