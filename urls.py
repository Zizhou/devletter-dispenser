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

)
