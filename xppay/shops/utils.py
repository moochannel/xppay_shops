import base64
from io import BytesIO

import qrcode
from django.contrib.staticfiles import finders
from PIL import Image


def make_qrcode_for_pdf(embeded_string, box_size=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        border=1,
        box_size=box_size,
    )
    qr.add_data(embeded_string)
    qr.make(fit=True)

    qr_image = qr.make_image().convert('RGBA')
    logo_path = finders.find('shops/XPpay_on_qrcode.png')
    logo_image = Image.open(logo_path)
    qr_image.paste(
        logo_image, (
            int((qr_image.width - logo_image.width) / 2),
            int((qr_image.height - logo_image.height) / 2)
        )
    )

    return image_to_b64(qr_image)


def image_to_b64(pil_image):
    encoded = None
    with BytesIO() as buffer:
        pil_image.save(buffer, 'PNG')
        encoded = base64.b64encode(buffer.getvalue())

    return f'data:image/png;base64,{encoded.decode()}'
