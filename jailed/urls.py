from django.conf.urls import url, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'api/incarcerations', views.IncarcerationViewSet, base_name="Incarceration")

urlpatterns = [
    url(r'^$', views.jailed_home),
    url(r'^', include(router.urls))
    ]