from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional

class ToursForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    number = StringField('Номер телефона', validators=[DataRequired()])
    type = TextAreaField("Немного о себе")
    place = TextAreaField('Куда', validators=[DataRequired()])
    date = IntegerField('Длительность (дней)', validators=[DataRequired()])
    content = TextAreaField('Дополнительные требования', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку')