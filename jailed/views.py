from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchVector
from .models import Incarceration, IncarcerationTag, IncarcerationSerializer
from django.db.models import Count, Q, F
from django.http import FileResponse
import logging

from rest_framework import viewsets
from katika.models import ReadOnlyOrAdmin

import csv

logger = logging.getLogger(__name__)


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

    q = Q()

    if q_str:
        jailed_set = Incarceration.objects.annotate(
            search=SearchVector('last_name', 'first_name', 'alias', 'name_mispelling'),
        ).filter(search=q_str)

        q = (Q(incarceration__last_name__iexact=q_str) | Q(incarceration__first_name__iexact=q_str)
             | Q(incarceration__alias__iexact=q_str) | Q(incarceration__name_mispelling__iexact=q_str))
    else:
        jailed_set = Incarceration.objects.all()

    judge_id = request.GET.get('j')

    if judge_id:

        jailed_set = jailed_set.filter(judges__id=judge_id)
        q = q & Q(incarceration__judges__id=judge_id)

    selection = ''

    if request.GET.get('deceased') == 'true':
        jailed_set = jailed_set.filter(deceased=True)
        q = q & Q(incarceration__deceased=True)
        selection = 'deceased=true'

    # check the selection ...
    if request.GET.get('pretrial') == 'true':
        jailed_set = jailed_set.filter(conviction_date=None).filter(release_date__isnull=True)
        q = q & Q(incarceration__conviction_date=None) & Q(incarceration__release_date=None) &\
        Q(incarceration__conviction_duration_years=None) & Q(incarceration__conviction_duration_months=None) &\
        Q(incarceration__conviction_duration_days=None)

        selection = 'pretrial=true'

    if request.GET.get('released') == 'true':
        jailed_set = jailed_set.exclude(release_date__isnull=True)
        #TODO check for tag it's not working
        q = q & (~Q(incarceration__release_date=None))
        selection = 'released=true'

    if request.GET.get('detained') == 'true':
        jailed_set = jailed_set.filter(release_date__isnull=True)
        q = q & Q(incarceration__release_date=None)
        selection = 'detained=true'

    if request.GET.get('female') == 'true':
        jailed_set = jailed_set.filter(sex=1)
        q = q & Q(incarceration__sex=1)
        selection = 'female=true'

    #In case of downloading, terminate here
    if request.GET.get('download'):

        filename = '/tmp/incarceration.csv'

        export_data(filename, jailed_set=jailed_set)

        response = FileResponse(open(filename, 'rb'))

        response.setdefault('Content-Disposition', 'attachment; filename={}'.format(filename))

        return response

    tag = request.GET.get('tag', '')
    if tag:
        # TODO filtering cases with multiple tags doesn't seem to be working well
        jailed_set = jailed_set.filter(tags__name__in=[tag])
        q = q & Q(incarceration__tags__name__exact=tag)

    jailed_set = jailed_set.order_by(*order_list)

    # for s in jailed_set:
    #     print("name = {}, tags={}".format(s, s.tags.all()))

# TODO check Q with search vector
# TODO Django and Facet with tag

    page = request.GET.get('page', 1)

    paginator = Paginator(jailed_set, 50)

    # tags = jailed_set.exclude(tags__isnull=True)\
    #     .annotate(name=F('tags__name')).values('name')\
    #     .annotate(count=Count('pk')).order_by('-count')

    #tags = jailed_set.exclude(tags__isnull=True) \
    #    .annotate(name=F('tags__name'))
    tags = IncarcerationTag.objects.filter(q).annotate(count=Count('incarceration')).distinct()\
        .values('name', 'count')

    # for t in tags:
    #     print(t)
        #print(t.name)

    # tags = jailed_set.exclude(tags__isnull=True) \
    #     .annotate(name=F('tags__name')).values('name') \
    #     .annotate(count=Count('pk')).order_by('-count')
    #
    # for t in tags:
    #     print(t)

    #tags = IncarcerationTag.objects.annotate(count=Count('incarceration')).order_by('-count')

    #print(tags)
    # print("#\n#\n#\n")
    # print(tags2)

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


class IncarcerationViewSet(viewsets.ModelViewSet):

    serializer_class = IncarcerationSerializer

    #TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):

        return Incarceration.objects.all()


def export_data(filename='incarceration.csv', jailed_set=None):

    logger.info("Starting!")

    data = []

    if not jailed_set:
        jailed_set = Incarceration.objects.all()

    for jailed in jailed_set:
        data.append(jailed.to_dict())

    if len(data) == 0:
        logger.info("Empty data, exiting")
        return

    logger.info(f"{len(data)} records retrieved")
    logger.debug(f"first data: {data[0]}")

    with open(filename, mode='w') as csv_file:

        # TODO have better control of fields to be exported
        # dict contains fields not in fieldnames: 'prison'
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()

        writer.writerows(data)
        logger.info(f"{len(data)} rows written in {filename}")

    logger.info("Exiting!")
