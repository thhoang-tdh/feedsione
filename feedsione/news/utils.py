import re
from django.template.defaultfilters import slugify
import shortuuid


def unique_slug_generator(instance, name='default-slug'):
    """
    This is slug generator, assumming instance is a model
    with a slug field.
    return: slug, with default max length of 255
    """
    Kclass = instance.__class__
    slug = "{shortuuid}-{slug}".format(
                shortuuid=shortuuid.ShortUUID().random(length=22),
                slug=slugify(name))
    slug = slug[:255]
    qs_exists = Kclass.objects.filter(slug=slug).exists()
    if qs_exists:
        return unique_slug_generator(instance, name)
    else:
        return slug