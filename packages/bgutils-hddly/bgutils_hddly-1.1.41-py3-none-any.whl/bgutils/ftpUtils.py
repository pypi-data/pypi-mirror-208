import paramiko
class bgftpUtil:
    def putpic(self,filepath,filename):
        # # 要传输文件的路径
        # filepath = "./myname.jpg"
        # # 上传后的传输文件的文件名
        # filename = "drawpic_myname.jpg" #请将myname改为本人学号
        try:
            transport = paramiko.Transport(("home.hddly.cn", 8021))
            transport.connect(username = "student", password = "student")
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.chdir("/send/")
            sftp.put(filepath,filename)
            print('上传成功......')
            sftp.close()
            transport.close()
        except:
            print('连接失败......')
