from django.db import models as django_models

import modelcluster.models
from modelcluster.fields import ParentalKey

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)

from wagtail_dynamic_choice.model_fields import DynamicChoiceField

from .apps import get_app_label
from .categories import validate_category

__all__ = ['BeBriefSiteSettings', 'PostCategoryIndexPageSetting']

APP_LABEL = get_app_label()


@register_setting
class BeBriefSiteSettings(BaseSiteSetting, modelcluster.models.ClusterableModel):

    panels = [
            InlinePanel('post_category_index_pages'),
        ]


class PostCategoryIndexPageSetting(Orderable):

    class Meta(Orderable.Meta):
        verbose_name = 'Post Category Index Page'
        verbose_name_plural = 'Post Category Index Pages'
        unique_together = (('site_setting', 'category'),)

    site_setting = ParentalKey(BeBriefSiteSettings, related_name="post_category_index_pages",
                               on_delete=django_models.CASCADE, blank=False)

    category = DynamicChoiceField(max_length=128, validators=[validate_category], default='',
                                  blank=False, null=False,
                                  choices_function_name=APP_LABEL + ".categories.get_post_category_choices")

    canonical_index_page = django_models.ForeignKey(APP_LABEL + '.postindexpage',
                                                    null=True, blank=True, related_name='+',
                                                    on_delete=django_models.SET_NULL)

    panels = [
        FieldPanel('site_setting'),
        FieldPanel('category'),
        FieldPanel('canonical_index_page'),
    ]

    def __str__(self):
        return f"{self.category} for {self.site_setting.site_name}" # noqa
