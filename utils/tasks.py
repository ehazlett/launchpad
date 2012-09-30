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
import utils
from subprocess import Popen, PIPE, STDOUT

def action_handler(config=None):
    if not config:
        return "No config ; skipping"
    email_notify_users = config.get('notifications', {}).get('email')
    msg = ''
    # run commands
    msg += 'Commands: \n\n'
    for cmd in config.get('commands'):
        p = Popen(cmd, env=config.get('environment'), shell=True, bufsize=4096,
                  stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        (stdin, stdout) = (p.stdin, p.stdout)
        msg += '{0}: \n{1}'.format(cmd, p.stdout.read())
        msg += '----------\n'
    if email_notify_users:
        utils.send_mail('Launchpad Action: {0}'.format(config.get('name')), \
            msg, email_notify_users)
    return 'Done'

