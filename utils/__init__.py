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
import os
import hashlib
from flask import current_app, request, Response, json
from urlparse import urlparse, urljoin
from flask.ext.mail import Message
import config

def get_redis_connection():
    """
    Returns a Redis connection for the current app

    """
    return current_app.config.get('redis')

def generate_api_response(data, status=200, content_type='application/json'):
    """
    `flask.Response` factory for api responses

    :param data: Data that gets serialized to JSON
    :param status: Status code (default: 200)
    :param content_type: Content type (default: application/json)

    """
    indent = None
    if request.args.get('indent'):
        indent = 2
    # check if need to add status_code
    if data == type({}) and not data.has_key('status_code'):
        data['status_code'] = status
    # serialize
    if type(data) != type(''):
        data = json.dumps(data, sort_keys=True, indent=indent)
    resp = Response(data, status=status, content_type=content_type)
    return resp

def hash_text(text):
    """
    Hashes text with app key

    :param text: Text to encrypt

    """
    h = hashlib.sha256()
    h.update(getattr(config, 'SECRET_KEY'))
    h.update(text)
    return h.hexdigest()

def send_mail(subject=None, text='', to=[]):
    """
    Sends mail

    :param subject: Subject
    :param text: Message
    :param to: Recipients as list

    """
    try:
        mail = current_app.config.get('mail')
        msg = Message(subject, sender=current_app.config.get('DEFAULT_MAIL_SENDER'), \
            recipients=to)
        msg.body = text
        res = mail.send(msg)
    except RuntimeError: # working out of request context
        import smtplib
        session = smtplib.SMTP(getattr(config, 'MAIL_SERVER'), \
            getattr(config, 'MAIL_PORT'))
        session.ehlo()
        if getattr(config, 'MAIL_USE_TLS'):
           session.starttls()
           session.ehlo()
        username, password = getattr(config, 'MAIL_USERNAME'), getattr(config, \
            'MAIL_PASSWORD')
        if username:
            session.login(username, password)
        sender = getattr(config, 'DEFAULT_MAIL_SENDER')
        msg = [
            'From: ' +  sender,
            'Subject: ' + subject,
            'To: ' + ','.join(to),
            '',
            text,
        ]
        res = session.sendmail(sender, to, '\r\n'.join(msg))
        session.quit()
    return res

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    next_url = request.values.get('next')
    if next_url and is_safe_url(next_url):
        return next_url

def load_configs():
    """
    Loads handler configs from CONF_DIR

    """
    data = {}
    config_dir = getattr(config, 'CONF_DIR')
    for cfg in os.listdir(config_dir):
        fname, ext = os.path.splitext(cfg)
        if ext == '.cfg':
            try:
                c = json.loads(open(os.path.join(config_dir, cfg)).read())
                data[c.get('name')] = c
            except Exception, e:
                print(e)
    return data
