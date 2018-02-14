from django.db import models
from django.contrib import admin
from rest_framework import serializers
from person.models import Person
from mezzanine.core.fields import FileField
from mezzanine.utils.models import upload_to
from django.utils.translation import ugettext_lazy as _

from mezzanine.utils.urls import unique_slug
from django.utils.text import slugify


class Scholar(Person):

    slug = models.SlugField(blank=True, null=True)

    # Keywords?

    def save(self, *args, **kwargs):

        if not self.slug:
            slug = ""
            if self.last_name:
                slug += self.last_name + " "
            if self.first_name:
                slug += self.first_name

            slug = slugify(slug)
            self.slug = unique_slug(Scholar.objects.all(), 'slug', slug)

        super(Scholar, self).save(*args, **kwargs)

    class Meta:
        abstract = False


class ScholarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholar
        #fields = '__all__'
        exclude = ('id',)


admin.site.register(Scholar)


class Degree(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(null=True, max_length=10)

    def __str__(self):
        return "{}".format(self.abbreviation)


class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'


admin.site.register(Degree)


class University(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(null=True, max_length=30)
    country = models.CharField(null=True, default="Cameroon", max_length=30)
    address = models.CharField(blank=True, null=True, max_length=30)

    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to=upload_to("kthesis.featured_image", "kthesis"),
                               format="Image", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Universities'


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'


admin.site.register(University)


class Thesis(models.Model):
    title = models.TextField()
    abstract = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Scholar, blank=True, null=True, on_delete=models.SET_NULL)
    degree = models.ForeignKey(Degree, blank=True, null=True, on_delete=models.SET_NULL)
    supervisors = models.ManyToManyField(Scholar, blank=True, related_name='supervisors')
    committee = models.ManyToManyField(Scholar, blank=True, related_name='committee')
    link = models.URLField(blank=True, null=True)
    university = models.ForeignKey(University, blank=True, null=True, on_delete=models.SET_NULL)
    faculty = models.CharField(blank=True, null=True, max_length=255)
    department = models.CharField(blank=True, null=True, max_length=255)
    date = models.PositiveSmallIntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    # Keywords?

    def save(self, *args, **kwargs):

        print("Slug: {}".format(self.slug))

        if not self.slug:
            print("Generating slug field")
            slug = slugify(self.title)
            self.slug = unique_slug_max_length(Thesis.objects.all(), 'slug', slug, 50)

        super(Thesis, self).save(*args, **kwargs)

    def __str__(self):
        if self.author:
            return "{}, {}, {}".format(self.author.last_name, self.title, self.date)
        else:
            return "{}, {}".format(self.title, self.date)

    class Meta:
        verbose_name_plural = 'Theses'  # ?
        ordering = ['-date']


def unique_slug_max_length(queryset, slug_field, slug, max_length):
    """
    Ensures a slug is unique for the given queryset, appending
    an integer to its end until the slug is unique.
    restrict max length recursively
    !!! risky !!!
    """
    result_slug = unique_slug(queryset, slug_field, slug)

    if not max_length or max_length <= 0 or len(result_slug) <= max_length:
        return result_slug

    result_slug = result_slug[:max_length]

    while True:
        result_slug = unique_slug(queryset, slug_field, result_slug)

        if len(result_slug) <= max_length:
            break

        delta = len(result_slug) % max_length
        print(result_slug)
        result_slug = result_slug[:-2*delta]

        print(result_slug)

    return result_slug


class ThesisSerializer(serializers.ModelSerializer):
    author = ScholarSerializer(read_only=True)
    degree = DegreeSerializer(read_only=True)
    supervisors = ScholarSerializer(many=True, read_only=True)
    committee = ScholarSerializer(many=True, read_only=True)
    university = UniversitySerializer(read_only=True)

    # tracks = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='track-detail'
    # )

    class Meta:
        model = Thesis
        #fields = '__all__'
        exclude = ('id',)


admin.site.register(Thesis)
