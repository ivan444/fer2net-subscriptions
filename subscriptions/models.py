# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db import connection
from subscriptions.auth import VBULLETIN_CONFIG
from datetime import datetime, timedelta

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

    # Process additional usergroups
    for groupid in row[3].split(','):
      if groupid in VBULLETIN_CONFIG['superuser_groupids']:
        user.is_superuser = True
      if groupid in VBULLETIN_CONFIG['staff_groupids']:
        user.is_staff = True
    
    user.set_unusable_password()
    user.save()

  return user


# Custom date widget for date field
def makeCustomDatefield(f):
  formfield = f.formfield()
  if isinstance(f, models.DateField):
    formfield.widget.format = '%m/%d/%Y'
    formfield.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
  return formfield

# Service bill (bill for hosting, licenses, etc.)
class Bill(models.Model):
  BILL_TYPES = (
    ('H', 'forum hosting'),
    ('M', 'materials hosting'),
    ('F', 'forum licenses'),
    ('W', 'windows licenses'),
    ('D', 'domain'),
    ('O', 'other expenses'),
  )
  BILL_TYPES_DICT = dict(BILL_TYPES)

  billType = models.CharField(max_length=1, choices=BILL_TYPES)

  # bill amount (size of bill)
  amount = models.IntegerField()

  # date of payment 
  date = models.DateTimeField()

  # date of expiration of service
  expirationDate = models.DateTimeField()

  # academic year in which this bill belongs to (format: "yyyy/yyyy", eg. "2006/2007")
  academicYear = models.CharField(max_length=9)

class BillForm(forms.ModelForm):
  # enable custom date widget
  formfield_callback = makeCustomDatefield
  class Meta:
    model = Bill


class EBankingSubForm(forms.Form):
  userid = forms.IntegerField(min_value=0)
  amount = forms.IntegerField(min_value=0)
  date = forms.DateField()#input_formats='%d.%m.%Y.')

  def save(self):
    if self.cleaned_data == {}: return None
    # TODO: ovo ne mora biti točno!!! dodati u config? ebaniking_paymaster_id? bolje: hidden field forme - id trenutno logiranog korisnika
    admin = User.objects.get(pk=1)
    # TODO: provjeri postoji li user!!!!
    user = fetchUser(self.cleaned_data["userid"])
    amount = self.cleaned_data["amount"]
    date = self.cleaned_data["date"]
    s = Subscription(user=user, amount=amount, date=date, paymentType='E', subsEnd=date+timedelta(days=365))
    s.paymaster=admin
    s.save()
    return s


class EBankingUploadForm(forms.Form):
  paymentsFile = forms.FileField(label='XML - uplate')


# User subscription
class Subscription(models.Model):
  # user who paid for subscription
  user = models.ForeignKey(User, unique=False, null=False, related_name="subscriptions")

  # payment amount
  amount = models.IntegerField()

  # payment is delayed but subscription is active
  delayed = models.BooleanField(default=False)

  # date of payment
  date = models.DateTimeField()

  # date of subscription end
  subsEnd = models.DateTimeField()

  # type of payment - eBanking, inPerson
  PAYMENT_CHOICES = (
    ('E', 'e-banking'),
    ('P', 'in person'),
  )
  paymentType = models.CharField(max_length=1, choices=PAYMENT_CHOICES)

  # who has received payment (admin for eBanking)
  paymaster = models.ForeignKey(User, unique=False, null=False, related_name="processed_payments")

  # is record valid
  valid = models.BooleanField(default=True)

