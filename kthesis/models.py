from django.db import models
from django.contrib import admin
from rest_framework import serializers
from django import forms
from person.models import Person
from mezzanine.core.fields import FileField
from mezzanine.utils.models import upload_to
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from mezzanine.utils.urls import unique_slug

from django.utils.text import slugify

#customizing admin list forms
#https://djangobook.com/customizing-change-lists-forms/
################################################################
#
#   fields are by default in English, if French is also available
#   then _fr carries the French version
#
################################################################

class Scholar(Person):

    slug = models.SlugField(blank=True, null=True)
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

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
        exclude = ('id',)


class ScholarAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'sex')
    search_fields = ('last_name', 'first_name')


admin.site.register(Scholar, ScholarAdmin)


class Degree(models.Model):
    name = models.CharField(max_length=50, blank=True)
    name_fr = models.CharField(max_length=50, blank=True)
    abbreviation = models.CharField(null=True, blank=True, max_length=10)
    abbreviation_fr = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):

        if self.abbreviation:
            return self.abbreviation

        if self.abbreviation_fr:
            return self.abbreviation_fr

        if self.name:
            return self.name

        if self.name_fr:
            return self.name_fr


class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'


admin.site.register(Degree)


class University(models.Model):
    name = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255, blank=True)
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


class KeywordEn(models.Model):

    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Keywords (English)'
        ordering = ['name']


class KeywordFr(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Keywords (French)'
        ordering = ['name']


admin.site.register(KeywordEn)
admin.site.register(KeywordFr)


class Thesis(models.Model):
    title = models.TextField(blank=True, null=True)
    title_fr = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    abstract_fr = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Scholar, blank=True, null=True, on_delete=models.SET_NULL)
    degree = models.ForeignKey(Degree, blank=True, null=True, on_delete=models.SET_NULL)
    supervisors = models.ManyToManyField(Scholar, blank=True, related_name='supervisors')
    committee = models.ManyToManyField(Scholar, blank=True, related_name='committee')
    link = models.URLField(blank=True, null=True)
    university = models.ForeignKey(University, blank=True, null=True, on_delete=models.SET_NULL)
    faculty = models.CharField(blank=True, null=True, max_length=255)
    department = models.CharField(blank=True, null=True, max_length=255)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    keywords = models.ManyToManyField(KeywordEn, blank=True)
    keywords_fr = models.ManyToManyField(KeywordFr, blank=True)

    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):

        print("Slug: {}".format(self.slug))

        if not self.slug:
            print("Generating slug field")
            slug = slugify(self.title + self.title_fr + str(self.author))
            self.slug = unique_slug_max_length(Thesis.objects.all(), 'slug', slug, 50)

        super(Thesis, self).save(*args, **kwargs)

    def __str__(self):

        output_list = []

        if self.author:
            output_list.append(self.author.last_name)

        if self.title:
            output_list.append(self.title)
        elif self.title_fr:
            output_list.append(self.title_fr)

        if self.year:
            output_list.append(str(self.year))

        if len(output_list) == 0:
            output_list.append(str(self.pk))

        return ",".join(output_list)

    class Meta:
        verbose_name_plural = 'Theses'  # ?
        ordering = ['-year']


class ScholarForm(forms.ModelForm):

    class Meta:
        model = Scholar
        exclude = ('featured_image', 'slug', 'reported_by', )


class ThesisForm(forms.ModelForm):

    class Meta:
        model = Thesis
        exclude = ('slug', 'reported_by', )
        labels = {
            'title' : 'Title (in English)',
            'title_fr': 'Titre (en Français)',
            'year': 'Year (Année de soutenance)',
            'abstract_fr': 'Résumé',
            'keywords_fr': 'Mots clés',
        }
        widgets = {
            'title': forms.Textarea(attrs={'rows':1}),
            'title_fr': forms.Textarea(attrs={'rows': 1}),
        }


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


class ThesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'year', 'university')
    search_fields = ('title', 'author')
    list_filter = ('university', 'year')
    filter_horizontal = ('supervisors', 'committee')
    raw_id_fields = ('author',)


admin.site.register(Thesis, ThesisAdmin)
#tagulous.admin.register(Thesis)
