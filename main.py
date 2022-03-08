from flask import *
from config import Config
import datetime
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

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
        default = db.Column(db.Boolean(), server_default='1')

    class RefBooksElements(db.Model):
        __tablename__ = 'ref_books_elements'
        id =  db.Column(db.Integer(), primary_key=True)
        ref_book = db.Column(db.Integer, db.ForeignKey('reference_books.id'), nullable=False)
        ref_value = db.Column(db.String(255), nullable=False)
        ref_date = db.Column(db.DateTime(), nullable=False)

    class Documents(db.Model):
        __tablename__ = 'documents'
        id = db.Column(db.Integer(), primary_key=True)
        doc_name = db.Column(db.String(100), unique=True, nullable=False)
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

        theme = db.relationship('RefBooksElements', secondary='doc_themes')
        court_punishment =  db.relationship('RefBooksElements', secondary='doc_court_punishments')
        # doc_text

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
        ref_book = db.Column(db.Integer(), db.ForeignKey('reference_books.id'), nullable=False)
        ref_element = db.Column(db.Integer(), db.ForeignKey('ref_books_elements.id'), nullable=False) # переименовала!!


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

    @app.route('/', methods=['GET', 'POST'])
    def index():
        doc, warning = get_text()
        return render_template('index.html',
                               title="Добро пожаловать!",
                               #page_type="Главная",
                               warning=warning,
                               doc=doc)

    @app.route('/<int:id>')
    def doc_page(id):
        warning = ''
        doc = Documents.query.filter_by(id=id).first()
        if not doc:
            warning = "Документа с ID "+str(id)+" нет в базе данных"
            title = "Документ не найден"
        else:
            title = doc.doc_name
        return render_template('doc_page.html',
                               doc=doc,
                               title=title,
                               warning=warning)

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