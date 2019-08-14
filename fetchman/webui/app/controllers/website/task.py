# -*- coding: utf-8 -*-

import json

from flask import Blueprint
from flask import request
from flask import render_template
from flask import make_response
from flask import abort
from flask import redirect
from flask import url_for
from flask import Response
from flask import jsonify

task = Blueprint('task', __name__)

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

@task.route('/task', methods=['GET'])
def get_tasks():
    """任务列表
    """
    limit = 12
    offset = request.args.get('offset', 0, type=int)
    project_id = request.args.get('project_id', '', type=str)
    status = request.args.get('status', 0, type=int)

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

    tasks = []
    if status > 0:
        for it in mongo.db[project_id].find({'status': status}).skip(offset).limit(limit):
            tasks.append(it)
    else:
        for it in mongo.db[project_id].find().skip(offset).limit(limit):
            tasks.append(it)

    return render_template('/task/index.html', **locals())

@task.route('/task/<task_id>')
def get_task(task_id):
    """项目详情
    """
    project_id = request.args.get('project_id', '', type=str)
    task = mongo.db[project_id].find_one({'id': task_id})

    return render_template('/task/detail.html', json=json, **locals())
