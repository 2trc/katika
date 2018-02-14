from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from .views import blog_home, blog_page



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', blog_home),
    url(r'^(?P<page_slug>[\w-]+)', blog_page)
]
