
from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name="bgutils_hddly",
    version="1.1.41",
    author="hddly",  #作者名字
    author_email="goodym@163.com",
    description="bigdata utils.",
    license="MIT",
    url="https://biglab.site",  #github地址或其他地址
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    install_requires=[
            'pandas>=1.1.0',  #所需要包的版本号
            'numpy>=1.14.0',   #所需要包的版本号
            'paramiko>=2.11.0',
            'pymongo>=3.11.1',
            'requests>=2.26.0',
            'seaborn>=0.11.2',
            'SQLAlchemy>=1.4.27',
            'moviepy>=1.0.3'
    ],
    zip_safe=True,
)

# beautifulsoup4==4.11.1
# C3==0.1
# chardet==4.0.0
# django_recaptcha==3.0.0
# matplotlib==3.2.2
# setuptools==65.4.1

