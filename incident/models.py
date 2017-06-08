from django.db import models

from rest_framework import serializers


# Create your models here.
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


class Incident(models.Model):
    type = models.ForeignKey(IncidentType, null=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=255)#, help_text="As accurate as possible<br/>Adresse aussi précise que possible")
    date = models.DateField('date')
    registration_date = models.DateField(verbose_name='registration date', auto_now=True)
    description = models.TextField()
    source = models.URLField()
    deaths = models.PositiveIntegerField(blank=True, null=True)
    wounded = models.PositiveIntegerField(blank=True, null=True)

    # panels = [
    #     FieldPanel('type'),
    #     FieldPanel('address'),
    #     FieldPanel('date'),
    #     FieldPanel('description'),
    #     FieldPanel('source'),
    #     MultiFieldPanel([
    #         FieldPanel('deaths'),
    #         FieldPanel('wounded')
    #     ], heading="Casualties"),
    # ]

    def __str__(self):
        return "{}: {}, {}".format(self.type, self.location, self.date)

    class Meta:
        verbose_name_plural = 'Incidents' #?
        ordering = ['-date']

    # search_fields = Page.search_fields + [
    #     index.SearchField('description'),
    #     index.SearchField('date'),
    #     index.SearchField('address'),
    # ]


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        #fields = ('url', 'username', 'email', 'groups')
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    #type = IncidentTypeSerializer(queryset=IncidentType.objects.all())
    #type = serializers.RelatedField(source='type', read_only=True)
    class Meta:
        model = Incident
        #fields = ('url', 'name')
        fields = '__all__'