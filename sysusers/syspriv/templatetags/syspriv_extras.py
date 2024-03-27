from django import template
from .. import models

register = template.Library()

@register.filter
def get_system_object(id, var):
    try:
        s = models.System.objects.get(id=id.value)
        if var == 'db_type':
            for choice in models.System.db_type_choices:
                if choice[0] == getattr(s, var):
                    return choice[1]
        else:
            return getattr(s, var)
    except:
        return ''

@register.filter
def get_role_object(id, var):
    try:
        s = models.Role.objects.get(id=id.value)
        return getattr(s, var)
    except:
        return ''

@register.filter
def has_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False

