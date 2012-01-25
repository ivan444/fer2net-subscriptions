from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^index$', 'subscriptions.views.index', name='index'),
  url(r'^staff$', 'subscriptions.views.indexStaff', name='staff'),
  url(r'^superuser$', 'subscriptions.views.indexSuperuser', name='superuser'),
  url(r'^member$', 'subscriptions.views.indexMember', name='member'),
  url(r'^stats$', 'subscriptions.views.stats', name='stats'),
  url(r'^$', 'subscriptions.views.index', name='index-clean'),
  url(r'^payment/ebanking/file$', 'subscriptions.views.importEbankingFile', name='ebanking_payment'),
  url(r'^payment/ebanking/process$', 'subscriptions.views.importEbankingPayments', name='ebanking_payment_mult'),
  url(r'^payment/make$', 'subscriptions.views.makePayment', name='make_payment'),
  url(r'^payment/make/(?P<uid>[\d ]+)/(?P<amount>\d+)$', 'subscriptions.views.makePayment', name='make_payment'),
  url(r'^payment/delete$', 'subscriptions.views.deletePayment', name='delete_payment'),
  url(r'^payment/delete/(?P<uid>[\d ]+)$', 'subscriptions.views.deletePayment', name='delete_payment'),
  url(r'^login$', 'subscriptions.views.loginview', name='loginview'),
  url(r'^logout$', 'subscriptions.views.logoutview', name='logout'),
  #url(r'^admin/', include(admin.site.urls)),
  url(r'^site_media/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/'}, name="templates"),
  url(r'^site_media/images/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/images'}, name="images"),
  url(r'^site_media/js/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/js'}, name="js"),
  url (r'^favication.ico$', 'django.views.static.serve', { 'document_root': settings.SITE_ROOT + '/templates/'}, name="favication"),
  url(r'^.*$', 'subscriptions.views.index', name='index'),
)

