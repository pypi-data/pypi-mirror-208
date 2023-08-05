
from django.conf import settings

from wagtail import blocks
from wagtail_dynamic_stream_block.blocks import DynamicStreamBlock
from wagtail_switch_block.block_registry import BlockRegistry

from wagtail_tags_block.blocks import TagsBlock, TagsValue

from officekit.blocks import NameListBlock

from .apps import get_app_label


__all__ = ['PostContentBlock', 'PostContentValue', 'PostTagsBlock', 'PostTagsBlockValue',
           'PostBlock', 'PostBlockValue',
           'POST_BLOCK_REGISTRY', 'register_post_block', 'post_block_choices' # noqa
           'BaseResourceBlock']

APP_LABEL = get_app_label()


class PostBlockRegistry(BlockRegistry):

    # noinspection PyMethodMayBeStatic
    def should_register_block(self, app_label, local_identifier, block_type, block_args, block_kwargs, **kwargs):
        return True

    # noinspection PyMethodMayBeStatic
    def should_include_entry_for_switch_block(self, identifier, entry, switch_block):
        return True

    # noinspection PyMethodMayBeStatic
    def instantiate_block(self, identifier, entry, switch_block):

        block_kwargs = dict(entry.block_kwargs)
        block = entry.block_type(*entry.block_args, **block_kwargs)
        block.set_name(identifier)

        return block


POST_BLOCK_REGISTRY = PostBlockRegistry()
POST_BLOCK_REGISTRY.define_procedures_in_caller_module("post")


PostContentValue = blocks.StreamValue


class PostContentBlock(DynamicStreamBlock):

    class Meta:
        icon = 'form'
        default = []
        template = APP_LABEL + '/blocks/post_content_stream.html'

    def __init__(self, **kwargs):
        super().__init__(child_blocks_function_name=APP_LABEL + ".blocks.post_block_choices", **kwargs)


PostTagsBlockValue = TagsValue


class PostTagsBlock(TagsBlock):

    class Meta:
        template = APP_LABEL + '/blocks/post_tags_block.html'
        tag_model = APP_LABEL + ".posttag"

        classname = settings.BE_BRIEF_POST_TAGS_BLOCK_CLASSNAME
        tag_classname = settings.BE_BRIEF_POST_TAGS_BLOCK_TAG_CLASSNAME
        container_element = settings.BE_BRIEF_POST_TAGS_BLOCK_CONTAINER_ELEMENT


PostDatesBlockValue = blocks.StructValue


class PostDatesBlock(blocks.StructBlock):

    class Meta:
        template = APP_LABEL + '/blocks/post_dates_block.html'

    first_published_at = blocks.DateBlock(label="First Published", required=False, default={})
    last_published_at = blocks.DateBlock(label="Last Published", required=False, default={})


PostBlockValue = blocks.StructValue


class PostBlock(blocks.StructBlock):

    class Meta:
        classname = settings.BE_BRIEF_RECORD_BLOCK_CLASSNAME
        template = APP_LABEL + '/blocks/post_block.html'

    post = blocks.StaticBlock() # placeholder

    title = blocks.CharBlock(required=False)
    dates = PostDatesBlock(required=False)

    authors = NameListBlock(required=False, classname=settings.BE_BRIEF_RECORD_BLOCK_AUTHORS_CLASSNAME,
                            container_element="ol", template=APP_LABEL + "/blocks/post_authors_block.html")

    tags = PostTagsBlock(required=False)
    content = PostContentBlock(required=False)

    def deconstruct(self):
        path, args, kwargs = blocks.Block.deconstruct(self)
        return path, args, kwargs

    def value_for_post(self, post):

        authors = self.child_blocks['authors'].value_from_group_members(
            [assignment.author for assignment in post.authors.all()])

        tags = [tag.name for tag in post.tags.all()]
        tags = self.child_blocks['tags'].to_python(tags)

        dates = {
            "first_published_at": post.first_published_at,
            "last_published_at": post.last_published_at
        }

        dates = self.child_blocks['dates'].to_python(dates)

        value = blocks.StructValue(self, {
            "post": post,
            "title": post.title,
            "dates": dates,
            "authors": authors,
            "tags": tags,
            "content": post.content
        })

        return value
