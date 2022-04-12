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
from forms import EditMeta

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
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    class ReferenceBooks(db.Model):
        __tablename__ = 'reference_books'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_name = db.Column(db.String(255), nullable=False)
        ref_default = db.Column(db.Boolean(), server_default='1')

    class RefBooksElements(db.Model):
        __tablename__ = 'ref_books_elements'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_book = db.Column(db.Integer, db.ForeignKey('reference_books.id'), nullable=False)
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
        lawsuit_price = db.Column(db.Integer(), nullable=True)
        court_result = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=True)
         #???
        compens = db.Column(db.Integer(), nullable=True)
        appeal =  db.Column(db.Boolean(), nullable=True)
        appeal_succ = db.Column(db.Boolean(), nullable=True)
        appeal_date = db.Column(db.DateTime(), nullable=True)
        ap_decision_date = db.Column(db.DateTime(), nullable=True)
        ap_dec_time = db.Column(db.Integer(), nullable=True) # вычислить!
        decision_exec_date = db.Column(db.DateTime(), nullable=True)
        decision_exec_time = db.Column(db.Integer(), nullable=True) # вычислить!

        doc_text = db.Column(db.Text(), nullable=True)
        img_names = db.Column(db.String(100), nullable=True)

        theme = db.relationship('RefBooksElements', secondary='doc_themes')
        court_punishment =  db.relationship('RefBooksElements', secondary='doc_court_punishments')
        ref_doc_properties = db.relationship('RefBooksElements', secondary='ref_doc_properties')

    class DocThemes(db.Model):
        __tablename__ = 'doc_themes'
        id = db.Column(db.Integer(), primary_key=True)
        doc_id = db.Column(db.Integer(), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
        theme_id = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id', ondelete='CASCADE'))

    class DocCourtPunishments(db.Model):
        __tablename__ = 'doc_court_punishments'
        id = db.Column(db.Integer(), primary_key=True)
        doc_id = db.Column(db.Integer(), db.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
        court_punishment_id = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id', ondelete='CASCADE'), nullable=False)

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

    if not User.query.filter(User.email == 'member1@example.com').first():
        user = User(email='member1@example.com',
                    email_confirmed_at=datetime.datetime.utcnow(),
                    password=user_manager.hash_password('Password1'),
                    first_name="Василий",
                    last_name="Иванов",)
        user.roles.append(Role(name="Beginner_Researcher"))
        db.session.add(user)
        db.session.commit()

    if not User.query.filter(User.email == 'member2@example.com').first():
        user = User(email='member2@example.com',
                    email_confirmed_at=datetime.datetime.utcnow(),
                    password=user_manager.hash_password('Password1'),
                    first_name="Иван",
                    last_name="Васильев",)
        user.roles.append(Role(name="Experienced_Researcher"))
        db.session.add(user)
        db.session.commit()

        # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(email='admin@example.com',
                    email_confirmed_at=datetime.datetime.utcnow(),
                    password=user_manager.hash_password('Password1'),
                    first_name="Николай",
                    last_name="Николаев",)
        user.roles.append(Role(name='Admin'))
        db.session.add(user)
        db.session.commit()

    def add_themes_punishments():
        doc = Documents(doc_name='test',
                        reg_date=datetime.datetime.utcnow(),)
        doc.theme.append(RefBooksElements.query.filter_by(ref_value='потрава').first())
        doc.court_punishment.append(RefBooksElements.query.filter_by(ref_value='штраф').first())
        db.session.add(doc)
        db.session.commit()


    def get_roles(cur_user):
        roles_list = cur_user.roles
        user_roles = []
        for role in roles_list:
            user_roles.append(Role.query.filter_by(id=role.id).first().name)
        return user_roles

    def get_text():
        doc = ''
        warning = ''
        if request.method == "GET":
            doc_id = request.args.get('doc_id')
            if doc_id:
                doc_id = int(doc_id)
                doc = Documents.query.filter_by(id=doc_id).first()
                if not doc:
                    warning = "Текста с id "+str(doc_id)+" нет в базе данных"
                    doc = ''
        return doc, warning

    th_names = ['Дата регистрации документа в базе данных', 'Губерния', 'Уезд', 'Волость',
                'Место жительства истца', 'Место жительства ответчика', 'Дата подачи заявления', 'Дата вынесения решения',
                'Время ожидания', 'Темы',
                'Номер по книге решений суда', 'Присутствие истца', 'Присутствие ответчика',
                'Цена предъявленного иска в рублях', 'Результат суда', 'Наказания по суду',
                'Сумма присуждённого возмещения в рублях',
                'Обжаловано', 'Обжалование успешно', 'Дата подачи апелляции', 'Дата решения по апелляции',
                'Время ожидания решения апелляции', 'Дата исполнения решения', 'Время ожидания решения']
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
                                                  Documents.decision_exec_time)\
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

    @app.route('/') # methods=['GET', 'POST'])
    def index():
        #docs = Documents.query.all()
        docs, docs_themes, docs_punishments = get_all_docs()
        #docs_list = [dict((col, getattr(doc, col)) for col in doc.__table__.columns.keys()) for doc in docs]
        docs_list = query_to_dict(docs)
        docs_themes, docs_punishments = get_themes_puns()
        #print(docs_punishments)
        for i in range(len(docs_themes)):
            docs_list[i].update(docs_themes[i])
            docs_list[i].update(docs_punishments[i])
        #print(docs_list)
        return render_template('index.html',
                               title="Добро пожаловать!",
                               column_dict=column_dict,
                               docs_list=docs_list)

    @app.route('/<int:id>', methods=['GET', 'POST'])
    def doc_page(id):
        warning = ''
        doc = Documents.query.filter_by(id=id).first()
        if request.method == "POST":
            new_doc_name = request.form.get("doc_name")
            #new_create_date = form.create_date.data
            #new_decision_date = form.decision_date.data
            doc.doc_name = new_doc_name
            db.session.commit()
        if doc:
            doc_dict = query_to_dict(doc)
            #doc_dict = dict(itertools.islice(doc_dict.items(), 1, 26))
            title = doc.doc_name
        else:
            warning = "Документа с ID "+str(id)+" нет в базе данных"
            title = "Документ не найден"
            doc_dict = {}

        return render_template('doc_page.html',
                               doc_dict=doc_dict,
                               title=title,
                               warning=warning)

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @roles_required(['Admin'])
    def edit(id):
        new_name = ''
        doc = Documents.query.filter_by(id=id).first()
        doc_dict = query_to_dict(doc)
        form = EditMeta()
        if doc_dict:
            form.doc_name.data = doc_dict['doc_name']
            form.create_date.data = doc_dict['create_date']
            form.decision_date.data = doc_dict['decision_date']
            #form.guberniya.choices = []
        else:
            warning = "Такого документа нет"
        return render_template('edit_meta.html',
                               title="Редактировать метаданные",
                               doc_dict=doc_dict,
                               form=form,
                               new_name=new_name)

    @app.route('/research')
    def research():
        return render_template('research.html',
                               title="Исследования")

    @app.route('/about_project')
    def about_project():
        return render_template('about_project.html',
                               title="О проекте")

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
    app.run()