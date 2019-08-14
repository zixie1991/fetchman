# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Date
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import config
from app.utils import utils

class User(db.Model):
    '''用户
    '''
    __tablename__ = 't_user'
    default_attrs = ['id', 'username', 'avatar', 'nickname']
    id = Column(Integer, primary_key=True)
    flag = Column(Integer, unique=False, default=0)
    status = Column(Integer, unique=False, default=0)
    status = Column(Integer, unique=False, default=0)
    username = Column(String(255), unique=False, default='')
    nickname = Column(String(255), unique=False, default='')
    email = Column(String(255), unique=False, default='')
    mobile = Column(String(16), unique=False, default='')
    password = Column(String(255), unique=False, default='')
    salt = Column(String(16), unique=False, default='')
    avatar = Column(String(128), unique=False, default='')
    reg_time = Column(DateTime, unique=False, default=datetime.now)
    reg_ip = Column(String(255), unique=False, default='')
    last_login = Column(DateTime, unique=False, default=datetime.now)
    last_ip = Column(String(255), unique=False, default='')
    valid_email = Column(Integer, unique=False, default=0)
    group_id = Column(Integer, unique=False, default=0)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self, *args):
        result = utils.to_dict(self, *args)
        if 'nickname' in result and not result['nickname']:
            result['nickname'] = '%s%s' % (config.APP_NICKNAME, self.id)

        return result

    @staticmethod
    def get_user_by_uid(uid):
        user = db.session.query(User).filter_by(flag=0).filter_by(id=uid).first()
        return user

    @staticmethod
    def get_users_by_uids(uids):
        results = {}
        if not uids:
            return results

        users = db.session.query(User).filter_by(flag=0).filter(User.id.in_(uids)).all()
        for user in users:
            results[user.id] = user

        return results

    @staticmethod
    def get_user_by_email_or_name(email=None, name=None):
        user = db.session.query(User).filter_by(flag=0).filter((User.username == name) | (User.email == email)).first()
        return user
