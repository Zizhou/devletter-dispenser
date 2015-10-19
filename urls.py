from django.conf.urls import patterns, url

from dispenser import views

urlpatterns = patterns('',
    url(r'^$', views.main_page, name = 'main'),
    url(r'submit/', views.submit, name = 'submit'),
    url(r'retrieve/$', views.retrieve, name = 'retrieve'),
    url(r'^api/get_notes/(?P<game_id>\d+)/$', views.get_notes, name = 'get_notes'),
    url(r'^retrieve/get/(?P<game_id>\d+)/$', views.retrieve_code, name = 'get_code'),
    url(r'batch/$', views.batch, name = 'batch'),
    url(r'^batch/get/(?P<game_id>\d+)/$', views.batch_code, name = 'batch_code'),
    url(r'find/$', views.find, name = 'find'),
    url(r'codepocalypse/$', views.rand, name = 'codepocalypse'),
    url(r'auto/$', views.auto_main, name = 'auto'),
    url(r'auto/get$', views.auto_get, name = 'auto_get'),
    url(r'auto/return$', views.auto_return, name = 'auto_return'),
    url(r'auto/donate/$', views.auto_donate, name = 'auto_donate'),
    url(r'auto/ticket/$', views.auto_ticket, name = 'auto_ticket'),
    url(r'raffle/$', views.raffle, name = 'raffle'),
    url(r'bulk_export/$', views.bulk_export, name = 'bulk'),
)
