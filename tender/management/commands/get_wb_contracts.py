from django.core.management.base import BaseCommand, CommandError
from tender.models import WBProject, WBContract
import requests
import logging

from datetime import datetime
import json
from html import unescape
import time

logger = logging.getLogger(__name__)


project_id_cache = {}

def get_contract_list(project_id):

    logger.info("Retrieving contract list for project ID: %s", project_id)

    page_url = "https://search.worldbank.org/api/contractdata?format=json&fct=regionname_exact,countryshortname_exact,procu_meth_text_exact,procu_type_text_exact,procurement_group_desc_exact,supplier_countryshortname_exact,mjsecname_exact,sector_exact&fl=id,projectid,project_name,contr_id,contr_desc,countryshortname,total_contr_amnt,procu_meth_text,procurement_group,contr_sgn_date,countryshortname_exact,supplier_contr_amount&fl=*&os=&qterm=&srt=contr_sgn_date%20desc,id%20asc&rows={}&projectid={}&apilang=en"
    
    # we start with 200
    rows = 200
    url = page_url.format(rows, project_id)
    r = requests.get(url)
    o_json = r.json()
    

    if rows < o_json["total"]:
        rows = o_json["total"]
        url = page_url.format(rows, project_id)
        r = requests.get(url)
    
    o_text = r.text
    o_json = json.loads(unescape(o_text))    
  
    return {"contract": o_json["contract"]}


def get_project(project_id):

    if project_id in project_id_cache:
        return project_id_cache[project_id]
    else:
        project = WBProject.objects.filter(project_id=project_id)[0]
        project_id_cache[project_id] = project
        return project


def convert_to_wb_contract(contract):

    wb_contract = WBContract()

    wb_contract.contract_id = contract.get("id")
    wb_contract.description = contract.get("contr_desc")
    #"contr_sgn_date": "18-Aug-2022"
    date = contract.get("contr_sgn_date")
    if date:
        wb_contract.date = datetime.strptime(date, "%d-%b-%Y").date()
    
    if contract.get("total_contr_amnt"):
        wb_contract.cost = int(float(contract.get("total_contr_amnt")))
    
    wb_contract.procurement_group = contract.get("procurement_group")
    wb_contract.procurement_meth_text = contract.get("procu_meth_text")

    wb_contract.project = get_project(contract["projectid"])

    return wb_contract


def handle_contract_list(contract_list):
    
    for contract in contract_list:

        try:                
            wb_contract = convert_to_wb_contract(contract)
            wb_contract.save()
        except Exception as e:
            logger.error("Error converting and saving contract %s", e)


# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):
    # https://search.worldbank.org/api/contractdata?format=json&fct=regionname_exact,countryshortname_exact,procu_meth_text_exact,procu_type_text_exact,procurement_group_desc_exact,supplier_countryshortname_exact,mjsecname_exact,sector_exact&fl=id,projectid,project_name,contr_id,contr_desc,countryshortname,total_contr_amnt,procu_meth_text,procurement_group,contr_sgn_date,countryshortname_exact,supplier_contr_amount&fl=*&os=&qterm=&srt=contr_sgn_date%20desc,id%20asc&rows=200&projectid=P151155&apilang=en

    def add_arguments(self, parser):

        parser.add_argument(
            '-c', '--count',
            help='How many projects to scanned',
            type=int
        )

        parser.add_argument(
            '-d', '--delay',
            help='Delay in between queries',
            default=2,
            type=float
        )


    def handle(self, *args, **options):

        logger.info("Starting!")

        count = options["count"]

        delay = options["delay"]

        start = 1



        for project in WBProject.objects.filter(is_scanned=False):

            logger.info("Processing project ID: %s\tName: %s", project.project_id, project.name)
            contract_list = get_contract_list(project.project_id)
            handle_contract_list(contract_list["contract"])
            project.is_scanned = True
            project.save()

            if count and start >= count:
                break

            start += 1

            time.sleep(delay)
            
        logger.info("Exiting!")






