# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.context_processors import csrf
import logging
import md5
from django.db import connection
from subscriptions.auth import VBULLETIN_CONFIG

@login_required 
def index(request):
  return indexStaff(request)
  #message = u"Hello world! ČĆŠĐŽ"
  #return render_to_response('index.html', {'message': message})

@login_required 
def indexStaff(request):
  cursor = connection.cursor()

  cursor.execute("""SELECT userid, username, email
                    FROM %suser"""
                 % (VBULLETIN_CONFIG['tableprefix']))
  row = cursor.fetchall()
  allUsers = []
  for r in row:
    usr = {}
    usr["userid"] = r[0]
    usr["username"] = r[1]
    usr["email"] = r[2]
    allUsers.append(usr)

  return render_to_response('index-staff.html', {'allUsers': allUsers})

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

