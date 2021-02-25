import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
from app import models
from app import DB

from app.models import Target
from . import vuln

# 通用单模型查询&新增&修改
def common_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    search = request.args.get('search')
    if search:
        target = ""
        vuln_url = ""
        vuln_info = ""
        vuln_level = ""
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
            if('level' in i):
                vuln_level = i.split("=")[1]
            if('url' in i):
                vuln_url = i.split("=")[1]
            if('info' in i):
                vuln_info = i.split("=")[1]
        query = DB.session.query(
                    DynamicModel.vuln_path, 
                    DynamicModel.vuln_level, 
                    DynamicModel.vuln_info,
                    DynamicModel.vuln_time,
                    Target.target_name,
                ).join(
                    Target,
                    Target.id == DynamicModel.vuln_target
                ).filter(
                    Target.target_name.like("%{}%".format(target)),
                    DynamicModel.vuln_level.like("%{}%".format(vuln_level)),
                    DynamicModel.vuln_info.like("%{}%".format(vuln_info)),
                    DynamicModel.vuln_path.like("%{}%".format(vuln_url)),
                    DynamicModel.vuln_time <= end_time, 
                    DynamicModel.vuln_time >= start_time,
                ).order_by(DynamicModel.vuln_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        search = search.replace("&&", "%26%26")
        total_count = DynamicModel.query.join(
            Target,
            Target.id == DynamicModel.vuln_target
        ).filter(
            Target.target_name.like("%{}%".format(target)),
            DynamicModel.vuln_level.like("%{}%".format(vuln_level)),
            DynamicModel.vuln_info.like("%{}%".format(vuln_info)),
            DynamicModel.vuln_path.like("%{}%".format(vuln_url)),
            DynamicModel.vuln_time <= end_time, 
            DynamicModel.vuln_time >= start_time,
        ).count()

    else:
        # 查询列表
        query = DB.session.query(
            DynamicModel.vuln_path, 
            DynamicModel.vuln_level, 
            DynamicModel.vuln_info,
            DynamicModel.vuln_time,
            Target.target_name,
            ).join(
                Target,
                Target.id == DynamicModel.vuln_target
            ).order_by(DynamicModel.vuln_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'search': search}
    return render_template(view, form=dict, current_user=current_user)


# 通知方式查询
@vuln.route('/vuln', methods=['GET', 'POST'])
@login_required
def vuln():
    return common_list(models.vuln, 'result/vuln.html')
