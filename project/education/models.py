"""
https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/table/?disjunctive.nom_etablissement&disjunctive.type_etablissement&disjunctive.appartenance_education_prioritaire&disjunctive.type_contrat_prive&disjunctive.code_type_contrat_prive&disjunctive.pial&refine.code_departement=972&refine.type_etablissement=Lyc%C3%A9e&refine.type_etablissement=Coll%C3%A8ge&refine.type_etablissement=Ecole
"""

from enum import Enum, IntEnum

from django.db import models

from wagtail.search import index
from wagtail.snippets.models import register_snippet

# Create your models here.

class CEnum (Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class CIntEnum (IntEnum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TypeEtabEnum (CEnum):
    DEFAUT  = 'DEFAUT'
    AUTRE   = 'AUTRE'
    ECOLE   = 'Ecole'
    COLLEGE = 'Collège'
    LYCEE   = 'Lycée'
    ADMIN   = 'SERVICE ADMINSTRATIF'
    INFO    = 'INFORMATION ET ORIENTATION'


class StatusEnum (CEnum):
    DEFAUT  = 'DEFAUT'
    AUTRE   = 'AUTRE'
    PUBLIC  = 'PUBLIC'
    PRIVE   = 'PRIVE'


class TypeContratPriveEnum (CEnum):
    DEFAUT                      = 'DEFAUT'
    AUTRE                       = 'AUTRE'
    SANS_OBJET                  = 'SANS OBJET'
    HORS_CONTRAT                = 'HORS CONTRAT'
    CONTRAT_ASSO_TTS_CLASSES    = 'CONTRAT D\'ASSOCIATION TOUTES CLASSES'
    CONTRAT_ASSO_PART_CLASSES   = 'CONTRAT ASSOCIATION PARTIE DES CLASSES'
    CONTRAT_SIMPLE_TTS_CLASSES  = 'CONTRAT SIMPLE TOUTES CLASSES'
    CONTRAT_SIMPLE_PART_CLASSES = 'CONTRAT SIMPLE POUR PARTIE DES CLASSES'


class EtatEnum (CEnum):
    DEFAUT  = 'DEFAUT'
    AUTRE   = 'AUTRE'
    OUVERT  = 'OUVERT'
    FERME   = 'A FERMER'


class MinistereTutelleEnum (CEnum):
    DEFAUT  = 'DEFAUT'


class LibelleNatureEnum (CEnum):
    DEFAUT  = 'DEFAUT'
    AUTRE   = 'AUTRE'


class GradeEnum (Enum):
    DEFAUT  = 'Défaut'
    OTHER   = 'AUTRE'
    TPS     = 'Très Petite Section'
    PS      = 'Petite Section'
    MS      = 'Moyenne Section'
    GS      = 'Grande Section'
    CP      = 'CP'
    CE1     = 'CE1'
    CE2     = 'CE2'
    CM1     = 'CM1'
    CM2     = 'CM2'
    C6      = '6eme'
    C5      = '5eme'
    C4      = '4eme'
    C3      = '3eme'
    L2      = '2nd'
    L1      = '1ere'
    TERM    = 'Terminale'
    UNI     = 'Etudes'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


''' MODELS '''

@register_snippet
class School (models.Model, index.Indexed):
    identifiant_de_l_etablissement  = models.CharField(max_length=128, default='', blank=True, null=True)
    nom_etablissement               = models.CharField(max_length=128, default='', blank=True, null=True)

    type_etablissement              = models.CharField(max_length=128, default='DEFAUT', blank=True, null=True, choices=TypeEtabEnum.choices())
    status_public_prive             = models.CharField(max_length=128, default='DEFAUT', blank=True, null=True, choices=StatusEnum.choices())
    # libelle_nature​                  = models.CharField(max_length=128, default='', blank=True, null=True, choices='DEFAUT')

    # Accueil
    etat                            = models.CharField(max_length=128, default='DEFAUT', blank=True, null=True, choices=EtatEnum.choices())

    ecole_maternelle                = models.BooleanField(default=False, blank=True, null=True)
    ecole_elementaire               = models.BooleanField(default=False, blank=True, null=True)
    voie_generale                   = models.BooleanField(default=False, blank=True, null=True)
    voie_technologique              = models.BooleanField(default=False, blank=True, null=True)
    voie_professionnelle            = models.BooleanField(default=False, blank=True, null=True)

    # Contact
    fax                             = models.CharField(max_length=128, default='', blank=True, null=True)
    telephone                       = models.CharField(max_length=128, default='', blank=True, null=True)
    mail                            = models.CharField(max_length=128, default='', blank=True, null=True)

    # URLs
    web                             = models.URLField(default='', blank=True, null=True)
    fiche_onisep                    = models.URLField(default='', blank=True, null=True)

    # Address
    adresse_1                       = models.CharField(max_length=128, default='', blank=True, null=True)
    adresse_2                       = models.CharField(max_length=128, default='', blank=True, null=True)
    adresse_3                       = models.CharField(max_length=128, default='', blank=True, null=True)
    code_postal                     = models.CharField(max_length=10 , default='', blank=True, null=True)
    code_commune                    = models.CharField(max_length=10 , default='', blank=True, null=True)
    nom_commune                     = models.CharField(max_length=64 , default='', blank=True, null=True)
    # code_region                     = models.CharField(max_length=10 , default='', blank=True, null=True)
    # code_academie                   = models.CharField(max_length=10 , default='', blank=True, null=True)
    # code_departement                = models.CharField(max_length=10 , default='', blank=True, null=True)
    # libelle_region​                  = models.CharField(max_length=64 , default='', blank=True, null=True)
    # libelle_academie                = models.CharField(max_length=64 , default='', blank=True, null=True)
    # libelle_departement             = models.CharField(max_length=64 , default='', blank=True, null=True)
    # position                        = models.CharField(max_length=64 , default='', blank=True, null=True)
    # latitude                        = models.CharField(max_length=64 , default='', blank=True, null=True)
    # longitude                       = models.CharField(max_length=64 , default='', blank=True, null=True)
    # epsg_origine                    = models.CharField(max_length=64 , default='', blank=True, null=True)
    # coordx_origine                  = models.CharField(max_length=64 , default='', blank=True, null=True)
    # coordy_origine                  = models.CharField(max_length=64 , default='', blank=True, null=True)
    # precision_localisation          = models.CharField(max_length=64 , default='', blank=True, null=True)

    # Options
    restauration                        = models.BooleanField(default=False, blank=True, null=True)
    hebergement                         = models.BooleanField(default=False, blank=True, null=True)
    ulis                                = models.BooleanField(default=False, blank=True, null=True)
    apprentissage                       = models.BooleanField(default=False, blank=True, null=True)
    segpa                               = models.BooleanField(default=False, blank=True, null=True)
    section_arts                        = models.BooleanField(default=False, blank=True, null=True)
    section_cinema                      = models.BooleanField(default=False, blank=True, null=True)
    section_theatre                     = models.BooleanField(default=False, blank=True, null=True)
    section_sport                       = models.BooleanField(default=False, blank=True, null=True)
    section_internationale              = models.BooleanField(default=False, blank=True, null=True)
    section_europeenne                  = models.BooleanField(default=False, blank=True, null=True)
    lycee_agricole                      = models.BooleanField(default=False, blank=True, null=True)
    lycee_militaire                     = models.BooleanField(default=False, blank=True, null=True)
    lycee_des_metiers                   = models.BooleanField(default=False, blank=True, null=True)
    post_bac                            = models.BooleanField(default=False, blank=True, null=True)
    appartenance_education_prioritaire  = models.CharField(max_length=10, default='', blank=True, null=True)

    # SCHOOL
    siren_siret                         = models.CharField(max_length=64, default='', blank=True, null=True)       
    nombre_d_eleves                     = models.IntegerField(default=0, blank=True, null=True)
    # nom_circonscription               = models.CharField(max_length=64 , default='', blank=True, null=True)                 
    date_ouverture                      = models.CharField(max_length=64 , default='', blank=True, null=True)       
    date_maj_ligne                      = models.CharField(max_length=64 , default='', blank=True, null=True)

    type_contrat_prive                  = models.CharField(max_length=64 , default='DEFAUT', blank=True, null=True, choices=TypeContratPriveEnum.choices())        

    # ministere_tutelle​                       = models.CharField(max_length=64 , default='', blank=True, null=True, choices=MinistereTutelleEnum.DEFAUT)  
    # etablissement_mere                         
    # type_rattachement_etablissement_mere        
    # code_bassin_formation                       
    # libelle_bassin_formation                

    # OTHERS
    # greta                     =
    # rpi_disperse              =
    # rpi_concentre             =
    # code_nature               = models.CharField(max_length=10, default='', blank=True, null=True)  
    # code_type_contrat_prive   = models.CharField(max_length=10, default='', blank=True, null=True)  
    # pial                      = models.CharField(max_length=64, default='', blank=True, null=True)  

    # NOT FOUND
    # multi_uai                             =
    # etablissement_multi_lignes            =
    # code_zone_animation_pedagogique       =
    # libelle_zone_animation_pedagogique    =

    search_fields = [
        index.SearchField('nom_etablissement', partial_match=True)
    ]

    class Meta:
        verbose_name = 'Education: Ecole'

    def __str__(self) -> str:
        return self.nom_etablissement

    def get_school_type_tags (self):
        tags = []

        if self.ecole_maternelle:
            tags.append('MAT')

        if self.ecole_elementaire:
            tags.append('ELE')

        if any([self.voie_generale, self.voie_technologique, self.voie_professionnelle]):
            tags.append('LYC')

        if not tags:
            tags.append('COL')

        return ','.join(tags)


