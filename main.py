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

    class Documents(db.Model):
        __tablename__ = 'documents'
        id = db.Column(db.Integer(), primary_key=True)
        doc_name = db.Column(db.String(100), unique=True, nullable=False)
        reg_date = db.Column(db.DateTime())
        owner = db.Column(db.ForeignKey('users.id'), nullable=True)  #, ondelete='CASCADE'))

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
                               title="Welcome!",
                               page_type="Home page",
                               curr_user=current_user,
                               warning=warning,
                               doc=doc)

    @app.route('/members')
    @login_required
    def member_page():
        doc, warning = get_text()
        return render_template('index.html',
                               title="Welcome!",
                               page_type="Members page",
                               curr_user=current_user,
                               user_roles=get_roles(current_user),
                               warning=warning,
                               doc=doc)

    @app.route('/admin')
    @roles_required(['Admin'])
    def admin_page():
        doc, warning = get_text()
        return render_template('index.html',
                               title="Welcome!",
                               page_type="Admin page",
                               curr_user=current_user,
                               user_roles=get_roles(current_user),
                               warning=warning,
                               doc=doc)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()