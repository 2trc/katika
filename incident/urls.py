from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from .views import incident_home, IncidentViewSet, IncidentTypeViewSet


# urlpatterns = [
#     url(r'', incident_home),
#     ]


router = routers.DefaultRouter()
router.register(r'api/type', IncidentTypeViewSet)
router.register(r'api', IncidentViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', incident_home),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]