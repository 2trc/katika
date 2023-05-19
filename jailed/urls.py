from django.conf.urls import include
from django.urls import path
from . import views
from rest_framework import routers

app_name ="jailed"
router = routers.DefaultRouter()

router.register('api/incarcerations', views.IncarcerationViewSet, basename="Incarceration")

urlpatterns = [
    path('', views.jailed_home),
    path('', include(router.urls))
]