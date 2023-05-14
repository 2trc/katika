from django.core.management.base import BaseCommand, CommandError
from tender.models import WBProject
import requests
from bs4 import BeautifulSoup
import time, logging, os

from pytz import timezone
from datetime import datetime
from django.utils import dateparse
import json

logger = logging.getLogger(__name__)


# TODO: testing
def fetch_page(url: str, max_retries=5, sleep_retry=60):

    retry_count = 0

    while retry_count < max_retries :

        try:
            r = requests.get(url)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            logger.exception(e)
            retry_count += 1

        time.sleep(sleep_retry)

    return None

def get_pagination(options):  

    start = options['start']
    row = options['row']
    end = options['end']
    
    return start, end, row


def get_project_list(start, end, row):

    logger.info("Running with start page [%s], row [%s], end [%s]",
                 start, row, end)

    page_url = "https://search.worldbank.org/api/v2/projects?format=json&fct=projectfinancialtype_exact,status_exact,regionname_exact,theme_exact,sector_exact,countryshortname_exact,cons_serv_reqd_ind_exact,esrc_ovrl_risk_rate_exact&fl=id,regionname,countryname,projectstatusdisplay,project_name,countryshortname,pdo,impagency,cons_serv_reqd_ind,url,boardapprovaldate,closingdate,projectfinancialtype,curr_project_cost,ibrdcommamt,idacommamt,totalamt,grantamt,borrower,lendinginstr,envassesmentcategorycode,esrc_ovrl_risk_rate,sector1,sector2,sector3,theme1,theme2,%20%20status,totalcommamt,proj_last_upd_date,curr_total_commitment&apilang=en&rows={}&countrycode_exact=CM&os={}"

    
    project_list = {}
    
    while True:

        if end:
            if start >= end:
                break
        
        url = page_url.format(row, start)

        start += row

        page_content = fetch_page(url)

        project_list.update(page_content["projects"])

        if len(page_content["projects"]) < row:
            break

  
    return {"projects": project_list}


# TODO should throw exception when status not found
def get_status(status_str):
    status_str_low = status_str.lower()

    for item in WBProject.STATUS:
        if status_str_low == item[1].lower():
            return item[0]

def get_theme(theme_str):
    
    if theme_str and len(theme_str):
        main_theme = theme_str.split("!$")[0]
        if  main_theme:
            return main_theme
    
    return None



def get_sector(*sector_list):

    logger.info(sector_list)

    weight = 0
    main_sector = None

    for sector in sector_list:

        if sector:
            if sector.get("Percent") > weight:
                weight = sector["Percent"]
                main_sector = sector["Name"]
    
    logger.info("Main sector returned: %s", main_sector)
    return main_sector

def get_financial_type(projectfinancialtype):
    # Return first item that is not "Other"
    logger.info("retrieveing financial type")
    if not projectfinancialtype or len(projectfinancialtype)==0:
        return None
    
    for item in projectfinancialtype:
        if "Other" != item:
            logger.info("Financial type retrieved: %s", item)
            return item

def convert_to_wb_project(project):

    wb_project = WBProject()

    wb_project.project_id = project.get("id")
    wb_project.name = project.get("project_name")
    if project.get("project_abstract"):
        wb_project.abstract = project.get("project_abstract").get("cdata!")
    wb_project.link = project.get("url")
    wb_project.financial_type = get_financial_type(project.get("projectfinancialtype"))
    wb_project.status = get_status(project.get("status"))
    wb_project.agency = project.get("impagency")
    
    #"boardapprovaldate": "2018-05-01T00:00:00Z"
    boardapprovaldate = project.get("boardapprovaldate")
    if boardapprovaldate:
        wb_project.start_date = dateparse.parse_datetime(boardapprovaldate).date()
    #"closingdate": "12/31/2026 12:00:00 AM"
    closingdate = project.get("closingdate")
    if closingdate:
        wb_project.end_date = datetime.strptime(closingdate.split(" ")[0], "%m/%d/%Y").date()
    
    #"proj_last_upd_date": "2023-02-15T00:00:00Z"
    proj_last_upd_date = project.get("proj_last_upd_date")
    if proj_last_upd_date:
        wb_project.last_update = dateparse.parse_datetime(proj_last_upd_date).date()
    
    wb_project.cost = int(project.get("totalamt").replace(",", ""))
    logger.info("converting cost worked: %s", wb_project.cost)

    wb_project.lendinginstr = project.get("lendinginstr")
    wb_project.main_theme = get_theme(project.get("theme1"))
    wb_project.main_sector = get_sector(project.get("sector1"), project.get("sector2"), project.get("sector3"))

    return wb_project


# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):
    # https://search.worldbank.org/api/v2/projects?format=json&fct=projectfinancialtype_exact,status_exact,regionname_exact,theme_exact,sector_exact,countryshortname_exact,cons_serv_reqd_ind_exact,esrc_ovrl_risk_rate_exact&fl=id,regionname,countryname,projectstatusdisplay,project_name,countryshortname,pdo,impagency,cons_serv_reqd_ind,url,boardapprovaldate,closingdate,projectfinancialtype,curr_project_cost,ibrdcommamt,idacommamt,totalamt,grantamt,borrower,lendinginstr,envassesmentcategorycode,esrc_ovrl_risk_rate,sector1,sector2,sector3,theme1,theme2,%20%20status,totalcommamt,proj_last_upd_date,curr_total_commitment&apilang=en&rows=20&countrycode_exact=CM&os=80

    def add_arguments(self, parser):

        parser.add_argument(
            '-s', '--start',
            help='row from where to start',
            type=int,
            default=0
        )

        parser.add_argument(
            '-e', '--end',
            help='row where to end',
            type=int
        )

        parser.add_argument(
            '-r', '--row',
            help='row size',
            type=int,
            default=20
        )

        parser.add_argument(
            '-i', '--input',
            help='Input file name',
            type=str
        )

        parser.add_argument(
            '-o', '--output',
            help='Output file name',
            type=str
        )


    def handle(self, *args, **options):

        logger.info("Starting!")

        if options['input']:
            i_filename = options['input']

            with open(i_filename, 'r') as f:
                project_list = json.load(f)

        else:
            start, end, row = get_pagination(options)
            project_list = get_project_list(start, end, row)

        if options['output']:

            o_filename = options['output']
            
            try:
                with open(o_filename, "w") as f:
                    json.dump(project_list, f)
            except IOError as e:
                logger.error("Error opening %s, %s", o_filename, e)
        else:
            for project in project_list["projects"]:

                try:                
                    wb_project = convert_to_wb_project(project_list["projects"][project])
                    wb_project.save()
                except Exception as e:
                    logger.error("Error converting and saving project %s", e)

        logger.info("Exiting!")






