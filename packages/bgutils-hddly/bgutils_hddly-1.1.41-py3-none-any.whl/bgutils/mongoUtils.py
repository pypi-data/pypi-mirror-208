import pymongo

def insertMongdbOne(collecter,title,url,content):
    client = pymongo.MongoClient('home.hddly.cn:57017')
    db = client['pythondb']  # 选择pythondb
    collection = db.test  # 使用 test集合
    # info = {'title': title, 'url': url, 'content': content, 'collecter': collecter}
    info = {'title': title, 'url': url, 'collecter': collecter}
    print(info)
    collection.insert_one(info)
    client.close()  # 关闭Mongodb连接

