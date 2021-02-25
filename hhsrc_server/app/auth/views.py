from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, ChangePwdForm
from app.models import User
from app import DB
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter(
                    User.username == form.username.data,
                ).first()
            if check_password_hash(user.password, form.password.data):
                login_user(user, form.rememberme.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                flash('用户名或密码错误')
        except Exception as e:
            print(e)
            flash('用户名或密码错误')

    return render_template('auth/login.html', form = form)

@auth.route('/changepwd', methods=['GET', 'POST'])
def changepwd():
    form = ChangePwdForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter(User.username == 'admin',).first()
            
            if check_password_hash(user.password, form.password.data):
                newpassword = generate_password_hash(form.newpassword.data)
                user.password = newpassword
                DB.session.commit()
                flash('修改成功')
            else:
                flash('旧密码错误')
        except Exception as e:
            DB.session.rollback()
            print(e)
            flash('旧密码错误')
    return render_template('auth/changepwd.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('auth.login'))
