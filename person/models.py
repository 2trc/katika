from django.db import models
from mezzanine.core.fields import FileField
from mezzanine.utils.models import upload_to
from django.utils.translation import ugettext_lazy as _


# Create your models here.

SEX = ((0, 'M'), (1, 'F'))


class Person(models.Model):
    first_name = models.CharField(blank=True, null=True, max_length=255)
    last_name = models.CharField(max_length=255)
    alias = models.CharField(blank=True, null=True, max_length=255)
    birthday = models.DateField(blank=True, null=True)
    sex = models.PositiveSmallIntegerField(blank=True, null=True, choices=SEX)
    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to=upload_to("person.featured_image", "person"),
                               format="Image", max_length=255, null=True, blank=True)

    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name.upper())

    def __str__(self):
        # if self.alias:
        #     return self.alias
        # else:
        return self.get_full_name()

    class Meta:
        abstract = True

