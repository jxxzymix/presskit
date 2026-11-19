# JXXZY Racing Artist Experience V2

9 halaman independen + 404. Tema racing cyan / deep blue / red, tanpa klaim afiliasi BMW.

## Isi paket
Semua HTML, CSS, JS, manifest, sitemap, robots, workflow, validasi, downloader aset. Foto/video/PDF biner asli belum disertakan karena akses unduh arsip tidak tersedia. `asset-manifest.json` mencatat aset yang dirujuk, dan `hydrate_assets.py` mengambilnya dari commit sumber yang diaudit. Link fallback foto mengarah ke commit tersebut; akses internet tetap diperlukan jika aset belum diunduh.

## Cara pakai
1. Ekstrak ZIP. Jika memakai repository lama, salin file paket ke checkout lama tanpa menghapus folder `assets` asli.
2. Jalankan `python hydrate_assets.py` (atau klik `SETUP_WINDOWS.bat` untuk unduh + preview).
3. `python check_site.py`, `node --check assets/racing.js`, lalu `python -m http.server 4173`.
4. Buka http://localhost:4173/. Test menu, music, gallery, booking, print.
5. Review git diff; commit dan push ke main. GitHub Pages harus menggunakan GitHub Actions. Jika workflow legacy manual tetap ada, jangan jalankan bersamaan.

## Batasan
EPK PDF asli adalah versi 15 halaman. Web EPK di paket ini adalah layout cetak fleksibel, bukan replika presisi 15 halaman. Tidak ada backend, statistik palsu, kalender live, atau klaim booking terkirim. Player pihak ketiga memerlukan koneksi dan izin embed. Validasi statis bukan pengujian browser/Lighthouse.
