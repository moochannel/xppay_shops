from django import template
from django.contrib.staticfiles import finders
from django.utils.html import format_html
from PIL import Image

from shops.models import Benefit, ShopApproval
from shops.utils import image_to_b64

register = template.Library()


@register.filter
def state_label(state):
    return Benefit.get_state_display(state)


@register.simple_tag
def b64encode_image(image_path):
    physical_path = finders.find(image_path)
    if not physical_path:
        return None

    return image_to_b64(Image.open(physical_path))


@register.simple_tag
def unapproved_shops_badge():
    unapproved_num = ShopApproval.unapproved_count()
    if unapproved_num > 0:
        return format_html('<span class="new badge">{}</span>', unapproved_num)
    else:
        return ''
