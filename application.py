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
from flask import request, json
from flask.ext.mail import Mail
from flask.ext import redis
from utils import generate_api_response
import config
#from raven.contrib.flask import Sentry
#sentry = Sentry(config.SENTRY_DSN)

app = config.create_app()
mail = Mail(app)
redis = redis.init_redis(app)
# add exts for blueprint use
app.config['redis'] = redis
app.config['mail'] = mail

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

@app.route('/notify', methods=['GET', 'POST'])
def notify():
    # github
    post = request.form.get('payload')
    data = None
    if post:
        payload = json.loads(post)
        repo = payload.get('repository', {}).get('name')
        commit = payload.get('after')
        username = payload.get('head_commit', {}).get('committer', {}).get('username')
        data = {
            'repo': repo,
            'commit': commit,
            'username': username,
        }
    return generate_api_response({'status': 'thanks!'})

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
