# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request
from flask import render_template
from flask import make_response
from flask import abort
from flask import redirect
from flask import url_for
from flask import Response
from flask import jsonify

project = Blueprint('project', __name__)

from sqlalchemy.orm import lazyload
from sqlalchemy.orm import joinedload
from werkzeug import secure_filename
from flask import send_from_directory
from werkzeug import SharedDataMiddleware
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user

from app import mongo
from app.models import Website

@project.route('/project', methods=['GET'])
def get_projects():
    """项目列表
    """
    limit = 12
    offset = request.args.get('offset', 0, type=int)

    collection_names = []
    for name in mongo.db.collection_names():
        if name.startswith('system.'):
            continue

        collection_names.append(name)
    collection_names = collection_names[offset: offset + limit]

    websites = Website.get_websites_by_en_names(collection_names)

    projects = []
    for project_id in collection_names:
        project = {
                'project_id': project_id,
                'task_count': mongo.db[project_id].find({}).count(),
                'task_status': {
                    1: mongo.db[project_id].find({'status': 1}).count(),
                    2: mongo.db[project_id].find({'status': 2}).count(),
                    3: mongo.db[project_id].find({'status': 3}).count(),
                    4: mongo.db[project_id].find({'status': 4}).count(),
                    5: mongo.db[project_id].find({'status': 5}).count(),
                    }
                }
        try:
            project.update(websites[project_id].to_dict())
        except:
            pass

        projects.append(project)

    return render_template('/project/index.html', **locals())

@project.route('/project/<project_id>')
def get_project(project_id):
    """项目详情
    """

    project = {
            'project_id': project_id,
            'task_count': mongo.db[project_id].find({}).count(),
            'task_status': {
                1: mongo.db[project_id].find({'status': 1}).count(),
                2: mongo.db[project_id].find({'status': 2}).count(),
                3: mongo.db[project_id].find({'status': 3}).count(),
                4: mongo.db[project_id].find({'status': 4}).count(),
                5: mongo.db[project_id].find({'status': 5}).count(),
                }
            }

    website = Website.get_website_by_en_name(project_id)
    if website:
        project.update(website.to_dict())

    return render_template('/project/detail.html', **locals())
