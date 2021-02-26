#!/bin/bash

echo "Asia/Shanghai" > /etc/timezone

echo -e "LANG=\"zh_CN.UTF-8\"\nLANGUAGE=\"zh_CN:zh:en_US:en\"" >> /etc/environment
echo -e "en_US.UTF-8 UTF-8\nzh_CN.UTF-8 UTF-8\nzh_CN.GBK GBK\nzh_CN GB2312" >> /var/lib/locales/supported.d/local
echo -e "export LANG=\"en_US.UTF-8\"\nalias python3='PYTHONIOENCODING=utf-8 python3'\nlocale-gen" >> /root/.bashrc
source /root/.bashrc

echo 'requirepass hhsrc' >> /etc/redis/redis.conf
sed -i 's/bind 127.0.0.1 ::1/# bind 127.0.0.1 ::1/g' /etc/redis/redis.conf
sed -i 's/\[mysqld\]/\[mysqld\]\nwait_timeout=31536000\ninteractive_timeout=31536000/g' /etc/mysql/mariadb.conf.d/50-server.cnf
/etc/init.d/redis-server start

service rabbitmq-server start
rabbitmqctl add_user hhsrc hhsrc
rabbitmqctl add_vhost hhsrc
rabbitmqctl set_user_tags hhsrc administrator
rabbitmqctl set_permissions -p hhsrc hhsrc ".*" ".*" ".*"

cd /tmp
service mysql start
mysqladmin 
mysql -uroot -proot < db.sql --default-character-set=utf8
service mysql restart

nohup celery flower --broker=amqp://hhsrc:hhsrc@127.0.0.1:5672/hhsrc --basic_auth=hhsrc:hhsrc &

/bin/bash