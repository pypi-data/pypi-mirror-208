import os
from setuptools import setup, find_packages

__version__ = '1.0.15'  # 版本号
# requirements = open('requirements.txt').readlines()  # 依赖文件
#pip.exe install -U influxdb --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install -U xmqt --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install -U DingtalkChatbot --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install -U baostock -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages
#pip.exe install -U apscheduler --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install -U kafka-python --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install -U pykafka --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install confluent-kafka --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install taospy --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip.exe install chinese_calendar --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple/
#pip install tqsdk -U  --target=D:\国信iQuant策略交易平台\bin.x64\Lib\site-packages -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host=pypi.tuna.tsinghua.edu.cn


#编译 打包
#python setup.py build
#python setup.py sdit
#发布到pip服务器
#python setup.py upload


setup(

    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # 属于什么类型
        'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        'Programming Language :: Python :: 3.7',
    ],

    name="xmqt",
    version=__version__,
    author="bobzhangfw",
    author_email="bobzhangfw@163.com",
    description="Pyhont Qt Basic Module  -->公众号：Python 量化基础库",

    # 项目主页
    url="http://xoenmap.icu/",

    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(exclude=["tests"]),
    python_requires='>=3.5.0',
    # install_requires=requirements  # 安装依赖
    # # 安装过程中，需要安装的静态文件，如配置文件、service文件、图片等
    # data_files=[
    #     ('', ['conf/*.conf']),
    #     ('/usr/lib/systemd/system/', ['bin/*.service']),
    # ],
    #
    # # 希望被打包的文件
    # package_data={
    #     '': ['*.txt'],
    #     'bandwidth_reporter': ['*.txt']
    # },
    # # 不打包某些文件
    # exclude_package_data={
    #     'bandwidth_reporter': ['*.txt']
    # }
)
