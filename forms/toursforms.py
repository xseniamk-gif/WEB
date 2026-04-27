from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional

class ToursForm(FlaskForm):
    title = StringField('Название тура', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    duration = IntegerField('Длительность (дней)', validators=[DataRequired()])
    content = TextAreaField('Описание тура', validators=[DataRequired()])
    free_pl = IntegerField('Свободных мест', validators=[DataRequired()])
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    is_published = BooleanField('Опубликован')
    img = FileField('Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения!')
    ])
    submit = SubmitField('Сохранить')