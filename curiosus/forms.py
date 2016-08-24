from flask.ext.wtf import Form

from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
