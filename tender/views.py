from typing import List
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import get_object_or_404
# Create your views here.
from .models import ArmpEntry, TenderOwner, ArmpContract, Entreprise, WBContract, WBProject,\
    TenderSerializer, TenderOwnerSerializer, EntrepriseSerializer
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import F, Count, Sum, Q
from django.db.models.functions import ExtractYear
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.core.paginator import Paginator
from rest_framework import viewsets, serializers
from katika.models import ReadOnlyOrAdmin

import logging

logger = logging.getLogger(__name__)


# class TenderOwnerViewset(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     serializer_class = TenderOwnerSerializer
#     permission_classes = [ReadOnlyOrAdmin]
#
#     def get_queryset(self):
#
#         query_set = TenderOwner.objects.all()
#
#         s_term = self.request.GET.get('q', '')
#
#         if s_term:
#
#             return query_set.annotate(
#                 search=SearchVector('short_name', 'full_name', config='french_unaccent'),
#             ).filter(search=SearchQuery(s_term, config='french_unaccent'))
#
#         return query_set


class TenderOwnerListView(ListView):

    model = TenderOwner
    paginate_by = 50

    def get_queryset(self):

        object_list = super().get_queryset().annotate(total=Count('armpentry'))

        return query_tender_owners(self.request, object_list)

    def get_context_data(self, **kwargs):
        # https://www.reddit.com/r/djangolearning/comments/9xdsnh/using_get_queryset_and_get_context_data_together/
        data = super().get_context_data(**kwargs)

        query_str = self.request.GET.get('q', '')
        if query_str:
            data['q'] = query_str

        return data


def query_tender_owners(request, object_list):

    query_str = request.GET.get('q', '')

    sort_str = request.GET.get('sort', '')

    if query_str:

        object_list = object_list.annotate(
            search=SearchVector('short_name', 'full_name', config='french_unaccent'),
        ).filter(search=SearchQuery(query_str, config='french_unaccent'))

    if not sort_str:
        sort_str = '-a'

    if 'count' in sort_str:
        my_sorting = F('total')
    else:
        my_sorting = F('short_name')

    if '-' in sort_str:
        my_sorting = my_sorting.asc(nulls_last=True)
    else:
        my_sorting = my_sorting.desc(nulls_last=True)

    object_list = object_list.order_by(my_sorting)

    return object_list


class TenderOwnerViewSet(viewsets.ModelViewSet):

    serializer_class = TenderOwnerSerializer
    # TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        return query_tender_owners(self.request, TenderOwner.objects.all())


class TenderListView(ListView):

    model = ArmpEntry
    paginate_by = 100

    def get_queryset(self):

        return query_armp_entry(self.request, self.model.objects.all())

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


def query_armp_entry(request, object_list):

    query_str = request.GET.get('q', '')
    query_o_str = request.GET.get('q_o', '')
    owner_str = request.GET.get('o', request.GET.get('owner_id', ''))
    sort_str = request.GET.get('sort', '')
    tender_type = request.GET.get('type', request.GET.get('publication_type', ''))
    region_str = request.GET.get('r', request.GET.get('region', ''))
    year_str = request.GET.get('y', request.GET.get('year', ''))

    object_list = search_queryset(object_list, query_str)
    object_list = search_owner_queryset(object_list, query_o_str)
    object_list = restrict_owner(object_list, owner_str)
    object_list = restrict_type(object_list, tender_type)
    object_list = restrict_region(object_list, region_str)
    object_list = restrict_year(object_list, year_str)

    object_list = sort_queryset(object_list, sort_str)

    return object_list


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


class TenderViewSet(viewsets.ModelViewSet):

    serializer_class = TenderSerializer
    # TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        return query_armp_entry(self.request, ArmpEntry.objects.all())

    #queryset = ArmpEntry.objects.all()


class ContractListView(ListView):

    model = ArmpContract
    paginate_by = 100

    def get_queryset(self):

        query_str = self.request.GET.get('q', '')
        query_o_str = self.request.GET.get('q_o', '')
        owner_str = self.request.GET.get('o', '')
        sort_str = self.request.GET.get('sort', '')
        tender_type = self.request.GET.get('type', '')
        titulaire_str = self.request.GET.get('t', '')
        year_str = self.request.GET.get('y', '')
        niu_str = self.request.GET.get('n', '')

        object_list = self.model.objects.all()

        # if query_str:
        #     object_list= object_list.annotate(
        #         search=SearchVector('title', config='french_unaccent'),
        #     ).filter(search=query_str)

        if query_str:
            object_list = object_list.filter(search_vector=SearchQuery(query_str, config='french_unaccent'))

        if year_str:
            object_list = object_list.filter(year=year_str)

        if owner_str:
            object_list = object_list.filter(maitre_ouvrage=owner_str)

        if titulaire_str:
            object_list = object_list.filter(titulaire=titulaire_str)

        if tender_type:
            if tender_type == '0':
                object_list = object_list.filter(status__in=[3,4,6])
            elif tender_type in ['1','2','5']:
                object_list = object_list.filter(status=tender_type)
        
        # if niu_str:
        #     object_list = object_list.filter(is_niu_available=False)

        #print("search done!")

        sort_tuple = []
        # TODO use regex match
        if 'cost' in sort_str:

            if '-cost' == sort_str:
                my_sorting = F('cost').asc(nulls_last=True)
            elif 'cost' == sort_str:
                my_sorting = F('cost').desc(nulls_last=True)

            sort_tuple.append(my_sorting)

        elif 'date' in sort_str:

            if '-' in sort_str:
                sort_tuple +=['-year', '-date']
            else:
                sort_tuple +=['year', 'date']
        else:
            sort_tuple +=['-year', '-date']

        sort_tuple.append('-status')

        return object_list.order_by(*sort_tuple)

    def get_context_data(self, **kwargs):
        # https://www.reddit.com/r/djangolearning/comments/9xdsnh/using_get_queryset_and_get_context_data_together/
        data = super().get_context_data(**kwargs)
        query_set = self.object_list

        data['owners'] = query_set.values('maitre_ouvrage')\
             .annotate(total=Count('maitre_ouvrage')).order_by('-total')
        data['titulaires'] = query_set.values('titulaire').annotate(total=Count('titulaire')).order_by('-total')
        data['years'] = query_set.values('year')\
             .annotate(total=Count('year')).order_by('-year')

        query_str = self.request.GET.get('q', '')
        if query_str:
            data['q'] = query_str

        if self.request.GET.get('steroid', False):
            data['o_length'] = ":30"
        else:
            data['o_length'] = ":10"

        return data


def titulaire_stats(request):

    query_str = request.GET.get('q', '')
    #query_o_str = self.request.GET.get('q_o', '')
    #owner_str = self.request.GET.get('o', '')
    sort_str = request.GET.get('sort', '')
    #tender_type = self.request.GET.get('type', '')
    #titulaire_str = self.request.GET.get('t', '')
    year_str = request.GET.get('y', '')

    query_set = ArmpContract.objects.exclude(titulaire__isnull=True).exclude(titulaire__exact='')

    if query_str:
        query_set= query_set.annotate(
            search=SearchVector('titulaire', config='french_unaccent'),
        ).filter(search=query_str)

    if year_str:
        query_set = query_set.filter(year=year_str)

    years = query_set.values('year') \
        .annotate(total=Count('year')).order_by('-year')

    query_set = query_set.values('titulaire').annotate(count=Count('titulaire'))\
        .annotate(cost=Sum('cost'))

    if sort_str:

        if 'count' in sort_str:
            my_sorting = F('count')
        else:
            my_sorting = F('cost')

        if '-' in sort_str:
            my_sorting = my_sorting.desc(nulls_last=True)
        else:
            my_sorting = my_sorting.asc(nulls_last=True)

        object_list = query_set.order_by(my_sorting)

    else:
        object_list = query_set.order_by(F('count').desc(nulls_last=True))

    paginator = Paginator(object_list, 50)

    page = int(request.GET.get('page', '1'))

    page_obj = paginator.page(page)

    object_list = page_obj.object_list


    return render(request, 'titulaire_stats.html', context={
        'object_list': object_list,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages>1,
        'paginator': paginator,
        'years': years,
        #'data_js': json.dumps(data)
    })


class EntrepriseListView(ListView):

    model = Entreprise
    paginate_by = 10
    template_name = "tender/entreprise_list.html"

    def get_params(self):

        query_str = self.request.GET.get('q', '')
        telephone = self.request.GET.get('t', self.request.GET.get('telephone', ''))
        bp = self.request.GET.get('bp', '')
        niu = self.request.GET.get('n', self.request.GET.get('niu', ''))

        return query_str, telephone, bp, niu

    def is_landing_page(self):

        return len(self.request.GET)==0


    def get_queryset(self):

        if self.is_landing_page():
            return []

        query_str, telephone, bp, niu = self.get_params()

        object_list = self.model.objects.prefetch_related('cdi_cri')

        if query_str:
            object_list = object_list.filter(change_list__search_vector=SearchQuery(query_str, config='french_unaccent'))

        if telephone:
            object_list = object_list.filter(telephone__contains=telephone)

        if bp:
            object_list = object_list.filter(bp=bp)

        if niu:
            object_list = object_list.filter(niu__contains=niu)

        return object_list.order_by('niu').distinct()  # .order_by(*sort_tuple)


    def get_context_data(self, **kwargs):
        # https://www.reddit.com/r/djangolearning/comments/9xdsnh/using_get_queryset_and_get_context_data_together/
        data = super().get_context_data(**kwargs)

        data['q'] = self.request.GET.get('q', '')

        data['is_landing'] = self.is_landing_page()

        return data

class Entreprise2ListView(EntrepriseListView):

    model = Entreprise
    paginate_by = 10
    template_name = "tender/entreprise_list.html"

    def get_queryset(self):

        if self.is_landing_page():
            return []

        query_str, telephone, bp, niu = self.get_params()

        search_query = Q(change_list__search_vector=SearchQuery(query_str, config='french_unaccent'))

        t2 = query_str.replace(" ", "")

        if t2.isnumeric():
            if len(t2) == 8:
                search_query |= Q(change_list__search_vector=SearchQuery("6"+t2, config='french_unaccent')) | Q(telephone__contains=t2)
            elif len(t2) == 9:
                t2 = t2[1:]
                search_query |= Q(change_list__search_vector=SearchQuery(t2, config='french_unaccent')) | Q(telephone__contains=t2)

        object_list = self.model.objects.prefetch_related('cdi_cri')

        object_list = object_list.filter(search_query)

        return object_list.order_by('niu').distinct()

    def get_template_names(self) -> List[str]:

        if self.is_landing_page():
            return "tender/entreprise2_list.html"

        return "tender/entreprise_list.html"


def get_enterprise(request, niu):

    e = get_object_or_404(Entreprise, niu=niu)

    return render(request, 'get_entreprise.html', context={
        'object': e,
    })


class ContribuableSet(viewsets.ModelViewSet):

    serializer_class = EntrepriseSerializer
    # TODO align access-right with django-admin?
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        return query_entreprise(self.request, Entreprise.objects.all())


class WBContractListView(ListView):

    model = WBContract
    paginate_by = 50

    def get_queryset(self):

        query_str = self.request.GET.get('q', '')
        project_id = self.request.GET.get('p')
        sort_str = self.request.GET.get('sort', '')
        year_str = self.request.GET.get('y', '')
        titulaire_str = self.request.GET.get('t', '')

        object_list = self.model.objects.prefetch_related('project')

        if project_id:
            object_list = object_list.filter(project__project_id=project_id)

        if query_str:
            object_list = object_list.filter(
                Q(search_vector=SearchQuery(query_str, config='french_unaccent'))|
                Q(suppliers__name__icontains=query_str))

        if year_str:
            object_list = object_list.filter(date__year=year_str)

        if titulaire_str:
            object_list = object_list.filter(suppliers__name=titulaire_str)


        sort_tuple = []
        # TODO use regex match
        if 'cost' in sort_str:

            if '-cost' == sort_str:
                my_sorting = F('cost').asc(nulls_last=True)
            elif 'cost' == sort_str:
                my_sorting = F('cost').desc(nulls_last=True)

            sort_tuple.append(my_sorting)

        elif 'date' in sort_str:

            if '-' in sort_str:
                sort_tuple +=['-date']
            else:
                sort_tuple +=['date']
        else:
            sort_tuple = ['-date']

        #sort_tuple.append('-status')

        #print("sorting done and about to return!")

        return object_list.order_by(*sort_tuple)


    def get_context_data(self, **kwargs):
        # https://www.reddit.com/r/djangolearning/comments/9xdsnh/using_get_queryset_and_get_context_data_together/
        data = super().get_context_data(**kwargs)

        query_set = self.object_list

        data['projects'] = query_set.values(project_id=F('project__project_id'))\
             .annotate(total=Count('project_id')).order_by('-total')
        data['years'] = query_set.annotate(year=ExtractYear('date')).values('year')\
            .annotate(total=Count('year')).order_by('-year')
        data['titulaires'] = query_set.values('suppliers__name').annotate(total=Count('suppliers__name')).order_by('-total')
        data['statuses'] = query_set.values(status=F('project__status')).annotate(total=Count('status')).order_by('-total')
        data['total_cost'] = query_set.aggregate(value=Sum('cost'))

        for item in data['statuses']:
            item['name'] = WBProject.STATUS[item['status']][1]
        # data['years'] = query_set.values('year')\
        #      .annotate(total=Count('year')).order_by('-year')

        query_str = self.request.GET.get('q', '')
        if query_str:
            data['q'] = query_str

        if self.request.GET.get('steroid', False):
            data['o_length'] = ":30"
        else:
            data['o_length'] = ":10"

        return data



