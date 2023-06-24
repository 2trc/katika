from django.core.management.base import BaseCommand, CommandError
import logging
import os
#from os import path
import json
from budget.models import BudgetProgramme, Chapitre
from django.db.models import Sum
from collections import defaultdict
from time import time
import csv

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):

        logger.info("Starting!")

        q = BudgetProgramme.objects.order_by('year').values('year', 'chapitre__short_name').distinct().annotate(cp=Sum('cp'))
        l = list(q)
        a =defaultdict(lambda: dict())
        for ii in l:
            y = a[ii['chapitre__short_name']]
            y[ii['year']]=ii['cp']

        for ii in a:
            a[ii]['chapitre']=ii

        ts = int(time())

        a = list(a.values())
        with open(f'budget/budget-chapitre-{ts}.csv', 'w') as csv_file:
            fieldnames = list(a[0].keys())
            fieldnames = [fieldnames[-1]]+fieldnames[:-1]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()

            writer.writerows(a)


        logger.info("Exiting!")
