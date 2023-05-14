from django.test import TestCase

from tender.models import WBProject
from tender.management.commands.get_wb_projects import convert_to_wb_project, get_sector, get_theme
from django.db import IntegrityError
from datetime import date

class TestWBProject(TestCase):

    def test_normal(self):

        json_project = {
            "curr_project_cost": "205500000",
            "curr_total_commitment": "150",
            "id": "P039856",
            "projectfinancialtype": [
                "IDA"
            ],
            "regionname": "Western and Central Africa",
            "countryname": [
                "Republic of Cameroon"
            ],
            "lendinginstr": "Sector Adjustment Loan",
            "projectstatusdisplay": "Closed",
            "project_name": "Structural Adjustment Credit (02) Project",
            "totalamt": "150,000,000",
            "countryshortname": "Cameroon",
            "sector1": {
                "Name": "Central Government (Central Agencies)",
                "Percent": 32
            },
            "sector2": {
                "Name": "Banking Institutions",
                "Percent": 29
            },
            "sector3": {
                "Name": "Other Industry, Trade and Services",
                "Percent": 18
            },
            "theme1": "Macroeconomic management!$!24!$!23",
            "theme2": "Other financial and private sector development!$!13!$!44",
            "totalcommamt": "150,000,000",
            "boardapprovaldate": "1996-02-08T00:00:00Z",
            "closingdate": "1/21/1999 12:00:00 AM",
            "url": "https://projects.worldbank.org/en/projects-operations/project-detail/P039856",
            "envassesmentcategorycode": "C",
            "idacommamt": "150,000,000",
            "ibrdcommamt": "0",
            "status": "Closed",
            "proj_last_upd_date": "2013-01-15T00:00:00Z",
            "project_abstract": {
                "cdata!": "The Health and Population Sector Operation"
            }
        }

        wb_project = convert_to_wb_project(json_project)

        self.assertEqual(wb_project.project_id, "P039856")
        self.assertEqual(wb_project.cost, 150000000)
        self.assertEqual(wb_project.status, WBProject.CLOSED)
        self.assertEqual(wb_project.link, "https://projects.worldbank.org/en/projects-operations/project-detail/P039856")
        self.assertEqual(wb_project.start_date, date(1996, 2, 8))
        self.assertEqual(wb_project.end_date, date(1999, 1, 21))
        self.assertEqual(wb_project.last_update, date(2013, 1, 15))
        self.assertEqual(wb_project.main_sector, "Central Government (Central Agencies)")
        self.assertEqual(wb_project.main_theme, "Macroeconomic management")
        self.assertEqual(wb_project.abstract, "The Health and Population Sector Operation")

    
    def test_main_sector(self):
        
        sector1 = { "Name": "Early Childhood Education", "Percent": 21 }
        sector2 = { "Name": "Social Protection", "Percent": 46}
        sector3 = { "Name": "Health", "Percent": 20 }

        main_sector = get_sector(sector1, sector2, sector3)

        self.assertEqual(main_sector, "Social Protection")


    def test_main_theme(self):
        t1 = get_theme("!$!0")

        self.assertIsNone(t1)

        t2 = get_theme("Other financial and private sector development!$!14!$!44")
        self.assertEqual(t2, "Other financial and private sector development")

        t3 = get_theme("Law reform!$!29!$!33")
        self.assertEqual(t3, "Law reform")

