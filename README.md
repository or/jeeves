## To get jeeves up and running locally

```
$ sudo apt-get install redis-server
$ pip install -r requirements.txt
$ cp jeeves/settings.py{.template,}
$ ./manage.py migrate
$ ./manage.py createsuperuser
$ ./manage.py runserver
$ # in another terminal
$ ./manage.py runsd
$ # in yet another terminal
$ celery worker -A jeeves
$ # now add a project in the web application
$ # use './build.py' as the build script
$ # and schedule the first build:
$ ./manage.py schedule_build <project name>
```
