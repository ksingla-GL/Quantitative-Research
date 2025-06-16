from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote,get_futures_chain

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

###HYPERPARAMs
threshold=0.08

fos=pd.read_csv("fo_mktlots.csv")
fos=fos['SYMBOL    '].tolist()
fos=fos[4:]
total_stocks=[]
for stock in fos:
    stock=stock.replace(' ','')
    total_stocks.append(stock)
year=2020
month=4

expiry=max([i for i in get_expiry_date(year=year, month=month)])

ints=[]
for stock in total_stocks:             
    current_price_info=get_quote(stock,instrument='FUTSTK',expiry=expiry)
    dof=current_price_info['data'][0]
    if len(dof)==0 or dof['buyPrice1']=='-' or dof['sellPrice1']=='-':
        total_stocks.remove(stock)
        continue
    dof['buyPrice1']=pd.to_numeric(dof['buyPrice1'].replace(',',''))
    dof['sellPrice1']=pd.to_numeric(dof['sellPrice1'].replace(',',''))
    dof['underlyingValue']=pd.to_numeric(dof['underlyingValue'].replace(',',''))
    strike_0=int((dof['buyPrice1']+dof['sellPrice1'])/2)
    ce_info=get_quote(stock,instrument='OPTSTK',expiry=expiry,option_type='CE',\
                                  strike=strike_0)
    dof2=ce_info['data'][0]
    if len(dof2)==0 or dof2['buyPrice1']=='-' or dof2['sellPrice1']=='-':
        continue
    dof2['buyPrice1']=pd.to_numeric(dof2['buyPrice1'].replace(',',''))
    dof2['sellPrice1']=pd.to_numeric(dof2['sellPrice1'].replace(',',''))  
    if dof2['sellPrice1']/dof2['buyPrice1']>1.3:
        continue
    if ((dof2['buyPrice1']+dof2['sellPrice1'])/2)/strike_0<threshold:
        ints.append(stock)
    
        