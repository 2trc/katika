from django.conf.urls import  include
from django.urls import path
from django.contrib import admin
from rest_framework import routers
from .views import blog_home, blog_page


app_name = "kblog"
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', blog_home),
    path('<slug:page_slug>', blog_page)
]
