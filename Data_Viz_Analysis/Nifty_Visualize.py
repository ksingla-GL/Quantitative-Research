# -*- coding: utf-8 -*-
"""
Created on Sat May  4 12:28:31 2019

@author: Spectre
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime as dt
from nsepy import get_history
from datetime import datetime as date2

futs=pd.DataFrame()
for year in range(2007,2020):
    for month in range(1,13):
        if year==2019 and month==8:
            break
        cur_fut=pd.read_csv(str(year)+'/'+str(month)+'/Fut.csv')
        futs=futs.append(cur_fut)
        
atms=pd.DataFrame()
for date in np.unique(futs['Date']):
    atm_price=int(futs.loc[futs['Date']==date,'Close'].values[0]//100*100)
    exp_date=futs.loc[futs['Date']==date,'Expiry'].values[0]
    month=pd.to_datetime(date).month
    yr=pd.to_datetime(date).year
    if yr<2007:
        continue
    try:
        ce=pd.read_csv(str(yr)+'/'+str(month)+'/'+'CE/'+str(atm_price)+'.csv')
        pe=pd.read_csv(str(yr)+'/'+str(month)+'/'+'PE/'+str(atm_price)+'.csv')
    except:
        ce=get_history(symbol='NIFTY',start=date2(yr,month,1),end=pd.to_datetime(exp_date),\
            index=True,option_type='CE',strike_price=atm_price,expiry_date=pd.to_datetime(exp_date))
        ce=ce.reset_index().rename(columns={'index':'Date'})
        pe=get_history(symbol='NIFTY',start=date2(yr,month,1),end=pd.to_datetime(exp_date),\
            index=True,option_type='PE',strike_price=atm_price,expiry_date=pd.to_datetime(exp_date))
        pe=pe.reset_index().rename(columns={'index':'Date'})
    try:
        ce=ce.loc[(ce['Date']==pd.to_datetime(date).to_pydatetime().date())&(ce['Expiry']==\
                  pd.to_datetime(exp_date).to_pydatetime().date()),'Close'].values[0]
        pe=pe.loc[(pe['Date']==date)&(pe['Expiry']==exp_date),'Close'].values[0]
    except:
        ce=np.nan
        pe=np.nan
    atms=atms.append([[date,atm_price,ce,pe]])         
atms.columns=['Date','Atm_Fut','Atm_CE','Atm_PE']  
atms['Year']=pd.to_datetime(atms['Date']).dt.year
atms['Date_sliced']=atms['Date'].str[-5:]

fig=plt.figure(figsize=(25,15))
i=1
for year in np.unique(atms['Year']):
    data=atms.loc[atms['Year']==year]
    data['Atm_CE']=data['Atm_CE']/data['Atm_Fut']*100
    data['Atm_PE']=data['Atm_PE']/data['Atm_Fut']*100
    ax1=fig.add_subplot(4,4,i)
    ax1.plot(data['Date_sliced'],data[['Atm_CE','Atm_PE']])
    ax1.legend(['Atm_CE','Atm_PE'])  
    plt.title('TS Plot for '+str(year))
    i+=1
    
fig.tight_layout()
fig.savefig('../Nifty_DV_Output/'+'ATM_Prices_Perc2.png')

futs=pd.DataFrame()
for year in range(2010,2019):
    for month in range(1,13):
        if year==2018 and month==4:
            break
        cur_fut=pd.read_csv(str(year)+'/'+str(month)+'/Fut.csv')
        futs=futs.append(cur_fut)

otms=pd.DataFrame()
for date in np.unique(futs['Date']):
    atm_price=int(futs.loc[futs['Date']==date,'Close'].values[0]//100*100)
    exp_date=futs.loc[futs['Date']==date,'Expiry'].values[0]
    month=pd.to_datetime(date).month
    yr=pd.to_datetime(date).year
    if yr<2007:
        continue
    
    otmp_ce=int(atm_price*1.1//100*100)
    while True:        
        try:
            ce=pd.read_csv(str(yr)+'/'+str(month)+'/'+'CE/'+str(otmp_ce)+'.csv')
            break
        except:
            otmp_ce-=100
    otmp_pe=int(atm_price*0.9//100*100)
    while True:        
        try:
            pe=pd.read_csv(str(yr)+'/'+str(month)+'/'+'PE/'+str(otmp_pe)+'.csv')
            break
        except:
            otmp_pe+=100
    
    try:
        ce=ce.loc[(ce['Date']==date)&(ce['Expiry']==exp_date),'Close'].values[0]
        pe=pe.loc[(pe['Date']==date)&(pe['Expiry']==exp_date),'Close'].values[0]
    except:
        ce=np.nan
        pe=np.nan
    otms=otms.append([[date,atm_price,ce,pe,otmp_ce,otmp_pe]])  
       
otms.columns=['Date','Atm_Fut','Atm_CE','Atm_PE','Strike_CE','Strike_PE']  
otms['Year']=pd.to_datetime(otms['Date']).dt.year
otms['Date_sliced']=otms['Date'].str[-5:]

vols=pd.DataFrame()
for date in np.unique(futs['Date']):
    atm_price=futs.loc[futs['Date']==date,'Close'].values[0]    
    vols=vols.append([[date,atm_price]]) 
    
vols.columns=['Date','Atm']
vols['Ret']=vols['Atm']/vols['Atm'].shift(1)-1
vols['Year']=pd.to_datetime(vols['Date']).dt.year
vols['Month']=pd.to_datetime(vols['Date']).dt.month
stds=pd.DataFrame(vols.groupby(['Year','Month'])['Ret'].std())
stds=stds.reset_index()
stds['Ret']*=100

fig2=plt.figure(figsize=(25,15))
i=1
for year in np.unique(stds['Year']):
    if year<2007:
        continue
    data=stds[stds['Year']==year]
    ax2=fig2.add_subplot(4,3,i)
    ax2.plot(data['Month'],data['Ret'])
    plt.title('Std TS plot for '+str(year))
    plt.xlabel('Month')
    plt.ylabel('Vol')
    i+=1
    
fig2.tight_layout()
fig2.savefig('../Nifty_DV_Output/'+'ATM_Fut_Rets_Vols2.png')

futs['Year']=pd.to_datetime(futs['Date']).dt.year
futs['Month']=pd.to_datetime(futs['Date']).dt.month

for i in [1,2,5,10,22]:
    futs[str(i)+'d_ret']=futs['Close']/futs['Close'].shift(i)-1
    
sum1=pd.DataFrame(futs.groupby(['Year','Month'])['1d_ret'].sum())    
sum1.plot()   

sum20=pd.DataFrame(futs.groupby(['Year','Month'])['20d_ret'].sum())    

