from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
from subsf2net import settings
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^index$', 'subsf2net.subscriptions.views.index', name='index'),
  url(r'^staff$', 'subsf2net.subscriptions.views.indexStaff', name='staff'),
  url(r'^superuser$', 'subsf2net.subscriptions.views.indexSuperuser', name='superuser'),
  url(r'^member$', 'subsf2net.subscriptions.views.indexMember', name='member'),
  url(r'^stats$', 'subsf2net.subscriptions.views.stats', name='stats'),
  url(r'^$', 'subsf2net.subscriptions.views.index', name='index-clean'),
  url(r'^payment/ebanking/file$', 'subsf2net.subscriptions.views.importEbankingFile', name='ebanking_payment'),
  url(r'^payment/ebanking/process$', 'subsf2net.subscriptions.views.importEbankingPayments', name='ebanking_payment_mult'),
  url(r'^payment/make$', 'subsf2net.subscriptions.views.makePayment', name='make_payment'),
  url(r'^payment/make/(?P<uid>[\d ]+)/(?P<amount>\d+)$', 'subsf2net.subscriptions.views.makePayment', name='make_payment'),
  url(r'^payment/delete$', 'subsf2net.subscriptions.views.deletePayment', name='delete_payment'),
  url(r'^payment/delete/(?P<uid>[\d ]+)$', 'subsf2net.subscriptions.views.deletePayment', name='delete_payment'),
  url(r'^payment/superuser/delete$', 'subsf2net.subscriptions.views.superuserDeletePayment', name='superuser_delete_payment'),
  url(r'^payment/superuser/delete/(?P<sid>[\d ]+)$', 'subsf2net.subscriptions.views.superuserDeletePayment', name='superuser_delete_payment'),
  url(r'^login$', 'subsf2net.subscriptions.views.loginview', name='loginview'),
  url(r'^logout$', 'subsf2net.subscriptions.views.logoutview', name='logout'),
  #url(r'^admin/', include(admin.site.urls)),
  url(r'^site_media/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/'}, name="templates"),
  url(r'^site_media/images/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/images'}, name="images"),
  url(r'^site_media/js/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/js'}, name="js"),
  url (r'^favication.ico$', 'django.views.static.serve', { 'document_root': settings.SITE_ROOT + '/templates/'}, name="favication"),
  url(r'^.*$', 'subsf2net.subscriptions.views.index', name='index'),
)

