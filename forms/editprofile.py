from flask import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.simple import EmailField, TextAreaField
from wtforms.validators import DataRequired, Length


class EditProfileForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    number = StringField('Номер телефона', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")