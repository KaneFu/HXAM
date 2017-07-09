#!/usr/bin/env python
# coding=utf-8
import pandas as pd
import datetime


data = 'tickab/300001.SZ.csv'
df = pd.read_csv(data,index_col=0,parse_dates=True)
vwap = df.resample('D',how='last').dropna(axis=0,how='all')
vwap['vwap_m'] = vwap['Turover']/vwap['Volume']
# panel_dict = {}
for day in vwap.index.date:
	data = df[day.strftime('%Y-%m-%d')][datetime.datetime.combine(day,datetime.time(9,30)):]
	print data.shape