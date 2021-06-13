from django.db import models
from mezzanine.core.models import Displayable, RichText
from django.contrib import admin

# Create your models here.


class Transcript(Displayable, RichText):

    #title = models.CharField(max_length=50, blank=True)
    source = models.URLField(blank=True, null=True, verbose_name="primary source")
    source_2 = models.URLField(blank=True, null=True, verbose_name="2nd source")
    source_3 = models.URLField(blank=True, null=True, verbose_name="3rd source")


#class TranscriptAdmin(admin.ModelAdmin):
#    pass


#admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Transcript)