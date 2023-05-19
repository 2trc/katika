from django.urls import path
from anycluster import views
from django.conf import settings

app_name = "anycluster"

urlpatterns = [
    path('grid/<int:zoom>/<int:gridSize>/', views.getGrid, name='getGrid'),
    path('kmeans/<int:zoom>/<int:gridSize>/', views.getPins, name='getPins'),
    path('getClusterContent/<int:zoom>/<int:gridSize>/', views.getClusterContent, name='getClusterContent'),
    path('getAreaContent/<int:zoom>/<int:gridSize>/', views.getAreaContent, name='getAreaContent'),
]
