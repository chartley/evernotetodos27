#!/bin/sh

# restart
/etc/init.d/gunicorn restart && /etc/init.d/nginx restart

