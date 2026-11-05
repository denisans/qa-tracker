#!/usr/bin/env python3
"""QA Tracker: satu-satunya jalur untuk mengubah data/qa.json (hanya pustaka standar Python).

Perintah:
  validate                  periksa seluruh data
  summary                   ringkasan angka
  list [--status S] [--id ID] [--all] [--cc-status S]   keluarkan temuan (JSON)
  add FILE.json             tambah temuan baru (ID dibuat otomatis)
  update FILE.json          ubah kolom QA/Dev pada temuan yang ada
  apply-check FILE.json     tulis hasil cek Claude Code (kolom cc_*)
  dashboard                 buat dist/dashboard.html dari data terbaru
  export-csv                ekspor CSV ke dist/qa.csv
  versions                  daftar versi (tag git)

Tulis-perintah (add, update, apply-check) default PRATINJAU. Tambah --yes untuk menulis,
--commit untuk sekaligus membuat commit git + tag versi (rollback = kembali ke tag).
"""
import argparse, csv, datetime, json, os, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data" / "qa.json"
STATUS = ["Baru", "Dalam Perbaikan", "Sudah Fixed - Siap Retest", "Closed (Terverifikasi)", "Reopened", "Ditunda", "Won't Fix"]
SEVERITY = ["Critical", "High", "Medium", "Low"]
PRIORITY = ["P0 - Issue on Flow", "P1 - Feedback/Minor/UI", "Note", "Need Confirmation"]
CC = ["Belum Dicek", "Terverifikasi Fixed", "Belum Fixed", "Perlu Cek Manual", "Tidak Ada Bukti"]
HASIL = ["Pass", "Fail"]
FIELDS = ["id", "modul", "judul", "deskripsi", "langkah", "expected", "actual", "severity", "priority", "status",
          "pic_dev", "pelapor", "tgl_lapor", "link_discord", "ringkasan_discord", "link_fix", "tgl_fix",
          "catatan_dev", "tgl_retest", "hasil_retest", "bukti_lain", "catatan_qa", "cc_status", "cc_tanggal", "cc_bukti"]
CC_FIELDS = ("cc_status", "cc_tanggal", "cc_bukti")
EDITABLE = [f for f in FIELDS if f != "id" and f not in CC_FIELDS]
CLOSED = "Closed (Terverifikasi)"
OFF = {"Ditunda", "Won't Fix"}
ENUMS = {"status": STATUS, "severity": SEVERITY, "priority": PRIORITY, "cc_status": CC, "hasil_retest": HASIL}
URLS = ("link_discord", "link_fix")
DATES = ("tgl_lapor", "tgl_fix", "tgl_retest", "cc_tanggal")


def die(m):
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def today():
    return datetime.date.today().isoformat()


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        die(f"Tidak bisa membaca {p}: {e}")


def save(p, obj):
    p = Path(p)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def problems(f, partial=False):
    out = []
    for k in f:
        if k not in FIELDS:
            out.append(f"kolom tidak dikenal '{k}'")
    if not partial and not str(f.get("judul", "")).strip():
        out.append("judul wajib diisi")
    if "id" in f and not re.fullmatch(r"QA-\d{4}", str(f["id"])):
        out.append(f"format id salah: {f['id']}")
    for k, allowed in ENUMS.items():
        if f.get(k, "") not in [""] + allowed:
            out.append(f"{k} harus salah satu dari {allowed}")
    for k in URLS:
        if f.get(k, "") and not str(f[k]).startswith("https://"):
            out.append(f"{k} harus diawali https://")
    for k in DATES:
        if f.get(k, "") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f[k])):
            out.append(f"{k} harus berformat YYYY-MM-DD")
    return out


def is_open(f):
    return f.get("status", "") != CLOSED and f.get("status", "") not in OFF


def next_version(db):
    m = re.fullmatch(r"v(\d+)\.(\d+)", db["meta"].get("version", "v2.0"))
    return f"v{m.group(1)}.{int(m.group(2)) + 1}" if m else "v2.1"


def commit_write(db, args, ids, ringkasan):
    v = next_version(db)
    db["meta"]["version"], db["meta"]["updated"] = v, today()
    db["history"].append({"versi": v, "tanggal": today(), "oleh": os.environ.get("QA_USER", "Claude Code"),
                          "ringkasan": ringkasan, "ids": ids})
    save(args.data, db)
    print(f"Tersimpan sebagai {v}.")
    if args.commit and Path(args.data).resolve() == DEFAULT_DATA.resolve():
        try:
            subprocess.run(["git", "add", "data/qa.json"], cwd=ROOT, check=True)
            subprocess.run(["git", "commit", "-m", f"qa {v}: {ringkasan}"], cwd=ROOT, check=True)
            subprocess.run(["git", "tag", f"qa-{v}"], cwd=ROOT, check=True)
            print(f"Commit dan tag qa-{v} dibuat. Rollback: git checkout qa-<versi-lama> -- data/qa.json")
        except Exception as e:
            print(f"Peringatan: commit git gagal ({e}). Data sudah tersimpan; commit manual.", file=sys.stderr)


def cmd_validate(args, db):
    errs, warns, seen = [], [], set()
    for f in db["findings"]:
        fid = f.get("id", "?")
        if fid in seen:
            errs.append(f"{fid}: id ganda")
        seen.add(fid)
        errs += [f"{fid}: {p}" for p in problems(f)]
        if f.get("status", "") == "":
            warns.append(f"{fid}: status kosong")
    links = Counter(f["link_discord"] for f in db["findings"] if f.get("link_discord"))
    warns += [f"link Discord dipakai {n} temuan: ...{l[-19:]}" for l, n in links.items() if n > 1]
    for w in warns:
        print("PERINGATAN:", w)
    if errs:
        die("Data tidak valid:\n  - " + "\n  - ".join(errs))
    print(f"OK: {len(db['findings'])} temuan valid, versi data {db['meta']['version']}.")


def stats(db):
    fs = db["findings"]
    st = Counter(f.get("status", "") or "(kosong)" for f in fs)
    p0 = [f for f in fs if f.get("priority", "").startswith("P0") and is_open(f)]
    sev = [f for f in fs if f.get("severity") in ("Critical", "High") and is_open(f)]
    return {"total": len(fs), "status": dict(st), "priority": dict(Counter(f.get("priority", "") or "(kosong)" for f in fs)),
            "cek_cc": dict(Counter(f.get("cc_status", "") or "Belum Dicek" for f in fs)),
            "p0_terbuka": len(p0), "critical_high_terbuka": len(sev),
            "konflik_dev_vs_cc": [f["id"] for f in fs if f.get("status") == STATUS[2] and f.get("cc_status") == "Belum Fixed"],
            "tanpa_link_discord": [f["id"] for f in fs if not f.get("link_discord")]}


def cmd_summary(args, db):
    print(json.dumps({"versi": db["meta"]["version"], **stats(db)}, ensure_ascii=False, indent=2))


def cmd_list(args, db):
    out = []
    for f in db["findings"]:
        if args.id:
            if f["id"] not in args.id:
                continue
        elif not args.all:
            s = f.get("status", "")
            if (args.status and s not in args.status) or (not args.status and (s == CLOSED or s in OFF)):
                continue
        if args.cc_status and (f.get("cc_status") or "Belum Dicek") not in args.cc_status:
            continue
        out.append({k: v for k, v in f.items() if v != ""})
    print(json.dumps({"count": len(out), "findings": out}, ensure_ascii=False, indent=2))


def read_list(path):
    data = load(path)
    if isinstance(data, dict):
        data = data.get("findings") or data.get("results") or []
    if not isinstance(data, list) or not data:
        die("Isi file harus berupa daftar (list) yang tidak kosong")
    return data


def norm(s):
    return re.sub(r"\W+", " ", str(s).lower()).strip()


def cmd_add(args, db):
    items, errs = read_list(args.file), []
    existing = {f["id"]: f for f in db["findings"]}
    nums = [int(i[3:]) for i in existing] or [0]
    links = {f["link_discord"]: f["id"] for f in db["findings"] if f.get("link_discord")}
    titles = {norm(f["judul"]): f["id"] for f in db["findings"]}
    new = []
    for n, it in enumerate(items, 1):
        src = {k: v for k, v in it.items() if k != "inbox_id"}
        f = {k: "" for k in FIELDS}
        f.update({k: str(v) for k, v in src.items()})
        f["id"] = f"QA-{max(nums) + n:04d}"
        f["status"] = f["status"] or "Baru"
        f["cc_status"] = f["cc_status"] or "Belum Dicek"
        f["tgl_lapor"] = f["tgl_lapor"] or today()
        if it.get("inbox_id"):
            f["catatan_qa"] = (f["catatan_qa"] + "\n" if f["catatan_qa"] else "") + f"Dari inbox artifact: {it['inbox_id']}"
        errs += [f"baris {n} ({f['judul'][:30]}): {p}" for p in problems(f)]
        if not args.allow_duplicate:
            if f["link_discord"] in links:
                errs.append(f"baris {n}: link Discord sudah dipakai {links[f['link_discord']]} (tambah --allow-duplicate jika memang benar)")
            if norm(f["judul"]) in titles:
                errs.append(f"baris {n}: judul sama dengan {titles[norm(f['judul'])]} (tambah --allow-duplicate jika memang benar)")
        new.append(f)
    if errs:
        die("Tidak bisa menambah:\n  - " + "\n  - ".join(errs))
    print(f"{'ID':<9} {'Priority':<24} Judul")
    for f in new:
        print(f"{f['id']:<9} {(f['priority'] or '-'):<24} {f['judul'][:70]}")
    if not args.yes:
        print(f"\nPRATINJAU: {len(new)} temuan baru belum disimpan. Jalankan ulang dengan --yes (dan --commit).")
        return
    db["findings"] += new
    commit_write(db, args, [f["id"] for f in new], f"tambah {len(new)} temuan baru ({new[0]['id']}..{new[-1]['id']})")


def cmd_update(args, db):
    items, errs = read_list(args.file), []
    by = {f["id"]: f for f in db["findings"]}
    changes = []
    for it in items:
        fid = it.get("id")
        if fid not in by:
            errs.append(f"{fid}: ID tidak ada")
            continue
        bad = [k for k in it if k != "id" and k not in EDITABLE]
        if bad:
            errs.append(f"{fid}: kolom tidak boleh diubah di sini: {bad} (kolom cc_* hanya lewat apply-check)")
            continue
        upd = {k: str(v) for k, v in it.items() if k != "id"}
        errs += [f"{fid}: {p}" for p in problems(upd, partial=True)]
        for k, v in upd.items():
            if by[fid].get(k, "") != v:
                changes.append((fid, k, by[fid].get(k, ""), v))
    if errs:
        die("Tidak bisa mengubah:\n  - " + "\n  - ".join(errs))
    if not changes:
        print("Tidak ada perubahan.")
        return
    for fid, k, old, new in changes:
        print(f"{fid:<9} {k:<18} {old[:30] or '(kosong)'} -> {new[:40]}")
    if not args.yes:
        print(f"\nPRATINJAU: {len(changes)} perubahan belum disimpan. Jalankan ulang dengan --yes (dan --commit).")
        return
    for fid, k, _, new in changes:
        by[fid][k] = new
    ids = sorted({c[0] for c in changes})
    commit_write(db, args, ids, f"ubah {len(changes)} kolom pada {len(ids)} temuan")


def cmd_apply_check(args, db):
    items, errs, seen = read_list(args.file), [], set()
    by = {f["id"]: f for f in db["findings"]}
    for it in items:
        fid = str(it.get("id", ""))
        if fid not in by or fid in seen:
            errs.append(f"{fid}: ID tidak ada atau ganda")
        seen.add(fid)
        if it.get("cc_status") not in CC[1:]:
            errs.append(f"{fid}: cc_status harus salah satu dari {CC[1:]}")
        if not str(it.get("evidence", "")).strip():
            errs.append(f"{fid}: evidence (bukti) wajib diisi")
    if errs:
        die("Hasil tidak valid:\n  - " + "\n  - ".join(errs))
    print(f"{'ID':<9} {'Status temuan':<27} {'CC sebelumnya':<20} -> CC baru")
    for it in items:
        f = by[it["id"]]
        print(f"{f['id']:<9} {(f['status'] or '(kosong)'):<27} {(f['cc_status'] or 'Belum Dicek'):<20} -> {it['cc_status']}")
    if not args.yes:
        print("\nPRATINJAU: belum ada yang ditulis. Jalankan ulang dengan --yes (dan --commit) setelah divalidasi.")
        return
    for it in items:
        f = by[it["id"]]
        f["cc_status"], f["cc_tanggal"], f["cc_bukti"] = it["cc_status"], today(), str(it["evidence"]).strip()[:1500]
    c = Counter(i["cc_status"] for i in items)
    commit_write(db, args, [i["id"] for i in items], f"cek Claude Code {len(items)} temuan (" + ", ".join(f"{k}: {v}" for k, v in c.items()) + ")")


def cmd_dashboard(args, db):
    tpl = (ROOT / "dashboard" / "template.html").read_text(encoding="utf-8")
    if "/*__QA_DATA__*/null" not in tpl:
        die("Penanda /*__QA_DATA__*/null tidak ada di dashboard/template.html")
    payload = json.dumps({"meta": db["meta"], "findings": db["findings"], "history": db.get("history", [])}, ensure_ascii=False).replace("</", "<\\/")
    out = Path(args.out) if args.out else ROOT / "dist" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace("/*__QA_DATA__*/null", payload), encoding="utf-8")
    print(f"Dashboard dibuat: {out} ({len(db['findings'])} temuan, versi data {db['meta']['version']})")


def cmd_export_csv(args, db):
    out = ROOT / "dist" / "qa.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(db["findings"])
    print(f"CSV dibuat: {out}")


def cmd_versions(args, db):
    print(f"Versi data sekarang: {db['meta']['version']}")
    try:
        print(subprocess.run(["git", "tag", "-l", "qa-v*", "--sort=-creatordate"], cwd=ROOT, capture_output=True, text=True).stdout or "(belum ada tag git)")
    except Exception:
        print("(git tidak tersedia)")
    for h in db["history"][-10:]:
        print(f"{h['versi']:<6} {h['tanggal']}  {h['oleh']}: {h['ringkasan']}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=str(DEFAULT_DATA), help="Lokasi qa.json (uji/lanjutan)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate"); sub.add_parser("summary"); sub.add_parser("export-csv"); sub.add_parser("versions")
    l = sub.add_parser("list")
    l.add_argument("--status", action="append"); l.add_argument("--id", action="append")
    l.add_argument("--cc-status", action="append"); l.add_argument("--all", action="store_true")
    for name in ("add", "update", "apply-check"):
        s = sub.add_parser(name); s.add_argument("file")
        s.add_argument("--yes", action="store_true"); s.add_argument("--commit", action="store_true")
        if name == "add":
            s.add_argument("--allow-duplicate", action="store_true")
    d = sub.add_parser("dashboard"); d.add_argument("--out")
    a = p.parse_args()
    db = load(a.data)
    {"validate": cmd_validate, "summary": cmd_summary, "list": cmd_list, "add": cmd_add, "update": cmd_update,
     "apply-check": cmd_apply_check, "dashboard": cmd_dashboard, "export-csv": cmd_export_csv, "versions": cmd_versions}[a.cmd.replace("-", "_") if False else a.cmd](a, db)


if __name__ == "__main__":
    main()
