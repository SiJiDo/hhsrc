from app.models import blacklist


def black_list_query(target_id, domain, ip):
    #获取黑名单
    blacklist_query = blacklist.query.filter(blacklist.black_target == target_id).all()
    blacklist_list = []
    for i in blacklist_query:
        temp = ""
        if 'domain:' in i.black_name:
            temp = i.black_name.split("domain:")[1]
        if 'ip:' in i.black_name:
            temp = i.black_name.split("ip:")[1]
        if(temp != ""):
            blacklist_list.append(temp)
    for b in blacklist_list:
        if(domain):
            if(b in domain):
                return True
        if(ip):
            if(b in ip):
                return True
    return False

def black_list_query_pro(target_id, domain, ip, cursor, conn):
    #获取黑名单
    sql = "SELECT * FROM hhsrc_blacklist WHERE black_target=%s"
    cursor.execute(sql,(target_id))
    blacklist_query = cursor.fetchall()
    blacklist_list = []
    for i in blacklist_query:
        temp = ""
        if 'domain:' in i[1]:
            temp = i[1].split("domain:")[1]
        if 'ip:' in i[1]:
            temp = i[1].split("ip:")[1]
        if(temp != ""):
            blacklist_list.append(temp)
    for b in blacklist_list:
        if(domain):
            if(b in domain):
                return True
        if(ip):
            if(b in ip):
                return True
    return False

def black_list_title_query(target_id, http_title, cursor, conn):
    #获取黑名单
    sql = "SELECT * FROM hhsrc_blacklist WHERE black_target=%s"
    cursor.execute(sql,(target_id))
    blacklist_query = cursor.fetchall()
    blacklist_list = []
    for i in blacklist_query:
        temp = ''
        if 'title:' in i[1]:
            temp = i[1].split("title:")[1]
        if(temp != ''):
            blacklist_list.append(temp)
    for b in blacklist_list:
        if(http_title):
            if(b in http_title):
                print(http_title + "被过滤啦!过滤规则:" + b)
                return True
    return False