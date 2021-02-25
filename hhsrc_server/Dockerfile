FROM ubuntu:18.04

ADD ./docker_config/sources.list /etc/apt/
ADD ./docker_config/localtime /etc/localtime
ADD ./docker_config/init.sh /tmp/
ADD ./docker_config/db.sql /tmp/

COPY . /app/

RUN apt-get clean && apt-get update
RUN apt-get install -y vim python3 python3-pip nmap redis erlang-nox rabbitmq-server mariadb-server language-pack-zh-hans fontconfig --fix-missing\
    && cd /app \
    && pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt

RUN chmod +x /tmp/init.sh

EXPOSE 5000
EXPOSE 6379
EXPOSE 5672
EXPOSE 5555
CMD ["/tmp/init.sh"]
