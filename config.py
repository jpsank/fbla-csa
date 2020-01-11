import os
basedir = os.path.abspath(os.path.dirname(__file__))


# CONFIGURATION

DEBUG = True

# Logging
LOGS_PATH = os.path.join(basedir, 'logs')

# Pagination
DEFAULT_PER_PAGE = 50


# EXTENSIONS

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Session
SESSION_TYPE = 'sqlalchemy'
