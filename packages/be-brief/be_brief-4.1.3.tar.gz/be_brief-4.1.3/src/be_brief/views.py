from wagtail.snippets.views.snippets import SnippetViewSet
from .side_panels import PostSidePanels

__all__ = ['PostViewSet']


class CreateView(SnippetViewSet.add_view_class):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context.get("form")
        side_panels = PostSidePanels(
            self.request,
            self.model(),
            self,
            show_schedule_publishing_toggle=getattr(
                form, "show_schedule_publishing_toggle", False
            ),
        )

        context['side_panels'] = side_panels
        return context


class PostViewSet(SnippetViewSet):

    add_view_class = CreateView

