from django.db import models
from katika.models import NullsLastQuerySet
from django.contrib import admin
from person.models import Person, SEX
from django.contrib.gis.db import models as geo_models
from katika.models import AbstractTag
from mapwidgets.widgets import GooglePointFieldWidget
import copy
from rest_framework import serializers

# TODO auto-complete for prison, people?
# https://django-autocomplete-light.readthedocs.io/en/master/

class IncarcerationTag(AbstractTag):
    pass


class Prison(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    location = geo_models.PointField()

    def __str__(self):
        return self.short_name if self.short_name else self.name


# Magistrate or juge?
class Judge(Person):
    pass


admin.site.register(Judge)


class Incarceration(Person):
    #Todo change sources to comment
    #Todo add source, source_2, source_3
    #Todo extract&remove image, source/_2/_3 from comment
    arrest_date = models.DateField(null=True, blank=True)
    incarceration_date = models.DateField(null=True, blank=True)
    conviction_date = models.DateField(null=True, blank=True)
    conviction_duration_years = models.PositiveSmallIntegerField(null=True, blank=True)
    conviction_duration_months = models.PositiveSmallIntegerField(null=True, blank=True)
    conviction_duration_days = models.PositiveSmallIntegerField(null=True, blank=True)
    estimated_release_date = models.DateField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    prison = models.ForeignKey(Prison, null=True, blank=True, on_delete=models.SET_NULL)
    sources = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(IncarcerationTag, blank=True)
    deceased = models.BooleanField(null=True, blank=True)
    dates_inaccurate = models.BooleanField(null=True, blank=True)

    #related juges/magistrates
    judges = models.ManyToManyField(Judge, null=True, blank=True)

    #https://stackoverflow.com/questions/15121093/django-adding-nulls-last-to-query
    objects = NullsLastQuerySet.as_manager()
    
    def more_info(self):

        m_info = "Birthday: {}, ".format(self.birthday) if self.birthday else ""
        
        if self.sex is not None:           
            if SEX[self.sex][1] == 'M':
                m_info += "Male, "
            else:
                m_info += "Female"

        if self.sources:
            m_info += "\nSources: {}".format(self.sources)


        return m_info

    def to_dict(self):
        out = copy.copy( self.__dict__)
        for x in ['id','prison_id', '_state', '_prison_cache']:
            if x in out:
                out.pop(x)

        if self.prison:
            out['prison'] = str(self.prison)

        if self.tags:
            out['tags'] = ",".join([tag.name for tag in self.tags.all()])

        if self.sex:
            out['sex'] = 'F'
        else:
            out['sex'] = 'M'

        return out

    #class Meta:
    #    managed = True


class IncarcerationAdmin(admin.ModelAdmin):

    list_display = ('last_name', 'first_name', 'prison', 'birthday', 'arrest_date', 'incarceration_date', 'conviction_date', 'release_date')
    search_fields = ('first_name', 'last_name', 'name_mispelling', 'alias', 'sources')
    #list_filter = ('type', 'date')


admin.site.register(Incarceration, IncarcerationAdmin)


class IncarcerationTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncarcerationTag
        fields = ('name', 'name_fr')


class PrisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prison
        fields = ("name", "short_name")


class IncarcerationSerializer(serializers.ModelSerializer):

    tags = IncarcerationTagSerializer(many=True)
    prison = PrisonSerializer()

    class Meta:

        model = Incarceration
        fields = ("first_name", "last_name", "alias", "birthday", "arrest_date", "incarceration_date",
                  "prison", "tags", "conviction_date", "conviction_duration_years", "conviction_duration_months",
                  "conviction_duration_days", "release_date", "deceased", "sources",)


class PrisonAdmin(admin.ModelAdmin):

    fiels = ["name", "short_name", "location"]

    formfield_overrides = {
        geo_models.PointField: {"widget": GooglePointFieldWidget},
        # KeywordsField: {"widget": KeywordsWidget},

    }


admin.site.register(IncarcerationTag)
admin.site.register(Prison, PrisonAdmin)



