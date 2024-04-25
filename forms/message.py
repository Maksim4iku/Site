from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    text = TextAreaField("Сообщение пользователю", validators=[DataRequired()])
    id_user = IntegerField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Применить')
