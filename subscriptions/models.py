# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User

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
  date = forms.DateTimeField(input_formats='%d.%m.%Y.')


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

