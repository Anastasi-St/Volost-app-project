import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, \
    DateField, SelectField, IntegerField, DecimalField, BooleanField, \
    MultipleFileField
from flask_wtf.file import  FileAllowed
from wtforms.validators import DataRequired, regexp

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

class AddDoc(FlaskForm):
    doc_name = StringField("Название документа: ", validators=[DataRequired()])
    guberniya = SelectField("Губерния: ", coerce=int)
    uyezd = SelectField("Уезд: ", coerce=int)
    volost = SelectField("Волость: ", coerce=int)
    plaintiff_res_place = SelectField("Место жительства истца: ", coerce=int)
    defendant_res_place = SelectField("Место жительства ответчика: ", coerce=int)
    create_date = DateField("Дата подачи заявления: ", default=datetime.date(1914, 1, 1))
    decision_date = DateField("Дата вынесения решения: ", default=datetime.date(1914, 1, 1))
    theme = SelectMultipleField("Темы: ", coerce=int)
    dec_book_num = IntegerField("Номер по книге решений: ")
    presence_plaintiff = BooleanField("Присутствие истцов: ", false_values=(False,))
    presence_defendant = BooleanField("Присутствие ответчиков: ", false_values=(False,))
    lawsuit_price = DecimalField("Цена предъявленного иска в рублях: ")
    court_result = SelectField("Результат суда: ", coerce=int)
    court_punishment = SelectMultipleField("Наказания по суду: ", coerce=int)
    compens = DecimalField("Сумма присуждённого возмещения в рублях: ")

    appeal = BooleanField("Обжалование: ", false_values=(False,))
    appeal_succ = BooleanField("Успешность обжалования: ", false_values=(False,))
    appeal_date = DateField("Дата подачи апелляции: ", default=datetime.date(1914, 1, 1))
    ap_decision_date = DateField("Дата решения апелляции: ", default=datetime.date(1914, 1, 1))
    decision_exec_date = DateField("Дата исполнения решения: ", default=datetime.date(1914, 1, 1))

    img_names = MultipleFileField("Изображения: ") #validators=[regexp(u'^[^/\\\\]\.jpg$')])
    doc_text = TextAreaField("Текст документа:")

    add_submit = SubmitField("Добавить документ")

class SearchForm(FlaskForm):
    reg_date_start = DateField("Время регистрации документа:")
    reg_date_end = DateField("")

    guberniya = SelectMultipleField("Губерния: ", coerce=int)
    uyezd = SelectMultipleField("Уезд: ", coerce=int)
    volost = SelectMultipleField("Волость: ", coerce=int)
    plaintiff_res_place = SelectMultipleField("Место жительства истца: ", coerce=int)
    defendant_res_place = SelectMultipleField("Место жительства ответчика: ", coerce=int)

    create_date_start = DateField("Дата подачи заявления:")
    create_date_end = DateField("")

    decision_date_start = DateField("Дата вынесения решения:")
    decision_date_end = DateField("")

    wait_time_start = IntegerField("Ожидание решения (в днях): ")
    wait_time_end = IntegerField("")

    theme = SelectMultipleField("Темы: ", coerce=int)

    #dec_book_num_start = IntegerField("Номер по книге решений: ")
    #dec_book_num_end = IntegerField("")

    presence_plaintiff = BooleanField("Присутствие истцов: ", false_values=(False,))
    presence_defendant = BooleanField("Присутствие ответчиков: ", false_values=(False,))

    #lawsuit_price_start = DecimalField("Цена предъявленного иска в рублях: ")
    #lawsuit_price_end = DecimalField("")

    court_result = SelectMultipleField("Результат суда: ", coerce=int)
    court_punishment = SelectMultipleField("Наказания по суду: ", coerce=int)

    #compens_start = DecimalField("Сумма присуждённого возмещения в рублях: ")
    #compens_end = DecimalField("")

    appeal = BooleanField("Обжалование: ", false_values=(False,))
    appeal_succ = BooleanField("Успешность обжалования: ", false_values=(False,))

    #appeal_date_start = DateField("Дата подачи апелляции: ")
    #appeal_date_end = DateField("")

    #ap_decision_date_start = DateField("Дата решения апелляции: ")
    #ap_decision_date_end = DateField("")

    decision_exec_date_start = DateField("Дата исполнения решения: ")
    decision_exec_date_end = DateField("")

    doc_text = BooleanField("Наличие текста: ", false_values=(False,))
    img_names = BooleanField("Наличие изображений: ", false_values=(False,))

    submit = SubmitField("Искать")

class AddPics(FlaskForm):
    imgs = MultipleFileField("", validators=[FileAllowed(['jpg', 'jpeg', 'png'], "Неверный формат!")])
    submit_pics = SubmitField("Добавить изображения")

class SemanticMarkup(FlaskForm):
    text = TextAreaField("Текст: ")
    sem_submit = SubmitField("Сохранить")