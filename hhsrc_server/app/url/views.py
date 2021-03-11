import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils

from app.models import Target,http, dirb, subdomain, vuln
from app import DB
from app.targetManager.forms import TargetForm
from . import url

# 通用列表查询
def url_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    search = request.args.get('search')
    if search:
        target = ""
        http_url = ""
        http_title = ""
        http_status = ""
        start_time = "2021-01-01 00:00:00"
        end_time = "2099-01-01 00:00:00"
        info = search.split("&&")
        for i in info:
            if('target' in i):
                target = i.split("=")[1]
            if('start_time' in i):
                start_time = i.split("=")[1]
            if('end_time' in i):
                end_time = i.split("=")[1]
            if('url' in i):
                http_url = i.split("=")[1]
            if('title' in i):
                http_title = i.split("=")[1]
            if('status' in i):
                http_status = i.split("=")[1]
        query = DB.session.query(
                    DynamicModel.id,
                    DynamicModel.http_schema, 
                    DynamicModel.http_name, 
                    DynamicModel.http_title,
                    DynamicModel.http_status,
                    DynamicModel.http_length,
                    DynamicModel.http_screen,
                    DynamicModel.http_time,
                    Target.target_name,
                ).join(
                    Target,
                    Target.id == DynamicModel.http_target
                ).filter(
                    Target.target_name.like("%{}%".format(target)),
                    DynamicModel.http_name.like("%{}%".format(http_url)),
                    DynamicModel.http_title.like("%{}%".format(http_title)),
                    DynamicModel.http_status.like("%{}%".format(http_status)),
                    DynamicModel.http_time <= end_time, 
                    DynamicModel.http_time >= start_time,
                ).order_by(DynamicModel.http_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        search = search.replace("&&", "%26%26")
        total_count = DynamicModel.query.join(
            Target,
            Target.id == DynamicModel.http_target
        ).filter(
            Target.target_name.like("%{}%".format(target)),
            DynamicModel.http_name.like("%{}%".format(http_url)),
            DynamicModel.http_title.like("%{}%".format(http_title)),
            DynamicModel.http_status.like("%{}%".format(http_status)),
            DynamicModel.http_time <= end_time, 
            DynamicModel.http_time >= start_time,
        ).count()
    else:
        # 查询列表
        query = DB.session.query(
            DynamicModel.id,
            DynamicModel.http_schema, 
            DynamicModel.http_name, 
            DynamicModel.http_title,
            DynamicModel.http_status,
            DynamicModel.http_length,
            DynamicModel.http_screen,
            DynamicModel.http_time,
            Target.target_name,
            ).join(
                Target,
                Target.id == DynamicModel.http_target
            ).order_by(DynamicModel.http_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))
    for i in content:
        i['dirb_count'] = dirb.query.filter(dirb.dir_http == str(i['id'])).count()
        i['vuln_count'] = vuln.query.filter(vuln.vuln_http == str(i['id'])).count()

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'id': id,'search': search}
    return render_template(view, form=dict, current_user=current_user)


# 通用列表查询
def url_info(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10
    vuln_page = int(request.args.get('vuln_page')) if request.args.get('vuln_page') else 1
    vuln_length = int(request.args.get('vuln_length')) if request.args.get('vuln_length') else 10

    # 查询列表
    http_info = DB.session.query(
            DynamicModel.http_schema,
            DynamicModel.http_name, 
            DynamicModel.http_title,
            DynamicModel.http_status,
            DynamicModel.http_length,
            DynamicModel.http_screen,
            DynamicModel.http_time,
            Target.target_name,
        ).join(
            Target,
            Target.id == DynamicModel.http_target
        ).filter(
            DynamicModel.id == id,
        ).first()
    #获取ip地址
    try:
        ip = subdomain.query.filter(subdomain.subdomain_name == http_info.http_name.split(":")[0]).first().subdomain_ip
        print(ip)
    except:
        ip = ""

    # 查询敏感目录列表
    query_dirb = DB.session.query(
        dirb.dir_path, 
        dirb.dir_status, 
        dirb.dir_title,
        dirb.dir_length,
        dirb.dir_time,
        ).filter(
            dirb.dir_http == id,
        ).paginate(page, length)
    
    # 查询敏感目录列表
    query_vuln = DB.session.query(
        vuln.vuln_level, 
        vuln.vuln_info, 
        vuln.vuln_path,
        vuln.vuln_time,
        ).filter(
            vuln.vuln_http == id,
        ).paginate(vuln_page, vuln_length)

    #获取总数，用于分页
    vuln_total_count = vuln.query.filter(vuln.vuln_http == id).count()
    total_count = dirb.query.filter(dirb.dir_http == id).count()

    dirb_content = []
    vuln_content = []
    #转换成dict
    for q in query_dirb.items:
        dirb_content.append(utils.queryToDict(q))
    for q in query_vuln.items:
        vuln_content.append(utils.queryToDict(q))

    dict = {'http_info': http_info, 'id': id, 'ip':ip,
            'dirb_content': dirb_content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length,
            'vuln_content': vuln_content, 'vuln_total_count': vuln_total_count,
            'vuln_total_page': math.ceil(vuln_total_count / vuln_length), 'vuln_page': vuln_page, 'vuln_length': vuln_length,
            }
    return render_template(view, form=dict, current_user=current_user)

# 通知方式查询
@url.route('/urlinfo', methods=['GET', 'POST'])
@login_required
def urlinfo():
    return url_info(http, 'result/url_info.html')

# 通知方式查询
@url.route('/url', methods=['GET', 'POST'])
@login_required
def url():
    return url_list(http, 'result/url.html')
