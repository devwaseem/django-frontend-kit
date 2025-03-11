from django import template
from django.utils.safestring import mark_safe

from frontend_kit.manifest import AssetTag

register = template.Library()

@register.simple_tag
def fk_load(tags: list[AssetTag]) -> str:
    return mark_safe("\n".join([
        tag.render()
        for tag in tags
    ]))