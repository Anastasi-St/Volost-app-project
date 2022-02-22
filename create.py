import datetime
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin

def create_app(app):
    babel = Babel(app)
    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        email = db.Column(db.String(255), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        login = db.Column(db.String(100), nullable=False, server_default='')
        name = db.Column(db.String(200), nullable=False, server_default='')

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

    user_manager = UserManager(app, db, User)
    db.create_all()

    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(email='member@example.com',
                    email_confirmed_at=datetime.datetime.utcnow(),
                    password=user_manager.hash_password('Password1'),)
        db.session.add(user)
        db.session.commit()

        # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(email='admin@example.com',
                    email_confirmed_at=datetime.datetime.utcnow(),
                    password=user_manager.hash_password('Password1'),)
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    return app

