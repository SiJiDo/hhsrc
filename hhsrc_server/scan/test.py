from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

scheduler.add_job(rest_status, 'cron', args=[c[0],], month=corn[2], day=corn[4], day_of_week=int(corn[3])-1 ,hour=corn[5], minute=corn[6])

rest_status