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
from flask import request, json, redirect, url_for
from flask.ext.mail import Mail
from flask.ext import redis
from utils import generate_api_response
from utils import tasks
import utils
import config
import time
from multiprocessing import Process
#from raven.contrib.flask import Sentry
#sentry = Sentry(config.SENTRY_DSN)

app = config.create_app()
mail = Mail(app)
redis = redis.init_redis(app)
# add exts for blueprint use
app.config['redis'] = redis
app.config['mail'] = mail

app.config['configs'] = utils.load_configs()

# ----- context processors
# ----- end context processors

# ----- template filters
# ----- end filters

@app.route('/')
def index():
    data = {
        'version': getattr(config, 'APP_VERSION'),
    }
    return generate_api_response(data)

@app.route('/notify', methods=['POST'])
def notify():
    # github payload (https://help.github.com/articles/post-receive-hooks)
    post = request.form.get('payload')
    if post:
        payload = json.loads(post)
        repo = payload.get('repository', {}).get('name')
        #commit = payload.get('after')
        #username = payload.get('head_commit', {}).get('committer', {}).get('username')
        repo_cfg = app.config.get('configs', {}).get(repo)
        if repo_cfg:
            # run handler in subprocess (for async)
            p = Process(target=tasks.action_handler, args=(repo_cfg,))
            p.start()
            # log action
            redis.set('actions:{0}:{1}'.format(repo, time.time()), post)
    return generate_api_response({'status': 'thanks!'})

@app.route('/actions')
def actions():
    name = request.args.get('name')
    if name:
        key = 'actions:{0}:*'.format(name)
    else:
        key = 'actions:*'
    keys = redis.keys(key)
    actions = []
    [actions.append(json.loads(redis.get(x))) for x in keys]
    return generate_api_response(actions)

@app.route('/actions/clear')
def actions_clear():
    name = request.args.get('name')
    if name:
        key = 'actions:{0}:*'.format(name)
    else:
        key = 'actions:*'
    keys = redis.keys(key)
    [redis.delete(x) for x in keys]
    return redirect(url_for('actions'))

# ----- utility functions
if __name__=='__main__':
    from optparse import OptionParser
    op = OptionParser()
    op.add_option('--host', dest='host', action='store', default='127.0.0.1', \
        help='Hostname/IP on which to listen')
    op.add_option('--port', dest='port', action='store', type=int, \
        default=5000, help='Port on which to listen')
    opts, args = op.parse_args()

    app.run(host=opts.host, port=opts.port, debug=True)
