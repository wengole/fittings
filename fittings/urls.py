from django.urls import path
from django.conf.urls import url


from . import views

app_name = 'fittings'

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^fit/add/$', views.add_fit, name='add_fit'),
    url(r'^fit/(?P<fit_id>[0-9]+)/$', views.view_fit, name='view_fit'),
]