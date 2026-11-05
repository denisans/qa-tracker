---
description: Ubah tampilan dashboard (UI) dengan aman: cadangan bernomor, edit, pratinjau, persetujuan, lalu terbit.
allowed-tools: Bash(python scripts/qa.py:*), Bash(python3 scripts/qa.py:*), Bash(git:*), Bash(cp:*), Bash(ls:*), Read, Edit, Write, Artifact
argument-hint: [perubahan tampilan yang diinginkan, bahasa biasa]
---

Tugas: ubah tampilan dashboard sesuai `$ARGUMENTS`. Yang diubah HANYA `dashboard/template.html`. Jangan menyentuh `data/qa.json`.

1. Jika `$ARGUMENTS` kosong, tanyakan apa yang ingin diubah.
2. Cadangan bernomor: lihat `ls dashboard/versions/`, ambil nomor tertinggi N, lalu `cp dashboard/template.html dashboard/versions/template.v<N+1>.html`. Sebutkan nomor ini ke user sebagai titik kembali.
3. Edit `dashboard/template.html`. Pertahankan: penanda `/*__QA_DATA__*/null`, token warna terang dan gelap, form inbox (kolom dan perilakunya), serta pembuatan elemen lewat `textContent` (jangan memakai innerHTML untuk data temuan). Jaga tampilan di lebar 400px tanpa geser samping dan kontras teks yang terbaca.
4. Bangun: `python scripts/qa.py validate && python scripts/qa.py dashboard`. Jika gagal, perbaiki atau kembalikan dari cadangan.
5. Pratinjau: jika ada Playwright atau browser, ambil tangkapan layar `dist/dashboard.html` (desktop dan 400px) dan tunjukkan ke user. Jika tidak ada, jelaskan perubahan dalam kata-kata dan minta user membuka `dist/dashboard.html`.
6. Minta persetujuan user. JANGAN menerbitkan sebelum disetujui. Jika user menolak, kembalikan: `cp dashboard/versions/template.v<N+1>.html dashboard/template.html` dan jangan ubah apa pun lagi.
7. Setelah disetujui: jalankan langkah `/qa-publish` (terbitkan ke URL di `artifact/ARTIFACT_URL.txt` tanpa mengirim ulang capabilities). Lalu simpan hasil akhir sebagai versi baru: `cp dashboard/template.html dashboard/versions/template.v<N+2>.html`, `git add -A`, `git commit -m "ui v<N+2>: <ringkasan>"`, `git tag ui-v<N+2>`. Tanyakan dulu sebelum `git push`.
8. Laporkan singkat: apa yang berubah, nomor versi, cara kembali (`git checkout ui-v<N+1> -- dashboard/template.html` lalu `/qa-publish`).
