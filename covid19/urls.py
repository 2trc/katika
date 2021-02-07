from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from . import views

# https://docs.djangoproject.com/en/3.0/topics/class-based-views/intro/

urlpatterns = [
    url(r'^$', views.covid_home),

    url(r'producers/(?P<pk>\d+)/edit/$', permission_required('covid19.change_covidproducer')(views.ProducerUpdate.as_view()),
        name='update-producer'),
    url(r'producers/add/$', permission_required('covid19.add_covidproducer')(views.ProducerCreate.as_view()),
        name='add-producer'),
    url(r'producers/$', views.ProducerList.as_view(), name='producer-list'),

    url(r'initiatives/(?P<pk>\d+)/edit/$', permission_required('covid19.change_covidinitiative')(views.InitiativeUpdate.as_view()),
        name='update-initiative'),
    url(r'initiatives/add/$', permission_required('covid19.add_covidinitiative')(views.InitiativeCreate.as_view()),
        name='add-initiative'),
    url(r'initiatives/$', views.InitiativeList.as_view(), name='initiative-list'),

    url(r'funds/(?P<pk>\d+)/edit/$', permission_required('covid19.change_covidfund')(views.FundUpdate.as_view()),
        name='update-fund'),
    url(r'funds/add/$', permission_required('covid19.add_covidfund')(views.FundCreate.as_view()),
        name='add-fund'),
    url(r'funds/$', views.FundList.as_view(), name='fund-list'),
    ]