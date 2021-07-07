# -*- coding: utf-8 -*-
from werkzeug.security import check_password_hash, generate_password_hash
from app import DB,login_manager
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import LONGTEXT
import os

# 管理员账号
class User(DB.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_user'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    username = DB.Column(DB.String(20), nullable=False, unique=True)  # 用户名
    password = DB.Column(DB.String(128), nullable=False)  # 密码

# 扫描引擎模式
class scanmethod(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_scanmethod'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    scanmethod_name = DB.Column(DB.String(128))   #扫描方式名
    scanmethod_subdomain = DB.Column(DB.Boolean, default=True) #是否扫描子域名
    scanmethod_port = DB.Column(DB.Boolean, default=True)  #是否扫描端口
    scanmethod_port_portlist = DB.Column(DB.String(128))  #扫描端口类型选择
    scanmethod_url = DB.Column(DB.Boolean, default=True) #是否扫描http
    scanmethod_dirb = DB.Column(DB.Boolean, default=False)   #是否扫描目录
    scanmethod_dirb_wordlist = DB.Column(DB.String(128))  #扫描字典选择
    scanmethod_vuln = DB.Column(DB.Boolean, default=False)    #是否扫描指纹
    scanmethod_time = DB.Column(DB.String(128))   #修改时间

# 定时引擎模式
class scancorn(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_scancorn'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    scancorn_name = DB.Column(DB.String(20))   #定时名
    scancorn_month = DB.Column(DB.String(20)) #定时月
    scancorn_week = DB.Column(DB.String(20))  #定时周
    scancorn_day = DB.Column(DB.String(20))  #定时天
    scancorn_hour = DB.Column(DB.String(20)) #定时小时
    scancorn_min = DB.Column(DB.String(20)) #定时分钟
    scancorn_time = DB.Column(DB.String(20))   #修改时间

# 记录计划任务
class cornjob(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_cornjob'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    cornjob_name = DB.Column(DB.String(128))  #计划任务名字
    cornjob_time = DB.Column(DB.String(128))  #计划任务时间

# 通用配置
class commonconfig(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_commonconfig'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    config_server = DB.Column(DB.String(128)) # server酱通知
    config_count = DB.Column(DB.Integer,default=1) # 最多几个任务同时扫描

# 目标信息
class Target(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_target'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    target_name = DB.Column(DB.String(128))   #扫描目标名
    target_description = DB.Column(DB.String(128))    #扫描目标描述
    target_method = DB.Column(DB.String(128))  #扫描方式的引擎
    target_level = DB.Column(DB.Integer)   #扫描优先度
    target_corn = DB.Column(DB.Boolean, default=False)   #是否周期扫描
    target_corn_id = DB.Column(DB.String(128))    #周期扫描的引擎
    target_status = DB.Column(DB.Integer, default=0)   #扫描0表示未扫描，1表示扫描中，2表示扫完完成
    target_time = DB.Column(DB.String(128))   #修改时间

# 域名信息管理
class domain(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_domain'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    domain_name = DB.Column(DB.String(128), unique=True)   #扫描域名名
    domain_subdomain_status = DB.Column(DB.Boolean, default=False)   #子域扫描状态
    domain_time = DB.Column(DB.String(128))   #修改时间
    domain_target = DB.Column(DB.Integer) #隶属于的目标

# 黑名单息管理
class blacklist(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_blacklist'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    black_name = DB.Column(DB.String(128), unique=True)   #黑名单内容，以domain,ip,title三类标志
    black_time = DB.Column(DB.String(128))   #修改时间
    black_target = DB.Column(DB.Integer) #隶属于的目标

# 子域名信息管理
class subdomain(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_subdomain'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    subdomain_name = DB.Column(DB.String(128), unique=True)   #子域名
    subdomain_ip = DB.Column(DB.String(128))   #子域ip
    subdomain_info = DB.Column(DB.String(128))   #子域解析信息
    subdomain_port_status = DB.Column(DB.Boolean, default=False)   #端口扫描状态
    subdomain_http_status = DB.Column(DB.Boolean, default=False)   #http扫描状态
    subdomain_time = DB.Column(DB.String(128))   #修改时间
    subdomain_target = DB.Column(DB.Integer) #隶属于的目标

# ip信息管理
class port(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_port'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    port_domain = DB.Column(DB.String(128))   #ip对应域名
    port_ip = DB.Column(DB.String(128))   #ip域名
    port_port = DB.Column(DB.String(128))   #ip端口
    port_server = DB.Column(DB.String(128))   #ip服务
    port_http_status = DB.Column(DB.Boolean, default=False)   #http扫描状态
    port_time = DB.Column(DB.String(128))   #修改时间
    port_target = DB.Column(DB.Integer) #隶属于的目标

# http信息管理
class http(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_http'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    http_schema = DB.Column(DB.String(128)) #协议
    http_name = DB.Column(DB.String(128), unique=True)   # url信息
    http_title = DB.Column(DB.String(128))   #http 标题
    http_status = DB.Column(DB.String(128))   # http 响应码
    http_length = DB.Column(DB.String(128))   # http 响应长度
    http_screen = DB.Column(LONGTEXT)   # http 页面截图
    http_dirb_status = DB.Column(DB.Boolean, default=False) #是否扫描目录
    http_vuln_status = DB.Column(DB.Boolean, default=False) #是否扫描漏洞
    http_see = DB.Column(DB.Boolean, default=False) #是否已读
    http_time = DB.Column(DB.String(128))   #修改时间
    http_target = DB.Column(DB.Integer) #隶属于的目标

#漏洞扫描
class vuln(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_vuln'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    vuln_mainkey = DB.Column(DB.String(128), unique=True) #主键
    vuln_name = DB.Column(DB.String(128)) #漏洞名
    vuln_info = DB.Column(DB.String(128)) #漏洞信息
    vuln_level = DB.Column(DB.String(128)) #漏洞级别
    vuln_path = DB.Column(LONGTEXT) #漏洞路径
    vuln_http = DB.Column(DB.String(128)) #隶属于的http
    vuln_target = DB.Column(DB.Integer) #隶属于的目标
    vuln_time = DB.Column(DB.String(128)) # 修改时间

# 目录信息管理
class dirb(DB.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'hhsrc_dirb'
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True)
    dir_base = DB.Column(DB.String(128), unique=True)   # url路径
    dir_path = DB.Column(DB.String(128))   # 路径
    dir_status = DB.Column(DB.String(128))   # dirb 响应码
    dir_length = DB.Column(DB.String(128)) #dirb 响应长度
    dir_title = DB.Column(DB.String(128)) # dirb 目录名
    dir_time = DB.Column(DB.String(128))   #修改时间
    dir_http = DB.Column(DB.Integer) #隶属于的http
    dir_target = DB.Column(DB.Integer) #隶属于的目标


@login_manager.user_loader
def load_user(user_id):
    user = DB.session.query(User).get(user_id)
    return user

if __name__ == '__main__':
    # user = User(username = 'admin', password = 'pbkdf2:sha256:150000$c7P9YSFs$7adc2214bab28233a14211e915dd0ee90d2715a86970988a69b624cb8ef06c1f')
    # common = commonconfig(config_server = 'None', config_count = 1)
    # DB.session.add_all([user,common])   # 把对象添加到会话中.
    # DB.session.commit()
    DB.create_all()
    DB.session.commit()