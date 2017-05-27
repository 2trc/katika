from django.db import models
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from django.template.response import TemplateResponse

from django.core.paginator import Paginator
from django import forms

from wagtail.wagtailsearch import index


#from bootstrap3_datetime.widgets import DateTimePicker
#from bootstrap_datepicker.widgets import DatePicker
#from datetimewidget.widgets import DateTimeWidget


from django.utils.text import slugify

# Create your models here.

@register_snippet
class IncidentType(models.Model):

    name = models.CharField(max_length=255)
    order_key = models.IntegerField(unique=True, help_text='For ordering Incident Types')

    # parent_category = models.ForeignKey('self', null=True, blank=True)

    # gravity, meta-data?

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Incident Types'
        ordering = ['-order_key']


# INCIDENT_TYPE = (
#     ('MURDER', 'Murder'),
#     ('ACCIDENT', 'Accident'),
#     ('BRIBERY', 'Corruption and Bribery'),
#     ('KIDNAPPING', 'Kidnapping'),
#     ('TERRORISM', 'Terrorism'),
#     ('ROBBERY', 'Robbery'),
#     ('OTHER', 'Other')
# )


@register_snippet
class Incident(models.Model):
    type = models.ForeignKey(IncidentType, null=True, on_delete=models.SET_NULL)
    # type = models.CharField(max_length=20, choices=INCIDENT_TYPE, default=INCIDENT_TYPE[-1])
    #icon = models.ForeignKey(
    #    'wagtailimages.Image', null=True, blank=True,
    #    on_delete=models.SET_NULL, related_name='+'
    #)
    #type = models.Case()
    address = models.CharField(max_length=255)#, help_text="As accurate as possible<br/>Adresse aussi précise que possible")
    date = models.DateField('date')
    description = RichTextField()
    source = models.URLField()
    deaths = models.PositiveIntegerField(blank=True, null=True)
    wounded = models.PositiveIntegerField(blank=True, null=True)

    panels = [
        FieldPanel('type'),
        FieldPanel('address'),
        FieldPanel('date'),
        FieldPanel('description'),
        FieldPanel('source'),
        MultiFieldPanel([
            FieldPanel('deaths'),
            FieldPanel('wounded')
        ], heading="Casualties"),
    ]

    def __str__(self):
        return "{}: {}, {}".format(self.type, self.address, self.date)

    class Meta:
        verbose_name_plural = 'Incidents' #?
        ordering = ['-date']

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('date'),
        index.SearchField('address'),
    ]


class IncidentProject(RoutablePageMixin, Page):

    intro = RichTextField(blank=True)
    submit_info = RichTextField(blank=True)
    thanks_info = RichTextField(blank=True)

    @route(r'^$')
    def base(self, request):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request)
        )

    @route(r'^submit-incident/$')
    def submit(self, request):

        if request.method == 'GET':
            return TemplateResponse(
                request,
                'incident/submit_incident.html',
                self.get_context(request)
            )
        else:
            from .views import submit_incident
            return submit_incident(request, self)

    @route(r'^submit-thank-you/$')
    def thanks(self, request):
        return TemplateResponse(
            request,
            'incident/incident_submission_thank_you.html',
            {"thanks_info": self.thanks_info}
        )

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(IncidentProject, self).get_context(request)

        incident_list = Incident.objects.all().order_by('-date')

        paginator = Paginator(incident_list, 10)

        page = 1

        if request.method == 'GET':

            page = request.GET.get('page', 1)

        incidents = paginator.page(page)

        #blogpages = self.get_children().live().order_by('-first_published_at')
        context['incidents'] = incidents
        context['form'] = IncidentForm()
        return context


class IncidentForm(forms.ModelForm):

    #date = forms.DateField(
    #    widget= DateTimeWidget(attrs={'id': "yourdatetimeid"}, usel10n=True, bootstrap_version=3)
        #widget=DateTimeWidget(usel10n=True, bootstrap_version=3)
    #)

    #widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))
        #widget=BootstrapDateTimeInput())

    #date = forms.DateField(
    #    widget=DatePicker(options={"format": "mm/dd/yyyy", "autoclose": True}))

    class Meta:
        model = Incident
        fields = ('type', 'address', 'date', 'description',
                    'source', 'wounded', 'deaths')


