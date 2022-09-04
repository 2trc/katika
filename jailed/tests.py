from django.test import TestCase

from jailed.models import IncarcerationTag, Incarceration

from jailed.management.commands.jailed_twitter_bot import list_death_anniversaries, list_injust_birthdays


from datetime import datetime, timedelta


class InjustBirthdayTestCase(TestCase):

    #@classmethod
    #def setUpTestData(cls):
    def setUp(self):
        a_tag = IncarcerationTag.objects.create(name="Anglophone Crisis", name_fr="")
        i_tag = IncarcerationTag.objects.create(name="Incommunicado", name_fr="")
        j_tag = IncarcerationTag.objects.create(name="Journalist", name_fr="")

        t = datetime.strptime("2021-12-19", "%Y-%m-%d")
        THIRTY_YEARS = 365 * 30

        s = Incarceration.objects.create(birthday=datetime.strptime("2000-12-19", "%Y-%m-%d"),
                                         last_name='Bolo', first_name='Guy')
        #s.tags.add(a_tag)
        s.tags.add(i_tag, a_tag, j_tag)
        #s.save()

    def test_list_birthdays(self):

        l = list_injust_birthdays(m=12, d=19)

        for i in l:
            print(f"{i},{i.last_name},{i.first_name},{i.tags.all()}")

        self.assertEqual(1, l.count())


class DeceasedTestCase(TestCase):

    def test_deceased(self):

        self.fail("älso fail")

