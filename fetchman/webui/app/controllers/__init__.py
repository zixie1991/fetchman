# -*- coding: utf-8 -*-

from . import website
from . import api
from . import admin

default_blueprints = []
default_blueprints.extend(website.blueprints)
default_blueprints.extend(api.blueprints)
default_blueprints.extend(admin.blueprints)
