from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def time_since(value):
    if not value:
        return ""

    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    elif seconds < 172800:
        return "yesterday"
    else:
        return f"{int(seconds // 86400)} days ago"