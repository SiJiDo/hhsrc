from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
import time


class scanmethodForm(FlaskForm):
    scanmethod_name = StringField('扫描模式名', validators=[DataRequired(message='不能为空')])
    scanmethod_subdomain = BooleanField('子域名扫描',default=True)
    scanmethod_port = BooleanField('端口扫描',default=True)
    scanmethod_port_portlist = SelectField('端口模式', choices=[('top100', 'top100端口'), ('top1000', 'top1000端口'),('all', '全端口')])
    scanmethod_url = BooleanField('站点扫描',default=True)
    scanmethod_dirb = BooleanField('目录扫描',default=False)
    scanmethod_dirb_wordlist =  SelectField('目录字典', choices=[('top1000', 'top1000字典'), ('top7000', 'top7000字典')])
    scanmethod_vuln = BooleanField('漏洞扫描',default=False)
    scanmethod_time = StringField('目标修改时间', default=time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())))
    submit = SubmitField('提交')