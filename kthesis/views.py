from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from django.http import HttpResponseRedirect
from .models import ThesisSerializer, Thesis, ScholarSerializer, Scholar,\
    University, UniversitySerializer, ScholarForm, ThesisForm
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Full-text search stuff
# http://blog.lotech.org/postgres-full-text-search-with-django.html
from django.db.models.functions import Concat
from django.db.models import TextField, Value as V
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchVector


#https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
def kthesis_home(request):

    thesis_set = Thesis.objects.all()
    page = request.GET.get('page', 1)

    print(request.GET)

    query_str = request.GET.get('q')

    if(query_str):
        thesis_set = perform_thesis_search(thesis_set, query_str)

    paginator = Paginator(thesis_set, 10)
    try:
        theses = paginator.page(page)
    except PageNotAnInteger:
        theses = paginator.page(1)
    except EmptyPage:
        theses = paginator.page(paginator.num_pages)

    return render(request, 'kthesis.html', context= build_context_from_thesis_set(theses))


def perform_thesis_search(thesis_set, query_str):
    vector = SearchVector('title', weight='A') + \
             SearchVector('title_fr', weight='A') + \
             SearchVector('abstract', weight='C') + \
             SearchVector('abstract_fr', weight='C') + \
             SearchVector('author__last_name', weight='C') + \
             SearchVector('author__first_name', weight='C') + \
             SearchVector(StringAgg('supervisors__last_name', delimiter=' '), weight='C') + \
             SearchVector(StringAgg('supervisors__first_name', delimiter=' '), weight='C') + \
             SearchVector(StringAgg('committee__last_name', delimiter=' '), weight='C') + \
             SearchVector(StringAgg('committee__first_name', delimiter=' '), weight='C') + \
             SearchVector(StringAgg('keywords__name', delimiter=' '), weight='B') + \
             SearchVector(StringAgg('keywords_fr__name', delimiter=' '), weight='B')

    return thesis_set.annotate(document=vector).filter(document=query_str)


def kthesis_author(request, slug):

    print("Author slug: {}".format(slug))

    author = get_object_or_404(Scholar, slug=slug)

    print("Author ID: {}".format(author.id))

    theses = Thesis.objects.filter(Q(committee__id__exact= author.id)|
                                   Q(supervisors__id__exact= author.id)|
                                   Q(author__id = author.id)).distinct()

    #theses = Thesis.objects.all().filter(author__slug=slug)

    return render(request, 'kthesis.html', context={'theses': theses,
                                                    'selected_author': author})

@login_required
def add_author(request):

    form = ScholarForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        scholar = form.save(commit=False)

        scholar.save()

        # for Many2Many Relationship
        # https://docs.djangoproject.com/en/2.0/topics/forms/modelforms/
        # http://www.joshuakehn.com/2013/6/23/django-m2m-modelform.html
        form.save_m2m()

        scholar = form.instance

        scholar.reported_by = request.user

        scholar.save()

        return HttpResponseRedirect('/kthesis')

    return render(request, 'add_scholar.html', {'form': form})


@login_required
def add_thesis(request):

    form = ThesisForm(data=request.POST or None, label_suffix='')

    if request.method == 'POST' and form.is_valid():
        thesis = form.save(commit=False)

        thesis.save()

        # for Many2Many Relationship
        # https://docs.djangoproject.com/en/2.0/topics/forms/modelforms/
        # http://www.joshuakehn.com/2013/6/23/django-m2m-modelform.html
        form.save_m2m()

        thesis = form.instance

        thesis.reported_by = request.user

        thesis.save()

        return HttpResponseRedirect('/kthesis')

    return render(request, 'add_thesis.html', {'form': form})


def kthesis_university(request, id):

    university = get_object_or_404(University, pk=id)

    theses = Thesis.objects.all().filter(university__pk=id)

    return render(request, 'kthesis.html', context={'theses': theses,
                                                    'selected_university': university})

def kthesis_year(request, id):

    theses = Thesis.objects.all().filter(year=id)

    return render(request, 'kthesis.html', context={'theses': theses,
                                                    'selected_year': id})

def build_context_from_thesis_set(thesis_set):
    ''' from thesis query set return context including
    1. thesis list
    2. facet for university
    3. facet for year
    '''
    ##TODO consider query filtering...

    university_facet = University.objects.annotate(num_thesis=Count('thesis')).order_by('-num_thesis')
    year_facet = Thesis.objects.all().values('year').annotate(total=Count('year'))

    print(year_facet)

    return {'theses': thesis_set, 'university_facet': university_facet,
            'year_facet': year_facet}



class ThesisViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = ThesisSerializer
    queryset = Thesis.objects.all()


class ScholarViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ScholarSerializer

    def get_queryset(self):

        if 'slug' in self.kwargs:
            return Scholar.objects.all().filter(slug=self.kwargs['slug'])
        else:
            return Scholar.objects.all()


class UniversityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UniversitySerializer
    queryset = University.objects.all()
