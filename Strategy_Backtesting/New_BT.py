# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:14:59 2019

@author: Spectre
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 19:49:04 2019

@author: Spectre
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime as dt

try:
    os.chdir('Desktop/Nifty_Data/')
except:
    pass

profs=pd.DataFrame(columns=['Date','Atm_CE','Atm_PE','Otm_CE','Otm_PE','Total_Profit'])
for year in range(2007,2019):
    for month in range(1,13):
        if year==2018 and month==4:
            break
        cur_fut=pd.read_csv(str(year)+'/'+str(month)+'/Fut.csv')
        cur_fut['Month']=pd.to_datetime(cur_fut['Date']).dt.month
        if len(cur_fut.loc[cur_fut['Month']==month,'Underlying'])==0 or \
        cur_fut.loc[cur_fut['Month']==month,'Underlying'].values[0]!=cur_fut.loc[cur_fut['Month']==month,'Underlying'].values[0]:
            continue
        atm_price=int(cur_fut.loc[cur_fut['Month']==month,'Underlying'].values[0]//100*100)
        #exp_date=futs.loc[futs['Date']==date,'Expiry'].values[0]
        atm_ce=pd.read_csv(str(year)+'/'+str(month)+'/'+'CE/'+str(atm_price)+'.csv')
        atm_ce['Month']=pd.to_datetime(atm_ce['Date']).dt.month
        atm_ce=atm_ce.loc[atm_ce['Month']==month]
        atm_ce['Underlying']=np.where(atm_ce['Underlying']!=atm_ce['Underlying'],cur_fut['Close'].values[-len(atm_ce):]\
              ,atm_ce['Underlying'])
        atm_pe=pd.read_csv(str(year)+'/'+str(month)+'/'+'PE/'+str(atm_price)+'.csv')
        atm_pe['Month']=pd.to_datetime(atm_pe['Date']).dt.month
        atm_pe=atm_pe.loc[atm_pe['Month']==month]
        atm_pe['Underlying']=np.where(atm_pe['Underlying']!=atm_pe['Underlying'],cur_fut['Close'].values[-len(atm_pe):]\
              ,atm_pe['Underlying'])
        
        otmp_pe=int(atm_price*0.9//100*100)
        otmp_ce=int(atm_price*1.1//100*100)
        
        while True:
            try:
                otm_ce=pd.read_csv(str(year)+'/'+str(month)+'/'+'CE/'+str(otmp_ce)+'.csv')
                break
            except:
                otmp_ce-=100
        otm_ce['Month']=pd.to_datetime(otm_ce['Date']).dt.month
        otm_ce=otm_ce.loc[otm_ce['Month']==month]
        
        while True:
            try:
                otm_pe=pd.read_csv(str(year)+'/'+str(month)+'/'+'PE/'+str(otmp_pe)+'.csv')
                break
            except:
                otmp_pe+=100
                
        otm_pe['Month']=pd.to_datetime(otm_pe['Date']).dt.month
        otm_pe=otm_pe.loc[otm_pe['Month']==month]
        """
        for day in otm_ce['Date'].values:
            cur_atm_ce=atm_ce.loc[atm_ce['Date']==day,'Close'].values[0]
            if cur_atm_ce/atm_price<0.03:
        """
        if atm_ce.iloc[0]['Close']/atm_price<0.03:
            continue
        atm_ce_ret=(atm_ce['Close'].values[0]-atm_ce['Close'].values[-1])/atm_ce['Close'].values[0]
        atm_pe_ret=(atm_pe['Close'].values[0]-atm_pe['Close'].values[-1])/atm_pe['Close'].values[0]        
        otm_ce_ret=(-otm_ce['Close'].values[0]+otm_ce['Close'].values[-1])/otm_ce['Close'].values[0]
        otm_pe_ret=(-otm_pe['Close'].values[0]+otm_pe['Close'].values[-1])/otm_pe['Close'].values[0]
        
        profit=atm_ce_ret*atm_ce['Close'].values[0]+atm_pe_ret*atm_pe['Close'].values[0]+\
        otm_ce_ret*otm_ce['Close'].values[0]+otm_pe_ret*otm_pe['Close'].values[0]
        
        profs.loc[len(profs)]=[atm_ce['Date'].values[-1],atm_ce_ret*atm_ce['Close'].values[0],\
        atm_pe_ret*atm_pe['Close'].values[0],otm_ce_ret*otm_ce['Close'].values[0],\
        otm_pe_ret*otm_pe['Close'].values[0],profit]
        
        