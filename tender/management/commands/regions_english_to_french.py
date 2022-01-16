from django.core.management.base import BaseCommand, CommandError
from tender.models import ArmpEntry
import logging

logger = logging.getLogger(__name__)


# TODO: testing
# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):

    def handle(self, *args, **options):

        region_list = {
            "WEST": "OUEST" ,
            "EAST": "EST",
            "CENTER": "CENTRE",
            "NORTH-WEST": "NORD-OUEST",
            "SOUTH-WEST": "SUD-OUEST",
            "FAR-NORTH": "EXTRÊME-NORD",
            "NORTH": "NORD",
            "ADAMAWA": "ADAMAOUA",
            "SOUTH": "SUD",
            "CENTRAL SERVICES": "SERVICES CENTRAUX"
        }

        for r_en, r_fr in region_list.items():

            ArmpEntry.objects.filter(region=r_en).update(region=r_fr)

