# Digital Watermarking & Compression Tool

Aplikasi Python untuk watermarking dan kompresi gambar digital berbasis CLI.
Wa Ode Amerta Lambelu Jamaluddin 18224034
Tugas Sistem Multimedia K02 2026

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

## Cara Kerja Watermarking

Aplikasi ini mendukung dua jenis watermark:

1. **Visible watermark** — teks atau logo yang terlihat langsung di atas gambar.
2. **Invisible watermark** — pesan tersembunyi yang disimpan dalam bit pixel sehingga hampir tidak berubah secara visual.

### Visible watermark

- Watermark teks dibuat dengan menggambar teks ke layer transparan dan menggabungkannya ke gambar utama.
- Watermark logo dilakukan dengan meresize logo, menyesuaikan opacity, lalu menempelkan logo ke posisi yang dipilih.

Contoh input dan logo:

![Original Image](assets/sample_images/choso.jpg)

![Watermark Logo](assets/watermark_logo/sonic.png)

![Output](output/choso_logo_watermarked.jpg)

### Invisible watermark (LSB)

Invisible watermark menggunakan teknik **LSB steganography** pada channel merah.

- Setiap karakter pesan diubah menjadi format binary 8-bit.
- Setiap bit pesan disimpan di **Least Significant Bit** (bit paling rendah) dari channel merah setiap pixel.
- Ubah bit paling rendah berarti nilai merah hanya berubah paling banyak 1 dari 0–255.
- Akibatnya, gambar tampak hampir sama untuk mata manusia, tetapi pesan dapat diekstrak kembali secara akurat.

Proses embed:

1. Tambahkan delimiter akhir pesan `<<<END>>>`.
2. Konversi tiap karakter ke urutan 8 bit.
3. Sisipkan setiap bit ke LSB channel merah pixel berikutnya.
4. Simpan hasil sebagai **PNG** agar bit tersembunyi tidak rusak.

Proses ekstraksi:

1. Baca nilai merah setiap pixel.
2. Ambil bit LSB dari channel merah.
3. Gabungkan setiap 8 bit menjadi karakter.
4. Berhenti ketika delimiter `<<<END>>>` ditemukan.

> Karena hanya bit paling kecil yang diubah, perbedaan visual biasanya tidak terlihat, tetapi data pesan tetap tersimpan secara tersembunyi.

---

## Analisis Kualitas Gambar

Modul analisis (`modules/analysis.py`) menghitung metrik kualitas antara gambar asli dan gambar watermarked.

### Metrik yang dihitung

- `MSE` (Mean Squared Error): semakin kecil semakin mirip.
- `PSNR` (Peak Signal-to-Noise Ratio): semakin besar semakin bagus.
  - > 40 dB = sangat baik
  - 30–40 dB = baik
  - < 30 dB = terlihat degradasi
- `SSIM` (Structural Similarity Index): nilai antara 0–1, semakin mendekati 1 semakin mirip.
  - > 0.95 = sangat mirip
  - > 0.80 = masih dapat diterima

### Visualisasi yang dibuat

Fungsi `plot_analysis()` menampilkan:

- Gambar asli vs gambar watermarked
- `Difference Map (10×)` yang memperbesar perbedaan pixel
- Bar chart `MSE`, `PSNR`, dan `SSIM`
- Histogram distribusi warna `RGB`
- Ringkasan kualitas dan ukuran file

Ini membantu melihat apakah watermark bersifat halus sekaligus memverifikasi bahwa perubahan citra tetap kecil.

Contoh hasil analisis perbandingan gambar before and after watermark:
assets/hasil_analisis/ss_hasil_analisis2.png

---

## Struktur Folder

```
watermarking_app/
├── main.py               # Entry point & menu
├── modules/
│   ├── watermark.py      # Logika watermarking
│   ├── compression.py    # Logika kompresi
│   └── analysis.py       # Logika analisis hasil watermarking
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

- **Invisible watermark** menggunakan teknik **LSB (Least Significant Bit)** pada channel merah.
- Output invisible watermark harus disimpan sebagai **PNG**; file JPEG akan merusak data LSB.
- Kompresi JPEG bersifat **lossy** (ada penurunan kualitas), PNG bersifat **lossless**.
- Semua output disimpan di folder `output/`.
