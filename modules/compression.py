"""
modules/compression.py
======================
Modul untuk semua operasi kompresi gambar:
- Kompresi JPEG (lossy) dengan kontrol kualitas
- Kompresi PNG (lossless) dengan kontrol level
- Kompresi batch (banyak file sekaligus)
- Info gambar & estimasi kompresi
"""

import os
from PIL import Image
from utils.file_handler import FileHandler


class CompressionModule:
    def __init__(self):
        self.fh = FileHandler()
        self.supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]

    # =========================================================
    # 1. KOMPRESI JPEG (Lossy)
    # =========================================================
    def compress_jpeg(self, img_path, output_path, quality=75):
        """
        Kompres gambar menjadi JPEG dengan kualitas tertentu.

        Parameters:
            img_path    : path gambar input
            output_path : path output (.jpg)
            quality     : kualitas 1-95 (semakin rendah = file lebih kecil, kualitas turun)
                          Rekomendasi: 75-85 untuk keseimbangan baik
        """
        try:
            original_size = os.path.getsize(img_path)

            img = Image.open(img_path)

            # Konversi ke RGB jika perlu (JPEG tidak support alpha)
            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Simpan dengan kualitas tertentu
            img.save(output_path, format="JPEG", quality=quality, optimize=True)

            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100

            return {
                "success": True,
                "output_path": output_path,
                "original_size": self.fh.format_file_size(original_size),
                "compressed_size": self.fh.format_file_size(compressed_size),
                "ratio": f"{ratio:.1f}% lebih kecil",
                "quality": quality
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 2. KOMPRESI PNG (Lossless)
    # =========================================================
    def compress_png(self, img_path, output_path, compress_level=6):
        """
        Kompres gambar menjadi PNG lossless.
        PNG tidak mengurangi kualitas visual, tapi pengurangan ukuran lebih terbatas.

        Parameters:
            img_path       : path gambar input
            output_path    : path output (.png)
            compress_level : level kompresi 0-9 (0=tidak kompres, 9=maksimum kompres/lambat)
                             Default 6 adalah keseimbangan kecepatan dan ukuran yang baik.
        """
        try:
            original_size = os.path.getsize(img_path)

            img = Image.open(img_path)

            # Simpan sebagai PNG dengan level kompresi
            img.save(output_path, format="PNG", compress_level=compress_level, optimize=True)

            compressed_size = os.path.getsize(output_path)

            if original_size > 0:
                ratio = (1 - compressed_size / original_size) * 100
            else:
                ratio = 0

            return {
                "success": True,
                "output_path": output_path,
                "original_size": self.fh.format_file_size(original_size),
                "compressed_size": self.fh.format_file_size(compressed_size),
                "ratio": f"{ratio:.1f}% lebih kecil" if ratio > 0 else "Tidak ada pengurangan",
                "compress_level": compress_level
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 3. KOMPRESI BATCH
    # =========================================================
    def compress_batch(self, folder_path, quality=75, output_subfolder="compressed"):
        """
        Kompres semua gambar dalam sebuah folder.

        Parameters:
            folder_path      : path folder berisi gambar
            quality          : kualitas JPEG (1-95)
            output_subfolder : nama subfolder output di dalam folder input
        """
        try:
            output_folder = os.path.join(folder_path, output_subfolder)
            os.makedirs(output_folder, exist_ok=True)

            # Cari semua file gambar
            image_files = [
                f for f in os.listdir(folder_path)
                if os.path.splitext(f)[1].lower() in self.supported_formats
            ]

            if not image_files:
                return {"success": False, "error": "Tidak ada file gambar di folder ini."}

            total = len(image_files)
            success_count = 0
            fail_count = 0
            total_original = 0
            total_compressed = 0

            print(f"\n  Memproses {total} file gambar...")
            print()

            for i, filename in enumerate(image_files, 1):
                src_path = os.path.join(folder_path, filename)
                name, _ = os.path.splitext(filename)
                out_path = os.path.join(output_folder, f"{name}_compressed.jpg")

                original_size = os.path.getsize(src_path)
                result = self.compress_jpeg(src_path, out_path, quality=quality)

                if result["success"]:
                    compressed_size = os.path.getsize(out_path)
                    total_original += original_size
                    total_compressed += compressed_size
                    success_count += 1
                    print(f"  [{i}/{total}] ✓ {filename}")
                else:
                    fail_count += 1
                    print(f"  [{i}/{total}] ✗ {filename} — {result['error']}")

            total_saved = total_original - total_compressed
            return {
                "success": True,
                "total": total,
                "success_count": success_count,
                "fail_count": fail_count,
                "total_saved": self.fh.format_file_size(total_saved),
                "output_folder": output_folder
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # 4. INFO GAMBAR
    # =========================================================
    def get_image_info(self, img_path):
        """
        Tampilkan informasi detail sebuah gambar.
        """
        try:
            file_size = os.path.getsize(img_path)
            img = Image.open(img_path)

            # Ambil DPI jika ada
            dpi = img.info.get("dpi", "Tidak tersedia")
            if isinstance(dpi, tuple):
                dpi = f"{dpi[0]:.0f} x {dpi[1]:.0f} DPI"

            # Coba baca kualitas JPEG
            jpeg_quality = None
            if img.format == "JPEG":
                quantization = img.quantization
                if quantization:
                    # Estimasi kualitas dari quantization table (perkiraan kasar)
                    q_val = sum(quantization[0]) / len(quantization[0])
                    if q_val <= 2:
                        jpeg_quality = "~95 (sangat tinggi)"
                    elif q_val <= 8:
                        jpeg_quality = "~85 (tinggi)"
                    elif q_val <= 16:
                        jpeg_quality = "~75 (standar)"
                    elif q_val <= 32:
                        jpeg_quality = "~60 (sedang)"
                    else:
                        jpeg_quality = "~40 atau lebih rendah"

            return {
                "success": True,
                "info": {
                    "filename": os.path.basename(img_path),
                    "file_size": self.fh.format_file_size(file_size),
                    "resolution": f"{img.width} x {img.height} pixel",
                    "format": img.format or "Tidak diketahui",
                    "mode": img.mode,
                    "dpi": dpi,
                    "jpeg_quality": jpeg_quality
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
