# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.context_processors import csrf

@login_required
def index(request):
  message = u"Hello world! ČĆŠĐŽ"
  return render_to_response('index.html', {'message': message})

@login_required
def drugi(request):
  return render_to_response('index.html', {'message': "drugi"})

def loginview(request):
  c = {}
  c.update(csrf(request))
  retResp = render_to_response('login.html', c)

  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username = username, password = password)
    if user is not None:
      login(request, user)
    else:
      return redirect("login")
      
    redirectUrl = request.POST['next']
    if redirectUrl is not None and redirectUrl != '':
      retResp = redirect(redirectUrl)

  return retResp

def logoutview(request):
  logout(request)
  return redirect("loginview")
