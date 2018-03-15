from django import forms
from django.db import models
from django.contrib import admin
from rest_framework import serializers
from person.models import Person
from mezzanine.core.fields import RichTextField
from mezzanine.utils.models import upload_to
from mezzanine.core.fields import FileField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from mezzanine.generic.fields import KeywordsField

from mezzanine.utils.urls import unique_slug
from django.utils.text import slugify

from kthesis.models import unique_slug_max_length

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit

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
    importance = models.IntegerField(choices=((1, _("LOW")),
                                              (2, _("MEDIUM")),
                                              (3, _("HIGH"))),
                                     default=1)
    accuracy = models.IntegerField(choices=((1, _("DAY")),
                                            (2, _("MONTH")),
                                            (3, _("YEAR"))),
                                   default=1)

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

    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    tags = KeywordsField()



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


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'History event',
                Div('date', 'importance'),
                'title',
                'content',
                Div('image_url', 'image_credits', 'image_caption'),
                'source'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        super(EventForm, self).__init__(*args, **kwargs)

    date = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = Event
        exclude = ('personnage', 'featured_image', 'tags', 'reported_by', 'slug')


# class EventAdmin(admin.ModelAdmin):
#     class Meta:
#         form = EventForm

#admin.site.register(Event, EventAdmin)
admin.site.register(Event)

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