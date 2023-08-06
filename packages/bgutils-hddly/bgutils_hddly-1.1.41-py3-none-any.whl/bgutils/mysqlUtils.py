import json
import pandas as pd
from sqlalchemy import create_engine
class bgmysqlUtil:
    def __init__(self):
        mysql_username = 'test'
        mysql_password = 'test'
        # 填写真实数库ip
        mysql_ip = 'home.hddly.cn'
        port = 53306
        db = 'test'
        # 初始化数据库连接,使用pymysql库
        self.engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(mysql_username, mysql_password, mysql_ip, port, db))

    # 查询mysql数据库
    def query(self, sql):
        df = pd.read_sql_query(sql, self.engine)
        # df = pandas.read_sql(sql,self.engine)     这种读取方式也可以

        # 返回dateframe格式
        return df

    def select_rand_db(self, types=None):
        if types:
            sql = "select ip,port,types from eie_ip where types='{}' order by rand() limit 1".format(types)
        else:
            sql = "select ip,port,types from eie_ip order by rand() limit 1 "
        df = pd.read_sql(sql, self.engine)
        results = json.loads(df.to_json(orient='records'))
        if results and len(results) == 1:
            return results[0]
        return None