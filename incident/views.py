from django.shortcuts import render
#from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from rest_framework import viewsets

from .models import IncidentType, Incident, IncidentSerializer, IncidentTypeSerializer


def incident_home(request):

    incident_list = Incident.objects.all().order_by('-date')

    paginator = Paginator(incident_list, 10)

    page = 1

    if request.method == 'GET':
        page = request.GET.get('page', 1)

    incidents = paginator.page(page)

    # blogpages = self.get_children().live().order_by('-first_published_at')

    return render(request, 'incident.html', {'incidents': incidents})


#def thanks(request):

#    return render(request, 'thanks.html')


class IncidentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = IncidentType.objects.all()#.order_by('-date_joined')
    serializer_class = IncidentTypeSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer