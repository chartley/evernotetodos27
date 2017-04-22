#!/bin/sh

# pull django
runuser -l django -c "cd /home/django/django_project && git pull"

# restart
/usr/local/sbin/_restart_django.sh

