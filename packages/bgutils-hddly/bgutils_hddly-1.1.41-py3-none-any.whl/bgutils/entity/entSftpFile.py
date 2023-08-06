import urllib.request
class entSftpFile:
    # CREATE TABLE `sftp_files` (
    #   `id` int(10) NOT NULL AUTO_INCREMENT,
    #   `filename` varchar(20) COLLATE utf8_bin NOT NULL,
    #   `url` varchar(200) COLLATE utf8_bin NOT NULL,
    #   `stud` varchar(100) COLLATE utf8_bin NOT NULL,
    #   `uptime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #   PRIMARY KEY (`id`)
    # ) ENGINE=InnoDB AUTO_INCREMENT=482 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
    filename = ""
    url = ""
    stud = ""

    def __init__(self,filename,url,stud) -> None:
        super().__init__()
        self.filename=filename
        url_encode = urllib.request.quote(url, safe='/:?=&', encoding='utf-8')
        self.url=url_encode
        # url解码
        # url_decode = urllib.request.unquote(url_encode)

        self.stud=stud


