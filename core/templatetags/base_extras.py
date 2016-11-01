from django import template
from core.models import Permission

register = template.Library()


@register.filter
def build_absolute_uri(request, url):
    return request.build_absolute_uri(url)


@register.filter
def can_edit(request, file):
    return file.has_permission(request.user, Permission.CATEGORIES.edit)


@register.filter
def can_share(request, file):
    return file.can_share(request.user)
