from django.core.management.base import BaseCommand, CommandError
from tender.models import WBSupplier, WBContract
import requests
import logging

from datetime import datetime
import json
from html import unescape
import time

logger = logging.getLogger(__name__)


supplier_cache = {}

def get_contract_details(contract_id):

    logger.info("Retrieving contract list for project ID: %s", contract_id)

    url = f"https://search.worldbank.org/api/contractdata?format=json&fl=*&contr_id={contract_id}&apilang=en"
    
    r = requests.get(url)

    o_json = r.json()
  
    return o_json["contract"][0]


def get_suppliers(suppinfo):
    '''
    `suppinfo` represents a list of json/dict object with supplier info 
    '''

    suppliers = []
    
    for item in suppinfo:

        s_id = item["id"]
        
        if s_id in supplier_cache:
            suppliers.append(supplier_cache[s_id])
        else:
            
            s = get_or_create_supplier(item)
            supplier_cache[item["id"]] = s

            suppliers.append(s)            
    
    return suppliers


def get_or_create_supplier(supplier_content):

    query_set = WBSupplier.objects.filter(supplier_id=supplier_content["id"])

    if len(query_set):
        return query_set[0]
    else:
        s = WBSupplier()
        s.supplier_id = supplier_content["id"]
        s.name = supplier_content["name"]
        s.country = supplier_content["country"]
        s.save()
        return s



# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):
    # https://search.worldbank.org/api/contractdata?format=json&fct=regionname_exact,countryshortname_exact,procu_meth_text_exact,procu_type_text_exact,procurement_group_desc_exact,supplier_countryshortname_exact,mjsecname_exact,sector_exact&fl=id,projectid,project_name,contr_id,contr_desc,countryshortname,total_contr_amnt,procu_meth_text,procurement_group,contr_sgn_date,countryshortname_exact,supplier_contr_amount&fl=*&os=&qterm=&srt=contr_sgn_date%20desc,id%20asc&rows=200&projectid=P151155&apilang=en

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--count',
            help='Maximum number of contracts to attend to',
            type=int
        )

        parser.add_argument(
            '-d', '--delay',
            help='Delay in between queries',
            default=0.5,
            type=float
        )

        


    def handle(self, *args, **options):

        logger.info("Starting!")

        count = options['count']
        delay = options['delay']

        start = 0
        for wb_contract in WBContract.objects.filter(is_scanned=False):
            
            try:
                contract_json = get_contract_details(wb_contract.contract_id)
                suppliers = get_suppliers(contract_json["suppinfo"])
                wb_contract.suppliers.add(*suppliers)
                wb_contract.is_scanned = True
                wb_contract.save()
                
            except Exception as e:
                logger.error("Error collecting suppliers for %s. Error: %s", wb_contract, e)
            
            start +=1
            if count and start >= count:
                break
            time.sleep(delay)

        logger.info("Exiting!")






