# -*- coding: utf-8 -*-
# Created by Fouvy On 2017/6/29
__author__ = 'fouvy'

import mPyArtic
from datetime import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

stock_code = '300222_sz'  #科大智能
# stock_code = '600000_sh'
#从数据库中读取对应股票某段时间内的数据
data = mPyArtic.TICK_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(datetime(2016,9,1)),mPyArtic.stdDate(datetime(2016,9,30))))
data = mPyArtic.ORDER_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(datetime(2016,9,1)),mPyArtic.stdDate(datetime(2016,9,30))))
data = mPyArtic.TRANS_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(datetime(2016,9,1)),mPyArtic.stdDate(datetime(2016,9,30))))
data = mPyArtic.ORDERQUEUE_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(datetime(2016,9,1)),mPyArtic.stdDate(datetime(2016,9,30))))
data = mPyArtic.TICK_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(datetime(2016,9,1)),mPyArtic.stdDate(datetime(2016,9,30))))
#将时间规范化为本地时间
data.index = data.index.tz_convert(tz=mPyArtic.TZ_LOCAL)
data['2016-09-23 09:50:00':'2016-09-23 14:50:00']
data = data[[u'P', u'V', u'T', u'MI', u'AV', u'AT', u'O',u'AP1',u'AV1']]

date_range = np.unique(data.index.date)
vwap_m = np.zeros(len(date_range))
vwap_s = np.zeros(len(date_range))
day_o  = np.zeros(len(date_range))
for i in range(len(date_range)):
	# print i
	df = data[datetime.combine(date_range[i],time(9,40)):datetime.combine(date_range[i],time(14,56,59))]
	vwap_m[i] = np.sum(df['T'])/np.sum(df['V'])
	day_o[i] = df['O'][-1]
	
	# tra_V_ = df['V'].resample('1min',how='mean')  #1min内平均下单
	# tra_V_ = df['V'].resample('1min').apply(lambda x:np.min(x[x>0]))  #1min内最小交易量下单
	tra_V_ = df['V'].resample('1min').sum()
	tra_V_mean = df['V'].resample('1min').mean()
	ps = df['P'].resample('1min').last()
	ps_mov_avg = pd.rolling_mean(ps,window=1,min_periods=1)
	tra_V_mov_avg = pd.expanding(tra_V_).mean()
	mask = tra_V_>=tra_V_mov_avg #np.logical_and(tra_V_>=tra_V_mov_avg,ps>=ps_mov_avg)
	# print np.sum(mask)
	tra_mount = np.zeros(tra_V_.shape[0])
	tra_mount[mask] = tra_V_mean[mask]
	tra_V_ = tra_mount

	df_tick = df[['AV1','AP1']].resample('1min').last()
	df_tick['tra_V'] = tra_V_
	tra_V = df_tick[['AV1','tra_V']].apply(min,axis=1)

	vol_pct = tra_V/np.sum(tra_V)
	vwap_s[i] = np.sum(vol_pct*df_tick['AP1'])
	
	
print vwap_m
print vwap_s
print np.mean((vwap_m-vwap_s)/day_o)

	# dMI = np.zeros(df.index.shape[0])
	# dMI[0] = df['MI'][0]
	# dMI[1:] = np.diff(df['MI'],1)
	# df['dMI'] = dMI
	
	# df['avgMI'] = df['V']/df['dMI']
	
	# fig = plt.figure()
	# ax1 = fig.add_subplot(111)
	# df['V'].plot(axes=ax1)
	# ax2 = ax1.twinx()
	# df['P'].plot(color='r',axes=ax2)
