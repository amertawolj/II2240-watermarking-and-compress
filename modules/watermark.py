"""
modules/watermark.py
====================
Modul untuk semua operasi watermarking:
- Watermark teks (visible)
- Watermark logo/gambar (visible)
- Invisible watermark menggunakan LSB (Least Significant Bit)
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from utils.file_handler import FileHandler


class WatermarkModule:
    def __init__(self):
        self.fh = FileHandler()

    # =========================================================
    # HELPER: Hitung posisi berdasarkan nama posisi
    # =========================================================
    def _get_position(self, base_size, element_size, position="center", margin=20):
        """
        Hitung koordinat (x, y) berdasarkan posisi yang diminta.
        base_size    : (width, height) gambar utama
        element_size : (width, height) elemen yang akan ditempatkan
        """
        bw, bh = base_size
        ew, eh = element_size

        positions = {
            "center":      ((bw - ew) // 2, (bh - eh) // 2),
            "topleft":     (margin, margin),
            "topright":    (bw - ew - margin, margin),
            "bottomleft":  (margin, bh - eh - margin),
            "bottomright": (bw - ew - margin, bh - eh - margin),
        }
        return positions.get(position, positions["center"])

    # =========================================================
    # 1. WATERMARK TEKS (Visible)
    # =========================================================
    def add_text_watermark(self, img_path, text, output_path,
                           opacity=0.5, position="center",
                           font_size=None, color=(255, 255, 255)):
        """
        Sisipkan watermark teks ke gambar.

        Parameters:
            img_path    : path gambar input
            text        : teks yang akan dijadikan watermark
            output_path : path output
            opacity     : transparansi teks (0.0 - 1.0)
            position    : posisi teks
            font_size   : ukuran font (auto jika None)
            color       : warna teks dalam RGB
        """
        try:
            # Buka gambar asli
            base_img = Image.open(img_path).convert("RGBA")
            bw, bh = base_img.size

            # Auto font size: 5% dari lebar gambar
            if font_size is None:
                font_size = max(20, int(bw * 0.05))

            # Buat layer transparan untuk teks
            txt_layer = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            # Coba pakai font sistem, fallback ke default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            # Ukuran teks
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            # Posisi teks
            x, y = self._get_position((bw, bh), (text_w, text_h), position)

            # Alpha dari opacity
            alpha = int(255 * opacity)
            rgba_color = color + (alpha,)

            # Gambar teks
            draw.text((x, y), text, font=font, fill=rgba_color)

            # Gabungkan layer
            watermarked = Image.alpha_composite(base_img, txt_layer)

            # Simpan (convert ke RGB jika output JPEG)
            ext = os.path.splitext(output_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                watermarked = watermarked.convert("RGB")

            watermarked.save(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "file_size": self.fh.format_file_size(os.path.getsize(output_path))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 2. WATERMARK LOGO (Visible)
    # =========================================================
    def add_logo_watermark(self, img_path, logo_path, output_path,
                           opacity=0.4, scale=0.2, position="bottomright"):
        """
        Sisipkan watermark berupa logo/gambar ke gambar.

        Parameters:
            img_path    : path gambar utama
            logo_path   : path logo/gambar watermark
            output_path : path output
            opacity     : transparansi logo (0.0 - 1.0)
            scale       : skala logo relatif terhadap gambar utama (0.1 - 0.5)
            position    : posisi logo
        """
        try:
            # Buka gambar utama dan logo
            base_img = Image.open(img_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")

            bw, bh = base_img.size

            # Resize logo sesuai skala
            logo_w = int(bw * scale)
            logo_h = int(logo.height * (logo_w / logo.width))
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

            # Sesuaikan opacity logo
            r, g, b, a = logo.split()
            a = a.point(lambda i: int(i * opacity))
            logo.putalpha(a)

            # Posisi logo
            x, y = self._get_position((bw, bh), (logo_w, logo_h), position)

            # Tempel logo ke layer transparan
            txt_layer = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            txt_layer.paste(logo, (x, y), logo)

            # Gabungkan
            watermarked = Image.alpha_composite(base_img, txt_layer)

            # Simpan
            ext = os.path.splitext(output_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                watermarked = watermarked.convert("RGB")

            watermarked.save(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "file_size": self.fh.format_file_size(os.path.getsize(output_path))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 3. INVISIBLE WATERMARK - Embed (LSB Steganography)
    # =========================================================
    def embed_invisible_watermark(self, img_path, message, output_path):
        """
        Sisipkan pesan tersembunyi ke gambar menggunakan LSB.
        Gambar output HARUS disimpan sebagai PNG agar data tidak rusak.

        Cara kerja:
        - Setiap karakter pesan dikonversi ke 8-bit binary
        - Setiap bit disimpan di bit paling kecil (LSB) dari channel merah pixel
        - Perubahan warna hampir tidak terdeteksi mata (max 1 nilai dari 0-255)
        """
        try:
            img = Image.open(img_path).convert("RGB")
            pixels = np.array(img, dtype=np.uint8)

            # Tambahkan delimiter akhir pesan
            message_with_end = message + "<<<END>>>"

            # Konversi pesan ke bit
            bits = []
            for char in message_with_end:
                bits.extend([int(b) for b in format(ord(char), '08b')])

            total_bits = len(bits)
            total_pixels = pixels.shape[0] * pixels.shape[1]

            if total_bits > total_pixels:
                return {
                    "success": False,
                    "error": f"Pesan terlalu panjang. Maksimal {total_pixels // 8 - 10} karakter untuk gambar ini."
                }

            # Sisipkan bit ke LSB channel merah
            flat_red = pixels[:, :, 0].flatten().copy()

            for i, bit in enumerate(bits):
                flat_red[i] = (flat_red[i] & 0xFE) | bit  # Set LSB

            pixels[:, :, 0] = flat_red.reshape(pixels.shape[0], pixels.shape[1])

            # Simpan sebagai PNG (wajib, JPEG akan merusak LSB)
            result_img = Image.fromarray(pixels)
            result_img.save(output_path, format="PNG")

            return {
                "success": True,
                "output_path": output_path,
                "bits_used": total_bits,
                "file_size": self.fh.format_file_size(os.path.getsize(output_path))
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 4. INVISIBLE WATERMARK - Extract (LSB)
    # =========================================================
    def extract_invisible_watermark(self, img_path):
        """
        Ekstrak pesan tersembunyi dari gambar yang sudah di-watermark dengan LSB.
        """
        try:
            img = Image.open(img_path).convert("RGB")
            pixels = np.array(img, dtype=np.uint8)

            # Ambil LSB dari channel merah
            flat_red = pixels[:, :, 0].flatten()
            bits = [int(pixel & 1) for pixel in flat_red]

            # Rekonstruksi karakter dari bit
            chars = []
            for i in range(0, len(bits) - 7, 8):
                byte = bits[i:i+8]
                char_code = int("".join(str(b) for b in byte), 2)
                if char_code == 0:
                    break
                chars.append(chr(char_code))

                # Cek apakah sudah ketemu delimiter
                joined = "".join(chars)
                if joined.endswith("<<<END>>>"):
                    message = joined[:-9]  # Hapus delimiter
                    return {"success": True, "message": message}

            return {
                "success": False,
                "error": "Tidak ditemukan watermark tersembunyi dalam gambar ini."
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
