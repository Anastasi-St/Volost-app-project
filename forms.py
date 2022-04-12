from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired

class EditMeta(FlaskForm):
    doc_name = StringField("Название документа: ", validators=[DataRequired()])
    guberniya = SelectField("Губерния: ", coerce=int)
    uyezd = SelectField("Уезд: ", coerce=int)
    volost = SelectField("Волость: ", coerce=int)
    plaintiff_res_place = SelectField("Место жительства истца: ", coerce=int)
    defendant_res_place = SelectField("Место жительства ответчика: ", coerce=int)
    create_date = DateField("Дата подачи заявления: ")
    decision_date = DateField("Дата вынесения решения: ")
    dec_book_num = IntegerField("Номер по книге решений: ")
    submit = SubmitField("Сохранить изменения")


