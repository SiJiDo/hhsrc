import math
from flask import render_template, redirect, flash, request
from flask_login import login_required, current_user
import time

from app.models import scanmethod
from app import DB
from app import utils
from app.scanconfig.forms import scanmethodForm
from . import scanconfig

# 通用单模型查询&新增&修改
def scanconfig_edit(DynamicModel, form, view):
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
                    model.scanmethod_name = form.scanmethod_name.data
                    model.scanmethod_subdomain = form.scanmethod_subdomain.data
                    model.scanmethod_port = form.scanmethod_port.data
                    model.scanmethod_port_portlist = form.scanmethod_port_portlist.data
                    model.scanmethod_url = form.scanmethod_url.data
                    model.scanmethod_dirb = form.scanmethod_dirb.data
                    model.scanmethod_dirb_wordlist = form.scanmethod_dirb_wordlist.data
                    model.scanmethod_vuln = form.scanmethod_vuln.data
                    model.scanmethod_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
                    DB.session.commit()
                    flash('修改成功')
                except Exception as e:
                    DB.session.rollback()
                    print(e)
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            try:
                scanmethod_model = scanmethod(
                    scanmethod_name = form.scanmethod_name.data,
                    scanmethod_subdomain = form.scanmethod_subdomain.data,
                    scanmethod_port = form.scanmethod_port.data,
                    scanmethod_port_portlist = form.scanmethod_port_portlist.data,
                    scanmethod_url = form.scanmethod_url.data,
                    scanmethod_dirb = form.scanmethod_dirb.data,
                    scanmethod_dirb_wordlist = form.scanmethod_dirb_wordlist.data,
                    scanmethod_vuln = form.scanmethod_vuln.data,
                    scanmethod_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())),
                )
                DB.session.add(scanmethod_model)
                DB.session.commit()
                flash('保存成功')
            except Exception as e:
                DB.session.rollback()
                flash('保存失败')
            return redirect('scanconfig')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)

# 通用列表查询
def scanconfig_list(DynamicModel, view):
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

# 添加扫描模块式
@scanconfig.route('/scanconfigedit', methods=['GET', 'POST'])
@login_required
def scanconfigedit():
    return scanconfig_edit(scanmethod, scanmethodForm(), 'scanmethodedit.html')


# 查看扫描模式
@scanconfig.route('/scanconfig', methods=['GET'])
@login_required
def scanconfig():
    return scanconfig_list(scanmethod, 'scanmethod.html')


