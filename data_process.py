#!/usr/bin/env python
# coding=utf-8
import numpy as np
import scipy.io as sio
import h5py
import pandas as pd
from datetime import datetime


path = 'tickab/300001.SZ.mat'
f = h5py.File(path)
data = {}
for k,dataset in f[u'StockTickAB'].items():
	data[k] = dataset.value

fileds = ['Date','Time','Price','Volume','Turover','Open','AccVolume','AccTurover']
stk_data = pd.DataFrame(None)
for filed in fileds:
	print filed
	stk_data[filed] = np.ravel(data[filed])
stk_data['AskPrice1'] = data['AskPrice10'][0,:]

date_ = pd.to_datetime(stk_data['Date'],format='%Y%m%d')
time_ = pd.to_datetime(stk_data['Time'],format='%H%M%S%f')
datetime_ = [0]*date_.shape[0]
for i in range(date_.shape[0]):
	datetime_[i]= datetime.combine(date_[i].date(),time_[i].time()).strftime('%Y-%m-%d %H:%M:%S')
stk_data.index=datetime_
stk_data.drop(['Date','Time'],axis=1,inplace=True)
stk_data.to_csv(path[:-3]+'csv')
