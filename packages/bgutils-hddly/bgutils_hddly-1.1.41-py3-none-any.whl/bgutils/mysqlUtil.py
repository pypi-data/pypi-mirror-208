import json
import sys

import pandas as pd
from bgutils.redisUtil import redisUtil
from sqlalchemy import create_engine
from sqlalchemy import text

class mysqlUtil:
    __mysql_username = 'test'
    __mysql_password = 'test'
    # 填写真实数库ip
    __mysql_ip = 'home.hddly.cn'
    __port = 53306
    __db = 'test'
    __redis = redisUtil()

    def __init__(self):
        self.OpenDB(self.__db)

    def OpenDB(self, dbname):
        self.__db = dbname
        self.__mysql_ip = 'home.hddly.cn'
        self.__port = 53306
        self.engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.__mysql_username,
                                                    self.__mysql_password,
                                                    self.__mysql_ip,
                                                    self.__port,
                                                    self.__db))

    def OpenDBYgxy(self, dbname):
        self.__db = dbname
        self.__mysql_ip = '10.255.10.51'
        self.__port = 3306
        self.engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.__mysql_username,
                                                    self.__mysql_password,
                                                    self.__mysql_ip,
                                                    self.__port,
                                                    self.__db))

    def OpenDBAny(self, ip, port, dbname):
        self.__db = dbname
        self.__mysql_ip = ip
        self.__port = port
        self.engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(self.__mysql_username,
                                                    self.__mysql_password,
                                                    self.__mysql_ip,
                                                    self.__port,
                                                    self.__db))

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

    # 查询上传文件是否有重复
    def chk_file_exist(self,fdesc,fsize,duration):
        if fsize and duration:
            # 判断float相等： abs(duration-123.31)<0.01
            sql = "select id from sftp_files where fsize={} and  abs(duration-{})<0.01 limit 1".format(fsize,duration)
            connection = self.engine.connect()
            df = pd.read_sql(text(sql), con=connection)
            results = json.loads(df.to_json(orient='records'))
            if results and len(results) == 1:
                # 记录采集重复信息
                sys.stdout.write("repeat:"+fdesc +","+str(fsize)+","+str(duration)+"\n")
                return 1
            else:
                return 0
        else:
            return -1

    def chk_file_exist_surl(self,surl,fdesc):
        if surl and fdesc:
            surl = surl[0:99]  # 只取前100位
            fdesc = fdesc[0:999]
            # 先从redis中判断 是否存在，如果不存在，再从mysql中查找，找到的话添加到redis中
            if self.__redis.sismember("surl",surl):
                return 1
            if self.__redis.sismember("fdesc",fdesc):
                return 1

            # 判断float相等： abs(duration-123.31)<0.01
            sql = "select id from sftp_files where surl='{}' or fdesc='{}' limit 1".format(surl,fdesc)
            connection = self.engine.connect()
            df = pd.read_sql(text(sql), con=connection)
            results = json.loads(df.to_json(orient='records'))
            if results and len(results) == 1:
                # 记录采集重复信息
                self.__redis.sadd("surl",surl)
                self.__redis.sadd("fdesc",fdesc)
                return 1
            else:
                return 0
        else:
            return -1
    # 添加上传文件记录
    def sftp_file_ins(self, filename, url, stud, fdesc, fsize, duration, ftype,pid,surl):
        try:
            df = pd.DataFrame(columns=['filename', 'url', 'stud', 'fdesc', 'fsize', 'duration', 'ftype','pid','surl'])
            # print(df)
            surl=surl[0:99] #截取字符串前100个字符
            row1 = pd.DataFrame(
                {'filename': self.escape(filename),
                 'url': self.escape(url),
                 'stud': self.escape(stud),
                 'fdesc': self.escape(fdesc),
                 'fsize': fsize,
                 'duration': duration,
                 'ftype': ftype,
                 'pid':pid,
                 'surl':self.escape(surl)}, index=[1])
            # print(row1)
            # df=df.append(row1,ignore_index=True)
            df = pd.concat([df, row1], ignore_index=True)  # append过时，改用concat
            # print(df)
            df.to_sql("sftp_files", self.engine, if_exists='append', index=False)  # 'sftp_files'

        except Exception as ex:
            print("sftp_file_ins error:%s" % ex)

    # 获了上传文件记录
    def get_file_list(self, ftype):
        if ftype:
            ftype = str(ftype).lower()
            sql = 'select id,url,fdesc,fsize,duration,ftype,uptime,pid from sftp_files where ftype="{}" order by uptime desc limit 100'.format(
                ftype)
        else:
            ftype = ".mp4"
            sql ='select id,url,fdesc,fsize,duration,ftype,uptime,pid from sftp_files where ftype="{}" order by uptime desc limit 100'.format(
                ftype)
        connection = self.engine.connect()
        df = pd.read_sql(text(sql), con=connection)
        results = json.loads(df.to_json(orient='records'))
        if results and len(results) == 1:
            return results[0]
        elif results and len(results)>1:
            return results
        else:
            return None
        # 获了上传文件记录

    def get_files_bypid(self, pid):
        if pid:
            pid = str(pid).lower()
            sql = 'select id,url,fdesc,fsize,duration,ftype,uptime,pid from sftp_files where pid="{}" order by id desc limit 100'.format(
                pid)
        else:
            pid = "p023101".lower()
            sql ='select id,url,fdesc,fsize,duration,ftype,uptime,pid from sftp_files where pid="{}" order by id desc limit 100'.format(
                pid)
        connection = self.engine.connect()
        df = pd.read_sql(sql=text(sql),con=connection)
        results = json.loads(df.to_json(orient='records'))
        if results and len(results) == 1:
            return results[0]
        elif results and len(results) > 1:
            return results
        else:
            return None

    def process_item(self, item, tblname):
        data = pd.DataFrame(dict(item), index=[0])
        data.to_sql(tblname, self.engine, if_exists='append', index=False)  # 'taobao_data'
        return item

    def escape(self,content) :
        if (content and len(str(content).strip()))>0 :
            content = content.replace("\\\\", "\\\\\\\\");
            content = content.replace("_", "\\\\_");
            content = content.replace("%", "\\\\%");
            content = content.replace("'", "\\\\'");

        return content;

