# -*- coding: utf-8 -*-

from functools import wraps
import datetime
import sys

from flask import Flask
from flask import g
from flask import request
from flask import url_for
from flask import render_template
from flask import send_from_directory
from flask import session
from werkzeug import SharedDataMiddleware
from flask_login import current_user

from config import config
from config import config_logging
from extensions import db
from extensions import mongo
from extensions import csrf
from extensions import login_manager
from utils.filters import init_jinja_filters


def create_app():
    app = Flask(__name__)

    # 初始化配置
    app.config.from_object(config)
    config.init_app(app)
    config_logging(app)

    # db配置
    db.init_app(app)

    # mongo
    mongo.init_app(app)

    # 控制器配置
    from controllers import default_blueprints
    for blueprint in default_blueprints:
        app.register_blueprint(blueprint)

    # 开启 CsrfProtect 模块
    csrf.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        user = db.session.query(User).get(int(user_id))
        user.nickname = user.to_dict()['nickname']
        return user
    login_manager.init_app(app)
    # cookie有效期
    app.permanent_session_lifetime = datetime.timedelta(minutes=24*60)
    login_manager.remember_cookie_duration = datetime.timedelta(days=1)

    # 访问静态资源
    def public_file(filename):
        return send_from_directory(app.config.get("UPLOAD_FOLDER"), filename)

    app.add_url_rule("/public/<filename>", "public_file", build_only=True)

    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app,
        {
            "/public": app.config.get("UPLOAD_FOLDER")
        },
        cache = False
        # tips: http://stackoverflow.com/questions/11515804/zombie-shareddatamiddleware-on-python-heroku
    )

    # favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    # Robots
    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, 'robots.txt')

    # sitemap.xml
    @app.route('/sitemap<name>')
    def sitemap(name):
        return send_from_directory(app.static_folder, 'sitemap%s' % name)

    # 过滤器处理
    configure_template_filters(app)

    # 错误处理
    configure_error_handlers(app)

    return app

def configure_template_filters(app):
    def url_for_other_page(offset, limit):
        # args = request.view_args.copy()
        args = dict(request.view_args.items() + request.args.to_dict().items())  #如果采用上面那句则换页时querystring会丢失
        args['offset'] = offset
        args['limit'] = limit
        return url_for(request.endpoint, **args)

    app.jinja_env.globals['url_for_other_page'] = url_for_other_page
    app.jinja_env.globals['config'] = config
    init_jinja_filters(app)

def configure_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
