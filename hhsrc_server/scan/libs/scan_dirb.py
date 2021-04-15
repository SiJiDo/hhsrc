from celery.result import AsyncResult
from celery import Celery
from flask import Flask
from app.models import dirb, http
from scan import utils
from app import DB
import time 
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
    sql = "SELECT * from hhsrc_http WHERE http_target=%s AND http_dirb_status=%s"
    cursor.execute(sql,(target_id, False))
    http_query = cursor.fetchall()

    #fileleak
    for target in http_query:
        url = target[1] + '://' + target[2]
        dirb_scan = task.send_task('fileleak.run', args=(url,scanmethod_query[7]), queue='fileleak')
        scan_queue = []
        scan_queue.append(AsyncResult(dirb_scan.id))

        while True:
            for d in scan_queue:
                if d.successful():
                    try:
                        save_result(target, target_id, d.result['result'], cursor, conn)
                    except Exception as e:
                        print(e)
                    scan_queue.remove(d)
            if not scan_queue:
                break
    cursor.close()
    conn.close()

#子域名的http扫描
def save_result(target, target_id, dirb_result, cursor, conn): 
    for result in dirb_result:
        #过滤掉302
        if(result['status-code'] == '302' or result['status-code'] == '301'):
            continue
        #入库
        print("dirb入库:" + result['host'] + result['path'])
        try:
            sql = "REPLACE INTO hhsrc_dirb (dir_base,dir_path,dir_length,dir_status, dir_title, dir_http, dir_time, dir_target) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                result['host'] + result['path'],
                result['path'],
                result['content-length'],
                result['status-code'],
                result['title'],
                target[0],
                time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                target_id,
            )
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)        

    #标记已扫描
    try:
        sql = "UPDATE hhsrc_http SET http_dirb_status=%s WHERE id=%s"
        cursor.execute(sql,(True,target[0]))
        conn.commit()
    except Exception as e:
        print(e)
    return
