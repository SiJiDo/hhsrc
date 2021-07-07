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

    print("删除之前的计划任务")
    #删除计划任务列表，保证之前的子进程退出
    sql = "DELETE FROM hhsrc_cornjob"
    cursor.execute(sql)
    conn.commit()
    time.sleep(60)

    print("重新生成新的计划任务列表")
    sql = "SELECT * FROM hhsrc_scancorn"
    cursor.execute(sql)
    scancorn_query = cursor.fetchall()
    for corn in scancorn_query:
        #查询绑定了的target
        sql = "SELECT * from hhsrc_target Where target_corn_id = {} and target_corn=True".format(corn[0])
        cursor.execute(sql)
        target_query = cursor.fetchall()
        for c in target_query:
            print(c)
            #绑定计划任务
            if(corn[3] == '*'):
                scheduler.add_job(rest_status, 'cron', args=[c[0],], month=corn[2], day=corn[4], day_of_week=corn[3] ,hour=corn[5], minute=corn[6])
            else:
                scheduler.add_job(rest_status, 'cron', args=[c[0],], month=corn[2], day=corn[4], day_of_week=int(corn[3])-1 ,hour=corn[5], minute=corn[6])
        for job in scheduler.get_jobs():
            sql='insert into hhsrc_cornjob(cornjob_name, cornjob_time) values(%s,%s)'
            result = cursor.execute(sql,(str(job), time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))))
            conn.commit()

    cursor.close()
    conn.close()

    scheduler.start()
    print("--------------计划任务---------------")
    while(scheduler.get_jobs()):
        conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
        cursor = conn.cursor()

        sql = "SELECT * from hhsrc_cornjob";
        result = cursor.execute(sql)
        
        if(result == 0):
            break
        time.sleep(5)
        cursor.close()
        conn.close()
    print("-------------计划任务结束--------------")
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
    DB_HOST = cfg.get("DATABASE", "DB_HOST")
    DB_USER = cfg.get("DATABASE", "DB_USER")
    DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
    DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
    cursor = conn.cursor()
    print(target_id)
    print("开始计划任务")
    sql = "UPDATE hhsrc_target SET target_status=0 WHERE id=%s"
    cursor.execute(sql,(target_id))
    conn.commit()
    sql = "UPDATE hhsrc_domain SET domain_subdomain_status=False WHERE domain_target=%s"
    cursor.execute(sql,(target_id))
    conn.commit()
    sql = "UPDATE hhsrc_subdomain SET subdomain_port_status=False,subdomain_http_status=False WHERE subdomain_target=%s"
    cursor.execute(sql,(target_id))
    conn.commit()
    sql = "UPDATE hhsrc_port SET port_http_status=False WHERE port_target=%s"
    cursor.execute(sql,(target_id))
    conn.commit()
    sql = "UPDATE hhsrc_http SET http_dirb_status=False,http_vuln_status=False WHERE http_target=%s"
    cursor.execute(sql,(target_id))
    conn.commit()
    scan.run(target_id)
    cursor.close()
    conn.close()

if __name__ == '__main__':
    setcorn()