import json
from logging import critical
import re

from datetime import datetime
from io import BytesIO

from django import forms
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, F, Count, FilteredRelation, Case, Value, When
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField
from django.db.models.functions import Concat
from django.forms import fields, widgets
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.utils.timezone import now
from django.utils.translation import templatize

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable
from wagtail.documents.models import AbstractDocument, Document
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

# from xhtml2pdf import pisa
from weasyprint import HTML

from .data import ZIPS

from core.models import SEOAbstractEmailForm, SEOPage, login_required_view

from user.forms import AuthForm, SignupForm
from user.models import Auth

from education.models import GradeEnum, School

from payment.models import IncorrectAmount, IncorrectCustomer, IncorrectProduct, IncorrectPayload


# from .forms import MemberForm

# from .forms import MemberForm

# Create your models here.


PHONE_REGEX = r"^(?:0|\+\d{1,3}?)\s?(?:\d\s?){9}$"

# ContributionPlan.objects.annotate(member=F('members__member__id'), price=F('members__price'), date_bought=F('members__date_bought')).values('id', 'member', 'price', 'date_bought')

# ContributionPlan.objects.filter(contribution=1).annotate(member=F('members__member__id'), price=F('members__price')).values('id', 'name', 'description', 'mod', 'member', 'price').filter(Q(member=2) | Q(member__isnull=True))


# @register_snippet
class SchoolYear (models.Model):
    date_end = models.DateField(verbose_name='Date fin')
    date_start = models.DateField(verbose_name='Date début')

    is_active = models.BooleanField(default=False, verbose_name='Active ?')

    def activate (self):
        _ = SchoolYear.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        
        if not self.is_active:
            self.is_active = True
            self.save()

    def __str__(self):
        return f'#{self.id} - {self.date_start} {self.date_end}'


@register_snippet
class Application (ClusterableModel):
    name = models.CharField(max_length=128, default='', verbose_name='Intitulé')
    description = models.TextField(default='', verbose_name='Description')
    condition = RichTextField(blank=True, verbose_name='Condition de candidature')

    date_end = models.DateField(verbose_name='Date fin')
    date_start = models.DateField(verbose_name='Date début')

    is_active = models.BooleanField(default=False, verbose_name='Est actif ?')

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('description'),
            FieldPanel('condition'),
        ], heading='Informations'),
        MultiFieldPanel([
            FieldPanel('date_start'),
            FieldPanel('date_end'),
            FieldPanel('is_active'),
        ], heading='Dates'),
    ]

    class Meta:
        verbose_name = 'Candidature'
        ordering = ['-is_active', '-date_end']

    @property
    def years (self):
        start = datetime.strftime(self.date_start, '%Y')
        end = datetime.strftime(self.date_end, '%Y')
        return f'{start} - {end}'

    @property
    def expired (self):
        now = datetime.now()
        if self.date_end < now.date():
            return True
        return False

    # Set an application to active
    # Deactivate other applications
    def activate (self):
        _ = Application.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        
        if not self.is_active:
            self.is_active = True
            self.save()

    # Apply to an application
    def apply (self, member, children_list):
        if not self.is_active:
            raise Exception ('Cette candidature est désactivé.')

        children = MemberChild.objects.filter(pk__in=children_list)
        member_applications = MemberApplication.objects.filter(member=member, application=self)

        if len(children) != len(children_list):
            raise Exception ('Liste enfant incorrecte.')

        for child in children:
            # Check if children belongs to member
            if child.member.pk != member.pk:
                raise Exception ('L\'enfant n\'est pas lié au compte')

            # Check
            if not member_applications.filter(child=child):
                MemberApplication.objects.create(
                    child=child,
                    member=member,
                    application=self
                )

        return True

    # Add children and MemberApplication to self Application
    def prepare (self, member):
        try:
            _ = []
            children = MemberChild.objects.filter(member=member)
            member_applications = MemberApplication.objects.filter(member=member, application=self)

            for child in children:
                _child = {
                    'id': child.id,
                    'last_name': child.last_name,
                    'first_name': child.first_name,
                    'grade': child.grade,
                    'school': child.school.__str__(),
                    # 'date_signed': datetime.now()
                }

                child_application = member_applications.filter(child=child)

                if child_application:
                    _child['date_signed'] = child_application.first().date_signed

                _.append(_child)

            setattr(self, 'children', _)
            
        except Exception as e:
            print (e)
            pass

        return self

    def __str__(self):
        active = '- (active)' if self.is_active else ''
        return f'#{self.id} - {self.name} {active}'
        return f'#{self.id} - {self.name} - {self.date_start} {self.date_end} {active}'


@register_snippet
class Contribution (ClusterableModel):
    banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='banner'
    )

    name = models.CharField(max_length=128, default='', verbose_name='Intitulé')
    description = models.TextField(default='', verbose_name='Description')

    date_end = models.DateField(verbose_name='Date fin')
    date_start = models.DateField(verbose_name='Date début')

    base_price = models.FloatField(default=0.0, verbose_name='Prix de base')

    is_active = models.BooleanField(default=False, verbose_name='Est actif ?')
    is_payable = models.BooleanField(default=False, verbose_name='Disponible à l\'achat ?')

    MEMBER = 0

    panels = [
        ImageChooserPanel('banner'),
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('description')
        ], heading='Informations'),
        MultiFieldPanel([
            FieldPanel('date_start'),
            FieldPanel('date_end')
        ], heading='Dates'),
        MultiFieldPanel([
            FieldPanel('base_price'),
            FieldPanel('is_active'),
            FieldPanel('is_payable')
        ], heading='Paramètres'),
        # MultiFieldPanel([
        #     InlinePanel('plans', heading='Tarifs', label='tarif')
        # ], heading='Tarifs'),
    ]

    class Meta:
        verbose_name = 'Cotisation'
        ordering = ['-date_end']

    @property
    def price (self):
        return self.base_price

    @property
    def cheapest (self):
        return self.plans.order_by('mod').first()

    @property
    def years (self):
        start = datetime.strftime(self.date_start, '%Y')
        end = datetime.strftime(self.date_end, '%Y')
        return f'{start} - {end}'

    @property
    def plans_for_member (self):
        if self.MEMBER:
            return self.plans.annotate(price=F('members__price'), date_bought=F('members__date_bought')).values('id', 'name', 'description', 'mod', 'price', 'date_bought').filter(Q(member=self.MEMBER) | Q(member__isnull=True))
        
        return self.plans.all()

    @property
    def expired (self):
        now = datetime.now()
        if self.date_end < now.date():
            return True
        return False

    def buy (self, id, amount, email):
        try:
            member = Member.objects.get(auth__email=email)

            member_contribution = MemberContribution.objects.filter(member=member, contribution=self)
            if member_contribution:
                raise IncorrectProduct

            if amount != self.base_price:
                raise IncorrectAmount

            member_contribution = MemberContribution.objects.create(
                price=amount,
                member=member,
                contribution=self,
                transaction_id=id
            )

            return member_contribution.id

        except Member.DoesNotExist:
            raise IncorrectCustomer

        # except Exception as e:
        #     raise IncorrectPayload


    def activate (self):
        _ = Contribution.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        
        if not self.is_active:
            self.is_active = True
            self.is_payable = True
            self.save()

    def __str__(self):
        active = '- (active)' if self.is_active else ''
        return f'#{self.id} - {self.name} {active}'
        return f'#{self.id} - {self.name} - {self.date_start} {self.date_end} {active}'


""" 
Not used anymore bcz we only want 1 plan 
Refer directly to Contribution
"""
class ContributionPlan (Orderable):
    name = models.CharField(max_length=128, default='', verbose_name='Intitulé')
    description = models.TextField(default='', verbose_name='Description')

    mod = models.FloatField(default=0.0, verbose_name='Modificateur de prix')

    contribution = ParentalKey(
        Contribution,
        on_delete=models.CASCADE,
        related_name='plans'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('mod'),
    ]

    class Meta:
        verbose_name = 'Cotisation Tarif'

    @property
    def price (self):
        return self.contribution.base_price + self.mod

    def __str__(self):
        return f'{self.name} - (Cotisation: {self.contribution})'
        

@register_snippet
class Member (index.Indexed, models.Model):
    auth = models.OneToOneField(
        Auth,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='member'
    )

    last_name = models.CharField(max_length=100, default='', verbose_name='Nom')
    first_name = models.CharField(max_length=100, default='', verbose_name='Prénom')

    job = models.CharField(max_length=60, blank=True, null=True, default='', verbose_name='Profession')

    @property
    def email (self):
        return self.auth.email
    # email = models.EmailField(default='', verbose_name='Email')

    address1 = models.CharField(max_length=100, default='', verbose_name='Ligne 1')
    zip_code = models.CharField(max_length=60, default='', verbose_name='Code Postal')

    city = models.CharField(max_length=60, default='', verbose_name='Ville', null=True, blank=True)
    country = models.CharField(max_length=60, default='Martinique', verbose_name='Pays', null=True, blank=True)
    address2 = models.CharField(max_length=100, default='', verbose_name='Ligne 2', null=True, blank=True)

    phone_cell = models.CharField(max_length=60, default='', verbose_name='Téléphone mobile')
    phone_pro = models.CharField(max_length=60, default='', verbose_name='Téléphone professionnel', null=True, blank=True)
    phone_home = models.CharField(max_length=60, default='', verbose_name='Téléphone fixe', null=True, blank=True) 

    newsletter_sub = models.BooleanField(default=True, verbose_name='Abonné newsletter')

    # email = ''
    # is_superuser = ''

    panels = [
        MultiFieldPanel([
            FieldPanel('last_name'),
            FieldPanel('first_name'),
            FieldPanel('job'),
            FieldPanel('newsletter_sub'),
        ], heading='Informations'),
        MultiFieldPanel([
            FieldPanel('address1'),
            FieldPanel('address2'),
            FieldPanel('city'),
            FieldPanel('zip_code'),
        ], heading='Adresse'),
        MultiFieldPanel([
            FieldPanel('phone_home'),
            FieldPanel('phone_cell'),
            FieldPanel('phone_pro'),
        ], heading='Téléphones'),
        MultiFieldPanel([
            # FieldPanel('email', widget=forms.EmailField),
            # FieldPanel('is_superuser', widget=forms.BooleanField),
            SnippetChooserPanel('auth')
        ], heading='Authentification'),
    ]

    search_fields = [
        index.SearchField('last_name', partial_match=True),
        index.SearchField('first_name', partial_match=True),
        index.SearchField('email', partial_match=True),
        # index.RelatedFields('children', [
        #     index.SearchField('last_name', partial_match=True),
        #     index.SearchField('first_name', partial_match=True),
        # ])
    ]

    class Meta:
        verbose_name = 'Membres: Parents'

    # Apply to an application
    def apply (self, application, child):
        pass

    # Pay a contribution
    def pay (self):
        pass

    def __str__ (self):
        return f'#{self.id} - {self.first_name} {self.last_name}'


@register_snippet
class MemberChild (index.Indexed, models.Model):
    last_name = models.CharField(
        max_length=100, default='', verbose_name='Nom')
    first_name = models.CharField(
        max_length=100, default='', verbose_name='Prénom')

    dob = models.DateField(verbose_name='Date de naissance')

    grade = models.CharField(max_length=20, default=GradeEnum.DEFAUT.value, choices=GradeEnum.choices(), null=True, blank=True, verbose_name='Classe')
    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='students'
    )

    # bar = models.BooleanField(default=True)
    # foo = models.BooleanField(default=True)

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='children'
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('last_name'),
            FieldPanel('first_name'),
            FieldPanel('dob'),
        ], heading='Informations'),
        MultiFieldPanel([
            FieldPanel('grade'),
            SnippetChooserPanel('school')
        ], heading='Scolarité'),
        MultiFieldPanel([
            SnippetChooserPanel('member')
        ], heading='Parenté'),
    ]

    search_fields = [
        index.SearchField('last_name', partial_match=True),
        index.SearchField('first_name', partial_match=True),
        # index.FilterField('dob'),
        # index.SearchField('first_name', partial_match=True),
        # index.RelatedFields('member', [
        #     index.SearchField('country'),
            # index.FilterField('first_name', partial_match=True),
        # ])
    ]

    class Meta:
        ordering = ['id']
        verbose_name = 'Membre: Enfant'
        # description = 'Ajouter un enfant à un parent'

    def school_str (self):
        return f'{self.first_name} {self.last_name} - {self.school} - {self.grade}'

    def __str__(self):
        return f'#{self.id} - {self.first_name} {self.last_name} - {self.dob}'


@register_snippet
class MemberContribution (models.Model, index.Indexed):
    price = models.FloatField(default=0.0, verbose_name='Prix achat')
    date_bought = models.DateTimeField(default=datetime.now, verbose_name='Date achat')

    ONLINE  = 'ON'
    CASH    = 'SO'
    CHECK   = 'JR'
    CREDIT  = 'SR'
    METHODS = [
        (ONLINE, 'En ligne'),
        (CASH, 'Espèce'),
        (CHECK, 'Chèque'),
        (CREDIT, 'Crédit'),
    ]
    method = models.CharField(
        max_length=2,
        choices=METHODS,
        default=ONLINE,
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='contributions'
    )

    contribution = models.ForeignKey(
        Contribution,
        on_delete=models.CASCADE,
        related_name='members'
    )

    transaction_id = models.PositiveIntegerField(default=0, verbose_name='ID transaction')
    
    # contribution_plan = models.ForeignKey(
    #     ContributionPlan,
    #     on_delete=models.CASCADE,
    #     related_name='_members'
    # )

    panels = [
        MultiFieldPanel([
            FieldPanel('price'),
            FieldPanel('date_bought'),
            FieldPanel('method'),
            SnippetChooserPanel('member'),
            SnippetChooserPanel('contribution'),
        ], heading='Informations'),
        MultiFieldPanel([
            FieldPanel('transaction_id')
        ], heading='Paiement en ligne')
    ]

    class Meta:
        ordering = ['-contribution__is_active', '-date_bought']
        verbose_name = 'Membre: Cotisation - Gérez les cotisations parents'
        verbose_name_plural = 'Membre: Cotisation - Gérez les cotisations parents'

    def __str__ (self):
        return f'#{self.id} - {self.contribution} - {self.member}'


# Added child directly there
@register_snippet
class MemberApplication (ClusterableModel):  
    date_signed = models.DateTimeField(default=datetime.now, verbose_name='Date signature')

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Membre'
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='members_application',
        verbose_name='Candidature'
    )

    child = models.ForeignKey(
        MemberChild,
        on_delete=models.CASCADE,
        related_name='child_application',
        verbose_name='Enfant'
    )

    panels = [
        SnippetChooserPanel('member'),
        SnippetChooserPanel('child'),
        SnippetChooserPanel('application'),
        # MultiFieldPanel([
        #     InlinePanel('school_lists')
        # ], heading='Listes candidature')
    ]
 
    class Meta:
        verbose_name = 'Membre: Candidature - Gérez les candidatures parents'
        verbose_name_plural = 'Membre: Candidature - Gérez les candidatures parents'
        ordering = ['member', 'application', 'child']

    def __str__ (self):
        return f'#{self.id} - {self.application} - {self.member} - {self.child}'


# Not used - See above
class MemberApplicationChild (Orderable):
    date_signed = models.DateTimeField(default=datetime.now, verbose_name='Date signature')

    application = ParentalKey(
        'memberships.MemberApplication',
        related_name='school_lists'
    )

    child = models.ForeignKey(
        MemberChild,
        on_delete=models.CASCADE,
        related_name='_child_application',
        verbose_name='Enfant',
        limit_choices_to={}
    )

    panels = [
        FieldPanel('date_signed'),
        SnippetChooserPanel('child')
    ]

    class Meta:
        verbose_name = 'Membre: Candidature par Ecole'

    def get_children_by_member (self, member=None):
        if member:
            return {'member': member}
        return {}


# 
class CustomDocument (AbstractDocument):
    description = models.TextField(default='', blank=True, null=True, verbose_name='Description')
    # last_update = models.DateTimeField(default=datetime.now, verbose_name='Dernière modification')

    admin_form_fields = Document.admin_form_fields + (
        'description',
    )

    class Meta:
        ordering = ['-created_at']

    # def save (self, *args, **kwargs):
    #     super(AbstractDocument, self).save(*args, **kwargs)


# class Donation (models.Model):
#     pass


####################################################################################
# FORMS
####################################################################################

class MemberForm (forms.ModelForm):
    class Meta:
        model = Member 
        fields = '__all__'
        # fields = ('last_name', 'first_name', 'job', 'address1', 'city', 'phone_cell', 'phone_pro', 'phone_home',)
        exclude = ['auth']

    def _clean_phone (self, phone):
        if re.search(PHONE_REGEX, phone):
            return phone
        raise ValidationError('Format incorrect.')

    def clean_last_name (self):
        return self.cleaned_data['last_name'].upper()
        
    def clean_first_name (self):
        return self.cleaned_data['first_name'].capitalize()

    def clean_job (self):
        if self.cleaned_data['job']:
            return self.cleaned_data['job'].capitalize()
        return ''

    def clean_address1 (self):
        return self.cleaned_data['address1'].capitalize()

    def clean_address2 (self):
        if self.cleaned_data['address2']:
            return self.cleaned_data['address2'].capitalize()
        return ''

    def clean_zip_code (self):
        zip = self.cleaned_data['zip_code']
        if zip in ZIPS:
            self.cleaned_data['city'] = ''
            return zip
        raise ValidationError('Code postal inconnu.')

    def clean_phone_cell (self):
        return self._clean_phone (self.cleaned_data['phone_cell'])

    def clean_phone_pro (self):
        phone = self.cleaned_data['phone_pro']
        if not phone:
            return ''            
        return self._clean_phone (phone)

    def clean_phone_home (self):
        phone = self.cleaned_data['phone_home']
        if not phone:
            return ''
        return self._clean_phone (phone)

    def clean_newsletter_sub (self):
        if 'newsletter_sub' in self.cleaned_data:
            if self.cleaned_data['newsletter_sub']:
                return True
        self.cleaned_data['newsletter_sub'] = False
        return False


class MemberChildForm (forms.ModelForm):

    class Meta:
        model = MemberChild
        fields = '__all__'
        exclude = ['member']

    def clean_last_name (self):
        return self.cleaned_data['last_name'].upper()
        
    def clean_first_name (self):
        return self.cleaned_data['first_name'].capitalize()

    # def clean_grade (self):
    #     print ('Hello')
    #     grade = self.cleaned_data['grade']
    #     if not grade:
    #         raise ValidationError(f'Sélectionnez un choix valide.')

    #     try:
    #         _ = GradeEnum[grade]
    #         return grade
    #     except:
    #         raise ValidationError(f'Sélectionnez un choix valide. {grade} n\'en fait pas partie.')


class RegistrationForm (MemberForm, AuthForm):
    class Meta:
        fields = '__all__'
        # fields = AuthForm.Meta.fields + MemberForm.Meta.fields


####################################################################################
# PAGES
####################################################################################

class RegistrationPage (SEOPage):
    template = 'memberships/registration_page.html'
    landing_page_template = 'memberships/registration_page_landing.html'

    promote_panels = SEOPage.promote_panels + [
        # FieldPanel('template_credentials'),
        # FieldPanel('template_memberships'),
        # FieldPanel('template_landing'),
    ]

    class Meta:
        verbose_name = 'Memberships: Inscription'

    def serve (self, request, *args, **kwargs):
        auth_form = None
        member_form = None
        template = self.template

        if request.method == 'POST':
            auth_form = SignupForm(request.POST)
            member_form = MemberForm(request.POST)

            # if auth_form.is_valid():
            #     auth = Auth.objects.filter(email=auth_form.cleaned_data['email'])
            #     if auth:
            #         auth_form.add_error('email', 'L\'adresse email est déjà utilisé.')

            # Re-check auth_form
            if all([auth_form.is_valid(), member_form.is_valid()]):
                auth = auth_form.save()
                auth.set_password(request.POST.get('password2'))
                auth.save()

                member = member_form.save()
                member.auth = auth
                member.city = ZIPS[member.zip_code]
                member.save()

                template = self.landing_page_template

            else:
                print (auth_form.errors)
                print (member_form.errors)

        context = self.get_context(request)
        context['auth_form'] = auth_form
        context['member_form'] = member_form

        return render(
            request,
            template,
            context
        )
            

    # def _serve(self, request, *args, **kwargs):
    #     """
    #     Implements a simple multi-step form.

    #     Stores each step into a session.
    #     When the last step was submitted correctly, saves whole form into a DB.
    #     """

    #     session_key_data = 'form_data-%s' % self.pk
    #     is_last_step = False
    #     step_number = int(request.GET.get('p', 1))   
    #     is_last_step = True if step_number == 3 else False
    #     print (step_number)

    #     if request.method == 'POST':
    #         prev_form_class, prev_template = self.get_data_for_step(step_number - 1)
    #         prev_form = prev_form_class(data=request.POST)

    #         if prev_form.is_valid():
    #             print ('a')
    #             form_data = request.session.get(session_key_data, {})
    #             form_data.update(prev_form.cleaned_data)
    #             request.session[session_key_data] = form_data

    #             if is_last_step:
    #                 auth_form = SignupForm(form_data)
    #                 member_form = MemberForm(form_data)
                    
    #                 if all(auth_form.is_valid(), member_form.is_valid()):
    #                     auth = auth_form.save()
    #                     member = member_form.save()
    #                     member.auth = auth
    #                     member.save()

    #                     del request.session[session_key_data]
    #                     return render (request, self.template_landing, {'member': member})

    #                 # If whole submission is incorrect
    #                 # Send user to the beginning
    #                 else:
    #                     message = 'Une erreur est survenue lors de l\'inscription. Veuillez recommencer.'
    #                     form_class, template = self.get_data_for_step(0)
    #                     form = form_class()

    #             else:
    #                 print ('c')
    #                 form_class, template = self.get_data_for_step(step_number)
    #                 form = form_class()
            
    #         else:
    #             print ('e')
    #             form = prev_form
    #             template = prev_template
    #             print (form.errors)

    #     else:
    #         print ('g')
    #         form_class, template = self.get_data_for_step(1) 
    #         form = form_class()
        

    #     context = self.get_context(request)
    #     context['form'] = form

    #     return render(
    #         request,
    #         template,
    #         context
    #     )

    #     paginator = Paginator(self.get_form_fields(), per_page=1)
    #     try:
    #         step = paginator.page(step_number)
    #     except PageNotAnInteger:
    #         step = paginator.page(1)
    #     except EmptyPage:
    #         step = paginator.page(paginator.num_pages)
    #         is_last_step = True

    #     if request.method == 'POST':
    #         # The first step will be submitted with step_number == 2,
    #         # so we need to get a form from previous step
    #         # Edge case - submission of the last step

    #         prev_step = step if is_last_step else paginator.page(step.previous_page_number())

    #         # Create a form only for submitted step
    #         prev_form_class = self.get_form_class_for_step(prev_step)
    #         prev_form = prev_form_class(request.POST, page=self, user=request.user)
    #         if prev_form.is_valid():
    #             # If data for step is valid, update the session
    #             form_data = request.session.get(session_key_data, {})
    #             form_data.update(prev_form.cleaned_data)
    #             request.session[session_key_data] = form_data

    #             if prev_step.has_next():
    #                 # Create a new form for a following step, if the following step is present
    #                 form_class = self.get_form_class_for_step(step)
    #                 form = form_class(page=self, user=request.user)
    #             else:
    #                 # If there is no next step, create form for all fields
    #                 form = self.get_form(
    #                     request.session[session_key_data],
    #                     page=self, user=request.user
    #                 )

    #                 if form.is_valid():
    #                     # Perform validation again for whole form.
    #                     # After successful validation, save data into DB,
    #                     # and remove from the session.
    #                     form_submission = self.process_form_submission(form)
    #                     del request.session[session_key_data]
    #                     # render the landing page
    #                     return self.render_landing_page(request, form_submission, *args, **kwargs)
    #         else:
    #             # If data for step is invalid
    #             # we will need to display form again with errors,
    #             # so restore previous state.
    #             form = prev_form
    #             step = prev_step
    #     else:
    #         # Create empty form for non-POST requests
    #         form_class = self.get_form_class_for_step(step)
    #         form = form_class(page=self, user=request.user)

    #     context = self.get_context(request)
    #     context['form'] = form
    #     context['fields_step'] = step
    #     return render(
    #         request,
    #         self.template,
    #         context
    #     )


# Test Registration landing page
class RegistrationLandingPage (SEOPage):
    template = 'memberships/registration_page_landing.html'

    class Meta:
        verbose_name = 'Memberships: Inscription Landing Page Test'


class RegistrationPage2 (SEOPage):
    template_credentials = models.CharField(max_length=125, default='memberships/credentials_page.html')
    template_memberships = models.CharField(max_length=125, default='memberships/memberships_page.html')

    template_landing = models.CharField(max_length=125, default='memberships/landing_page.html')

    promote_panels = SEOPage.promote_panels + [
        FieldPanel('template_credentials'),
        FieldPanel('template_memberships'),
        FieldPanel('template_landing'),
    ]

    class Meta:
        verbose_name = 'Memberships: Inscription (Old)'

    def get_data_for_step (self, step):
        if step == 2:
            return MemberForm, self.template_memberships

        else:
            return SignupForm, self.template_credentials
            

    def serve(self, request, *args, **kwargs):
        """
        Implements a simple multi-step form.

        Stores each step into a session.
        When the last step was submitted correctly, saves whole form into a DB.
        """

        session_key_data = 'form_data-%s' % self.pk
        is_last_step = False
        step_number = int(request.GET.get('p', 1))   
        is_last_step = True if step_number == 3 else False
        print (step_number)

        if request.method == 'POST':
            prev_form_class, prev_template = self.get_data_for_step(step_number - 1)
            prev_form = prev_form_class(data=request.POST)

            if prev_form.is_valid():
                print ('a')
                form_data = request.session.get(session_key_data, {})
                form_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = form_data

                if is_last_step:
                    auth_form = SignupForm(form_data)
                    member_form = MemberForm(form_data)
                    
                    if all(auth_form.is_valid(), member_form.is_valid()):
                        auth = auth_form.save()
                        member = member_form.save()
                        member.auth = auth
                        member.save()

                        del request.session[session_key_data]
                        return render (request, self.template_landing, {'member': member})

                    # If whole submission is incorrect
                    # Send user to the beginning
                    else:
                        message = 'Une erreur est survenue lors de l\'inscription. Veuillez recommencer.'
                        form_class, template = self.get_data_for_step(0)
                        form = form_class()

                else:
                    print ('c')
                    form_class, template = self.get_data_for_step(step_number)
                    form = form_class()
            
            else:
                print ('e')
                form = prev_form
                template = prev_template
                print (form.errors)

        else:
            print ('g')
            form_class, template = self.get_data_for_step(1) 
            form = form_class()
        

        context = self.get_context(request)
        context['form'] = form

        return render(
            request,
            template,
            context
        )

        paginator = Paginator(self.get_form_fields(), per_page=1)
        try:
            step = paginator.page(step_number)
        except PageNotAnInteger:
            step = paginator.page(1)
        except EmptyPage:
            step = paginator.page(paginator.num_pages)
            is_last_step = True

        if request.method == 'POST':
            # The first step will be submitted with step_number == 2,
            # so we need to get a form from previous step
            # Edge case - submission of the last step

            prev_step = step if is_last_step else paginator.page(step.previous_page_number())

            # Create a form only for submitted step
            prev_form_class = self.get_form_class_for_step(prev_step)
            prev_form = prev_form_class(request.POST, page=self, user=request.user)
            if prev_form.is_valid():
                # If data for step is valid, update the session
                form_data = request.session.get(session_key_data, {})
                form_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = form_data

                if prev_step.has_next():
                    # Create a new form for a following step, if the following step is present
                    form_class = self.get_form_class_for_step(step)
                    form = form_class(page=self, user=request.user)
                else:
                    # If there is no next step, create form for all fields
                    form = self.get_form(
                        request.session[session_key_data],
                        page=self, user=request.user
                    )

                    if form.is_valid():
                        # Perform validation again for whole form.
                        # After successful validation, save data into DB,
                        # and remove from the session.
                        form_submission = self.process_form_submission(form)
                        del request.session[session_key_data]
                        # render the landing page
                        return self.render_landing_page(request, form_submission, *args, **kwargs)
            else:
                # If data for step is invalid
                # we will need to display form again with errors,
                # so restore previous state.
                form = prev_form
                step = prev_step
        else:
            # Create empty form for non-POST requests
            form_class = self.get_form_class_for_step(step)
            form = form_class(page=self, user=request.user)

        context = self.get_context(request)
        context['form'] = form
        context['fields_step'] = step
        return render(
            request,
            self.template,
            context
        )


# Profile Page Dashboard
class ProfilePage (Page):
    template = 'memberships/profile_page.html'

    class Meta:
        verbose_name = 'Profile: Main Page'

    @login_required_view ('/unauthorized')
    def serve(self, request, *args, **kwargs):
        context = self.get_context (request)
        context['errors'] = []
        context['criticals'] = []

        try:
            member = Member.objects.get(auth__email=request.user)

            context['member'] = member

        except Member.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        return render (
            request,
            self.template,
            context
        )
        return super().serve(request, *args, **kwargs)


# Profil Page User Account 
class ProfileAccountPage (RoutablePageMixin, Page):
    template = 'memberships/profile_account_page.html'

    class Meta:
        verbose_name = 'Profile: Compte Parent'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def root (self, request, *args, **kwargs):
        form = None
        context = self.get_context (request)
        context['errors'] = []
        context['criticals'] = []

        # Check self.apply returns
        print (kwargs)
        if 'criticals' in kwargs:
            context['criticals'].extend(kwargs['criticals'])

        try:
            member = Member.objects.get(auth__email=request.user)
            form = MemberForm(request.POST or None, instance=member)

            if request.method == 'POST':

                print (request.POST)
            
                if form.is_valid():
                    member = form.save()
                    member.city = ZIPS[member.zip_code]
                    member.save()
                    print (member.newsletter_sub)

                else:
                    print (request.POST['zip_code'])
                    print (form.errors)

            context['member'] = member

        except Member.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        context['url'] = self.get_url()
        context['form'] = form
        
        return render (
            request,
            self.template,
            context
        )

    @route (r'^apply/$')
    @login_required_view ('/unauthorized')
    def apply (self, request):
        context = self.get_context(request)
        context['url'] = self.get_url()
        context['criticals'] = []

        response = {'status': 'Failure'}

        if request.method == 'POST':
            if not request.data or 'children' not in request.POST:
                response['message'] = 'Aucune donnée fournie.'
                return JsonResponse(response, status=400)

            try:
                member = Member.objects.get(auth__email=request.user)

                print (request.POST)

                response['status'] = 'Success'
                return JsonResponse(response, status=200)

            except Member.DoesNotExist:
                response['message'] = 'Impossible de récupérer les données du profil.'
                return JsonResponse(response, status=400)

        else:
            response['message'] = 'Méthode non autorisée.'
            return JsonResponse(response, status=405)

        return render (
            request,
            self.template,
            context
        )  

        context = self.get_context(request)
        context['url'] = self.get_url()
        context['criticals'] = []

        if request.method == 'POST':
            try:
                member = Member.objects.get(auth__email=request.user)

                print (request.POST)

                return HttpResponseRedirect(self.get_url())

            except Member.DoesNotExist:
                context['criticals'].append(
                    'Impossible de récupérer les données du profil.'
                )

        else:
            context['criticals'].append(
                'Méthode non autorisée.'
            )

        return self.root(request, kwargs={'criticals': context['criticals']})

        return render (
            request,
            self.template,
            context
        )        


# Profil Page User Account 
class ProfileApplicationPage (RoutablePageMixin, Page):
    template = 'memberships/profile_applications_page.html'

    class Meta:
        verbose_name = 'Profile: Candidatures Parent'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def root (self, request, *args, **kwargs):
        context = self.get_context (request)
        context['errors'] = []
        context['criticals'] = []

        try:
            member = Member.objects.get(auth__email=request.user)

            if request.method == 'POST':
                if request.POST:
                    # print (request.POST)

                    children = []

                    for x in request.POST:
                        # print (x)
                        try:
                            id = int(x)
                            if request.POST[x] == 'on':
                                children.append (id)
                        except ValueError:
                            pass

                    # print (children)

                    app = Application.objects.filter(is_active=True).first()
                    app.apply(member, children)

                else:
                    context['errors'].append('Aucune donnée fournie.')

            context['member'] = member

        except Member.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        except Exception as e:
            context['errors'].append(str(e))

        context['url'] = self.get_url() 
        
        return render (
            request,
            self.template,
            context
        )


# Profil: Child Pages List/Create/Update/Delete
class ProfileChildrenIndexPage (RoutablePageMixin, Page):
    template = 'memberships/profile_children_page.html'
    template_detail = 'memberships/profile_children_detail_page.html'
    template_delete = 'memberships/profile_children_delete_page.html'

    class Meta:
        verbose_name = 'Profile: Children Index Page'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def list (self, request, *args, **kwargs):
        form = None
        context = self.get_context (request)
        context['errors'] = []
        context['criticals'] = []

        try:
            member = Member.objects.get(auth__email=request.user)
            form = MemberForm(request.POST or None, instance=member)

            if request.method == 'POST':

                print (request.POST)
            
                if form.is_valid():
                    member = form.save()
                    member.city = ZIPS[member.zip_code]
                    member.save()
                    print (member.newsletter_sub)

                else:
                    print (request.POST['zip_code'])
                    print (form.errors)
        
        except Member.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        context['form'] = form

        return render (
            request,
            self.template,
            context
            )

    """ Create, Read, Update """
    @route(r'^add/$')
    @route(r'^(\d+)/$', name='pk')
    @login_required_view ('/unauthorized')
    def cru (self, request, pk=0):
        context = self.get_context (request)
        context['errors'] = []
        context['criticals'] = []
        
        template = self.template_detail

        try:
            member = Member.objects.get(auth__email=request.user)

            # If child exist
            # Check he is related to parent
            if pk:
                child = MemberChild.objects.get(
                    pk=pk,
                    member=member
                )
                form = MemberChildForm(request.POST or None, instance=child)

            else:
                # data = request.POST
                # data['member'] = member
                form = MemberChildForm(request.POST or None)

            if request.method == 'POST':
                # print (request.POST)
                if form.is_valid():
                    # print (child.id)
                    child = form.save(commit=False)
                    child.member = member
                    child.save()
                    return HttpResponseRedirect(self.get_url())

                else:
                    print (form.errors)

        except Member.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        except MemberChild.DoesNotExist:
            context['criticals'].append(
                'Impossible de récupérer les données de l\'enfant.'
            )

        context['pk'] = pk
        context['form'] = form
        context['grades'] = GradeEnum.choices()[1:]
        context['schools'] = School.objects.all()

        return render (
            request,
            template,
            context
        )

    @route(r'^delete/(\d+)/$', name='pk')
    @login_required_view ('/unauthorized')
    def delete (self, request, pk):
        template = self.template_delete
        context = self.get_context (request)
        context['criticals'] = []

        try:
            child = MemberChild.objects.get(pk=pk)

            if child.member.id != request.user.member.id:
                context['criticals'].append('Vous n\'êtes pas autorisé a accéder à cette ressource.')
                return self._render(request, self.template_detail)

            if request.method == 'POST':
                child.delete()
                return HttpResponseRedirect(self.get_url())

            context['child'] = child

        except MemberChild.DoesNotExist:
            context['criticals'].append('Enfant introuvable.')

        return render (
            request,
            template,
            context
            )

    @login_required_view ('/unauthorized')
    def _render (self, request, template, context_udt = {}):
        context = self.get_context(request)
        context.update(context_udt)
        return render (
            request,
            template,
            context
        )


# Profil: Contributions and Plans
class ProfileContribution (RoutablePageMixin, Page):
    template = 'memberships/profile_contribution.html'
    template_bill = 'memberships/profile_contribution_bill.html'

    class Meta:
        verbose_name = 'Profil: Cotisations'

    # def serve(self, request, *args, **kwargs):
    #     print ('Serve')
    #     return render(
    #         request,
    #         self.template,
    #         self.get_context(request, *args, **kwargs)
    #     )

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def list (self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['errors'] = []
        context['criticals'] = []

        try:
            member = Member.objects.get(auth__email=request.user)
            member_contribs = MemberContribution.objects.filter(member=member)
            if member_contribs:
                context['contribution'] = None
                context['contributions'] = []

                for contribution in Contribution.objects.all():
                    _ = member_contribs.filter(contribution=contribution).first()
                    if _:
                        # setattr(plan, 'contribution', plan.contribution.id)

                        setattr(contribution, 'ticket_id', _.id)
                        setattr(contribution, 'price_bought', _.price)
                        setattr(contribution, 'date_bought', _.date_bought)

                    if contribution.is_active:
                        context['contribution'] = contribution
                    else:
                        context['contributions'].append(contribution)

            else:
                context['contribution'] = Contribution.objects.filter(is_active=True).first()
                context['contributions'] = Contribution.objects.all().exclude(is_active=True).order_by('id')

        except Exception as e:
            print (str(e))
            context['criticals'].append(
                'Impossible de récupérer les données du profil.'
            )

        return render (
            request,
            self.template,
            context
        )

    # Using VADS instead
    @route (r'^pay/(\d+)/$', name='pk')
    @login_required_view ('/unauthorized')
    def pay (self, request, pk):
        return 

    def _facture (self, request, pk=0, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)

        try:
            mc = MemberContribution.objects.get(pk=pk)
            context['member_contribution'] = mc

            MONTHS = [
                '',
                'janvier',
                'février',
                'mars',
                'avril',
                'mai',
                'juin',
                'juillet',
                'août',
                'septembre',
                'octobre',
                'novembre',
                'décembre',
            ]

            context['date_literal'] = f'{mc.date_bought.day} {MONTHS[mc.date_bought.month]} {mc.date_bought.year}'
        except MemberContribution.DoesNotExist:
            if settings.DEBUG:
                pass

            context['critical'] = 'Reçu introuvable. Veuillez recommencer.'

        return context

    @route (r'^facture/(\d+)/$', name='pk')
    @login_required_view ('/unauthorized')
    def facture (self, request, pk=0, *args, **kwargs):
        context = self._facture (request, pk, *args, **kwargs)

        return render (
            request,
            self.template_bill,
            context
        )

    @route (r'^facture/pdf/(\d+)/$', name='pk')
    @login_required_view ('/unauthorized')
    def facture_pdf (self, request, pk=0, *args, **kwargs):
        template = get_template (self.template_bill)
        html = template.render(self._facture(request, pk, *args, **kwargs))

        # result = BytesIO()

        # pdf = pisa.pisaDocument(BytesIO(html.encode('utf8')), result)

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        filename = 'bill-2021.pdf'

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="' + filename + '"'
        return response

        if not pdf.err:
            # return FileResponse (result, as_attachment=True, filename='bill.pdf')
            return HttpResponse (result.getvalue(), content_type='application/pdf')

        return None

        context = self.get_context(request, *args, **kwargs)

        try:
            mc = MemberContribution.objects.get(pk=pk)
            context['member_contribution'] = mc

            MONTHS = [
                'janvier',
                'février',
                'mars',
                'avril',
                'mai',
                'juin',
                'juillet',
                'août',
                'septembre',
                'octobre',
                'novembre',
                'décembre',
            ]

            context['date_literal'] = f'{mc.date_bought.day} {MONTHS[mc.date_bought.month]} {mc.date_bought.year}'
        except MemberContribution.DoesNotExist:
            if settings.DEBUG:
                pass

            else:
                context['critical'] = 'Reçu introuvable. Veuillez recommencer.'
            

        return render (
            request,
            self.template_bill,
            context
        )


# ???
class ProfileChildrenPage (RoutablePageMixin, Page):
    template = 'memberships/profile_children_page.html'

    class Meta:
        verbose_name = 'Profile: Children Page'

    @route(r'^mes-enfants/add/$')
    @route(r'^mes-enfants/(\d+)/$', name='id')
    def do (self, request, id=0):
        if request.user.is_authenticated:

            errors = []

            # If child exist
            # Check he is related to parent
            if id:
                try:
                    child = MemberChild.objects.get(
                        pk=id,
                        member__auth__email=request.user
                    )
                    form = MemberChildForm(request.POST or None, instance=child)

                except MemberChild.DoesNotExist:
                    errors.append('Enfant introuvable.')
                    return self._render(request, self.template, {'errors': errors})

            else:
                form = MemberChildForm(request.POST or None)

            if request.method == 'POST':

                if form.is_valid():
                    member = form.save()

                else:
                    print (request.POST['zip_code'])
                    print (form.errors)

            context = self.get_context (request)
            context['form'] = form

            return render (
                request,
                self.template,
                context
            )

        else:
            return HttpResponse('Accès interdit', status=401)

    def _render (self, request, template, context_udt):
        context = self.get_context(request)
        context.update(context_udt)
        return render (
            request,
            template,
            context
        )

    def serve (self, request, *args, **kwargs):
        if request.user.is_authenticated:
            member = Member.objects.get(auth__email=request.user)
            form = MemberForm(request.POST or None, instance=member)

            if request.method == 'POST':

                print (request.POST)
            
                if form.is_valid():
                    member = form.save()
                    member.city = ZIPS[member.zip_code]
                    member.save()
                    print (member.newsletter_sub)

                else:
                    print (request.POST['zip_code'])
                    print (form.errors)

            context = self.get_context (request)
            context['form'] = form

            return render (
                request,
                self.template,
                context
            )

        else:
            return HttpResponse('Accès interdit', status=401)


class ProfileDocumentsPage (RoutablePageMixin, Page):
    template = 'memberships/profile_documents_page.html'

    class Meta:
        verbose_name = 'Profil: Documents'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def root (self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)

        return render (
            request,
            self.template,
            context
        )


class ProfileSchoolList (RoutablePageMixin, Page):
    template = 'memberships/profile_schools_list.html'
    template_details = 'memberships/profile_schools_details.html'
    
    class Meta:
        verbose_name = 'Profil: Candidatures par ecoles'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def root (self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)

        try:
            app = Application.objects.get(is_active=True)

            schools = School.objects.filter(students__child_application__application=app).annotate(count=Count('nom_etablissement')).order_by('-count')

            page = request.GET.get('page', 1)
            print (page)

            paginator = Paginator(schools, 10)
            page_obj = paginator.get_page(page)

            context['page_obj'] = page_obj
        
        except Application.DoesNotExist:
            context['criticals'] = ['Aucune candidature active']

        return render (
            request,
            self.template,
            context
        )

    @route (r'^(\d+)/$', name='id')
    @login_required_view ('/unauthorized')
    def details (self, request, id, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)

        try:
            app = Application.objects.get(is_active=True)

            schools = School.objects.filter(id=id, students__child_application__application=app).annotate(count=Count('nom_etablissement')).order_by('-count')
            school = schools.first()
            # print (schools)

            members = Member.objects.filter(applications__application=app, applications__child__school=school).order_by('last_name')

            context['school'] = school
            context['members'] = members
        
        except Application.DoesNotExist:
            context['criticals'] = ['Aucune candidature active.']

        except School.DoesNotExist:
            context['criticals'] = ['Ecole introuvable.']

        except Exception as e:
            print (e)

        return render (
            request,
            self.template_details,
            context
        )

    @route (r'^json/$', name='id')
    @route (r'^json/(\d+)/$', name='id')
    @login_required_view ('/unauthorized')
    def dl_json (self, request, id=0, *args, **kwargs):
        data = []
        response_obj = {'status': 'Failure'}

        try:
            app = Application.objects.get(is_active=True)

            schools = School.objects.filter(students__child_application__application=app).annotate(count=Count('nom_etablissement')).order_by('-count')

            def do (school):
                # school = schools.filter(id=id).first()
                members = Member.objects.filter(applications__application=app, applications__child__school=school).order_by('last_name')
                
                return {
                    'ecole': school.nom_etablissement,
                    'membres': [f'{member.last_name} {member.first_name}' for member in members]
                }

            if id:
                data.append(
                    do(schools.filter(id=id).first())
                )

            else:
                for school in schools:
                    data.append(
                        do(school)
                    )

            # print (data)
            
            response = HttpResponse(json.dumps(data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export.json'
            return response

            # return JsonResponse(data, status=200)
        
        except Application.DoesNotExist:
            response_obj['message'] = 'Aucune candidature active.'

        except School.DoesNotExist:
            response_obj['message'] = 'Ecole introuvable.'

        except Exception as e:
            response_obj['message'] = str(e)

        return JsonResponse(response_obj, status=400)


class AdminMembers (RoutablePageMixin, Page):
    template = 'memberships/admin_members_list_page.html'
    template_details = 'memberships/admin_members_details_page.html'

    class Meta:
        verbose_name = 'Profile Admin: Membres'

    @route (r'^$')
    @login_required_view ('/unauthorized')
    def list (self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)

        members = Member.objects.all()

        try:
            con = Contribution.objects.get(is_active=True)
            # members = members.annotate(contribution=FilteredRelation('contributions', condition=Q(contributions__contribution=con)))
            # members = members.annotate(contribution=F('contributions__contribution')).filter(Q(contribution=con.id) | Q(contribution__isnull=True))
            # members = members.objects.annotate(contribution=FilteredRelation('contributions', condition=Q(contributions__contribution=con)))

            members = members.annotate(
                contribution=Case(
                    When(contributions__contribution=con, then=Value(con.id)),
                    default=Value(None)
                )
            ).distinct('id')

        except:
            con = None

        try:
            app = Application.objects.get(is_active=True)

            children = MemberChild.objects.annotate(
                application=Case(
                    When(child_application__application=app, then=Value(app.id)),
                    default=Value(None)
                )
            ).distinct('id')

        except:
            con = None

        # for m in Member.objects.annotate(contribution=FilteredRelation('contributions', condition=Q(contributions__contribution=con))).order_by('id'):
        #     print (m)

        # for m in Member.objects.annotate(contribution=F('contributions__contribution')).filter(Q(contribution=con.id)).order_by('id'):
        #     print (m)

        # members = Member.objects.annotate(
        #     contribution=Case(
        #         When(contributions__contribution=con, then=Value(con.id)),
        #         default=Value(None)
        #     )
        # ).distinct('id')



        # members = Member.objects.annotate(children_f=FilteredRelation('children', condition=Q(children__first_name='Emerson'))).values('id', 'first_name', 'last_name', 'children_f__id', 'children_f__first_name').filter(Q(children_f__is_null=False))

        # members = Member.objects.annotate(c_id=F('children__id'), c_first_name=F('children__first_name')).values('id', 'first_name', 'last_name', 'c_id', 'c_first_name').filter(Q(c_first_name='Emerson'))
        # condition=)).filter(Q(children_f__is_null=False))

        # members = self._filtering (request, members)

        page = request.GET.get('page', 1)

        paginator = Paginator(members, 10)
        page_obj = paginator.get_page(page)

        context['page_obj'] = page_obj
        context['grades'] = dict(GradeEnum.choices())

        return render(
            request,
            self.template,
            context
        )


    @route (r'^membre/(\d+)/$', name='id')
    # @route (r'^enfant/(\d+)/$', name='child_id')
    @login_required_view ('/unauthorized')
    def details (self, request, id=0, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['criticals'] = []

        try:
            # if id:
            #     member = Member.objects.get(pk=id)

            # elif child_id:
            #     member = Member.objects.get(children__pk=child_id)

            # else:
            #     raise Exception ('Aucun argument donné.')

            member = Member.objects.get(pk=id)

            # Base

            try:
                app = Application.objects.get(is_active=True)
                children = member.children.all()
                for child in children:
                    mapp = MemberApplication.objects.filter(
                        child=child,
                        application=app
                    ).first()
                    setattr(child, 'mapp', mapp)

                    mapp = MemberApplication.objects.filter(child=child, application=app).first()

            except:
                children = member.children.all()

            setattr(member, 'children_', children)

            context['member'] = member
            context['member_contributions'] = MemberContribution.objects.filter(member=member)

        except Member.DoesNotExist:
            context['criticals'].append('Membre introuvable.')

        except Exception as e:
            context['criticals'].append(str(e))

        return render (
            request,
            self.template_details,
            context
        )

    """
    Tags
        names
        email
        enfant_id
        children_names
        school_name
        grade
    """
    def _filtering (self, request, members):
        # Member
        names = request.GET.get('names', False)
        if names:
            members = members.annotate(
                names=Concat('first_name', Value(' '), 'last_name')
            ).filter(
                names__icontains=names
            )

        email = request.GET.get('email', False)
        if email:
            members = members.filter(auth__email__icontains=email)

        # Children
        child_id = request.GET.get('child_id', False)
        if child_id:
            pass

        child_names = request.GET.get('child_names', False)
        if child_names:
            members = members.annotate(
                names=Concat('children__first_name', Value(' '), 'children__last_name')
            ).filter(
                names__icontains=child_names
            )
        
        grade = request.GET.get('grade', False)
        if grade:
            members = members.filter(children__grade=getattr(GradeEnum, grade))

        school_name = request.GET.get('school_name', False)
        if school_name:
            members = members.filter(children__school__nom_etablissement__icontains=school_name)

        return members

        
