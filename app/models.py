from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from hashlib import md5

# this class inherits from db.Model, a base class for all Flask-SQLAlchemy models
class User(UserMixin, db.Model):
    # FIELDS 
    id = db.Column(db.Integer, primary_key=True)
    # the additional arguments allow future searches to be more efficient
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref="author", lazy='dynamic')
    # remember everytime the database is modified, I need to alter the database
    #   using the migration script in terminal 
    # REMEMBER: Finalize the changes using "flask db upgrade"
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # METHODS
    # retrieves the user's information 
    def __repr__(self):
        return '<User {}>'.format(self.username)

    # password hashing and verification 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))