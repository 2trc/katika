from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin
from django import forms
from django.contrib.gis.db import models as geo_models
from django.contrib.gis import forms as geo_forms

from rest_framework import serializers
from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget

from geopy.geocoders import Nominatim

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
    registration_date = models.DateField(verbose_name='registration date', auto_now=True)
    description = models.TextField()
    source = models.URLField()
    deaths = models.PositiveIntegerField(blank=True, null=True)
    wounded = models.PositiveIntegerField(blank=True, null=True)
    missing = models.PositiveIntegerField(blank=True, null=True)
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    tags_string = models.TextField(default="", blank=True)

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

        # For some reasons the many2many are not being picked up
        # Needs to have a value for field before this many-to-many relationship can be used
        #super(Incident, self).save(*args, **kwargs)

        # self.tags_string = ""
        #
        # if hasattr(self, "tags") and self.tags:
        #     print("has tags: ".format(self.tags))
        #     for tag in self.tags.all():
        #         if tag.name:
        #             self.tags_string += tag.name + ","
        #         if tag.name_fr:
        #             self.tags_string += tag.name_fr
        # else:
        #     print("doesn't have tag or empty")

        super(Incident, self).save(*args, **kwargs)


# https://stackoverflow.com/questions/23795811/django-accessing-manytomany-fields-from-post-save-signal
#https://stackoverflow.com/questions/26493254/using-djangos-m2m-changed-to-modify-what-is-being-saved-pre-add
#https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
@receiver(m2m_changed, sender=Incident.tags.through)
def save_tags_string(sender, **kwargs):

    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)

    if action == 'post_add':
        instance.tags_string = ""

        for tag in instance.tags.all():
            if tag.name:
                instance.tags_string += tag.name + ","
            if tag.name_fr:
                instance.tags_string += tag.name_fr + ","

        if instance.tags_string:
            print("tags_string worked: " + instance.tags_string)
            instance.save()
        else:
            print("no tags_string")



class IncidentAdmin(admin.ModelAdmin):

    # fields = ['name', 'age', 'residence']
    #fieldset = {'address', fields = ['type', 'location', 'date', 'description', 'source', 'deaths', 'wounded']
    exclude = ['address']
    formfield_overrides = {
        geo_models.PointField: {"widget": GooglePointFieldWidget},
        #KeywordsField: {"widget": KeywordsWidget},

    }

    list_display = ('date', 'registration_date', 'type', 'reported_by', 'deaths',
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
