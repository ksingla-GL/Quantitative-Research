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
turnover_threshold=10000
scale_threshold=1.25

fos=pd.read_csv("fo_mktlots.csv")
fos=fos['SYMBOL    '].tolist()
fos=fos[4:]
total_stocks=[]
for stock in fos:
    stock=stock.replace(' ','')
    total_stocks.append(stock)
    
def find_nearest_strike(stock,atm_price,prev_date,cur_date,expiry):
    strike=atm_price*0.975//10*10
    end=atm_price*1.025
    closest=end-strike
    nearest_strike=0
    step=0.25 if atm_price<100 else 2.5
    nearest_ce=0
    while strike<=end:
        ce= get_history(symbol=stock,start=prev_date,end=cur_date,\
            index=False,option_type='CE',strike_price=strike,expiry_date=pd.to_datetime(expiry))
        if len(ce)==0 or (ce['Turnover'].values<turnover_threshold).any():
            strike+=step
            continue        
        elif abs(strike-atm_price)<closest:
            closest=abs(strike-atm_price)
            nearest_strike=strike
            nearest_ce=ce
            if closest/atm_price<0.01:
                break
        strike+=step
    return nearest_strike,nearest_ce

def find_itm_strike(stock,atm_price,op_type,prev_date,cur_date,expiry):
    if op_type=='CE':
        strike=atm_price*0.925//10*10
        #end=atm_price*0.975
    else:
        strike=atm_price*1.0825//10*10
        #end=atm_price*1.025//10*10
    farthest=0
    farthest_strike=0
    step=0.25 if atm_price<100 else 2.5
    farthest_op=0
    while abs(strike-atm_price)>0.02*atm_price:
        op= get_history(symbol=stock,start=prev_date,end=cur_date,\
            index=False,option_type=op_type,strike_price=strike,expiry_date=pd.to_datetime(expiry))
        if len(op)==0 or (op['Turnover'].values<turnover_threshold).any():
            if op_type=='CE':
                strike+=step
            else:
                strike-=step
            continue        
        elif abs(strike-atm_price)>farthest:
            farthest=abs(strike-atm_price)
            farthest_strike=strike
            farthest_op=op
            
            if op_type=='CE':
                if abs((strike+op.loc[op.index==prev_date,'Close'].values[0])-atm_price)<0.01*atm_price:
                    break
            elif abs((strike-op.loc[op.index==prev_date,'Close'].values[0])-atm_price)<0.01*atm_price:
                break

        if op_type=='CE':
            strike+=step
        else:
            strike-=step
    return farthest_strike,farthest_op
  
res=pd.DataFrame(columns=['Date','Stock','Fut','CE_Strike','PE_Strike','Op_Cost','PnL'])
for year in range(2016,2017):
    for month in range(1,13):
        #year=2020
        #month=4
        prev_month=month-1 if month>1 else 12
        prev_year=year if prev_month==month-1 else year-1
        
        expiry=max([i for i in get_expiry_date(year=year, month=month)])     
        for stock in total_stocks:                         
            fut_prices=get_history(symbol=stock,start=date(prev_year,prev_month,24),
            end=pd.to_datetime(expiry),futures=True,index=False,expiry_date=expiry)
            if len(fut_prices)<8:
                continue

            prevdate=fut_prices.index.values[6]
            for dat in fut_prices.index.values[7:-7]:
                strike=int(fut_prices.loc[fut_prices.index==prevdate,'Close'].values[0])
                atm=strike
                strike,ce=find_itm_strike(stock,strike,'CE',prevdate,dat,expiry)
                if strike==0 or np.mean(ce['Turnover'].values)<turnover_threshold:
                    prevdate=dat
                    continue
                # ce.loc[ce.index==prevdate,'Close'].values[0]/strike>threshold 
                if np.mean(fut_prices.loc[fut_prices.index<dat,'Turnover'].iloc[-7:].values)<turnover_threshold:
                    prevdate=dat
                    continue
                
                strike=atm
                atm_ce_strike,atm_ce=find_nearest_strike(stock,strike,prevdate,dat,expiry)
                if atm_ce_strike==0:
                    prevdate=dat
                    continue
                
                if np.std(fut_prices.loc[fut_prices.index<dat,'Close'].iloc[-7:].values)>atm_ce.loc[atm_ce.index\
                ==prevdate,'Close'].values[0]*scale_threshold:
                    strike=atm
                    pe_strike,pe=find_itm_strike(stock,strike,'PE',prevdate,dat,expiry)
                    if np.mean(pe['Turnover'].values)<turnover_threshold:
                        prevdate=dat
                        continue
                    res.loc[len(res)]=[prevdate,stock,fut_prices.loc[fut_prices.index==prevdate,'Close'].values[0]\
                    ,strike,pe_strike,ce.loc[ce.index==prevdate,'Close'].values[0]+pe.loc[pe.index\
                    ==prevdate,'Close'].values[0],(ce.loc[ce.index==dat,'Close'].values[0]+pe.loc[pe.index\
                    ==dat,'Close'].values[0])-(ce.loc[ce.index==prevdate,'Close'].values[0]+pe.loc[pe.index\
                    ==prevdate,'Close'].values[0])]
                prevdate=dat
                
res['pnl_perc']=res['PnL']/res['Op_Cost']
                