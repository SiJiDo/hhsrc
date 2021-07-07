import math
from flask import render_template, request
from flask_login import login_required, current_user
from app import utils
from app.models import Target
from app import DB

from app import models
from . import port

# 通用列表查询
def common_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    search = request.args.get('search')
    if search:
        target = ""
        port_domain = ""
        port_ip = ""
        port_port = ""
        port_server = ""
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
                port_domain = i.split("=")[1]
            if('ip' in i):
                port_ip = i.split("=")[1]
            if('port' in i):
                port_port = i.split("=")[1]
            if('server' in i):
                port_server = i.split("=")[1]
        query = DB.session.query(
                    DynamicModel.port_domain, 
                    DynamicModel.port_ip, 
                    DynamicModel.port_port,
                    DynamicModel.port_server,
                    DynamicModel.port_time,
                    Target.target_name,
                ).join(
                    Target,
                    Target.id == DynamicModel.port_target
                ).filter(
                    Target.target_name.like("%{}%".format(target)),
                    DynamicModel.port_domain.like("%{}%".format(port_domain)),
                    DynamicModel.port_ip.like("%{}%".format(port_ip)),
                    DynamicModel.port_port.like("%{}%".format(port_port)),
                    DynamicModel.port_server.like("%{}%".format(port_server)),
                    DynamicModel.port_time <= end_time, 
                    DynamicModel.port_time >= start_time,
                ).order_by(DynamicModel.port_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = models.port.query.join(
            Target,
            Target.id == DynamicModel.port_target
        ).filter(
            Target.target_name.like("%{}%".format(target)),
            DynamicModel.port_domain.like("%{}%".format(port_domain)),
            DynamicModel.port_ip.like("%{}%".format(port_ip)),
            DynamicModel.port_port.like("%{}%".format(port_port)),
            DynamicModel.port_server.like("%{}%".format(port_server)),
            DynamicModel.port_time <= end_time, 
            DynamicModel.port_time >= start_time,).count()
        search = search.replace("&&", "%26%26")
    else:
        # 查询列表
        query = DB.session.query(
            DynamicModel.port_domain, 
            DynamicModel.port_ip, 
            DynamicModel.port_port,
            DynamicModel.port_server,
            DynamicModel.port_time,
            Target.target_name,
            ).join(
                Target,
                Target.id == DynamicModel.port_target
            ).order_by(DynamicModel.port_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = models.port.query.count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'search': search, 'id': id}
    return render_template(view, form=dict, current_user=current_user)

# 通知方式查询
@port.route('/port', methods=['GET', 'POST'])
@login_required
def port():
    return common_list(models.port, 'result/port.html')
