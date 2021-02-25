from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), ])
    password = PasswordField('密码', validators=[DataRequired()])
    rememberme = BooleanField('记住我')
    submit = SubmitField('提交')

class ChangePwdForm(FlaskForm):
    password = PasswordField('旧密码', validators=[DataRequired()])
    newpassword = PasswordField('新密码', validators=[DataRequired()])
    submit = SubmitField('提交')