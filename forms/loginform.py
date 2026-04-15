from flask import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=50)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')