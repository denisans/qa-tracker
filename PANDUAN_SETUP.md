# QA Tracker KRESNA — Panduan Setup

## Isi repo
- `data/qa.json` — data tunggal (30 temuan, versi v2.0, riwayat versi di dalamnya)
- `scripts/qa.py` — satu-satunya jalur mengubah data (pratinjau dulu, `--yes` untuk menulis, `--commit` untuk commit + tag `qa-vX.Y`)
- `.claude/commands/` — `/qa-check`, `/qa-add`, `/qa-sync`, `/qa-publish`, `/qa-summary`, `/qa-ui`
- `dashboard/template.html` — sumber dashboard; hasil build di `dist/dashboard.html`
- `.github/workflows/validate.yml` — CI memeriksa data tiap push
- `artifact/ARTIFACT_URL.txt` — alamat dashboard yang sudah terbit

## Setup satu kali (PM)
1. Buat repo kosong di GitHub (private), lalu di folder ini: `git init && git add -A && git commit -m "init" && git branch -M main && git remote add origin <URL-REPO> && git push -u origin main`
2. Pastikan Python 3.9+ terpasang (tanpa library tambahan).
3. Salin `config/app.example.json` ke `config/app.json`, isi `app_path` dengan folder repo aplikasi (untuk `/qa-check`).
4. Buka folder ini di VS Code dengan Claude Code. Cek: `python scripts/qa.py validate`.
5. Dashboard: buka tautan di `artifact/ARTIFACT_URL.txt`, Share, tambahkan QA sebagai Contributor (agar bisa kirim lewat form) dan dev sebagai Viewer.

## Alur harian
- QA lapor di Discord seperti biasa. Lalu salah satu: isi form di dashboard, atau tempel teks ke `/qa-add`.
- PM: `/qa-sync` (ambil dari form) atau `/qa-add` → periksa pratinjau → setuju → `/qa-publish`.
- Dev: perbaiki, lalu isi Link Fix lewat PM/QA (atau minta Claude: "ubah QA-0007 status Sudah Fixed - Siap Retest, link_fix ...").
- PM: `/qa-check` → Claude membaca kode, menampilkan pratinjau → setuju → tersimpan + `/qa-publish`.
- QA retest, lalu Closed / Reopened.

## Mengubah tampilan dashboard
Jalankan `/qa-ui` diikuti permintaan Anda, mis. `/qa-ui ubah warna tab Dev jadi hijau`. Claude membuat cadangan bernomor di `dashboard/versions/`, mengedit, menunjukkan pratinjau, dan baru menerbitkan setelah Anda setuju. Kembali ke tampilan lama: `git checkout ui-v2 -- dashboard/template.html` lalu `/qa-publish`.

## Rollback
`python scripts/qa.py versions` lalu `git checkout qa-v2.1 -- data/qa.json` dan `/qa-publish`.

## Batasan yang perlu diketahui
- Belum diuji pada akun GitHub dan Claude Code Anda; hanya diuji offline.
- Claude Code tidak bisa membaca Discord. Tautan Discord hanya disimpan.
- `/qa-sync` dan `/qa-publish` butuh alat Artifact di Claude Code Anda. Jika tidak ada, pakai `/qa-add` dan buka `dist/dashboard.html` langsung.
- Severity belum terisi; risiko rilis dihitung dari Priority P0.
- Cek Claude Code = bukti kode, bukan uji aplikasi.
