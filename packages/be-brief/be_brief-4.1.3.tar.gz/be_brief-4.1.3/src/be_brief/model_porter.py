
from model_porter.config import ModelPorterConfig
from model_porter.utilities import define_tags as define_generic_tags

from officekit.models import GroupMember

from .models import PostAuthor, PostTag, PostTagItem


def link_authors(*, identifiers, context):

    record = context.get_variable(context.INSTANCE_VARIABLE)
    result = []

    for identifier in identifiers:
        author = GroupMember.objects.get(identifier=identifier)

        if author is None:
            continue

        by = PostAuthor()
        by.post = record
        by.author_id = author.id

        result.append(by)

    return result


def define_tags(*, tag_values, context):
    return define_generic_tags(tag_values=tag_values, tag_class=PostTag, tag_item_class=PostTagItem, context=context)


def publish_post(*, instance, context):
    instance.save()
    revision = instance.save_revision(log_action=False)
    revision.publish()
    instance.refresh_from_db()
    return instance


class BeBriefConfig(ModelPorterConfig):

    def __init__(self, app_label, module):
        super(BeBriefConfig, self).__init__(app_label, module)
        self.register_function_action(link_authors, context_argument='context')
        self.register_function_action(define_tags, context_argument='context')
        self.register_function_action(publish_post, context_argument='context')
