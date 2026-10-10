#!/usr/bin/env python3
"""
cue-splitter — массовая нарезка образов FLAC+CUE на отдельные треки.

Структура: Корень -> Исполнитель -> Альбом -> *.flac + *.cue
Запуск:
    python split_cue.py "D:\\Музыка\\Muse Japan CD" --dry-run   (только показать, что будет сделано)
    python split_cue.py "D:\\Музыка\\Muse Japan CD"             (выполнить)

Требуется ffmpeg в PATH. Оригиналы (flac + cue) переносятся в подпапку _original.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

SAMPLE_FRAMES_PER_SEC = 75  # в CUE 75 кадров = 1 секунда


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1251", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def unquote(s: str) -> str:
    s = s.strip()
    m = re.match(r'^"(.*)"', s)
    return m.group(1) if m else s.split()[0] if s else ""


def parse_cue(path: Path):
    text = read_text(path)
    album = {"performer": "", "title": "", "date": "", "genre": "", "files": []}
    tracks = []
    cur = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, rest = line.partition(" ")
        key = key.upper()
        if key == "FILE":
            album["files"].append(unquote(rest))
        elif key == "TRACK":
            cur = {"num": int(rest.split()[0]), "title": "", "performer": "", "start": None}
            tracks.append(cur)
        elif key == "TITLE":
            (cur if cur else album)["title"] = unquote(rest)
        elif key == "PERFORMER":
            (cur if cur else album)["performer"] = unquote(rest)
        elif key == "INDEX" and cur is not None:
            idx, _, t = rest.partition(" ")
            if idx == "01":
                mm, ss, ff = (int(x) for x in t.strip().split(":"))
                cur["start"] = mm * 60 + ss + ff / SAMPLE_FRAMES_PER_SEC
        elif key == "REM":
            k, _, v = rest.partition(" ")
            k = k.upper()
            if k == "DATE":
                album["date"] = unquote(v)
            elif k == "GENRE":
                album["genre"] = unquote(v)
    return album, tracks


def safe(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    return name or "_"


def find_flac(folder: Path, cue: Path, album: dict):
    if len(album["files"]) == 1:
        cand = folder / Path(album["files"][0]).name
        if cand.exists():
            return cand
    same = cue.with_suffix(".flac")
    if same.exists():
        return same
    flacs = list(folder.glob("*.flac"))
    return flacs[0] if len(flacs) == 1 else None


def process(folder: Path, cue: Path, dry: bool) -> bool:
    album, tracks = parse_cue(cue)
    if len(album["files"]) != 1:
        print(f"  ПРОПУСК: в CUE {len(album['files'])} FILE-записей (нужна ровно одна)")
        return False
    if not tracks or any(t["start"] is None for t in tracks):
        print("  ПРОПУСК: не удалось прочитать треки из CUE")
        return False
    flac = find_flac(folder, cue, album)
    if flac is None:
        print("  ПРОПУСК: не найден FLAC-файл")
        return False

    total = len(tracks)
    outputs = []
    for i, t in enumerate(tracks):
        end = tracks[i + 1]["start"] if i + 1 < total else None
        artist = t["performer"] or album["performer"]
        out = folder / f"{t['num']:02d}. {safe(t['title'] or 'Track ' + str(t['num']))}.flac"
        outputs.append(out)

        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-ss", f"{t['start']:.6f}"]
        if end is not None:
            cmd += ["-t", f"{end - t['start']:.6f}"]
        cmd += ["-i", str(flac), "-vn", "-map_metadata", "-1", "-c:a", "flac",
                "-metadata", f"TITLE={t['title']}",
                "-metadata", f"ARTIST={artist}",
                "-metadata", f"ALBUM={album['title']}",
                "-metadata", f"ALBUMARTIST={album['performer']}",
                "-metadata", f"TRACKNUMBER={t['num']}",
                "-metadata", f"TRACKTOTAL={total}"]
        if album["date"]:
            cmd += ["-metadata", f"DATE={album['date']}"]
        if album["genre"]:
            cmd += ["-metadata", f"GENRE={album['genre']}"]
        cmd.append(str(out))

        print(f"  {out.name}")
        if not dry:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0 or not out.exists() or out.stat().st_size == 0:
                print(f"  ОШИБКА ffmpeg: {r.stderr.strip()}")
                for o in outputs:  # откат: удаляем то, что успели создать
                    o.unlink(missing_ok=True)
                return False

    if not dry:
        orig = folder / "_original"
        orig.mkdir(exist_ok=True)
        shutil.move(str(flac), str(orig / flac.name))
        shutil.move(str(cue), str(orig / cue.name))
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Массовая нарезка образов FLAC+CUE на отдельные треки.")
    ap.add_argument("root", type=Path, help="корневая папка с музыкой")
    ap.add_argument("--dry-run", action="store_true",
                    help="только показать, что будет сделано")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg не найден в PATH. Установите: winget install Gyan.FFmpeg")

    done = skipped = 0
    for cue in sorted(args.root.rglob("*.cue")):
        folder = cue.parent
        if "_original" in folder.parts:
            continue
        print(f"\n{folder}")
        if process(folder, cue, args.dry_run):
            done += 1
        else:
            skipped += 1
    print(f"\nГотово: обработано {done}, пропущено {skipped}"
          + (" (пробный запуск, ничего не изменено)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
