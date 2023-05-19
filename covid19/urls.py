from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from . import views


app_name="covid19"

urlpatterns = [
    path('', views.covid_home),

    path('producers/<int:pk>/edit/', permission_required('covid19.change_covidproducer')(views.ProducerUpdate.as_view()),
        name='update-producer'),
    path('producers/add/', permission_required('covid19.add_covidproducer')(views.ProducerCreate.as_view()),
        name='add-producer'),
    path('producers/', views.ProducerList.as_view(), name='producer-list'),

    path('initiatives/<int:pk>/edit/', permission_required('covid19.change_covidinitiative')(views.InitiativeUpdate.as_view()),
        name='update-initiative'),
    path('initiatives/add/$', permission_required('covid19.add_covidinitiative')(views.InitiativeCreate.as_view()),
        name='add-initiative'),
    path('initiatives/$', views.InitiativeList.as_view(), name='initiative-list'),

    path('funds/<int:pk>/edit/', permission_required('covid19.change_covidfund')(views.FundUpdate.as_view()),
        name='update-fund'),
    path('funds/add/', permission_required('covid19.add_covidfund')(views.FundCreate.as_view()),
        name='add-fund'),
    url('funds/', views.FundList.as_view(), name='fund-list'),
    ]