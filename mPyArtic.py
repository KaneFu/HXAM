#-*- coding:utf8 -*-
#
#

from arctic import Arctic, tickstore, date
import datetime
import pytz
import json
import pandas as pd
import array

#import time
#import ptvsd
#ptvsd.enable_attach(secret = 'artic')

TZ_LOCAL = pytz.timezone('Asia/Shanghai')

DB_HOST = '192.168.10.252'
DB_PORT = 27017

DB_ORDER_COLLECTION = 'HXAM.order'
DB_TRANS_COLLECTION = 'HXAM.transaction'
DB_ORDERQUEUE_COLLECTION = 'HXAM.orderqueue'
DB_TICK_COLLECTION = 'HXAM.tick'  #HXAM数据库中tick表

STORE = Arctic('%s:%d' % (DB_HOST,DB_PORT))

def Init_library_DataBase(collection):
    # Data is grouped into 'libraries'.
    # Users may have one or more named libraries:
    STORE.list_libraries()
    
    # Create a library
    # STORE.initialize_library(collection)
    
    # Get a library
    library = STORE[collection]
    return library


ORDER_HANDLE = Init_library_DataBase(DB_ORDER_COLLECTION)
TRANS_HANDLE = Init_library_DataBase(DB_TRANS_COLLECTION)
ORDERQUEUE_HANDLE = Init_library_DataBase(DB_ORDERQUEUE_COLLECTION)
TICK_HANDLE = Init_library_DataBase(DB_TICK_COLLECTION)

def insertOrder(dic, arrTmap = None):
    # {'index': datetime.datetime(2012, 5, 2, 1, 15, 0, 80000, tzinfo=<UTC>), 
    #     'FC': 66, 'I': 9814, 'OK': 48, 'P': 0.1, 'V': 100, 'id': u'000001.SZ'}

    if arrTmap != None:
        for t in arrTmap:
            # data[t] = data[t].map(time_t2datetime)
            # dic[t] = [time_t2datetime(x) for x in dic[t]]
            if not type(dic[t]) is array.array:
                dic[t] = array.array('d',[dic[t],])
            dic[t] = map(time_t2datetime, dic[t])
    # print dic['id'][0]
    ORDER_HANDLE.write(dic['id'][0], dic)

def insertTrans(dic, arrTmap = None):
    # {'index': datetime.datetime(2012, 5, 2, 1, 15, 0, 80000, tzinfo=<UTC>), 
    #     'FC': 66, 'BSF': 66, 'OK': 48, 'P': 0.1, 'V': 100, 'id': u'000001.SZ', 'AO': , 'BO', }

    if arrTmap != None:
        for t in arrTmap:
            # data[t] = data[t].map(time_t2datetime)
            if not type(dic[t]) is array.array:
                dic[t] = array.array('d',[dic[t],])
            dic[t] = map(time_t2datetime, dic[t])
    # print dic['id'][0]
    TRANS_HANDLE.write(dic['id'][0], dic)

def insertTick(dic, arrTmap = None):
    # {'index': datetime.datetime(2012, 5, 2, 1, 15, 0, 80000, tzinfo=<UTC>), 
    #     'P': 0.1, 'V': 100, 'T': , 'MI': , 'O': , 'H': , 'L': , 'PC': , 'TAV': ,
    #     'TBV': , 'AV': , 'AT': , 'AAP': , 'BAP': , 'TF': , 'BSF': , 'IT': ,
    #     'AP10': , 'AV10': , 'BP10': , 'BV10': , 'id': u'000001.SZ'}
    # time.sleep(60)
    # print type(dic['id'])
    # if not type(dic['index']) is array.array:
    #    print 'change type'
    #    dic = tupledic(dic)
    if arrTmap != None:
        for t in arrTmap:
            # data[t] = data[t].map(time_t2datetime)
            if not type(dic[t]) is array.array:
                dic[t] = array.array('d',[dic[t],])
            dic[t] = map(time_t2datetime, dic[t])
    TICK_HANDLE.write(dic['id'][0], dic)

def insertOrderQueue(dic, arrTmap = None):
    # {'index': datetime.datetime(2012, 5, 2, 1, 15, 0, 80000, tzinfo=<UTC>), 
    #     'P': 0.1, 'S': 60, 'id': u'000001.SZ', 'OI': , 'ABI': , 'ABV50': }

    if arrTmap != None:
        for t in arrTmap:
            # data[t] = data[t].map(time_t2datetime)
            if not type(dic[t]) is array.array:
                dic[t] = array.array('d',[dic[t],])
            dic[t] = map(time_t2datetime, dic[t])
    # print dic['id'][0]
    ORDERQUEUE_HANDLE.write(dic['id'][0], dic)

def time_t2datetime(timet):
    # localize timet, then change it to utc time
    return TZ_LOCAL.localize(datetime.datetime.utcfromtimestamp(timet)).astimezone (pytz.utc)

def stdDate(dt):
    return dt.replace(tzinfo=TZ_LOCAL).astimezone(pytz.utc)