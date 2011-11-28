# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from subscriptions.auth.backends import VBulletinBackend
from django.core.context_processors import csrf

@login_required (redirect_field_name='index')
def index(request):
  message = u"Hello world! ČĆŠĐŽ"
  return render_to_response('index.html', {'message': message})

def loginview(request):
  if request.method == 'POST':
     username = request.POST['username']
     password = request.POST['password']
     user = VBulletinBackend().authenticate(username = username, password = password)
     if user is not None:
       login(request, user)
     else:
       return redirect("login")
      
  c = {}
  c.update(csrf(request))
  return render_to_response('login.html', c)

def logoutview(request):
  logout(request)
  return redirect("login")
