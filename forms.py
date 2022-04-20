import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, \
    DateField, SelectField, IntegerField, DecimalField, BooleanField
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
    theme = SelectMultipleField("Темы: ", coerce=int)
    dec_book_num = IntegerField("Номер по книге решений: ")
    presence_plaintiff = BooleanField("Присутствие истцов: ", default='checked', false_values=(False,))
    presence_defendant = BooleanField("Присутствие ответчиков: ", default='checked', false_values=(False,))
    lawsuit_price = DecimalField("Цена предъявленного иска в рублях: ")
    court_result = SelectField("Результат суда: ", coerce=int)
    court_punishment = SelectMultipleField("Наказания по суду: ", coerce=int)
    compens = DecimalField("Сумма присуждённого возмещения в рублях: ")

    appeal = BooleanField("Обжалование: ", default='unchecked', false_values=(False,))
    appeal_succ = BooleanField("Успешность обжалования: ", default='unchecked', false_values=(False,))
    appeal_date = DateField("Дата подачи апелляции: ")
    ap_decision_date = DateField("Дата решения апелляции: ")
    decision_exec_date = DateField("Дата исполнения решения: ")

    submit = SubmitField("Сохранить изменения")

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    dates = ['create_date', 'decision_date', 'appeal_date', 'ap_decision_date', 'decision_exec_date']
    #    for date in dates:
    #        if not getattr(self, date).data:
    #            setattr(getattr(self, date), 'data', datetime.date(1914, 1, 1))

