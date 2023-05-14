from django.test import TestCase

from tender.models import WBContract, WBSupplier
from tender.management.commands.get_wb_suppliers import get_or_create_supplier, get_suppliers
from django.db import IntegrityError
from datetime import date

# psycopg2.ProgrammingError: text search configuration "french_unaccent" does not exist
# LINE 1: ...nder_wbproject" SET "search_vector" = to_tsvector('french_un...
# https://www.dbi-services.com/blog/what-the-hell-are-these-template0-and-template1-databases-in-postgresql/
class TestWBSupplier(TestCase):

    def test_normal(self):

        supp_info = [
				{
					"name": "LUXAN ENGINEERING",
					"id": "471294",
					"countryshortname": "Cameroon",
					"countryname": "Republic of Cameroon",
					"country": "CM",
					"supplier_contr_amount": "651671.68"
				},
				{
					"name": "TPF CONSULTORES",
					"id": "471305",
					"countryshortname": "Portugal",
					"countryname": "Portuguese Republic",
					"country": "PT",
					"supplier_contr_amount": "651671.68"
				}
			]

        
        s = get_or_create_supplier(supp_info[0])

        self.assertEqual(s.supplier_id, "471294")

        self.assertEqual(1, WBSupplier.objects.count())

        s1 = get_or_create_supplier(supp_info[0])

        self.assertEqual(s1.supplier_id, "471294")

        self.assertEqual(1, WBSupplier.objects.count())

        s2 = get_or_create_supplier(supp_info[1])

        self.assertEqual(s2.supplier_id, "471305")

        self.assertEqual(2, WBSupplier.objects.count())

