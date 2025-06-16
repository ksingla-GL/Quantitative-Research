# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 13:42:08 2020

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

from datetime import datetime
from datetime import timedelta

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
#print("Current Time =", current_time)

try:
    os.chdir("C:/Users/Spectre/Desktop/Live_Data")
except:
    pass

year=2020
month=4

near_expiry=min([i for i in get_expiry_date(year=year, month=month)])
far_expiry=max([i for i in get_expiry_date(year=year, month=month)])

pe_data=pd.DataFrame(columns=['Time','Bid','Ask','LTP','Annvol','ImpVol','Vwap',\
                    'UnderlyingValue','% of Underlying','Expiry'])
ce_data=pd.DataFrame(columns=['Time','Bid','Ask','LTP','Annvol','ImpVol','Vwap',\
                    'UnderlyingValue','% of Underlying','Expiry'])
far_pe_data=pd.DataFrame(columns=['Time','Bid','Ask','LTP','Annvol','ImpVol','Vwap',\
                    'UnderlyingValue','% of Underlying','Expiry'])
far_ce_data=pd.DataFrame(columns=['Time','Bid','Ask','LTP','Annvol','ImpVol','Vwap',\
                    'UnderlyingValue','% of Underlying','Expiry'])
FMT = '%H:%M:%S'
prev_time=current_time
while current_time<"15:30:05":
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(prev_time, FMT)
    if tdelta<timedelta(seconds=59):
        continue
    
    cur_date=now.strftime("%d-%m-%y")
    current_price_info=get_quote(symbol='NIFTY', instrument='OPTIDX', expiry=near_expiry,\
                    option_type='PE', strike=8500)
    current_price_info=get_quote(symbol='NIFTY', instrument='OPTIDX', expiry=near_expiry,\
                    option_type='CE', strike=8500)
    
    pe_dof=current_price_info['data'][0]
    ce_dof=current_price_info['data'][0]
    #dof means Data of Interest
    uv=pd.to_numeric(pe_dof['underlyingValue'].replace(',',''))
    ltp=pd.to_numeric(pe_dof['lastPrice'].replace(',',''))
    
    pe_data.loc[len(pe_data)]=[current_time,pe_dof['buyPrice1'],pe_dof['sellPrice1'],ltp,pe_dof[\
    'annualisedVolatility'],pe_dof['impliedVolatility'],pe_dof['vwap'],uv,round((ltp/uv)*100,2)\
    ,pe_dof['expiryDate']]
    pe_data.set_index('Time').to_csv("Nifty_Options/PE/"+cur_date+"_Near_85.csv")
    
    uv=pd.to_numeric(ce_dof['underlyingValue'].replace(',',''))
    ltp=pd.to_numeric(ce_dof['lastPrice'].replace(',',''))
    
    ce_data.loc[len(ce_data)]=[current_time,ce_dof['buyPrice1'],ce_dof['sellPrice1'],ltp,ce_dof[\
    'annualisedVolatility'],ce_dof['impliedVolatility'],ce_dof['vwap'],uv,round((ltp/uv)*100,2)\
    ,ce_dof['expiryDate']]
    ce_data.set_index('Time').to_csv("Nifty_Options/CE/"+cur_date+"_Near_85.csv")
    
    """NOW THE SAME FOR FAR EXPIRY"""
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    cur_date=now.strftime("%d-%m-%y")
    
    current_price_info=get_quote(symbol='NIFTY', instrument='OPTIDX', expiry=far_expiry,\
                    option_type='PE', strike=8500)
    current_price_info=get_quote(symbol='NIFTY', instrument='OPTIDX', expiry=far_expiry,\
                    option_type='CE', strike=8500)
    
    pe_dof=current_price_info['data'][0]
    ce_dof=current_price_info['data'][0]
    #dof means Data of Interest
    uv=pd.to_numeric(pe_dof['underlyingValue'].replace(',',''))
    ltp=pd.to_numeric(pe_dof['lastPrice'].replace(',',''))
    
    far_pe_data.loc[len(far_pe_data)]=[current_time,pe_dof['buyPrice1'],pe_dof['sellPrice1'],ltp,pe_dof[\
    'annualisedVolatility'],pe_dof['impliedVolatility'],pe_dof['vwap'],uv,round((ltp/uv)*100,2)\
    ,pe_dof['expiryDate']]
    far_pe_data.set_index('Time').to_csv("Nifty_Options/PE/"+cur_date+"_Far_85.csv")
    
    uv=pd.to_numeric(ce_dof['underlyingValue'].replace(',',''))
    ltp=pd.to_numeric(ce_dof['lastPrice'].replace(',',''))
    
    far_ce_data.loc[len(far_ce_data)]=[current_time,ce_dof['buyPrice1'],ce_dof['sellPrice1'],ltp,ce_dof[\
    'annualisedVolatility'],ce_dof['impliedVolatility'],ce_dof['vwap'],uv,round((ltp/uv)*100,2)\
    ,ce_dof['expiryDate']]
    far_ce_data.set_index('Time').to_csv("Nifty_Options/CE/"+cur_date+"_Far_85.csv")
    
    prev_time=current_time
