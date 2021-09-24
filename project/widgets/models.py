import pytz
from datetime import datetime, timedelta

from django.db import models
from django.db.models import F
from django.utils.timezone import now

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
# from wagtail.images.views.serve import generate_image_url
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

# from .serializers import PlaceSerializer

def _localize(date):
    if type(date) is str:
        _ = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    else:
        _ = date
    return pytz.utc.localize(_)

def T (datetime):
    return datetime.strftime("%d/%m/%Y") #, %H:%M")

# Create your models here.

@register_snippet
class Place (ClusterableModel):
    name = models.TextField(default='', verbose_name='Nom')
    label = models.TextField(default='', blank=True, verbose_name='Nom aternatif')

    email = models.EmailField(blank=True, default='')

    caption = RichTextField(blank=True, max_length=250, verbose_name='Court texte')

    maps = models.URLField(default='', blank=True, verbose_name='URL Google Maps')
    city = models.CharField(max_length=125, default='', blank=True, verbose_name='Ville')
    zip_code = models.CharField(max_length=10, default='', blank=True, verbose_name='Code postal')
    address_1 = models.CharField(max_length=255, default='', blank=True, verbose_name='Adresse ligne 1')
    address_2 = models.CharField(max_length=255, default='', blank=True, verbose_name='Adresse ligne 2')

    phone_fax = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone fax')
    phone_cell = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone portable')
    phone_home = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone fixe')

    latitude = models.FloatField(blank=True, default=0)
    longitude = models.FloatField(blank=True, default=0)

    # Socials
    google = models.URLField(default='', blank=True)
    twitter = models.URLField(default='', blank=True)
    youtube = models.URLField(default='', blank=True)
    facebook = models.URLField(default='', blank=True)
    instagram = models.URLField(default='', blank=True)


    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('label'),
        ], heading='Noms'),
        FieldPanel('caption'),
        FieldPanel('email'),
        MultiFieldPanel([
            FieldPanel('address_1'),
            FieldPanel('address_2'),
            FieldPanel('city'),
            FieldPanel('zip_code'),
            FieldPanel('maps'),
        ], heading='Adresse'),
        MultiFieldPanel([
            FieldPanel('phone_cell'),
            FieldPanel('phone_home'),
            FieldPanel('phone_fax'),
        ], heading='Téléphones'),
        MultiFieldPanel([
            FieldPanel('google'),
            FieldPanel('twitter'),
            FieldPanel('youtube'),
            FieldPanel('facebook'),
            FieldPanel('instagram'),
        ], heading='Réseaux sociaux'),
        MultiFieldPanel([
            FieldPanel('latitude'),
            FieldPanel('longitude'),
        ], heading='Coordonées'),
        # InlinePanel('gallery_images', label='Gallerie d\'images'),
    ]

    # @property
    # def images_formated (self):
    #     images = self.gallery_images.all()
    #     return [
    #         images[:6],
    #         images[6:]
    #     ]

    def __str__ (self):
        return self.name

    class Meta:
        verbose_name_plural = 'Lieu'




#### UPEEM ####

class Employee (models.Model):
    PREFIX_CHOICES = (
        ('', 'Aucun'),
        ('M. ', 'Monsieur'),
        ('Mme. ', 'Madame'),
        ('Mlle. ', 'Mademoiselle')
    )

    prefix = models.CharField(max_length=120, choices=PREFIX_CHOICES, blank=True, verbose_name='Préfixe')
    last_name = models.CharField(max_length=120, verbose_name='Nom')
    first_name = models.CharField(max_length=120, verbose_name='Prénom')

    TYPE_CHOICES = (
        ('', 'Aucun'),
        ('DIR.ANIM.', 'Directeur ACM'),
        ('DIR.F.ANIM.', 'Directrice Animation'),
        ('ANIM.M', 'Animateur ACM'),
        ('ANIM.F', 'Animatrice'),
        ('OFFICE', 'Employé Administratif'),
    )
    type = models.CharField(max_length=120, choices=TYPE_CHOICES, blank=True)

    grades = models.CharField(max_length=120, default='', blank=True, verbose_name='Diplômes (BAFA/BPJEPS)')
    qualifications = models.CharField(max_length=120, default='', blank=True, verbose_name='Qualifications (PSC1/BTS)')

    panels = [
        MultiFieldPanel([
            FieldPanel('prefix'),
            FieldPanel('last_name'),
            FieldPanel('first_name'),
            FieldPanel('type'),
            FieldPanel('grades'),
            FieldPanel('qualifications'),
        ], heading='Employé')
    ]

    def get_type (self):
        return dict(Employee.TYPE_CHOICES)[self.type]

    @staticmethod
    def get_types (prefix):
        return dict(Employee.TYPE_CHOICES)[prefix]

    # Purpose of this method is to fix missing type choices
    @staticmethod
    def fix_type_choices ():
        # Fix 1
        _ = Employee.objects.filter(type='DIR.F.ANIM.')
        _.update(type='DIR.ANIM.')

        # Fix 2
        _ = Employee.objects.filter(type='ANIM.F')
        _.update(type='ANIM.M')

    def __str__ (self):
        return f'{self.prefix}{self.last_name} {self.first_name}'

"""
@register_snippet
class Place (ClusterableModel):
    name = models.TextField(default='', verbose_name='Nom')
    label = models.TextField(default='', blank=True, verbose_name='Nom aternatif')

    email = models.EmailField(blank=True, default='')

    caption = RichTextField(blank=True, max_length=250, verbose_name='Court texte')

    city = models.CharField(max_length=125, default='', blank=True, verbose_name='Ville')
    zip_code = models.CharField(max_length=10, default='', blank=True, verbose_name='Code postal')
    address_1 = models.CharField(max_length=255, default='', blank=True, verbose_name='Adresse ligne 1')
    address_2 = models.CharField(max_length=255, default='', blank=True, verbose_name='Adresse ligne 2')

    phone_fax = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone fax')
    phone_cell = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone portable')
    phone_home = models.CharField(max_length=20, default='', blank=True,  verbose_name='Téléphone fixe')

    latitude = models.FloatField(blank=True, default=0)
    longitude = models.FloatField(blank=True, default=0)

    # Socials
    google = models.URLField(default='', blank=True)
    twitter = models.URLField(default='', blank=True)
    youtube = models.URLField(default='', blank=True)
    facebook = models.URLField(default='', blank=True)
    instagram = models.URLField(default='', blank=True)


    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('label'),
        ], heading='Noms'),
        FieldPanel('caption'),
        FieldPanel('email'),
        MultiFieldPanel([
            FieldPanel('address_1'),
            FieldPanel('address_2'),
            FieldPanel('city'),
            FieldPanel('zip_code'),
        ], heading='Adresse'),
        MultiFieldPanel([
            FieldPanel('phone_cell'),
            FieldPanel('phone_home'),
            FieldPanel('phone_fax'),
        ], heading='Téléphones'),
        MultiFieldPanel([
            FieldPanel('latitude'),
            FieldPanel('longitude'),
        ], heading='Coordonées'),
        InlinePanel('gallery_images', label='Gallerie d\'images'),
    ]

    @property
    def images_formated (self):
        images = self.gallery_images.all()
        return [
            images[:6],
            images[6:]
        ]

    def __str__ (self):
        return self.name

    class Meta:
        verbose_name_plural = 'Lieu'


class PlaceGalleryImage (Orderable):
    place = ParentalKey(
        Place,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )

    caption = RichTextField(blank=True, max_length=250, verbose_name='Texte court')

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

    @property
    def url (self):
        return self.image.file.url

    # @property
    # def thumbnail (self):
    #     return generate_image_url(self.image, 'fill-350x250')

    def __str__ (self):
        return f'Gallery image for {self.place}'

    class Meta:
        verbose_name = 'Lieu'
        verbose_name_plural = 'Lieux'
"""

class SchoolWidget (models.Model):
    """ School """
    school_director = models.CharField(max_length=240, default='', blank=True, verbose_name='Directeur Ecole (Nom Complet)')
    
    total_classrooms = models.IntegerField(default=0, blank=True, verbose_name='Nbrs classes')
    total_classmates = models.IntegerField(default=0, blank=True, verbose_name='Nbrs enfants')

    directory_link = models.URLField(default='', blank=True, verbose_name='Lien Annuaire de l\'Education')

    """ Program """
    program_theme       = models.CharField(max_length=120, default='', blank=True, verbose_name='Thème')
    program_start       = models.CharField(max_length=120, default='', blank=True, verbose_name='Date début')
    program_end         = models.CharField(max_length=120, default='', blank=True, verbose_name='Date fin')
    program_duration    = models.CharField(max_length=120, default='', blank=True, verbose_name='Durée')

    program_project     = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Project pédagogique (privé)'
    )

    program_planning    = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Planning d\'activité'
    )

    program_project_summary = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Résumé project pédagogique'
    )

    """ Animation """
    anim_director = models.OneToOneField(
        Employee,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='anim_director',
    )

    total_employees = models.IntegerField(default=0, blank=True, verbose_name='Nbrs employés')

    """ Base """
    place = models.OneToOneField(
        Place,
        on_delete=models.CASCADE,
        related_name='place'
    )

    panels = [
        SnippetChooserPanel('place'),
        MultiFieldPanel([
            FieldPanel('school_director'),
            FieldPanel('total_classrooms'),
            FieldPanel('total_classmates'),
            FieldPanel('directory_link'),
        ], heading='Ecole'),
        MultiFieldPanel([
            FieldPanel('program_start'),
            FieldPanel('program_theme'),
            FieldPanel('program_duration'),
            FieldPanel('program_end'),
            DocumentChooserPanel('program_project'),
            DocumentChooserPanel('program_project_summary'),
            DocumentChooserPanel('program_planning'),
        ], heading='Programme'),
        MultiFieldPanel([
            SnippetChooserPanel('anim_director'),

        ], heading='Animation')
    ]

    class Meta:
        verbose_name = 'Ecole'
        verbose_name_plural = 'Ecoles'

    @property
    def program_project_url (self):
        return self.program_project.url
    
    def __str__ (self):
        # return self.place.name
        return f'Ecole: {self.place.name}'


""" ICON BOX """

class IconBox (Orderable):
    title = models.CharField(max_length=120, default='', verbose_name='Titre')
    content = RichTextField(max_length=250, default='', verbose_name='Contenu')

    link = models.CharField(max_length=255, blank=True, default='', verbose_name='Lien')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='image',
    )

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('content'),
        FieldPanel('link')
    ]

    class Meta:
        verbose_name = 'Icon Box 1'
        verbose_name_plural = 'Icon Box 1'

    def __str__ (self):
        return self.title


""" ALERTS """

class AlertsIndexPage (Page):

    class Meta:
        verbose_name = 'Alertes: Page Index'

    def get_context (self, request):
        context = super().get_context(request)
        context['alerts'] = Alert.objects.all()

        return context


class AlertManager (models.Manager):
    def upcoming (self):
        return self.filter(
            date_start__gt=now()
        )

    def expired (self):
        return self.filter(
            date_end__lte=now()
        )
    
    def active (self, truncate=0):
        q = self.filter(
            date_start__lte=now(),
            date_end__gt=now()
        )
        return q[:truncate] if truncate else q


class Alert (Orderable):
    title = models.CharField(max_length=120, default='')
    content = RichTextField(max_length=250, default='')

    date_start = models.DateTimeField(verbose_name='Date de publication')
    date_end = models.DateTimeField(verbose_name='Date de fin')

    # Unused - too many issues with lookup
    # lifespan = models.PositiveIntegerField(blank=True, default=0, verbose_name='Durée visibilité en jour')

    date_created = models.DateTimeField(default=now)

    objects = AlertManager()

    panels = [
        FieldPanel('title', heading='Titre'),
        FieldPanel('content', heading='Contenu'),
        FieldPanel('type', heading='Type'),
        MultiFieldPanel([
            FieldPanel('date_start'), #, heading='Date de publication'),
            FieldPanel('date_end'), #, heading='Date de fin'),
        ], heading='Informations')
    ]

    ALERT_TYPE = (
        ('info', 'Information (Bleu)'),
        ('danger', 'Important (Rouge)'),
        ('success', 'Succès (Vert)'),
        ('warning', 'Attention (Jaune)')
    )
    type = models.CharField(max_length=50, choices=ALERT_TYPE, default='')

    class Meta:
        ordering = ['date_start']
        verbose_name = 'Alerte'

    def __str__ (self):
        return f'{self.title} ({self.type}) - {T(self.date_start)} {T(self.date_end)} ' 


