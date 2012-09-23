from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'v2.views.home', name='home'),
    # url(r'^v2/', include('v2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', direct_to_template, {'template': 'not_authenticated.html'}), 
    url(r'^Login$', 'core.views.login_view'),
    url(r'^Logout$', 'core.views.logout_view'),
    url(r'^CreateAccount$', 'core.views.create_account_view'),
    url(r'^Home$', 'core.home.index'),
    url(r'^ChatInit$', 'core.chat.init'),
    url(r'^Chat/Message/Post$', 'core.chat.message_post'),
    url(r'^Chat/Message/History$', 'core.chat.return_history'),
)
urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
