#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.common import * 
import json

api = TdxHq_API()

block_list = []


def get_block():
    all_list = api.get_security_list(1, 0)
    for i in all_list:
        code  = int (i['code'])
        if (code >= 880300) and (code <=880999) and (code != 880650):
            print(i['code'],i['name'])
            block_list.append([i['code'],i['name']])

dayK_list = []
block_list= [

['汽车类','880390'],['酒店餐饮','880423'],['酿酒','880380'],['食品饮料','880372'],['农林牧渔','880360'],['有色','880324'],['日用化工','880355'],['医疗保健','880398'],['石油','880310'],['电力','880305'],['煤炭','880301'],['水务','880454'],['旅游','880424'],['家用电器','880387'],['文教休闲','880422'],['化工','880335'],['环境保护','880456'],['钢铁','880318'],['化纤','880330'],['建材','880344'],['矿物制品','880351'],['电气设备','880446'],['造纸','880350'],['医药','880400'],['纺织服饰','880367'],['家居用品','880399'],['工业机械','880440'],['航空','880430'],['通用机械','880437'],['商业连锁','880406'],['商贸代理','880414'],['传媒娱乐','880418'],['运输设备','880432'],['船舶','880431'],['电器仪表','880448'],['广告包装','880421'],['工程机械','880447'],['公共交通','880453'],['供气供热','880455'],['电信运营','880452'],['仓储物流','880464'],['交通设施','880465'],['运输服务','880459'],['银行','880471'],['半导体','880491'],['元器件','880492'],['软件服务','880493'],['证券','880472'],['房地产','880482'],['保险','880473'],['多元金融','880474'],['IT设备','880489'],['通信设备','880490'],['互联网','880494'],['综合类','880497'],['建筑','880476'],

]
def get_bar():
    content = ""
    
    for line in block_list:
        name = line[0]
        code = line[1]
        datas = api.get_index_bars(9,1, code, 0, 200)

        datas = api.to_df(datas)

        print(code,name,datas)
        if len(datas)<20:
            continue
        datas = datas.assign(date=datas['datetime'].apply(lambda x: str(x)[0:10])).drop(['year', 'month', 'day', 'hour', 'minute', 'datetime'], axis=1)
        datas.rename(columns={'vol':'volume'},inplace = True)

        print(len(datas),datas.iloc[-1].date)
        df = datas.to_json(orient='table')
        jsondatas = json.loads(df)['data']
        for d in jsondatas:
            d['name'] = name
            d['code'] = code
            d['volume'] = float("%.4f" % (d['volume'] * 100)) #股 = 手*100
            del d['index']

        dayK_list.append({code:jsondatas})

    save_file("bk.json",json.dumps(dayK_list))



if api.connect('119.147.212.81', 7709):
    # 获取板块

    #get_block()
    
    get_bar()
