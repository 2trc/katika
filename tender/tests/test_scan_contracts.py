from django.test import TestCase

from tender.models import Exercice
from tender.management.commands.scan_contracts_contribuables import clean_enterprise_name\
    , was_enterprise_active, get_registration_delta, min_registration
from django.db import IntegrityError
from datetime import date

class TestScanContracts(TestCase):

    def test_clean_enterprise(self):

        name = "ETS Watson"
        self.assertEqual("Watson", clean_enterprise_name(name))

        name = "Wat ETS SA"
        self.assertEqual("Wat ETS", clean_enterprise_name(name))

        name = "My name sarl"
        self.assertEqual("My name", clean_enterprise_name(name))

        name = "last_name s.A"
        self.assertEqual("last_name", clean_enterprise_name(name))

        name = " GRPT TRACTEBEL ENGINEERING "
        self.assertEqual("TRACTEBEL ENGINEERING", clean_enterprise_name(name))

        name = "GROUPEMENT CHANAS"
        self.assertEqual("CHANAS", clean_enterprise_name(name))
    

    def test_was_enterprise_active(self):

        excercise_list = [Exercice(month= 1, year= 2020), 
                          Exercice(month= 12, year= 2019),
                          Exercice(month= 10, year= 2019)]

        c_date = date(2019, 12, 25)
        self.assertTrue(was_enterprise_active(c_date, excercise_list))

        c_date = date(2019, 10, 1)
        self.assertTrue(was_enterprise_active(c_date, excercise_list))

        c_date = date(2020, 2, 10)
        self.assertFalse(was_enterprise_active(c_date, excercise_list))

        c_date = date(2019, 11, 13)
        self.assertFalse(was_enterprise_active(c_date, excercise_list))

        c_date = date(2010, 3, 30)
        self.assertFalse(was_enterprise_active(c_date, excercise_list))


        self.assertFalse(was_enterprise_active(c_date, []))


    def test_registration_delta(self):

        earliest = Exercice(month=5, year=2018)
        c_date = date(2018, 8, 30)

        self.assertEqual(3, get_registration_delta(c_date, earliest))

        c_date = date(2018, 5, 15)
        self.assertEqual(0, get_registration_delta(c_date, earliest))
        
        c_date = date(2017, 5, 15)
        self.assertEqual(-11, get_registration_delta(c_date, earliest))

        c_date = date(2019, 6, 15)
        self.assertEqual(13, get_registration_delta(c_date, earliest))

    
    def test_min_registration(self):

        self.assertEqual( 2, min_registration(12, 2))
        self.assertEqual( 3, min_registration(3, 11))
        self.assertEqual( 5, min_registration(None, 5))
        self.assertEqual( 6, min_registration(6, None))
        self.assertIsNone(min_registration(None, None))
