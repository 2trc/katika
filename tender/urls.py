from django.conf.urls import url, include
from django.contrib import admin
from .views import TenderListView, TenderOwnerListView, ContractListView, titulaire_stats, \
    EntrepriseListView, get_enterprise, TenderViewSet, ContribuableSet, TenderOwnerViewSet, \
    WBContractListView
from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'api/tenders', TenderViewSet, base_name="ArmpEntry")
router.register(r'api/tender_owners', TenderOwnerViewSet, base_name="TenderOwner")
router.register(r'api/contribuables', ContribuableSet, base_name="Enterprise")


urlpatterns = [

    url(r'^owners/$', TenderOwnerListView.as_view()),
    url(r'^contracts/titulaires/$', titulaire_stats),
    url(r'^contracts/$', ContractListView.as_view()),
    url(r'^contribuables/niu/(?P<niu>[A-Z0-9]+)/$', get_enterprise),
    url(r'^contribuables/$', EntrepriseListView.as_view()),
    url(r'^wbcontracts/$', WBContractListView.as_view()),
    url(r'^$', TenderListView.as_view(), name='tender-list'),
    url(r'^', include(router.urls)),
]