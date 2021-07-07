from flask import render_template, flash, request
from flask_login import login_required, current_user

from app import models
from app import DB
from . import commonconfig

import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

# 通用列表查询
def common_list(DynamicModel,view):

    action = request.args.get('action')
    count = request.args.get('count')
    server = request.args.get('server')

    print(server)
    
    model = DynamicModel.query.first()

    if action == 'set':
        try:
            model.config_count = int(count)
            model.config_server = server
            DB.session.commit()
            flash('修改成功')
        except:
            DB.session.rollback()
            flash('修改失败')

    dict = {
        'config_count':model.config_count,
        'config_server':model.config_server,
        'public_host':cfg.get("HOST","PUBLIC_HOST")
    }
    return render_template(view, form=dict, current_user=current_user)

# 首页
@commonconfig.route('/commonconfig', methods=['GET'])
@login_required
def commonconfig():
    return common_list(DynamicModel= models.commonconfig, view="common_config.html")
