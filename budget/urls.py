from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.budget_global),
    url(r'^add-budget-programme', views.budgetprogramme_add),
    url(r'^region', views.region),
    url(r'^prog$', views.budget_programme),
    ]
