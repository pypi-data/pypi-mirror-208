
from django.utils.text import slugify


def define_tags(*, tag_values, tag_class, tag_item_class, context):

    tags = []

    for value in tag_values:
        try:
            tag = tag_class.objects.get(name=value)
        except tag_class.DoesNotExist:
            slug = slugify(value)
            tag = tag_class(name=value, slug=slug)
            tag.save()

        tags.append(tag)

    result = []

    for tag in tags:
        tagged_item = tag_item_class(tag=tag, content_object_id=None)
        result.append(tagged_item)

    return result

