from django.db import models
from django.contrib import admin


class Chapitre(models.Model):

    number = models.PositiveIntegerField(blank=True, null=True)
    short_name = models.CharField(max_length=20)
    full_name_fr = models.CharField(max_length=100, blank=True, null=True)
    full_name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.short_name


class ChapitreAdmin(admin.ModelAdmin):

    list_display = ('number', 'short_name', 'full_name_fr', 'full_name_en')
    search_fields = ('short_name', 'full_name_fr', 'full_name_en')
    list_filter = ('short_name',)
    #filter_horizontal = ('supervisors', 'committee')
    #raw_id_fields = ('author',)


admin.site.register(Chapitre, ChapitreAdmin)


class AnnualEntry(models.Model):

    year = models.PositiveIntegerField()
    chapitre = models.ForeignKey(Chapitre)
    ae = models.BigIntegerField(blank=True, null=True)
    cp = models.BigIntegerField(blank=True, null=True)

    BF_BIP = [
        ('BF', 'Budget de Fonctionement'),
        ('BIP', "Budget d'Investissement")
    ]

    bf_bip = models.CharField(max_length=3, choices=BF_BIP)

    STATUS = [
        ('LF', 'Loi de Finance'),
        ('REV', 'Revised'),
        ('EX', 'Executed'),
    ]

    status = models.CharField(max_length=3, choices=STATUS)

    REGIONS = [
        ('EN', 'Extrême-Nord'),
        ('NO', 'Nord'),
        ('AD', 'Adamaoua'),
        ('LT', 'Littoral'),
        ('CE', 'Centre'),
        ('OU', 'Ouest'),
        ('NW', 'North-West'),
        ('SW', 'South-West'),
        ('SU', 'Sud'),
        ('ES', 'Est'),
        ('AC', 'Administration Centrale')
    ]

    region = models.CharField(max_length=3, choices=REGIONS)

    class Meta:
        unique_together = ("year", "chapitre", "status", "region", 'bf_bip')


class AnnualEntryAdmin(admin.ModelAdmin):

    list_display = ('chapitre', 'year', 'bf_bip', 'status', 'region', 'ae', 'cp')
    search_fields = ('chapitre', 'region')
    list_filter = ('chapitre', 'year')


admin.site.register(AnnualEntry, AnnualEntryAdmin)


class BudgetProgramme(models.Model):
    year = models.PositiveIntegerField()
    chapitre = models.ForeignKey(Chapitre)
    pg_id = models.CharField(max_length=20, blank=True, null=True)
    exercice_id = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=10)
    ae = models.BigIntegerField(blank=True, null=True)
    cp = models.BigIntegerField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    objective_fr = models.TextField(blank=True, null=True)
    objective_en = models.TextField(blank=True, null=True)
    indicator_fr = models.TextField(blank=True, null=True)
    indicator_en = models.TextField(blank=True, null=True)

    class Meta:

        unique_together = ("year", "chapitre", "code")


class BudgetProgrammeAdmin(admin.ModelAdmin):

    list_display = ('chapitre', 'year', 'code', 'pg_id', 'ae', 'cp')
    search_fields = ('chapitre', 'description_fr', 'objective_fr', 'indicator_fr')
    list_filter = ('chapitre', 'year', 'code')


admin.site.register(BudgetProgramme, BudgetProgrammeAdmin)

