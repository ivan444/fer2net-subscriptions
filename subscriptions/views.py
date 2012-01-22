# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.template import RequestContext
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta
import logging
import md5
import xml.dom.minidom
from django.db import connection
from subscriptions.auth import VBULLETIN_CONFIG
from subscriptions.models import Subscription, Bill, BillForm, EBankingUploadForm, EBankingSubForm, fetchUser

@login_required 
def index(request):
  if request.user.is_superuser:
    return indexSuperuser(request)
  elif request.user.is_staff:
    return indexStaff(request)
  else:
    return indexMember(request)

@login_required 
def indexMember(request):
  subs = Subscription.objects.filter(user__id = request.user.id).order_by('-date').all()
  return render_to_response('index-member.html', {'username': request.user.username, 'subs': subs})


@login_required 
def indexSuperuser(request):
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  if request.method == "POST":
    form = BillForm(request.POST)
    if form.is_valid():
      bill = form.save()
  else:
    form = BillForm()

  bills = Bill.objects.order_by('-date').all()


  subs = Subscription.objects.order_by('-date').all()
  return render_to_response('index-superuser.html', {'username': request.user.username, 'allSubs': subs, 'bill_form': form, 'allBills': bills}, context_instance=RequestContext(request))


#TODO: close cursor
@login_required 
def indexStaff(request):
  if not (request.user.is_staff or request.user.is_superuser):
    return HttpResponse("user is not staff member!", status=403)

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
    subs = Subscription.objects.filter(user__id = int(r[0])).order_by('-date').all()
    if len(subs) == 0:
      usr["sub_expr"] = -365
    else:
      td = datetime.now() - subs[0].date
      usr["sub_expr"] = max(-365, 365-td.days)

    allUsers.append(usr)

  return render_to_response('index-staff.html', {'allUsers': allUsers})


@login_required 
def makePayment(request, uid=None, amount=None):
  if uid==None or amount==None: return Http404("no params")
  if not (request.user.is_staff or request.user.is_superuser):
    return HttpResponse("user is not staff member!", status=403)

  user = fetchUser(uid)
  intAmount = int(amount)
  sub = Subscription(user=user, amount=intAmount)
  sub.delayed = intAmount == 0
  sub.paymaster = request.user
  sub.paymentType = 'P'
  sub.date = datetime.now()
  sub.subsEnd = sub.date + timedelta(days=365)
  sub.save()

  request.session.modified = True

  activateMember(user)

  return HttpResponse('{status:"ok"}', mimetype='application/javascript; charset=utf8')


def activateMember(user):
  """Aktiviranje korisnika."""
  pass # TODO


@login_required 
def deletePayment(request, uid=None):
  if uid==None: return Http404("no params")
  if not (request.user.is_staff or request.user.is_superuser):
    return HttpResponse("user is not staff member!", status=403)

  user = fetchUser(uid)
  nw = datetime.now()
  ss = Subscription.objects.filter(user__id = int(uid)).filter(paymaster = request.user).filter(valid = True).filter(date__year = nw.year).filter(date__month = nw.month).filter(date__day = nw.day).order_by('-date').all()
  request.session.modified = True
  if len(ss) == 0:
    return HttpResponse("there are no subscriptions to delete", status=404)
  else:
    sub = ss[0]
    sub.valid = False
    sub.save()
    return HttpResponse('{status:"ok"}', mimetype='application/javascript; charset=utf8')


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
      return redirect(c['next'])
    else:
      c['wrong_login'] = True
   
  # show the form 
  return render_to_response('login.html', c)


def logoutview(request):
  logout(request)
  return redirect("loginview")


@login_required
def stats(request):
 # TODO
 # ukupno skupljeno po ak.godini,
 # ukupan trošak u akademskoj godini,
 # trenutno ukupno stanje f2 blagajne,
 # uplaćeno uživo/int. bankarstvom,
 # broj studenata koji je platio
  return redirect("index")


def processUploadedPayments(xmlContents):
  payments = []
  doc = xml.dom.minidom.parseString(xmlContents)
  trans = doc.getElementsByTagName("transactions")[0]
  for t in trans.getElementsByTagName("transaction"):
    p = {}
    p["date"] = t.getAttribute("date")
    p["userid"] = desc = t.getAttribute("description")
    p["amount"] = t.getElementsByTagName("receive")[0].getAttribute("amount")
    payments.append(p)
  return payments


@login_required 
def importEbankingFile(request):
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  if request.method == "POST":
    form = EBankingUploadForm(request.POST, request.FILES)
    if form.is_valid():
      try:
        payments = processUploadedPayments(form.cleaned_data["paymentsFile"].read())
        PaymentFormSet = formset_factory(EBankingSubForm, extra=2, can_delete=True)
        formset = PaymentFormSet(initial=payments)
        return render_to_response('payments-from-file.html', {'username': request.user.username, 'formset': formset}, context_instance=RequestContext(request))
      except:
        print "ERROR" # TODO sredi ovo
  else:
    form = EBankingUploadForm()

  return render_to_response('payments-file.html', {'username': request.user.username, 'upload_form': form}, context_instance=RequestContext(request))


@login_required 
def importEbankingPayments(request):
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  if request.method == "POST":
    PaymentFormSet = formset_factory(EBankingSubForm)
    formset = PaymentFormSet(request.POST)
    if formset.is_valid():
      for frm in formset.forms:
        print "save frm"
        frm.save()
    else:
      print "Invalid form!!"
      print formset.errors

    return redirect("superuser")

  else:
    return redirect("ebanking_payment")

