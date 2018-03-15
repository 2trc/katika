from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets

from .models import IncidentType, Incident, IncidentSerializer, \
    IncidentTypeSerializer, IncidentForm, Tag

from django.db.models import Q

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


@login_required
def incident_add(request):
    form = IncidentForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():

        incident = form.save(commit=False)

        incident.save()

        # for Many2Many Relationship
        # https://docs.djangoproject.com/en/2.0/topics/forms/modelforms/
        # http://www.joshuakehn.com/2013/6/23/django-m2m-modelform.html
        form.save_m2m()

        incident = form.instance

        incident.reported_by = request.user

        incident.save()
        #incident.save_tags_string()

        # blog_page = form.save()
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


# Use Q for query filtering
def incident_aggregation(request):

    queryset = Incident.objects.all()

    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    type = request.GET.get('type')
    tags_string = request.GET.get('tags')

    queryset = filter_query_set(queryset, startdate_str=startdate, enddate_str=enddate,
                                type=type, tags_string=tags_string)

    return HttpResponse(JsonResponse(queryset.aggregate(Sum('wounded'),
                                                        Sum('deaths'),
                                                        Sum('missing'))))


def tags_facet(request):

    startdate_str = request.GET.get('startdate')
    enddate_str = request.GET.get('enddate')
    type = request.GET.get('type')
    tags_string = request.GET.get('tags_string')

    queryset = Tag.objects.all()

    q = Q()

    # from django.db.models import Subquery doesn't seem to work
    # https://stackoverflow.com/questions/45228187/possible-to-filter-the-queryset-after-querying-django
    if startdate_str is not None:
        startdate = datetime.strptime(startdate_str, "%Y-%m-%d")
        #queryset = queryset.filter(incident__date__gte=startdate)
        q = q & Q(incident__date__gte=startdate)

    if enddate_str is not None:
        enddate = datetime.strptime(enddate_str, "%Y-%m-%d")
        #queryset = queryset.filter(incident__date__lte=enddate)
        q = q & Q(incident__date__lte=enddate)

    if type is not None:
        #queryset = queryset.filter(incident__type__name=type)
        q = q & Q(incident__type__name=type)


    if tags_string is not None:
        #queryset = queryset.filter(incident__tags_string__contains=tags_string)
        q = q & Q(incident__tags_string__contains=tags_string)

    # TODO check if there isn't a better way than safe=False
    # Don't understand why the distinct is necessary
    return HttpResponse(JsonResponse(list(
        queryset.filter(q)
            .distinct()
            .annotate(count=Count('incident'))
            .order_by('-count')
            .values('name', 'name_fr', 'id', 'count')
            ),
        safe=False
    ))


def incident_geo_serialize(request):

    return HttpResponse(serialize('geojson', Incident.objects.all()))
                                  #geometry_field='point', fields='name,'))
                        #content_type='application/json')


def anycluster(request):

    return render(request, 'anybase.html', {})

class IncidentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = IncidentTypeSerializer
    queryset = IncidentType.objects.all()



def filter_query_set(queryset,startdate_str, enddate_str, type, tags_string ):

    # print("startdate: {}, endate: {}, type: {}".format(startdate_str, enddate_str, type))

    if startdate_str is not None:
        startdate = datetime.strptime(startdate_str, "%Y-%m-%d")
        queryset = queryset.filter(date__gte=startdate)

    if enddate_str is not None:
        enddate = datetime.strptime(enddate_str, "%Y-%m-%d")
        queryset = queryset.filter(date__lte=enddate)

    if type is not None:
        queryset = queryset.filter(type__name=type)

    if tags_string is not None:
        queryset = queryset.filter(tags_string__contains=tags_string)

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
        tags_string = self.request.query_params.get('tags_string', None)

        queryset = filter_query_set(queryset, startdate_str=startdate, enddate_str=enddate,
                                    type=type, tags_string=tags_string)

        orderby = self.request.query_params.get('orderby', None)
        order = self.request.query_params.get('order', None)

        #TODO descending ordering by deaths and wounded
        #not working. Why is missing working??
        if orderby is not None:

            #Null stuff https://stackoverflow.com/questions/5235209/django-order-by-position-ignoring-null

            queryset = queryset.annotate(null_stuff=Count(orderby))

            if order is not None and order == "ascending":
                queryset = queryset.order_by('-null_stuff', orderby)
            else:
                queryset = queryset.order_by('-null_stuff', '-{}'.format(orderby))

        return queryset




#TODO function for parsing query parameters