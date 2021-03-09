from celery.result import AsyncResult
from celery import Celery
from flask import Flask
from app.models import http
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
    sql = "SELECT * FROM hhsrc_http WHERE http_target=%s AND http_vuln_status=%s"
    cursor.execute(sql,(target_id, False))
    http_query = cursor.fetchall()

    #nuclei
    for target in http_query:
        url = target[1] + '://' + target[2]
        vuln_scan = task.send_task('nuclei.run', args=(url,), queue='nuclei')
        scan_queue = []
        scan_queue.append(AsyncResult(vuln_scan.id))

        starttime = time.time()
        nowtime = starttime

        while True:
            for vuln in scan_queue:
                if vuln.successful():
                    try:
                        save_result(target, target_id, vuln.result['result'], cursor, conn)
                    except Exception as e:
                        print(e)
                    scan_queue.remove(vuln)
                if(nowtime > starttime + 120):
                    set_scan(target, cursor, conn)
                    task.control.revoke(vuln_scan.id, terminate=True)
                    print(target[2] + "目标超时")
                    scan_queue.remove(vuln)
                nowtime = time.time()
            if not scan_queue:
                break
    cursor.close()
    conn.close()

def save_result(target, target_id, vuln_result, cursor, conn): 
    for result in vuln_result:
        #入库
        print("vuln入库:" + result['vuln_info'])
        try:
            sql = "REPLACE INTO hhsrc_vuln (vuln_mainkey, vuln_name,vuln_info,vuln_level,vuln_path, vuln_http, vuln_target, vuln_time) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                result['vuln_path'] + result['vuln_info'],
                result['target'],
                result['vuln_info'],
                result['vuln_level'],
                result['vuln_path'],
                target[0],
                target_id,
                time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
            )
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)

    #标记已扫描
    try:
        sql = "UPDATE hhsrc_http SET http_vuln_status=%s WHERE id=%s"
        cursor.execute(sql,(True, target[0]))
        conn.commit()
    except Exception as e:
        print(e)
    return

def set_scan(target, cursor, conn):
    #标记已扫描
    try:
        sql = "UPDATE hhsrc_http SET http_vuln_status=%s WHERE id=%s"
        cursor.execute(sql,(True, target[0]))
        conn.commit()
    except Exception as e:
        print(e)
    return