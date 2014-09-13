from django.conf.urls import patterns, url

from dispenser import views

urlpatterns = patterns('',
    url(r'^$', views.main_page, name = 'main'),
)
