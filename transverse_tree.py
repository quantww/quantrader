from Klang.lang import kparser,setPY,Kexec
from Klang import (Kl,
    C,O,V,H,L, CLOSE,HIGH,DATETIME,
    MA,CROSS,BARSLAST,HHV,COUNT,
    MAX,MIN,MACD,TRANSVERSE)
from Klang.common import end as today
import talib 

import sys
import linecache
import pandas as pd

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo(a):
    return Kl.currentdf['name'] + "-" + Kl.currentdf['code']

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

all_list = []
def main_loop(start,endday):
    offset = 60 #要计算MA60，所以之前的60不能计算

    #for df in Kl.df_all[:100]:
    for df in Kl.df_all:
        
        Kl.code(df["code"])
        if start is None:
            Kl.date(end=endday)
        else:
            Kl.data(start=start,end=endday)
        try:
            if len(C) < 70:
                continue

            allC = C.data

            datelist = []
        
            for i in range(10,len(C)-offset):
                datelist.append(str(DATETIME[i]))

        except:
            pass

        for i in range(0,len(datelist)):
            d = datelist[i]
            Kl.date(end=d)
            try:
                ma5  = MA(C,5)
                ma10 = MA(C,10)
                ma30 = MA(C,30)
                ma60 = MA(C,60)
                v20 =  MA(V,20)
                valv1 = V / v20 
                valc1 = ((C-C[1]) / C[1]) * 100
                valc5 = C / ma5  
                valc10 = C / ma10  
                valc60 = C / ma60 
                maxc10 = talib.MAX(allC[-10-i:-i-1],9)[-1]
                target = ((maxc10- C.data[-1] ) / C.data[-1] )* 100
                tran = TRANSVERSE() #60日波动，<15判定为横盘震荡
                if target > 10:
                    label = 1
                else:
                    label = 0
                if(valc1 > 8):
                    #print(C.data[-1],allC[-11-i],maxc10)
                    print(Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc60,valc1,valv1,tran,label)
                    all_list.append([Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc60,valc1,valv1,tran,label])
            except :
                print("Klang ERROR",df['code'],df['name'])

                PrintException()

main_loop(start=None,endday='2021-07-01')
fields = ['name','code','日期','5日均线比','10日均线比','60日均线比','涨幅','20日量比','60日震荡','是否涨幅10%']
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_train'+today+'.csv',index=False)


all_list = []
main_loop(start='2021-07-15',endday=today)
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_test'+today+'.csv',index=False)


