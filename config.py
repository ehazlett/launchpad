#!/usr/bin/env python
# Copyright 2012 Evan Hazlett
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import Flask
import logging

APP_NAME = 'launchpad'
APP_VERSION = '0.1'
INTERNAL_API_KEYS = (
    'arcus-default-key',
)
LOG_LEVEL = logging.DEBUG
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 12
REDIS_PASSWORD = None
SENTRY_DSN = None
SECRET_KEY = '1q2w3e4r5t6y7u8i9o0pazsxdcfv'

def create_app():
    """
    Flask app factory

    :rtype: `flask.Flask`

    """
    app = Flask(__name__)
    app.config.from_object('config')
    #sentry.init_app(app)
    return app

try:
    from local_config import *
except ImportError:
    pass
