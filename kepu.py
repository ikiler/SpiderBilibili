import random

import requests
import sys,getopt
# 导入CSV安装包
import csv

from Logger import ErrorLog, DataLog, Logger

errLog = log = Logger('./log/error.log')
dataLog = log = Logger('log/data.json')
progress = log = Logger('./log/progress.log')
rid = None
page = "1"
outputfile = "defaultSpider.csv"

# 加载User_Agent函数
def LoadUserAgent(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas


def getVideoInfo(url, params, uas):
    # 随机选择user_agent
    ua = random.choice(uas)

    # 蘑菇代理的隧道订单
    appKey = "TndmVERKdldyQjRIcnhqaTpBN3BHS1VVNDBMT2FCbUYy"
    # 蘑菇隧道代理服务器地址
    ip_port = 'secondtransfer.moguproxy.com:9001'
    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}

    # 加载headers
    headers = {
        "Proxy-Authorization": 'Basic ' + appKey,
        'referer': "http://www.bilibili.com/",
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        'User-Agent': ua
    }
    # 通过requests.get来请求数据，再通过json()解析
    i = 0
    while i < 3:
        try:
            response = requests.get(url, params=params, headers=headers, proxies=proxy, verify=False,
                                    allow_redirects=False).json()
            dataLog.logger.info(response)
            data = response['data']['archives']
            return data
        except Exception as e:
            errStr = "出错url：" + url + str(params) +"\n"
            errLog.logger.error(errStr)
            errLog.logger.error(e)
            i += 1
    return None


def parseData(data):
    # 1. 创建文件对象
    f = open(outputfile, 'a', encoding='utf-8')
    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f,delimiter='|')
    # 3. 构建列表头
    # csv_writer.writerow(["aid", "attribute", "bvid", "cid", "ctime", "desc", "mid", "name", "pubdate", "pic"
    #                      , "coin", "danmaku", "favorite", "like", "reply", "share", "view", "title", "tname"])
    aid = data.get('aid', "None")
    attribute = data.get('attribute', "None")
    bvid = data.get('bvid', "None")
    cid = data.get('cid', "None")
    ctime = data.get('ctime', "None")
    desc = data.get('desc', "None")
    mid = data.get('owner', {}).get('mid', "None")
    name = data.get('owner', {}).get('name', "None")
    pubdate = data.get('pubdate', "None")
    pic = data.get('pic', "None")
    coin = data.get('stat', {}).get('coin', "None")
    danmaku = data.get('stat', {}).get('danmaku', "None")
    favorite = data.get('stat', {}).get('favorite', "None")
    like = data.get('stat', {}).get('like', "None")
    reply = data.get('stat', {}).get('reply', "None")
    share = data.get('stat', {}).get('share', "None")
    view = data.get('stat', {}).get('view', "None")
    title = data.get('title', "None")
    tname = data.get('tname', "None")
    # 4. 写入csv文件内容
    csv_writer.writerow([aid, attribute, bvid, cid, ctime, desc, mid, name, pubdate, pic
                            , coin, danmaku, favorite, like, reply, share, view, title, tname])
    # 5. 关闭文件
    f.close()

def initConfig(argv):
    global rid,outputfile,page
    try:
        opts, args = getopt.getopt(argv, "i:p:o:", ["outputfile="])
    except getopt.GetoptError:
        print('spider.py -i <rid> -p <page> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('spider.py -i <rid> -p <page> -o <outputfile>')
            sys.exit()
        elif opt == "-i":
            rid = arg
        elif opt in ("-o", "--outputfile"):
            outputfile = arg
    if rid is None:
        print('-i rid is must!!')
        sys.exit(2)

if __name__ == '__main__':
    initConfig(sys.argv[1:])
    print(rid,page,outputfile)
    sys.exit(2)
    # 加载user_agents.txt文件
    uas = LoadUserAgent("user_agent")
    url = "https://api.bilibili.com/x/web-interface/newlist"
    while (True):
        querystring = {"rid": rid, "type": "0", "pn": page, "ps": "50", "jsonp": "jsonp"}
        data = getVideoInfo(url=url, params=querystring, uas=uas)
        if data is None:
            continue
        elif not data:
            break
        for item in data:
            parseData(item)
        page += 1
    progress.logger.info("科普完成")
#
# headers = {
#     'referer': "http://www.bilibili.com/",
# }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
# json_obj = json.loads(response.text)
