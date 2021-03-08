from celery.result import AsyncResult
from celery import Celery
from flask import Flask
from app.models import domain,blacklist,subdomain
from scan.libs import scan_domaininfo
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

    #查询该目标的主域
    sql = "SELECT * FROM hhsrc_domain where domain_target = %s and domain_subdomain_status = False"
    cursor.execute(sql,(target_id))
    domain_query = cursor.fetchall()
    #开始扫描
    for domain_info in domain_query:
        
        #发送celery,进行3次容错判断
        flag = False
        count = 0
        all_result = []
        while(flag == False and count < 3):
            al_result = []
            #subfinder扫描
            subfinder_scan = task.send_task('subfinder.run', args=(domain_info[1],), queue='subfinder')
            scan_queue = []
            scan_queue.append(AsyncResult(subfinder_scan.id))
            #获取结果
            while True:
                for sub in scan_queue:
                    if sub.successful():
                        subdomain_result = sub.result
                        al_result += subdomain_result['result']
                        if(al_result):
                            count = 3
                            flag = True
                        else:
                            count = count + 1
                            flag = False
                        scan_queue.remove(sub)
                if not scan_queue:
                    break
            all_result = al_result

        #massdns扫描
        pass

        #先去重子域名结果
        all_result = list(set(all_result))
        #调用domaininfo 存储数据
        domaininfo_result = scan_domaininfo.domaininfo(all_result)
        for i in domaininfo_result:
            #过滤掉解析不出来的域名
            if(not i or '\\' in i['domain']):
                continue
            i['domain'] = i['domain'].strip()
            if(not i['domain']):
                continue
            #黑名单过滤
            if(utils.black_list_query_pro(target_id, i['domain'], ','.join(i['ips']),cursor,conn)):
                continue
            #ip个数大于5就pass
            if(subdomain.query.filter(subdomain.subdomain_ip == ','.join(i['ips'])).count() > 5):
                continue
            #入库
            print("开始入库:" + i['domain'])
            i['domain'].replace("'","\'")
  
            sql = "REPLACE INTO hhsrc_subdomain (subdomain_name,subdomain_ip,subdomain_info,subdomain_port_status, subdomain_http_status, subdomain_time, subdomain_target) VALUES('{}', '{}', '{}', {}, {}, '{}', '{}')".format(
                i['domain'],
                ','.join(i['ips'][:3]),
                i['type'],
                False,
                False,
                time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                target_id,
            )
            result = cursor.execute(sql)
            conn.commit()

        #标记该主域已扫描
        sql='update hhsrc_domain set domain_subdomain_status = %s where domain_target=%s'
        result = cursor.execute(sql,(True,target_id)) 
        conn.commit()

    cursor.close()
    conn.close()
    return