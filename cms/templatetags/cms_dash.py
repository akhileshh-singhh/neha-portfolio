from django import template
from django.contrib.admin.models import LogEntry

from cms.models import Asset, Inquiry, Page, Section

register = template.Library()


@register.simple_tag
def dash_stats():
    return {
        "blocks": Section.objects.count(),
        "visible": Section.objects.filter(visible=True).count(),
        "pages": Page.objects.count(),
        "assets": Asset.objects.count(),
        "messages": Inquiry.objects.count(),
        "unread": Inquiry.objects.filter(is_read=False).count(),
        "db_empty": not Page.objects.exists(),
    }


@register.simple_tag
def recent_edits(limit=8):
    return list(LogEntry.objects.select_related("content_type", "user")[:limit])
