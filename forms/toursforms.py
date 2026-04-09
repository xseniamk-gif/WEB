from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class ToursForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    cost = StringField('Стоимость', validators=[DataRequired()])
    data = StringField('Даты поездки', validators=[DataRequired()])
    about = TextAreaField("О туре")
    free_pl = StringField('Свободные места', validators=[DataRequired()])
    submit = SubmitField('В корзину')