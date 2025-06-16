# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:28:31 2020

@author: Spectre
"""

"""Hyperparams"""
rate=7.0
threshold=0.08
turnover_threshold=1000
scale_threshold=1.25

import pandas as pd

fos=pd.read_csv("C:/Users/Spectre/Desktop/Live_Data/fo_mktlots.csv")
fos=fos['SYMBOL    '].tolist()
fos=fos[4:]
total_stocks=[]
for stock in fos:
    stock=stock.replace(' ','')
    total_stocks.append(stock)

from bs4 import BeautifulSoup as bs

import mibian
from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote,get_futures_chain
from nsetools import Nse

import pandas as pd
import numpy as np
import os

from datetime import datetime
from datetime import timedelta

def find_OTM_strikes(stock,fut_prices,expiry):
    
    #cur_date=fut_prices.index.values[1]
    #prev_date=fut_prices.index.values[0]
    itm_pes=[]
    itm_ces=[]
    for ind in range(1,len(fut_prices)):
        cur_date=fut_prices.index.values[ind]
        prev_date=fut_prices.index.values[ind-1]
        atm_price=fut_prices.loc[fut_prices.index==cur_date,'Close'].values[0]
        
        strike=int(atm_price*1.25//10)*10
        end=int(atm_price//10)*10
        farthest=strike-end
        farthest_strike_ce=0
        farthest_strike_pe=0
        step=-10 if atm_price>400 else -5
        
        if atm_price>25000:
            step=-500
        elif atm_price>10000:
            step=-250   
        elif atm_price>5000:
            step=-100   
        elif atm_price>2500:
            step=-50
        elif atm_price>1000:
            step=-20
        strike=int(atm_price*1.25//step)*step
        #farthest_pe=0
        while strike>=end:
            try:
                ce= get_history(symbol=stock,start=cur_date,end=cur_date,\
                index=False,option_type='CE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
            except:
                try:
                    ce=get_history(symbol=stock,start=cur_date,end=cur_date,\
                    index=False,option_type='CE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
                except:
                    strike+=step
                    if strike<end:
                        itm_ces.append(0)
                    #itm_pes.append(0)
                    continue
            if len(ce)==0 or ce['Turnover'].iloc[0]=='-' or ce['Turnover'].iloc[0]<turnover_threshold:
                strike+=step
                if strike<end:
                    itm_ces.append(0)
                #itm_pes.append(0)
                continue        
            farthest=abs(strike-atm_price)
            farthest_strike_ce=strike
            itm_ces.append(strike)
            break
            #strike+=step
        
        """NOW RUNNING FOR CALLS"""
        strike=int(atm_price*0.7//10)*10
        end=int(atm_price//10)*10
        farthest=end-strike
        farthest_strike_pe=0
        step=-10 if atm_price>400 else -5
        
        if atm_price>25000:
            step=-500
        elif atm_price>10000:
            step=-250   
        elif atm_price>5000:
            step=-100   
        elif atm_price>2500:
            step=-50
        elif atm_price>1000:
            step=-20
        step*=-1
        strike=int(atm_price*0.7//step)*step
        
        while strike<=end:
            try:
                pe= get_history(symbol=stock,start=cur_date,end=cur_date,\
                index=False,option_type='PE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
            except:
                try:
                    pe= get_history(symbol=stock,start=cur_date,end=cur_date,\
                    index=False,option_type='PE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
                except:
                    strike+=step
                    #itm_ces.append(0)
                    if strike<end:
                        itm_pes.append(0)
                    continue
            if len(pe)==0 or pe['Turnover'][0]<turnover_threshold:
                strike+=step
                #itm_ces.append(0)
                if strike>end:
                        itm_pes.append(0)
                continue
                
            farthest=abs(strike-atm_price)
            farthest_strike_pe=strike
            #farthest_ce=ce
            itm_pes.append(strike)
            break
            #strike+=step
        
    return itm_ces,itm_pes
            
def find_ITM_strikes(stock,fut_prices,expiry):
    
    #cur_date=fut_prices.index.values[1]
    #prev_date=fut_prices.index.values[0]
    itm_pes=[]
    itm_ces=[]
    for ind in range(1,len(fut_prices)):
        cur_date=fut_prices.index.values[ind]
        prev_date=fut_prices.index.values[ind-1]
        atm_price=fut_prices.loc[fut_prices.index==cur_date,'Close'].values[0]
        
        strike=int(atm_price*1.25//10)*10
        end=int(atm_price//10)*10
        farthest=strike-end
        farthest_strike_ce=0
        farthest_strike_pe=0
        step=-10 if atm_price>400 else -5
        
        if atm_price>25000:
            step=-500
        elif atm_price>10000:
            step=-250   
        elif atm_price>5000:
            step=-100   
        elif atm_price>2500:
            step=-50
        elif atm_price>1000:
            step=-20
        start=int(atm_price*1.25//step)*step
        strike=(((start+end)/2)//step)*step
        ans=0
        #farthest_pe=0
        while strike>=end:
            try:
                pe= get_history(symbol=stock,start=cur_date,end=cur_date,\
                index=False,option_type='PE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
            except:
                try:
                    pe= get_history(symbol=stock,start=cur_date,end=cur_date,\
                    index=False,option_type='PE',strike_price=strike+step,expiry_date=pd.to_datetime(expiry))
                    strike+=step
                except:
                    try:
                        pe= get_history(symbol=stock,start=cur_date,end=cur_date,\
                        index=False,option_type='PE',strike_price=strike-step,expiry_date=pd.to_datetime(expiry))
                        strike-=step
                    except:
                        start=strike
                        strike=(((start+end)/2)//step)*step
                        if strike==start or strike==end:
                            break
                        continue
            if (len(pe)==0 or pe['Turnover'][0]<turnover_threshold):
                start=strike
                strike=(((start+end)/2)//step)*step
                if strike==start or strike==end:
                    break
                continue
            
            if strike>ans:
                ans=strike
            end=strike
            strike=(((start+end)/2)//step)*step
            if strike==start or strike==end:
                break
        itm_pes.append(ans)
        
        """NOW RUNNING FOR CALLS"""
        strike=int(atm_price*0.7//10)*10
        end=int(atm_price//10)*10
        farthest=end-strike
        farthest_strike_ce=0
        step=-10 if atm_price>400 else -5
        
        if atm_price>25000:
            step=-500
        elif atm_price>10000:
            step=-250   
        elif atm_price>5000:
            step=-100   
        elif atm_price>2500:
            step=-50
        elif atm_price>1000:
            step=-20
        step*=-1
        start=int(atm_price*0.7//step)*step
        #farthest_ce=0
        strike=(((start+end)/2)//step)*step
        ans=0
        while strike<=end:
            try:
                ce= get_history(symbol=stock,start=cur_date,end=cur_date,\
                index=False,option_type='CE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
            except:
                try:
                    ce= get_history(symbol=stock,start=cur_date,end=cur_date,\
                    index=False,option_type='CE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
                except:
                    start=strike
                    strike=(((start+end)/2)//step)*step
                    if strike==start or strike==end:
                        break
                    continue
            if (len(ce)==0 or ce['Turnover'][0]<turnover_threshold):
                start=strike
                strike=(((start+end)/2)//step)*step
                if strike==start or strike==end:
                    break
                continue
            
            if strike<ans:
                ans=strike
            end=strike
            strike=(((start+end)/2)//step)*step
            if strike==start or strike==end:
                break
        itm_ces.append(ans)
        
    return itm_ces,itm_pes
  

os.chdir("C:/Users/Spectre/Desktop/Live_Data/IV_Curves")
#import matplotlib
import matplotlib.pyplot as plt

nse=Nse()

year=2017
month=1


for year in range(2017,2020):
    if str(year) not in os.listdir():
        os.mkdir(str(year))
    for month in range(1,13):
        if str(month) not in os.listdir(str(year)):
            os.mkdir(str(year)+"/"+str(month))
        if year==2020 and month>7:
            break
        expiry=max([i for i in get_expiry_date(year=year, month=month)])
        for stock in total_stocks[:]:
            if stock not in os.listdir(str(year)+"/"+str(month)):
                os.mkdir(str(year)+"/"+str(month)+"/"+stock)
            else:
                continue
            
            
            fut_prices=get_history(symbol=stock,start=date(year,month,1),
            end=pd.to_datetime(expiry),futures=True,index=False,expiry_date=expiry)
            #current_price_info=get_quote(stock,instrument='FUTSTK',expiry=expiry)
            if len(fut_prices)>0:
                atm_price=fut_prices['Close'].iloc[0]
            else:
                print(stock+" Fut absent in "+str(month)+"/"+str(year))
                continue
            
            otm_ce,otm_pe=find_OTM_strikes(stock,fut_prices,expiry)
            itm_ce,itm_pe=find_ITM_strikes(stock,fut_prices,expiry)
            df=pd.DataFrame(index=fut_prices.index[1:],columns=['Atm','Itm_CE','Otm_CE','Itm_PE','Otm_PE'])
            #df=pd.DataFrame(index=fut_prices.index[1:],columns=['Atm','Itm_CE','Otm_CE','Itm_PE','Otm_PE'])
            df[:]=np.array([fut_prices['Close'].values[1:].tolist(),itm_ce,otm_ce,itm_pe,otm_pe]).transpose()
            df.to_csv(str(year)+"/"+str(month)+"/"+stock+"/ITM_OTM_Strikes.csv")
