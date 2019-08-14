# -*- coding: utf-8 -*-

# flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# flask_wtf
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

# flask_login
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

# flask_pymongo
from flask.ext.pymongo import PyMongo
mongo = PyMongo()
