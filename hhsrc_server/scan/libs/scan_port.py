from celery.result import AsyncResult
from celery import Celery
from flask import Flask
from app.models import domain,port,subdomain
import time 
from app import DB
import configparser
import pymysql

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def run(target_id, scanmethod_query):
    #初始化数据库连接
    DB_HOST = cfg.get("DATABASE", "DB_HOST")
    DB_USER = cfg.get("DATABASE", "DB_USER")
    DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
    DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
    cursor = conn.cursor()

    task = Celery(app.name, broker=cfg.get("CELERY_CONFIG", "CELERY_BROKER_URL"), backend=cfg.get("CELERY_CONFIG", "CELERY_RESULT_BACKEND"))
    task.conf.update(app.config)

    #查询该目标的未扫描的域名
    sql = "SELECT * FROM hhsrc_subdomain where subdomain_target=%s and subdomain_port_status=False"
    cursor.execute(sql,(target_id))
    subdomain_query = cursor.fetchall()

    #开始扫描
    for subdomain_info in subdomain_query:
        #排除多个ip解析情况，该情况大概率是cdn
        if(',' in subdomain_info[2] or '' == subdomain_info[2]):
            #表示域名扫描
            sql='update hhsrc_subdomain set subdomain_port_status = %s where id=%s'
            cursor.execute(sql, (True, subdomain_info[0]))
            conn.commit()
            continue
        #发送celery,进行3次容错判断
        flag = False
        count = 0
        while(flag == False and count < 3):
            #naabu + nmap
            naabu_scan = task.send_task('naabu.run', args=(subdomain_info[2], scanmethod_query[4]), queue='naabu')
            scan_queue = []
            scan_queue.append(AsyncResult(naabu_scan.id))
            while True:
                for p in scan_queue:
                    if p.successful():
                        try:
                            temp = p.result['result']
                            if(temp):
                                count = 3
                                flag = True
                                save_result(subdomain_info, target_id, p.result['result'],cursor,conn)
                            else:
                                count = count + 1
                                flag = False
                        except Exception as e:
                            print(e)
                        scan_queue.remove(p)
                if not scan_queue:
                    break
    cursor.close()
    conn.close()
    return

def save_result(subdomain_info, target_id, port_result,cursor, conn):  
    print("--------------------存储端口数据处-------------------------")
    print(port_result)
    for result in port_result:
        #去重,port比较特殊需要2个字段才能判断是否重复，因此需要进行查询
        sql = "SELECT * from hhsrc_port WHERE port_ip =%s and port_port = %s"
        port_count = cursor.execute(sql,(result['ip'],str(result['port'])))
        if(port_count > 0):
            continue 
        #存储数据
        sql = "SELECT subdomain_name from hhsrc_subdomain WHERE id=%s"
        cursor.execute(sql,(subdomain_info[0]))
        host = cursor.fetchone()[0]
        print("开始端口入库:" + host + ":" + str(result['port']))
        #入库
        sql = "REPLACE INTO hhsrc_port (port_domain,port_ip,port_port,port_server, port_http_status, port_time, port_target) VALUES('{}', '{}', '{}', '{}', {}, '{}', '{}');".format(
            host,
            result['ip'],
            str(result['port']),
            result['server'],
            False,
            time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
            target_id,
        )
        cursor.execute(sql)
        conn.commit()
    #标记该子域名端口扫描结束
    sql='UPDATE hhsrc_subdomain SET subdomain_port_status=%s WHERE id=%s'
    result = cursor.execute(sql,(True,subdomain_info[0])) 
    conn.commit()
    return