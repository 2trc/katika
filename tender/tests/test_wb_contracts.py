from django.test import TestCase

from tender.models import WBProject, WBContract
from tender.management.commands.get_wb_contracts import convert_to_wb_contract
from django.db import IntegrityError
from datetime import date

# psycopg2.ProgrammingError: text search configuration "french_unaccent" does not exist
# LINE 1: ...nder_wbproject" SET "search_vector" = to_tsvector('french_un...
# https://www.dbi-services.com/blog/what-the-hell-are-these-template0-and-template1-databases-in-postgresql/
class TestWBContract(TestCase):

    def test_normal(self):

        PROJECT_ID = "P151155"
        json_contracts = {
            "contract": [
                {
                    "id": "1709191",
                    "project_name": "CAMEROON - Strengthening Public Sector Effectiveness and Statistical Capacity Project",
                    "contr_id": "1709191",
                    "contr_sgn_date": "18-Aug-2022",
                    "countryshortname": "Cameroon",
                    "projectid": PROJECT_ID,
                    "contr_desc": "ACQUISITION DES MOTOS TOUT TERRAIN POUR LE COMPTE DU PROJET PEPS",
                    "total_contr_amnt": "88933.0",
                    "supplier_contr_amount": "88933.12",
                    "procurement_group": "GO",
                    "procu_meth_text": "Request for Quotations"
                },
                {
                    "id": "1709247",
                    "project_name": "CAMEROON - Strengthening Public Sector Effectiveness and Statistical Capacity Project",
                    "contr_id": "1709247",
                    "contr_sgn_date": "16-Aug-2021",
                    "countryshortname": "Cameroon",
                    "projectid": PROJECT_ID,
                    "contr_desc": "Acquisition d'un minibus pour la coordination du projet PEPS",
                    "total_contr_amnt": "49049.0",
                    "supplier_contr_amount": "49049.41",
                    "procurement_group": "GO",
                    "procu_meth_text": "Request for Quotations"
                }
            ]
        }

        project = WBProject()
        project.project_id="P151155"
        project.link="https://google.com"
        project.save()

        contract_1 = convert_to_wb_contract(json_contracts["contract"][0])
        contract_2 = convert_to_wb_contract(json_contracts["contract"][1])

        self.assertEqual(contract_1.project.project_id, PROJECT_ID)
        self.assertEqual(contract_2.project.project_id, PROJECT_ID)

        self.assertEqual(contract_1.contract_id, "1709191")
        self.assertEqual(contract_2.description, "Acquisition d'un minibus pour la coordination du projet PEPS")

        self.assertEqual(contract_1.cost, 88933)

    

