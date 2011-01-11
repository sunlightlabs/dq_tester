from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'cfda.views.index', name='index'),
    url(r'^agency/(?P<cfda_id>\d{2})', 'agency.views.agency' ),
    url(r'^program/(?P<number>\d{2}\.\d{3})', 'cfda.views.cfda' ),
    url(r'^failed/$', 'agency.views.failed', name='failed'),
    url(r'^nottested/$', 'agency.views.nottested', name='nottested'),
    # Example:
    # (r'^dq_tester/', include('dq_tester.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )


