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
from datetime import timedelta

import pandas as pd
import numpy as np
import os

ind='NIFTY'

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
            prev_month=max((month+9)%12,1)
            prev_year=year-(prev_month//10)
            fut_prices=get_history(symbol=ind,start=date(prev_year,prev_month,1),
            end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
            """
            if len(fut_prices)==0:
                continue
            """
            fut_prices.to_csv(savedir+'/'+"Fut.csv")
            
            strike_0=(fut_prices['Underlying'].iloc[0]//100)*100
            if strike_0!=strike_0:
                strike_0=(fut_prices['Last'].iloc[0]//100)*100
            strike_max=int(strike_0+1500)
            strike_min=int(strike_0-1500)
            
            for op_type in ['PE','CE']:
                if op_type not in os.listdir(savedir+'/'):
                    os.mkdir(savedir+'/'+op_type)
                for strike in range(strike_min,strike_max+50,50):
                    if str(strike)+".csv" not in os.listdir(savedir+'/'+op_type+'/'):                     
                        nifty_opt = get_history(symbol=ind,start=date(prev_year,prev_month,1),end=pd.to_datetime(expiry),index=True,option_type=op_type,strike_price=strike,expiry_date=pd.to_datetime(expiry))
                        if len(nifty_opt)>0:
                            nifty_opt.to_csv(savedir+'/'+op_type+'/'+str(strike)+".csv")
                            
"""
expiry="29-11-2018"
strike=9800
op_type='PE'
year=2018
month=11
nifty_opt = get_history(symbol=ind,start=date(year,month,1),end=pd.to_datetime(expiry),index=True,option_type=op_type,strike_price=strike,expiry_date=pd.to_datetime(expiry))
ADDING CODE FOR WEEKLIES TOO STARTING FEB 2019
"""
for year in range(2019,2021):
    if str(year) not in os.listdir():
        os.mkdir(str(year))
    for month in range(1,13):
        if year==2019 and month<11:
            continue
        savedir=str(year)+'/'+str(month)
        if str(month) not in os.listdir(str(year)+'/'):
            os.mkdir(savedir)

        expiry = max([i for i in get_expiry_date(year=year, month=month)])
        prev_month=max((month+9)%12,1)
        prev_year=year-(prev_month//10)
        fut_prices=get_history(symbol=ind,start=date(prev_year,prev_month,1),
        end=pd.to_datetime(expiry),futures=True,index=True,expiry_date=expiry)
        """
        if len(fut_prices)==0:
            continue
        """
        fut_prices.to_csv(savedir+'/'+"Fut.csv")
        
        strike_0=(fut_prices['Underlying'].iloc[0]//100)*100
        if strike_0!=strike_0:
            strike_0=(fut_prices['Last'].iloc[0]//100)*100
        strike_max=int(strike_0+1500)
        strike_min=int(strike_0-1500)
        
        week_expiries=[]
        sd=date(year,month,1)
        while sd.date()<expiry:
            nifty_opt = get_history(symbol=ind,start=date(prev_year,prev_month,1),end=\
            pd.to_datetime(sd),index=True,option_type='CE',strike_price=strike_0,\
            expiry_date=pd.to_datetime(sd))
            if len(nifty_opt)>0:
                week_expiries.append(sd)
                sd+=timedelta(1)
            else:
                sd+=timedelta(1)
        week_expiries.append(expiry)
        
        
        for op_type in ['PE','CE']:
            if op_type not in os.listdir(savedir+'/'):
                os.mkdir(savedir+'/'+op_type)
            for strike in range(strike_min,strike_max+50,50):                    
                nifty_opt = pd.DataFrame()
                for weekly_expiry in week_expiries:
                    nifty_opt_add = get_history(symbol=ind,start=date(prev_year,prev_month,1),end=\
                    pd.to_datetime(weekly_expiry),index=True,option_type=op_type,strike_price=strike,\
                    expiry_date=pd.to_datetime(weekly_expiry))
                    nifty_opt=nifty_opt.append(nifty_opt_add)
                if len(nifty_opt)>0:
                    nifty_opt.to_csv(savedir+'/'+op_type+'/'+str(strike)+".csv")
                        
        