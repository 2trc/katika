from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from . import views



# urlpatterns = [
#     url(r'', incident_home),
#     ]


router = routers.DefaultRouter()
#router.register(r'api/type', IncidentTypeViewSet)
router.register(r'api/thesis', views.ThesisViewSet)
router.register(r'api/scholar/(?P<slug>[-\w]+)', views.ScholarViewSet, 'scholar_slug')
router.register(r'api/scholar', views.ScholarViewSet, 'scholar_list')
router.register(r'api/university', views.UniversityViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', views.kthesis_home),
    url(r'^add-thesis', views.add_thesis),
    url(r'^add-scholar', views.add_author),
    url(r'^scholar/(?P<slug>[-\w]+)', views.kthesis_author),
    url(r'^university/(?P<id>[\d]+)', views.kthesis_university),
    url(r'^year/(?P<id>[\d]+)', views.kthesis_year),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
