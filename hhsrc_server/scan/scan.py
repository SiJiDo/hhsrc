from flask import Flask
from celery import Celery
from scan.libs import scan_subdomain, scan_domaininfo, scan_port, scan_url, scan_dirb, scan_vuln
from app.models import Target,scanmethod,blacklist,subdomain,port, commonconfig
from scan import utils
from scan import corn
import time
import configparser
from multiprocessing import Process
from app import DB
from sqlalchemy import create_engine
import pymysql

cfg = configparser.ConfigParser()
cfg.read('config.ini')

# 通用子域名扫描
def run(target_id = '0'):
    #初始化数据库连接
    DB_HOST = cfg.get("DATABASE", "DB_HOST")
    DB_USER = cfg.get("DATABASE", "DB_USER")
    DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
    DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
    cursor = conn.cursor()

    sql = "SELECT * FROM hhsrc_commonconfig"
    cursor.execute(sql)
    max_count = cursor.fetchone()[2]
    sql = "SELECT * FROM hhsrc_target where target_status = 1"
    scan_count = cursor.execute(sql)
    #并发扫描目标个数应小于设置的格式
    if(scan_count >= max_count):
        return
    
    #开始扫描
    sql = "SELECT * FROM hhsrc_target where target_status = 0"
    wait_scan_query = cursor.execute(sql)
    while(wait_scan_query > 0):
        sql = "SELECT * FROM hhsrc_target where target_status = 0 order by target_level desc"
        cursor.execute(sql)
        target_query = cursor.fetchone()

        sql='UPDATE hhsrc_target SET target_status=%s WHERE id=%s'
        cursor.execute(sql,(1,target_query[0]))
        conn.commit()
        
        sql = "SELECT * FROM hhsrc_scanmethod where id = %s"
        cursor.execute(sql,(target_query[3]))
        scanmethod_query = cursor.fetchone()
        print(scanmethod_query)
        print(target_query)
        #扫描模式配置扫描子域
        print("subdomain开过" + str(scanmethod_query[2]))
        if(scanmethod_query[2]):
            scan_subdomain.run(target_query[0])
        #扫描端口信息
        print("port开关:" + str(scanmethod_query[3]))
        if(scanmethod_query[3]):
            scan_port.run(target_query[0], scanmethod_query)
        # #扫描http信息
        print("http开关:" + str(scanmethod_query[5]))
        if(scanmethod_query[5]):
            scan_url.run(target_query[0])
        # #扫描敏感目录
        print("dirb开关:" + str(scanmethod_query[6]))
        if(scanmethod_query[6]):
            scan_dirb.run(target_query[0], scanmethod_query)
        # #扫描漏洞
        print("vuln开关:" + str(scanmethod_query[8]))
        if(scanmethod_query[8]):
            scan_vuln.run(target_query[0])
        # 扫描结束
        print(str(target_query[1]) + "扫描结束")

        sql='update hhsrc_target set target_status = %s where id=%s'
        cursor.execute(sql,(2,target_query[0]))
        conn.commit()

        sql = "SELECT * FROM hhsrc_target where target_status = 0"
        wait_scan_query = cursor.execute(sql)
    cursor.close()
    conn.close()
    return

# 添加精准资产时的动作
def run_subdomain(target_id, subdomain_list):
    #先去重子域名结果
    all_result = list(set(subdomain_list))
    domaininfo_result = []
    #调用domaininfo 存储数据
    domaininfo_result = scan_domaininfo.domaininfo(all_result)
    for i in domaininfo_result:
        #过滤掉解析不出来的域名
        if(not i or '\\' in i['domain']):
            continue
        #过滤掉空白书记
        i['domain'] = i['domain'].strip()
        if(not i['domain']):
            continue
        #黑名单过滤
        if(utils.black_list_query(target_id, i['domain'], ','.join(i['ips']))):
            continue
        #ip个数大于5就pass
        if(subdomain.query.filter(subdomain.subdomain_ip == ','.join(i['ips'])).count() > 5):
            continue
        #入库
        i['domain'].replace("'","\'")
        try:
            sql = "REPLACE INTO hhsrc_subdomain (subdomain_name,subdomain_ip,subdomain_info,subdomain_port_status, subdomain_http_status, subdomain_time, subdomain_target) VALUES('{}', '{}', '{}', {}, {}, '{}', '{}');".format(
                i['domain'],
                ','.join(i['ips'][:3]),
                i['type'],
                False,
                False,
                time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                target_id,
            )
            DB.session.execute(sql)
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()
    return

if __name__ == '__main__':
    scan()