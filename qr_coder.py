# qr_coder.py
import qrcode
from PIL import Image, ImageDraw

def generate_qr(data, qr_color, bg_color, logo_path, logo_percent):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color=qr_color,
        back_color=bg_color
    ).convert("RGB")

    if logo_path:
        qr_img = add_logo(qr_img, logo_path, logo_percent)

    return qr_img


def add_logo(qr_img, logo_path, percent):
    logo = Image.open(logo_path).convert("RGBA")
    qr_w, _ = qr_img.size

    logo_size = int(qr_w * (percent / 100))
    padding = 12
    box_size = logo_size + padding * 2

    logo.thumbnail((logo_size, logo_size))

    box = Image.new("RGBA", (box_size, box_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(box)
    draw.rounded_rectangle(
        (0, 0, box_size, box_size),
        radius=18,
        fill="white"
    )

    box.paste(
        logo,
        ((box_size - logo.width) // 2, (box_size - logo.height) // 2),
        logo
    )

    pos = ((qr_w - box_size) // 2, (qr_w - box_size) // 2)
    qr_img.paste(box, pos, box)

    return qr_img
