from django.shortcuts import render
import json
from budget.models import AnnualEntry, BudgetProgramme, Chapitre
from django.db.models import Sum, Case, When, BigIntegerField, Q

COLORS = {"EN": "rgb(84,48,5)", "NO": "rgb(140,81,10)", "AD": "rgb(191,129,45)",
          "OU": "rgb(0,60,48)", "NW": "rgb(1,102,94)", "SW": "rgb(128,205,193)",
          "LT": "rgb(205,52,181)", "CE": "rgb(50,17,95)",
          "ES": "rgb(234,95,148)",
          "SU": "rgb(175,201,255)",
        #"SU": "rgb(96,62,50)",
          "AC": "rgb(158,132,132)", "BF": "rgb(233, 100, 60)"}


R_ORDER = {
    "BF": 0, "AC": 1, "CE": 2, "LT": 3, "SU": 4, "ES": 5,
    "OU": 6, "SW": 7, "NW": 8, "AD": 9, "NO": 10, "EN": 11
}


def region(request):
    c = request.GET.get('c')

    if c:
        c_num = int(c)

    #print(c_num)

    my_data = dict()

    my_data['BF'] = {'x': [], 'y': [], 'name': 'BF', 'type': 'bar',
                     'marker': {'color': COLORS['BF']}
                     }

    bf = AnnualEntry.objects.filter(status='LF').filter(bf_bip="BF")

    if c:
        bf = bf.filter(chapitre__number=c_num)

    bf = bf.values('year').annotate(cp=Sum('cp'))

    for entry in bf:
        my_data['BF']['x'].append(entry['year'])
        my_data['BF']['y'].append(entry['cp'])

    raw_data = AnnualEntry.objects. \
        filter(status='LF').filter(bf_bip='BIP')

    if c:
        raw_data = raw_data.filter(chapitre__number=c_num)

    raw_data = raw_data.values('year', 'region').annotate(cp=Sum('cp'))

    for entry in raw_data:

        region = entry['region']

        if region not in my_data:
            my_data[region] = {'x': [], 'y': [], 'name': region, 'type': 'bar',
                               'marker': { 'color': COLORS[region]}
                               }

        my_data[region]['x'].append(entry['year'])
        my_data[region]['y'].append(entry['cp'])

    list_values = list(my_data.values())
    sorted_list = sorted(list_values, key=lambda x: R_ORDER[x['name']])
    #sorted_list = sorted(list_values, key=lambda x: x['y'], reverse=True)
    #sorted_list = sorted(list_values, key=lambda x: x['y'])

    return render(request, 'general.html', context={'data': json.dumps(sorted_list)})



def department(request):

    raw_data = AnnualEntry.objects.values('chapitre__number', 'chapitre__short_name', 'chapitre__full_name_fr', 'year').\
        order_by('chapitre__number').\
        annotate(bf=Sum(
        Case(When(bf_bip="BF", then='cp'), output_field=BigIntegerField()))).\
        annotate(bip=Sum(
        Case(When(bf_bip="BIP", then='cp'), output_field=BigIntegerField())))

    return render(request, 'by-department.html', context={'data': raw_data})


def chapter_focus(request, c):

    queryset = BudgetProgramme.objects.filter(chapitre__number=c)

    data_qs = queryset.order_by('year').values('year').distinct().annotate(cp=Sum('cp'))

    queryset = queryset.order_by('-year', 'code')

    data = [{
        "x": [entry['year'] for entry in data_qs],
        "y": [round(entry['cp'] / 1000000000, 2) for entry in data_qs],
        "mode": "lines+markers",
        "line": {
            "width": 5
        },
        "marker": {
            "size": 10
        }
    }]

    #print(data)

    return render(request, 'budget-programme.html', context={
        'queryset': queryset,
        'data_js': json.dumps(data),
        'c': c
    })


def budget_global(request):

    queryset = BudgetProgramme.objects.all()

    queryset = queryset.order_by('year').values('year').distinct().annotate(cp=Sum('cp'), ae=Sum('ae'))

    data = []

    for ii in ["ae", "cp"]:

        data.append({
            "x": [entry['year'] for entry in queryset],
            "y": [round(entry[ii] / 1000000000, 2) for entry in queryset],
            "mode": "lines+markers",
            "line": {
                "width": 5
            },
            "marker": {
                "size": 10
            },
            "name": ii.upper()
        })

    return render(request, 'budget-global.html', context={
        'queryset': queryset,
        'data_js': json.dumps(data)
    })


def budget_programme(request):

    c = request.GET.get('c')

    if c:
        return chapter_focus(request, c)

    years = BudgetProgramme.objects.values('year').distinct().order_by('year')

    year = request.GET.get('y', years.last()['year'])

    queryset = BudgetProgramme.objects.filter(year=year).order_by('chapitre__number','code')

    data_qs = Chapitre.objects.filter(budgetprogramme__year=year).annotate(cp=Sum('budgetprogramme__cp'))

    data = [{
        "type": "treemap",
        "labels": [entry.short_name for entry in data_qs],
        "parents": ["" for _ in data_qs],
        "values": [round(entry.cp/1000000000,2) for entry in data_qs],
        "textinfo": "label+value+percent parent",
        "outsidetextfont": {"size": 20, "color": "#377eb8"},
        "marker": {"line": {"width": 0.1}},
        "pathbar": {"visible": False},
    }]

    return render(request, 'budget-programme.html', context={
        'queryset': queryset,
        'data_js': json.dumps(data),
        'years': years,
        'year': year
    })
