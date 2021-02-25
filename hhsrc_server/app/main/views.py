import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import DB
from app.models import Target, subdomain, port, http

from . import main


# 通用列表查询
def common_list(view):

    dict = {
        'target_count':Target.query.count(),
        'subdomain_count':subdomain.query.count(),
        'port_count':port.query.count(),
        'http_count':http.query.count(),
    }
    return render_template(view, form=dict, current_user=current_user)


# 根目录跳转
@main.route('/', methods=['GET'])
@login_required
def root():
    return redirect(url_for('main.index'))



# 首页
@main.route('/index', methods=['GET'])
@login_required
def index():
    return common_list(view="index.html")
