from django.db import models
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.models import Page

from django.forms import forms


# Create your models here.
@register_snippet
class HistoryEvent(models.Model):
    #type = models.ForeignKey(IncidentType, on_delete=models.PROTECT)
    #type = models.CharField(max_length=1, choices=INCIDENT_TYPE, default=INCIDENT_TYPE[-1])
    #icon = models.ForeignKey(
    #    'wagtailimages.Image', null=True, blank=True,
    #    on_delete=models.SET_NULL, related_name='+'
    #)
    #type = models.Case()

    date = models.DateField('date')
    description = models.TextField()

    panels = [

        #FieldPanel('address'),
        FieldPanel('date'),
        FieldPanel('description'),
        #FieldPanel('source')
    ]

    def __str__(self):
        description_len = len(self.description)

        short = self.description if description_len < 10 else self.description[:9]

        return "{}: {}".format(self.date, short)

    class Meta:
        verbose_name_plural = 'Kamerun history events' #?


class Kistory(Page):

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(Kistory, self).get_context(request)

        event_list = HistoryEvent.objects.all().order_by('-date')

        paginator = HistoryEvent(event_list, 10)

        page = 1

        if request.method == 'GET':

            page = request.GET.get('page', 1)

        events = paginator.page(page)

        #blogpages = self.get_children().live().order_by('-first_published_at')
        context['events'] = events
        return context