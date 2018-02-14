from django import forms
from django.db import models
from django.contrib import admin
from rest_framework import serializers
from person.models import Person
from mezzanine.core.fields import RichTextField
from mezzanine.utils.models import upload_to
from mezzanine.core.fields import FileField
from django.utils.translation import ugettext_lazy as _

from mezzanine.utils.urls import unique_slug
from django.utils.text import slugify

from kthesis.models import unique_slug_max_length

import uuid


# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
# To study python manage.py migrate --fake core zero

class Personnage(Person):

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = False

class PersonnageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnage
        fields = '__all__'


admin.site.register(Personnage)

class Event(models.Model):

    date = models.DateField('date')
    title = models.TextField()
    content = RichTextField(blank=True, null=True)
    personnages = models.ManyToManyField(Personnage, blank=True, related_name='personnages')

    duration = models.DurationField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    image_credits = models.CharField(max_length=255, blank=True, null=True)
    image_caption = models.CharField(max_length=255, blank=True, null=True)
    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to=upload_to("event.featured_image", "event"),
                               format="Image", max_length=255, null=True, blank=True)
    source = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    # Keywords?

    def save(self, *args, **kwargs):

        if not self.slug:
            slug = self.title

            slug = slugify(slug)
            self.slug = unique_slug_max_length(Event.objects.all(), 'slug', slug, 255)

        super(Event, self).save(*args, **kwargs)
    # Keywords?

    def __str__(self):
        return "{}, {}".format(self.date, self.title)

    class Meta:
        verbose_name_plural = 'History events'  # ?
        ordering = ['-date']


class EventSerializer(serializers.ModelSerializer):

    personnages = PersonnageSerializer(many=True, read_only=True)

    # def to_representation(self, instance):
    #     """Convert `username` to lowercase."""
    #     ret = super().to_representation(instance)
    #
    #     if ret['featured_image']:
    #         print("featured_image: {}".format(ret))
    #         ret['image_url'] = ret['featured_image']
    #     return ret

    class Meta:
        model = Event
        fields = '__all__'


admin.site.register(Event)

class EventForm(forms.ModelForm):

    date = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = Event
        #fields = '__all__'
        exclude = ('personnage', 'featured_image',)


class PersonnageForm(forms.ModelForm):

    birthday = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    # formfield_overrides = {
    #     'featured_image': {'widget': forms.ClearableFileInput},
    # }
    # featured_image = forms.ImageField(
    #     required=False,
    #     widget=forms.ClearableFileInput(
    #         attrs={
    #             'accept': ','.join(settings.ALLOWED_IMAGE_TYPES),
    #             'clear_checkbox_label': 'Remove custom cover'}
    #     ),
    # )
    # featured_image = forms.ImageField(required=False,
    #                                   error_messages={'invalid': _("Image files only")},
    #                  widget=forms.FileInput)

    class Meta:
        model = Personnage
        exclude = ('featured_image',)