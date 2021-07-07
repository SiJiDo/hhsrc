from celery.result import AsyncResult
from celery import Celery
from scan.conn import dbconn
import time 
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def run(target_id, scanmethod_query):
    #初始化数据库连接
    conn,cursor = dbconn()
    task = Celery(broker=cfg.get("CELERY_CONFIG", "CELERY_BROKER_URL"), backend=cfg.get("CELERY_CONFIG", "CELERY_RESULT_BACKEND"))
    task.conf.update(
        CELERY_TASK_SERIALIZER = 'json',
        CELERY_RESULT_SERIALIZER = 'json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE = 'Asia/Shanghai',
        CELERY_ENABLE_UTC = False,
    )

    #查询该目标的未扫描的域名
    sql = "SELECT * from hhsrc_http WHERE http_target=%s AND http_dirb_status=%s"
    cursor.execute(sql,(target_id, False))
    http_query = cursor.fetchall()

    #jsfinder
    for target in http_query:
        url = target[1] + '://' + target[2]
        jsfinder_scan = task.send_task('jsfinder.run', args=(url,), queue='jsfinder')
        scan_queue = []
        scan_queue.append(AsyncResult(jsfinder_scan.id))

        while True:
            for d in scan_queue:
                if d.successful():
                    try:
                        save_jsfinder_result(target, target_id, d.result['result'], cursor, conn)
                    except Exception as e:
                        print(e)
                    scan_queue.remove(d)
            if not scan_queue:
                break

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

#获取jsfinder信息
def save_jsfinder_result(target, target_id, jsfinder_result, cursor, conn): 
    for result in jsfinder_result:
        #过滤掉302
        if(result['status-code'] == '302' or result['status-code'] == '301'):
            continue
        #去掉根目录
        if(result['path'] == '' or result['path'] == '/'):
            continue
        #去重相同页面
        sql = "SELECT * from hhsrc_dirb WHERE dir_base like %s AND dir_length=%s"
        if(cursor.execute(sql,('%' + result['host'] + '%',result['content-length'])) >= 1):
            continue

        #入库
        print("jsfinder入库:" + result['host'] + result['path'])
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

#获取fileleak信息
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
