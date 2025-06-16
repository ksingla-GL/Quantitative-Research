# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 19:32:07 2019

@author: Spectre
"""

from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote

import pandas as pd
import numpy as np
import os

for year in range(2015,2019):
    if str(year) not in os.listdir():
        os.mkdir(str(year))
    for month in range(1,13):
        if year==2019 and month==4:
            break
        else:
            savedir=str(year)+'/'+str(month)
            if str(month) not in os.listdir(str(year)+'/'):
                os.mkdir(savedir)
            expiry = get_expiry_date(year=year, month=month)
            prev_month=max((month+9)%12,1)
            prev_year=year-(prev_month//10)
            fut_prices=get_history(symbol="BANKNIFTY",start=date(prev_year,prev_month,1),
            end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
            fut_prices.to_csv(savedir+'/'+"Fut.csv")
            
            strike_0=(fut_prices['Underlying'].iloc[0]//100)*100
            strike_max=int(strike_0+1500)
            strike_min=int(strike_0-1500)
            
            for op_type in ['PE','CE']:
                if op_type not in os.listdir(savedir+'/'):
                    os.mkdir(savedir+'/'+op_type)
                for strike in range(strike_min,strike_max+50,50):
                    if str(strike)+".csv" not in os.listdir(savedir+'/'+op_type+'/'):                     
                        nifty_opt = get_history(symbol="BANKNIFTY",start=date(prev_year,\
                        prev_month,1),end=pd.to_datetime(expiry),index=True,option_type=\
                        op_type,strike_price=strike,expiry_date=pd.to_datetime(expiry))
                        if len(nifty_opt)>0:
                            nifty_opt.to_csv(savedir+'/'+op_type+'/'+str(strike)+".csv")