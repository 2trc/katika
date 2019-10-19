from django.db import models
from django.contrib import admin
from person.models import Person, SEX

# Create your models here.

class Incarceration(Person):
    #prison = 
    arrest_date = models.DateField(null=True, blank=True)
    #arrest_place =,
    incarceration_date = models.DateField(null=True, blank=True)
    conviction_date = models.DateField(null=True, blank=True)
    conviction_duration = models.DurationField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    sources = models.TextField(null=True, blank=True)
    
    def more_info(self):

        m_info = "Birthday: {}, ".format(self.birthday) if self.birthday else ""
        
        if self.sex:
            m_info += "Sex: {}".format(SEX[self.sex])

        if self.sources:
            m_info += "\nSources: {}".format(self.sources)


        return m_info

    #class Meta:
    #    managed = True

admin.site.register(Incarceration)