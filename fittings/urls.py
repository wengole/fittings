from django.urls import path
from django.conf.urls import url


from . import views

app_name = 'fittings'

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^fit/add/$', views.add_fit, name='add_fit'),
]