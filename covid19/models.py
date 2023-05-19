from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.gis.db import models as geo_models

class CovidCategory(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CovidProducer(models.Model):

    FACE_MASK = 'FM'
    WATER_EQUIPMENT = 'WE'

    PRODUCT_CATEGORY = [
        (FACE_MASK, "Face Mask"),
        (WATER_EQUIPMENT, "Water Equipment")
    ]

    # category = models.CharField(
    #     max_length=2,
    #     choices=PRODUCT_CATEGORY,
    #     default=FACE_MASK
    # )

    type = models.ForeignKey(CovidCategory, blank=True, null=True, on_delete=models.SET_NULL)

    LITTORAL = 'LT'
    CENTER = 'CE'
    FAR_NORTH = 'FN'
    NORTH = 'NO'
    ADAMAOUA = 'AD'
    SOUTH_WEST = 'SW'
    NORTH_WEST = 'NW'
    EAST = 'ES'
    SOUTH = 'SO'
    WEST = 'WE'

    REGION_LIST = [
        (LITTORAL, 'Littoral'),
        (CENTER, 'Center'),
        (FAR_NORTH, 'Far North'),
        (NORTH, 'North'),
        (ADAMAOUA, 'Adamoua'),
        (SOUTH_WEST, 'South West'),
        (NORTH_WEST, 'North West'),
        (EAST, 'East'),
        (SOUTH, 'South'),
        (WEST, 'West')
    ]

    region = models.CharField(
        max_length=2,
        choices=REGION_LIST,
        null=True, blank=True
    )

    price = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)


class CovidProducerForm(forms.ModelForm):

    class Meta:
        model = CovidProducer
        fields = ['type', 'region', 'price', 'phone', 'contact_person', 'description', 'description', 'website', 'address']


class CovidInitiative(models.Model):

    initiator = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    date = models.DateField(blank=True)
    description = models.TextField(blank=True)
    location_text = models.CharField(max_length=255, blank=True, null=True)


class CovidInitiativeForm(forms.ModelForm):

    class Meta:
        model = CovidInitiative
        fields = ['initiator', 'website', 'date', 'location_text', 'description']


class CovidProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'type', 'contact_person', 'price', 'phone')
    search_fields = ('contact', 'phone', 'description', 'address')
    list_filter = ('type', )
    #filter_horizontal = ('supervisors', 'committee')
    #raw_id_fields = ('author',)


class CovidCatalogAdmin(admin.ModelAdmin):

    fields = ['name',]

    list_display = ('id', 'name')


class CovidInitiativeAdmin(admin.ModelAdmin):

    #fields = ['name',]

    list_display = ('id', 'initiator', 'date')


class CovidFund(models.Model):

    name = models.CharField(max_length=255)
    initiator = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    target = models.PositiveIntegerField(blank=True, null=True)


class CovidFundForm(forms.ModelForm):

    class Meta:
        model = CovidFund
        fields = ['name', 'initiator', 'contact', 'website', 'start_date', 'end_date', 'description', 'target']


class CovidFundAdmin(admin.ModelAdmin):

    list_display = ('id', 'initiator', 'start_date')


admin.site.register(CovidProducer, CovidProductAdmin)
admin.site.register(CovidCategory, CovidCatalogAdmin)
admin.site.register(CovidInitiative, CovidInitiativeAdmin)
admin.site.register(CovidFund, CovidFundAdmin)




