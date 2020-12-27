from django.db import models
from django.contrib.auth.models import User, Permission

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

    # security forces
    deaths_security_forces = models.PositiveIntegerField(blank=True, null=True)
    wounded_security_forces = models.PositiveIntegerField(blank=True, null=True)
    missing_security_forces = models.PositiveIntegerField(blank=True, null=True)

    # perpetrators
    deaths_perpetrator = models.PositiveIntegerField(blank=True, null=True)
    wounded_perpetrator = models.PositiveIntegerField(blank=True, null=True)
    missing_perpetrator = models.PositiveIntegerField(blank=True, null=True)

    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    tag_ids = models.TextField(default="", blank=True)

    location_inaccurate = models.NullBooleanField(null=True, blank=True)

    #sources = models.

    def __str__(self):
        return "{}: {}, {}".format(self.type, self.date, self.address)

    class Meta:
        verbose_name_plural = 'Incidents' #?
        ordering = ['-date']

    def get_address(self):

        geolocator = Nominatim()
        # set Nomatim timeout to 10sec as it might happen that the service is slow
        # default is 1s and that speed is not needed for our service
        geolocator.timeout = 10
        try:
            loc = geolocator.reverse((self.location.y, self.location.x))
        except Exception as e:
            print("reverse didn't work: {}".format(e))
            return

        try:
            address = loc.raw['address']
        except Exception as e:
            print("Getting address failed: {}", e)
            return

        display_list = []

        if 'building' in address:
            display_list.append(address['building'])
        elif 'residential' in address:
            display_list.append(address['residential'])
        elif 'village' in address:
            display_list.append(address['village'])
        elif 'suburb' in address:
            display_list.append(address['suburb'])
        elif 'town' in address:
            display_list.append(address['town'])
        elif 'city' in address:
            display_list.append(address['city'])

        if 'county' in address:
            display_list.append(address['county'])

        if 'state' in address:
            display_list.append(address['state'])

        if len(display_list) == 0:
            self.address = loc.address
        else:
            self.address = ", ".join(display_list)

    def save(self, *args, **kwargs):
        #TODO is one instance efficient?
        # print("saving, location {}".format(self.location))
        # print(*args)
        # print(**kwargs)
        #Avoid reverse querying if address already exists
        # if not self.address:
        #     try:
        #         #https://github.com/geopy/geopy/issues/262
        #         #fixed with geopy v-1.12.0
        #         self.get_address()
        #     except Exception as e:
        #         print(e)
        #         #pass

        self.get_address()

        # try:
        #     self.get_tag_ids()
        # except:
        #     pass

        print("tag_ids when saving: {}".format(self.tag_ids))

        if not self.registration_date:
            self.registration_date = datetime.datetime.now()

        super(Incident, self).save(*args, **kwargs)

    def get_tag_ids(self, params=None):

        self.tag_ids = ""

        ids = []

        tags = params if params else self.tags.all() if self.tags else []

        for tag in tags:
            ids.append(str(tag.pk))

        self.tag_ids = ",".join(ids)

        print("inside get_tag_ids: {}".format(self.tag_ids))


def find_miss_matching_tags():
    '''
    Return a list of incidents where the tags m2m doesn't match
    with the tag_ids list. For cleaning up bug where tag_ids
    weren't getting updated when incident was edited
    '''

    incidents = []

    for incident in Incident.objects.all().iterator():

        if not incident.tags:
            continue

        first_set = set()
        for tag in incident.tags.all():
            first_set.add(str(tag.id))

        if incident.tag_ids:
            second_set = set(incident.tag_ids.split(','))
        else:
            second_set = set()

        if first_set != second_set:
            print("there is a difference")
            print('1st set: {}'.format(first_set))
            print('2nd set: {}'.format(second_set))
            incidents.append(incident)

    return incidents


# https://stackoverflow.com/questions/23795811/django-accessing-manytomany-fields-from-post-save-signal
#https://stackoverflow.com/questions/26493254/using-djangos-m2m-changed-to-modify-what-is-being-saved-pre-add
#https://docs.djangoproject.com/en/dev/ref/signals/#m2m-changed
@receiver(m2m_changed, sender=Incident.tags.through)
def save_tag_ids(sender, **kwargs):


    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)

    #print("inside m2m save_tag_ids, with action:".format(action))

    if action == 'post_add':
        instance.get_tag_ids()

        if instance.tag_ids:
            print("tags_string worked: " + instance.tag_ids)
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
                    'source', 'deaths', 'wounded', 'missing',
                    'deaths_security_forces','wounded_security_forces','missing_security_forces',
                    'deaths_perpetrator','wounded_perpetrator','missing_perpetrator', 'location_inaccurate')

        widgets = {
            'location': GooglePointFieldWidget,
            'description': forms.Textarea(attrs={'rows': 8}),
            'tags': forms.SelectMultiple(attrs={'size': 8})
        }


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

"""
from django.db.models import Sum, Count
from incident.models import Incident
from django.db.models.functions import ExtractMonth, Extractyear

c = Incident.objects.annotate(month=ExtractMonth('date')).annotate(year=ExtractMonth('date')).values('month').annotate(count=Sum('deaths')).
   ...: annotate(year=ExtractYear('date')).values('year', 'month','count')

"""