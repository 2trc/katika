from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from . import views

app_name ="khistory"

# urlpatterns = [
#     url(r'', incident_home),
#     ]


router = routers.DefaultRouter()
#router.register(r'api/type', IncidentTypeViewSet)
router.register('api/event', views.EventViewSet, base_name="Event")
router.register('api/personnage', views.PersonnageViewSet)
#router.register(r'api/university', UniversityViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.khistory_home),
    path('archive$', views.khistory_archive),
    path('event/add', views.add_event),
    path('personnage/add', views.add_personnage),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
]