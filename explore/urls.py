from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    url(r'^/p/(\w+)$', 'air.views.object', name='object'),
    url(r'^/compare/(\w+)$', 'air.views.compareTo', name='compareTo'),
    url(r'^/compare/(\w+)/(\w+)$', 'air.views.compare', name='compare'),
    url(r'^/categories/$', 'air.views.categories', name='categories'),
    url(r'^/category/$', 'air.views.category', name='category'),
    url(r'^/projection/(\w+)/(\w+)$', 'air.views.projection', name='projection'),
    url(r'^$', 'air.views.explore', name='explore'),
)
