# this creates the web application
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import routes, models


import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

"""
To test logging to email, use:
(venv) $ python -m smtpd -n -c DebuggingServer localhost:8025
and set:
export MAIL_SERVER=localhost
MAIL_PORT=8025
FLASK_DEBUG=0
or:
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=<your-gmail-username>
export MAIL_PASSWORD=<your-gmail-password>
FLASK_DEBUG=0
"""

# only enables emails when app is NOT set to debug mode
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        # creates an SMTPHandler instance and sets it so it only reports
        #   errors and not warnings or informational messages
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], 
            subject='Microblog Failure',
            credentials=auth, 
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    # rotates logs, ensuring that the files don't grow too large
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, 
                                        backupCount=10)
    # provides custom formatting for the log messages                                   
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # sets logging categories based on preset classifications
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
    



