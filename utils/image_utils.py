"""
utils/image_utils.py
====================
Helper umum untuk operasi gambar:
- Resize gambar
- Konversi mode warna
- Preview metadata
"""

import os
from PIL import Image


def resize_image(img_path, output_path, max_width=None, max_height=None, keep_aspect=True):
    """
    Resize gambar dengan menjaga aspect ratio (opsional).

    Parameters:
        img_path    : path input
        output_path : path output
        max_width   : lebar maksimum (pixel)
        max_height  : tinggi maksimum (pixel)
        keep_aspect : pertahankan rasio aspek
    """
    try:
        img = Image.open(img_path)
        w, h = img.size

        if keep_aspect:
            if max_width and max_height:
                img.thumbnail((max_width, max_height), Image.LANCZOS)
            elif max_width:
                ratio = max_width / w
                img = img.resize((max_width, int(h * ratio)), Image.LANCZOS)
            elif max_height:
                ratio = max_height / h
                img = img.resize((int(w * ratio), max_height), Image.LANCZOS)
        else:
            new_w = max_width or w
            new_h = max_height or h
            img = img.resize((new_w, new_h), Image.LANCZOS)

        img.save(output_path)
        return {"success": True, "new_size": img.size}

    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_format(img_path, output_path):
    """
    Konversi format gambar (mis. PNG ke JPEG, BMP ke PNG, dll).
    Format output ditentukan dari ekstensi output_path.
    """
    try:
        img = Image.open(img_path)
        ext = os.path.splitext(output_path)[1].lower()

        if ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        img.save(output_path)
        return {"success": True, "output_path": output_path}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_dominant_color(img_path, n=1):
    """
    Dapatkan warna dominan dari gambar.
    Berguna untuk menentukan warna watermark yang kontras.
    """
    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize((50, 50))  # Resize kecil untuk kecepatan

        pixels = list(img.getdata())
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)

        brightness = (avg_r * 299 + avg_g * 587 + avg_b * 114) / 1000

        return {
            "success": True,
            "avg_color": (avg_r, avg_g, avg_b),
            "brightness": brightness,
            # Warna watermark yang disarankan berdasarkan brightness
            "suggested_watermark_color": (255, 255, 255) if brightness < 128 else (0, 0, 0)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
