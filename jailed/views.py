from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchVector
from .models import Incarceration, IncarcerationTag
from person.models import SEX

import csv

def jailed_home(request):
    # &q={{q}}&o={{curr.o}}&s={{curr.s}}
    # q={{q}}&o=name&s={{s.name}}, s.arrest, s.incarceration, s.conviction, s.release, s.prison
    curr = {'o': request.GET.get('o'), 's': request.GET.get('s')}
    s = {'last_name': None, 'arrest': None, 'incarceration': None, 'conviction': None, 'release': None, 'prison': None}

    order_list = []

    for k in s:

        print(k,curr)

        if k == curr['o']:

            order_str = "{}{}".format(get_sign(curr['s']), k)
            s[k] = 'dsc' if curr['s'] != 'dsc' else 'asc'

            if k not in ('last_name', 'prison'):
                order_str += "_date"

            order_list.append(order_str)

    if len(order_list) == 0:
        order_list = ['-arrest_date', '-incarceration_date', '-conviction_date', '-release_date']

    q_str = request.GET.get('q', '')

    if q_str:
        jailed_set = Incarceration.objects.annotate(
            search=SearchVector('last_name', 'first_name', 'alias'),
        ).filter(search=q_str)
    else:
        jailed_set = Incarceration.objects.all()

    selection = ''

    if request.GET.get('deceased') == 'true':
        jailed_set = jailed_set.filter(deceased=True)
        selection = 'deceased=true'

    # check the selection ...
    if request.GET.get('detained') == 'true':
        jailed_set = jailed_set.filter(conviction_date=None).filter(release_date__isnull=True)
        selection = 'detained=true'

    if request.GET.get('released') == 'true':
        jailed_set = jailed_set.exclude(release_date__isnull=True)
        selection = 'released=true'

    if request.GET.get('female') == 'true':
        jailed_set = jailed_set.filter(sex=1)
        selection = 'female=true'

    tag = request.GET.get('tag', '')
    if tag:
        jailed_set = jailed_set.filter(tags__name=tag)

    jailed_set = jailed_set.order_by(*order_list)

    page = request.GET.get('page', 1)

    paginator = Paginator(jailed_set, 50)

    tags = IncarcerationTag.objects.all()

    try:
        jailed = paginator.page(page)

    except PageNotAnInteger:
        jailed = paginator.page(1)
    except EmptyPage:
        jailed = paginator.page(paginator.num_pages)

    return render(request, 'jailed.html', context= {'jailed': jailed, 'paginator': paginator,
                                                    's': s, 'curr': curr, 'q': q_str,
                                                    'selection': selection, 'tags': tags, 's_tag':tag})


def get_sign(sign_name):
    return "" if sign_name == 'dsc' else "-"


def export_data(filename='incarceration.csv'):
    data = []
    for jailed in Incarceration.objects.all():
        data.append(jailed.to_dict())

    if len(data) == 0:
        print("Empty data, exiting")
        return

    print(f"{len(data)} records retrieved")
    print(f"first data: {data[0]}")

    with open(filename, mode='w') as csv_file:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        writer.writerows(data)
        print(f"{len(data)} rows written in {filename}")

    print("returning")