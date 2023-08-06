#coding=utf-8
# formatHtml

from bs4 import BeautifulSoup
import chardet

# url = 'http://www.tipdm.com/tipdm/index.html'
def getfile(file):
    with open(file, 'r') as f:
        data=f.read()
        print(data)
    return data

data=getfile("C:\\tmp\\b50506.html")
encoding = chardet.detect(data)['encoding']
# 初始化HTML
html = data.decode()
print("格式化前文本：",html)
soup = BeautifulSoup(html, "lxml")    # 生成BeautifulSoup对象
print("输出格式化的BeautifulSoup对象:", soup.prettify())
# 代码 3-28
# 通过name参数搜索名为title的全部子节点
print ("名为title的全部子节点:" , soup.find_all("title"))
print ("title子节点的文本内容:" , soup.title.string)
print ("使用get_text()获取的文本内容:" , soup.title.get_text())
target = soup.find_all("ul", class_="menu")   # 按照CSS类名完全匹配
print("CSS类名匹配获取的节点:" , target)
target = soup.find_all(id='menu')            # 传入关键字id，按符合条件的搜索
print("关键字id匹配的节点:" , target)
target = soup.ul.find_all('a')
print("所有名称为a的节点:" , target)
# 创建两个空列表用于存放链接及文本
urls = []
text = []
# 分别提取链接和文本
for tag in target:
    urls.append(tag.get('href'))
    text.append(tag.get_text())
for url in urls:
    print(url)
for i in text:
    print(i)
