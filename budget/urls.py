
from django.urls import path

from . import views

app_name = 'budget'
urlpatterns = [
    path('', views.budget_global),
    path('add-budget-programme', views.budgetprogramme_add),
    path('region', views.region),
    path('prog', views.budget_programme),
    ]
