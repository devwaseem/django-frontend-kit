from typing import cast

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from frontend_kit.manifest import AssetTag
from frontend_kit.page import Page


class PageContextNotFoundError(Exception):
    def __init__(self, message: str = "Page not found in context") -> None:
        super().__init__(message)


register = template.Library()


def _get_csp_nonce(context: template.Context) -> str | None:
    if not getattr(settings, "DJFK_DEV_ENV", True):
        return None
    request = context.get("request")
    if not request:
        return None
    return getattr(request, "csp_nonce", None)


@register.simple_tag(takes_context=True)
def fk_stylesheets(context: template.Context) -> str:
    if "page" not in context:
        raise PageContextNotFoundError

    page = cast(Page, context["page"])
    nonce = _get_csp_nonce(context)
    return mark_safe(
        "\n".join([tag.render(nonce=nonce) for tag in page.stylesheets])
    )


@register.simple_tag(takes_context=True)
def fk_preloads(context: template.Context) -> str:
    if "page" not in context:
        raise PageContextNotFoundError

    page = cast(Page, context["page"])
    return mark_safe("\n".join([tag.render() for tag in page.preload_imports]))


@register.simple_tag(takes_context=True)
def fk_head_scripts(context: template.Context) -> str:
    if "page" not in context:
        raise PageContextNotFoundError

    page = cast(Page, context["page"])
    nonce = _get_csp_nonce(context)
    return mark_safe(
        "\n".join([tag.render(nonce=nonce) for tag in page.head_imports])
    )


@register.simple_tag(takes_context=True)
def fk_body_scripts(context: template.Context) -> str:
    if "page" not in context:
        raise PageContextNotFoundError

    page = cast(Page, context["page"])
    nonce = _get_csp_nonce(context)
    return mark_safe(
        "\n".join([tag.render(nonce=nonce) for tag in page.body_imports])
    )


@register.simple_tag(takes_context=True)
def fk_custom_entry(context: template.Context, name: str) -> str:
    if "page" not in context:
        raise PageContextNotFoundError

    page = cast(Page, context["page"])
    nonce = _get_csp_nonce(context)
    files = [name + ".entry.js", name + ".entry.ts"]
    asset_tags: list[AssetTag] = []
    for file in files:
        try:
            tags = page.resolve_import(file_name=file)
        except FileNotFoundError:
            continue
        asset_tags.extend(list(tags))

    if not asset_tags:
        raise FileNotFoundError(
            f"Could not find entry file '{name}'. "
            f"Looked for files: {', '.join(files)}"
        )

    return mark_safe(
        "\n".join([tag.render(nonce=nonce) for tag in asset_tags])
    )
