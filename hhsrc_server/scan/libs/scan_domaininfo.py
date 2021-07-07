from celery.result import AsyncResult
from celery import Celery
from scan.conn import dbconn
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

#获取domaininfo信息
def domaininfo(domain_target):
    conn,cursor = dbconn()
    task = Celery(broker=cfg.get("CELERY_CONFIG", "CELERY_BROKER_URL"), backend=cfg.get("CELERY_CONFIG", "CELERY_RESULT_BACKEND"))
    task.conf.update(
        CELERY_TASK_SERIALIZER = 'json',
        CELERY_RESULT_SERIALIZER = 'json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE = 'Asia/Shanghai',
        CELERY_ENABLE_UTC = False,
    )

    #发送celery,进行3次容错判断
    flag = False
    count = 0
    while(flag == False and count < 3):
        domaininfo_scan = task.send_task('domaininfo.run', args=(domain_target,), queue='domaininfo')
        scan_queue = []
        scan_queue.append(AsyncResult(domaininfo_scan.id))
        temp = ""
        while True:
            for info in scan_queue:
                if info.successful():
                    try:
                        domaininfo_result = info.result
                        #返回数据
                        temp = domaininfo_result['result']
                        if(temp):
                            count = 3
                            flag = True
                        else:
                            count = count + 1
                            flag = False
                    except Exception as e:
                        print(e)
                    scan_queue.remove(info)
            if not scan_queue:
                break
    return temp