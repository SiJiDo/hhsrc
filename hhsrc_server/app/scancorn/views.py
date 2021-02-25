import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
import time
from app.scancorn.forms import scancornForm

from app import models
from app import DB
from . import scancorn

# 通用单模型查询&新增&修改
def scancorn_edit(DynamicModel, form, view):
    id = request.args.get('id', '')
    if id:
        # 查询
        model = DynamicModel.query.filter(DynamicModel.id == id,).first()
        if request.method == 'GET':
            model = utils.queryToDict(model)
            utils.dict_to_form(model, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    model.scancorn_name = form.scancorn_name.data
                    model.scancorn_month = form.scancorn_month.data
                    model.scancorn_week = form.scancorn_week.data
                    model.scancorn_day = form.scancorn_day.data
                    model.scancorn_hour = form.scancorn_hour.data
                    model.scancorn_min = form.scancorn_min.data
                    model.scancorn_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
                    DB.session.commit()
                    flash('修改成功')
                except Exception as e:
                    DB.session.rollback()
                    flash('修改失败')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            try:
                model = DynamicModel(
                    scancorn_name = form.scancorn_name.data,
                    scancorn_month = form.scancorn_month.data,
                    scancorn_week = form.scancorn_week.data,
                    scancorn_day = form.scancorn_day.data,
                    scancorn_hour = form.scancorn_hour.data,
                    scancorn_min = form.scancorn_min.data,
                    scancorn_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())),
                )
                DB.session.add(model)
                DB.session.commit()
            except Exception as e:
                DB.session.rollback()
                flash('修改失败')
            return redirect('scancorn ')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)

# 通用列表查询
def scancorn_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    # 删除操作
    if action == 'del' and id:
        try:
            result = DynamicModel.query.filter(DynamicModel.id == id).first()
            DB.session.delete(result)
            DB.session.commit()
            flash('删除成功')
        except:
            DB.session.rollback()
            flash('删除失败')

    # 查询列表
    query = DynamicModel.query.paginate(page, length)
    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))
    total_count = DynamicModel.query.count()

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template(view, form=dict, current_user=current_user)

# 通知方式配置
@scancorn.route('/scancornedit', methods=['GET', 'POST'])
@login_required
def scancornedit():
    return scancorn_edit(models.scancorn, scancornForm(), 'scancornedit.html')

# 通知方式查询
@scancorn.route('/scancorn', methods=['GET', 'POST'])
@login_required
def scancorn():
    return scancorn_list(models.scancorn, 'scancorn.html')

