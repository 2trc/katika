from django.urls import path
from .views import TranscriptListView, transcript_page

app_name = "transcribe"

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', TranscriptListView.as_view(), name='transcript-list'),
    path('<slug:page_slug>', transcript_page),
]