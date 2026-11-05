---
description: Bangun dashboard dari data terbaru dan publikasikan/perbarui sebagai artifact.
allowed-tools: Bash(python scripts/qa.py:*), Bash(python3 scripts/qa.py:*), Bash(git:*), Read, Write, Artifact
---

1. Validasi lalu bangun: `python scripts/qa.py validate && python scripts/qa.py dashboard` (menghasilkan `dist/dashboard.html`).
2. Baca `artifact/ARTIFACT_URL.txt`.
   - Jika ada URL: publikasikan `dist/dashboard.html` dengan alat Artifact memakai `url` tersebut (memperbarui artifact yang sama). Jangan mengirim ulang `capabilities`.
   - Jika belum ada: publikasikan pertama kali dengan `capabilities` = `{"db":{"rules":[{"path":"inbox","read":"view","write":"interact"}]},"user":{"scopes":["profile"]}}`, icon `chart`, judul halaman "QA Tracker KRESNA". Simpan URL hasilnya ke `artifact/ARTIFACT_URL.txt` dan commit.
3. Jika alat Artifact tidak tersedia di Claude Code user: katakan apa adanya, dan sebutkan `dist/dashboard.html` bisa dibuka langsung di browser (tanpa form inbox).
4. Ingatkan user: agar QA bisa mengirim lewat form, bagikan artifact sebagai Contributor.
