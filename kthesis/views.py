from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import ThesisSerializer, Thesis, ScholarSerializer, Scholar,\
    University, UniversitySerializer
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


#https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
def kthesis_home(request):

    thesis_set = Thesis.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(thesis_set, 10)
    try:
        theses = paginator.page(page)
    except PageNotAnInteger:
        theses = paginator.page(1)
    except EmptyPage:
        theses = paginator.page(paginator.num_pages)

    return render(request, 'kthesis.html', context={'theses': theses})


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

def kthesis_university(request, id):

    university = get_object_or_404(University, pk=id)

    theses = Thesis.objects.all().filter(university__pk=id)

    return render(request, 'kthesis.html', context={'theses': theses,
                                                    'selected_university': university})

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
