import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITAL = re.compile(r"\*(.+?)\*", re.S)


@register.filter
def rich(value):
    """Escape, then allow **bold**, *italic* and line breaks."""
    if not value:
        return ""
    out = escape(str(value).strip())
    out = _BOLD.sub(r"<b>\1</b>", out)
    out = _ITAL.sub(r"<i>\1</i>", out)
    out = out.replace("\r\n", "\n").replace("\n", "<br>")
    return mark_safe(out)


@register.filter
def repeat_text(value, times=12):
    """Repeat the ticker text so the CSS marquee never shows a gap."""
    if not value:
        return ""
    return mark_safe((escape(value) + " &nbsp; ") * int(times))


@register.filter
def video_embed(url):
    """Turn a YouTube / Vimeo watch link into an embeddable URL ('' if not recognised)."""
    if not url:
        return ""
    m = re.search(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{6,})", url)
    if m:
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
    m = re.search(r"vimeo\.com/(?:video/)?(\d+)", url)
    if m:
        return f"https://player.vimeo.com/video/{m.group(1)}"
    return ""


@register.filter
def by_slot(items, slot):
    return [i for i in items if i.slot == slot]


@register.filter
def not_slot(items, slot):
    return [i for i in items if i.slot != slot]


@register.filter
def nth(items, index):
    try:
        return items[int(index)]
    except (IndexError, ValueError, TypeError):
        return None
