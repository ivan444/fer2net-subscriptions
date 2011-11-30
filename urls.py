from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^$', 'subscriptions.views.index', name='index'),
  url(r'^login$', 'subscriptions.views.loginview', name='loginview'),
  url(r'^logout$', 'subscriptions.views.logoutview', name='logout'),
  url(r'^drugi$', 'subscriptions.views.drugi', name='drugi'),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^site_media/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/'}, name="templates"),
  url(r'^site_media/images/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/images'}, name="images"),
  url(r'^site_media/js/(?P<path>[a-zA-Z\-\._0-9]+)$', 'django.views.static.serve', {'document_root': settings.SITE_ROOT + '/templates/js'}, name="js"),
)

