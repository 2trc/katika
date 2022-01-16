from django.core.management.base import BaseCommand, CommandError
import logging
import os
#from os import path
import json
from budget.models import BudgetProgramme, Chapitre

logger = logging.getLogger(__name__)


def dict_to_programme(in_json):

    o = BudgetProgramme()

    o.year = 2021 - ( 55 - int(in_json['idExercice']) )
    o.pg_id = in_json["id"]
    o.exercice_id = in_json["idExercice"]
    o.code = in_json["pgCode"]
    o.ae = int(1000*float(in_json["AE"]))
    o.cp = int(1000 *float(in_json["CP"]))
    o.description_fr = in_json["pgLibelleFr"]
    o.description_en = in_json["pgLibelleEn"]
    o.objective_fr = in_json["obLibelleFr"]
    o.objective_en = in_json["obLibelleEn"]
    o.indicator_fr = in_json["inLibelleFr"]
    o.indicator_en = in_json["inLibelleEn"]

    c = Chapitre.objects.filter(number=int(in_json["chCode"]))
    if not c.count():
        short_name = in_json["chAbreviation"]
        if len(short_name) > 20:
            short_name = short_name[:20]
        c = Chapitre.objects.create(
            number = int(in_json["chCode"]),
            short_name = short_name,
            full_name_fr = in_json["chLibelleFr"],
            full_name_en = in_json["chLibelleEn"]
        )
    else:
        c = c[0]

    o.chapitre = c

    return o


class Command(BaseCommand):

    def handle(self, *args, **options):

        logger.info("Starting!")

        folder_name = "budget/data/"

        for file_name in os.listdir(folder_name):

            logger.info("Handling %s", file_name)

            with open(os.path.join("budget/data", file_name), "r") as f:

                try:
                    in_json = json.load(f)
                except Exception as e:
                    logger.exception(e)
                    continue

                if not in_json:
                    continue

                for record in in_json["records"]:

                    o = dict_to_programme(record)

                    try:
                        o.save()
                    except Exception as e:
                        logger.error("Error saving: %s", record)
                        logger.exception(e)

        logger.info("Exiting!")
