from django.core.management.base import BaseCommand, CommandError
import logging, os
from tender.models import ArmpContract, WBContract,Entreprise
from django.db.utils import IntegrityError
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
import re
from datetime import datetime
from dateutil import relativedelta
from retry.api import retry_call


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def clean_enterprise_name(name_in):

    name_out = name_in.strip()

    name_out = re.sub("^ets ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub("^etablissement ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub("^ste ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub("^societe ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub("^gr?pt ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub("^groupement ", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?sarl$", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?ltd$", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?limited$", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?co\.?$", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?co\.? ?ltd\.?$", "", name_out, flags=re.IGNORECASE)
    name_out = re.sub(" ?s\.?a\.?$", "", name_out, flags=re.IGNORECASE)

    return name_out

owner_cache = dict()

def was_enterprise_active(c_date, excercise_list):

    '''
    It is assumes exercise_list is ordered from latest to earliest
    return
    is_active   -> where the date is included in the exercice_list
    '''

    month = c_date.month
    year = c_date.year

    for excerice in excercise_list:

        if month == excerice.month and year == excerice.year:
            return True
        
        # small optimization
        if year > excerice.year:
            break
        elif year == excerice.year and month > excerice.month:
            break
    
    return False


def get_registration_delta(c_date, earliest):
    '''
    return
    from_registration  -> number of months from the first element in the exercise_list to date
    '''
    earliest_date = datetime.strptime(f"01/{earliest.month}/{earliest.year}", "%d/%m/%Y")

    delta = relativedelta.relativedelta(c_date, earliest_date)

    return delta.years*12 + delta.months


def process_single_contribuable(c_name, c_date):

    '''
    returns
        niu_count ->            number of NIU found
        is_active ->            in case niu_count=1, whether NIU was active at the time otherwise null
        from_registration ->    in case niu_count=1, number of months from first registration
    '''
    cleaned_item = clean_enterprise_name(c_name)
    if c_name in owner_cache:
        niu_count, excercise_list = owner_cache[c_name]
    else:        
        query_set = Entreprise.objects.filter(change_list__search_vector=SearchQuery(cleaned_item, config="french_unaccent")).distinct()
        niu_count = query_set.count()
        if niu_count == 1:
            excercise_list = list(query_set.first().exercice_list.all())
        else:
            excercise_list = None
            owner_cache[c_name] = niu_count, excercise_list

    if niu_count == 1 and c_date:

        is_active = was_enterprise_active(c_date, excercise_list)
        from_registration = get_registration_delta(c_date, excercise_list[-1])

        return niu_count, is_active, from_registration

    else:
        return niu_count, None, None


def min_registration(reg1, reg2):

    if reg1 and reg2:
        return min(reg1, reg2)
    elif reg1:
        return reg1
    else:
        return reg2

class Command(BaseCommand):
    # Todo add possibility to grab only certain page - range

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--count',
            help='How many to handle',
            type=int
        )

        parser.add_argument(
            '-w', '--world_bank',
            help="For World Bank Contracts",
            action='store_true'
        )

    def handle(self, *args, **options):

        logger.info("Starting!")

        if options['world_bank']:
            contract_list = WBContract.objects.filter(is_contribuables_scanned=False)
        else:
            contract_list = ArmpContract.objects.filter(is_contribuables_scanned=False)

        b = options['count']

        ii = 1

        for contract in contract_list:

            r_niu_count = 0
            r_is_active = True
            r_from_registration = None



            for item in contract.get_supplier_names():

                #niu_count, is_active, from_registration = process_single_contribuable(item)

                cleaned_item = clean_enterprise_name(item)
                niu_count, is_active, from_registration = process_single_contribuable(cleaned_item, contract.date)
                r_niu_count = max(r_niu_count, niu_count)
                r_is_active = r_is_active and is_active
                r_from_registration = min_registration(r_from_registration, from_registration)

                if not is_active:
                    break
            
            contract.niu_count = r_niu_count
            contract.is_active = r_is_active
            contract.from_registration = r_from_registration
            contract.is_contribuables_scanned = True
            
            try:
                retry_call(contract.save, fargs=None, fkwargs=None, tries=3, delay=60)
            except Exception as e:
                print(e)
                print(contract)
                print(r_from_registration)
                raise(e)

            if ii % 100 == 0:
                print(f"{ii} done!")

            ii += 1
            if b and ii > b:
                break

        logger.info("Exiting!")
