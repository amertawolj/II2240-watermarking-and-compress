"""
Digital Watermarking & Compression Tool
========================================
Aplikasi untuk watermarking dan kompresi gambar digital.
"""

import os
import sys
from modules.watermark import WatermarkModule
from modules.compression import CompressionModule
from utils.file_handler import FileHandler


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    print("=" * 55)
    print("     DIGITAL WATERMARKING & COMPRESSION TOOL")
    print("=" * 55)
    print()


def print_main_menu():
    print_banner()
    print("  Pilih menu:")
    print()
    print("  [1]  Watermarking")
    print("  [2]  Compression")
    print("  [0]  Keluar")
    print()
    print("-" * 55)


def print_watermark_menu():
    print_banner()
    print("  MENU WATERMARKING")
    print()
    print("  [1]  Tambah Watermark Teks")
    print("  [2]  Tambah Watermark Logo/Gambar")
    print("  [3]  Tambah Invisible Watermark (LSB)")
    print("  [4]  Ekstrak Invisible Watermark")
    print("  [0]  Kembali ke Menu Utama")
    print()
    print("-" * 55)


def print_compression_menu():
    print_banner()
    print("  MENU COMPRESSION")
    print()
    print("  [1]  Kompres Gambar (JPEG)")
    print("  [2]  Kompres Gambar (PNG - Lossless)")
    print("  [3]  Kompres Batch (Banyak File)")
    print("  [4]  Lihat Info Kompresi")
    print("  [0]  Kembali ke Menu Utama")
    print()
    print("-" * 55)


def handle_watermark_menu():
    wm = WatermarkModule()
    fh = FileHandler()

    while True:
        clear_screen()
        print_watermark_menu()
        choice = input("  Pilih opsi: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            # Watermark Teks
            print()
            img_path = input("  Path gambar input : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            text = input("  Teks watermark     : ").strip()
            opacity = input("  Opacity (0.1-1.0) [default 0.5]: ").strip()
            opacity = float(opacity) if opacity else 0.5

            position = input("  Posisi (center/bottomright/bottomleft/topright/topleft) [default center]: ").strip()
            position = position if position else "center"

            output_path = fh.generate_output_path(img_path, suffix="_watermarked")
            result = wm.add_text_watermark(img_path, text, output_path, opacity=opacity, position=position)

            print()
            if result["success"]:
                print(f"  ✓ Berhasil! Disimpan di: {result['output_path']}")
                print(f"  ✓ Ukuran: {result['file_size']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "2":
            # Watermark Logo
            print()
            img_path = input("  Path gambar input : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            logo_path = input("  Path logo/gambar  : ").strip().strip('"')
            if not fh.validate_image(logo_path):
                input("  [Enter untuk lanjut]")
                continue

            opacity = input("  Opacity (0.1-1.0) [default 0.4]: ").strip()
            opacity = float(opacity) if opacity else 0.4

            scale = input("  Skala logo (0.1-0.5) [default 0.2]: ").strip()
            scale = float(scale) if scale else 0.2

            position = input("  Posisi (center/bottomright/bottomleft/topright/topleft) [default bottomright]: ").strip()
            position = position if position else "bottomright"

            output_path = fh.generate_output_path(img_path, suffix="_logo_watermarked")
            result = wm.add_logo_watermark(img_path, logo_path, output_path, opacity=opacity, scale=scale, position=position)

            print()
            if result["success"]:
                print(f"  ✓ Berhasil! Disimpan di: {result['output_path']}")
                print(f"  ✓ Ukuran: {result['file_size']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "3":
            # Invisible Watermark (LSB)
            print()
            img_path = input("  Path gambar input  : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            message = input("  Pesan tersembunyi  : ").strip()
            output_path = fh.generate_output_path(img_path, suffix="_invisible_wm", force_ext=".png")
            result = wm.embed_invisible_watermark(img_path, message, output_path)

            print()
            if result["success"]:
                print(f"  ✓ Berhasil! Disimpan di: {result['output_path']}")
                print(f"  ✓ Pesan disisipkan pada {result['bits_used']} bit")
                print(f"  ✓ Format: PNG (wajib untuk invisible watermark)")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "4":
            # Ekstrak Invisible Watermark
            print()
            img_path = input("  Path gambar (PNG)  : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            result = wm.extract_invisible_watermark(img_path)

            print()
            if result["success"]:
                print(f"  ✓ Pesan ditemukan : '{result['message']}'")
            else:
                print(f"  ✗ {result['error']}")
            input("\n  [Enter untuk lanjut]")

        else:
            print("  Pilihan tidak valid.")
            input("  [Enter untuk lanjut]")


def handle_compression_menu():
    cm = CompressionModule()
    fh = FileHandler()

    while True:
        clear_screen()
        print_compression_menu()
        choice = input("  Pilih opsi: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            # Kompres JPEG
            print()
            img_path = input("  Path gambar input     : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            quality = input("  Kualitas JPEG (1-95) [default 75]: ").strip()
            quality = int(quality) if quality else 75

            output_path = fh.generate_output_path(img_path, suffix=f"_compressed_q{quality}", force_ext=".jpg")
            result = cm.compress_jpeg(img_path, output_path, quality=quality)

            print()
            if result["success"]:
                print(f"  ✓ Berhasil! Disimpan di  : {result['output_path']}")
                print(f"  ✓ Ukuran asal            : {result['original_size']}")
                print(f"  ✓ Ukuran setelah kompres : {result['compressed_size']}")
                print(f"  ✓ Rasio kompresi         : {result['ratio']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "2":
            # Kompres PNG Lossless
            print()
            img_path = input("  Path gambar input        : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            level = input("  Level kompresi (0-9) [default 6]: ").strip()
            level = int(level) if level else 6

            output_path = fh.generate_output_path(img_path, suffix=f"_compressed_png", force_ext=".png")
            result = cm.compress_png(img_path, output_path, compress_level=level)

            print()
            if result["success"]:
                print(f"  ✓ Berhasil! Disimpan di  : {result['output_path']}")
                print(f"  ✓ Ukuran asal            : {result['original_size']}")
                print(f"  ✓ Ukuran setelah kompres : {result['compressed_size']}")
                print(f"  ✓ Rasio kompresi         : {result['ratio']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "3":
            # Batch Compression
            print()
            folder_path = input("  Path folder gambar : ").strip().strip('"')
            if not os.path.isdir(folder_path):
                print("  ✗ Folder tidak ditemukan.")
                input("  [Enter untuk lanjut]")
                continue

            quality = input("  Kualitas JPEG (1-95) [default 75]: ").strip()
            quality = int(quality) if quality else 75

            result = cm.compress_batch(folder_path, quality=quality)

            print()
            if result["success"]:
                print(f"  ✓ Total file diproses  : {result['total']}")
                print(f"  ✓ Berhasil             : {result['success_count']}")
                print(f"  ✓ Gagal                : {result['fail_count']}")
                print(f"  ✓ Total penghematan    : {result['total_saved']}")
                print(f"  ✓ Output folder        : {result['output_folder']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        elif choice == "4":
            # Info Kompresi
            print()
            img_path = input("  Path gambar : ").strip().strip('"')
            if not fh.validate_image(img_path):
                input("  [Enter untuk lanjut]")
                continue

            result = cm.get_image_info(img_path)

            print()
            if result["success"]:
                info = result["info"]
                print(f"  {'File':<20}: {info['filename']}")
                print(f"  {'Ukuran File':<20}: {info['file_size']}")
                print(f"  {'Resolusi':<20}: {info['resolution']}")
                print(f"  {'Format':<20}: {info['format']}")
                print(f"  {'Mode Warna':<20}: {info['mode']}")
                print(f"  {'DPI':<20}: {info['dpi']}")
                if info.get("jpeg_quality"):
                    print(f"  {'Kualitas JPEG':<20}: {info['jpeg_quality']}")
            else:
                print(f"  ✗ Gagal: {result['error']}")
            input("\n  [Enter untuk lanjut]")

        else:
            print("  Pilihan tidak valid.")
            input("  [Enter untuk lanjut]")


def main():
    while True:
        clear_screen()
        print_main_menu()
        choice = input("  Pilih menu: ").strip()

        if choice == "1":
            handle_watermark_menu()
        elif choice == "2":
            handle_compression_menu()
        elif choice == "0":
            clear_screen()
            print("  Terima kasih! Program selesai.")
            print()
            sys.exit(0)
        else:
            print("  Pilihan tidak valid. Coba lagi.")
            input("  [Enter untuk lanjut]")


if __name__ == "__main__":
    main()
