import pymysql

#初始化数据库连接
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWD = ""
DB_DATABASE = "hhsrc2"
conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
cursor = conn.cursor()

#查询该目标的主域
sql = "SELECT * FROM hhsrc_domain where domain_target = %s and domain_subdomain_status = False"
cursor.execute(sql,(61))
domain_query = cursor.fetchall()
print(domain_query)