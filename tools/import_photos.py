#!/usr/bin/env python3
"""
Scan photos/ and turn every image into a sightings.json entry.

The species name is taken from the file name, so name your photos after the
bird — the matcher is forgiving about separators, capitals and word order:

    photos/north-island-robin-01.jpg   -> Petroica longipes
    photos/Petroica_longipes_2.jpg     -> Petroica longipes
    photos/2026-01-14 tui zealandia.jpg-> Prosthemadera novaeseelandiae

Date and coordinates come from the photo's EXIF where present.

    python3 tools/import_photos.py                 # preview what it found
    python3 tools/import_photos.py --write         # merge into data/sightings.json
    python3 tools/import_photos.py --place "Zealandia, Wellington"

Needs Pillow:  pip install Pillow
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECIES = ROOT / "data" / "species.json"
SIGHTINGS = ROOT / "data" / "sightings.json"
PHOTOS = ROOT / "photos"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}

STOP = {"img", "dsc", "dscn", "p", "photo", "pic", "copy", "edit", "final", "raw"}


def tokens(text):
    text = re.sub(r"[^A-Za-z]+", " ", text).lower()
    out = []
    for w in text.split():
        if len(w) < 3 or w in STOP:
            continue
        out.append(w)
    return out


def load_species():
    db = json.loads(SPECIES.read_text(encoding="utf-8"))
    rows = []
    for r in db["species"]:
        sci, en = r[0], r[1]
        rows.append((sci, en, set(tokens(en)) | set(tokens(sci))))
    return rows


def match(stem, rows):
    want = set(tokens(stem))
    if not want:
        return None, 0.0
    best, score = None, 0.0
    for sci, en, toks in rows:
        hit = want & toks
        if not hit:
            continue
        # reward covering the species' own words, not just any overlap
        s = len(hit) / len(toks) + 0.35 * (len(hit) / len(want))
        if s > score:
            best, score = (sci, en), s
    return best, score


def exif(path):
    try:
        from PIL import Image, ExifTags
    except ImportError:
        return {}
    try:
        img = Image.open(path)
        raw = img.getexif()
        if not raw:
            return {}
        out = {}
        tag = {v: k for k, v in ExifTags.TAGS.items()}
        dt = raw.get(tag.get("DateTime")) or None
        ifd = raw.get_ifd(0x8769)
        dt = ifd.get(tag.get("DateTimeOriginal"), dt)
        if dt:
            m = re.match(r"(\d{4})[:\-](\d{2})[:\-](\d{2})", str(dt))
            if m:
                out["date"] = "-".join(m.groups())
        gps = raw.get_ifd(0x8825)
        if gps:
            def dms(v):
                return float(v[0]) + float(v[1]) / 60 + float(v[2]) / 3600
            if 2 in gps and 4 in gps:
                lat = dms(gps[2]) * (-1 if str(gps.get(1, "N")).upper().startswith("S") else 1)
                lon = dms(gps[4]) * (-1 if str(gps.get(3, "E")).upper().startswith("W") else 1)
                out["lat"] = round(lat, 6)
                out["lon"] = round(lon, 6)
        return out
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="merge results into data/sightings.json")
    ap.add_argument("--place", default="", help="place name to apply to every entry")
    ap.add_argument("--min-score", type=float, default=0.55, help="name-match threshold")
    args = ap.parse_args()

    if not PHOTOS.is_dir():
        sys.exit("No photos/ folder found next to this script.")

    rows = load_species()
    found, unmatched = [], []

    for p in sorted(PHOTOS.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        best, score = match(p.stem, rows)
        rel = "photos/" + str(p.relative_to(PHOTOS)).replace("\\", "/")
        if not best or score < args.min_score:
            unmatched.append((rel, score))
            continue
        rec = {"sci": best[0], "date": "", "place": args.place, "photo": rel}
        rec.update(exif(p))
        rec = {k: rec[k] for k in ("sci", "date", "place", "lat", "lon", "photo") if k in rec}
        found.append((rec, best[1], score))

    for rec, en, score in found:
        bits = [rec["sci"], f"({en})", rec.get("date") or "no date"]
        if "lat" in rec:
            bits.append(f'{rec["lat"]:.4f}, {rec["lon"]:.4f}')
        else:
            bits.append("no GPS")
        print(f'  {rec["photo"]:<45} -> {" · ".join(bits)}')

    if unmatched:
        print("\nCould not name these from the file name:")
        for rel, score in unmatched:
            print(f"  {rel}  (best score {score:.2f})")

    print(f"\n{len(found)} matched, {len(unmatched)} unmatched.")

    if not args.write:
        print("Nothing written. Re-run with --write to merge into data/sightings.json.")
        return

    existing = []
    if SIGHTINGS.exists():
        try:
            existing = json.loads(SIGHTINGS.read_text(encoding="utf-8")) or []
        except json.JSONDecodeError:
            sys.exit("data/sightings.json is not valid JSON — fix it before writing.")

    have = {(r.get("sci"), r.get("photo")) for r in existing}
    added = [rec for rec, _, _ in found if (rec["sci"], rec.get("photo")) not in have]
    existing.extend(added)
    SIGHTINGS.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {len(added)} new records. data/sightings.json now holds {len(existing)}.")


if __name__ == "__main__":
    main()
