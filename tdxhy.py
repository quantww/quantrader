#pytdx

import os
from pytdx.hq import TdxHq_API
import pandas as pd
from common.common import *
from common.framework import init_stock_list,getstockinfo
api = TdxHq_API()

serverip = '119.147.212.81'
serverip = '119.147.212.81'

tdxblockdf = ''
tdxblockex = ''

float2 = lambda a:float('%.2f' % a)

block_list = []

filename = './datas/stock_tdx_block'+endday+'.html'

codename = {}
content = ""

#获取所有的板块
def get_block():
    all_list = api.get_security_list(1, 0)
    for i in all_list:
        code  = int (i['code'])
        if (code >= 880300) and (code <=880999) and (code != 880650):
            #print(i['code'],i['name'])
            block_list.append([i['code'],i['name']])
dayK_list = []
#获取板块日K数据
def get_blockbar():
    global content
    for i in block_list:
        code = i[0]
        name = i[1]
        datas = api.get_index_bars(9,1, code, 0, 20)
        if datas == None or len(datas)<20:
            continue
        c1 = datas[-1]['close']
        d1 = datas[-1]['datetime']
        c2 = datas[-2]['close']
        c5 = datas[-5]['close']
        c10 = datas[-10]['close']
        c20 = datas[-20]['close']
        print(name,code,d1,c1,(c1-c2)*100/c2,(c1-c5)*100/c5,(c1-c10)*100/c10,(c1-c20)*100/c20)
        dayK_list.append([name,code,d1,c1,(c1-c2)*100/c2,(c1-c5)*100/c5,(c1-c10)*100/c10,(c1-c20)*100/c20])

    df = pd.DataFrame(dayK_list,columns=['name','code','date','close','今日涨幅','周涨幅','半月涨幅','月涨幅'])
    df = df.sort_values(by='今日涨幅',ascending=False).reset_index()

    del df['index']
    content += df.loc[df['今日涨幅']> 0,:].to_html(escape=False,float_format='%.2f')


    df1 = df.iloc[:20]

    df = df.sort_values(by='周涨幅',ascending=False).reset_index()
    
    del df['index']

    content += df.loc[df['周涨幅']>0,:].to_html(escape=False,float_format='%.2f')
 
    return df1, df.iloc[:20]

    #print("save file",filename)
    #save_file(filename,content)



#获取个股对应的板块名称
def QA_fetch_get_tdx_industry() -> pd.DataFrame:
    import random
    import tempfile
    import shutil
    import os
    from urllib.request import urlopen
    global tdxblockdf

    def gettempdir():
        tmpdir_root = tempfile.gettempdir()
        subdir_name = 'tdx_base' #+ str(random.randint(0, 1000000))
        tmpdir = os.path.join(tmpdir_root, subdir_name)
        if not os.path.exists(tmpdir): 
            os.makedirs(tmpdir)

        return tmpdir
 
    def download_tdx_file(tmpdir) -> str:
        url = 'http://www.tdx.com.cn/products/data/data/dbf/base.zip'
        try:
            file = tmpdir + '/' + 'base.zip'
            f = urlopen(url)
            data = f.read()
            with open(file, 'wb') as code:
                code.write(data)
            f.close()
            shutil.unpack_archive(file, extract_dir=tmpdir)
            os.remove(file)
        except:
            pass
        return tmpdir

    def read_industry(folder:str) -> pd.DataFrame:
        incon = folder + '/incon.dat' # tdx industry file
        hy = folder + '/tdxhy.cfg' # tdx stock file

        tbk = {}
        # tdx industry file
        with open(incon, encoding='GB18030', mode='r') as f:
            incon = f.readlines()
        incon_dict = {}
        for i in incon:
            if i[0] == '#' and i[1] != '#':
                j = i.replace('\n', '').replace('#', '')
                incon_dict[j] = []
                start = 1
            else:
                if i[1] != '#':
                    codelist = i.replace('\n', '').split(' ')[0].split('|')
                    if len(codelist[0]) == 5 and codelist[0][0] == 'T':
                        tbk[codelist[0]] = codelist[1]

                    incon_dict[j].append(i.replace('\n', '').split(' ')[0].split('|'))

        incon = pd.concat([pd.DataFrame.from_dict(v).assign(type=k) for k,v in incon_dict.items()]) \
            .rename({0: 'code', 1: 'name'}, axis=1).reset_index(drop=True)


        with open(hy, encoding='GB18030', mode='r') as f:
            hy = f.readlines()
        hy = [line.replace('\n', '') for line in hy]
        hy = pd.DataFrame(line.split('|') for line in hy)
        # filter codes
        hy = hy[~hy[1].str.startswith('9')]
        hy = hy[~hy[1].str.startswith('2')]

        hy1 = hy[[1, 2]].set_index(2).join(incon.set_index('code')).set_index(1)[['name', 'type']]
        hy2 = hy[[1, 3]].set_index(3).join(incon.set_index('code')).set_index(1)[['name', 'type']]

        # add 56 tdx block
        count = 0
        hy['tbk1'] = ""
        for i in hy[2].values:
            if len(i) >=5:
                hy['tbk1'].iloc[count] = tbk[i[:5]]
            count += 1

        # join tdxhy and swhy
        df = hy.set_index(1) \
            .join(hy1.rename({'name': hy1.dropna()['type'].values[0], 'type': hy1.dropna()['type'].values[0]+'_type'}, axis=1)) \
            .join(hy2.rename({'name': hy2.dropna()['type'].values[0], 'type': hy2.dropna()['type'].values[0]+'_type'}, axis=1)).reset_index()

        df.rename({0: 'sse', 1: 'code', 2: 'TDX_code', 3: 'SW_code'}, axis=1, inplace=True)
        df = df[[i for i in df.columns if not isinstance(i, int) and  '_type' not in str(i)]]
        df.columns = [i.lower() for i in df.columns]

        #shutil.rmtree(folder, ignore_errors=True)
        return df
    folder = gettempdir()
    dirpath = folder
    if not os.path.exists(folder + '/incon.dat') or not os.path.exists(folder + '/tdxhy.cfg'): 
        print("Save file to ",folder)
        download_tdx_file(folder)

    if len(tdxblockdf ) < 1000:
        print("Read file from ",folder)
        df = read_industry(folder)
        tdxblockdf = df


#获取个股日K数据
def get_bar(code,sse):
    sse = int(sse)
    code = str(code)
    api.connect(serverip, 7709)

    if sse == 1:
        code1 = 'sh' + code
    else:
        code1 = 'sz' + code

    datas = api.get_security_bars(9,sse,code, 0, 10)
    info = api.get_finance_info(sse, code)
    datas = api.to_df(datas)

    if len(datas) < 5:
        return None
    try:
        liutonggu = float(info['liutongguben'])
    except:
        liutonggu = 0.1
    close = datas.close.iloc[-1]
    close1 = datas.close.iloc[-2]
    close5 = datas.close.iloc[-5]
    c1 = (close -close1) / close1
    c5 = (close -close5) / close5
    c1 = float(c1)*100
    c5  = float(c5)*100
    liutonggu  = liutonggu * close / 10000 / 10000
    code = code1
    name = codename.get(code,"")
    if (liutonggu < 100):
        return None

    if c5  < 5:
        return None
        
    return (code,name,close,float2(c1),float2(c5),float2(liutonggu))

#初始化 ,并获取概念板块名称
api.connect(serverip, 7709)
api.get_and_parse_block_info('block.dat')
b = api.get_and_parse_block_info('block_gn.dat')
hy1 = pd.DataFrame(b)

# 获取板块
QA_fetch_get_tdx_industry()
hy = tdxblockdf
hydict = {}
hy1dict = {}

#个股对应板块名的表
for i in range(0,len(hy)):
    sse = hy.sse.iloc[i]
    code = hy.code.iloc[i]
    bkname = hy.tdxnhy.iloc[i]
    hydict[code] = [bkname,sse]

#个股对应概念板块的表
for i in range(0,len(hy1)):
    code = hy1.code.iloc[i]
    bkname = hy1.blockname.iloc[i]
    hy1dict[code] = [bkname]


# 0 is name, 1 is sse
def getmarket(code):
    return hydict[code][1]

def gettdxbk(code):
    code = code.split('.')[1]
    return hydict.get(code,[""])[0]

def gettdxgn(code):
    code = code.split('.')[1]
    return hy1dict.get(code,[""])[0]


def create_clickable_code(code):
    url_template= '''<a href="https://gu.qq.com/{code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

def create_color_hqltgz(hqltsz):
    if hqltsz >= 200.0:
        url_template= '''<font color="#ef4136">{hqltsz}</font></a>'''.format(hqltsz=hqltsz)
    else:
        url_template = '''{hqltsz}'''.format(hqltsz=hqltsz)
    return url_template

#获取板块下面的个股数据
def sortblock(bklist,bkname,sse=0):
    global content
    result_list = []
    if sse:
        for i in range(0,len(bklist)):
            ret =  get_bar(bklist.code.iloc[i],getmarket(bklist.code.iloc[i]))
            if ret is not None:
                result_list.append(ret)
    else:
        for i in range(0,len(bklist)):
            ret = get_bar(bklist.code.iloc[i],bklist.sse.iloc[i])
            if ret is not None:
                result_list.append(ret)

    if len(result_list) == 0:
        return

    df = pd.DataFrame(result_list,columns=['code','name','close','今日涨幅','周涨幅','流通市值'])
    df = df.sort_values(by='今日涨幅',ascending=False).reset_index()
    del df['index']

    df['板块'] = bkname
    df['code'] = df['code'].apply(create_clickable_code)
    df['流通市值'] = df['流通市值'].apply(create_clickable_code)
    content += '板块:' + bkname + '\n' 
    content += df.to_html(escape=False,float_format='%.2f')
    

    
#尝试获取板块下面的股票列表
def get_code_list(bkname):
    print(bkname)
    l1 =  hy1.loc[hy1.blockname == bkname,:]
    if len(l1) > 0:
        sortblock(l1,bkname,1)
        return
    
    l =  hy.loc[hy.tdxnhy == bkname,:]
    if len(l):
        sortblock(l,bkname)
        return

    tbk1 = hy.loc[hy.tbk1 == bkname,:]
    if len(tbk1):
        sortblock(tbk1,bkname)
        return

#tdx 板块信息只有 个股code对应板块名
#因此要获取code和股票名的 对应表
alllist = init_stock_list()
for i in alllist:
    code,name,tdxbk,tdxgn = getstockinfo(i)
    codename[code.replace('.','')] = name

if __name__ == "__main__":
    api.connect(serverip, 7709)
    get_block()
    df1,df2 = get_blockbar()

    for i in range(0,len(df1)):
        get_code_list(df1.name.iloc[i])

    for i in range(0,len(df2)):
        get_code_list(df2.name.iloc[i])

    print("save to ", 'file://'+os.getcwd()+ '/' + filename)
    save_file(filename,content)