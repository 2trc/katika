from django.shortcuts import render
# Create your views here.
from .models import Transcript
from django.views.generic.list import ListView


def transcribe_home(request):

    transcripts = Transcript.objects.all()

    return render(request, 'transcript_index.html', {'transcripts': transcripts})


def transcript_page(request, page_slug):

    transcript = Transcript.objects.get(slug=page_slug)

    return render(request, 'transcript_detail.html', {'transcript': transcript})


class TranscriptListView(ListView):

    model = Transcript
    paginate_by = 100

