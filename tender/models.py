from django.db import models
from django.contrib import admin
import logging
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from rest_framework import serializers


logger = logging.getLogger(__name__)

# TODO auto-complete for owner?
# https://django-autocomplete-light.readthedocs.io/en/master/

class TenderOwner(models.Model):
    short_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    #owner_id = models.IntegerField(blank=True, unique=True)
    #ARMP keeps changing short_name so in order not to miss entries, they can be collected first
    #then re-assigned later
    owner_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["owner_id"]

    def __str__(self):
        return "{}, {}".format(self.owner_id, self.short_name)


class TenderOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderOwner
        exclude = ('id',)


class ArmpEntry(models.Model):

    owner = models.ForeignKey(TenderOwner, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.TextField(null=True, blank=True)
    link = models.URLField(verbose_name="primary source")
    publication_type = models.CharField(max_length=20, blank=True, null=True)
    verbose_type = models.CharField(max_length=50, blank=True, null=True)
    publication_datetime = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    expiration_time = models.TimeField(blank=True, null=True)
    dao_link = models.URLField(verbose_name="DAO link", blank=True)
    original_link = models.URLField(verbose_name="Original Document link", blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    content = models.TextField(null=True, blank=True)
    extra_content = models.TextField(null=True, blank=True)
    projected_cost = models.BigIntegerField(null=True, blank=True)
    final_cost = models.BigIntegerField(null=True, blank=True)

    cost = models.BigIntegerField(null=True, blank=True)

    region = models.CharField(max_length=50, blank=True, null=True)
    ao_id = models.CharField(max_length=50, blank=True, null=True)
    own_id = models.CharField(max_length=50, blank=True, null=True)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        # TODO this works????
        # x=ArmpEntry()
        # x.save()
        # x=ArmpEntry()
        # x.save()

        unique_together = ("owner", "link", "publication_type", "verbose_type")
        indexes = [

            GinIndex(fields=['search_vector']),

        ]
        #ordering = ["-publication_datetime"]

    def __str__(self):
        return "{}, {}".format(self.owner, self.title)

    def save(self, *args, **kwargs):

        if not self.cost:
            if self.final_cost:
                self.cost = self.final_cost
            else:
                self.cost = self.projected_cost

        super(ArmpEntry, self).save(*args, **kwargs)

        #https://blog.lotech.org/postgres-full-text-search-with-django.html
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            self.search_vector = SearchVector('title', 'content', config='french_unaccent')
            self.save(update_fields=['search_vector'])


class TenderOwnerAdmin(admin.ModelAdmin):

    list_display = ('owner_id', 'short_name', 'full_name')
    search_fields = ('owner_id', 'short_name', 'full_name')


admin.site.register(TenderOwner, TenderOwnerAdmin)


class ArmpEntryAdmin(admin.ModelAdmin):

    list_display = ('owner', 'publication_datetime', 'cost', 'publication_type', 'title', 'link')
    search_fields = ('title', 'content')
    #search_fields = ('search_vector',)
    list_filter = ('owner', 'publication_datetime', 'publication_type')
    #filter_horizontal = ('supervisors', 'committee')
    #raw_id_fields = ('author',)


admin.site.register(ArmpEntry, ArmpEntryAdmin)


class TenderSerializer(serializers.ModelSerializer):

    #type = IncidentTypeSerializer()
    #tags = serializers.StringRelatedField(many=True)
    #tags = TagSerializer(many=True)
    #content = serializers.CharField(max_length=1000) couldn't figure out Textfield->Charfield
    owner = TenderOwnerSerializer()

    class Meta:

        model = ArmpEntry
        fields = ('title', 'link', 'publication_type', 'publication_datetime',
                  'expiration_date', 'expiration_time', 'dao_link', 'region',
                  'cost', 'owner',)






# class AddressBP(models.Model):
#     bp = models.PositiveIntegerField(verbose_name='Boite Postale')
#     ville = models.CharField(max_length=50)
#
#     class Meta:
#         unique_together = ("bp", "ville")


# admin.site.register(AddressBP)


class CDI_CRI(models.Model):
    # CRI, CENTRE REGIONAL DES IMPOTS
    cri = models.CharField(max_length=50, verbose_name='Centre Régional des Impôts')
    # CDI, CENTRE DES IMPOTS DE RATTACHEMENT, CENTRE DE RATTACHEMENT, CENTRE_DE_RATTACHEMENT
    cdi = models.CharField(max_length=50, verbose_name='Centre des Impôts de Rattachement')

    matches = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.cri}-{self.cdi}"

    class Meta:
        unique_together = ("cdi", "cri")
        verbose_name_plural = "CDIs"


class CDI_CRIAdmin(admin.ModelAdmin):
    list_display = ("cdi", "cri", "matches")
    list_filter = ("cri",)
    search_fields = ("matches",)


admin.site.register(CDI_CRI, CDI_CRIAdmin)


class CDI_CRI_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CDI_CRI
        exclude = ('id','matches')


class Exercice(models.Model):

    # contribuable = models.ForeignKey(Contribuable)
    # EXERCICE
    year = models.PositiveIntegerField()
    # MOIS
    JAN = 1
    FEV = 2
    MAR = 3
    AVR = 4
    MAI = 5
    JUN = 6
    JUL = 7
    AOU = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12

    MOIS = (
        (JAN, 'JANVIER'),
        (FEV, 'FEVRIER'),
        (MAR, 'MARS'),
        (AVR, 'AVRIL'),
        (MAI, 'MAI'),
        (JUN, 'JUIN'),
        (JUL, 'JUILLET'),
        (AOU, 'AOUT'),
        (SEP, 'SEPTEMBRE'),
        (OCT, 'OCTOBRE'),
        (NOV, 'NOVEMBRE'),
        (DEC, 'DECEMBRE'),
    )

    month = models.IntegerField(choices=MOIS)

    #https://fiscalis.dgi.cm/UploadedFiles/AttachedFiles/ArchiveListecontribuable/FICHIER%20SEPTEMBRE%202015.xlsx
    url = models.URLField(blank=True)

    @staticmethod
    def build_contribuable_url(m,y):
        month = Exercice.MOIS[m-1][1]
        return f"https://fiscalis.dgi.cm/UploadedFiles/AttachedFiles/ArchiveListecontribuable/FICHIER%20{month}%20{y}.xlsx"

    def save(self, *args, **kwargs):
        # print(*args)
        # print(**kwargs)

        self.url = Exercice.build_contribuable_url(self.month, self.year)
        super(Exercice, self).save(*args, **kwargs)
        #self.save()

    def __str__(self):
        return f"{self.year}/{self.month}"

    class Meta:

        unique_together = ("year", "month")

        ordering = ["-year", "-month"]


class ExerciceAdmin(admin.ModelAdmin):

    list_display = ('year', 'month')
    search_fields = ('year', 'month')
    list_filter = ('year', 'month')


admin.site.register(Exercice, ExerciceAdmin)


class EntrepriseChange(models.Model):

    exercice = models.ForeignKey(Exercice, null=True, blank=True, on_delete=models.SET_NULL)
    niu = models.CharField(max_length=255)
    log = models.CharField(max_length=255)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        unique_together = ('log', 'exercice', 'niu')
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

        ordering = ["-exercice__year", "-exercice__month"]

    def __str__(self):
        return f"{self.niu} - {self.exercice.year}/{self.exercice.month}: {self.log}"

    def save(self, *args, **kwargs):
        # print(*args)
        # print(**kwargs)
        super(EntrepriseChange, self).save(*args, **kwargs)
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            # instance = self._meta.default_manager.with_documents().get(pk=self.pk)

            self.search_vector = SearchVector('niu', 'log', config='french_unaccent')
            # if self.pk % 1000 == 0:
            #    print(f"{self.pk}, {self.search_vector}")
            # print(f"{self.pk}, {self.search_vector}")
            self.save(update_fields=['search_vector'])


admin.site.register(EntrepriseChange)


class Entreprise(models.Model):
    # NIU
    niu = models.CharField(max_length=50, unique=True)

    # RAISON SOCIALE, RAISON_SOCIALE, NOM ET PRENOM OU RAISON SOCIALE, latest
    raison_sociale = models.CharField(max_length=255, null=True, blank=True)

    # SIGLE, SIGLE OU ENSEIGNE COMMERCIALE, latest
    sigle = models.CharField(max_length=255, null=True, blank=True)

    # ACTIVITE PRINCIPALE, ACTIVITE_PRINCIPALE, latest
    activite_principale = models.CharField(max_length=255, null=True, blank=True, verbose_name='Activité Principale')
    # comma separated
    #activite_principale_cs = models.CharField(max_length=255, null=True, blank=True, verbose_name='Activité Principale')

    # BOITE POSTALE, BOITE_POSTALE, showing latest
    bp = models.PositiveIntegerField(null=True, blank=True, verbose_name='Boite Postale')
    #address = models.ForeignKey(AddressBP, blank=True)

    # TELEPHONE, comma separated
    telephone = models.CharField(max_length=255, null=True, blank=True)

    # CRI, CENTRE REGIONAL DES IMPOTS
    #cri = models.CharField(max_length=50, null=True, blank=True, verbose_name='Centre Régional des Impôts')
    # CDI, CENTRE DES IMPOTS DE RATTACHEMENT, CENTRE DE RATTACHEMENT, CENTRE_DE_RATTACHEMENT
    #cdi = models.CharField(max_length=50, null=True, blank=True, verbose_name='Centre des Impôts de Rattachement')
    cdi_cri = models.ForeignKey(CDI_CRI, blank=True, null=True, on_delete=models.SET_NULL)

    # ETAT NIU, ETATNIU
    etat_niu = models.CharField(max_length=20, null=True, blank=True)
    # FORME JURIDIQUE, FORME_JURIDIQUE
    forme_juridique = models.CharField(max_length=50, null=True, blank=True)

    # LIEU - DIT, LIEUX - DIT, LIEUX_DIT
    lieu_dit = models.CharField(max_length=50, null=True, blank=True)
    # N, N°, a ignoré

    # REGIME, REGIME D 'IMPOSITION
    LIBERATOIRE = "IL"
    REEL = "REEL"
    HRI = "HRI"
    RSI = "RSI"
    SAL = "SAL"

    REGIME_FISCAL = (
        (LIBERATOIRE, "IMPOT LIBERATOIRE"),
        (REEL, "REGIME REEL"),
        (RSI, "REGIME SIMPLIFIE"),
        (HRI, "HORS REGIME D'IMPOSITION"),
        (SAL, "SALARIE")
    )

    regime = models.CharField(max_length=4, choices=REGIME_FISCAL, null=True, blank=True)

    # sub category
    PP = "PP"
    PM = "PM"
    IL_A = "A"
    IL_A2 = "A2"
    IL_A3 = "A3"
    IL_B = "B"
    IL_B2 = "B2"
    IL_B3 = "B3"
    IL_C = "C"
    IL_C2 = "C2"
    IL_D = "D"

    REGIME_SUB = (
        (PP, "Personne Physique"),
        (PM, "Personne Morale"),
        (IL_A, "A"),
        (IL_A2, "A2"),
        (IL_A3, "A3"),
        (IL_B, "B"),
        (IL_B2, "B2"),
        (IL_B3, "B3"),
        (IL_C, "C"),
        (IL_C, "C2"),
        (IL_D, "D"),
    )

    regime_sub = models.CharField(max_length=2, choices=REGIME_SUB, null=True, blank=True)

    # REGION ADMINISTRATIVE, REGION_ADMINISTRATIVE
    region = models.CharField(max_length=25, null=True, blank=True, verbose_name='Région Administrative')

    # DEPARTEMENT
    departement = models.CharField(max_length=50, null=True, blank=True)

    # VILLE
    ville = models.CharField(max_length=50, null=True, blank=True)
    # COMMUNE
    commune = models.CharField(max_length=50, null=True, blank=True)

    # QUARTIER
    quartier = models.CharField(max_length=255, null=True, blank=True)

    # Taux de précompte
    #taux_precompte = models.PositiveSmallIntegerField(null=True, blank=True)

    # VENTE BOISSON, VENTE_BOISSON
    vente_boisson = models.CharField(max_length=20, null=True, blank=True)

    # IDCLASSE ACTIVITE, IDCLASSE_ACTIVITE
    id_classe_activite = models.CharField(max_length=20, null=True, blank=True)

    change_list = models.ManyToManyField(EntrepriseChange, blank=True)
    exercice_list = models.ManyToManyField(Exercice, blank=True)

    def __str__(self):

        field_values = []
        for i in Entreprise._meta.get_fields():
            if i.name in ["change_list", "exercice_list", 'id']:
                continue

            value = self.__getattribute__(i.name)
            if value:
                field_values.append(str(value))

        return ",".join(field_values)

        #return f"{self.raison_sociale}, {self.sigle}, {self.bp}, {self.telephone}"


    def update(self, other):

        changes = []

        for field in Entreprise._meta.get_fields():
            if field.name in ['change_list', 'exercice_list', 'id']:
                continue
            a = self.__getattribute__(field.name)
            b = other.__getattribute__(field.name)
            if a != b:
                changes.append(str(b))
                self.__setattr__(field.name, b)

        return ",".join(changes)

    class Meta:
        ordering = ["sigle", "raison_sociale"]


class EntrepriseAdmin(admin.ModelAdmin):

    list_display = ('niu', 'raison_sociale','sigle', 'regime', 'forme_juridique', 'ville', 'telephone')
    search_fields = ('raison_sociale', 'sigle', 'niu', 'telephone')
    list_filter = ('regime', 'forme_juridique', 'ville', 'departement', 'region', 'etat_niu')


admin.site.register(Entreprise, EntrepriseAdmin)


class EntrepriseSerializer(serializers.ModelSerializer):

    #owner = TenderOwnerSerializer()
    cdi_cri = CDI_CRI_Serializer()

    class Meta:
        model = Entreprise
        fields = ["niu", "raison_sociale", "sigle", "activite_principale", "bp",
                  "telephone", "etat_niu", "forme_juridique", "lieu_dit", "regime",
                  "regime_sub", "region", "departement", "ville", "commune", "quartier",
                  "cdi_cri"]


class ContribuableMixin(models.Model):

    niu_count = models.PositiveIntegerField(default=0)
    is_active = models.NullBooleanField(null=True, blank=True)
    from_registration = models.SmallIntegerField(blank=True, null=True)
    is_contribuables_scanned = models.BooleanField(default=False)

    def get_supplier_names(self)->list:
        pass

    class Meta:
        abstract = True

class ArmpContract(ContribuableMixin):

    maitre_ouvrage = models.CharField(max_length=255)
    reference = models.CharField(blank=True, max_length=255)
    title = models.CharField(max_length=2550)
    date = models.DateField(blank=True, null=True)
    cost = models.BigIntegerField(null=True, blank=True)
    titulaire = models.CharField(blank=True, max_length=255)
    
    # niu_count = models.PositiveIntegerField(default=0)
    # is_active = models.NullBooleanField(null=True, blank=True)
    # from_registration = models.SmallIntegerField(blank=True, null=True)
    # is_contribuables_scanned = models.BooleanField(default=False)

    INFRUCTUEUX = 1
    ANNULE = 2
    ATTRIBUE = 3
    SIGNE = 4
    RESILIE = 5
    RECEPTIONNE = 6

    STATUS = (
        (INFRUCTUEUX, 'INFRUCTUEUX'),
        (ANNULE, 'ANNULE'),
        (ATTRIBUE, 'ATTRIBUE'),
        (SIGNE, 'SIGNE'),
        (RESILIE, 'RESILIE'),
        (RECEPTIONNE, 'RECEPTIONNE'),
    )

    status = models.IntegerField(choices=STATUS)
    year = models.PositiveIntegerField(blank=True, null=True)

    search_vector = SearchVectorField(null=True, blank=True)

    s_unique = models.CharField(blank=True, max_length=1000)

    class Meta:
        # 2022, check LE VICOMTE SARL
        # 2022
        # Fourniture de quatre (04) lots de pièces de rechange pour camions RVI (MIDLUM et DXI) à la SODECOTON
        # Fourniture de quatre (04) lots de pièces de rechange pour camions RVI à la SODECOTON
        # 2021
        # MIDLUM et DXI à la SODECOTON
        #unique_together = (("maitre_ouvrage", "title", "year", "titulaire"), ("s_unique",))
        unique_together = (("maitre_ouvrage", "title", "year", "titulaire", "cost"), ("s_unique",))
        indexes = [

            GinIndex(fields=['search_vector']),

        ]

    def __str__(self):
        return "{}, {}, {}, {}, {}".format(self.maitre_ouvrage, self.reference, self.year, self.cost, self.title )
    
    def get_supplier_names(self):
        return self.titulaire.split("/")

    def save(self, *args, **kwargs):
        # print(*args)
        # print(**kwargs)
        self.s_unique = self.__str__()[:1000]
        super(ArmpContract, self).save(*args, **kwargs)
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            # instance = self._meta.default_manager.with_documents().get(pk=self.pk)

            self.search_vector = SearchVector('maitre_ouvrage', 'title',
                                              'reference', 'titulaire', config='french_unaccent')
            #if self.pk % 1000 == 0:
            #    print(f"{self.pk}, {self.search_vector}")
            #print(f"{self.pk}, {self.search_vector}")
            self.save(update_fields=['search_vector'])


class ArmpContractAdmin(admin.ModelAdmin):

    list_display = ('maitre_ouvrage', 'status','reference', 'title', 'date', 'year', 'cost', 'titulaire')
    search_fields = ('title', 'maitre_ouvrage', 'titulaire', 'reference')
    list_filter = ('status', 'maitre_ouvrage', 'year')


admin.site.register(ArmpContract, ArmpContractAdmin)

####################################################################################################
## WORLD BANK PROJECT
####################################################################################################

# TODO don't forget tags whether one-to-one or many-to-one
# TODO french or english accent for search_vector?

class WBProject(models.Model):
    #Listing projects https://search.worldbank.org/api/v2/projects?format=json&fct=projectfinancialtype_exact,status_exact,regionname_exact,theme_exact,sector_exact,countryshortname_exact,cons_serv_reqd_ind_exact,esrc_ovrl_risk_rate_exact&fl=id,regionname,countryname,projectstatusdisplay,project_name,countryshortname,pdo,impagency,cons_serv_reqd_ind,url,boardapprovaldate,closingdate,projectfinancialtype,curr_project_cost,ibrdcommamt,idacommamt,totalamt,grantamt,borrower,lendinginstr,envassesmentcategorycode,esrc_ovrl_risk_rate,sector1,sector2,sector3,theme1,theme2,%20%20status,totalcommamt,proj_last_upd_date,curr_total_commitment&apilang=en&rows=20&countrycode_exact=CM&os=80

    project_id = models.CharField(max_length=20, unique=True) #id
    
    # Maybe charfield?
    name = models.TextField(null=True, blank=True) #project_name
    abstract = models.TextField(null=True, blank=True) #project_abstract.cdata!
    objective = models.TextField(null=True, blank=True) #pdo
    link = models.URLField(verbose_name="primary source") # url
    # borrower = models.CharField(max_length=255, blank=True, null=True) # borrower

    financial_type = models.CharField(max_length=10, blank=True, null=True) # projectfinancialtype[0]
    main_theme = models.CharField(max_length=255, blank=True, null=True) # ignore "!$!0"
    main_sector = models.CharField(max_length=255, blank=True, null=True) # sectorx.name, check sectorx.percent

    is_scanned = models.BooleanField(default=False)

    CLOSED = 0
    ACTIVE = 1
    DROPPED = 2
    PIPELINE = 3

    STATUS = (
        (CLOSED, 'Closed'),
        (ACTIVE, 'Active'),
        (DROPPED, 'Dropped'),
        (PIPELINE, 'Pipeline'),
    )

    status = models.IntegerField(choices=STATUS, blank=True, null=True) # status

    # Implementing Agency
    agency = models.CharField(max_length=255, blank=True, null=True) # impagency
    
    start_date = models.DateField(blank=True, null=True) #boardapprovaldate
    end_date = models.DateField(blank=True, null=True) #closingdate
    last_update = models.DateField(blank=True, null=True) #proj_last_upd_date

    cost = models.BigIntegerField(null=True, blank=True) # curr_project_cost

    # Note sure what this about
    lendinginstr = models.CharField(max_length=255, blank=True, null=True)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:

        indexes = [

            GinIndex(fields=['search_vector']),

        ]
        ordering = ["-start_date", '-cost']

    def __str__(self):
        return "{}: {}".format(self.project_id, self.name)

    def save(self, *args, **kwargs):

        super(WBProject, self).save(*args, **kwargs)

        #https://blog.lotech.org/postgres-full-text-search-with-django.html
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            self.search_vector = SearchVector('name', 'abstract', config='french_unaccent')
            self.save(update_fields=['search_vector'])


class WBProjectAdmin(admin.ModelAdmin):

    list_display = ('project_id', 'start_date', 'cost', 'name')
    search_fields = ('project_id', 'name', 'abstract', 'search_vector')
    list_filter = ('financial_type', 'status', 'agency')
    #exclude = ['search_vector']


admin.site.register(WBProject, WBProjectAdmin)


class WBSupplier(models.Model):
    # Listing sup

    # Maybe Integer?
    supplier_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=5, blank=True, null=True)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:

        indexes = [

            GinIndex(fields=['search_vector']),

        ]
        ordering = ["-supplier_id"]

    def __str__(self):
        return "{}, {}".format(self.supplier_id, self.name)

    def save(self, *args, **kwargs):

        super(WBSupplier, self).save(*args, **kwargs)

        #https://blog.lotech.org/postgres-full-text-search-with-django.html
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            self.search_vector = SearchVector('name', config='french_unaccent')
            self.save(update_fields=['search_vector'])


class WBSupplierAdmin(admin.ModelAdmin):

    list_display = ('supplier_id', 'name')
    search_fields = ('supplier_id', 'name', 'search_vector')
    exclude = ['search_vector']


admin.site.register(WBSupplier, WBSupplierAdmin)


class WBContract(ContribuableMixin):

    # Maybe Integer?
    contract_id = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(WBProject, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField()
    date = models.DateField()
    suppliers = models.ManyToManyField(WBSupplier, blank=True)
    cost = models.BigIntegerField()
    team_fullname = models.CharField(max_length=255, blank=True, null=True)
    procurement_group = models.CharField(max_length=255, blank=True, null=True)
    procurement_group_description = models.CharField(max_length=255, blank=True, null=True)
    procurement_meth_text = models.CharField(max_length=255, blank=True, null=True)
    rw_type = models.CharField(max_length=255, blank=True, null=True)

    is_scanned = models.BooleanField(default=False)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:

        indexes = [

            GinIndex(fields=['search_vector',]),
        ]
        ordering = ["-date", "project__project_id"]
    
    def get_project_id(self):
        return self.project.project_id

    def __str__(self):
        return "{}, {}: {}".format(self.project.project_id, self.contract_id, self.description)


    def get_supplier_names(self) -> list:
        return [x.name for x in self.suppliers.all()]

    def save(self, *args, **kwargs):

        super(WBContract, self).save(*args, **kwargs)

        #https://blog.lotech.org/postgres-full-text-search-with-django.html
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            self.search_vector = SearchVector('description', 'team_fullname', config='french_unaccent')
            self.save(update_fields=['search_vector'])


class WBContractAdmin(admin.ModelAdmin):

    list_display = ('date', 'get_project_id', 'cost', 'description')
    list_filter = ('project__project_id',)
    search_fields = ('search_vector',)

admin.site.register(WBContract, WBContractAdmin)



