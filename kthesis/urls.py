from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from rest_framework import routers
from . import views


app_name = "kthesis"

# urlpatterns = [
#     url(r'', incident_home),
#     ]


router = routers.DefaultRouter()
#router.register(r'api/type', IncidentTypeViewSet)
router.register('api/thesis', views.ThesisViewSet)
router.register('api/scholar/<slug:slug>', views.ScholarViewSet, 'scholar_slug')
router.register('api/scholar', views.ScholarViewSet, 'scholar_list')
router.register('api/university', views.UniversityViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.kthesis_home),
    path('add-thesis', views.add_thesis),
    path('add-scholar', views.add_author),
    path('scholar/<slug:slug>', views.kthesis_author),
    path('university/<int:id>', views.kthesis_university),
    path('year/<int:id>', views.kthesis_year),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
]
