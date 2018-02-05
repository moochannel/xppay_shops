from django import template

from shops.models import Benefit

register = template.Library()


@register.filter
def state_label(state):
    return Benefit.get_state_display(state)
