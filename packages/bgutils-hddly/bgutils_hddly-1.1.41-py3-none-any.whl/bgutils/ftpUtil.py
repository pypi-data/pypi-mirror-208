import os

import paramiko
from bgutils.mysqlUtil import mysqlUtil
from moviepy.editor import VideoFileClip


class ftpUtil:
    # 登陆参数设置
    __hostname = "home.hddly.cn"
    __host_port = 8021
    __username_media = "ftpuser"
    __password_media = "ywq20120721"
    __username_stud ="student"
    __password_stud ="student"
    __remotedir_media = "media/"
    __remotedir_stud = "send/"
    __url_head="https://home.hddly.cn:8443/stud/"
    __mutil= mysqlUtil()

    def chk_file_exist_surl(self,surl,fdesc):
        return self.__mutil.chk_file_exist_surl(surl,fdesc)

    def putfile_project(self, local_path, prj_id, stud_id, no_file,fdesc,surl):
        # # 要传输文件的路径
        # filepath = "./myname.jpg"
        # # 上传后的传输文件的文件名
        # remote_file = 项目ID(6位)+学生ID（11位）+文件ID(2位)+文件类型
        # 如P22001_20190010011_01.jpg
        try:
            ftype = os.path.splitext(local_path)[-1]
            if ftype.upper()=='.MP4' or ftype.upper()=='.WMV':
                clip=VideoFileClip(local_path)
                duration=clip.duration
            else:
                duration=0
            fsize=os.path.getsize(local_path)
            # 根据文件大小fsize和时间duration，在数据库中判断是否已采集(>0)，是的话就返回，否则继续
            iexist=self.__mutil.chk_file_exist(fdesc,fsize,duration)
            if iexist>0:
                print("repeat：%s,%d,%f" % (fdesc,fsize,duration))
                return
            transport = paramiko.Transport((self.__hostname, self.__host_port))
            transport.connect(username=self.__username_stud, password=self.__password_stud)
            sftp = paramiko.SFTPClient.from_transport(transport)
            pid="p" + prj_id.zfill(6)
            remotepath = "%s%s"%(self.__remotedir_stud , pid)
            try:
                sftp.chdir(remotepath)
            except:
                sftp.mkdir(remotepath)
                sftp.chdir(remotepath)
            stud = stud_id.zfill(11)
            no = no_file.zfill(8)
            remote_file = "%s%s%s%s"%(pid,stud,no,ftype)
            sftp.put(local_path, remote_file)
            print('success upload......')
            sftp.close()
            transport.close()
        except Exception as ex:
            print("connect error:%s" % ex)

        try:
            # 记录文件列表
            # item = entSftpFile()
            # item['filename'] = local_path
            # item['url'] = self.__url_head+remote_file
            # item['stud'] = stud
            remotefullpath = "%s%s%s/%s" % (self.__url_head,
                                           self.__remotedir_stud,
                                           pid,
                                           remote_file)
            self.__mutil.sftp_file_ins(local_path,
                                       remotefullpath,
                                       stud,
                                       fdesc,
                                       fsize,
                                       duration,
                                       ftype,
                                       pid,
                                       surl)
        except Exception as ex:
            print("sftp_file_ins error:%s" % ex)

    def putfile_stud(self,local_path,prj_id,stud_id,no_file):
        self.putfile_project(local_path,prj_id,stud_id,no_file,'','');


    def putfile_media(self,local_path,remote_file):
        t = paramiko.Transport((self.__hostname, self.__host_port))
        t.connect(username=self.__username_media, password=self.__password_media)
        sftp = paramiko.SFTPClient.from_transport(t)
        remote_path = self.__remotedir_media + remote_file  # 远程路径
        put_info = sftp.put(local_path, remote_path, confirm=True)
        print(put_info)
        print(f"finished put file:{local_path}.")
        t.close

    def getfile_media(self,remote_file,local_path):
        t = paramiko.Transport((self.__username_media, self.__host_port))
        t.connect(username=self.__username_media, password=self.__password_media)
        sftp = paramiko.SFTPClient.from_transport(t)
        remote_path = self.__remotedir_media + remote_file  # 远程路径
        sftp.get(remotepath=remote_path, localpath=local_path)
        print(f"finished get file:{local_path}.")
        t.close