# QA Tracker KRESNA

Sumber data tunggal: `data/qa.json`. Ubah HANYA lewat `python scripts/qa.py` (pratinjau default, `--yes` untuk menulis, `--commit` untuk commit + tag versi).
- Jangan edit `data/qa.json` dengan tangan atau skrip lain.
- Kolom `cc_*` hanya diisi lewat `apply-check`. Closed diputuskan QA setelah retest, bukan Claude.
- Selalu tampilkan pratinjau ke user dan minta persetujuan sebelum `--yes`.
- Balas dalam bahasa Indonesia, singkat.
Perintah: /qa-check, /qa-add, /qa-sync, /qa-publish, /qa-summary, /qa-ui (ubah tampilan dashboard, hanya dashboard/template.html, cadangan di dashboard/versions/).
