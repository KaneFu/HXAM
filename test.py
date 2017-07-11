#-*- coding:utf8 -*-


import mPyArtic
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



stock_code = '300222_sz'  #科大智能
# stock_code = '600006_sh'  #浦发银行
# stock_code = '000001_sz'  #浦发银行

LEN = 30	#历史数据时长
VOL = 100000   #母单大小

#从数据库中读取对应股票某段时间内的数据
start_day = datetime.datetime(2014,4,1)
end_day = datetime.datetime(2014,12,30)
tick = mPyArtic.TICK_HANDLE.read(stock_code,mPyArtic.date.DateRange(mPyArtic.stdDate(start_day),mPyArtic.stdDate(end_day)))
tick.index = tick.index.tz_convert(tz=mPyArtic.TZ_LOCAL)
tick = tick[['P','V','T','MI','AV','AT','AP1','AV1','O']]
date_list = np.unique(tick.index.date)

def prcInd(Series):
	l = Series.shape[0]
	if l == 0:
		return np.nan
	up = np.diff(Series,1)>0
	return float(np.sum(up))/l


VWAP_s = np.zeros(len(date_list)-LEN)*np.nan 
VWAP_m = np.zeros(len(date_list)-LEN)*np.nan
Open = np.zeros(len(date_list)-LEN)*np.nan 
V_trd = np.zeros(len(date_list)-LEN)*np.nan 
Av_claps = np.zeros(len(date_list)-LEN)*np.nan 

for j in range(LEN,len(date_list)):
	
	try:
		#history
		his_dict = {}
		for i in range(j-LEN,j):	
			date = date_list[i]
			# print date
			st = datetime.datetime.combine(date,datetime.time(9,30,0,0))
			ed = datetime.datetime.combine(date,datetime.time(14,56,59,99))
			day_data = tick[st:ed]
			##成交笔数
			dMI = np.zeros(day_data.index.shape[0])
			dMI[0] = day_data['MI'][0]
			dMI[1:] = np.diff(day_data['MI'],1)
			day_data['dMI'] = dMI	
		
			V = day_data['V'].resample('1min').sum().dropna()
			# print V.shape
			V_dist = V/np.sum(V)
			MI = day_data['dMI'].resample('1min').sum().dropna()
			prc_ind = day_data['P'].resample('1min').apply(prcInd).dropna()	
			his_df = pd.DataFrame({'V':V,'V_dist':V_dist,'MI':MI,'prc_ind':prc_ind})
			his_df.index = his_df.index.time
			his_dict[date] = his_df
		
		panel = pd.Panel(his_dict)
		his_dist = panel.minor_xs('V_dist').apply(np.nanmean,axis=1).values
		if len(his_dist) == 237:
			his_dist = np.insert(his_dist,120,0)
		
		panel_v = panel.values[:,:,[0,1,3]]   #day*minute*[MI,V,prc_ind]
		min_v = np.zeros(panel_v.shape[2])
		len_v = np.zeros(panel_v.shape[2])
		for i in range(panel_v.shape[2]):
			min_v[i] = np.nanmin(panel_v[:,:,i])
			len_v[i] = np.nanmax(panel_v[:,:,i]) - np.nanmin(panel_v[:,:,i])
			panel_v[:,:,i] = (panel_v[:,:,i]-min_v[i])/len_v[i]
		
		x = np.apply_along_axis(lambda x:0.7*x[0]+0.1*x[1]+0.2*x[2],2,panel_v)
		x_mean = np.nanmean(x)
		x_std = np.nanstd(x)
		
		today = date_list[j]

		print "today is: ",today
		st = datetime.datetime.combine(today,datetime.time(9,30,0,0))
		ed = datetime.datetime.combine(today,datetime.time(14,56,59,99))
		stmsk = datetime.datetime.combine(today,datetime.time(11,31,0,0))
		edmsk = datetime.datetime.combine(today,datetime.time(12,59,59,99))
		tindx = pd.date_range(start=st,end=ed,freq='1min',tz=mPyArtic.TZ_LOCAL)
		tmsk = pd.date_range(start=stmsk,end=edmsk,freq='1min',tz=mPyArtic.TZ_LOCAL)
		tindx = tindx.difference(tmsk)

		day_data = tick[st:ed]

		##成交笔数
		dMI = np.zeros(day_data.index.shape[0])
		dMI[0] = day_data['MI'][0]
		dMI[1:] = np.diff(day_data['MI'],1)
		day_data['dMI'] = dMI	
		##有时候当天会少几分钟		
		AP1 = day_data['AP1'].resample('1min').last().dropna()
		AV1 = day_data['AV1'].resample('1min').last().dropna()
		
		MI = (day_data['dMI'].resample('1min').sum().dropna()-min_v[0])/len_v[0]
		V = (day_data['V'].resample('1min').sum().dropna()-min_v[1])/len_v[1]
		prc_ind = (day_data['P'].resample('1min').apply(prcInd).dropna()-min_v[2])/len_v[2]
		x = 0.7*V+0.1*MI+0.2*prc_ind
		
		V_delta_hat = VOL*his_dist  #profile 要求的交易数
		V_hat = np.cumsum(V_delta_hat)  #profile 要求的累积交易数
		V_delta = np.zeros(len(V_hat))  #交易数
		Vt = 0  #累积交易数
		flag = False
		av_count = 0  #当天吃掉卖一单量的次数
		for i in range(len(V_hat)):
			if flag:  #母单完成
				pass
			else:
				try:
					if Vt >= V_hat[i]:
						if x[i] < x_mean:
							V_delta[i] = 0
						elif x[i] > x_mean+0.1*x_std:
							V_delta[i] = int((V_delta_hat[i]+V_hat[i]-Vt)*x[i]/x_mean*np.random.uniform(0.9,1.1))
					else:
						V_delta[i] = int(V_delta_hat[i]*x[i]/x_mean*np.random.uniform(0.9,1.1))
					if V_delta[i] >= AV1[i]:
						av_count+=1
						V_delta[i] = AV1[i]
					if Vt+V_delta[i] >= VOL:
						V_delta[i] = VOL - Vt
						flag = True
					Vt+=V_delta[i]

				except Exception as e:
					print e
					break

		
		VWAP_s[j-LEN] = np.sum(V_delta*AP1)/np.sum(V_delta)
		VWAP_m[j-LEN] = day_data['AT'].iloc[-1]/day_data['AV'].iloc[-1]
		Open[j-LEN] = day_data['O'].iloc[-1]
		V_trd[j-LEN] = np.sum(V_delta)
		Av_claps[j-LEN] = av_count

	except Exception as e:
		print e
		# print j
		# print "error day:",today
		continue


diff = (VWAP_m-VWAP_s)/Open
ratio = np.nanmean(diff)
print ratio
print "trd info: ",V_trd
print "claps info: ",Av_claps
with open('log.txt','a') as f:
	f.write('%s\t %s\t %s\t %d\t %d\t %f\t %f\n' 
		% (start_day.strftime('%Y%m%d'),end_day.strftime('%Y%m%d'),stock_code,LEN,VOL,ratio,np.nanmedian(V_trd)))