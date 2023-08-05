# from django.urls import reverse
# from wagtail.admin.ui.side_panels import BasePreviewSidePanel, BaseSidePanels

from wagtail.snippets.side_panels import SnippetPreviewSidePanel, SnippetSidePanels

from .apps import get_app_label

__all__ = ['PostSidePanels']

APP_LABEL = get_app_label()


class PostPreviewSidePanel(SnippetPreviewSidePanel):

    def get_context_data(self, parent_context):

        saved_primary_key = self.object.pk
        self.object.pk = None

        context = super().get_context_data(parent_context)

        self.object.pk = saved_primary_key
        return context


class PostSidePanels(SnippetSidePanels):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        side_panel_index = [index for index, side_panel in enumerate(self.side_panels) if isinstance(side_panel, SnippetPreviewSidePanel)]

        if side_panel_index:
            side_panel_index = side_panel_index[0]
            old_side_panel = self.side_panels[side_panel_index]
            self.side_panels[side_panel_index] = PostPreviewSidePanel(old_side_panel.object, old_side_panel.request)

