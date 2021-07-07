import math
from flask import render_template, flash, request, send_from_directory
from flask_login import login_required, current_user
from wtforms import SelectField
from app import utils
from multiprocessing import Process
import time
from scan import scan
from scan import corn

from app.models import Target,scanmethod, domain, blacklist, subdomain, port, http, dirb, scancorn, vuln
from app.targetManager.forms import TargetForm
from app.targetManager import target_utils
from app import DB
from . import target

# 通用单模型查询&新增&修改
def target_edit(DynamicModel, form, view):
    #定义扫描模式下拉框
    model = scanmethod.query.all()
    model = utils.queryToDict(model)
    list = [(c['id'],c['scanmethod_name']) for c in model]
    form.target_method.choices = list

    #定义扫描周期下拉框
    model = scancorn.query.all()
    model = utils.queryToDict(model)
    list_corn = [(c['id'],c['scancorn_name']) for c in model]
    form.target_corn_id.choices = list_corn

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
                    model.target_name = form.target_name.data
                    model.target_description = form.target_description.data
                    model.target_method = form.target_method.data
                    model.target_level = form.target_level.data
                    model.target_corn = form.target_corn.data
                    model.target_corn_id = form.target_corn_id.data
                    model.target_time = form.target_time.data
                    DB.session.commit()
                    flash('修改成功')
                except Exception as e:
                    DB.session.rollback()
                    print(e)
                    flash('修改失败')
                #存储非target字段
                target_utils.save_domain(target_id=id, form=form)
                target_utils.save_blacklist(target_id=id, form=form)
                target_utils.save_subdomain(target_id=id, form = form)
                target_utils.save_ip(target_id=id, form = form)
                #开始扫描
                p=Process(target=scan.run,args=(id,))
                p.start()
                #启动计划任务监控子进程
                print("开始计划任务监控")
                p = Process(target=corn.setcorn)
                p.start()
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            #提取目标id
            try:
                t = Target(
                    target_name = form.target_name.data,
                    target_description = form.target_description.data,
                    target_method = form.target_method.data,
                    target_level = form.target_level.data,
                    target_corn = form.target_corn.data,
                    target_corn_id = form.target_corn_id.data,
                    target_time = form.target_time.data,
                    target_status = form.target_status.data,
                )
                DB.session.add(t)   # 把对象添加到会话中.
                DB.session.commit()
            except Exception as e:
                DB.session.rollback()
                print(e)
                flash('新增失败')

            id = DynamicModel.query.filter(DynamicModel.target_name == form.target_name.data,).order_by(DynamicModel.target_time.desc()).first().id
            #存储非target字段
            target_utils.save_domain(target_id=id, form=form)
            target_utils.save_blacklist(target_id=id, form=form)
            target_utils.save_subdomain(target_id=id, form = form)
            target_utils.save_ip(target_id=id, form = form)
            #开始扫描
            p=Process(target=scan.run,args=(id,))
            p.start()
            #启动计划任务监控子进程
            print("开始计划任务监控")
            p = Process(target=corn.setcorn)
            p.start()
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)

# 通用列表查询
def target_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10

    # 删除操作
    if action == 'del' and id:
        try:
            result = DynamicModel.query.filter(DynamicModel.id == id).all()
            [DB.session.delete(r) for r in result]
            result = blacklist.query.filter(blacklist.black_target == id).all()
            [DB.session.delete(r) for r in result]
            result = domain.query.filter(domain.domain_target == id).all()
            [DB.session.delete(r) for r in result]
            result = subdomain.query.filter(subdomain.subdomain_target == id).all()
            [DB.session.delete(r) for r in result]
            result = port.query.filter(port.port_target == id).all()
            [DB.session.delete(r) for r in result]
            result = http.query.filter(http.http_target == id).all()
            [DB.session.delete(r) for r in result]
            result = dirb.query.filter(dirb.dir_target == id).all()
            [DB.session.delete(r) for r in result]
            result = vuln.query.filter(vuln.vuln_target == id).all()
            [DB.session.delete(r) for r in result]
            DB.session.commit()
            flash('删除成功')
        except Exception as e:
            print(e)
            DB.session.rollback()
            flash('删除失败')

    search = request.args.get('search')
    if search:
        target = ""
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
        print(target)
        print(start_time)
        search = search.replace("&&", "%26%26")
        query = DynamicModel.query.filter(
                DynamicModel.target_name.like("%{}%".format(target)),
                DynamicModel.target_time <= end_time, 
                DynamicModel.target_time >= start_time,
                ).order_by(DynamicModel.target_time.desc(),DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.filter(
            DynamicModel.target_name.like("%{}%".format(target)),
            DynamicModel.target_time <= end_time, 
            DynamicModel.target_time >= start_time,
            ).count()
    else:
        query = DynamicModel.query.order_by(DynamicModel.target_time.desc(),DynamicModel.id.desc()).paginate(page, length)
        total_count = DynamicModel.query.count()

    content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))

    for i in content:
        i['domain_total_count'] = domain.query.filter(domain.domain_target == i['id']).count()
        i['subdomain_total_count'] = subdomain.query.filter(subdomain.subdomain_target == i['id']).count()
        i['port_total_count'] = port.query.filter(port.port_target == i['id']).count()
        i['url_total_count'] = http.query.filter(http.http_target == i['id']).count()

    dict = {'content': content, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 'search': search}
    return render_template(view, form=dict, current_user=current_user)


# 通用列表查询
def target_info(DynamicModel, view):
    # 接收参数
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else 10
    domain_id = request.args.get('domain_id')
    blacklist_id = request.args.get('blacklist_id')
    action = request.args.get('action')

    blacklist_page = int(request.args.get('blacklist_page')) if request.args.get('blacklist_page') else 1
    blacklist_length = int(request.args.get('blacklist_length')) if request.args.get('blacklist_length') else 10

    if action == 'output':
        target_utils.output_excel(id)
        return send_from_directory(r"/tmp",filename="hhsrc_output.xls",as_attachment=True)

    if action == 'restart':
        try:
            #开始重新扫描
            target_model = Target.query.filter(Target.id == id).first()
            target_model.target_status = 0
            try:
                domain_model = domain.query.filter(domain.domain_target == id).all()
                for model in domain_model:
                    model.domain_subdomain_status = False
            except:
                pass
            try:
                subdomain_model = subdomain.query.filter(subdomain.subdomain_target == id).all()
                for model in subdomain_model:
                    model.subdomain_port_status = False
                    model.subdomain_http_status = False
            except:
                pass
            try:
                port_model = port.query.filter(port.port_target == id).all()
                for model in port_model:
                    model.port_http_status = False
            except:
                pass
            try:
                http_model = http.query.filter(http.http_target == id).all()
                for model in http_model:
                    model.http_dirb_status = False
                    model.http_vuln_status = False
            except:
                pass
            DB.session.commit()
            flash('开始重新扫描')
            p = Process(target=scan.run,args=(id,))
            p.start()
        except Exception as e:
            DB.session.rollback()
            print(e)
            flash('未知错误')

    # 删除操作
    if action == 'del' and (domain_id or blacklist_id):
        try:
            if(blacklist_id):
                result = blacklist.query.filter(blacklist.id == blacklist_id).all()
                [DB.session.delete(r) for r in result]
            else:
                domain_name = domain.query.filter(domain.id == domain_id).first().domain_name
            
                result = subdomain.query.filter(subdomain.subdomain_name.like("%.{}".format(domain_name))).all()
                [DB.session.delete(r) for r in result]
                result = port.query.filter(port.port_domain.like("%.{}".format(domain_name))).all()
                [DB.session.delete(r) for r in result]
                result = http.query.filter(http.http_name.like("%.{}".format(domain_name))).all()
                [DB.session.delete(r) for r in result]
                result = dirb.query.filter(dirb.dir_base.like("%.{}".format(domain_name))).all()
                [DB.session.delete(r) for r in result]
                result = vuln.query.filter(vuln.vuln_http.like("%.{}".format(domain_name))).all()
                [DB.session.delete(r) for r in result]
                result = domain.query.filter(domain.id == domain_id).all()
                [DB.session.delete(r) for r in result]
            DB.session.commit()
            flash('删除成功')
        except Exception as e:
            print(e)
            DB.session.rollback()
            flash('删除失败')

    query_target = Target.query.filter(
        Target.id == id,
    ).first()
    subdomain_total_count = subdomain.query.filter(subdomain.subdomain_target == id).count()
    port_total_count = port.query.filter(port.port_target == id).count()
    url_total_count = http.query.filter(http.http_target == id).count()

    #获取blacklist的信息
    query_blacklist = blacklist.query.filter(
        blacklist.black_target == id,
    ).paginate(blacklist_page, blacklist_length)

    # 获取domain的信息
    query = DynamicModel.query.filter(
        DynamicModel.domain_target == id,
    ).order_by(DynamicModel.domain_time.desc(),DynamicModel.id.desc()).paginate(page, length)

    #获取总数，用于分页
    blacklist_total_count = blacklist.query.filter(blacklist.black_target == id).count()
    total_count = domain.query.filter(domain.domain_target == id).count()

    content = []
    blacklist_content = []
    #转换成dict
    for q in query.items:
        content.append(utils.queryToDict(q))
    for q in query_blacklist.items:
        blacklist_content.append(utils.queryToDict(q))
    for i in content:
        i['subdomain_count'] = subdomain.query.filter(subdomain.subdomain_target == id, subdomain.subdomain_name.like('%.{}'.format(i['domain_name']))).count()
        i['port_count'] = port.query.filter(port.port_target == id, port.port_domain.like('%.{}'.format(i['domain_name']))).count()
        i['url_count'] = http.query.filter(http.http_target == id, http.http_name.like('%.{}'.format(i['domain_name']))).count()

    dict = {'content': content, 'total_count': total_count,'id':id,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length, 
            'subdomain_total_count': subdomain_total_count, 'port_total_count': port_total_count, 'url_total_count': url_total_count,
            'blacklist_content': blacklist_content, 'blacklist_total_count': blacklist_total_count,
            'blacklist_total_page': math.ceil(blacklist_total_count / blacklist_length), 'blacklist_page': blacklist_page, 'blacklist_length': blacklist_length, 
            'target_info': query_target}
    return render_template(view, form=dict, current_user=current_user)

# 目标信息配置
@target.route('/targetinfo', methods=['GET', 'POST'])
@login_required
def targetinfo():
    return target_info(domain, 'target_info.html')

# 目标信息配置
@target.route('/targetedit', methods=['GET', 'POST'])
@login_required
def targetedit():
    return target_edit(Target, TargetForm(), 'targetedit.html')

# 目标信息查询
@target.route('/target', methods=['GET', 'POST'])
@login_required
def target():
    return target_list(Target, 'target.html')
