

### 前言

陆陆续续尝试写了个扫描平台，方便src的信息收集，又想只用台vps就跑得动，又要功能全面，于是就开始写这个项目了

hhsrc项目是将一些**优秀的工具（在最后有罗列）**集成起来，也学习了一些优秀的框架，最后该平台采用了flask+mysql+celery的方式，实现多个客户端异步同时扫描



整个项目分为server和client 2个模块，server为信息存储平台，client为扫描模块，可分开部署，client可部署多台，只需要client的redis和rabbitmq的地址填server的即可



### 性能效果

目前可以以同时只扫1个项目的设置下，在2G内存的vps上同时运行客户端和服务器端2个docker容器



### 扫描逻辑思路

![](img/0_4.png)



### 部署方法

##### 服务器端

先配置redis和rabbitmq的密码(默认为:hhsrc，建议修改)

hhsrc_server/docker_config/init.sh

```
echo 'requirepass [redis密码]' >> /etc/redis/redis.conf
sed -i 's/bind 127.0.0.1 ::1/# bind 127.0.0.1 ::1/g' /etc/redis/redis.conf
/etc/init.d/redis-server start

service rabbitmq-server start
rabbitmqctl add_user hhsrc [rabbitmq密码]
rabbitmqctl add_vhost hhsrc
rabbitmqctl set_user_tags hhsrc administrator
rabbitmqctl set_permissions -p hhsrc hhsrc ".*" ".*" ".*"

cd /tmp
service mysql start
mysqladmin 
mysql -uroot -proot < db.sql --default-character-set=utf8
service mysql restart

nohup celery flower --broker=amqp://hhsrc:[rabbitmq密码]@127.0.0.1:5672/hhsrc --basic_auth=hhsrc:[flower密码] &
```

然后修改redis和rabbitmq的地址，PUBLIC_HOST填公网地址，该地址用于celery服务监控

hhsrc_server/config.ini

```
[CELERY_CONFIG]
CELERY_BROKER_URL = amqp://hhsrc:hhsrc@127.0.0.1:5672/hhsrc
CELERY_RESULT_BACKEND = redis://:hhsrc@127.0.0.1:6379/2

[DATABASE]
DB_HOST = 127.0.0.1
DB_USER = root
DB_PASSWD = root
DB_DATABASE = hhsrc

[HOST]
PUBLIC_HOST = 127.0.0.1
```

此时就可以启动客户端了

```
hhsrc_server/

docker-compose build
docker-compose up -d
```



##### 客户端

修改docker-compose.yaml 中的redis和rabbitmq地址为server的地址，注意这里客户端和服务器端如果部署在同一台服务器上，地址应为docker的网关地址，可以用以下命令查看

```
docker inspect [容器id]
```

修改docker-compose.yaml

```
version: "2"
services:
  worker:
    build: .
    tty: true
    environment:
      DEBUG: 'False'
      BROKER: 'amqp://hhsrc:hhsrc@127.0.0.1:5672/hhsrc'
      BACKEND: 'redis://:hhsrc@127.0.0.1:6379/2'
      TZ: Asia/Shanghai
    restart: always
```

之后启动docker

```
hhsrc_client/

docker-compose build
docker-compose up -d

#进入docker启动脚本
docker exec -it hhsrcclient_worker_1 bash
cd /app
python3 client_run.py
```

### 搜索语法

搜索语法参考了rengine的搜索方式，一个搜索框，每个条件以&&分隔，进行模糊查询

如可以使用

```
target=123&&start_time=2021-01-15&&end_time=2021-01-16
```

获取到时间在2021年1月15日到2021年1月16日之间有更新，项目属于123的资产

下面是各个页面的搜索关键字

| 模块                                     | 搜索内容                   | 搜索关键字 |
| ---------------------------------------- | -------------------------- | ---------- |
| 所有模块                                 | 项目名                     | Target     |
| 所有模块                                 | 项目更新起始时间           | start_time |
| 所有模块                                 | 项目更新终止时间           | end_time   |
| 子域名扫描模块，端口扫描模块             | 子域名名                   | subdomain  |
| 子域名扫描模块，端口扫描模块             | ip地址                     | ip         |
| 端口扫描模块                             | 端口号                     | port       |
| 端口扫描模块                             | 端口服务                   | server     |
| 站点扫描模块，路径扫描模块，漏洞扫描模块 | 站点地址(查询时不带协议头) | url        |
| 站点扫描模块，路径扫描模块               | 页面标题                   | title      |
| 站点扫描模块，路径扫描模块               | 页面响应码                 | status     |
| 漏洞扫描模块                             | 漏洞等级                   | level      |
| 漏洞扫描模块                             | 漏洞信息                   | info       |



### 界面展示

hhsrc的版本为1.3.0是因为之前也写过2版的收集工具它们是这样的，使用的react，django前后端分离的形式数据库使用的MongoDB，第二版界面美观了许多但感觉没必要，而且代码写起来比较麻烦

第一版 1.0

![0_1](img/0_1.png)

第二版 2.0

![0_2](img/0_2.png)

![0_3](img/0_3.png)

hhsrc v1.3.1版本，前端更加的朴实，将精力着重于扫描逻辑代码

项目界面

![1](img/1.png)

项目详情

![2](img/2.png)

项目添加，增加了针对子域名添加和ip目标的添加

![3](img/3.png)

子域名扫描结果展示

![4](img/4.png)

端口扫描结果展示

![5](img/5.png)

http站点页面展示

![6](img/6.png)

站点详情

![7](img/7.png)

目录扫描

![8](img/8.png)

扫描模式添加（api爬取和指纹识别暂时没写完，这里选不选都无所谓）

![9](img/9.png)

周期配置，定时如周的值为4，小时为2，分钟为0，则表示在每周4，2:00重新扫描，*代码通配

![10](img/10.png)

worker监控，最多扫描任务数设置（最多扫描任务数为1，表示同时只有1个项目在扫描）

celery监控是用iframe加载了5555端口的flower，设置校验后才能查看，默认配置是hhsrc/hhsrc

![11](img/11.png)



### 结语

目前该系统还有很多需要完善的地方，也可能有还没发现的bug，后续会陆续修复

参考如下

#### 类似工具参考平台

rengine https://github.com/yogeshojha/rengine

bayonet https://github.com/CTF-MissFeng/bayonet

漏洞盒子的灯塔ARL https://github.com/TophantTechnology/ARL

LangSrcCurise https://github.com/LangziFun/LangSrcCurise

#### 工具列表

subfinder [https://github.com/projectdiscovery/subfinder](https://github.com/projectdiscovery/subfinder)
domaininfo(来自于ARL) 
naabu [https://github.com/projectdiscovery/naabu](https://github.com/projectdiscovery/naabu)
nmap [https://github.com/nmap/nmap](https://github.com/nmap/nmap)
httpx [https://github.com/projectdiscovery/httpx](https://github.com/projectdiscovery/httpx)
leakfile(来自于ARL)
gau [https://github.com/lc/gau](https://github.com/lc/gau) (待定，实际效果并不是太理想)
nuclei https://github.com/projectdiscovery/nuclei

#### 前端样式使用以下项目

https://github.com/xiiiblue/flask-adminlte-scaffold



***请注意，本工具仅供学习、收集目标授权情况下使用，请勿用作非法用途。***