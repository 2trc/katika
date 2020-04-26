from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import CovidProducer, CovidInitiative, CovidProducerForm, CovidInitiativeForm, \
    CovidFund, CovidFundForm
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse


def covid_home(request):

    return render(request, 'covid19.html')


class ProducerList(ListView):

    context_object_name = 'producers'
    model = CovidProducer
    template_name = "producers.html"
    paginate_by = 50


class ProducerUpdate(UpdateView):

    model = CovidProducer
    form_class = CovidProducerForm
    template_name = 'update_producer.html'

    def get_success_url(self):

        return reverse('producer-list')


class ProducerCreate(CreateView):

    model = CovidProducer
    form_class = CovidProducerForm
    template_name = 'update_producer.html'

    def get_success_url(self):

        return reverse('producer-list')


class InitiativeList(ListView):

    context_object_name = 'initiatives'
    model = CovidInitiative
    template_name = 'initiatives.html'
    paginate_by = 50


class InitiativeUpdate(UpdateView):

    model = CovidInitiative
    form_class = CovidInitiativeForm
    template_name = 'update_initiative.html'

    def get_success_url(self):

        return reverse('initiative-list')


class InitiativeCreate(CreateView):

    model = CovidInitiative
    form_class = CovidInitiativeForm
    template_name = 'update_initiative.html'

    def get_success_url(self):

        return reverse('initiative-list')


class FundList(ListView):

    context_object_name = 'funds'
    model = CovidFund
    template_name = 'funds.html'
    paginate_by = 50


class FundUpdate(UpdateView):

    model = CovidFund
    form_class = CovidFundForm
    template_name = 'update_fund.html'

    def get_success_url(self):

        return reverse('fund-list')


class FundCreate(CreateView):

    model = CovidFund
    form_class = CovidFundForm
    template_name = 'update_fund.html'

    def get_success_url(self):

        return reverse('fund-list')
