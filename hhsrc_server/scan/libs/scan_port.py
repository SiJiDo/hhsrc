from celery import Celery
import time 
import configparser
from scan.conn import dbconn
import queue
from threading import *

cfg = configparser.ConfigParser()
cfg.read('config.ini')

lock=Lock()

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
    sql = "SELECT * FROM hhsrc_subdomain where subdomain_target=%s and subdomain_port_status=False"
    cursor.execute(sql,(target_id))
    subdomain_query = cursor.fetchall()

    #初始化多线程
    thread_count = 10
    port_queue = queue.Queue()
    #开始扫描
    for subdomain_info in subdomain_query:
        #排除多个ip解析情况，该情况大概率是cdn
        if(',' in subdomain_info[2] or '' == subdomain_info[2]):
            #表示域名扫描
            sql='UPDATE hhsrc_subdomain SET subdomain_port_status = %s where id=%s'
            cursor.execute(sql, (True, subdomain_info[0]))
            sql='UPDATE hhsrc_subdomain SET subdomain_port_status=%s WHERE id=%s'
            cursor.execute(sql,(True,subdomain_info[0])) 
            conn.commit()
            continue
        port_queue.put(subdomain_info)

    # 使用多线程
    threads = []
    for i in range(0, thread_count):
        thread = portscan(port_queue, scanmethod_query[4],task, target_id, cursor, conn )
        thread.start()
        threads.append(thread)
    for j in threads:
        j.join()

    cursor.close()
    conn.close()
    
    return

#使用多线程
class portscan(Thread):
    def __init__(self, port_queue, config, task, target_id, cursor, conn):
        Thread.__init__(self)
        self.queue = port_queue
        self.config = config
        self.task = task
        self.target_id = target_id
        self.cursor = cursor
        self.conn = conn

    def run(self):
        queue = self.queue
        config = self.config
        task = self.task
        target_id = self.target_id
        cursor = self.cursor
        conn = self.conn

        while not queue.empty():
            try:
                subdomain_info = queue.get()
                target = subdomain_info[2]
                #发送celery
                #naabu + nmap
                naabu_scan = task.send_task('naabu.run', args=(target, config), queue='naabu')
                while True:
                    if naabu_scan.successful():
                        try:
                            lock.acquire()
                            save_result(subdomain_info, target_id, naabu_scan.result['result'],cursor,conn)
                            lock.release()
                            break
                        except Exception as e:
                            print(e)
                            break
            except:
                pass
                #print("[-]host unknow")

        return

def save_result(subdomain_info, target_id, port_result,cursor, conn):  
    print("--------------------存储端口数据处-------------------------")
    print(port_result)
    if(len(port_result) > 50):
        #标记该子域名端口扫描结束
        sql='UPDATE hhsrc_subdomain SET subdomain_port_status=%s WHERE id=%s'
        result = cursor.execute(sql,(True,subdomain_info[0])) 
        conn.commit()
        return 
        
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