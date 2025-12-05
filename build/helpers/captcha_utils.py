from flask import session, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import string


def generate_captcha():
    # Simple 5-character CAPTCHA
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['captcha'] = captcha_text  # store in session

    # Create image
    img = Image.new('RGB', (120, 40), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Use a simple font; system default or provide path
    try:
        font = ImageFont.truetype("arial.ttf", 25)
    except:
        font = ImageFont.load_default()

    d.text((20, 3), captcha_text, fill=(0, 0, 0), font=font)

    # Save image to memory
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
