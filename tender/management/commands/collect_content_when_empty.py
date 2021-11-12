from django.core.management.base import BaseCommand, CommandError
from tender.models import ArmpEntry
import requests
from bs4 import BeautifulSoup
import time
from django.db.models import Q


# TODO: logging in file and std.ou?
# TODO: testing

# ref: https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
class Command(BaseCommand):

    def handle(self, *args, **options):

        list_of_interest = ArmpEntry.objects.filter(
            Q(content__isnull=True)
            | Q(content__exact='')
        )

        ii = 0
        total = list_of_interest.count()

        print("{} entries found".format(total))

        s = requests.Session()

        for entry in list_of_interest:

            print("Processing {}".format(entry.link))
            r = s.get(entry.link)
            soup = BeautifulSoup(r.text, 'html.parser')

            entry.content = soup.text
            try:
                entry.original_link = soup.find(class_="float-left").a.get("href")
            except Exception as e:
                print(e)

            entry.save()
            ii += 1

            print("{:.3f}% done!".format(100.0*ii/total))

            time.sleep(5)

        s.close()
