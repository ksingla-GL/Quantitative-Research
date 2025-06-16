# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 19:28:51 2020

@author: Spectre
"""

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
diff_threshold=0.035

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


used_strikes={}
for stock in total_stocks:
    used_strikes[stock]=[]
FMT = '%H:%M:%S'
prev_time=current_time
while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    tdelta = datetime.strptime(current_time, FMT) - datetime.strptime(prev_time, FMT)
    #if tdelta<timedelta(seconds=1):
    #continue
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
        strike=int(0.8*strike_0)//10*10
        strike_max=int(1.2*strike_0)
        
        if used_strikes[stock]==[]:
            while strike<strike_max:
                ce_info=get_quote(stock,instrument='OPTSTK',expiry=expiry,option_type='CE',\
                                  strike=strike)
                dof2=ce_info['data'][0]
                
                if len(dof2)==0 or dof2['buyPrice1']=='-' or dof2['sellPrice1']=='-':
                    if abs(strike-strike_0)<0.02*strike_0 and len(used_strikes[stock])==0:
                        total_stocks.remove(stock)
                        break
                    strike+=2.5
                    continue
                dof2['buyPrice1']=pd.to_numeric(dof2['buyPrice1'].replace(',',''))
                dof2['sellPrice1']=pd.to_numeric(dof2['sellPrice1'].replace(',',''))    
                if dof2['sellPrice1']/dof2['buyPrice1']>1.2:
                    strike+=2.5
                    continue
                pe_info=get_quote(stock,instrument='OPTSTK',expiry=expiry,option_type='PE',\
                                  strike=strike)
                dof3=pe_info['data'][0]
                if len(dof3)==0 or dof3['buyPrice1']=='-' or dof3['sellPrice1']=='-':
                    if abs(strike-strike_0)<0.02*strike_0 and len(used_strikes[stock])==0:
                        total_stocks.remove(stock)
                        break
                    strike+=2.5
                    continue
                dof3['buyPrice1']=pd.to_numeric(dof3['buyPrice1'].replace(',',''))
                dof3['sellPrice1']=pd.to_numeric(dof3['sellPrice1'].replace(',','')) 
                if dof3['sellPrice1']/dof3['buyPrice1']>1.2: 
                    strike+=2.5
                    continue
                
                used_strikes[stock].append(strike)
                
                ce_price=(dof2['buyPrice1']+dof2['sellPrice1'])/2
                pe_price=(dof3['buyPrice1']+dof3['sellPrice1'])/2
                if abs(strike-(pe_price-ce_price)-strike_0)>strike_0*diff_threshold:
                    print("Anomaly found in "+stock+" for strike "+str(strike)+"......")
                    print("Op price:"+str(strike-(ce_price-pe_price)))
                    print("Fut price:"+str(strike_0))
                strike+=2.5
                
        else:
            for strike in used_strikes[stock]:
                ce_info=get_quote(stock,instrument='OPTSTK',expiry=expiry,option_type='CE',\
                                  strike=strike)
                dof2=ce_info['data'][0]
                if len(dof2)==0 or dof2['buyPrice1']=='-' or dof2['sellPrice1']=='-':
                    used_strikes[stock].remove(strike)
                    continue
                dof2['buyPrice1']=pd.to_numeric(dof2['buyPrice1'].replace(',',''))
                dof2['sellPrice1']=pd.to_numeric(dof2['sellPrice1'].replace(',',''))     
                if dof2['sellPrice1']/dof2['buyPrice1']>1.2: 
                    used_strikes[stock].remove(strike)
                    continue
                pe_info=get_quote(stock,instrument='OPTSTK',expiry=expiry,option_type='PE',\
                                  strike=strike)
                dof3=pe_info['data'][0]
                if len(dof3)==0 or dof3['buyPrice1']=='-' or dof3['sellPrice1']=='-':
                    used_strikes[stock].remove(strike)
                    continue
                dof3['buyPrice1']=pd.to_numeric(dof3['buyPrice1'].replace(',',''))
                dof3['sellPrice1']=pd.to_numeric(dof3['sellPrice1'].replace(',','')) 
                if dof3['sellPrice1']/dof3['buyPrice1']>1.2: 
                    used_strikes[stock].remove(strike)
                    continue
                
                ce_price=(dof2['buyPrice1']+dof2['sellPrice1'])/2
                pe_price=(dof3['buyPrice1']+dof3['sellPrice1'])/2
                if abs(strike-(pe_price-ce_price)-strike_0)>strike_0*diff_threshold:
                    print("Anomaly found in "+stock+" for strike "+str(strike)+"......")
                    print("Op price:"+str(strike-(ce_price-pe_price)))
                    print("Fut price:"+str(strike_0))

    prev_time=current_time