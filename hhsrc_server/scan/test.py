import pymysql

#初始化数据库连接
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWD = "root"
DB_DATABASE = "hhsrc2"
conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWD, db=DB_DATABASE, charset='utf8')
cursor = conn.cursor()

#查询该目标的主域
sql = "SELECT * FROM hhsrc_http"
cursor.execute(sql)
domain_query = cursor.fetchall()
print(len(domain_query))
print(domain_query[1:2])