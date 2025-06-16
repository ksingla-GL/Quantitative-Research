# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 15:46:51 2019

@author: Spectre
"""

from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote
from datetime import timedelta

import numpy as np
import pandas as pd
import os

nifty_50=pd.read_csv("Desktop/Nifty_Data/ind_nifty50list.csv")

os.chdir("Desktop/Nifty50_Data")
for ind in nifty_50['Symbol']:
    if ind not in os.listdir():
        os.mkdir(ind)
    os.chdir(ind)
    for year in range(2015,2020):
        if str(year) not in os.listdir():
            os.mkdir(str(year))
        for month in range(1,13):
            if year==2019 and month==8:
                break
            else:
                savedir=str(year)+'/'+str(month)
                if str(month) not in os.listdir(str(year)+'/'):
                    os.mkdir(savedir)
                else:
                    continue
                expiry = get_expiry_date(year=year, month=month)
                prev_month=month
                prev_year=year
                fut_prices=get_history(symbol=ind,start=date(prev_year,prev_month,1),
                end=pd.to_datetime(expiry),futures=True,index=False,expiry_date=expiry)
                if len(fut_prices)==0:
                    print("Its messed at "+str(month)+"th month, year "+str(year))
                    continue
                
                """
                if len(fut_prices)==0:
                    continue
                """
                fut_prices.to_csv(savedir+'/'+"Fut.csv")
                
                strike_0=(fut_prices['Underlying'].iloc[0]//100)*100
                if strike_0!=strike_0:
                    strike_0=(fut_prices['Last'].iloc[0]//100)*100
                strike_max=int(strike_0*1.25)
                strike_min=int(strike_0*0.75)
                
                strikes=[strike_0+(strike_max-strike_min)*i/20 for i in range(-10,11)]
                for op_type in ['PE','CE']:
                    if op_type not in os.listdir(savedir+'/'):
                        os.mkdir(savedir+'/'+op_type)
                       
                    for strike in strikes:
                        strike=int(strike)
                        if str(strike)+".csv" not in os.listdir(savedir+'/'+op_type+'/'):                     
                            nifty_opt = get_history(symbol=ind,start=date(prev_year,prev_month,1),\
                            end=pd.to_datetime(expiry),option_type=op_type,strike_price=strike,expiry_date\
                            =pd.to_datetime(expiry))
                            if len(nifty_opt)>0:
                                nifty_opt.to_csv(savedir+'/'+op_type+'/'+str(strike)+".csv")
    os.chdir("..")
