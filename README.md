# Digital Watermarking & Compression Tool

Aplikasi Python untuk watermarking dan kompresi gambar digital berbasis CLI.

---

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan Program

```bash
python main.py
```

---

## Fitur

### Menu 1 — Watermarking

| Opsi | Deskripsi |
|------|-----------|
| Tambah Watermark Teks | Sisipkan teks ke gambar dengan opacity & posisi |
| Tambah Watermark Logo | Tempelkan logo/gambar ke gambar utama |
| Invisible Watermark (LSB) | Sembunyikan pesan dalam pixel gambar |
| Ekstrak Invisible Watermark | Baca pesan tersembunyi dari gambar |

### Menu 2 — Compression

| Opsi | Deskripsi |
|------|-----------|
| Kompres JPEG | Kompresi lossy dengan kontrol kualitas 1-95 |
| Kompres PNG | Kompresi lossless dengan level 0-9 |
| Kompres Batch | Kompres semua gambar dalam satu folder |
| Info Gambar | Lihat metadata dan detail file |

---

## Struktur Folder

```
watermarking_app/
├── main.py               # Entry point & menu
├── modules/
│   ├── watermark.py      # Logika watermarking
│   └── compression.py    # Logika kompresi
├── utils/
│   ├── file_handler.py   # Validasi & helper file
│   └── image_utils.py    # Helper gambar
├── assets/               # Logo & gambar sample
├── output/               # Hasil output program
├── requirements.txt
└── README.md
```

---

## Catatan Teknis

- **Invisible watermark** menggunakan teknik **LSB (Least Significant Bit)** pada channel merah
- File output invisible watermark **wajib PNG** (JPEG akan merusak data LSB)
- Kompresi JPEG bersifat **lossy** (ada penurunan kualitas), PNG bersifat **lossless**
- Semua output disimpan di folder `output/`
