#!/usr/bin/python
import os
import sys

paths = ['/var/www', '/var/www/subsf2net/']

for path in paths:
  if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'subsf2net.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

