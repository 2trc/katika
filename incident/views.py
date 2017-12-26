from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Sum
from django.http import JsonResponse

from rest_framework import viewsets

from .models import IncidentType, Incident, IncidentSerializer, IncidentTypeSerializer, IncidentForm

from datetime import datetime

from anycluster.MapClusterer import MapClusterer


def incident_home(request):

    incident_list = Incident.objects.all().order_by('-date')

    paginator = Paginator(incident_list, 10)

    page = 1

    if request.method == 'GET':
        page = request.GET.get('page', 1)

    incidents = paginator.page(page)

    # blogpages = self.get_children().live().order_by('-first_published_at')

    return render(request, 'incident.html', {'incidents': incidents})


def incident_add(request):
    form = IncidentForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        #blog_page = form.save(commit=False)
        blog_page = form.save()
        # blog_page.slug = slugify(blog_page.title)
        # blog = blog_index.add_child(instance=blog_page)

        # if blog:
        #     blog.unpublish()
        #     # Submit page for moderation. This requires first saving a revision.
        #     blog.save_revision(submitted_for_moderation=True)
        #     # Then send the notification to all Wagtail moderators.
        #     send_notification(blog.get_latest_revision().id, 'submitted', None)
        return HttpResponseRedirect('/incident')
    #IncidentProject.reverse_subpage()

    #return render(request, 'portal_pages/blog_page_add.html', context)
    return render(request, 'add_incident.html', {'form': form})


def incident_aggregation(request):

    queryset = Incident.objects.all()

    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    type = request.GET.get('type')

    queryset = filter_query_set(queryset, startdate_str=startdate, enddate_str=enddate, type=type)

    return HttpResponse(JsonResponse(queryset.aggregate(Sum('wounded'), Sum('deaths'))))


def incident_geo_serialize(request):

    return HttpResponse(serialize('geojson', Incident.objects.all()))
                                  #geometry_field='point', fields='name,'))
                        #content_type='application/json')

#def thanks(request):

#    return render(request, 'thanks.html')


def anycluster(request):
    #cluster = MapClusterer(request)
    #geostuff = cluster.kmeansCluster()
    #print(geostuff)

    #return HttpResponse(serialize('geojson',{}))
    return render(request, 'anybase.html', {})

class IncidentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = IncidentTypeSerializer
    queryset = IncidentType.objects.all()



def filter_query_set(queryset,startdate_str, enddate_str, type ):

    print("startdate: {}, endate: {}, type: {}".format(startdate_str, enddate_str, type))

    if startdate_str is not None:
        startdate = datetime.strptime(startdate_str, "%Y-%m-%d")
        queryset = queryset.filter(date__gte=startdate)

    if enddate_str is not None:
        enddate = datetime.strptime(enddate_str, "%Y-%m-%d")
        queryset = queryset.filter(date__lte=enddate)

    if type is not None:
        queryset = queryset.filter(type__name=type)

    return queryset


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = IncidentSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Incident.objects.all()  # .order_by('-date_joined')
        startdate = self.request.query_params.get('startdate', None)
        enddate = self.request.query_params.get('enddate', None)
        type = self.request.query_params.get('type', None)

        queryset = filter_query_set(queryset, startdate_str=startdate, enddate_str=enddate, type=type)

        orderby = self.request.query_params.get('orderby', None)
        order = self.request.query_params.get('order', None)

        #TODO order by 'wounded' not working
        if orderby is not None:

            if order is not None and order == "ascending":
                queryset = queryset.order_by(orderby)
            else:
                queryset = queryset.order_by("-{}".format(orderby))

        return queryset




#TODO function for parsing query parameters