from django.conf.urls import url, include
from django.contrib import admin
from .views import TenderListView, TenderOwnerViewset
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'api/owner', TenderOwnerViewset, base_name='TenderOwner')


urlpatterns = [

    #url(r'q=(?P<search>[\w]+)', TenderListView.as_view()),
    url(r'^$', TenderListView.as_view(), name='tender-list'),
    url(r'^', include(router.urls)),
    #url(r'^(?P<page_slug>[\w-]+)', transcript_page),
]