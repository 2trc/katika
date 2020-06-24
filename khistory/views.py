from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import EventSerializer, Event, PersonnageSerializer, Personnage \
    , EventForm, PersonnageForm
from django.http import HttpResponseRedirect
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.decorators import login_required, permission_required
from katika.models import ReadOnlyOrAdmin
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
    pagination_class = NotPaginatedSetPagination

    # TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]  # https://code.djangoproject.com/ticket/27154


    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Event.objects.all()
        # 1 - ALL
        importance = self.request.query_params.get('importance', 1)

        return queryset.filter(importance__gte=importance)


class PersonnageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = PersonnageSerializer
    queryset = Personnage.objects.all()
    # TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]  # https://code.djangoproject.com/ticket/27154


@login_required
@permission_required('khistory.add_event', raise_exception=True)
def add_event(request):

    form = EventForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)

        if not request.user.is_anonymous:
            event.reported_by = request.user

        event.save()

        return HttpResponseRedirect('/khistory')

    return render(request, 'add_event.html', {'form': form})


@login_required
@permission_required('khistory.add_event', raise_exception=True)
def add_personnage(request):

    form = PersonnageForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect('/khistory')

    return render(request, 'add_personnage.html', {'form': form})