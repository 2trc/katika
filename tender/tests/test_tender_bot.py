from django.test import TestCase
from tender.models import ArmpEntry, TenderOwner
from datetime import datetime, timedelta
from tender.management.commands.tender_twitter_bot import *

# Create your tests here.


class TestTenderBot(TestCase):

    def setUp(self):

        a = TenderOwner.objects.create(
            owner_id = 12,
            short_name = "ab",
            full_name = "aaaa bbbb"
        )

        b = TenderOwner.objects.create(
            owner_id=21,
            short_name="ba",
            full_name="bbbb aaaa",
        )

        t = datetime.today()

        ArmpEntry.objects.create(
            owner=a,
            publication_datetime =t ,
            title = "asdasdasd Voiture asdasda",
            content= "asdasda Véhicules asdasda Meubles Pneus",
            link= "http://a.com",
            cost = 2

        )

        ArmpEntry.objects.create(
            owner=b,
            publication_datetime = t - timedelta(hours=1),
            title = "zzzzzzzzz Mobilier azazaazaza",
            content= "",
            link= "http://b.com",
            cost = 3
        )

        ArmpEntry.objects.create(
            owner=b,
            publication_datetime = t - timedelta(hours=2),
            title = "zzzzzzzzz Immobilier azazaazaza",
            content= """RELEASE NO. A/171/C/MINEDUB/SG/DRFM/UGSC-C2DE/EPM/AA 
            OF 15/11/2021 PUBLISHING THE RESULTS OF THE CALL FOR EXPRESSION 
            OF INTEREST NO. 002/A/171/ASMI/MINEDUB/SG/DRFM/UGSC-C2DE/EPM/AA/2021 
            OF 28 JULY 2021 ON""",
            link= "http://c.com",
            cost = 3
        )

    def test_twitter_get_recent_entries(self):
        entries = get_recent_entries()

        self.assertEqual(2, len(entries))

        self.assertEqual("#EndMotoCraziness", entries[0][1])
        self.assertEqual("#MarchesPublics237", entries[1][1])
