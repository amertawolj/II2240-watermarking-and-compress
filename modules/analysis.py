"""
modules/analysis.py
===================
Modul analisis kualitas gambar setelah watermarking.
Metrik yang dihitung:
- MSE  : Mean Squared Error
- PSNR : Peak Signal-to-Noise Ratio
- SSIM : Structural Similarity Index
"""

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.file_handler import FileHandler


class AnalysisModule:
    def __init__(self):
        self.fh = FileHandler()

    # =========================================================
    # CORE METRICS
    # =========================================================
    def calculate_mse(self, original, watermarked):
        """Mean Squared Error — makin kecil makin bagus (0 = identik)."""
        orig = np.array(original, dtype=np.float64)
        wm   = np.array(watermarked, dtype=np.float64)
        return float(np.mean((orig - wm) ** 2))

    def calculate_psnr(self, mse, max_pixel=255.0):
        """
        Peak Signal-to-Noise Ratio (dB) — makin besar makin bagus.
        > 40 dB  : sangat baik (hampir tidak terlihat bedanya)
        30-40 dB : baik
        < 30 dB  : terlihat degradasi
        """
        if mse == 0:
            return float('inf')
        return 20 * np.log10(max_pixel / np.sqrt(mse))

    def calculate_ssim(self, original, watermarked):
        """
        Structural Similarity Index (0-1) — makin mendekati 1 makin bagus.
        > 0.95 : sangat mirip
        > 0.80 : masih dapat diterima
        """
        orig = np.array(original, dtype=np.float64)
        wm   = np.array(watermarked, dtype=np.float64)

        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2

        mu1 = np.mean(orig)
        mu2 = np.mean(wm)
        sigma1_sq = np.var(orig)
        sigma2_sq = np.var(wm)
        sigma12   = np.mean((orig - mu1) * (wm - mu2))

        numerator   = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
        denominator = (mu1**2 + mu2**2 + c1) * (sigma1_sq + sigma2_sq + c2)

        return float(numerator / denominator)

    # =========================================================
    # HITUNG SEMUA METRIK
    # =========================================================
    def analyze(self, original_path, watermarked_path):
        """
        Hitung MSE, PSNR, dan SSIM antara dua gambar.
        Kedua gambar akan di-resize ke ukuran yang sama jika berbeda.
        """
        try:
            orig_img = Image.open(original_path).convert("RGB")
            wm_img   = Image.open(watermarked_path).convert("RGB")

            # Samakan ukuran
            if orig_img.size != wm_img.size:
                wm_img = wm_img.resize(orig_img.size, Image.LANCZOS)

            mse  = self.calculate_mse(orig_img, wm_img)
            psnr = self.calculate_psnr(mse)
            ssim = self.calculate_ssim(orig_img, wm_img)

            orig_size = os.path.getsize(original_path)
            wm_size   = os.path.getsize(watermarked_path)

            return {
                "success": True,
                "mse":  round(mse, 4),
                "psnr": round(psnr, 2) if psnr != float('inf') else "∞",
                "ssim": round(ssim, 6),
                "original_size":   self.fh.format_file_size(orig_size),
                "watermarked_size": self.fh.format_file_size(wm_size),
                "resolution": f"{orig_img.width} x {orig_img.height}",
                "orig_path": original_path,
                "wm_path":   watermarked_path,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================
    # ANALISIS MULTI-GAMBAR (untuk grafik perbandingan)
    # =========================================================
    def analyze_multiple(self, original_path, watermarked_paths):
        """
        Bandingkan satu gambar original dengan beberapa hasil watermark.
        watermarked_paths: list of (label, path)
        """
        results = []
        for label, wm_path in watermarked_paths:
            r = self.analyze(original_path, wm_path)
            if r["success"]:
                r["label"] = label
                results.append(r)
        return results

    # =========================================================
    # PLOT GRAFIK
    # =========================================================
    def plot_analysis(self, original_path, watermarked_path, result=None):
        """
        Tampilkan grafik analisis lengkap:
        - Gambar original vs watermarked
        - Difference map (amplified)
        - Bar chart MSE, PSNR, SSIM
        - Histogram distribusi pixel
        """
        if result is None:
            result = self.analyze(original_path, watermarked_path)

        if not result["success"]:
            print(f"  ✗ Gagal analisis: {result['error']}")
            return

        orig_img = Image.open(original_path).convert("RGB")
        wm_img   = Image.open(watermarked_path).convert("RGB")
        if orig_img.size != wm_img.size:
            wm_img = wm_img.resize(orig_img.size, Image.LANCZOS)

        orig_arr = np.array(orig_img, dtype=np.float64)
        wm_arr   = np.array(wm_img, dtype=np.float64)
        diff_arr = np.abs(orig_arr - wm_arr)

        # Amplify difference agar terlihat
        diff_vis = np.clip(diff_arr * 10, 0, 255).astype(np.uint8)

        # ---- Layout ----
        fig = plt.figure(figsize=(16, 10), facecolor="#0f0f0f")
        fig.suptitle("Digital Watermarking — Image Quality Analysis",
                     fontsize=16, fontweight="bold", color="white", y=0.98)

        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

        ax_orig  = fig.add_subplot(gs[0, 0])
        ax_wm    = fig.add_subplot(gs[0, 1])
        ax_diff  = fig.add_subplot(gs[0, 2])
        ax_bar   = fig.add_subplot(gs[1, 0])
        ax_hist  = fig.add_subplot(gs[1, 1])
        ax_info  = fig.add_subplot(gs[1, 2])

        img_style = dict(cmap=None, aspect="auto")

        # --- Original ---
        ax_orig.imshow(orig_img, **img_style)
        ax_orig.set_title("Original", color="white", fontsize=11)
        ax_orig.axis("off")
        ax_orig.text(0.5, -0.05, result["original_size"],
                     transform=ax_orig.transAxes, ha="center",
                     color="#aaaaaa", fontsize=9)

        # --- Watermarked ---
        ax_wm.imshow(wm_img, **img_style)
        ax_wm.set_title("Watermarked", color="white", fontsize=11)
        ax_wm.axis("off")
        ax_wm.text(0.5, -0.05, result["watermarked_size"],
                   transform=ax_wm.transAxes, ha="center",
                   color="#aaaaaa", fontsize=9)

        # --- Difference Map ---
        ax_diff.imshow(diff_vis, **img_style)
        ax_diff.set_title("Difference Map (10×)", color="white", fontsize=11)
        ax_diff.axis("off")
        ax_diff.text(0.5, -0.05, f"Max diff: {int(diff_arr.max())}",
                     transform=ax_diff.transAxes, ha="center",
                     color="#aaaaaa", fontsize=9)

        # --- Bar Chart Metrik ---
        metrics_labels = ["MSE", "PSNR (dB)", "SSIM"]
        psnr_val = result["psnr"] if result["psnr"] != "∞" else 100
        metrics_values = [result["mse"], float(psnr_val), result["ssim"] * 100]
        colors = ["#e74c3c", "#2ecc71", "#3498db"]

        bars = ax_bar.bar(metrics_labels, metrics_values, color=colors,
                          edgecolor="white", linewidth=0.5, width=0.5)

        for bar, val in zip(bars, [result["mse"], result["psnr"], result["ssim"]]):
            ax_bar.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(metrics_values) * 0.02,
                        str(val), ha="center", va="bottom",
                        color="white", fontsize=10, fontweight="bold")

        ax_bar.set_facecolor("#1a1a1a")
        ax_bar.set_title("Quality Metrics", color="white", fontsize=11)
        ax_bar.tick_params(colors="white")
        ax_bar.spines[:].set_color("#444")
        ax_bar.set_ylabel("Value  (SSIM × 100)", color="#aaaaaa", fontsize=9)
        for label in ax_bar.get_xticklabels():
            label.set_color("white")

        # --- Histogram ---
        channels = {"R": (orig_arr[:,:,0], wm_arr[:,:,0], "#e74c3c"),
                    "G": (orig_arr[:,:,1], wm_arr[:,:,1], "#2ecc71"),
                    "B": (orig_arr[:,:,2], wm_arr[:,:,2], "#3498db")}

        for ch, (o_ch, w_ch, col) in channels.items():
            ax_hist.hist(o_ch.flatten(), bins=64, alpha=0.4, color=col,
                         histtype="step", linewidth=1.5, label=f"Orig {ch}")
            ax_hist.hist(w_ch.flatten(), bins=64, alpha=0.8, color=col,
                         histtype="step", linewidth=1, linestyle="--", label=f"WM {ch}")

        ax_hist.set_facecolor("#1a1a1a")
        ax_hist.set_title("Pixel Distribution (RGB)", color="white", fontsize=11)
        ax_hist.tick_params(colors="white")
        ax_hist.spines[:].set_color("#444")
        ax_hist.set_xlabel("Pixel Value", color="#aaaaaa", fontsize=9)
        ax_hist.set_ylabel("Count", color="#aaaaaa", fontsize=9)
        leg = ax_hist.legend(fontsize=7, ncol=2, framealpha=0.3)
        for text in leg.get_texts():
            text.set_color("white")

        # --- Info Panel ---
        ax_info.set_facecolor("#1a1a1a")
        ax_info.axis("off")
        ax_info.set_title("Summary", color="white", fontsize=11)

        psnr_display = result["psnr"]
        psnr_grade   = "∞ (identik)" if psnr_display == "∞" else \
                       "Sangat Baik ✓" if float(psnr_display) > 40 else \
                       "Baik ✓"        if float(psnr_display) > 30 else \
                       "Degradasi ✗"

        ssim_grade = "Sangat Mirip ✓" if result["ssim"] > 0.95 else \
                     "Dapat Diterima"  if result["ssim"] > 0.80 else \
                     "Berbeda ✗"

        info_lines = [
            ("Resolusi",    result["resolution"]),
            ("", ""),
            ("MSE",         f"{result['mse']}"),
            ("PSNR",        f"{psnr_display} dB  →  {psnr_grade}"),
            ("SSIM",        f"{result['ssim']}  →  {ssim_grade}"),
            ("", ""),
            ("Ukuran Asli", result["original_size"]),
            ("Ukuran WM",   result["watermarked_size"]),
        ]

        y = 0.92
        for key, val in info_lines:
            if key == "":
                y -= 0.06
                continue
            ax_info.text(0.05, y, f"{key}:", transform=ax_info.transAxes,
                         color="#aaaaaa", fontsize=9, va="top")
            ax_info.text(0.42, y, val, transform=ax_info.transAxes,
                         color="white", fontsize=9, va="top", fontweight="bold")
            y -= 0.11

        for ax in [ax_orig, ax_wm, ax_diff, ax_bar, ax_hist, ax_info]:
            ax.set_facecolor("#1a1a1a") if ax not in [ax_orig, ax_wm, ax_diff] else None
            fig.patch.set_facecolor("#0f0f0f")

        plt.show()

    # =========================================================
    # PLOT PERBANDINGAN MULTI-GAMBAR
    # =========================================================
    def plot_comparison(self, results):
        """
        Bar chart perbandingan PSNR & SSIM untuk beberapa hasil watermark.
        results: output dari analyze_multiple()
        """
        if not results:
            print("  ✗ Tidak ada data untuk dibandingkan.")
            return

        labels = [r["label"] for r in results]
        psnr_vals = [float(r["psnr"]) if r["psnr"] != "∞" else 100 for r in results]
        ssim_vals = [r["ssim"] for r in results]
        mse_vals  = [r["mse"] for r in results]

        fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor="#0f0f0f")
        fig.suptitle("Watermark Quality Comparison", color="white",
                     fontsize=14, fontweight="bold")

        datasets = [
            (axes[0], psnr_vals, "PSNR (dB)", "#2ecc71", "Lebih tinggi = lebih baik"),
            (axes[1], ssim_vals, "SSIM",      "#3498db", "Mendekati 1.0 = lebih baik"),
            (axes[2], mse_vals,  "MSE",       "#e74c3c", "Lebih rendah = lebih baik"),
        ]

        for ax, vals, title, color, subtitle in datasets:
            bars = ax.bar(labels, vals, color=color, edgecolor="white",
                          linewidth=0.5, width=0.5)
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(vals) * 0.02,
                        f"{v:.4f}", ha="center", va="bottom",
                        color="white", fontsize=9, fontweight="bold")

            ax.set_facecolor("#1a1a1a")
            ax.set_title(title, color="white", fontsize=11)
            ax.set_xlabel(subtitle, color="#aaaaaa", fontsize=8)
            ax.tick_params(colors="white")
            ax.spines[:].set_color("#444")
            for lbl in ax.get_xticklabels():
                lbl.set_color("white")
                lbl.set_fontsize(9)

        plt.tight_layout()
        plt.show()