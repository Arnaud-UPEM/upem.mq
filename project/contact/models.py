from django import forms
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.admin.mail import send_mail
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField,
    FORM_FIELD_CHOICES
)
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from core.models import SEOAbstractEmailForm

# Create your models here.

class FormField(AbstractFormField):
    page = ParentalKey(
        'ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )


class ACMFormField(AbstractFormField):
    page = ParentalKey(
        'ACMContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )

    
class ContactPage(SEOAbstractEmailForm):

    place = models.ForeignKey(
        'widgets.Place',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_places',
        verbose_name='Lieu'
    )

    template = models.CharField(max_length=125, blank=True, default='contact/contact_page.html')

    landing_page_template = models.CharField(max_length=125, blank=True, default='contact/contact_page_landing.html')

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = SEOAbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname='col6'),
                FieldPanel('to_address', classname='col6'),
            ]),
            FieldPanel('subject'),
        ], heading='Paramètres'),
        InlinePanel('form_fields', label='Form Fields'),
        SnippetChooserPanel('place'),
    ]

    promote_panels = SEOAbstractEmailForm.promote_panels + [
        FieldPanel('template'),
        FieldPanel('landing_page_template'),
    ]

    class Meta:
        verbose_name = 'Contact: Formulaire'

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))
        content = '\n'.join(content)
        send_mail(
            self.subject, content, addresses, self.from_address)


# Formulaire de signalement
class ACMContactPage (AbstractEmailForm):

    template = 'contact/acm_contact_page.html'
    
    # Landing page is kinda a template
    landing_page_template = 'contact/contact_page_landing.html'

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname='col6'),
                FieldPanel('to_address', classname='col6'),
            ]),
            FieldPanel('subject'),
        ], heading='Paramètres'),
        InlinePanel('form_fields', label='Form Fields'),
    ]

    class Meta:
        verbose_name = 'Contact: Demande d\'intervention'

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            print (request.POST)
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
            if form.is_valid():
                
                bouble_check = False

                DATA_NAME = 'objet-de-votre-demande'
                DATA_OTHER_NAME = 'objet_de_votre_demande'

                if form.cleaned_data[DATA_NAME] == 'Autre':
                    choix_autre = request.POST.get(DATA_OTHER_NAME, False)
                    if choix_autre:
                        form.cleaned_data[DATA_NAME] = choix_autre
                        bouble_check = True
                    
                    else :
                        form.errors[DATA_NAME] = ['Si Autre, précisez votre choix']
                        form.errors[DATA_OTHER_NAME] = ['Précisez votre choix ici.']

                if bouble_check:
                    form_submission = self.process_form_submission(form)
                    return self.render_landing_page(request, form_submission, *args, **kwargs)

        else:
            form = self.get_form(page=self, user=request.user)

        ctx = self.get_context(request)
        ctx['form'] = form

        return render(
            request,
            self.template,
            ctx
        )

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))
        content = '\n'.join(content)
        send_mail(
            self.subject, content, addresses, self.from_address)
    

