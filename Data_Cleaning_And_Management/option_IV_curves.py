# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:28:31 2020

@author: Spectre
"""

"""Hyperparams"""
rate=7.0
threshold=0.08
turnover_threshold=25
scale_threshold=1.25
year=2020
month=11

import pandas as pd

fos=pd.read_csv("C:/Users/Spectre/Desktop/Live_Data/fo_mktlots.csv")
fos=fos['SYMBOL    '].tolist()
fos=fos[4:]
total_stocks=[]
for stock in fos:
    stock=stock.replace(' ','')
    total_stocks.append(stock)

from bs4 import BeautifulSoup as bs

URL="https://zerodha.com/margin-calculator/SPAN/"
#page = urllib.urlopen(quote_page)
    
import requests 
r = requests.get(URL) 
#print(r.content) 

soup = bs(r.content, 'html5lib') 
childs=list(soup.children)
l2=list(childs[1])
ptags=soup.find_all('p')
texts=[]

for i in range(len(ptags)):
    string=ptags[i].get_text()
    string=string.replace('\n','')
    string=string.replace('\t','')
    texts.append(string)

bans=texts[4].split(',')
for i in range(len(bans)):
    bans[i]=bans[i].replace(' ','')

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

def find_OTM_strikes(stock,atm_price,expiry):
    strike=int(atm_price*1.25//10)*10
    end=int(atm_price//10)*10
    farthest=strike-end
    farthest_strike_ce=0
    step=-10 if atm_price>1000 else -5
    if atm_price>15000:
        step=-100
        strike=int(atm_price*1.25//100)*100
    elif atm_price>7000:
        step=-50
        strike=int(atm_price*1.25//50)*50
    farthest_ce=0
    while strike>=end:
        try:
            ce= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='CE', strike=strike)
        except:
            try:
                pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='CE', strike=strike)
            except:
                strike+=step
                continue
        if len(ce)==0 or len(ce['data'][0])==0 or ce['data'][0]['turnoverinRsLakhs']=='-' or int(ce['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
            strike+=step
            continue        
        elif abs(strike-atm_price)<=farthest:
            farthest=abs(strike-atm_price)
            farthest_strike_ce=strike
            farthest_ce=ce
            break
        strike+=step
    
    """NOW RUNNING FOR PUTS"""
    strike=int(atm_price*0.7//10)*10
    end=int(atm_price//10)*10
    farthest=end-strike
    farthest_strike_pe=0
    step=10 if atm_price>1000 else 5
    if atm_price>15000:
        step=100
        strike=int(atm_price*0.7//100)*100
    elif atm_price>7000:
        step=50
        strike=int(atm_price*0.7//50)*50
    farthest_pe=0
    while strike<=end:
        try:
            pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='PE', strike=strike)
        except:
            try:
                pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='PE', strike=strike)
            except:
                strike+=step
                continue
        if len(pe)==0 or len(pe['data'][0])==0 or pe['data'][0]['turnoverinRsLakhs']=='-' or int(pe['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
            strike+=step
            continue        
        elif abs(strike-atm_price)<=farthest:
            farthest=abs(strike-atm_price)
            farthest_strike_pe=strike
            farthest_pe=pe
            break
        strike+=step
    return farthest_strike_ce,farthest_strike_pe
            
def find_ITM_strikes(stock,atm_price,expiry):
    strike=int(atm_price*1.25//10)*10
    end=int(atm_price//10)*10
    farthest=strike-end
    farthest_strike_ce=0
    farthest_strike_pe=0
    step=-10 if atm_price>1000 else -5
    if atm_price>15000:
        step=-100
        strike=int(atm_price*1.25//100)*100
    elif atm_price>7000:
        step=-50
        strike=int(atm_price*1.25//50)*50
    #farthest_pe=0
    while strike>=end:
        try:
            pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='PE', strike=strike)
        except:
            try:
                pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='PE', strike=strike)
            except:
                strike+=step
                continue
        if len(pe)==0 or len(pe['data'][0])==0 or pe['data'][0]['turnoverinRsLakhs']=='-' or int(pe['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
            strike+=step
            continue        
        elif abs(strike-atm_price)<=farthest:
            farthest=abs(strike-atm_price)
            farthest_strike_pe=strike
            #farthest_pe=pe
            break
        strike+=step
    
    """NOW RUNNING FOR CALLS"""
    strike=int(atm_price*0.7//10)*10
    end=int(atm_price//10)*10
    farthest=end-strike
    farthest_strike_ce=0
    step=10 if atm_price>1000 else 5
    if atm_price>15000:
        step=100
        strike=int(atm_price*0.7//100)*100
    elif atm_price>7000:
        step=50
        strike=int(atm_price*0.7//50)*50
    #farthest_ce=0
    while strike<=end:
        try:
            ce= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='CE', strike=strike)
        except:
            try:
                ce= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='CE', strike=strike)
            except:
                strike+=step
                continue
        if len(ce)==0 or len(ce['data'][0])==0 or ce['data'][0]['turnoverinRsLakhs']=='-' or int(ce['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
            strike+=step
            continue        
        elif abs(strike-atm_price)<=farthest:
            farthest=abs(strike-atm_price)
            farthest_strike_ce=strike
            #farthest_ce=ce
            break
        strike+=step
    
    return farthest_strike_ce,farthest_strike_pe

def draw_IV_curve(stock,atm_price,start_strike,end_strike,expiry):
    res=pd.DataFrame(columns=['Strike','IV'])
    step=10 if max(start_strike,end_strike)>1000 else 5
    if atm_price>15000:
        step=100
        start_strike=int(start_strike//100)*100
    elif atm_price>7000:
        step=50
        start_strike=int(start_strike//50)*50
    decay=(expiry-datetime.date(datetime.now())).days
    
    if end_strike>start_strike:
        strike=start_strike
        while strike<=end_strike:
            ce= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='CE', strike=strike)
            if len(ce)==0 or len(ce['data'][0])==0 or ce['data'][0]['turnoverinRsLakhs']=='-' or int(ce['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
                strike+=step
                continue
            x=ce['data'][0]['lastPrice']
            x=str(x).replace(',','')
            if x=='-' or abs(pd.to_numeric(x))<0.01 or x==0 or x==0.0:
                strike+=step
                continue
            c=mibian.BS([atm_price,strike,rate,decay],callPrice=pd.to_numeric(x))
            res.loc[len(res)]=[strike,c.impliedVolatility]
            strike+=step
            #print("Done strike "+str(strike))
    else:
        strike=start_strike
        while strike>=end_strike:
            pe= get_quote(symbol=stock, instrument='OPTSTK', \
                expiry=expiry,option_type='PE', strike=strike)
            if len(pe)==0 or len(pe['data'][0])==0 or pe['data'][0]['turnoverinRsLakhs']=='-' or int(pe['data'][0]['turnoverinRsLakhs'].replace(',','').\
               split('.')[0])<turnover_threshold:
                strike-=step
                continue
            x=pe['data'][0]['lastPrice']
            x=str(x).replace(',','')
            if x=='-' or abs(pd.to_numeric(x))<0.01 or x==0 or x==0.0:
                strike-=step
                continue
            p=mibian.BS([atm_price,strike,rate,decay],putPrice=pd.to_numeric(x))
            res.loc[len(res)]=[strike,p.impliedVolatility]
            strike-=step
    #res.set_index("Strike").plot(title='IV of '+stock)            
    return res

os.chdir("C:/Users/Spectre/Desktop/Live_Data/IV_Curves/Aug")
#import matplotlib
import matplotlib.pyplot as plt
#stock='SBIN'


#expiry=max([i for i in get_expiry_date(year=year, month=month)])
expiry=datetime.date(date(2020,11,26))
nse=Nse()

def draw_adhoc_curves(stock):
    q = nse.get_quote(stock)
    
    atm_price=q['lastPrice']
    otm_ce,otm_pe=find_OTM_strikes(stock,atm_price,expiry)
    itm_ce,itm_pe=find_ITM_strikes(stock,atm_price,expiry)
    ce_res=draw_IV_curve(stock,atm_price,itm_ce,otm_ce,expiry)
    ce_res.set_index("Strike").plot(title='IV of CE for '+stock+" priced "+str(atm_price))
    pe_res=draw_IV_curve(stock,atm_price,itm_pe,otm_pe,expiry)        
    pe_res.set_index("Strike").plot(title='IV of PE for '+stock+" priced "+str(atm_price))
    return ce_res,pe_res

c,p=draw_adhoc_curves('CHOLAFIN')
"""
for stock in total_stocks[122:]:
    if stock in bans or stock+"_PE.png" in os.listdir("Plots") or stock+"_CE for .png" in \
    os.listdir("Plots"):
        print("Already done with "+stock)
        continue
    q = nse.get_quote(stock)
    #current_price_info=get_quote(stock,instrument='FUTSTK',expiry=expiry)
    if len(q)>0:
        atm_price=q['lastPrice']
    #op_type='CE'
    #strike=int(atm_price*1.25//10)*10
    #end=int(atm_price//10)*10
    
    otm_ce,otm_pe=find_OTM_strikes(stock,atm_price,expiry)
    itm_ce,itm_pe=find_ITM_strikes(stock,atm_price,expiry)
    
    print(stock+" done")
    if otm_ce==0 or itm_ce==0:
        if otm_pe==0 or itm_pe==0:
            continue
    else:
        ce_res=draw_IV_curve(stock,atm_price,itm_ce,otm_ce,expiry)
        ce_res.set_index("Strike").plot(title='IV of CE for '+stock+" priced "+str(atm_price))
        plt.savefig("Plots/"+stock+"_CE for .png")
        plt.close()
        ce_res.to_csv("Output/"+stock+"_CE for "+str(atm_price)+".csv")
    if otm_pe!=0 and itm_pe!=0:
        pe_res=draw_IV_curve(stock,atm_price,itm_pe,otm_pe,expiry)        
        pe_res.set_index("Strike").plot(title='IV of PE for '+stock+" priced "+str(atm_price))
        plt.savefig("Plots/"+stock+"_PE.png")
        plt.close()
        pe_res.to_csv("Output/"+stock+"_PE for "+str(atm_price)+".csv")
        
"""