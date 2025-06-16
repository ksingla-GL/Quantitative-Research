# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 12:05:38 2019

@author: Spectre
"""

import os
import pandas as pd
import numpy as np

os.chdir("C:/Users/Spectre/Desktop/Nifty_Data")

ordered_cols=['Option Type','Expiry','Open','High','Low','Close','Turnover','Open Interest',\
              'Change in OI','Underlying']

for year in range(2007,2019):
    for month in range(1,13):
        if year==2019 and month==8:
            break
        cur_fut=pd.read_csv(str(year)+'/'+str(month)+'/Fut.csv')
        
        for file in os.listdir(str(year)+'/'+str(month)+'/'+'CE'):
            ce_new=pd.read_csv(str(year)+'/'+str(month)+'/'+'CE'+'/'+file)
            pe_new=pd.read_csv(str(year)+'/'+str(month)+'/'+'PE'+'/'+file)
            cur_fut=cur_fut.append(ce_new)
            cur_fut=cur_fut.append(pe_new)
        for date in np.unique(cur_fut['Date']):
            day=cur_fut.loc[cur_fut['Date']==date]
            if str(year) not in os.listdir('Day_Format'):
                os.mkdir('Day_Format/'+str(year))
            if str(month) not in os.listdir('Day_Format/'+str(year)+'/'):
                os.mkdir('Day_Format/'+str(year)+'/'+str(month))
            day.set_index('Strike Price')[ordered_cols].to_csv('Day_Format/'+str(year)+'/'+str(month)\
                          +'/'+date+'.csv')
            
