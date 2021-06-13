from django.conf.urls import url, include
from django.contrib import admin
from .views import TranscriptListView, transcript_page



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^$', TranscriptListView.as_view(), name='transcript-list'),
    url(r'^(?P<page_slug>[\w-]+)', transcript_page),
]