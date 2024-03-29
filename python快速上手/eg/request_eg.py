import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
import pandas

news_total = []
commentURL = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20'
url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callback=newsloadercallback&_=1509373193047'


def parseListLinks(url):
    newsdetails = []
    res = requests.get(url)
    jd = json.loads(res.text.strip().lstrip('newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetail(ent['url']))
    return newsdetails


def getNewsDetail(newsurl):
    result = {}
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    if soup.select('.second-title'):
        result['title'] = soup.select('.second-title')[0].text
    else:
        resultNone = '没有获取到内容'
        result['title'] = resultNone
        result['newssource'] = resultNone
        result['dt'] = resultNone
        result['article'] = resultNone
        result['editor'] = resultNone
        result['comments'] = getCommentCounts(newsurl)
        return result
    result['newssource'] = soup.select('.date-source')[0].text
    result['dt'] = soup.select('.date')[0].text
    result['article'] = ' '.join([p.text.strip() for p in soup.select('.article')])
    result['editor'] = soup.select('.show_author')[0].text
    result['comments'] = getCommentCounts(newsurl)
    print('获得一条新闻')
    return result


def getCommentCounts(newsurl):
    m = re.search('doc-i(.+).shtml', newsurl)
    newsid = m.group(1)
    comments = requests.get(commentURL.format(newsid))
    jd = json.loads(comments.text.strip('var data='))
    return jd['result']['count']['total']


for i in range(1, 8):
    print('正在爬取第' + str(i) + '页......')
    newsurl = url.format(i)
    newsary = parseListLinks(newsurl)
    news_total.extend(newsary)
print('抓取结束')
df = pandas.DataFrame(news_total)
df.to_excel('news.xlsx')