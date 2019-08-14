# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Date
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.utils import utils

class Website(db.Model):
    '''文章
    '''
    __tablename__ = 't_website'
    default_attrs = ['id', 'name', 'en_name', 'summary', 'url', 'logo', 'sort']
    id = Column(Integer, primary_key=True)
    flag = Column(Integer, unique=False, default=0)
    status = Column(Integer, unique=False, default=0)
    create_time = Column(DateTime, unique=False, default=datetime.now)
    update_time = Column(DateTime, unique=False, default=datetime.now)
    name = Column(String(40), unique=False, default='')
    en_name = Column(String(40), unique=False, default='')
    summary = Column(String(1000), unique=False, default='')
    logo = Column(String(255), unique=False, default='')
    url = Column(String(1000), unique=False, default='')
    sort = Column(Integer, unique=False, default=0)

    def __repr__(self):
        return '<Website %r>' % (self.name)

    def to_dict(self, *args):
        return utils.to_dict(self, *args)

    @staticmethod
    def get_website_by_website_id(website_id):
        website = db.session.query(Website).filter_by(flag=0).filter_by(id=website_id).first()
        return website

    @staticmethod
    def get_websites_by_website_ids(website_ids):
        results = {}
        if not website_ids:
            return results

        websites = db.session.query(Website).filter_by(flag=0).filter(Website.id.in_(website_ids)).all()
        for website in websites:
            results[website.id] = website

        return results

    @staticmethod
    def get_website_by_en_name(en_name):
        website = db.session.query(Website).filter_by(flag=0).filter_by(en_name=en_name).first()
        return website

    @staticmethod
    def get_websites_by_en_names(en_names):
        results = {}
        if not en_names:
            return results

        websites = db.session.query(Website).filter_by(flag=0).filter(Website.en_name.in_(en_names)).all()
        for website in websites:
            results[website.en_name] = website

        return results

    @staticmethod
    def get_websites():
        websites = db.session.query(Website).filter_by(flag=0).order_by(Website.sort.asc()).all()

        return websites
