import redis

class redisUtil:
    # 创建连接池并连接到redis，并设置最大连接数量;
    # conn_pool = redis.ConnectionPool(host='192.168.31.11',
    #                                  port=6379,
    #                                  max_connections=10,
    #                                  password='120721')
    conn_pool = redis.ConnectionPool(host='home.hddly.cn',
                                     port=56379,
                                     max_connections=10,
                                     password='120721')
    # 第一个客户端访问
    # re_pool = redis.Redis(connection_pool=conn_pool)

    #在集合中添加值
    def sadd(self,setname,setvalues):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        re_pool.sadd(setname,setvalues)

    #将一个或多个值 value 插入到列表 key 的表尾(最右边)
    def rpush(self,setname,setvalues):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        re_pool.rpush(setname, setvalues)

    #移除并返回列表 key 的头元素
    def lpop(self,setname):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        return re_pool.lpop(setname)
    #在集合中添加值
    def spop(self,setname):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        return re_pool.spop(setname)

    #在集合中判断值存在
    def sismember(self,setname,setvalue):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        return re_pool.sismember(setname,setvalue)

    #在集合中删除某个元素
    def sremove(self,setname,setvalue):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        return re_pool.srem(setname,setvalue)

    #将集合中的所有元素删除
    def sremoveall(self,setname):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        value=re_pool.spop(setname)
        i=0
        while (value):
            value = re_pool.spop(setname)
            i=i+1
        return i

    #获取集合元素个数
    def scard(self,setname):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        return re_pool.scard(setname)

    #设置字典中的键值
    def hset(self,setdname, setkey, setvalue):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        re_pool.hset(setdname, setkey, setvalue)

    # 获取字典中的键值
    def hget(self,setdname, setkey):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        re_pool.hget(setdname, setkey)

    # 获取字典中的键值
    def hgetall(self,setdname):
        re_pool = redis.Redis(connection_pool=self.conn_pool)
        # re_pool.hlen(setdname)
        return re_pool.hgetall(setdname)