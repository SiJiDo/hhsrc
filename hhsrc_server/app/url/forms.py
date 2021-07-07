from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

class HttpForm(FlaskForm):
    unsubmit = SubmitField('已阅')
    submit = SubmitField('未阅')