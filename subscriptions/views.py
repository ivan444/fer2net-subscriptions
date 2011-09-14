# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response

def index(request):
  message = u"Hello world! ČĆŠĐŽ"

  return render_to_response('index.html', {'message': message})

