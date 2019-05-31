import os

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, InputRequired
from flask_babel import lazy_gettext as _l

from vshaurme.models import User
from vshaurme.utils import get_rus_swear_words


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Log in'))


class RegisterForm(FlaskForm):
    def is_bad_username(self, field):
        path = current_app.config['SWEAR_WORDS']
        if os.path.getsize(path) > 0:
            with open(path, 'r') as f:
                for word in f:
                    if word.strip() in field.data:
                        raise ValidationError(_l("Please don't use swear words in username"))
        if get_rus_swear_words(field.data) > 0:
            raise ValidationError(_l("Please don't use swear words in username"))

    name = StringField(_l('Name'), validators=[DataRequired(), Length(1, 30)])
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 254), Email()])
    username = StringField(_l('Username'), validators=[InputRequired(), Length(1, 20), Regexp('^[a-zA-Z0-9]*$', message=_l('The username should contain only a-z, A-Z and 0-9.')), is_bad_username])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(), Length(8, 128), EqualTo(_l('password2'))])
    password2 = PasswordField(_l('Confirm password'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(_l('The email is already in use.'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class ForgetPasswordForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField(_l('Submit'))


class ResetPasswordForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(), Length(8, 128), EqualTo(_l('password2'))])
    password2 = PasswordField(_l('Confirm password'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
