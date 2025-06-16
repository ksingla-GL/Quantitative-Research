# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 17:48:33 2020

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

try:
    os.chdir("C:/Users/Spectre/Desktop/New_Strats/Nifty_Weekly_Strategy")
except:
    pass

data_dict="C:/Users/Spectre/Desktop/Nifty_Data/"

ce_pnl=pd.DataFrame(columns=["ST_entry","LT_entry","ST_exit","LT_exit"])
pe_pnl=pd.DataFrame(columns=["ST_entry","LT_entry","ST_exit","LT_exit"])

for year in range(2019,2021):
    for month in range(1,13):
        if year==2019 and month<3:
            continue
        if year==2020 and month==5:
            break
        #cur_data_dict=data_dict+"/"+str(year)+"/"+str(month)
        
        #near_expiries=[i for i in get_expiry_date(year=year, month=month)]
        final_expiry=max([i for i in get_expiry_date(year=year, month=month)])
               
        cur_fut=pd.read_csv(data_dict+str(year)+'/'+str(month)+'/Fut.csv')
        cur_fut['Month']=pd.to_datetime(cur_fut['Date']).dt.month
        if len(cur_fut.loc[cur_fut['Month']==month,'Underlying'])==0 or \
        cur_fut.loc[cur_fut['Month']==month,'Underlying'].values[0]!=cur_fut.loc[cur_fut['Month']==month,'Underlying'].values[0]:
            continue
        
        atm_price=int(cur_fut.loc[cur_fut['Month']==month,'Open'].values[0]//100*100)
        ce=pd.read_csv(data_dict+str(year)+'/'+str(month)+'/'+'CE/'+str(atm_price)+'.csv')
        ce['Month']=pd.to_datetime(ce['Date']).dt.month
        ce=ce.loc[ce['Month']==month]
        near_expiries=np.unique(ce['Expiry']).tolist()
        near_expiries=sorted(near_expiries)
        near_expiries=near_expiries[:-1]
        
        
        for expiry in near_expiries: 
            
            if expiry!=near_expiries[0]:
                atm_price=int(cur_fut.loc[cur_fut['Date']>prev_expiry,'Open'].values[0]//100*100)
                
            ce=pd.read_csv(data_dict+str(year)+'/'+str(month)+'/'+'CE/'+str(atm_price)+'.csv')
            ce['Month']=pd.to_datetime(ce['Date']).dt.month
            ce=ce.loc[ce['Month']==month]
            far_ce=ce.loc[pd.to_datetime(ce['Expiry'])==final_expiry]
            
            pe=pd.read_csv(data_dict+str(year)+'/'+str(month)+'/'+'PE/'+str(atm_price)+'.csv')
            pe['Month']=pd.to_datetime(pe['Date']).dt.month
            pe=pe.loc[pe['Month']==month]
            far_pe=pe.loc[pd.to_datetime(pe['Expiry'])==final_expiry]
            
            near_ce=ce.loc[pd.to_datetime(ce['Expiry'])==expiry]            
            near_pe=pe.loc[pd.to_datetime(pe['Expiry'])==expiry]
            
            if expiry!=near_expiries[0]:
                near_ce=near_ce.loc[near_ce['Date']>prev_expiry]
                near_pe=near_pe.loc[near_pe['Date']>prev_expiry]
            
            ce_pnl.loc[len(ce_pnl)]=[near_ce.iloc[0]['Open'],far_ce.loc[\
            far_ce['Date']==near_ce['Date'].iloc[0],'Open'].values[0],near_ce.iloc[-1]['Close'],\
            far_ce.loc[pd.to_datetime(far_ce['Date'])==expiry,'Close'].values[0]]
            
            pe_pnl.loc[len(pe_pnl)]=[near_pe.iloc[0]['Open'],far_pe.loc[\
            far_pe['Date']==near_pe['Date'].iloc[0],'Open'].values[0],near_pe.iloc[-1]['Close'],\
            far_pe.loc[pd.to_datetime(far_pe['Date'])==expiry,'Close'].values[0]]
            
            prev_expiry=expiry
            
ce_pnl['ST_pnl']=ce_pnl['ST_entry']-ce_pnl['ST_exit']
ce_pnl['LT_pnl']=ce_pnl['LT_exit']-ce_pnl['LT_entry']
ce_pnl['Total_pnl']=ce_pnl['ST_pnl']+ce_pnl['LT_pnl']

pe_pnl['ST_pnl']=pe_pnl['ST_entry']-pe_pnl['ST_exit']
pe_pnl['LT_pnl']=pe_pnl['LT_exit']-pe_pnl['LT_entry']
pe_pnl['Total_pnl']=pe_pnl['ST_pnl']+pe_pnl['LT_pnl']
                
            
            