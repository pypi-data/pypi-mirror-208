import paramiko
# sftpUtils.py

#############################配置信息#####################################
# 登陆参数设置
hostname = "home.hddly.cn"
host_port = 8021
username = "ftpuser"
password = "ywq20120721"
remotedir = "/media/"
########################################################################


def sftp_putfile(local_path,remote_file):
    t = paramiko.Transport((hostname, host_port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    remote_path = "/media/" + remote_file  # 远程路径
    put_info = sftp.put(local_path, remote_path, confirm=True)
    print(put_info)
    print(f"finished put file:{local_path}.")
    t.close

def sftp_getfile(remote_file,local_path):
    t = paramiko.Transport((hostname, host_port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    remote_path = "/media/" + remote_file  # 远程路径
    sftp.get(remotepath=remote_path, localpath=local_path)
    print(f"finished get file:{local_path}.")
    t.close