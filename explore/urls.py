from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': '/Users/friendofrobots/code/ice-divisi/explore/media'}),
    url(r'^p/(\d+)$', 'air.views.object', name='object'),
    url(r'^compare/(\d+)$', 'air.views.compareTo', name='compareTo'),
    url(r'^compare/(\d+)/(\d+)$', 'air.views.compare', name='compare'),
    url(r'^categories/$', 'air.views.categories', name='categories'),
    url(r'^category/$', 'air.views.category', name='category'),
    url(r'^projection/(\d+)/(\d+)$', 'air.views.projection', name='projection'),
    url(r'^$', 'air.views.explore', name='explore'),
)
