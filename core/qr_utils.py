
import qrcode

from io import BytesIO
from django.core.files.base import ContentFile


def generate_prescription_qr(prescription):

    verification_url = (
        f"http://127.0.0.1:8000/verify-prescription/"
        f"{prescription.verification_token}/"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(verification_url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")

    return ContentFile(image_buffer.getvalue())
