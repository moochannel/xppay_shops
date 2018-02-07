import base64
from io import BytesIO

from django import template
from django.contrib.staticfiles import finders
from PIL import Image

from shops.models import Benefit

register = template.Library()


@register.filter
def state_label(state):
    return Benefit.get_state_display(state)


@register.simple_tag
def b64encode_image(image_path):
    physical_path = finders.find(image_path)
    if not physical_path:
        return None

    encoded = None
    pil_image = Image.open(physical_path)
    with BytesIO() as buffer:
        pil_image.save(buffer, 'PNG')
        encoded = base64.b64encode(buffer.getvalue())

    return f'data:image/png;base64,{encoded.decode()}'
