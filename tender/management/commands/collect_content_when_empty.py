from django.core.management.base import BaseCommand, CommandError
from tender.models import ArmpEntry
import requests
from bs4 import BeautifulSoup
import time
from django.db.models import Q
from retry.api import retry_call

import logging

logger = logging.getLogger(__name__)
# TODO: testing


# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):

    def handle(self, *args, **options):

        logger.info("Starting!")

        list_of_interest = ArmpEntry.objects.filter(
            Q(content__isnull=True)
            | Q(content__exact='')
        )

        ii = 0
        total = list_of_interest.count()

        logger.info("%s entries found", total)

        s = requests.Session()

        for entry in list_of_interest:

            logger.info("Processing %s", entry.link)
            r = s.get(entry.link)
            soup = BeautifulSoup(r.text, 'html.parser')

            entry.content = soup.text
            try:
                entry.original_link = soup.find(class_="float-left").a.get("href")
            except Exception as e:
                logger.exception(e)

            # django.db.utils.InterfaceError: connection already closed
            retry_call(entry.save, fargs=None, fkwargs=None, tries=3, delay=60)
            
            ii += 1

            logger.info("%.3f done!", 100.0*ii/total)

            time.sleep(5)

        s.close()

        logger.info("Exiting!")
