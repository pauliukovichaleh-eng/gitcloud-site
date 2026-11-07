#!/usr/bin/env python3
"""Kontrola tekstu NA obrazach i filmach przed nocnym wdrożeniem (decyzja #749): check.mjs widzi tylko tekst strony,
a nazwisko klienta czy adres IP na zrzucie by przeszły. Tesseract (pol+eng+rus) czyta każdy podany plik:
obraz w 2x, film co 2 s (ffmpeg). Szuka słów z FORBIDDEN w check.mjs, z ocr-zakazane.txt i prywatnych adresów IP.
  ~/job-hunter/.venv/bin/python -I tools/odswiez/ocr.py PLIK...   (Pillow)      → kod 1 i lista trafień, kod 0 gdy czysto"""
import pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
words = re.findall(r"'([^']+)'", re.search(r"FORBIDDEN = \[(.*?)\];", (HERE.parent / "check.mjs").read_text(), re.S).group(1))
extra = HERE / "ocr-zakazane.txt"
words += [w.strip().lower() for w in extra.read_text().splitlines() if w.strip() and not w.startswith("#")] if extra.exists() else []
IP = re.compile(r"\b(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b")

def frames(f: pathlib.Path, tmp: str) -> list[str]:
    if f.suffix == ".mp4":
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(f), "-vf", "fps=1/2,scale=iw*2:-1", f"{tmp}/{f.stem}_%03d.png"], check=True)
        return sorted(str(p) for p in pathlib.Path(tmp).glob(f"{f.stem}_*.png"))
    from PIL import Image                                   # obrazy, też animowane WebP/GIF (co 15. klatka)
    im, out = Image.open(f), []
    for i in range(0, getattr(im, "n_frames", 1), 15):
        im.seek(i)
        fr = im.convert("RGB"); fr = fr.resize((fr.width * 2, fr.height * 2))
        out.append(f"{tmp}/{f.stem}_{i:03d}.png"); fr.save(out[-1])
    return out

bad = []
for arg in sys.argv[1:]:
    f = pathlib.Path(arg)
    if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4") or not f.exists():
        continue
    with tempfile.TemporaryDirectory() as tmp:
        for png in frames(f, tmp):
            txt = subprocess.run(["tesseract", png, "-", "-l", "pol+eng+rus", "--psm", "11"], capture_output=True, text=True).stdout
            low = txt.lower()
            # konsola ISP pokazuje wymyśloną sieć operatora (10.10/10.20/10.30): tam adresy są treścią, nazwy nadal sprawdzane
            hits = [w for w in words if w in low] + ([] if "/img/demo/" in str(f) else IP.findall(txt))
            if hits:
                bad.append(f"{f}: {', '.join(sorted(set(hits)))}")
                break
print("\n".join(bad) if bad else f"ocr: czysto ({len(sys.argv) - 1} plików)")
sys.exit(1 if bad else 0)
