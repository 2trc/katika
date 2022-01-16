from django.core.management.base import BaseCommand, CommandError
from tender.models import TenderOwner

from armp.tender_collector import get_owner_list
import requests
from bs4 import BeautifulSoup

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def owner_list_to_dict(o_queryset):

    result = dict()

    for o in o_queryset:

        result[o.owner_id] = o.full_name

    return result


def find_delta(l1, l2):

    s1 = set(l1.keys())
    s2 = set(l2.keys())

    s_delta = s1 - s2

    result = {}

    if s_delta:

        for o_key in s_delta:
            result[o_key] = l1[o_key]

    return result


def persist_new_owners(o_dict):

    my_time = datetime.now().strftime("%Y-%m-%d-%H-%M")

    file_name = "tender/new_owners/{}.csv".format(my_time)

    with open(file_name, 'w', encoding='utf-8') as f:

        for k,v in o_dict.items():
            f.write("{}, {}\n".format(k,v))


def insert_new_owners(o_dict):

    for owner_id, full_name in o_dict.items():

        TenderOwner.objects.create(owner_id=owner_id, full_name=full_name)


class Command(BaseCommand):

    def handle(self, *args, **options):

        logger.info("Starting!")

        r = requests.get('https://armp.cm')

        s = BeautifulSoup(r.text, 'html.parser')

        l1 = get_owner_list(s)

        l2 = owner_list_to_dict(TenderOwner.objects.all())

        d = find_delta(l1, l2)

        if len(d):
            logger.info("{} new owner(s) found".format(len(d)))

            persist_new_owners(d)

            insert_new_owners(d)

        logger.info('Exiting!')
