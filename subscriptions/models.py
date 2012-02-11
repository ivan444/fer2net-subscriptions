# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db import connection
from subscriptions.auth import VBULLETIN_CONFIG
from datetime import datetime, timedelta
import logging


def activateMember(user):
  """Aktiviranje korisnika."""
  cursor = connection.cursor()

  if (str(usergroupid(user)) in VBULLETIN_CONFIG['standard_groupids']):
    query = """
             UPDATE %suser
             SET `usergroupid` = %s
             WHERE userid = %s
          """
  else:
    query = """
             UPDATE %suser
             SET `membergroupids` = TRIM(LEADING ',' FROM CONCAT(`membergroupids`, ',%s'))
             WHERE userid = %s
          """

  cursor.execute(query % (VBULLETIN_CONFIG['tableprefix'], VBULLETIN_CONFIG['paid_03_2013_groupid'], user.id))

  user.profile.subscribed = True
  user.save()


def deactivateMember(user):
  """Deaktiviranje korisnika."""
  cursor = connection.cursor()

  if (usergroupid(user) == int(VBULLETIN_CONFIG['paid_03_2013_groupid'])):
    query = """
             UPDATE %suser
             SET `usergroupid` = %s
             WHERE userid = %s
          """
    cursor.execute(query % (VBULLETIN_CONFIG['tableprefix'], VBULLETIN_CONFIG['not_paid_groupid'], user.id))
  else:
    query = """
             UPDATE %suser
             SET `membergroupids` = TRIM(LEADING ',' FROM REPLACE(`membergroupids`, '%s', ''))
             WHERE userid = %s
          """
    cursor.execute(query % (VBULLETIN_CONFIG['tableprefix'], VBULLETIN_CONFIG['paid_03_2013_groupid'], user.id))

  user.profile.subscribed = False
  user.save()


def usergroupid(user):
  """ Vraća usergroupid zadanog korisnika. """
  cursor = connection.cursor()
  cursor.execute("""SELECT usergroupid FROM %suser WHERE userid = %s"""
                 % (VBULLETIN_CONFIG['tableprefix'], user.id))
  row = cursor.fetchone()
  return row[0]

class UserProfile(models.Model):
  user = models.ForeignKey(User, unique=True)
  subscribed = models.BooleanField(default=False)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


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
                      FROM """ + VBULLETIN_CONFIG['tableprefix'] + """user WHERE userid = %d""",
                   [iUid])

    allRows = cursor.fetchall()
    if len(allRows) == 0: return None
    else: row = allRows[0]

    user = User(id=iUid, username=row[1], email=row[4])

    user.is_staff = False
    user.is_superuser = False

    # Process primary usergroup
    if row[2] in VBULLETIN_CONFIG['superuser_groupids']:
      user.is_staff = True    
      user.is_superuser = True
    elif row[2] in VBULLETIN_CONFIG['staff_groupids']:
      user.is_staff = True

    # Check if user is subscribed
    if r[2] == VBULLETIN_CONFIG['paid_03_2013_groupid'] or VBULLETIN_CONFIG['paid_03_2013_groupid'] in r[3]:
      user.profile.subscribed = True

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

  # bill comment
  comment = models.CharField(max_length=256)

class BillForm(forms.ModelForm):
  # enable custom date widget
  formfield_callback = makeCustomDatefield
  class Meta:
    model = Bill


class EBankingSubForm(forms.Form):
  userid = forms.IntegerField(min_value=0)
  amount = forms.IntegerField(min_value=0)
  date = forms.DateField()

  def save(self):
    if self.cleaned_data == {}: return None
    # TODO: ovo ne mora biti točno!!! dodati u config? ebaniking_paymaster_id? bolje: hidden field forme - id trenutno logiranog korisnika
    admin = User.objects.get(pk=1)

    user = fetchUser(self.cleaned_data["userid"])
    if user == None:
      logging.warn("User with ID '%s' doesn't exist in Forum DB!" % (self.cleaned_data["userid"],))
      return None

    # skip if already subscribed
    if user.profile.subscribed:
      logging.warn("User with ID '%s' is already subscribed!" % (self.cleaned_data["userid"],))
      return None

    amount = self.cleaned_data["amount"]
    date = self.cleaned_data["date"]
    s = Subscription(user=user, amount=amount, date=date, paymentType='E', subsEnd=date+timedelta(days=365))
    s.paymaster=admin
    s.save()
    activateMember(user)
    logging.debug("User with ID '%s' is now subscribed using e-banking." % (self.cleaned_data["userid"],))
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

