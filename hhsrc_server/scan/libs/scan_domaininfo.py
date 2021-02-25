from celery.result import AsyncResult
from celery import Celery
from flask import Flask
import time 
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

#获取domaininfo信息
def domaininfo(domain_target):
    #不知道为什么在scan中调用会出错，这里直接把celery加进来防止出错
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = cfg.get("CELERY_CONFIG", "CELERY_BROKER_URL")
    app.config['CELERY_RESULT_BACKEND'] = cfg.get("CELERY_CONFIG", "CELERY_RESULT_BACKEND")
    task = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    task.conf.update(app.config)

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