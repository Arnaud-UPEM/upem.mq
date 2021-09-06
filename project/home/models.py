from django import forms
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from widgets.models import Alert, IconBox

from core.models import SEOPage


""" Used as Index Page """
class BlankIndexPage (SEOPage):

    class Meta:
        verbose_name = 'Template: Index'


""" Used as a free page with customizable template path """
class FreeHTMLPage (SEOPage):
    template = models.CharField(max_length=125, default='home/free_html_page.html')

    promote_panels = SEOPage.promote_panels + [
        FieldPanel('template')
    ]

    class Meta:
        verbose_name = 'Template: Page'


class HomePage(SEOPage):
    body = RichTextField(blank=True)

    icon_boxes = ParentalManyToManyField(
        IconBox,
        blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
        InlinePanel('gallery_images', label='Gallery images'),
        FieldPanel('icon_boxes', heading='Icon Boxes', widget=forms.CheckboxSelectMultiple)
    ]

    @property
    def alerts (self):
        return Alert.objects.active()

    def foo (self):
        return ['Hello', 'World']

    def serve (self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['foo'] = 'bar'
        
        return render (
            request,
            self.get_template(request, *args, **kwargs),
            context
        )


class HomeCarousel(Orderable):
    home = ParentalKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )

    link = models.URLField(blank=True, default='', verbose_name='URL')

    caption = RichTextField(blank=True, max_length=250, verbose_name='Courte introduction')

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('link'),
    ]


class WhoAreWePage (SEOPage):

    class Meta:
        verbose_name = 'Qui sommes-nous ?'
