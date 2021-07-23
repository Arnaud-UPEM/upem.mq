import re

from logging import error

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.utils.translation import templatize

from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet

from .data import ZIPS

from core.models import SEOAbstractEmailForm, SEOPage

from user.forms import AuthForm, SignupForm
from user.models import Auth

from education.models import GradeEnum, School

# from .forms import MemberForm

# from .forms import MemberForm

# Create your models here.


PHONE_REGEX = r"^(?:0|\+\d{1,3}?)\s?(?:\d\s?){9}$"


@register_snippet
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
class Member (models.Model):
    auth = models.OneToOneField(
        Auth,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='member'
    )

    last_name = models.CharField(max_length=100, default='', verbose_name='Nom')
    first_name = models.CharField(max_length=100, default='', verbose_name='Prénom')

    job = models.CharField(max_length=60, default='', verbose_name='Profession')

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

    panels = [
        MultiFieldPanel([
            FieldPanel('first_name'),
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
    ]

    def __str__ (self):
        return f'#{self.id} - {self.first_name} {self.last_name}'


class MemberChild (models.Model):
    last_name = models.CharField(
        max_length=100, default='', verbose_name='Nom')
    first_name = models.CharField(
        max_length=100, default='', verbose_name='Prénom')

    dob = models.DateField(verbose_name='Date de naissance')

    grade = models.CharField(max_length=20, default=GradeEnum.DEFAUT, null=True, blank=True, choices=GradeEnum.choices(), verbose_name='Classe')
    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='students'
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='children'
    )

    def __str__(self):
        return f'#{self.id} - {self.first_name} {self.last_name} - {self.dob}'


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
        return self.cleaned_data['job'].capitalize()

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
        print ('Hello')
        if 'newsletter_sub' in self.cleaned_data:
            if self.cleaned_data['newsletter_sub']:
                return True
        self.cleaned_data['newsletter_sub'] = False
        return False


class MemberChildForm (forms.ModelForm):
    class Meta:
        model = MemberChild
        fields = '__all__'


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


class ProfilePage (Page):
    template = 'memberships/profile_page.html'

    class Meta:
        verbose_name = 'Profile: Main Page'


class ProfileAccountPage (Page):
    template = 'memberships/profile_account_page.html'

    class Meta:
        verbose_name = 'Profile: Account Page'

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


class ProfileChildrenIndexPage (RoutablePageMixin, Page):
    template = 'memberships/profile_children_page.html'
    template_detail = 'memberships/profile_children_detail_page.html'
    template_delete = 'memberships/profile_children_delete_page.html'

    class Meta:
        verbose_name = 'Profile: Children Index Page'

    @route (r'^/$')
    def list (self, request, *args, **kwargs):
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

    """ Create, Read, Update """
    @route(r'^add/$')
    @route(r'^(\d+)/$', name='pk')
    def cru (self, request, pk=0):
        if request.user.is_authenticated:
            errors = []
            template = self.template_detail

            # If child exist
            # Check he is related to parent
            if pk:
                try:
                    child = MemberChild.objects.get(
                        pk=pk,
                        member__auth__email=request.user
                    )
                    form = MemberChildForm(request.POST or None, instance=child)

                except MemberChild.DoesNotExist:
                    errors.append('Enfant introuvable.')
                    return self._render(request, self.template_detail, {'errors': errors})

            else:
                form = MemberChildForm(request.POST or None)

            if request.method == 'POST':
                print (request.POST)
                if form.is_valid():
                    form.save()
                    template = self.template

                else:
                    print (form.errors)

            context = self.get_context (request)
            context['pk'] = pk
            context['form'] = form

            return render (
                request,
                template,
                context
            )

        else:
            return HttpResponse('Accès interdit', status=401)

    @route(r'^delete/(\d+)/$', name='pk')
    def delete (self, request, pk):
        template = self.template_delete
        context = self.get_context (request)
        context['errors'] = []

        if request.user.is_authenticated:
            try:
                child = MemberChild.objects.get(pk=pk)

                if child.member.id != request.user.member.id:
                    context['errors'].append('Vous n\'êtes pas autorisé a accéder à cette ressource.')
                    return self._render(request, self.template_detail)

                if request.method == 'POST':
                    child.delete()
                    return HttpResponseRedirect(self.get_url())

                context['child'] = child

            except MemberChild.DoesNotExist:
                context['errors'].append('Enfant introuvable.')

        else:
            context['errors'].append('Veuillez vous connecter pour accéder à ce contenu.')

        return render (
            request,
            template,
            context
        )

    def _render (self, request, template, context_udt = {}):
        context = self.get_context(request)
        context.update(context_udt)
        return render (
            request,
            template,
            context
        )


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

