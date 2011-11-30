# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.context_processors import csrf

@login_required 
def index(request):
  message = u"Hello world! ČĆŠĐŽ"
  return render_to_response('index.html', {'message': message})

def loginview(request):
  # c is dictionary used to send data to template
  c = { 'next': 'index',          # Where to go after the login, default
        'wrong_login': False }    # Did user provided us wrong data?

  if 'next' in request.GET: 
     c['next'] = request.GET['next'] 

  
  # generating anti-CSRF key
  c.update(csrf(request))         
 
  if request.method == 'POST':
     username = request.POST['username']
     password = request.POST['password']

     # in case this is wrong login, site should still remember where to go next
     c['next'] = request.POST['next'] 

     user = authenticate(username = username, password = password)
     if user is not None:
       login(request, user)
       return redirect (c['next'])
     else:
       c['wrong_login'] = True
        
  # show the form 
  return render_to_response('login.html', c)

def logoutview(request):
  logout(request)
  return redirect("loginview")

