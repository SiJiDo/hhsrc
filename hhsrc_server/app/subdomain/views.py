import math
from flask import render_template, request
from flask_login import login_required, current_user
from app import utils
from app import models
from app import DB
from app.models import Target
from . import subdomain

# 通用列表查询
def subdomain_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    search = request.args.get('search')
    if search:
        target = ""
        subdomain_name = ""
        subdomain_ip = ""
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
            if('subdomain' in i):
                subdomain_name = i.split("=")[1]
            if('ip' in i):
                subdomain_ip = i.split("=")[1]
        query = DB.session.query(
                    DynamicModel.id,
                    DynamicModel.subdomain_name, 
                    DynamicModel.subdomain_ip, 
                    DynamicModel.subdomain_info,
                    DynamicModel.subdomain_time,
                    Target.target_name,
                ).join(
                    Target,
                    Target.id == DynamicModel.subdomain_target
                ).filter(
                    Target.target_name.like("%{}%".format(target)),
                    DynamicModel.subdomain_name.like("%{}%".format(subdomain_name)),
                    DynamicModel.subdomain_ip.like("%{}%".format(subdomain_ip)),
                    DynamicModel.subdomain_time <= end_time, 
                    DynamicModel.subdomain_time >= start_time,
                ).order_by(DynamicModel.subdomain_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.join(
            Target,
            Target.id == DynamicModel.subdomain_target
        ).filter(
            Target.target_name.like("%{}%".format(target)),
            DynamicModel.subdomain_name.like("%{}%".format(subdomain_name)),
            DynamicModel.subdomain_ip.like("%{}%".format(subdomain_ip)),
            DynamicModel.subdomain_time <= end_time, 
            DynamicModel.subdomain_time >= start_time,
        ).count()
        search = search.replace("&&", "%26%26")
    else:
        # 查询列表
        query = DB.session.query(
            DynamicModel.id,
            DynamicModel.subdomain_name, 
            DynamicModel.subdomain_ip, 
            DynamicModel.subdomain_info,
            DynamicModel.subdomain_time,
            Target.target_name,
            ).join(
                Target,
                Target.id == DynamicModel.subdomain_target
            ).order_by(DynamicModel.subdomain_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.count()
    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))
    
    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'search': search}
    return render_template(view, form=dict, current_user=current_user)

# 通用列表查询
def subdomain_info(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    query_subdomain = DB.session.query(
        DynamicModel.subdomain_name,
        DynamicModel.subdomain_ip,
        DynamicModel.subdomain_info,
        DynamicModel.subdomain_time,
        Target.target_name,
    ).join(
        Target,
        Target.id == DynamicModel.subdomain_target
    ).filter(
        DynamicModel.id == id
    ).first()

    # 查询列表
    query = DB.session.query(
        models.port.port_port,
        models.port.port_server,
        models.port.port_time,
        ).filter(
            models.port.port_ip == query_subdomain.subdomain_ip,
        ).order_by(models.port.port_time.desc()).order_by(models.port.id.desc()).paginate(page, length)
    total_count = models.port.query.filter(models.port.port_ip == query_subdomain.subdomain_ip).count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))

    dict = {'content': content, 'total_count': total_count, 'id':id,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'subdomain_info': query_subdomain}
    return render_template(view, form=dict, current_user=current_user)

# 通知方式查询
@subdomain.route('/subdomaininfo', methods=['GET', 'POST'])
@login_required
def subdomaininfo():
    return subdomain_info(models.subdomain, 'result/subdomain_info.html')
    # return common_list(CfgNotify, 'test.html')


# 通知方式查询
@subdomain.route('/subdomain', methods=['GET', 'POST'])
@login_required
def subdomain():
    return subdomain_list(models.subdomain, 'result/subdomain.html')
    # return common_list(CfgNotify, 'test.html')

