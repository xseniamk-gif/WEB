from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    # login = StringField('Логин пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    number = StringField('Телефон пользователя', validators=[DataRequired()])
    # password = PasswordField('Пароль')
    # password_again = PasswordField('Повторите пароль')
    # user_type_id = SelectField("Категория", coerce=int, validators=[DataRequired()])
    submit = SubmitField('Применить')
