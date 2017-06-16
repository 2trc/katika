from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.serializers import serialize

from rest_framework import viewsets

from .models import IncidentType, Incident, IncidentSerializer, IncidentTypeSerializer, IncidentForm


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


def incident_geo_serialize(request):

    return HttpResponse(serialize('geojson', Incident.objects.all()))
                                  #geometry_field='point', fields='name,'))
                        #content_type='application/json')

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