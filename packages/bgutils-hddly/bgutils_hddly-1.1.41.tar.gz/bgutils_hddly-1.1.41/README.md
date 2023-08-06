# 概括
bgutils是一个适用于bigdata.hddly.cn大数据实验室的工具包
## 说明
本报名字为*packer*,使用方法包括数据库连接工具mysqlUtil,mongoUtil,文件上传工具ftpUtils...

### 打包方法
生成requirements.txt
pip install pipreqs
pipreqs ./ --encoding=utf8
安装setuptools& wheel
python -m pip install --upgrade setuptools wheel
安装twine
python -m pip install --upgrade twine
打包
python setup.py sdist bdist_wheel
发布
python -m twine upload -u goodym -p ywq****** --repository-url https://upload.pypi.org/legacy/  dist/*
### 安装方法
pip install -r requirements.txt
或
pip install -r requirements.txt  -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
### 参数说明

### 使用安装
pip install bgutils-hddly
pip install --upgrade bgutils-hddly
pip install --default-timeout=100 --upgrade bgutils-hddly
### 错误反馈
### 发布到国源pip源

### 查看版本
pip3 show bgutils-hddly

### 卸载版本
pip uninstall bgutils-hddly

### 安装依赖
pip3 install redis -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
