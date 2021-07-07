#!/bin/bash

echo "Asia/Shanghai" > /etc/timezone

echo -e "LANG=\"zh_CN.UTF-8\"\nLANGUAGE=\"zh_CN:zh:en_US:en\"" >> /etc/environment
echo -e "en_US.UTF-8 UTF-8\nzh_CN.UTF-8 UTF-8\nzh_CN.GBK GBK\nzh_CN GB2312" >> /var/lib/locales/supported.d/local
echo -e "export LANG=\"en_US.UTF-8\"\nalias python3='PYTHONIOENCODING=utf-8 python3'\nlocale-gen" >> /root/.bashrc
source /root/.bashrc

cd /tmp
service mysql start
mysqladmin 
mysql -uroot -proot < db.sql --default-character-set=utf8
service mysql restart

nohup celery flower --broker=amqp://hhsrc:hhsrc@127.0.0.1:5672/hhsrc --basic_auth=hhsrc:hhsrc &

/bin/bash
