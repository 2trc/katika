from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from .views import TenderListView, TenderOwnerListView, ContractListView, titulaire_stats, \
    EntrepriseListView, get_enterprise, TenderViewSet, ContribuableSet, TenderOwnerViewSet
from rest_framework import routers


app_name = 'tender'
router = routers.DefaultRouter()

router.register('api/tenders', TenderViewSet, basename="ArmpEntry")
router.register('api/tender_owners', TenderOwnerViewSet, basename="TenderOwner")
router.register('api/contribuables', ContribuableSet, basename="Enterprise")


urlpatterns = [

    path('owners/', TenderOwnerListView.as_view()),
    path('contracts/titulaires/', titulaire_stats),
    path('contracts/', ContractListView.as_view()),
    path('contribuables/niu/(?P<niu>[A-Z0-9]+)/$', get_enterprise),
    path('contribuables/', EntrepriseListView.as_view()),
    path('', TenderListView.as_view(), name='tender-list'),
    path('', include(router.urls)),
]