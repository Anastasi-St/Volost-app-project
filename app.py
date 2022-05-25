# -*- coding: utf-8 -*-

from flask import *
from config import Config
import datetime
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy import and_
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
import itertools
from forms import EditMeta, SearchForm

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    babel = Babel(app)
    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
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
        __tablename__ = 'user_roles'
        #id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

    class ReferenceBooks(db.Model):
        __tablename__ = 'reference_books'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_name = db.Column(db.String(255), nullable=False)
        ref_default = db.Column(db.Boolean(), server_default='1')

    class RefBooksElements(db.Model):
        __tablename__ = 'ref_books_elements'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_book = db.Column(db.Integer(), db.ForeignKey('reference_books.id'), nullable=False)
        ref_value = db.Column(db.String(255), nullable=False)
        ref_date = db.Column(db.DateTime(), nullable=False)

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
        document = db.Column(db.Integer(), db.ForeignKey('documents.id'), nullable=False)
        filetype = db.Column(db.String(100), nullable=False)

    class ActivityLog(db.Model):
        __tablename__ = 'activity_log'
        id =  db.Column(db.Integer(), primary_key=True)
        user = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
        datetime = db.Column(db.DateTime(), nullable=False)
        document = db.Column(db.Integer(), db.ForeignKey('documents.id'), nullable=False)
        doc_type = db.Column(db.String(100), nullable=False) # переименовала!!

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


    user_manager = UserManager(app, db, User)
    db.create_all()

    def calculate_waiting():
        for doc in Documents.query.all():
            if doc.decision_date and doc.create_date:
                doc.wait_time = (doc.decision_date - doc.create_date).days
            if doc.ap_decision_date and doc.appeal_date:
                doc.ap_dec_time = (doc.ap_decision_date - doc.appeal_date).days
            if doc.decision_exec_date and doc.decision_date:
                doc.decision_exec_time = (doc.decision_exec_date - doc.decision_date).days
        db.session.commit()

    #calculate_waiting()


    #for text in Documents.query.with_entities(Documents.id, Documents.doc_text).all():
    #    if text.doc_text:
    #        with codecs.open("doc_texts\\text_"+str(text.id)+".txt", 'w', encoding='windows-1251') as f:
    #            f.write(text.doc_text)



#if not User.query.filter(User.email == 'member1@example.com').first():
    #    user = User(email='member1@example.com',
    #                email_confirmed_at=datetime.datetime.utcnow(),
    #                password=user_manager.hash_password('Password1'),
    #                first_name="Василий",
    #                last_name="Иванов",)
    #    user.roles.append(Role(name="Beginner_Researcher"))
    #    db.session.add(user)
    #    db.session.commit()

    #if not User.query.filter(User.email == 'member2@example.com').first():
    #    user = User(email='member2@example.com',
    #                email_confirmed_at=datetime.datetime.utcnow(),
    #                password=user_manager.hash_password('Password1'),
    #                first_name="Иван",
    #                last_name="Васильев",)
    #    user.roles.append(Role(name="Experienced_Researcher"))
    #    db.session.add(user)
    #    db.session.commit()

        # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    #if not User.query.filter(User.email == 'admin@example.com').first():
    #    user = User(email='admin@example.com',
    #                email_confirmed_at=datetime.datetime.utcnow(),
    #                password=user_manager.hash_password('Password1'),
    #                first_name="Николай",
    #                last_name="Николаев",)
    #    user.roles.append(Role(name='Admin'))
    #    db.session.add(user)
    #    db.session.commit()

    #def add_themes_punishments():
    #    doc = Documents(doc_name='test',
    #                    reg_date=datetime.datetime.utcnow(),)
    #    doc.theme.append(RefBooksElements.query.filter_by(ref_value='потрава').first())
    #    doc.court_punishment.append(RefBooksElements.query.filter_by(ref_value='штраф').first())
    #    db.session.add(doc)
    #    db.session.commit()


    #def get_roles(cur_user):
    #    roles_list = cur_user.roles
    #    user_roles = []
    #    for role in roles_list:
    #        user_roles.append(Role.query.filter_by(id=role.id).first().name)
    #    return user_roles

    #def get_text():
    #    doc = ''
    #    warning = ''
    #    if request.method == "GET":
    #        doc_id = request.args.get('doc_id')
    #        if doc_id:
    #            doc_id = int(doc_id)
    #            doc = Documents.query.filter_by(id=doc_id).first()
    #            if not doc:
    #                warning = "Текста с id "+str(doc_id)+" нет в базе данных"
    #                doc = ''
    #   return doc, warning

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
        themes = aliased(RefBooksElements)

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
        warning = ''
        doc = Documents.query.filter_by(id=id).first()
        diff_fields = ['csrf_token', 'submit']
        if request.method == "POST":
            if 'editordata' in request.form:
                new_doc_text = request.form.get('editordata')
                #print(new_doc_text)
                doc.doc_text = new_doc_text
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

                    db.session.commit()
        if doc:
            doc_dict = query_to_dict(doc)
            title = doc.doc_name
        else:
            warning = "Документа с ID "+str(id)+" нет в базе данных"
            title = "Документ не найден"
            doc_dict = {}

        return render_template('doc_page.html',
                               doc_dict=doc_dict,
                               title=title,
                               warning=warning)

    @app.route('/text/<int:id>', methods=['GET', 'POST'])
    @roles_required(['Admin'])
    def text(id):
        doc = Documents.query.filter_by(id=id).first()

        if doc:
            doc_dict = query_to_dict(doc)
        else:
            doc_dict = {}

        warning = "Документа с ID "+str(id)+" нет в базе данных"
        return render_template('edit_text.html',
                               doc_dict=doc_dict,
                               title="Редактировать текст",
                               warning=warning)

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @roles_required(['Admin'])
    def edit(id):

        doc = Documents.query.filter_by(id=id).first()
        form = EditMeta()

        def set_form_data(form):
            for field in form:
                if field.name in fields:
                    field.data = getattr(doc, field.name)
                elif field.name in choices:
                    ch = ref_elements_list(choices[field.name])
                    field.choices = ch
                    if field.name in multiselect:
                        set_values = []
                        for el in getattr(doc, field.name):
                            new = RefBooksElements.query.with_entities(RefBooksElements.id,
                                                                       RefBooksElements.ref_value).filter_by(id=el.id).first()
                            set_values.append(new[0])
                        field.data = set_values
                    else:
                        field.data = getattr(doc, field.name)

        if doc:
            doc_dict = query_to_dict(doc)
            set_form_data(form)
        else:
            doc_dict = {}

        warning = "Документа с ID "+str(id)+" нет в базе данных"

        return render_template('edit_meta.html',
                               title="Редактировать метаданные",
                               doc_dict=doc_dict,
                               form=form,
                               checkboxes=checkboxes,
                               diff_fields=diff_fields,
                               multiselect=multiselect,
                               warning=warning)

    @app.route('/linguistic_info')
    def linguistic_info():
        return render_template('linguistic_info.html',
                               title="Взгляд лингвиста")

    @app.route('/research')
    def research():
        return render_template('research.html',
                               title="Исследования")

    @app.route('/about_project')
    def about_project():
        return render_template('about_project.html',
                               title="О проекте")

    @app.route('/ref_books')
    def ref_books():
        return render_template('ref_books.html',
                               title="Управление справочниками")

    @app.route('/activity_log')
    def activity_log():
        return render_template('activity_log.html',
                               title="Журнал действий")

    # @app.route('/members')
    # @login_required
    # def member_page():
    #     doc, warning = get_text()
    #     return render_template('index.html',
    #                            title="Welcome!",
    #                            page_type="Members page",
    #                            user_roles=get_roles(current_user),
    #                            warning=warning,
    #                            doc=doc)

    # @app.route('/admin')
    # @roles_required(['Admin'])
    # def admin_page():
    #     doc, warning = get_text()
    #     return render_template('index.html',
    #                            title="Welcome!",
    #                            page_type="Admin page",
    #                            user_roles=get_roles(current_user),
    #                            warning=warning,
    #                            doc=doc)

    return app

if __name__ == '__main__':
    app = create_app()
    #app.jinja_env.add_extension('jinja2.ext.do')
    app.run()
