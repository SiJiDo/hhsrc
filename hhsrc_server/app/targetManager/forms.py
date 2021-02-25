from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
import time
from app import utils

class TargetForm(FlaskForm):
    target_name = StringField('目标名', validators=[DataRequired(message='不能为空')])
    target_description = StringField('目标描述', validators=[DataRequired(message='不能为空')])
    target_time = StringField('目标修改时间', default=time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())))
    target_level = IntegerField('目标优先级', validators=[DataRequired(message='不能为空')])
    target_method = SelectField('扫描模式名')
    target_corn = BooleanField('周期监控', default=False)
    target_corn_id = SelectField('扫描周期名')
    target_status = IntegerField('扫描状况', default=0)

    black_name = TextAreaField('黑名单添加')
    domain_name = TextAreaField('主域名资产添加')
    subdomain_name = TextAreaField('精准域名资产添加')
    subdomain_ip = TextAreaField('ip资产添加')

    submit = SubmitField('添加/修改')

