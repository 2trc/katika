from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
# Create your views here.
from .models import ArmpEntry, TenderOwner, TenderOwnerSerializer
from django.views.generic.list import ListView
from django.db.models import F, Count
from django.db.models.functions import ExtractYear
from django.contrib.postgres.search import SearchVector, SearchQuery
from rest_framework import viewsets
from katika.models import ReadOnlyOrAdmin

import logging

logger = logging.getLogger(__name__)


class TenderOwnerViewset(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = TenderOwnerSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):

        query_set = TenderOwner.objects.all()

        s_term = self.request.GET.get('q', '')

        if s_term:

            return query_set.annotate(
                search=SearchVector('short_name', 'full_name'),
            ).filter(search=s_term)

        return query_set


class TenderListView(ListView):

    model = ArmpEntry
    paginate_by = 100

    def get_queryset(self):

        query_str = self.request.GET.get('q', '')
        query_o_str = self.request.GET.get('q_o', '')
        owner_str = self.request.GET.get('o', '')
        sort_str = self.request.GET.get('sort', '')
        tender_type = self.request.GET.get('type', '')
        region_str = self.request.GET.get('r', '')
        year_str = self.request.GET.get('y', '')

        object_list = self.model.objects.all()

        object_list = search_queryset(object_list, query_str)
        object_list = search_owner_queryset(object_list, query_o_str)
        object_list = restrict_owner(object_list, owner_str)
        object_list = restrict_type(object_list, tender_type)
        object_list = restrict_region(object_list, region_str)
        object_list = restrict_year(object_list, year_str)

        object_list = sort_queryset(object_list, sort_str)

        return object_list

    def get_context_data(self, **kwargs):
        # https://www.reddit.com/r/djangolearning/comments/9xdsnh/using_get_queryset_and_get_context_data_together/
        data = super().get_context_data(**kwargs)
        query_set = self.object_list

        data['owners'] = query_set.values(owner_id=F('owner__owner_id'), short_name=F('owner__short_name'))\
            .annotate(total=Count('owner')).order_by('-total')
        data['regions'] = query_set.values('region').annotate(total=Count('region')).order_by('-total')
        data['years'] = query_set.annotate(year=ExtractYear('publication_datetime')).values('year')\
            .annotate(total=Count('year')).order_by('-year')

        query_str = self.request.GET.get('q', '')
        if query_str:
            data['q'] = query_str

        if self.request.GET.get('steroid', False):
            data['o_length'] = ":30"
        else:
            data['o_length'] = ":10"

        return data


def search_queryset(query_set, query_str):

    if query_str:
        query_set = query_set.filter(search_vector=SearchQuery(query_str, config='french_unaccent'))

    return query_set


def search_owner_queryset(query_set, query_o_str):

    if query_o_str:
        query_set = query_set.filter(owner__full_name__icontains=query_o_str)

    return query_set


def restrict_owner(query_set, filter_str):

    if filter_str:

        query_set = query_set.filter(owner__owner_id=filter_str)

    return query_set


def restrict_type(query_set, type_str):

    accepted_list = ["ADDITIF", "AMI", "AO", "COMM", "DC", "DEC-ANN", "DEC-ATTR", "DEC-INF", "DEC-RES", "DP"]

    if type_str and type_str in accepted_list:

        query_set = query_set.filter(publication_type=type_str)

    return query_set


def restrict_region(query_set, region_str):

    if region_str:

        query_set = query_set.filter(region=region_str)

    return query_set


def restrict_year(query_set, year_str):

    if year_str:

        query_set = query_set.filter(publication_datetime__year=year_str)

    return query_set


def sort_queryset(query_set, sort_str):

    if sort_str:

        if 'cost' in sort_str:
            my_sorting = F('cost')
        else:
            my_sorting = F('publication_datetime')

        if '-' in sort_str:
            my_sorting = my_sorting.asc(nulls_last=True)
        else:
            my_sorting = my_sorting.desc(nulls_last=True)

        object_list = query_set.order_by(my_sorting)

    else:
        object_list = query_set.order_by(F('publication_datetime').desc(nulls_last=True))

    return object_list

