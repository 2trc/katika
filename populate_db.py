import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'katika.settings')

import django
from django.conf import settings
django.setup()


def populate():

	from jailed.models import Prison
	from django.contrib.gis.geos import GEOSGeometry
	p = GEOSGeometry('POINT(4.06388 9.71237)', srid=4326)

	p1 = Prison.objects.create(name="Japap", location=p)
	p2 = Prison.objects.create(name="ngata", location=p)

	from jailed.models import Incarceration

	i1 = Incarceration.objects.create(last_name="Ebosse", sex=0, prison=p1)
	i2 = Incarceration.objects.create(last_name="Abama", first_name="Solange", sex=1, prison=p2)

	from tender.models import TenderOwner

	o1 = TenderOwner.objects.create(owner_id=1, short_name="PRC", full_name="La Présidence ôôôô")
	o2 = TenderOwner.objects.create(owner_id=1000, short_name="Bizz", full_name="Bizz Group LTD")

	from tender.models import ArmpEntry
	from datetime import datetime

	ArmpEntry.objects.create(title="AO for a few TV monitors", link=settings.SITE_HOST, owner=o1, 
		publication_type="AO", verbose_type="Appel d'Offres", region="SUD")
	ArmpEntry.objects.create(title="Decision d'Attribution d'achat Numéro xxxx", 
		link=settings.SITE_HOST, owner=o2, publication_datetime=datetime.today(), region="CENTRE")

	from incident.models import IncidentType
	t = IncidentType()
	t.name="No sure"
	t.order_key=3
	t.save()

	from incident.models import Incident
	from datetime import date

	Incident.objects.create(type=t, location=p, date=date.today())


if __name__ == "__main__":
	populate()