import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # these are configuration settings

    # my SECRET_KEY is an import part of most Flask apps
    # Flask and its extensions used it as a crypto key to generate signatures
    # the Flask-WTF uses it to protect web forms against CSRF Attacks
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # this double-check is used to ensure fallbacks 

    # for this, I'm just going to use an SQLite database, don't need a whole server
    # this configuration key gives Flask_SQLAlchemy the location of the database
    # it's good practice to set configurations from environment variables & 
    #   provide a fallback 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # this disables a feature of SQLAlchemy that I don't need
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # this adds my email server details so I can be notified about bugs
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['ncaldwellgatsos@gmail.com']