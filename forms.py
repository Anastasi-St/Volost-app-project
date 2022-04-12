from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired

class EditMeta(FlaskForm):
    doc_name = StringField("Название документа: ", validators=[DataRequired()])
    #guberniya = SelectField("Губерния: ", coerce=int)
    create_date = DateField("Дата подачи заявления: ")
    decision_date = DateField("Дата вынесения решения: ")
    submit = SubmitField("Сохранить изменения")


