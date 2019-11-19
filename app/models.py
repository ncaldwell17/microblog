from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# db is a proxy for SQLAlchemy 
from app import db, login
from hashlib import md5

# migrate is a proxy defined in __init__.py for Flask_Migrate
# command to migrate a new changes to a database
# $ flask db migrate -m "[[NAME OF THE NEW DATABSE]]"
# $ flask db upgrade 

# this is a direct translation of what Miguel demonstrated on his page
# creates a brand-new table in the database using db.Table() class
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# this class inherits from db.Model, a base class for all Flask-SQLAlchemy models
class User(UserMixin, db.Model):
    # FIELDS 
    id = db.Column(db.Integer, primary_key=True)
    # the additional arguments allow future searches to be more efficient
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # defines the relationship between posts and authors
    # the first argument is the right side entity of the relationship 
    # backref defines how this relationship will be accessed from the right side entry
    posts = db.relationship('Post', backref="author", lazy='dynamic')

    # remember everytime the database is modified, I need to alter the database
    #   using the migration script in terminal 
    # REMEMBER: Finalize the changes using "flask db upgrade"
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # this helps define the relationship in the model class
    # secondary configures the association table that is used for the relationship
    # primaryjoin indicates the condition that links the left side entity 
    #       (the follower user) with the association table. 
    # now that I've defined this relationship as a variable, I can use it to create
    #       examples of that relationship
    # ex.) user1.followed.append(user2) OR user1.followed.remove(user2)
    followed = db.relationship('User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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

    def is_following(self, user):
        # count() is the query terminator, which I'd presume 
        #       prevents me from implementing count as a method instead
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        # the if condition is a precaution to make sure the method makes sense
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        # makes use of auxillary function to verify whether or not the user is 
        #   already following
        if self.is_following(user):
            self.followed.remove(user)

    #  helper that creates a temporary table that makes sorting scalable
    def followed_posts2(self): 
        # this function is useful becuase it uses joins to exclude those 
        #       who you're not following because the join condition makes 
        #       it need the user ID and followed_ID to match (see Miguel's tutorial for a visual)
        # The query is issued on the post class, which is a proxy for a table in the DB. 
        return Post.query.join(
            followers,(followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())

    # helper that creates a temporary table that makes sorting scalable AND 
    #       allows user to see others' and their own posts
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        # union allows me to expand the scope of what's retrieved from the DB
        return followed.union(own).order_by(Post.timestamp.desc())


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}'.format(self.body)

# login is a proxy for LoginManager(app)
@login.user_loader
def load_user(id):
    return User.query.get(int(id))