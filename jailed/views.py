from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Incarceration

# Create your views here.
def jailed_home(request):

    jailed_set = Incarceration.objects.all().order_by(
        '-arrest_date', '-incarceration_date', '-conviction_date', '-release_date')

    page = request.GET.get('page', 1)

    print(request.GET)

    #query_str = request.GET.get('q')

    #if(query_str):
    #    jailed_set = perform_thesis_search(jailed_set, query_str)

    paginator = Paginator(jailed_set, 50)

    try:
        jailed = paginator.page(page)

    except PageNotAnInteger:
        jailed = paginator.page(1)
    except EmptyPage:
        jailed = paginator.page(paginator.num_pages)

    return render(request, 'jailed.html', context= {'jailed': jailed})