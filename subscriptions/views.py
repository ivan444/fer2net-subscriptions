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
from subsf2net.subscriptions.auth import VBULLETIN_CONFIG
from subsf2net import settings
from subsf2net.subscriptions.models import Subscription, Bill, BillForm, EBankingUploadForm, EBankingSubForm, fetchUser, activateMember, deactivateMember

logger = logging.getLogger('subscriptions')

@login_required 
def index(request):
  if request.user.is_superuser:
    return indexSuperuser(request)
  elif request.user.is_staff and settings.cfgSubsPeriod:
    return indexStaff(request)
  else:
    return indexMember(request)


@login_required 
def indexMember(request):
  subs = Subscription.objects.filter(user__id = request.user.id).filter(valid=True).order_by('-date').all()
  return render_to_response('index-member.html', {'username': request.user.username, 'subs': subs})


@login_required 
def indexSuperuser(request, msg_info=None):
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  if request.method == "POST":
    form = BillForm(request.POST)
    if form.is_valid():
      bill = form.save()
  else:
    form = BillForm()

  subs = Subscription.objects.order_by('-date').all()
  bills = Bill.objects.order_by('-date').all()

  return render_to_response('index-superuser.html', {'msg_info':msg_info, 'username': request.user.username, 'allSubs': subs, 'bill_form': form, 'allBills': bills, 'billTypes': Bill.BILL_TYPES_DICT}, context_instance=RequestContext(request))


@login_required 
def indexStaff(request):
  if not ((request.user.is_staff and settings.cfgSubsPeriod) or request.user.is_superuser):
    return HttpResponse("user is not staff member or subs. collection period is over!", status=403)

  cursor = connection.cursor()

  cursor.execute("""SELECT userid, usergroupid, membergroupids, username, email
                    FROM %suser"""
                 % (VBULLETIN_CONFIG['tableprefix']))
  rows = cursor.fetchall()
  allUsers = []
  for r in rows:
    usr = {}
    usr["userid"] = r[0]
    iMGids = []
    for rgid in r[2].split(","):
      if rgid == '': continue
      else: iMGids.append(int(rgid))

    if int(r[1]) == VBULLETIN_CONFIG['paid_groupid'] or VBULLETIN_CONFIG['paid_groupid'] in iMGids:
      usr["valid"] = True
    else:
      usr["valid"] = False
    usr["username"] = r[3]
    usr["email"] = r[4]
    #subs = Subscription.objects.filter(user__id = int(r[0])).order_by('-date').all()
    #if len(subs) == 0:
    #  usr["sub_expr"] = -365
    #else:
    #  td = datetime.now() - subs[0].date
    #  usr["sub_expr"] = max(-365, 365-td.days)

    allUsers.append(usr)

  return render_to_response('index-staff.html', {'allUsers': allUsers})


@login_required 
def makePayment(request, uid=None, amount=None):
  """
  Make payment for user (create subscription).
  """
  if uid==None or amount==None: return Http404("no params")
  if not ((request.user.is_staff and settings.cfgSubsPeriod) or request.user.is_superuser):
    return HttpResponse("user is not staff member or subs. collection period is over!", status=403)

  intAmount = int(amount)

  request.session.modified = True

  user = fetchUser(uid)
  (actOk, oldGid) = activateMember(user)

  if not actOk:
    logger.warn("Failed to activate in-person (live) payment for user (%d, %s) by paymaster (%d, %s), amount %d." % (user.id, user.username, request.user.id, request.user.username, intAmount))
    return HttpResponse('{status:"failed"}', mimetype='application/javascript; charset=utf8', status=400)

  sub = Subscription(user=user, amount=intAmount)
  sub.oldGroupId = oldGid
  sub.delayed = intAmount == 0
  sub.paymaster = request.user
  sub.paymentType = 'P'
  sub.date = datetime.now()
  sub.subsEnd = sub.date + timedelta(days=365)
  sub.save()

  logger.info("Made in-person (live) payment for user (%d, %s) by paymaster (%d, %s), amount %d." % (user.id, user.username, request.user.id, request.user.username, intAmount))

  return HttpResponse('{status:"ok"}', mimetype='application/javascript; charset=utf8')


@login_required
def superuserDeletePayment(request, sid=None):
  """
  Delete payment (subscription) with id = sid. This is superuser only method!
  """
  if sid==None: return Http404("no params")
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  iSid = int(sid)
  deactOk = False
  try:
    s = Subscription.objects.get(pk=iSid)
    if s.valid:
      snewst = s.user.subscriptions.filter(valid=True).order_by('-subsEnd')[0]
      if snewst.id == s.id:
        deactOk = deactivateMember(s.user, s.oldGroupId)
  except Subscription.DoesNotExist:
    return HttpResponse("subscription with ID %d does not exist!" % (sid,), status=404)

  request.session.modified = True

  if deactOk:
    logger.info("Superuser (%s) deleted subscription with ID %d (date, user, userId) = (%s, %s, %d)." % (request.user.username, s.id, s.date, s.user.username, s.user.id))
    s.delete()
    return HttpResponse('{status:"ok"}', mimetype='application/javascript; charset=utf8')
  else:
    logger.warn("Superuser (%s) FAILED to delete subscription with ID %d (date, user, userId) = (%s, %s, %d)." % (request.user.username, s.id, s.date, s.user.username, s.user.id))
    return HttpResponse('{status:"failed"}', mimetype='application/javascript; charset=utf8', status=400)


@login_required
def deletePayment(request, uid=None):
  """
  Delete payment (subscription) of User with id == uid which is made today.
  Subscription will be deleted ONLY IF (s.paymaster == request.user AND s.date == today).
  """
  if uid==None: return Http404("no params")
  if not ((request.user.is_staff and settings.cfgSubsPeriod) or request.user.is_superuser):
    return HttpResponse("user is not staff member or subs. collection period is over!", status=403)

  user = fetchUser(uid)
  nw = datetime.now()
  ss = Subscription.objects.filter(user__id = int(uid)).filter(paymaster = request.user).filter(valid = True).filter(date__year = nw.year).filter(date__month = nw.month).filter(date__day = nw.day).order_by('-date').all()
  request.session.modified = True
  if len(ss) == 0:
    return HttpResponse("there are no subscriptions to delete", status=404)
  else:
    sub = ss[0]
    deactOk = deactivateMember(user, sub.oldGroupId)
    if deactOk:
      sub.valid = False
      sub.save()

      logger.info("Staff member (%s) invalidated (deleted) subscription with ID %d (date, user, userId) = (%s, %s, %d)" % (request.user.username, sub.id, sub.date, sub.user.username, sub.user.id))
      return HttpResponse('{status:"ok"}', mimetype='application/javascript; charset=utf8')
    else:
      logger.warn("Staff member (%s) FAILED to invalidate (delete) subscription with ID %d (date, user, userId) = (%s, %s, %d)" % (request.user.username, sub.id, sub.date, sub.user.username, sub.user.id))
      return HttpResponse('{status:"failed"}', mimetype='application/javascript; charset=utf8', status=400)


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
      c['msg_error'] = u"Zadali ste neispravan e-mail ili lozinku!"
   
  # show the form 
  return render_to_response('login.html', c)


def logoutview(request):
  """ Do user logout. """
  logout(request)
  return redirect("loginview")


def startOfAcYear(year):
  """
  Get start year of 'academic year' in which given
  year belongs. E.g.:
  year 2011 belongs to ac. year 2011/2012 - startOfAcYear(2011) == 2011
  year 2012 belongs to ac. year 2011/2012 - startOfAcYear(2012) == 2011 (!)
  """
  if year % 2 == 1: return year
  else: return year-1


@login_required
def stats(request):
  """
  Display statistics.
  """

  numberOfPayments = 0
  totalAmount = 0
  totalExpense = 0
  totalInPerson = 0
  totalEBanking = 0
  amountByYear = {}
  expenseByYear = {}
  inPersonByYear = {}
  paymentsByYear = {}
  ebByYear = {}
  aYears = set()

  subs = Subscription.objects.filter(valid=True).filter(amount__gt=0).all()
  for s in subs:
    aYear = startOfAcYear(s.date.year)
    aYears.add(aYear)

    totalAmount += s.amount
    amountByYear[aYear] = s.amount + amountByYear.get(aYear,0)

    numberOfPayments += 1
    paymentsByYear[aYear] = 1 + paymentsByYear.get(aYear,0)

    if s.paymentType == 'P':
      totalInPerson += s.amount
      inPersonByYear[aYear] = s.amount + inPersonByYear.get(aYear,0)
    else:
      totalEBanking += s.amount
      ebByYear[aYear] = s.amount + ebByYear.get(aYear,0)
  
  bills = Bill.objects.all()
  for b in bills:
    totalExpense += b.amount
    aYear = int(b.academicYear.split("/")[0])
    aYears.add(aYear)
    expenseByYear[aYear] = b.amount + expenseByYear.get(aYear,0)

  context = {
	  'numberOfPayments':numberOfPayments,
	  'paymentsByYear':paymentsByYear,
	  'totalAmount':totalAmount,
    'totalExpense':totalExpense,
    'totalInPerson':totalInPerson,
    'totalEBanking':totalEBanking,
    'amountByYear':amountByYear,
    'expenseByYear':expenseByYear,
    'inPersonByYear':inPersonByYear,
    'ebByYear':ebByYear,
    'aYears':aYears,
    'bills':bills,
    'billTypes': Bill.BILL_TYPES_DICT}

  return render_to_response('stat.html', context, context_instance=RequestContext(request))


def reformatDate(dtStr):
  """
  Transform date string from "dd.mm.yyyy." to "yyyy-mm-dd"
  """
  pts = dtStr.split(".")
  return pts[2]+"-"+pts[1]+"-"+pts[0]


def processUploadedPayments(xmlContents):
  """
  Parse e-banking payment records (XML transaction log).
  """
  payments = []
  doc = xml.dom.minidom.parseString(xmlContents)
  trans = doc.getElementsByTagName("transactions")[0]
  for t in trans.getElementsByTagName("transaction"):
    p = {}
    p["date"] = reformatDate(t.getAttribute("date"))
    p["userid"] = desc = t.getAttribute("description")
    amount = t.getElementsByTagName("receive")[0].getAttribute("amount")
    if "," in amount:
      p["amount"] = amount.split(",")[0]
    else:
      p["amount"] = "0"
    payments.append(p)
  return payments


@login_required 
def importEbankingFile(request):
  """
  Handle e-banking payments file (XML transaction log).
  """
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  msg_warning = None

  if request.method == "POST":
    form = EBankingUploadForm(request.POST, request.FILES)
    if form.is_valid():
      try:
        payments = processUploadedPayments(form.cleaned_data["paymentsFile"].read())
        PaymentFormSet = formset_factory(EBankingSubForm, extra=2)
        formset = PaymentFormSet(initial=payments)
        return render_to_response('payments-from-file.html', {'username': request.user.username, 'formset': formset}, context_instance=RequestContext(request))
      except Exception as e:
        msg_warning = "Error while processing e-banking file!"
        logger.error(msg_warning + "\n" + str(e))
  else:
    form = EBankingUploadForm()

  return render_to_response('payments-file.html', {'username': request.user.username, 'upload_form': form, 'msg_warning': msg_warning}, context_instance=RequestContext(request))


@login_required 
def importEbankingPayments(request):
  """
  Process e-banking payments (from web form data) and save subscriptions.
  """
  if not request.user.is_superuser:
    return HttpResponse("user is not superuser!", status=403)

  msgInfo = "<ul>"
  if request.method == "POST":
    PaymentFormSet = formset_factory(EBankingSubForm)
    formset = PaymentFormSet(request.POST)
    #if formset.is_valid():
    for frm in formset.forms:
      if frm.is_valid():
        ret = frm.save()
        if ret == None:
          logger.warn("Payment (uid = %s) skipped!" % (str(frm),))
          msgInfo += "<li>Payment skipped!</li>"
        else:
          logger.info("Payment (uid = %s) processed!" % (str(frm),))
          msgInfo += "<li>Payment processed!</li>"

      else:
        logger.error("Invalid e-banking payments form!")
        msgInfo += "<li>Payment invalid!</li>"
      #  return render_to_response('payments-from-file.html', {'username': request.user.username, 'formset': formset}, context_instance=RequestContext(request))
      #return render_to_response('superuser-errors.html', {'errors': formset.errors}, context_instance=RequestContext(request))

    msgInfo += "</ul>"

    return indexSuperuser(request, msgInfo)

  else:
    return redirect("ebanking_payment")

