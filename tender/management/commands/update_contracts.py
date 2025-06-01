import time

from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, date
import logging, os
from tender.models import ArmpContract
from bs4 import BeautifulSoup as bs
import re
from django.db.utils import IntegrityError
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_and_populate(page_raw_text, year, status):

    pattern = re.compile("[a-z ]", re.IGNORECASE)

    s = bs(page_raw_text, "html.parser")
    trs = s.tbody.find_all("tr")
    ii = 0
    logger.info("trs count()=%s", len(trs))
    for tr in trs:
        tds = tr.find_all("td")
        contract = ArmpContract()
        contract.maitre_ouvrage = re.sub(" +", " ", tds[0].text.strip())
        contract.reference = tds[1].text.strip()
        contract.title = tds[2].text.strip()
        my_day = tds[6].text.strip()
        if my_day:
            contract.date = datetime.strptime(my_day, "%d-%m-%Y")

        try:
            contract.cost = int(pattern.sub("", tds[9].text.strip()))
            contract.titulaire = re.sub("[ ,]+", " ", tds[10].text.strip())
        except IndexError as e:
            # seems new contracts don't necessarily have columns for INFRUCTUEUX
            #logger.error(e)
            #logger.error(tr)
            #exit(0)
            pass
        except ValueError as e:
            logger.error(tr)
            logger.error(e)
            exit(1)

        contract.status = status
        contract.year = year

        try:
            contract.save()
            ii += 1
        except IntegrityError as e:

            if ii%1000 == 0:
                logger.info("%s", ii)

            g = ArmpContract.objects.filter(maitre_ouvrage=contract.maitre_ouvrage,
                                            titulaire=contract.titulaire,
                                            title=contract.title,
                                            year=contract.year,
                                            reference=contract.reference)
            if g.count() == 0:
                logger.error(contract)
                continue

            if g.count() != 1:
                logger.warning("Unexpected finding count %s, %s", g.count(), contract)

            g = g[0]
            if g.status < status:
                logger.info("%s to be updated from %s to %s", g, g.status, status)
                g.status = status
                g.save()

        ii += 1

    logger.info("%s new contracts saved!", ii)


class Command(BaseCommand):
    # Todo add possibility to grab only certain page - range

    def add_arguments(self, parser):

        parser.add_argument(
            '-d', '--directory',
            help='Directory source',
            type=str
        )
        parser.add_argument(
            '-y', "--year",
            help="Year to parse",
            type=str
            )

    def handle(self, *args, **options):

        logger.info("Starting!")

        d = options['directory']

        if d:

            logger.info("Getting input from folder: %s", d)

            for filename in sorted(os.listdir(d)):
                print(filename)

                filename_split = filename.split('_')
                status = int(filename_split[2])
                year = int(filename_split[3].replace(".html", ""))

                with open(os.path.join(d,filename), "r", encoding="utf-8") as f:
                    parse_and_populate(f.read(), year, status)

        else:
            year = options["year"]
            if not year:
                year = date.today().year

            for status in range(1, 7):
                try:
                    # https://www.armp.cm/filtres?type=contrat&val=4
                    # https://www.armp.cm/filtres_avancee?filtre=contrat&valeur_filtre=4&type_maitre_ouvrage=CTD&nature_prestation=SPI&type_procedure=4&region=4&etat_du_projet=4&type_maitre_ouvrage=4&seuil=Choisir...&periode=4&exercice=2023
                    # url = f"https://www.armp.cm/filtres_avancee?filtre=contrat&valeur_filtre={status}&exercice={year}"
                    # https://www.armp.cm/filtres_avancee?filtre=contrat&valeur_filtre=1&type_maitre_ouvrage=MIN&nature_prestation=AG&type_procedure=1&region=1&etat_du_projet=2&type_maitre_ouvrage_avis=1&seuil=1&periode=1&tableau_de_bord=1&periode_recours=Choisir...&exercice=2023
                    # url = f"https://www.armp.cm/filtres_avancee?filtre=contrat&valeur_filtre={status}&etat_du_projet=3&exercice={year}"
                    url = f"https://www.armp.cm/filtres_avancee?filtre=contrat&valeur_filtre=1&type_maitre_ouvrage=MIN&nature_prestation=AG&type_procedure=1&region=1&etat_du_projet={status}&type_maitre_ouvrage_avis=1&seuil=1&periode=1&tableau_de_bord=1&periode_recours=Choisir...&exercice={year}"
                    print(url)
                    r = requests.get(url)
                    parse_and_populate(r.text, year, status)
                except Exception as e:
                    logger.error("failure handling %s", url)
                    logger.exception(e)
                    time.sleep(5)

        logger.info("Exiting!")

