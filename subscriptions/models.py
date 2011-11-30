from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
  user = models.ForeignKey(User, unique=True)

class Subscription(models.Model):
  # user who paid for subscription
  user = models.ForeignKey(User, unique=False, null=False, related_name="subscriptions")

  # payment amount
  amount = models.IntegerField()

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

  # if null: this subscription record is valid
  # if not null: subscription record was modified, child points to edited version of record
  child = models.OneToOneField(Subscription, null=True, related_name="parent")

