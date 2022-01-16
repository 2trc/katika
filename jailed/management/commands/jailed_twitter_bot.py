from django.core.management.base import BaseCommand, CommandError
import logging
from datetime import datetime
import time
from jailed.models import Incarceration
import tweepy

logger = logging.getLogger(__name__)

MAX_LENGTH=280

#jailed237
consumer_key = "LeBWiBoil99o7UzFZOWlvXmof"
consumer_secret = "WTGIaFWedmI7iMquXhwRC4pS80ZrMMVsikFsg0Cqw0jyP1pdE2"
access_token = "1472564228414480384-Cx7N6BbUEhYZUe9chLPHyiSjNPvhYZ"
access_token_secret = "rYczX5ufGITU7xUdEZQzw8Z7r6NCp4Yd3l7d4aufhHGLa"
#b = "AAAAAAAAAAAAAAAAAAAAALrQXAEAAAAA36X628VPjTWOiiBrsy%2BgbmdVRZk%3DBLWksD9mYrsFBKN19Pb84F60CPBgojkbmMqdBEhXIlaSWAssO4"


def initialize(c_key, c_secret, a_token, a_token_secret):

    #v1
    auth = tweepy.OAuthHandler(c_key, c_secret)

    # set access to user's access key and access secret
    auth.set_access_token(a_token, a_token_secret)

    # calling the api
    api = tweepy.API(auth, wait_on_rate_limit=True)

    return api

    #v2
    # return tweepy.Client(bearer_token=bearer, consumer_key=c_key, consumer_secret=c_secret,
    #                      access_token=a_token, access_token_secret=a_token_secret,
    #                      wait_on_rate_limit=True)



def clip_tweet(msg):

    return msg[:MAX_LENGTH]


def get_pretrial_str(l)->str:

    if l.conviction_date or l.conviction_duration_years or l.conviction_duration_months or l.conviction_duration_days:
        return ""
    else:
        return "pre-trial"


def build_tweet_for_deceased(l)->str:

    msg = "In memory of {} who died in {} detention this day on {}".format(
        str(l),
        get_pretrial_str(l),
        l.release_date.strftime("%Y-%m-%d"))

    if l.prison:
        msg += "\nat {}".format(l.prison.name)

    return clip_tweet(msg)


def build_tweet_for_tags(l)->str:

    if l.dates_inaccurate:
        msg = "We are \"celebrating\" {}'s birthday today in {} detention".format(
            str(l),
            get_pretrial_str(l)
        )
    else:
        msg = "{} is \"celebrating\" his/her birthday in {} detention".format(
            str(l),
            get_pretrial_str(l)
        )

    tag_list = [a.name for a in l.tags.all()]

    if "Incommunicado" in tag_list:
        msg += " INCOMMUNICADO"
    elif l.prison:
        msg += " at {}".format(l.prison.name)

    if l.dates_inaccurate:
        msg += "\nS/he was born around {}".format(l.birthday.year)

    if "Anglophone Crisis" in tag_list:
        msg += "\n#EndAnglophoneCrisis\n#FreeAllPoliticalPrisoners"
    elif "Political Prisoner" in tag_list:
        msg += "\n#FreeAllPoliticalPrisoners"
    elif "Journalist" in tag_list:
        msg += "\n#JournalismIsNotACrime"
    elif "LGBTQ" in tag_list:
        msg += "\n#LGBTQ"

    return clip_tweet(msg)


def list_injust_birthdays(m:int, d:int):

    l = Incarceration.objects.filter(birthday__month=m).filter(birthday__day=d).filter(
        release_date__isnull=True
    ).filter(
        tags__name__in = ["Anglophone Crisis", "Political Prisoner",
                          'Incommunicado', 'Journalist', 'LGBTQ']
    )

    return l


def list_death_anniversaries(m:int, d:int):

    l = Incarceration.objects.filter(deceased=True).filter(release_date__month=m).filter(release_date__day=d)

    return l


def publish_tweets(tweet_list):

    #print(tweet_list)

    #return

    api = initialize(consumer_key, consumer_secret, access_token, access_token_secret)

    for t in tweet_list:

        logger.info(t)

        try:
            api.update_status(t)
            # client.create_tweet(text=formatted)
            time.sleep(10)
        except tweepy.errors.BadRequest as e:
            logger.error("Tweeting failed with error: %s", e)
        except Exception as e:
            logger.exception(e)

    return


class Command(BaseCommand):

    def handle(self, *args, **options):

        logger.info("Starting!")

        curr_date = datetime.now()
        curr_m = curr_date.month
        curr_d = curr_date.day

        #lister
        #tweets = []

        #anniversaire de personnes injustement détenu-e-s
        tweets = [build_tweet_for_tags(t) for t in list_injust_birthdays(curr_m, curr_d)]
        #anniversaire de décès en incarcerration
        tweets += [build_tweet_for_deceased(t) for t in list_death_anniversaries(curr_m, curr_d)]

        #twitter la liste
        publish_tweets(tweets)

        logger.info("Exiting!")
