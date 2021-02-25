from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
