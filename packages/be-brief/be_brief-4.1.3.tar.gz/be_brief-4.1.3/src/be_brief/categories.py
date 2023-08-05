import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from wagtail_synopsis.curation import register_synopsis_category

__all__ = ['register_post_category', 'get_post_category_choices', 'validate_category', 'lookup_post_category']


POST_CATEGORIES = dict()


class PostCategory:

    @property
    def identifier(self):
        return self.app_label + ":" + self.local_identifier

    def __init__(self, app_label, local_identifier, name):

        self.app_label = app_label
        self.local_identifier = local_identifier
        self.name = name

        app = apps.get_app_config(self.app_label)
        self.app_name = app.verbose_name


def register_post_category(app_label, local_identifier, name):

    category = PostCategory(app_label=app_label, local_identifier=local_identifier, name=name)
    POST_CATEGORIES[category.identifier] = category

    register_synopsis_category(app_label, local_identifier, name)

    return category


def lookup_post_category(app_label, local_identifier=None, default=None):

    if local_identifier is None:
        identifier = app_label
    else:
        identifier = app_label + ":" + local_identifier

    return POST_CATEGORIES.get(identifier, default)


def get_post_category_choices():

    result = [(identifier, category.name + " [{}]".format(category.app_name.title()))
              for identifier, category in POST_CATEGORIES.items()]

    return result


def validate_category(value):

    if re.search(r"(^[^A-Za-z0-9_]|\s)", value):

        raise ValidationError(
            _("Categories must start with a letter, a digit or underscore "
              "and cannot contain whitespace characters: {:}").format(value)
        )