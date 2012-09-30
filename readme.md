#Launchpad
Launchpad is a web application that will perform operations on receipt of a VCS event, currently Github.  It works by specifying a configuration file that contains commands you want to execute.  After a post-receive hook is setup in Github (click on the "Admin" tab of your repo), Launchpad will run the operations -- for example, a deployment.

#Setup
Launchpad requires Redis.  Make sure you have it available and enter the connection information in `config.py`.  If Redis is running on `localhost:6379` you won't have to do anything.

* `pip install -r requirements.txt`
* `python application.py`

You will need to make your app publicly available in order to test the Github hooks -- a quick and easy way is with http://showoff.io.

#Configuration Files
By default, Launchpad does nothing -- you have to specify a configuration file (per repository) with commands (commands are executed in the order listed) and place that file in the `conf` directory.  Here is an example:

```javascript
{
  "name": "myrepo",
  "commands": [
    "git clone https://github.com/myuser/myrepo.git /tmp/myrepo",
    "virtualenv --distribute --no-site-packages /tmp/myrepo_ve",
    "/tmp/myrepo_ve/bin/pip install --use-mirrors -r /tmp/myrepo/requirements.txt",
    "cd /tmp/myrepo ; /tmp/myrepo_ve/bin/hyde gen ; /tmp/myrepo_ve/bin/hyde publish -c prod.yaml",
    "rm -rf /tmp/myrepo*"
  ],
  "environment": {
    "AWS_ACCESS_KEY_ID": "ABCDEFGHIJKLMNOP",
    "AWS_SECRET_ACCESS_KEY": "abcdefghijlkmnop1234567890",
    "PATH": "/tmp/myrepo_ve/bin:/usr/local/bin:/usr/bin:/bin"
  },
  "notifications": {
    "email": [
      "myuser@example.com"
    ]
  }
}
```

Note: the "name" in the configuration file *must* match the name of the Github repository.

In the above config, it is using [Hyde](https://github.com/hyde/hyde) to build and deploy (using S3).  You can set environment variables in the "environment" section.  To be notified of the result, add your email address (or addresses) to the "notifications: emails" section.
