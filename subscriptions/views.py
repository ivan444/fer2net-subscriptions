# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import logging
import md5
from django.db import connection
from subscriptions.auth import VBULLETIN_CONFIG

@login_required 
def index(request):
  return indexStaff(request)
  #message = u"Hello world! ČĆŠĐŽ"
  #return render_to_response('index.html', {'message': message})

#TODO: close cursor
@login_required 
def indexStaff(request):
  cursor = connection.cursor()

  cursor.execute("""SELECT userid, username, email
                    FROM %suser"""
                 % (VBULLETIN_CONFIG['tableprefix']))
  rows = cursor.fetchall()
  allUsers = []
  for r in rows:
    usr = {}
    usr["userid"] = r[0]
    usr["username"] = r[1]
    usr["email"] = r[2]
    allUsers.append(usr)

  return render_to_response('index-staff.html', {'allUsers': allUsers})


@login_required 
def makePayment(request, uid=None, amount=None):
  if uid==None or amount==None: return Http404("no params")
  #if not (request.user.is_staff or request.user.is_superuser):
  #  return HttpResponse("", status=403)

  user = fetchUser(uid)
  sub = Subscription(user=user, amount=int(amount), delayed=False)
  sub.paymaster = request.user
  sub.paymentType = 'P'
  sub.date = datetime.now()
  sub.subsEnd =sub.date + timedelta(days=365)
  sub.save()
  
  request.session.modified = True
  return HttpResponse("{\"status\":\"ok\"}", mimetype='application/javascript; charset=utf8')


#TODO: close cursor
def fetchUser(uid):
  """ Fetches one user from local space or retreives
      user FORUM user and saves it locally."""
  iUid = int(uid)

  try:
      user = User.objects.get(id=iUid)
  except User.DoesNotExist:
    cursor = connection.cursor()
    cursor.execute("""SELECT userid, username, usergroupid,
                      membergroupids, email
                      FROM %suser WHERE userid = %d"""
                   % (VBULLETIN_CONFIG['tableprefix'], iUid))
    row = cursor.fetchone()
    user = User(id=iUid, username=row[1], email=row[4])

    user.is_staff = False
    user.is_superuser = False
  
    # Process primary usergroup
    if row[2] in VBULLETIN_CONFIG['superuser_groupids']:
      user.is_staff = True    
      user.is_superuser = True
    elif row[2] in VBULLETIN_CONFIG['staff_groupids']:
      user.is_staff = True
    
    # Process addtional usergroups
    for groupid in row[3].split(','):
      if groupid in VBULLETIN_CONFIG['superuser_groupids']:
        user.is_superuser = True
      if groupid in VBULLETIN_CONFIG['staff_groupids']:
        user.is_staff = True
    
    user.set_unusable_password()
    user.save()

  return user


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

