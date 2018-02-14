from django.conf.urls import url, include
from rest_framework import routers
from . import views



# urlpatterns = [
#     url(r'', incident_home),
#     ]


router = routers.DefaultRouter()
#router.register(r'api/type', IncidentTypeViewSet)
router.register(r'api/event', views.EventViewSet)
router.register(r'api/personnage', views.PersonnageViewSet)
#router.register(r'api/university', UniversityViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', views.khistory_home),
    url(r'^archive$', views.khistory_archive),
    url(r'^event/add', views.add_event),
    url(r'^personnage/add', views.add_personnage),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]