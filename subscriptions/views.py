# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required (redirect_field_name='index')
def index(request):
  message = u"Hello world! ČĆŠĐŽ"
  return render_to_response('index.html', {'message': message})

def login(request):
  return render_to_response('login.html')
