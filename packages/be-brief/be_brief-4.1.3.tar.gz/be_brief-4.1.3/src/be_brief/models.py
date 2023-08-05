import re


# Django
import modelcluster.models
from django.db import models as django_models
from django.db.models import ForeignKey
from django.conf import settings
from django.db import transaction
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.core.files.utils import validate_file_name as validate_file_name_impl
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language_from_request
from django.utils.functional import cached_property, classproperty
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.shortcuts import redirect

# Wagtail

from wagtail.snippets.models import register_snippet
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path
from wagtail.models import (Page, Orderable, TranslatableMixin, DraftStateMixin, RevisionMixin, PreviewableMixin, Site,
                            Locale)

from wagtail.rich_text import RichText
from wagtail_preference_blocks.decorators import provides_preferences_context

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TagBase, ItemBase

from django_auxiliaries.validators import python_identifier_validator
from django_auxiliaries.variable_scope import WagtailPageMixin, reset_variable_scopes, load_variable_scope
from django_auxiliaries.servable import Servable

from wagtail_dynamic_choice.model_fields import DynamicChoiceField
from wagtail_synopsis.models import AUTHOR_ROLE, build_synopsis_class_for

from officekit.models import Person, Organisation, GroupMember
from tour_guide.anchors import AnchorRegistry
from tour_guide.decorators import chooses_navigation_categories

# Panels

from wagtail.admin.panels import (FieldPanel, InlinePanel, TabbedInterface, ObjectList)


# Registration Decorators

from wagtail.utils.decorators import cached_classmethod

from .categories import validate_category, lookup_post_category

from .model_fields import PostContentField
from .blocks import PostBlock

from .html_to_text import html_to_text


from .apps import get_app_label
from .wagtail_settings import BeBriefSiteSettings, PostCategoryIndexPageSetting
from .views import PostViewSet

APP_LABEL = get_app_label()


def validate_file_name(file_name):

    try:
        validate_file_name_impl(file_name, allow_relative_path=True)
    except SuspiciousOperation:
        raise ValidationError("File names must start with a forward slash and must not contain any " +
                              "parent directory components.")


class PostTag(TagBase):
    class Meta:
        verbose_name = "content tag"
        verbose_name_plural = "content tags"


class PostTagItem(ItemBase):

    class Meta:
        unique_together = (('content_object', 'tag'),)

    tag = django_models.ForeignKey(
        PostTag, related_name="tagged_post", on_delete=django_models.CASCADE
    )

    content_object = ParentalKey(
        to=APP_LABEL + '.Post',
        on_delete=django_models.CASCADE,
        related_name='tagged_items'
    )


def create_post_tag(*, tag, content_object):
    return PostTagItem(tag=tag, content_object_id=content_object.id)


def text_from_rich_text(rich_text):
    return html_to_text(rich_text.source)


SENTENCE_RE = re.compile(r'\.[ \t\n\r]+[A-Z]')


def extract_post_content_text(content):

    for stream_child in content:
        if stream_child.block_type != 'text':
            continue

        text = text_from_rich_text(stream_child.value)
        match = SENTENCE_RE.search(text)

        if match:
            text = text[:match.start() + 1]

        return text

    return ''


class AbstractPost(WagtailPageMixin, TranslatableMixin,
                   DraftStateMixin, RevisionMixin, AnchorRegistry, PreviewableMixin, Servable):

    class Meta:
        abstract = True
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    template = APP_LABEL + "/post_page.html"

    preview_template = APP_LABEL + "/post_page.html"
    ajax_preview_template = None

    RECORD_BLOCK = PostBlock(label="Post")

    year = django_models.PositiveIntegerField(default=0, editable=False, blank=False, null=False)
    month = django_models.PositiveSmallIntegerField(default=0, editable=False, blank=False, null=False)
    day = django_models.PositiveSmallIntegerField(default=0, editable=False, blank=False, null=False)

    category = DynamicChoiceField(max_length=128, validators=[validate_category], default='',
                                  blank=False, null=False,
                                  choices_function_name=APP_LABEL + ".categories.get_post_category_choices")

    live = django_models.BooleanField(verbose_name=_("live"), default=False, editable=True)

    created_by_user = django_models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('created by user'),
        null=True,
        blank=True,
        editable=False,
        on_delete=django_models.SET_NULL
    )

    slug = django_models.SlugField(
        verbose_name=_("slug"),
        allow_unicode=True,
        max_length=255,
        help_text=_(
            "The name of the post as it will appear in URLs"
        )
    )

    content = PostContentField(
                blank=True,
                help_text=
                "A content of the contents of this content.")

    tags = ClusterTaggableManager(through=APP_LABEL + '.PostTagItem', blank=True)

    content_panels = [
        FieldPanel('category', heading="Category"),
        FieldPanel('live', heading="Is Live?"),
        InlinePanel('authors', heading="Authors"),
        FieldPanel('tags', heading="Tags"),
        FieldPanel('content', heading="Post"),
    ]

    @cached_property
    def author_names(self):

        authors = [author.author.specific for author in self.authors.all()] # noqa
        authors = [author for author in authors if author]
        value = self.RECORD_BLOCK.child_blocks['authors'].value_from_group_members(authors) # noqa
        result = self.RECORD_BLOCK.child_blocks['authors'].render(value)
        return result

    @property
    def post_synopsis(self):

        if self.synopsis and self.synopsis.count() > 0: # noqa
            return self.synopsis.first() # noqa

        return None

    @property
    def as_block_value(self):
        return self.RECORD_BLOCK.value_for_post(self)

    def get_context(self, request):

        context = super().get_context(request)

        env = {
            'request': request,
            'page': None
        }

        reset_variable_scopes(env)

        load_variable_scope("tour_guide", anchor_registry=self)

        preferences_context = getattr(self, 'preferences_context', None)

        context.update({
            'post': self,
            'page_template': settings.BE_BRIEF_POST_PAGE_TEMPLATE,
            'preferences': preferences_context,
        })

        return context

    def get_preview_context(self, request, mode_name):

        context = super(AbstractPost, self).get_preview_context(request, mode_name)

        context.update(
            self.get_context(request)
        )

        return context

    def get_preview_template(self, request, mode_name):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax_preview_template or self.preview_template
        else:
            return self.preview_template

    def render(self, request):

        template = self.get_template(request)
        context = self.get_context(request)

        result = render_to_string(template, context=context, request=request)
        return result

    def sync_synopsis(self, synopsis):

        synopsis.category = self.category

        synopsis.rubric = ''
        synopsis.rubric_url = ''

        if not synopsis.summary:
            synopsis.summary = RichText(extract_post_content_text(self.content)) # noqa

        authors = [author.author.specific for author in self.authors.all()] # noqa
        authors = [author for author in authors if author]
        value = self.RECORD_BLOCK.child_blocks['authors'].json_from_group_members(authors) # noqa
        value['role'] = AUTHOR_ROLE

        synopsis.names = value

    def determine_url(self, request, current_site=None):
        return ''

    def __str__(self):
        category = lookup_post_category(self.category)
        category = category.name if category else self.category

        if self.first_published_at:
            result = f'[{category}] {self.title} ({self.year:d}/{self.month:d}/{self.day:d})' # noqa
        else:
            result = f'[{category}] {self.title} (Unpublished)' # noqa

        return result


@provides_preferences_context
class Post(AbstractPost, modelcluster.models.ClusterableModel):

    class Meta:
        unique_together = [("slug", "locale"), ("translation_key", "locale")]

    title = django_models.CharField(
        verbose_name=_("title"),
        max_length=255,
        help_text=_("The content title as you'd like it to be seen by the public"),
    )

    seo_title = django_models.CharField(
        verbose_name=_("title tag"),
        max_length=255,
        blank=True,
        help_text=_(
            "The name of the page displayed on search engine results as the clickable headline."
        ),
    )

    search_description = django_models.TextField(
        verbose_name=_("meta content"),
        blank=True,
        help_text=_(
            "The descriptive text displayed underneath a headline in search engine results."
        ),
    )

    content_panels = [
        FieldPanel('title', heading="Title", classname="title"),
        FieldPanel('slug', heading="Slug"),
        FieldPanel('tags', heading="Tags")
    ] + AbstractPost.content_panels

    promote_panels = [
        FieldPanel('seo_title'),
        FieldPanel('search_description')
    ]

    def full_clean(self, *args, **kwargs):

        # Set the locale
        if self.locale_id is None:
            self.locale = self.get_default_locale()

        super().full_clean(*args, **kwargs)

    def clean(self):
        super().clean()

        queryset = Post.objects.all().filter(year=self.year, month=self.month, day=self.day, slug=self.slug)

        if self.id:
            queryset = queryset.exclude(id=self.id)

        if queryset.exists():
            raise ValidationError({"slug": _("This slug is already in use")})

    @transaction.atomic
    def save(self, update_fields=None, clean=True, **kwargs):

        did_update_fields = False

        if self.first_published_at:
            self.year = self.first_published_at.year
            self.month = self.first_published_at.month
            self.day = self.first_published_at.day
            did_update_fields = True

        if clean:
            self.full_clean()

        if update_fields is not None and did_update_fields:
            update_fields_index = frozenset(update_fields)

            if 'year' not in update_fields_index:
                update_fields.append('year')

            if 'month' not in update_fields_index:
                update_fields.append('month')

            if 'day' not in update_fields_index:
                update_fields.append('day')

        super().save(update_fields=update_fields, **kwargs)

    def sync_synopsis(self, synopsis):
        super(Post, self).sync_synopsis(synopsis)

        synopsis.heading = self.title
        synopsis.created_at = self.first_published_at or timezone.now()
        synopsis.updated_at = self.last_published_at

    def determine_url(self, request, current_site=None):

        if current_site is None:
            current_site = Site.find_for_request(request)

        if current_site is None:
            current_site = Site.objects.get(is_default_site=True)

        site_settings = BeBriefSiteSettings.for_site(current_site)

        index_pages = site_settings.post_category_index_pages.all().filter(category=self.category)

        if index_pages.count() != 1 or not self.first_published_at:
            return ''

        canonical_index_page = index_pages.first().canonical_index_page

        result = canonical_index_page.get_url(request=request, current_site=current_site)
        result = f"{result}{self.first_published_at.year}/{self.first_published_at.month}/{self.first_published_at.day}/{self.slug}/"
        return result

    _edit_handler = None

    @classproperty
    def edit_handler(cls):

        if cls._edit_handler:
            return cls._edit_handler

        tabs = []

        if cls.content_panels:
            tabs.append(ObjectList(cls.content_panels, heading=_("Content")))

        synopsis_adapter = PostSynopsis.install_synopsis_adapter_for(
            editable_fields=['summary', 'visual'],
            sync_method=Post.sync_synopsis,
            tagged_item_class=PostTagItem,
            tags_field='tags',
            tagged_items_field='tagged_items'
        )

        tabs.append(synopsis_adapter.create_synopsis_panel_for(cls))

        if cls.promote_panels:
            tabs.append(ObjectList(cls.promote_panels, heading=_("Promote")))

        edit_handler = TabbedInterface(tabs)

        bound_handler = edit_handler.bind_to_model(cls)
        cls._edit_handler = bound_handler
        return bound_handler


Post = register_snippet(Post, viewset=PostViewSet)


class PostAuthor(Orderable):

    class Meta(Orderable.Meta):
        verbose_name = 'Author in Post'
        verbose_name_plural = 'Authors in Post'
        unique_together = (('author', 'post'),)

    post = ParentalKey(Post, related_name="authors", on_delete=django_models.CASCADE, blank=False)
    author = ForeignKey(GroupMember, related_name="posts", on_delete=django_models.CASCADE, blank=False)

    panels = [
        FieldPanel('post'),
        FieldPanel('author'),
    ]

    def __str__(self):
        author = self.author.specific # noqa

        if isinstance(author, Person):
            name = author.full_name
        elif isinstance(author, Organisation):
            name = author.name
        else:
            name = '[unknown group member type]'

        return f"{name} in {self.post.title}" # noqa


PostSynopsis = build_synopsis_class_for(Post)


@chooses_navigation_categories
class PostIndexPage(RoutablePageMixin, AnchorRegistry, Page):

    class Meta:
        verbose_name = "Post Index Page"
        verbose_name_plural = "Post Index Pages"

    default_redirect_target = settings.BE_BRIEF_POST_INDEX_REDIRECT_TARGET

    template = django_models.CharField(max_length=128, verbose_name="Template Path", blank=True, null=True,
                                       validators=(validate_file_name,))

    category = DynamicChoiceField(max_length=128, validators=[validate_category], default='',
                                  blank=False, null=False,
                                  choices_function_name=APP_LABEL + ".categories.get_post_category_choices")

    content_panels = Page.content_panels + [
        FieldPanel('template'),
        FieldPanel('category')
    ]

    @property
    def applicable_template(self):
        result = self.template if self.template else "/" + APP_LABEL + "/post_index_page.html"

        if result.startswith("/"):
            result = result[1:]

        return result

    def get_template(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax_template or self.applicable_template
        else:
            return self.applicable_template

    @path('')
    def default_view(self, request):

        if self.default_redirect_target:
            return redirect(self.default_redirect_target, permanent=False)

        if settings.BE_BRIEF_POST_INDEX_NOT_ACCESSIBLE:
            raise Http404('Not found.')

        return self.index_route(request)

    @path('<int:year>/<int:month>/<int:day>/<str:slug>/')
    def serve_post(self, request, year, month, day, slug):

        language = get_language_from_request(request)

        try:
            locale = Locale.objects.get_for_language(language)
        except Locale.DoesNotExist:
            locale = Locale.get_active()

        try:
            post = Post.objects.get(live=True,
                                    first_published_at__year=year, first_published_at__month=month,
                                    first_published_at__day=day, slug__iexact=slug, locale_id=locale.id)

        except Post.DoesNotExist:

            try:
                locale = Locale.objects.get_for_language('en')
            except Locale.DoesNotExist:
                locale = None

            posts = Post.objects.filter(live=True,
                                        first_published_at__year=year, first_published_at__month=month,
                                        first_published_at__day=day, slug__iexact=slug, locale_id=locale.id).order_by(
                'locale__language_code')

            if not posts.exists():
                raise Http404('Not found.')

            post = posts.first()

        return post.serve(request)
