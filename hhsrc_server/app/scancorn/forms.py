from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
import time

#对年月日进行预设
list_min = []
for i in range(0, 60):
    list_min.append((str(i),str(i)))
list_hour = [('*','*')]
for i in range(0,24):
    list_hour.append((str(i),str(i)))
list_day = [('*','*')]
for i in range(1,32):
    list_day.append((str(i),str(i)))

list_day_of_week = [('*','*')]
for i in range(1,8):
    list_day_of_week.append((str(i),str(i)))

list_month = [('*','*')]
for i in range(1,13):
    list_month.append((str(i),str(i)))


class scancornForm(FlaskForm):
    scancorn_name = StringField('定时器名', validators=[DataRequired(message='不能为空')])   #定时名
    scancorn_month = SelectField('月', choices=list_month) #定时月
    scancorn_week = SelectField('周', choices=list_day_of_week)  #定时周
    scancorn_day = SelectField('日', choices=list_day)  #定时天
    scancorn_hour = SelectField('小时', choices=list_hour) #定时小时
    scancorn_min = SelectField('分钟', choices=list_min) #定时分钟
    scancorn_time = StringField('目标修改时间', default=time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())))   #修改时间
    submit = SubmitField('提交')
