import IPy
import time
from app import DB
from app.models import domain, port, subdomain, http, dirb, vuln, blacklist
from scan import scan
from multiprocessing import Process
import xlwt

#获取带-的ip列表
def getip1(ip):
    last = ""
    test = ip.split('.')
    zone = []
    result = []
    count = 0
    for i in test:
        if("-" not in i):
            last = last + i + '.'
        if("-" in i):
            last = last + 'temp' + str(count) + '.'
            zone.append(int(i.split("-")[0]))
            zone.append(int(i.split("-")[1]))
            count = count + 1

    last = last[:-1]

    if len(zone) == 2: 
        for i in range(zone[0], zone[1] + 1):
            result.append(last.replace("temp0", str(i)))

    if len(zone) == 4:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                temp = last.replace("temp0", str(i))
                temp = temp.replace("temp1", str(j))
                result.append(temp)

    if len(zone) == 6:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                for k in range(zone[4], zone[5] + 1):
                    temp = last.replace("temp0", str(i))
                    temp = temp.replace("temp1", str(j))
                    temp = temp.replace("temp2", str(k))
                    result.append(temp)

    if len(zone) == 8:
        for i in range(zone[0], zone[1] + 1):
            for j in range(zone[2], zone[3] + 1):
                for k in range(zone[4], zone[5] + 1):
                    for v in range(zone[6], zone[7] + 1):
                        temp = last.replace("temp0", str(i))
                        temp = temp.replace("temp1", str(j))
                        temp = temp.replace("temp2", str(k))
                        temp = temp.replace("temp3", str(v))
                        result.append(temp)
    return result

#获取/24带子网掩码的ip
def getip2(ips):
    ip = IPy.IP(ips)
    return list(ip)

#保存域名
def save_domain(target_id, form):
    domain_list = form.domain_name.data.split('\r\n')
    for i in domain_list:
        #不重复的情况下存入主域数据
        if(i):
            try:
                if(domain.query.filter(domain.domain_name == i).count() > 0):
                    continue
                i = i.replace("'","\'")
                sql = "REPLACE INTO hhsrc_domain (domain_name,domain_subdomain_status,domain_time,domain_target) VALUES('{}', {}, '{}', '{}');".format(
                    i,
                    False,
                    time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                    target_id,
                )
                DB.session.execute(sql)
                DB.session.commit()
            except Exception as e:
                print(e)
                DB.session.rollback()
    return True

#保存精准域名
def save_subdomain(target_id, form):
    subdomain_list = form.subdomain_name.data.split('\r\n')
    if((subdomain_list[0] != '')):
        p=Process(target=scan.run_subdomain,args=(target_id, subdomain_list))
        p.start()
    return True

#保存精准ip
def save_ip(target_id, form):
    subdomain_list = form.subdomain_ip.data.split('\r\n')
    subdomain_last_list = []
    for i in subdomain_list:
        if("-" in i):
            try:
                subdomain_last_list += getip1(i)
            except Exception as e:
                print(e)
        elif("/" in i):
            try:
                subdomain_last_list = subdomain_last_list + getip2(i)
            except Exception as e:
                print(e)
        else:
            subdomain_last_list.append(i)
    for i in subdomain_last_list:
        i = str(i).strip()
        if(not i):
            continue
        #黑名单过滤
        if(black_list_query(target_id, '', i)):
            continue
        i = i.replace("'","\'")
        try:
            sql = "REPLACE INTO hhsrc_subdomain (subdomain_name,subdomain_ip,subdomain_info,subdomain_port_status, subdomain_http_status, subdomain_time, subdomain_target) VALUES('{}', '{}', '{}', {}, {}, '{}', '{}');".format(
                i,
                i,
                'None',
                False,
                False,
                time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                target_id,
            )
            DB.session.execute(sql)
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()
    return True

#保存黑名单
def save_blacklist(target_id, form):
    blacklist_list = form.black_name.data.split('\r\n')
    for i in blacklist_list:
        #剔除数据库中已存在黑名单的数据
        blacklist_remove(i, target_id)
        if(i and ('title:' in i or 'domain:' in i or 'ip:' in i)):
            try:
                i = i.replace("'","\'")
                sql = "REPLACE INTO hhsrc_blacklist (black_name,black_time,black_target) VALUES('{}', '{}', '{}');".format(
                    i,
                    time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), 
                    target_id,
                )
                DB.session.execute(sql)
                DB.session.commit()
            except Exception as e:
                print(e)
                DB.session.rollback()
    return True

#删除属于添加黑名单的信息(有待完善)
def blacklist_remove(black, target_id):
    if("domain:" in black):
        b = black.split("domain:")[1]
        try:
            result = subdomain.query.filter(subdomain.subdomain_name.like("%{}%".format(b)), subdomain.subdomain_target == target_id).all()
            [DB.session.delete(r) for r in result]
            result = port.query.filter(port.port_domain.like("%{}%".format(b)), port.port_target == target_id).all()
            [DB.session.delete(r) for r in result]
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()
    if("ip:" in black):
        b = black.split("ip:")[1]
        try:
            result = subdomain.query.filter(subdomain.subdomain_ip.like("%{}%".format(b)), subdomain.subdomain_target == target_id).all()
            [DB.session.delete(r) for r in result]
            result = port.query.filter(port.port_ip.like("%{}%".format(b)), port.port_target == target_id).all()
            [DB.session.delete(r) for r in result]
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()
    if("title:" in black):
        b = black.split("title:")[1]
        try:
            result = http.query.filter(http.http_title.like("%{}%".format(b)), http.http_target == target_id).all()
            [DB.session.delete(r) for r in result]
            DB.session.commit()
        except Exception as e:
            print(e)
            DB.session.rollback()

#过滤
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

#导出Excel
def output_excel(target_id):
    style = xlwt.easyxf('font: bold on')
    output_file = "/tmp/hhsrc_output.xls"
    workbook = xlwt.Workbook()
    sheet_doamin = workbook.add_sheet('主域名',cell_overwrite_ok=True)
    sheet_subdoamin = workbook.add_sheet('子域名',cell_overwrite_ok=True)
    sheet_port = workbook.add_sheet('端口',cell_overwrite_ok=True)
    sheet_url = workbook.add_sheet('url',cell_overwrite_ok=True)
    sheet_dirb = workbook.add_sheet('目录',cell_overwrite_ok=True)
    sheet_vuln = workbook.add_sheet('漏洞',cell_overwrite_ok=True)
    sheet_doamin.write(0,0,'主域名',style)
    sheet_doamin.col(1).width = 256 * 15
    sheet_doamin.write(0,1,'采集时间',style)
    sheet_doamin.col(1).width = 256 * 20
    sheet_subdoamin.write(0,0,'子域名',style)
    sheet_subdoamin.col(0).width = 256 * 35
    sheet_subdoamin.write(0,1,'ip',style)
    sheet_subdoamin.col(1).width = 256 * 50
    sheet_subdoamin.write(0,2,'解析',style)
    sheet_subdoamin.col(2).width = 256 * 10
    sheet_subdoamin.write(0,3,'采集时间',style)
    sheet_subdoamin.col(3).width = 256 * 20
    sheet_port.write(0,0,'域名',style)
    sheet_port.col(0).width = 256 * 35
    sheet_port.write(0,1,'ip',style)
    sheet_port.col(1).width = 256 * 18
    sheet_port.write(0,2,'端口',style)
    sheet_port.col(2).width = 256 * 10
    sheet_port.write(0,3,'服务',style)
    sheet_port.col(3).width = 256 * 15
    sheet_port.write(0,4,'采集时间',style)
    sheet_port.col(4).width = 256 * 20
    sheet_url.write(0,0,'目标',style)
    sheet_url.col(0).width = 256 * 60
    sheet_url.write(0,1,'标题',style)
    sheet_url.col(1).width = 256 * 30
    sheet_url.write(0,2,'响应码',style)
    sheet_url.col(2).width = 256 * 10
    sheet_url.write(0,3,'长度',style)
    sheet_url.col(3).width = 256 * 10
    sheet_url.write(0,4,'采集时间',style)
    sheet_url.col(4).width = 256 * 20
    sheet_dirb.write(0,0,'目标',style)
    sheet_dirb.col(0).width = 256 * 60
    sheet_dirb.write(0,1,'标题',style)
    sheet_dirb.col(1).width = 256 * 30
    sheet_dirb.write(0,2,'响应码',style)
    sheet_dirb.col(2).width = 256 * 10
    sheet_dirb.write(0,3,'长度',style)
    sheet_dirb.col(3).width = 256 * 10
    sheet_dirb.write(0,4,'采集时间',style)
    sheet_dirb.col(4).width = 256 * 20
    sheet_vuln.write(0,0,'漏洞等级',style)
    sheet_vuln.write(0,1,'漏洞名',style)
    sheet_vuln.col(1).width = 256 * 30
    sheet_vuln.write(0,2,'漏洞路径',style)
    sheet_vuln.col(2).width = 256 * 60
    sheet_vuln.write(0,3,'采集时间',style)
    sheet_vuln.col(3).width = 256 * 20
    
    row = 1
    for domain_info in domain.query.filter(domain.domain_target == target_id).all():
        sheet_doamin.write(row,0,domain_info.domain_name)
        sheet_doamin.write(row,1,domain_info.domain_time)
        row = row + 1
    row = 1
    for subdomain_info in subdomain.query.filter(subdomain.subdomain_target == target_id).all():
        sheet_subdoamin.write(row,0,subdomain_info.subdomain_name)
        sheet_subdoamin.write(row,1,subdomain_info.subdomain_ip)
        sheet_subdoamin.write(row,2,subdomain_info.subdomain_info)
        sheet_subdoamin.write(row,3,subdomain_info.subdomain_time)
        row = row + 1
    row = 1
    for port_info in port.query.filter(port.port_target == target_id).all():
        sheet_port.write(row,0,port_info.port_domain)
        sheet_port.write(row,1,port_info.port_ip)
        sheet_port.write(row,2,port_info.port_port)
        sheet_port.write(row,3,port_info.port_server)
        sheet_port.write(row,4,port_info.port_time)
        row = row + 1
    row = 1
    for url_info in http.query.filter(http.http_target == target_id).all():
        sheet_url.write(row,0,url_info.http_schema + "://" + url_info.http_name)
        sheet_url.write(row,1,url_info.http_title)
        sheet_url.write(row,2,url_info.http_status)
        sheet_url.write(row,3,url_info.http_length)
        sheet_url.write(row,4,url_info.http_time)
        row = row + 1
    row = 1
    for dirb_info in dirb.query.filter(dirb.dir_target == target_id).all():
        sheet_dirb.write(row,0,dirb_info.dir_base)
        sheet_dirb.write(row,1,dirb_info.dir_title)
        sheet_dirb.write(row,2,dirb_info.dir_status)
        sheet_dirb.write(row,3,dirb_info.dir_length)
        sheet_dirb.write(row,4,dirb_info.dir_time)
        row = row + 1
    row = 1
    for vuln_info in vuln.query.filter(vuln.vuln_target == target_id).all():
        sheet_vuln.write(row,0,vuln_info.vuln_level)
        sheet_vuln.write(row,1,vuln_info.vuln_info)
        sheet_vuln.write(row,2,vuln_info.vuln_path)
        sheet_vuln.write(row,3,vuln_info.vuln_time)
        row = row + 1
    
    workbook.save(output_file)
    