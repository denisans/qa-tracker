---
description: Cek temuan QA yang sudah diperbaiki dev (membaca kode repo aplikasi), lalu catat hasilnya. Pratinjau dulu, tulis setelah divalidasi.
allowed-tools: Bash(python scripts/qa.py:*), Bash(python3 scripts/qa.py:*), Bash(git:*), Read, Grep, Glob
argument-hint: [QA-0001 QA-0002 ... | kosong = semua yang belum Closed]
---

Tugas: cek di KODE apakah temuan QA sudah diperbaiki. Ini bukti kode saja, bukan uji aplikasi.

1. Ambil temuan: `python scripts/qa.py list` (jika ada argumen ID: `python scripts/qa.py list --id <ID>` per ID). Lewati yang sudah Closed, Ditunda, Won't Fix.
2. Lokasi kode aplikasi: baca `config/app.json` (`app_path`). Jika kosong, tanyakan kepada user folder repo aplikasinya, lalu jangan lanjut menebak.
3. Untuk tiap temuan: baca judul, deskripsi, langkah, expected/actual, `link_fix`, `catatan_dev`. Cari di kode (dan `git log` di repo aplikasi, mis. commit yang menyebut ID atau modulnya). Putuskan salah satu:
   - `Terverifikasi Fixed`: ada perubahan kode yang jelas menangani masalahnya
   - `Belum Fixed`: kode masih berperilaku seperti di laporan
   - `Perlu Cek Manual`: perbaikan bergantung pada data, UI, atau perilaku yang tidak bisa dipastikan dari kode
   - `Tidak Ada Bukti`: tidak ada perubahan terkait yang ditemukan
4. Tulis hasil ke `qa/tmp/check_results.json` (buat foldernya) berformat daftar:
   `[{"id":"QA-0001","cc_status":"Belum Fixed","evidence":"file:baris atau commit, satu-dua kalimat"}]`
   Bukti wajib konkret (path file, nama fungsi, hash commit). Jangan menebak.
5. Pratinjau: `python scripts/qa.py apply-check qa/tmp/check_results.json`. Tampilkan tabel ke user.
6. JANGAN menulis sebelum user setuju. Setelah setuju: `python scripts/qa.py apply-check qa/tmp/check_results.json --yes --commit`.
7. Laporkan ringkas: jumlah per hasil, versi baru, dan temuan yang bertentangan (status dev "Sudah Fixed" tetapi cek kode "Belum Fixed").

Aturan: jangan mengubah kolom status, severity, atau catatan QA/dev. Cek Claude Code hanya mengisi kolom cc_*. Keputusan Closed ada di QA setelah retest.
