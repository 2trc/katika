from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import EventSerializer, Event, PersonnageSerializer, Personnage \
    , EventForm, PersonnageForm
from django.http import HttpResponseRedirect
from rest_framework.pagination import PageNumberPagination
# Create your views here.

def khistory_home(request):

    return render(request, 'khistory.html')

def khistory_archive(request):

    return render(request, 'archive.html')


# http://www.tivix.com/blog/upgrading-to-django-rest-framework-31-pagination
class NotPaginatedSetPagination(PageNumberPagination):
    page_size = None


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = EventSerializer
    queryset = Event.objects.all()

    pagination_class = NotPaginatedSetPagination


class PersonnageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = PersonnageSerializer
    queryset = Personnage.objects.all()


def add_event(request):

    form = EventForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect('/khistory')

    return render(request, 'add_event.html', {'form': form})

def add_personnage(request):

    form = PersonnageForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect('/khistory')

    return render(request, 'add_personnage.html', {'form': form})