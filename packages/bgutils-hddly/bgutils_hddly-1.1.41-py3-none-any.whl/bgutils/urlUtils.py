import chardet
import requests
from bs4 import BeautifulSoup

from C3.BigData.entity.entUrlResult import entUrlResult


def getUrlContent(url):
    ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) Chrome/65.0.3325.181'}
    rqg = requests.get(url, headers=ua)
    rqg.encoding = chardet.detect(rqg.content)['encoding']
    # 初始化HTML
    print('rqg.encoding:',rqg.encoding)
    if rqg.encoding=='GB2312':
        html = rqg.content.decode('gbk')
    else:
        html = rqg.content.decode(rqg.encoding)
    print("格式化前文本：", html)
    return html

def getUrlResult(url):
    html = getUrlContent(url)
    soup = BeautifulSoup(html, "lxml")  # 生成BeautifulSoup对象
    tags_a = soup.find_all('a')
    if soup.find('title'):
        title = soup.find('title').text
    else:
        return
    urllist=[]
    print("所有名称为a的标签的个数:", len(tags_a))  # 获取所有名称为a的标签的个数
    for tag in tags_a:
        if tag.attrs.get('href') and (tag.attrs.get('href').startswith('http://')
                                      or tag.attrs.get('href').startswith('https://')):
            print(tag.attrs.get('href'))
            urllist.append(tag.attrs.get('href'))
    rlt = entUrlResult(url,title,html,urllist)
    return rlt

def getUrlLinkDeeps_0(url):
    urllist_all = []
    urllist_0 = []
    urllist_0.extend(getUrlResult(url).urls)
    for url0 in urllist_0:
        print("url0:",url0)
    urllist_all.extend(urllist_0)
    return urllist_all

def getUrlLinkDeeps_1(url):
    urllist_all = []
    urllist_0 = []
    urllist_1 = []
    urllist_0.extend(getUrlResult(url).urls)
    for url0 in urllist_0:
        print("url0:",url0)
        urllist_1.extend(getUrlResult(url0).urls)
    urllist_all.extend(urllist_0)
    urllist_all.extend(urllist_1)
    return urllist_all

