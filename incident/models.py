from django.db import models

from django.contrib import admin
from django import forms
from django.contrib.gis.db import models as geo_models
from django.contrib.gis import forms as geo_forms

from rest_framework import serializers
from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget

from geopy.geocoders import Nominatim

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


class IncidentTypeAdmin(admin.ModelAdmin):

    # fields = ['name', 'age', 'residence']
    fields = ['name', 'order_key']


admin.site.register(IncidentType, IncidentTypeAdmin)


class Incident(models.Model):
    type = models.ForeignKey(IncidentType, null=True, on_delete=models.SET_NULL)
    location = geo_models.PointField()
    address = models.TextField(null=True)
    # location = models.CharField(max_length=255)#, help_text="As accurate as possible<br/>Adresse aussi précise que possible")
    date = models.DateField('date')
    registration_date = models.DateField(verbose_name='registration date', auto_now=True)
    description = models.TextField()
    source = models.URLField()
    deaths = models.PositiveIntegerField(blank=True, null=True)
    wounded = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return "{}: {}, {}".format(self.type, self.date, self.address)

    class Meta:
        verbose_name_plural = 'Incidents' #?
        ordering = ['-date']

    def save(self, *args, **kwargs):
        #TODO is one instance efficient?
        geolocator = Nominatim()
        e = geolocator.reverse((self.location.y,self.location.x))
        self.address = e.address
        super(Incident, self).save(*args, **kwargs)


class IncidentAdmin(admin.ModelAdmin):

    # fields = ['name', 'age', 'residence']
    #fieldset = {'address', fields = ['type', 'location', 'date', 'description', 'source', 'deaths', 'wounded']
    fields = ['type', 'location', 'date', 'description', 'source', 'deaths', 'wounded']
    # formfield_overrides = {
    #     geo_models.PointField: {"widget": GooglePointFieldWidget}
    # }


admin.site.register(Incident, IncidentAdmin)


class IncidentForm(forms.ModelForm):

    location = geo_forms.PointField(widget=geo_forms.OSMWidget(attrs={'map_width':800,
                                                                      'map_height':500}))
    class Meta:
        model = Incident
        fields = ('type', 'location', 'date', 'description',
                    'source', 'wounded', 'deaths')

        widgets = {'location': GooglePointFieldWidget}



class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        #fields = ('url', 'username', 'email', 'groups')
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):
    #type = IncidentTypeSerializer(queryset=IncidentType.objects.all())
    #type_name = serializers.RelatedField(source='type.name')
    type = IncidentTypeSerializer()
    class Meta:
        model = Incident
        #fields = ('url', 'name')
        fields = '__all__'
