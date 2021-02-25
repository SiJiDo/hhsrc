from apscheduler.schedulers.background import BackgroundScheduler
from app.models import scancorn, Target, domain, subdomain, port, http, cornjob
from scan import scan
from app.models import DB
import time
import pymysql
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def setcorn():
    DB_HOST = cfg.get("DATABASE", "DB_HOST")
    DB_USER = cfg.get("DATABASE", "DB_USER")
    DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
    DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
    # 2.创建游标
    cursor = conn.cursor()

    #初始化扫描任务
    scheduler = BackgroundScheduler()

    print("删除之前的计划任务，重新生成新的计划任务列表")
    #删除计划任务列表，保证之前的子进程退出
    sql = "DELETE FROM hhsrc_cornjob"
    cursor.execute(sql)
    conn.commit()
    time.sleep(300)

    sql = "SELECT * FROM hhsrc_scancorn"
    cursor.execute(sql)
    scancorn_query = cursor.fetchall()
    for corn in scancorn_query:
        #查询绑定了的target
        sql = "SELECT * from hhsrc_target Where target_corn_id = {} and target_corn=True".format(corn[0])
        cursor.execute(sql)
        target_query = cursor.fetchall()
        for c in target_query:
            #绑定计划任务
            if(corn[3] == '*'):
                scheduler.add_job(rest_status, 'cron', args=[c[0],], month=corn[2], day=corn[4], day_of_week=corn[3] ,hour=corn[5], minute=corn[6])
            else:
                scheduler.add_job(rest_status, 'cron', args=[c[0],], month=corn[2], day=corn[4], day_of_week=int(corn[3])-1 ,hour=corn[5], minute=corn[6])
        for job in scheduler.get_jobs():
            sql='insert into hhsrc_cornjob(cornjob_name, cornjob_time) values(%s,%s)'
            result = cursor.execute(sql,(str(job), time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))))
            conn.commit()

    scheduler.start()
    print("--------------计划任务---------------")
    while(scheduler.get_jobs()):
        sql = "SELECT * from hhsrc_cornjob";
        result = cursor.execute(sql)
        if(result == 0):
            break
        time.sleep(60)
    print("-------------计划任务结束--------------")
    cursor.close()
    conn.close()
    exit()
    
    '''
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of the (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    second (int|str) – second (0-59)

    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

    *    any    Fire on every value
    */a    any    Fire every a values, starting from the minimum
    a-b    any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    xth y    day    Fire on the x -th occurrence of weekday y within the month
    last x    day    Fire on the last occurrence of weekday x within the month
    last    day    Fire on the last day within the month
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
    '''

def rest_status(target_id):
    print(target_id)
    print("开始计划任务")
    target_model = Target()
    r = target_model.update(target_status = 0).where(Target.id == target_id).execute()
    domain_model = domain()
    r = domain_model.update(domain_subdomain_status = False).where(domain.domain_target == target_id).execute()
    subdomain_model = subdomain()
    r = subdomain_model.update(subdomain_port_status = False).where(subdomain.subdomain_target == target_id).execute()
    r = subdomain_model.update(subdomain_http_status = False).where(subdomain.subdomain_target == target_id).execute()
    port_model = port()
    r = port_model.update(port_http_status = False).where(port.port_target == target_id).execute()
    http_model = http()
    r =  http_model.update(http_dirb_status = False).where(http.http_target == target_id).execute()
    r = http_model.update(http_api_status = False).where(http.http_target == target_id).execute()
    r = http_model.update(http_webinfo_status = False).where(http.http_target == target_id).execute()
    scan.run(target_id)

if __name__ == '__main__':
    setcorn()