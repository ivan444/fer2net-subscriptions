# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from subscriptions.auth.backends import VBulletinBackend

@login_required (redirect_field_name='index')
def index(request):
  message = u"Hello world! ČĆŠĐŽ"
  return render_to_response('index.html', {'message': message})

def loginview(request):
  if request.method == 'POST':
     username = request.POST['username']
     password = request.POST['password']
     user = VBulletinBackend.authenticate(username = username, password = password)
     if user is not None:
       login(request, user)
     else:
       return redirect("login")
      
  return render_to_response('login.html')

def logoutview(request):
  logout(request)
  return redirect("login")
