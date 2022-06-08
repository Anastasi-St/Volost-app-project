# -*- coding: utf-8 -*-

from flask import *
from config import Config
from werkzeug.utils import secure_filename
import datetime
import os, codecs, re
from natasha_stats import count_stats
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import aliased
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from forms import EditMeta, SearchForm, AddDoc, AddPics, SemanticMarkup

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    babel = Babel(app)
    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer(), primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        email = db.Column(db.String(255), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        first_name = db.Column(db.String(100), nullable=False, server_default='')
        last_name = db.Column(db.String(100), nullable=False, server_default='')

        roles = db.relationship('Role', secondary='user_roles')

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    class UserRoles(db.Model):
        __tablename__ = 'user_roles' #
        #id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

    Role()
    #UserRoles()

    class ReferenceBooks(db.Model):
        __tablename__ = 'reference_books'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_name = db.Column(db.String(255), nullable=False)
        ref_default = db.Column(db.Boolean(), server_default='1')

        def __str__(self):
            return self.ref_name

    class RefBooksElements(db.Model):
        __tablename__ = 'ref_books_elements'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_book = db.Column(db.Integer(), db.ForeignKey('reference_books.id'), nullable=False)
        ref_value = db.Column(db.String(255), nullable=False)
        ref_date = db.Column(db.DateTime(), nullable=False)

        def __str__(self):
            return self.ref_value

    class Documents(db.Model):
        __tablename__ = 'documents'
        id = db.Column(db.Integer(), primary_key=True)
        doc_name = db.Column(db.String(500), unique=True, nullable=False)
        reg_date = db.Column(db.DateTime(), nullable=False)
        owner = db.Column(db.ForeignKey('users.id'), nullable=True)  #, ondelete='CASCADE'))
        guberniya = db.Column(db.ForeignKey('ref_books_elements.id'), nullable=True)
        uyezd  = db.Column(db.ForeignKey('ref_books_elements.id'), nullable=True)
        volost = db.Column(db.ForeignKey('ref_books_elements.id'), nullable=True)
        plaintiff_res_place = db.Column(db.ForeignKey('ref_books_elements.id'), nullable=True)
        defendant_res_place = db.Column(db.ForeignKey('ref_books_elements.id'), nullable=True)
        create_date = db.Column(db.DateTime(), nullable=True)
        decision_date = db.Column(db.DateTime(), nullable=True)
        wait_time = db.Column(db.Integer(), nullable=True) # вычислить!
        dec_book_num = db.Column(db.Integer(), nullable=True)
        #???
        presence_plaintiff = db.Column(db.Boolean(), server_default='1', nullable=True)
        presence_defendant = db.Column(db.Boolean(), server_default='1', nullable=True)
        lawsuit_price = db.Column(db.Float(), nullable=True)
        court_result = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=True)
        #???
        # plaintiff_satisfied !
        # defendant_satisfied !
        compens = db.Column(db.Float(), nullable=True)
        appeal =  db.Column(db.Boolean(), nullable=True)
        appeal_succ = db.Column(db.Boolean(), nullable=True)
        appeal_date = db.Column(db.DateTime(), nullable=True)
        ap_decision_date = db.Column(db.DateTime(), nullable=True)
        ap_dec_time = db.Column(db.Integer(), nullable=True) # вычислить!
        decision_exec_date = db.Column(db.DateTime(), nullable=True)
        decision_exec_time = db.Column(db.Integer(), nullable=True) # вычислить!

        doc_text = db.Column(db.Text(), nullable=True)
        img_names = db.Column(db.String(100), nullable=True)

        theme = db.relationship('RefBooksElements', secondary='doc_themes', lazy='dynamic')
        court_punishment =  db.relationship('RefBooksElements', secondary='doc_court_punishments', lazy='dynamic')
        ref_doc_properties = db.relationship('RefBooksElements', secondary='ref_doc_properties', lazy='dynamic')

    class DocThemes(db.Model):
        __tablename__ = 'doc_themes'
        #id = db.Column(db.Integer(), primary_key=True)
        doc_id = db.Column(db.Integer(), db.ForeignKey('documents.id', ondelete='CASCADE'),
                           nullable=False, primary_key=True)
        theme_id = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id', ondelete='CASCADE'),
                             nullable=False, primary_key=True)

    class DocCourtPunishments(db.Model):
        __tablename__ = 'doc_court_punishments'
        #id = db.Column(db.Integer(), primary_key=True)
        doc_id = db.Column(db.Integer(), db.ForeignKey('documents.id', ondelete='CASCADE'),
                           nullable=False, primary_key=True)
        court_punishment_id = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id', ondelete='CASCADE'),
                                        nullable=False, primary_key=True)

    class DocumentsFiles(db.Model):
        __tablename__ = 'documents_files'
        id = db.Column(db.Integer(), primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        load_date = db.Column(db.DateTime(), nullable=False)
        document = db.Column(db.Integer(), nullable=False) #db.ForeignKey('documents.id', ondelete='CASCADE'))
        filetype = db.Column(ENUM('jpg', 'jpeg', 'png', name='file_type', create_type=False), nullable=False)

    class ActivityLog(db.Model):
        __tablename__ = 'activity_log'
        id =  db.Column(db.Integer(), primary_key=True)
        user = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
        datetime = db.Column(db.DateTime(), nullable=False)
        document = db.Column(db.Integer(), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
        doc_type = db.Column(ENUM('edit_meta', 'edit_text', 'edit_pics', 'add_doc', 'delete_doc',
                                  name='act_type', create_type=False), nullable=False) # переименовала!!

    class Participants(db.Model):
        __tablename__ = 'participants'
        id =  db.Column(db.Integer(), primary_key=True)
        id_doc = db.Column(db.Integer(), db.ForeignKey('documents.id'), nullable=False)
        partic_type = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=False)
        partic_kind = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=False)
        partic_num = db.Column(db.Integer(), server_default='0')

    class RefDocProperties(db.Model): # RELATIONS!
        __tablename__ = 'ref_doc_properties'
        id =  db.Column(db.Integer(), primary_key=True)
        doc = db.Column(db.Integer(), db.ForeignKey('documents.id'), nullable=False)
        ref_element = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=False) # переименовала!!
        #ref_book = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.ref_book'), nullable=False)

    class ResearchArticle(db.Model):
        __tablename__ = 'research_article'
        id = db.Column(db.Integer(), primary_key=True)
        title = db.Column(db.String(), nullable=False)
        source = db.Column(db.String(), nullable=True)
        preview = db.Column(db.Text(), nullable=True)
        thumbnail = db.Column(db.String(), nullable=True)
        article = db.Column(db.String(), nullable=True)

    user_manager = UserManager(app, db, User)
    db.create_all()

    def calculate_waiting(doc):
        if doc.decision_date and doc.create_date:
            doc.wait_time = (doc.decision_date - doc.create_date).days
        if doc.ap_decision_date and doc.appeal_date:
            doc.ap_dec_time = (doc.ap_decision_date - doc.appeal_date).days
        if doc.decision_exec_date and doc.decision_date:
            doc.decision_exec_time = (doc.decision_exec_date - doc.decision_date).days
        db.session.commit()

    def fill_docfiles(doc):
        if doc.img_names:
            filenames = doc.img_names.split(', ')
            for name in filenames:
                doc_file = DocumentsFiles()
                doc_file.filename = name
                doc_file.load_date = datetime.datetime(2022, 4, 5)
                doc_file.document = doc.id
                doc_file.filetype = name.split('.')[-1]
                db.session.add(doc_file)
                db.session.commit()

    th_names = ['Дата регистрации документа в базе данных', 'Губерния', 'Уезд', 'Волость',
                'Место жительства истца', 'Место жительства ответчика', 'Дата подачи заявления', 'Дата вынесения решения',
                'Время ожидания, дни', 'Темы',
                'Номер по книге решений суда', 'Присутствие истца', 'Присутствие ответчика',
                'Цена предъявленного иска в рублях', 'Результат суда', 'Наказания по суду',
                'Сумма присуждённого возмещения в рублях',
                'Обжаловано', 'Обжалование успешно', 'Дата подачи апелляции', 'Дата решения по апелляции',
                'Время ожидания решения апелляции, дни', 'Дата исполнения решения', 'Время ожидания решения, дни']
    not_displayed = ['id', 'doc_name', 'owner', 'doc_text', 'img_names']
    column_names = [x for x in Documents.__table__.columns.keys() if x not in not_displayed]
    column_names.insert(column_names.index('dec_book_num'), 'themes')
    column_names.insert(column_names.index('compens'), 'court_punishments')
    column_dict = dict(zip(column_names, th_names))
    #print(column_dict)


    def get_all_docs():
        plaintiff_res = aliased(RefBooksElements)
        defendant_res = aliased(RefBooksElements)
        guberniya = aliased(RefBooksElements)
        uyezd = aliased(RefBooksElements)
        volost = aliased(RefBooksElements)
        court_result = aliased(RefBooksElements)
        #themes = aliased(RefBooksElements)

        #print(Documents.query.with_entities(Documents.id, Documents.doc_name).all())

        docs_test = Documents.query.with_entities(Documents.id,
                                                  Documents.doc_name,
                                                  Documents.reg_date,
                                                  plaintiff_res.ref_value.label('plaintiff_res_place'),
                                                  defendant_res.ref_value.label('defendant_res_place'),
                                                  guberniya.ref_value.label('guberniya'),
                                                  uyezd.ref_value.label('uyezd'),
                                                  volost.ref_value.label('volost'),
                                                  Documents.create_date,
                                                  Documents.decision_date,
                                                  Documents.wait_time,
                                                  Documents.dec_book_num,
                                                  Documents.presence_plaintiff,
                                                  Documents.presence_defendant,
                                                  Documents.lawsuit_price,
                                                  court_result.ref_value.label('court_result'),
                                                  Documents.compens,
                                                  Documents.appeal,
                                                  Documents.appeal_succ,
                                                  Documents.appeal_date,
                                                  Documents.ap_decision_date,
                                                  Documents.ap_dec_time,
                                                  Documents.decision_exec_date,
                                                  Documents.decision_exec_time,
                                                  Documents.doc_text, # change!!
                                                  Documents.img_names)\
            .join(guberniya, guberniya.id == Documents.guberniya, isouter=True)\
            .join(uyezd, uyezd.id == Documents.uyezd, isouter=True)\
            .join(volost, volost.id == Documents.volost, isouter=True)\
            .join(plaintiff_res, plaintiff_res.id == Documents.plaintiff_res_place, isouter=True)\
            .join(defendant_res, defendant_res.id == Documents.defendant_res_place, isouter=True)\
            .join(court_result, court_result.id == Documents.court_result, isouter=True)\
            .all()
            #.join(DocThemes, isouter=True)\
            #.join(themes, isouter=True)\
            #.all()
            #.join(DocThemes, DocThemes.doc_id == Documents.id)\
            #.join(themes)\
            #.all()

        docs_themes = RefBooksElements.query.with_entities(Documents.id, RefBooksElements.ref_value)\
                         .join(DocThemes, DocThemes.theme_id == RefBooksElements.id)\
                         .join(Documents, DocThemes.doc_id == Documents.id).all()

        docs_punishments = RefBooksElements.query.with_entities(Documents.id, RefBooksElements.ref_value) \
                        .join(DocCourtPunishments, DocCourtPunishments.court_punishment_id == RefBooksElements.id) \
                        .join(Documents, DocCourtPunishments.doc_id == Documents.id).all()

        return docs_test, docs_themes, docs_punishments


    def get_themes_puns():
        docs, docs_th, docs_p = get_all_docs()
        ids = [doc['id'] for doc in docs]
        def get_lists(d, name):
            new_d = {}
            new_l = []
            for doc in d:
                if doc['id'] not in new_d:
                    new_d[doc['id']] = []
                new_d[doc['id']].append(doc['ref_value'])
            new_dd = {}
            for id in ids:
                if id in new_d.keys():
                    new_dd[id] = new_d[id]
                else:
                    new_dd[id] = []
            for id, val in zip(new_dd.keys(), new_dd.values()):
                new_l.append({'id': id, name: ', '.join(val)})
            return new_l

        theme_dicts = get_lists(docs_th, 'themes')
        puns_dicts = get_lists(docs_p, 'court_punishments')

        return theme_dicts, puns_dicts

    def query_to_dict(query_res):
        try:
            return [dict((col, getattr(obj, col)) for col in list(obj.keys())) for obj in query_res]
        except TypeError:
            return dict((col, getattr(query_res, col)) for col in query_res.__table__.columns.keys())

    #def query_to_list(query_res):
    #    return [item[0] for item in query_res]

    def ref_elements_list(n):
        query = RefBooksElements.query.with_entities(RefBooksElements.id,
                                                     RefBooksElements.ref_value).filter_by(ref_book=n).all()
        els_list = [tuple(list(item)) for item in query]
        return els_list

    def intersect(list1, list2):
        intersection = [val for val in list1 if val in list2]
        return intersection

    # Поля для форм
    fields = ['doc_name', 'create_date', 'decision_date', 'dec_book_num',
              'presence_plaintiff', 'presence_defendant', 'lawsuit_price',
              'compens', 'appeal', 'appeal_succ', 'appeal_date',
              'ap_decision_date', 'decision_exec_date']
    dates = ['create_date', 'decision_date', 'appeal_date', 'ap_decision_date', 'decision_exec_date']
    choices = {'guberniya': 7, 'uyezd': 8 , 'volost': 9, 'plaintiff_res_place': 10, 'defendant_res_place': 10,
               'court_result': 3, 'theme': 2, 'court_punishment': 4}
    multiselect = ['theme', 'court_punishment']
    checkboxes = ["presence_plaintiff", "presence_defendant", "appeal", "appeal_succ"]
    checkboxes_search = ['img_names', 'doc_text']
    diff_fields = ["csrf_token", "doc_name", "submit"]
    waits = ['wait_time', 'ap_dec_time', 'decision_exec_time']

    roles_trans = [('#E79C9C', 'Содержание жалобы'),
                   ('#FFC69C', 'Формулировка дела'),
                   ('#FFE79C', 'Объяснение истца(ов)'),
                   ('#B5D6A5', 'Объяснение/возражение ответчика(ов)'),
                   ('#A5C6CE', 'Показания свидетелей'),
                   ('#9CC6EF', 'Решение суда'),
                   ('#B5A5D6', 'Подписи судей'),
                   ('#D6A5BD', 'Расписка об ознакомении с решением'),
                   ('#E76363', 'Время отмены или утверждения решения'),
                   ('#F7AD6B', 'Статус исполнения решения'),
                   ('#FF9C00', 'Истец'),
                   ('#FFFF00', 'Ответчик'),
                   ('#00FF00', 'Свидетель'),
                   ('#00FFFF', 'Судья'),
                   ('#CEC6CE', 'Причастный (роль не определена)')]

    superior_roles = ['Experienced_Researcher', 'Admin', 'Superadmin']

    @app.route('/', methods=['GET', 'POST'])
    def index():
        docs, docs_themes, docs_punishments = get_all_docs()
        #docs_list = [dict((col, getattr(doc, col)) for col in doc.__table__.columns.keys()) for doc in docs]
        all_docs = Documents.query.all()
        docs_list = query_to_dict(docs)
        docs_themes, docs_punishments = get_themes_puns()

        for i in range(len(docs_themes)):
            docs_list[i].update(docs_themes[i])
            docs_list[i].update(docs_punishments[i])

        if request.method == 'POST':
            form = SearchForm(request.form)

            def select_docs(all_docs, form):
                fields = [field for field in form if field.name not in diff_fields]
                values = []
                id_list = []
                for doc in all_docs:
                    val = [doc.id]
                    for field in fields:
                        if field.name in multiselect:
                            els = [el.id for el in getattr(doc, field.name)]
                            val.append((els, field.data))
                        elif field.name in checkboxes_search:
                            if getattr(doc, field.name):
                                val.append((True, field.data))
                            else:
                                val.append((False, field.data))
                        else:
                            val.append((getattr(doc, field.name), field.data))
                    values.append(val)
                for el in values:
                    temp_list = []
                    count1 = 0
                    count2 = 0
                    for doc_val, form_val in el[1:]:
                        if form_val:
                            count1 += 1
                            if (type(doc_val) == list and intersect(doc_val, form_val)) \
                                or (type(doc_val) == int and doc_val in form_val) \
                                or (doc_val == True and form_val == doc_val):
                                    count2 += 1
                    #print(count1, count2)
                    if count1 == count2:
                        id_list.append(el[0])

                new_docs_list = [doc for doc in docs_list if doc['id'] in id_list ]
                #print(id_list)
                return new_docs_list
            if len(list(request.form.to_dict().keys())) > 2:
                docs_list = select_docs(all_docs, form)
        else:
            form = SearchForm()

        def set_search_form(form):
            for field in form:
                if field.name in choices:
                    ch = ref_elements_list(choices[field.name])
                    field.choices = ch

        set_search_form(form)

        return render_template('index.html',
                               title="Добро пожаловать!",
                               column_dict=column_dict,
                               docs_list=docs_list,
                               choices=choices,
                               diff_fields=diff_fields,
                               checkboxes=checkboxes,
                               checkboxes_search=checkboxes_search,
                               dates=dates,
                               waits=waits,
                               form=form)

    @app.route('/<int:id>', methods=['GET', 'POST'])
    def doc_page(id):
        doc = Documents.query.filter_by(id=id).first()

        if not doc:
            return redirect('/no_doc/'+str(id))

        diff_fields = ['csrf_token', 'submit']
        active_button = False

        if current_user.is_authenticated:
            roles = set([role.name for role in current_user.roles])
            if doc.owner == current_user.id or roles.issubset(set(superior_roles)):
                active_button = True

        if request.method == "POST":

            if 'editordata' in request.form:
                new_doc_text = request.form.get('editordata')
                #print(new_doc_text)
                doc.doc_text = new_doc_text
                new_action = ActivityLog(user=current_user.id,
                                         datetime=datetime.datetime.now(),
                                         document=doc.id,
                                         doc_type='edit_text')
                db.session.add(new_action)
                db.session.commit()

            elif 'doc_name' in request.form:
                form = EditMeta(request.form)

                #if form.validate():
                for field in form:
                    if field.name not in diff_fields:
                        if type(field.data) != list:
                            if getattr(doc, field.name) == field.data:
                                continue
                            else:
                                #print('вместо', str(getattr(doc, field.name)), '—', field.name+' —   '+str(field.data))
                                setattr(doc, field.name, field.data)
                        else:
                            ids = [el.id for el in getattr(doc, field.name)]
                            #print('айдис —', field.name, ids)
                            if field.data == ids:
                                #print('ничего не поменялось')
                                continue
                            else:
                                for idd in ids:
                                    if idd in field.data:
                                        continue
                                    else:
                                        el = RefBooksElements.query.filter_by(id=idd).first()
                                        getattr(doc, field.name).remove(el)
                                        #db.session.commit()
                                        #print('удалили', field.name, el)

                                for idd in field.data:
                                    if idd in ids:
                                        continue
                                    else:
                                        el = RefBooksElements.query.filter_by(id=idd).first()
                                        getattr(doc, field.name).append(el)
                                        db.session.merge(doc)
                                        #db.session.commit()
                                        #print('добавили', field.name, el)
                new_action = ActivityLog(user=current_user.id,
                                         datetime=datetime.datetime.now(),
                                         document=doc.id,
                                         doc_type='edit_meta')
                db.session.add(new_action)
                db.session.commit()
        if doc:
            doc_dict = query_to_dict(doc)
            doc_files = DocumentsFiles.query.filter_by(document=id).all()
            title = doc.doc_name
        else:
            title = "Документ не найден"
            doc_dict = {}
            doc_files = ''

        return render_template('doc_page.html',
                               doc_dict=doc_dict,
                               doc_files=doc_files,
                               title=title,
                               active_button=active_button,
                               active_text=True)

    @app.route('/<int:id>/imgs')
    def imgs(id):
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        doc_dict = query_to_dict(doc)
        doc_files = DocumentsFiles.query.filter_by(document=id).all()
        active_button = False

        if current_user.is_authenticated:
            roles = set([role.name for role in current_user.roles])
            if doc.owner == current_user.id or roles.issubset(set(superior_roles)):
                active_button = True
#
        return render_template('doc_page_imgs.html',
                               title=doc.doc_name,
                               doc_dict=doc_dict,
                               doc_files=doc_files,
                               active_img=True,
                               active_button=active_button)

    @app.route('/text/<int:id>', methods=['GET', 'POST'])
    @roles_required()
    def text(id):
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        roles = set([role.name for role in current_user.roles])
        if doc.owner == current_user.id or roles.issubset(set(superior_roles)):
            doc_dict = query_to_dict(doc)
            return render_template('edit_text.html',
                                   doc_dict=doc_dict,
                                   title="Редактировать текст")
        else:
            return redirect('/access_error/'+str(id))

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @roles_required()
    def edit(id):
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        form = EditMeta()
        roles = set([role.name for role in current_user.roles])

        if doc.owner == current_user.id or roles.issubset(set(superior_roles)):#

            def set_form_data(form):
                for field in form:
                    if field.name in fields:
                        field.data = getattr(doc, field.name)
                    elif field.name in choices:
                        ch = ref_elements_list(choices[field.name])
                        if field.name in choices and field.name not in multiselect:
                            ch.append((False, 'Ничего не выбрано'))
                        field.choices = ch
                        if field.name in multiselect:
                            set_values = []
                            for el in getattr(doc, field.name):
                                new = RefBooksElements.query.with_entities(RefBooksElements.id,
                                                                           RefBooksElements.ref_value).filter_by(id=el.id).first()
                                set_values.append(new[0])
                            field.data = set_values
                        else:
                            if getattr(doc, field.name) == None:
                                field.data = False
                            else:
                                field.data = getattr(doc, field.name)

            doc_dict = query_to_dict(doc)
            set_form_data(form)

            return render_template('edit_meta.html',
                                   title="Редактировать метаданные",
                                   doc_dict=doc_dict,
                                   form=form,
                                   checkboxes=checkboxes,
                                   diff_fields=diff_fields,
                                   multiselect=multiselect,
                                   choices=choices)
        else:
            return redirect('/access_error/'+str(id))

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @app.route('/add_doc', methods=['POST', 'GET'])
    @roles_required()
    def add_doc():
        docs = Documents.query.all()
        form = AddDoc()
        diff_fields_new = ["csrf_token", "doc_name", "img_names", "doc_text", "add_submit"]
        def set_form_choices(form):
            for field in form:
                if field.name in choices:
                    ch = ref_elements_list(choices[field.name])
                    if field.name not in multiselect:
                        ch.append((False, "Ничего не выбрано"))
                    field.choices = ch
                    if field.name not in multiselect and getattr(form, field.name).data == None:
                        setattr(getattr(form, field.name), 'data', False)
        set_form_choices(form)

        if request.method == "POST": # and form.validate_on_submit():
            images = os.listdir('static/images/doc_images')
            doc_form = AddDoc(request.form)

            if 'img_names' in request.files:
                files = request.files.getlist('img_names')
                for file in files:
                    if len(files) == 1 and file.filename == '':
                        pass
                    elif file and allowed_file(file.filename):
                        pass
                    else:
                        flash("Вы прикрепили файлы неверного формата. Допустимые форматы: .jpg, .jpeg, .png",
                              'warning')
                        return render_template('add_doc.html',
                                               form=form,
                                               docs=docs,
                                               diff_fields=diff_fields_new,
                                               choices=choices,
                                               multiselect=multiselect,
                                               checkboxes=checkboxes,
                                               title='Новый документ')

            new_doc = Documents(doc_name=doc_form.doc_name.data)
            new_doc.reg_date = datetime.datetime.now()
            new_doc.owner = current_user.id
            db.session.add(new_doc)
            db.session.commit()

            for field in doc_form:
                if field.name not in ['csrf_token', 'doc_name', 'add_submit']:
                    if field.name in multiselect:
                        for el_id in field.data:
                            new_el = RefBooksElements.query.filter_by(id=el_id).first()
                            getattr(new_doc, field.name).append(new_el)
                    elif field.name == 'img_names':
                        files = request.files.getlist('img_names')
                        file_names = ', '.join([file.filename for file in files])
                        for file in files:
                            if not file_names:
                                setattr(new_doc, field.name, None)
                                continue
                            else:
                                filename = secure_filename(file.filename)
                                if file.filename not in images:
                                    #print(filename, 'saved')
                                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

                                new_file = DocumentsFiles()
                                new_file.filename = filename
                                new_file.document = new_doc.id
                                new_file.load_date = datetime.datetime.now()
                                new_file.filetype = file.filename.split('.')[-1]

                                db.session.add(new_file)
                        if file_names:
                            setattr(new_doc, field.name, file_names)
                    elif field.data != '':
                        setattr(new_doc, field.name, field.data)
                    else:
                        setattr(new_doc, field.name, None)

            #db.session.add(new_doc)
            #db.session.commit()

            new_action = ActivityLog(user=current_user.id,
                                     datetime=datetime.datetime.now(),
                                     document=new_doc.id,
                                     doc_type='add_doc')

            db.session.add(new_action)
            db.session.commit()

            return redirect('/'+str(new_doc.id))

        return render_template('add_doc.html',
                               form=form,
                               docs=docs,
                               diff_fields=diff_fields_new,
                               choices=choices,
                               multiselect=multiselect,
                               checkboxes=checkboxes,
                               title='Новый документ')

    @app.route('/pics/<int:id>', methods=['POST', 'GET'])
    @roles_required()
    def edit_pics(id):
        doc_files = DocumentsFiles.query\
            .with_entities(DocumentsFiles.document, DocumentsFiles.filename)\
            .filter_by(document=id).all()
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        form = AddPics()

        roles = set([role.name for role in current_user.roles])

        if doc.owner == current_user.id or roles.issubset(set(superior_roles)):

            if request.method == 'POST':
                form = AddPics(request.form)

                if 'imgs' in request.files:
                    files = request.files.getlist('imgs')
                    #print(files)
                    for file in files:
                        if len(files) == 1 and file.filename == '':
                            flash("Вы не выбрали ни один файл", 'warning')
                            return render_template('edit_pics.html',
                                                   doc_files=doc_files,
                                                   doc=doc,
                                                   form=form,
                                                   title="Редактировать изображения")
                        elif file.filename in doc.img_names:
                            flash("У документа уже есть файл "+file.filename, 'warning')
                            return render_template('edit_pics.html',
                                                   doc_files=doc_files,
                                                   doc=doc,
                                                   form=form,
                                                   title="Редактировать изображения")
                        elif file and allowed_file(file.filename):
                            pass
                        else:
                            flash("Вы прикрепили файлы неверного формата. Допустимые форматы: .jpg, .jpeg, .png",
                                  'warning')
                            return render_template('edit_pics.html',
                                                   doc_files=doc_files,
                                                   doc=doc,
                                                   form=form,
                                                   title="Редактировать изображения")

                images = os.listdir('static/images/doc_images')
                files = request.files.getlist('imgs')
                for file in files:
                    filename = secure_filename(file.filename)
                    #if file.filename not in images:
                        #file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                    new_file = DocumentsFiles(filename=filename,
                                              load_date=datetime.datetime.now(),
                                              document=doc.id,
                                              filetype=filename.split('.')[-1])
                    #print(new_file.filename, new_file.load_date, new_file.document, new_file.filetype)
                    #db.session.add(new_file)
                #print(doc.img_names)
                doc.img_names += ', '+', '.join([file.filename for file in files])
                #print(doc.img_names)
                #db.session.commit()
        else:
            return redirect('/access_error/'+str(id))

        return render_template('edit_pics.html',
                               doc_files=doc_files,
                               doc=doc,
                               form=form,
                               title="Редактировать изображения")

    @app.route('/semantic_markup/<int:id>', methods=['POST', 'GET'])
    @roles_required(superior_roles)
    def semantic_markup(id):
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        form = SemanticMarkup()
        color_roles = [('#E79C9C', 'complaint_content'),
                       ('#FFC69C', 'case_statement'),
                       ('#FFE79C', 'plaintiff_explanation'),
                       ('#B5D6A5', 'defendant_explanation_objection'),
                       ('#A5C6CE', 'witness_testimony'),
                       ('#9CC6EF', 'court_decision'),
                       ('#B5A5D6', 'judges_signatures'),
                       ('#D6A5BD', 'decision_hearing_rec'),
                       ('#E76363', 'decision_approval_cancellation_date'),
                       ('#F7AD6B', 'decision_execution_status'),
                       ('#FF9C00', 'plaintiff'),
                       ('#FFFF00', 'defendant'),
                       ('#00FF00', 'witness'),
                       ('#00FFFF', 'judge'),
                       ('#CEC6CE', 'involved_no_role')]

        def to_hex(match):
            gr = match.group(1)
            tpl = tuple([int(n) for n in gr.split(', ')])
            result = '#%02x%02x%02x' % tpl
            return result.upper()

        roles = set([role.name for role in current_user.roles])
        if doc.owner == current_user.id or roles.issubset(set(superior_roles)):
            html_path = 'semant_html/html_'+str(id)+'.txt'
            clean_path = 'clean_texts/clean_text_'+str(id)+'.txt'
            xml_path = 'semant_xml/xml_'+str(id)+'.xml'
            if not os.path.exists(html_path):
                with codecs.open(clean_path, 'r', encoding='windows-1251') as doc_text:
                    doc_text = doc_text.read().replace('\n', '<br>')
                    form.text.data = doc_text
            else:
                with codecs.open(html_path, 'r', encoding='utf-8') as doc_markup:
                    doc_markup = doc_markup.read()
                    form.text.data = doc_markup

            if request.method == 'POST':
                form = SemanticMarkup(request.form)
                text = form.text.data

                def html_to_xml(html_txt):
                    if 'span' in html_txt:
                        new_text = re.sub(r'rgb\((.*?)\)', to_hex, html_txt, flags=re.I)
                        for col, val in color_roles:
                            new_text = new_text.replace('style="background-color: '+col+';"', 'type="'+val+'"')
                        new_text = new_text.replace('span', 'semantic')
                        new_text = '<?xml version="1.0" encoding="UTF-8"?><text>'+new_text+'</text>'
                        new_text = new_text.replace('<br>', '') #&#xA;
                        new_text = new_text.replace('&nbsp;', '&#xA0;')
                        new_text = re.sub(r'(</semantic>|<text>)(.*?)<', r'\g<1><plain_text>'+r'\g<2>'+'</plain_text><', new_text)
                        new_text = new_text.replace('<plain_text></plain_text>', '')
                    else:
                        new_text = '<?xml version="1.0" encoding="UTF-8"?><text><plain_text>'+html_txt+'</plain_text></text>'
                        new_text = new_text.replace('<br>', '') #&#xA;
                    return new_text

                if not os.path.exists(html_path):
                    with codecs.open(html_path, 'w', encoding='utf-8') as html:
                        html.write(text)
                    with codecs.open(xml_path, 'w', encoding='utf-8') as xml:
                        #to_xml = etree.fromstring(html_to_xml(text).encode('utf-8'))
                        #pretty_xml = etree.tostring(to_xml, pretty_print=True).decode('utf-8')
                        xml.write(html_to_xml(text))
                else:
                    with codecs.open(html_path, 'r+', encoding='utf-8') as html:
                        html_text = html.read()
                        if text != html_text:
                            with codecs.open(html_path, 'w', encoding='utf-8') as html:
                                html.write(text)
                            with codecs.open(xml_path, 'w', encoding='utf-8') as xml:
                                #to_xml = etree.fromstring(html_to_xml(text).encode('utf-8'))
                                #pretty_xml = etree.tostring(to_xml, pretty_print=True).decode('utf-8')
                                xml.write(html_to_xml(text))
                return redirect('/'+str(id))
        else:
            return redirect('/access_error/'+str(id))
        return render_template('semantic_markup.html',
                               title=doc.doc_name,
                               doc=doc,
                               form=form,
                               roles_trans=roles_trans)

    @app.route('/<int:id>/sem')
    def sem(id):
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            return redirect('/no_doc/'+str(id))
        doc_dict = query_to_dict(doc)
        active_button = False
        message = ''

        if current_user.is_authenticated:
            roles = set([role.name for role in current_user.roles])
            if doc.owner == current_user.id or roles.issubset(set(superior_roles)):
                active_button = True

        html_path = 'semant_html/html_'+str(id)+'.txt'

        if os.path.exists(html_path):
            with codecs.open(html_path, 'r', encoding='utf-8') as html:
                markup = html.read()
        else:
            markup = ''
            message = 'У данного документа ещё нет семантической разметки'

        return render_template('doc_page_sem.html',
                               title=doc.doc_name,
                               markup=markup,
                               message=message,
                               doc_dict=doc_dict,
                               active_sem=True,
                               active_button=active_button,
                               roles_trans=roles_trans)

    @app.route('/<int:id>/sem/xml')
    def download_xml(id):
        filename = 'xml_'+str(id)+'.xml'
        path = 'semant_xml/'
        if not os.path.exists(path+filename):
            print(path+filename)
            return  redirect('/'+str(id)+'/sem')
        return send_from_directory(path, filename, as_attachment=True)

    @app.route('/access_error/<int:id>')
    def access_error(id):
        return render_template('access_error.html',
                               id=id,
                               title='Доступ ограничен')

    @app.route('/no_doc/<int:id>')
    def no_doc(id):
        return render_template('no_doc.html',
                               id=id,
                               title="Документ не найден")

    wcount, scount = count_stats()
    @app.route('/linguistic_info')
    def linguistic_info():
        return render_template('linguistic_info.html',
                               wcount=wcount,
                               scount=scount,
                               title="Взгляд лингвиста")

    @app.route('/research')
    def research():
        articles = ResearchArticle.query.all()
        return render_template('research.html',
                               title="Исследования",
                               articles=articles)
    @app.route('/research/article/<int:id>')
    def article(id):
        article = ResearchArticle.query.filter_by(id=id).first()
        if not article:
            return redirect('/')
        art_path = 'articles/'+str(id)+'.txt'
        if os.path.exists(art_path):
            with codecs.open(art_path, 'r', encoding='windows-1251') as art:
                article_text = art.read()
        else:
            return redirect('/')
        return render_template('article.html',
                               title="Исследования",
                               article=article,
                               article_text=article_text)

    @app.route('/about_project')
    def about_project():
        return render_template('about_project.html',
                               title="О проекте")

    @app.route('/ref_books')
    @roles_required(superior_roles)
    def ref_books():
        ref_books = ReferenceBooks.query.all()
        return render_template('ref_books.html',
                               title="Управление справочниками",
                               ref_books=ref_books)

    @app.route('/ref_books/<int:id>', methods=['GET', 'POST'])
    @roles_required(superior_roles)
    def ref_book_edit(id):
        ref_book = RefBooksElements.query.filter_by(ref_book=id).all()
        ref_book_name = ReferenceBooks.query.filter_by(id=id).first()
        if not ref_book:
            return redirect('/no_book/'+str(id))
        if request.method == 'POST':
            for field in request.form:
                field_data = request.form.get(field)
                el_id = int(field)
                ref_el = RefBooksElements.query.filter_by(id=el_id).first()
                if ref_el.ref_value == field_data:
                    continue
                else:
                    ref_el.ref_value = field_data
            db.session.commit()
        return render_template('ref_book_edit.html',
                               title="Управление справочниками — "+ref_book_name.ref_name,
                               ref_book=ref_book,
                               ref_book_name=ref_book_name)

    @app.route('/ref_books/<int:id>/add_el', methods=['GET', 'POST'])
    @roles_required(superior_roles)
    def add_ref_el(id):
        ref_book = ReferenceBooks.query.filter_by(id=id).first()
        if not ref_book:
            return redirect('/no_book/'+str(id))
        if request.method == 'POST':
            new_ref_el = RefBooksElements()
            new_ref_el.ref_value = request.form.get('ref_value')
            db.session.add(new_ref_el)
            db.session.commit()

            return redirect('/ref_books/'+str(id))
        return render_template('add_ref_el.html',
                               title="Новый элмент справочника "+ref_book.ref_name,
                               ref_book=ref_book)

    @app.route('/no_book/<int:id>')
    def no_book(id):
        return render_template('no_book.html',
                               title="Справочник не найден",
                               id=id)


    @app.route('/activity_log')
    @login_required
    def activity_log():
        actions = ActivityLog.query.with_entities(ActivityLog.id,
                                                  User.first_name.label('user_name'),
                                                  User.last_name.label('user_lastname'),
                                                  Documents.doc_name.label('document_name'),
                                                  Documents.id.label('document_id'),
                                                  ActivityLog.datetime,
                                                  ActivityLog.doc_type
                                                  )\
        .join(User, User.id == ActivityLog.user)\
        .join(Documents, Documents.id == ActivityLog.document)\
        .all()
        #actions = [query_to_dict(action) for action in actions]
        #print(actions)
        actions_dct = {'edit_meta': 'Редактирование метаданных',
                       'edit_text': 'Редактирование текста',
                       'edit_pics': 'Редактирование изображений',
                       'add_doc': 'Добавление нового документа',
                       'delete_doc': 'Удаление документа'}
        return render_template('activity_log.html',
                               title="Журнал действий",
                               actions=actions,
                               actions_dct=actions_dct)

    return app

if __name__ == '__main__':
    app = create_app()
    #app.jinja_env.add_extension('jinja2.ext.do')
    app.run()
