from celery.result import AsyncResult
from celery import Celery
from flask import Flask
from app.models import domain, port, subdomain, http
from scan import utils
from app import DB
import time 
import configparser
import pymysql

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def run(target_id):
    #初始化数据库连接
    DB_HOST = cfg.get("DATABASE", "DB_HOST")
    DB_USER = cfg.get("DATABASE", "DB_USER")
    DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
    DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
    cursor = conn.cursor()

    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = cfg.get("CELERY_CONFIG", "CELERY_BROKER_URL")
    app.config['CELERY_RESULT_BACKEND'] = cfg.get("CELERY_CONFIG", "CELERY_RESULT_BACKEND")

    task = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    task.conf.update(app.config)

    #查询该目标的未扫描的域名
    sql = "SELECT * FROM hhsrc_subdomain WHERE subdomain_target=%s AND subdomain_http_status=%s"
    cursor.execute(sql,(target_id,False))
    subdomain_query = cursor.fetchall()
    sql = "SELECT * FROM hhsrc_port WHERE port_target=%s AND port_http_status=%s"
    cursor.execute(sql,(target_id,False))
    port_query = cursor.fetchall()

    subdomain_list = []
    #根据子域名来获取http信息
    for subdomain_info in subdomain_query:
        subdomain_list.append(subdomain_info[1])
    flag = False
    count = 0
    #httpx，进行3次容错判断
    while(flag == False and count < 3 and subdomain_list):
        httpx_scan = task.send_task('httpx.run', args=(subdomain_list,), queue='httpx')
        scan_queue = []
        scan_queue.append(AsyncResult(httpx_scan.id))

        while True:
            for h in scan_queue:
                if h.successful():
                    try:
                        if(h.result['result']):
                            save_result(subdomain_query, target_id, h.result['result'], cursor, conn)
                            flag = True
                            count = 3
                        else:
                            flag = False
                            count = count + 1
                    except Exception as e:
                        print(e)
                    scan_queue.remove(h)
            if not scan_queue:
                break

    port_list = []
    #根据ip获取http信息，排除80,443端口
    for port_info in port_query:
        if(port_info[3] == '443' or port_info[3] == '80'):
            continue
        port_list.append(port_info[1] + ':' + port_info[3])
    
    flag = False
    count = 0
    #httpx，进行3次容错判断
    while(flag == False and count < 3 and subdomain_list):
        httpx_scan = task.send_task('httpx.run', args=(port_list,), queue='httpx')
        scan_queue = []
        scan_queue.append(AsyncResult(httpx_scan.id))

        while True:
            for h in scan_queue:
                if h.successful():
                    try:
                        if(h.result['result']):
                            save_result_port(port_query, target_id, h.result['result'], cursor, conn)
                            flag = True
                            count = 3
                        else:
                            flag = False
                            count = count + 1
                    except Exception as e:
                        print(e)
                    scan_queue.remove(h)
            if not scan_queue:
                break

    #截图
    sql = "SELECT * FROM hhsrc_http WHERE http_target=%s AND http_screen=%s AND http_status!=%s AND http_status!=%s"
    cursor.execute(sql,(target_id,'None','302','301'))
    http_query = cursor.fetchall()

    http_list = []
    for http_info in http_query:
        http_list.append(http_info[1] + "://" + http_info[2])
        
    screenshot_scan = task.send_task('screenshot.run', args=(http_list,), queue='screenshot')
    scan_queue = []
    scan_queue.append(AsyncResult(screenshot_scan.id))

    while True:
        for h in scan_queue:
            if h.successful():
                try:
                    save_result_screenshot(h.result['result'], cursor, conn)
                except Exception as e:
                    print(e)
                scan_queue.remove(h)
        if not scan_queue:
            break

    cursor.close()
    conn.close()
    return

#子域名的http扫描
def save_result(subdomain_query, target_id, http_result, cursor, conn): 
    for result in http_result:
        #title黑名单过滤
        if(utils.black_list_title_query(target_id, result['title'], cursor, conn)):
            continue
        #入库
        print("开始subdomain的http入库:" + result['url'])
        sql = "REPLACE INTO hhsrc_http (http_schema,http_name,http_title,http_status, http_length, http_screen, http_time, http_target, http_dirb_status, http_vuln_status ) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {});".format(
            result['url'].split("://")[0],
            result['url'].split("://")[1],
            result['title'],
            result['status-code'],
            result['content-length'],
            "None",
            time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
            target_id,
            False,
            False,
        )
        cursor.execute(sql)
        conn.commit()
    #标记该子域已扫描 
    for subdomain_info in subdomain_query:
        sql='UPDATE hhsrc_subdomain SET subdomain_http_status=%s WHERE id=%s'
        result = cursor.execute(sql,(True,subdomain_info[0])) 
        conn.commit()
    return

#端口的http扫描
def save_result_port(port_query, target_id, http_result, cursor, conn):  
    for result in http_result:
        #title黑名单过滤
        if(utils.black_list_title_query(target_id, result['title'], cursor, conn)):
            continue
        #入库
        print("开始port的http入库:" + result['url'])
        sql = "REPLACE INTO hhsrc_http (http_schema,http_name,http_title,http_status, http_length, http_screen, http_time, http_target) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
            result['url'].split("://")[0],
            result['url'].split("://")[1],
            result['title'],
            result['status-code'],
            result['content-length'],
            "None",
            time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
            target_id,
        )
        cursor.execute(sql)
        conn.commit()  

    #标记该端口已扫描 
    for port_info in port_query:
        sql='UPDATE hhsrc_port SET port_http_status=%s WHERE id=%s'
    result = cursor.execute(sql,(True,port_info[0])) 
    conn.commit()
    return

#截图
def save_result_screenshot(http_result, cursor, conn):  
    i = 0
    while(i <= len(http_result)):
        if(len(http_result > 100)):
            for result in http_result[i: i + 100]:
                print("开始存储截图:" + result['http'])
                try:
                    sql='UPDATE hhsrc_http SET http_screen=%s WHERE http_name=%s'
                    result = cursor.execute(sql,(result['screen_base64'],result['http'].split("://")[1])) 
                    conn.commit()
                except Exception as e:
                    print(e) 
                i = i + 100
        else:
            for result in http_result[i:len(http_result)]:
                print("开始存储截图:" + result['http'])
                try:
                    sql='UPDATE hhsrc_http SET http_screen=%s WHERE http_name=%s'
                    result = cursor.execute(sql,(result['screen_base64'],result['http'].split("://")[1])) 
                    conn.commit()
                except Exception as e:
                    print(e)
    return