from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from rest_framework import routers
from .views import incident_home, incident_geo_serialize,IncidentViewSet, \
    IncidentTypeViewSet, incident_add, incident_edit, incident_aggregation, \
    incident_stats, anycluster, tags_facet




# urlpatterns = [
#     url('', incident_home),
#     ]

app_name = "incident"
router = routers.DefaultRouter()
router.register('api/type', IncidentTypeViewSet)
router.register('api', IncidentViewSet, basename="Incident")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', incident_home),
    path('', include(router.urls)),
    path('add', incident_add),
    #path('edit/<uuid:pk>/', incident_edit),
    path('edit', incident_edit),
    path('aggregate', incident_aggregation),
    path('stats', incident_stats),
    path('tags_facet', tags_facet),
    path('geojson', incident_geo_serialize),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('anycluster', anycluster)
]
