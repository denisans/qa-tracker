---
description: Tambah temuan QA baru dari teks yang ditempel (Discord/Notion/catatan). Draf dulu, simpan setelah divalidasi.
allowed-tools: Bash(python scripts/qa.py:*), Bash(python3 scripts/qa.py:*), Bash(git:*), Read, Write
argument-hint: [tempel teks laporan di sini]
---

Tugas: ubah laporan QA mentah di `$ARGUMENTS` menjadi temuan terstruktur.

1. Pecah menjadi satu temuan per masalah. Isi hanya yang ada di teks; jangan mengarang. Kolom: judul (wajib), modul, deskripsi, langkah, expected, actual, priority (`P0 - Issue on Flow`, `P1 - Feedback/Minor/UI`, `Note`, `Need Confirmation`; kosongkan jika tidak jelas), link_discord (https://), ringkasan_discord (salinan teks aslinya), pelapor, tgl_lapor (YYYY-MM-DD).
2. Jangan mengisi severity kecuali tertulis di laporan. Jangan mengisi status, ID, atau kolom cc_* (diisi otomatis).
3. Simpan daftar ke `qa/tmp/new.json` lalu pratinjau: `python scripts/qa.py add qa/tmp/new.json`. Skrip menolak duplikat (link Discord atau judul sama).
4. Tampilkan hasil draf ke user dan minta persetujuan. Setelah setuju: `python scripts/qa.py add qa/tmp/new.json --yes --commit`.
5. Laporkan ID baru dan versi data. Ingatkan untuk menjalankan `/qa-publish` agar dashboard ikut diperbarui.
