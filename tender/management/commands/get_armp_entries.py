from django.core.management.base import BaseCommand, CommandError
from tender.models import ArmpEntry, TenderOwner
import requests
from bs4 import BeautifulSoup
import time, logging, os
from armp.tender_collector import get_next_url
from armp.tender_parser import get_tous_les_avis, parse_one_avis
from pytz import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# TODO: testing
def fetch_page(url: str, max_retries=5, sleep_retry=60):

    retry_count = 0

    while retry_count < max_retries :

        try:
            r = requests.get(url)
            if r.status_code == 200:
                return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            logger.exception(e)
            retry_count += 1

        time.sleep(sleep_retry)

    return None


def parse_page(soup):

    next_url = get_next_url(soup)

    tender_list = []

    for avis in get_tous_les_avis(soup):
        parsed_avis = parse_one_avis(avis)
        tender_list.append(parsed_avis)

    return next_url, tender_list


def avis_to_armp_entry(avis):

    entry = ArmpEntry()

    try:
        entry.owner = TenderOwner.objects.get(short_name__exact=avis.get('owner_short'))

    except Exception as e:
        logger.error("Owner list needs to be updated with short name: %s", avis.get('owner_short'))
        logger.exception(e)

    entry.link = avis.get('details')

    if avis.get('cost'):
        entry.projected_cost = avis.get('cost')

    entry.expiration_date = avis.get('end_date')
    entry.expiration_time = avis.get('end_time')
    entry.region = avis.get('region')
    entry.verbose_type = avis.get('type')
    entry.publication_type = avis.get('publication_type')
    entry.dao_link = avis.get('dao')
    entry.tf = avis.get('tf')
    entry.title = avis.get('title')

    gzt = timezone('Africa/Douala')

    pub_date_time = avis.get("publish_date_time")
    if pub_date_time:
        entry.publication_datetime = gzt.localize(datetime.strptime(pub_date_time, "%d-%m-%Y %H:%M:%S"))

    end_date = avis.get('end_date')
    end_time = avis.get('end_time', '00:00:00')
    if end_date:
        a = gzt.localize(datetime.strptime(end_date + " " + end_time, "%d-%m-%Y %H:%M:%S"))
        entry.expiration_date = a.date()
        entry.expiration_time = a.time()

    return entry


def parse_arg(options):

    page = options['page']
    count = options['count']

    if count:
        return page, count, None, None

    if options['end_date']:
        end_date = datetime.strptime(options['end_date'], '%d-%m-%Y').date()
    else:
        end_date = datetime.today().date()

    if options['start_date']:
        start_date = datetime.strptime(options['start_date'], '%d-%m-%Y').date()
    else:
        start_date = datetime.today().date() - timedelta(days=1)

    return None, None, start_date, end_date


def parse_and_persist(entries):

    save_count = 0

    for entry in entries:

        tender = avis_to_armp_entry(entry)

        try:
            tender.save()

            save_count += 1
        except Exception as e:
            logger.warning('Problem while logging, probably a duplicate. Entry: %s', entry)
            logger.exception(e)

        # if tender.publication_datetime.date() >= start_date:
        #     # if we find at least one entry that is early than end date
        #     # we continue paging through
        #     stop_flag = False

    logger.info("%d entries saved", save_count)


def crawl_with_pages(page_start, page_count):

    logger.info("Running with start page [%s], page count [%s]",
                 page_start, page_count)

    page_url = "https://armp.cm/lang?val=fr"

    if page_start:
        page_url += "&page={}".format(page_start)

    try:
        page_count_i = int(page_count)
    except ValueError as e:
        logging.error('')

        return

    ii = 0

    while page_url and ii < page_count_i:

        logger.info('fetching: %s', page_url)

        page_content = fetch_page(page_url)
        page_url, entries = parse_page(page_content)
        ii += 1

        parse_and_persist(entries)


def crawl_with_dates(start_date, end_date):

    logger.info("Running with start date [%s], end date [%s]",
                 start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    # stop_flag = False

    # page_url = "https://armp.cm/"
    # page_url = "https://armp.cm/lang?val=fr"
    url_segment = "date_debut={}&date_fin={}".format(
        start_date.strftime("%d/%m/%Y"),
        end_date.strftime("%d/%m/%Y"),
    ).replace("/", "%2F")
    page_url = "https://armp.cm/recherche_avancee?{}".format(url_segment)

    # should we keep stop_flag ?

    while page_url:

        # stop_flag = True

        logger.info('fetching: %s', page_url)

        page_content = fetch_page(page_url)
        page_url, entries = parse_page(page_content)

        parse_and_persist(entries)


# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):
    # Todo add possibility to grab only certain page - range

    def add_arguments(self, parser):

        parser.add_argument(
            '-s', '--start-date',
            help='Date from where to start (oldest) e.g. 12-05-2020',
            type=str
        )

        parser.add_argument(
            '-e', '--end-date',
            help='Date where to stop (latest) e.g. 12-06-2021',
            type=str
        )

        parser.add_argument(
            '-p', '--page',
            help='Start page',
            type=str
        )

        parser.add_argument(
            '-c', '--count',
            help='Number of pages to collect',
            type=str
        )

    def handle(self, *args, **options):

        logger.info("Starting!")
        page_start, page_count, start_date, end_date = parse_arg(options)

        if page_count:
            crawl_with_pages(page_start, page_count)
        else:
            crawl_with_dates(start_date, end_date)

        logger.info("Exiting!")






