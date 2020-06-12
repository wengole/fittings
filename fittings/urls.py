from django.urls import path
from django.conf.urls import url


from . import views

app_name = "fittings"

urlpatterns = [
    url(r"^$", views.dashboard, name="dashboard"),
    url(r"^fit/add/$", views.add_fit, name="add_fit"),
    url(r"^fit/all/$", views.view_all_fits, name="view_all_fits"),
    url(r"^fit/(?P<fit_id>[0-9]+)/$", views.view_fit, name="view_fit"),
    url(r"^fit/(?P<fit_id>[0-9]+)/delete/$", views.delete_fit, name="delete_fit"),
    url(r"^fit/(?P<fit_id>[0-9]+)/save/$", views.save_fit, name="save_fit"),
    url(r"^fit/(?P<fit_id>[0-9]+)/edit/$", views.edit_fit, name="edit_fit"),
    url(r"^doctrine/add/$", views.add_doctrine, name="add_doctrine"),
    url(
        r"^doctrine/(?P<doctrine_id>[0-9]+)/$",
        views.view_doctrine,
        name="view_doctrine",
    ),
    url(
        r"^doctrine/(?P<doctrine_id>[0-9]+)/delete/$",
        views.delete_doctrine,
        name="delete_doctrine",
    ),
    url(
        r"^doctrine/(?P<doctrine_id>[0-9]+)/edit/$",
        views.edit_doctrine,
        name="edit_doctrine",
    ),
]
