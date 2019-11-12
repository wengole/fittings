from django.urls import path
from django.conf.urls import url


from . import views

app_name = 'fittings'

urlpatterns = [
    url(r'^$', views.test, name='test')
]