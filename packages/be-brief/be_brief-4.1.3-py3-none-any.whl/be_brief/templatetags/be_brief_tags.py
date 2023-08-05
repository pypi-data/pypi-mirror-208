from django import template

from ..apps import get_app_label

APP_LABEL = get_app_label()

register = template.Library()


SUPPORT_TEMPLATE_SETTING = APP_LABEL + '/tags/support.html'


@register.inclusion_tag(SUPPORT_TEMPLATE_SETTING, name="be_brief_support")
def be_brief_support_tag(*, container_element, is_admin_page=False):

    result = {
        'container_element': container_element,
        'is_admin_page': is_admin_page,
        'stylesheets': [],
        'scripts': []
    }

    return result
