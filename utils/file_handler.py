"""
utils/file_handler.py
=====================
Helper untuk operasi file:
- Validasi file gambar
- Generate nama output otomatis
- Format ukuran file
"""

import os


class FileHandler:
    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

    def validate_image(self, path):
        """
        Cek apakah file ada dan berformat gambar yang didukung.
        Cetak pesan error jika tidak valid.
        """
        if not os.path.exists(path):
            print(f"  ✗ File tidak ditemukan: {path}")
            return False

        ext = os.path.splitext(path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            print(f"  ✗ Format tidak didukung: {ext}")
            print(f"  Format yang didukung: {', '.join(self.SUPPORTED_EXTENSIONS)}")
            return False

        return True

    def generate_output_path(self, input_path, suffix="_output", force_ext=None):
        """
        Buat path output otomatis di folder 'output/' berdasarkan nama file input.

        Parameters:
            input_path : path file input
            suffix     : tambahan di akhir nama file (sebelum ekstensi)
            force_ext  : paksa ekstensi tertentu (mis. ".png"), jika None pakai ekstensi asli
        """
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)

        # Tentukan ekstensi output
        out_ext = force_ext if force_ext else ext

        # Buat folder output jika belum ada
        # Cari folder 'output' relatif terhadap lokasi script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(script_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"{name}{suffix}{out_ext}"
        return os.path.join(output_dir, output_filename)

    def format_file_size(self, size_bytes):
        """
        Format ukuran bytes menjadi string yang mudah dibaca.
        Contoh: 1048576 -> '1.00 MB'
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

    def list_images_in_folder(self, folder_path):
        """
        Daftar semua file gambar dalam sebuah folder.
        """
        if not os.path.isdir(folder_path):
            return []

        return [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in self.SUPPORTED_EXTENSIONS
        ]
