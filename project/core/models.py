from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel
from wagtail.core.models import Page
from wagtail.contrib.forms.models import AbstractEmailForm

# Create your models here.

class SEOPage (Page):
    seo_keywords = models.CharField(
        verbose_name=_("page keywords"),
        max_length=255,
        blank=True,
        help_text=_("Optional. 'Search Engine Friendly' keywords. This will appear in head metadata.")
    )

    seo_description = models.CharField(
        verbose_name=_("page description"),
        max_length=255,
        blank=True,
        help_text=_("Optional. 'Search Engine Friendly' description. This will appear in head metadata.")
    )

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('seo_keywords'),
            FieldPanel('seo_description'),
            FieldPanel('show_in_menus'),
            FieldPanel('search_description'),
        ], _('Common page configuration')),
    ]

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title


class SEOAbstractEmailForm (AbstractEmailForm):
    seo_keywords = models.CharField(
        verbose_name=_("page keywords"),
        max_length=255,
        blank=True,
        help_text=_("Optional. 'Search Engine Friendly' keywords. This will appear in head metadata.")
    )

    seo_description = models.CharField(
        verbose_name=_("page description"),
        max_length=255,
        blank=True,
        help_text=_("Optional. 'Search Engine Friendly' description. This will appear in head metadata.")
    )

    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('seo_keywords'),
            FieldPanel('seo_description'),
            FieldPanel('show_in_menus'),
            FieldPanel('search_description'),
        ], _('Common page configuration')),
    ]

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title

