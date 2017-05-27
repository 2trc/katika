from datetime import datetime, timedelta
from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.filter
def age(value):

    time_since = timesince(value)

    if time_since == '0 minutes':
        return 'just now'
    else:
        return '%(time)s ago' % {'time': time_since.split(', ')[0]}