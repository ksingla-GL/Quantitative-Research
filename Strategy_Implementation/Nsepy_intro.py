# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 22:15:55 2019

@author: Spectre
"""

from nsepy import get_history
from datetime import datetime as date
from nsepy.derivatives import get_expiry_date
from nsepy.history import get_price_list
from nsepy.live import get_quote

sbin = get_history(symbol='SBIN',
                    start=date(2015,1,1), 
                    end=date(2015,1,10))

expiry = get_expiry_date(year=2015, month=1)
stock_fut = get_history(symbol="SBIN",
                            start=date(2015,1,1),
                            end=date(2015,1,10),
                            futures=True,
                            expiry_date=[i for i in get_expiry_date(2015,1)][-1])

nifty_opt = get_history(symbol="NIFTY",
                        start=date(2015,1,1),
                        end=date(2015,1,10),
                        index=True,
                        option_type='CE',
                        strike_price=8200,
                        expiry_date=date(2015,1,29))

vix = get_history(symbol="INDIAVIX",
            start=date(2015,1,1),
            end=date(2015,1,10),
            index=True)

bhav_copy = get_price_list(dt=date(2020,3,27))

current_price_info=get_quote(symbol='NIFTY', instrument='OPTIDX', expiry=get_expiry_date(year=2019, month=8),\
                             option_type='CE', strike=11500)
current_price_info=get_quote('SBIN')
