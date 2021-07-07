import math
from flask import render_template, request
from flask_login import login_required, current_user
from app import utils
from app.models import dirb
from app import DB

from app.models import Target
from . import fileleak

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
        dir_url = ""
        dir_status = ""
        dir_title = ""
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
                dir_url = i.split("=")[1]
            if('title' in i):
                dir_title = i.split("=")[1]
            if('status' in i):
                dir_status = i.split("=")[1]
        query = DB.session.query(
                    DynamicModel.dir_base, 
                    DynamicModel.dir_status, 
                    DynamicModel.dir_length,
                    DynamicModel.dir_title,
                    DynamicModel.dir_time,
                    Target.target_name,
                ).join(
                    Target,
                    Target.id == DynamicModel.dir_target
                ).filter(
                    Target.target_name.like("%{}%".format(target)),
                    DynamicModel.dir_base.like("%{}%".format(dir_url)),
                    DynamicModel.dir_status.like("%{}%".format(dir_status)),
                    DynamicModel.dir_title.like("%{}%".format(dir_title)),
                    DynamicModel.dir_time <= end_time, 
                    DynamicModel.dir_time >= start_time,
                ).order_by(DynamicModel.dir_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        search = search.replace("&&", "%26%26")
        total_count = DynamicModel.query.join(
            Target,
            Target.id == DynamicModel.dir_target
        ).filter(
            Target.target_name.like("%{}%".format(target)),
            DynamicModel.dir_base.like("%{}%".format(dir_url)),
            DynamicModel.dir_status.like("%{}%".format(dir_status)),
            DynamicModel.dir_title.like("%{}%".format(dir_title)),
            DynamicModel.dir_time <= end_time, 
            DynamicModel.dir_time >= start_time,
        ).count()

    else:
        # 查询列表
        query = DB.session.query(
            DynamicModel.dir_base, 
            DynamicModel.dir_status, 
            DynamicModel.dir_length,
            DynamicModel.dir_title,
            DynamicModel.dir_time,
            Target.target_name,
            ).join(
                Target,
                Target.id == DynamicModel.dir_target
            ).order_by(DynamicModel.dir_time.desc()).order_by(DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'search': search}
    return render_template(view, form=dict, current_user=current_user)


# 通知方式查询
@fileleak.route('/fileleak', methods=['GET', 'POST'])
@login_required
def fileleak():
    return common_list(dirb, 'result/fileleak.html')
