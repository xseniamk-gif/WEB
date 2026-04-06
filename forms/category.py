from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    category_id = StringField('id')
    name = TextAreaField("Имя категории", validators=[DataRequired()])
    submit = SubmitField('Применить')
