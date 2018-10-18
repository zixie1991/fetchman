# -*- coding: utf-8 -*-

import os
import logging.config

import yaml

from fetchman import settings

def init_logger():
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.conf"))

def load_config(conf_path):
    settings.set('setting_module', os.path.abspath('.'))

    with open(conf_path, 'r') as f:
        settings.setdict(yaml.load(f))
