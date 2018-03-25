from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin
from django import forms
from django.contrib.gis.db import models as geo_models
from django.contrib.gis import forms as geo_forms

from rest_framework import serializers
from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget

from geopy.geocoders import Nominatim
import datetime

#from mezzanine.generic.fields import KeywordsField
#from mezzanine.generic.forms import KeywordsWidget, Keyword


from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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


class Tag(models.Model):
    name = models.CharField(max_length=30, null=True)
    name_fr = models.CharField(max_length=30, null=True)

    def __str__(self):

        display_name = ""

        if self.name:
            display_name = self.name

            if self.name_fr:
                display_name += ","

        if self.name_fr:
            display_name += self.name_fr

        return display_name

    class Meta:
        unique_together = ('name', 'name_fr')


admin.site.register(Tag)

class Incident(models.Model):
    type = models.ForeignKey(IncidentType, null=True, on_delete=models.SET_NULL)
    location = geo_models.PointField()
    address = models.TextField(null=True)
    date = models.DateField('date')
    last_modified = models.DateField(verbose_name='last modified', auto_now=True)
    registration_date = models.DateField(verbose_name='registration date')
    description = models.TextField()
    source = models.URLField()
    deaths = models.PositiveIntegerField(blank=True, null=True)
    wounded = models.PositiveIntegerField(blank=True, null=True)
    missing = models.PositiveIntegerField(blank=True, null=True)
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    tag_ids = models.TextField(default="", blank=True)

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

        # print("Address: {}".format(self.address))


    def save(self, *args, **kwargs):
        #TODO is one instance efficient?
        # print("saving, location {}".format(self.location))
        # print(*args)
        # print(**kwargs)
        try:
            self.get_address()
        except:
            pass

        #avoid saving before many2many relationship already created
        try:
            self.get_tag_ids()
        except:
            pass

        if not self.registration_date:
            self.registration_date = datetime.datetime.now()

        super(Incident, self).save(*args, **kwargs)

    def get_tag_ids(self):

        self.tag_ids = ""

        if self.tags:

            ids = []

            for tag in self.tags.all():
                ids.append(str(tag.pk))

            self.tag_ids = ",".join(ids)

# https://stackoverflow.com/questions/23795811/django-accessing-manytomany-fields-from-post-save-signal
#https://stackoverflow.com/questions/26493254/using-djangos-m2m-changed-to-modify-what-is-being-saved-pre-add
#https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
@receiver(m2m_changed, sender=Incident.tags.through)
def save_tag_ids(sender, **kwargs):

    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)

    if action == 'post_add':
        instance.get_tag_ids()

        if instance.tag_ids:
            #print("tags_string worked: " + instance.tag_ids)
            instance.save()
        # else:
        #     print("no tags_string")



class IncidentAdmin(admin.ModelAdmin):

    # fields = ['name', 'age', 'residence']
    #fieldset = {'address', fields = ['type', 'location', 'date', 'description', 'source', 'deaths', 'wounded']
    exclude = ['address']
    formfield_overrides = {
        geo_models.PointField: {"widget": GooglePointFieldWidget},
        #KeywordsField: {"widget": KeywordsWidget},

    }

    list_display = ('date', 'last_modified', 'registration_date','type', 'reported_by', 'deaths',
                    'wounded', 'missing', 'address')
    search_fields = ('description',)
    list_filter = ('type', 'date')
    #filter_horizontal = ('supervisors', 'committee')
    #raw_id_fields = ('author',)


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
                  'tags',
                    'source', 'deaths', 'wounded', 'missing')

        widgets = {'location': GooglePointFieldWidget}


class IncidentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncidentType
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IncidentSerializer(serializers.ModelSerializer):

    type = IncidentTypeSerializer()
    #tags = serializers.StringRelatedField(many=True)
    tags = TagSerializer(many=True)

    class Meta:

        model = Incident
        fields = '__all__'
