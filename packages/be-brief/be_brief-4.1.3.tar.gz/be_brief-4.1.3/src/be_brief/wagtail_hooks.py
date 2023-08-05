
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import MenuItem
from wagtail import hooks
from wagtail.permissions import ModelPermissionPolicy

from .apps import get_app_label
from .models import Post

APP_LABEL = get_app_label()


class PostsMenuItem(MenuItem):

    permission_policy = ModelPermissionPolicy(Post)

    def __init__(self, label, *args, **kwargs):

        app_label = Post._meta.app_label
        model_name = Post._meta.model_name

        url = reverse(
            f"wagtailsnippets_{app_label}_{model_name}:list"
        )

        super(PostsMenuItem, self).__init__(label, url, *args, **kwargs)

    def is_shown(self, request):
        return self.permission_policy.user_has_any_permission(
                    request.user, ["add", "edit", "delete"]
                ),


@hooks.register('register_admin_menu_item')
def register_posts_menu_item():
    return PostsMenuItem(
        _('Posts'),
        name='posts', icon_name='pilcrow', order=300
    )
