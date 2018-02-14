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
    missing = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return "{}: {}, {}".format(self.type, self.date, self.address)

    class Meta:
        verbose_name_plural = 'Incidents' #?
        ordering = ['-date']


    def get_address(self):
        geolocator = Nominatim()
        e = geolocator.reverse((self.location.y, self.location.x))

        prefix = None
        state = None

        address = e.raw['address']

        if 'state' in address:
            state = address['state']

        if 'building' in address :
            prefix = address['building']
        elif 'village' in address :
            prefix = address['village']
        elif 'suburb' in address :
            prefix = address['suburb']
        elif 'town' in address :
            prefix = address['town']
        elif 'city' in address:
            prefix = address['city']

        if not prefix or not state:
            self.address = e.address
        else:
            self.address = "{}, {}".format(prefix, state)

        print("Address: {}".format(self.address))


    def save(self, *args, **kwargs):
        #TODO is one instance efficient?
        # print("saving, location {}".format(self.location))
        # print(*args)
        # print(**kwargs)
        self.get_address()
        super(Incident, self).save(*args, **kwargs)


class IncidentAdmin(admin.ModelAdmin):

    # fields = ['name', 'age', 'residence']
    #fieldset = {'address', fields = ['type', 'location', 'date', 'description', 'source', 'deaths', 'wounded']
    fields = ['type', 'location', 'date', 'description', 'source',
              'deaths', 'wounded', 'missing']
    formfield_overrides = {
        geo_models.PointField: {"widget": GooglePointFieldWidget}
    }


admin.site.register(Incident, IncidentAdmin)

class IncidentForm(forms.ModelForm):

    #TODO reposition Cameroon by default and zoom level
    #TODO at least 2 level down
    # location = geo_forms.PointField(widget=geo_forms.OSMWidget(attrs={'map_width':800,
    #                                                                   'map_height':500,
    #                                                                   ## default_zoom not working
    #                                                                   ## version too old?
    #                                                                   'default_zoom': 6,
    #                                                                   'default_lon': 13.3934,
    #                                                                   'default_lat': 9.3226,
    #                                                                   ## map_srid creates confusion
    #                                                                   ## potential bug
    #                                                                   ##'map_srid': 4326
    #                                                                   }))

    date = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )


    class Meta:
        model = Incident
        fields = ('type', 'location', 'date', 'description',
                    'source', 'deaths', 'wounded', 'missing')

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
