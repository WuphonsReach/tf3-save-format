#!/usr/bin/env python3
"""Index of a player's game screenshots: UTC time, what each cluster shows, the saves written
around it, and the text read off the pictures. Private work files only: see "Privacy".

Usage:
  screenshot_index.py --work DIR [options] COMMAND

Commands:
  ocr           read the text off every shot (tesseract) into DIR/ocr/, once per shot and bar engine;
                also marks the game's loading screens (see below), a quick pass over shots already read
  todo          list the clusters of shots that no label covers yet, each with a hint whether its first
                shot looks like the same static view as the shot before it (edge correlation, needs
                numpy and Pillow; a long watch with shots 5 to 10 minutes apart is one cluster)
  sheets        contact sheets, 12 shots each, into --out (to read a cluster at a glance)
  build         write DIR/INDEX.md from DIR/labels.tsv, the OCR text and the saves
  find TERM..   shots whose OCR text holds every term (case-insensitive), with the cluster's label
  check         label facts (quoted names, "Name (123)" town labels, dates, dollar figures) that no
                shot of the cluster shows in its OCR text, and the share found
  hud           DIR/hud.csv: game date, account, earnings, people delivered and cargo delivered (totals
                since the game started) read off each shot's bottom bar

Options:
  --work DIR      where labels.tsv, INDEX.md, hud.csv and the OCR cache live (or env
                  TF3_SCREENSHOT_WORK). Name a folder git ignores.
  --shots DIR     the screenshot folder (or env TF3_SCREENSHOTS). Default: ~/Pictures/Screenshots,
                  then ~/Pictures, the first that holds images.
  --saves-dir DIR a folder of .sav files whose write times go next to the clusters; repeatable.
                  Default: the game's `save` and `save_maps` folders in the usual Steam places
                  (app 3493540). With none found the index simply has no save column.
  --date YYYYMMDD limit to shots of that local date; repeatable
  --jobs N        tesseract processes in parallel for `ocr` (default: up to 8)
  --hud-engine E  tesseract (default) or rapidocr: the engine that reads the bottom bar in `ocr`
  --out DIR       where `sheets` writes
  --no-nice       keep the normal priority (see below)

Priority: the script lowers its own priority at start (nice 19, and idle I/O when `ionice` is installed; the
tesseract and other child processes inherit it), so an `ocr` pass over thousands of 4K frames leaves the
machine usable and needs no `nice` prefix. `--no-nice` keeps the normal priority.

Shot names: Spectacle (`Screenshot_YYYYMMDD_HHMMSS.png`), GNOME (`Screenshot from YYYY-MM-DD
HH-MM-SS.png`), Windows (`Screenshot YYYY-MM-DD HHMMSS.png`) and Steam (`APPID_YYYYMMDDHHMMSS_N.png`)
carry the local time; any other .png/.jpg uses its file time. Shots are read from the folder itself and from
any folder below its `tf3` subfolder (the game's shots are filed into `tf3/YYYY-MM-DD/`). A shot's id is its local date and time,
`YYYYMMDD_HHMMSS`; the index prints UTC (local time to UTC by the system's time zone rules). The id and the OCR
cache follow the file name, not the folder, so filing a shot into a day folder, or moving it between them,
costs no new read; two shots of the same second get `-2`, `-3` in file-name order.

Loading screens: a shot of the game's load card (a save or a map-editor map loading) has black bars at the
top and bottom, a picture between them, the save's name centred in the top bar, a tip at the bottom and a
percentage or a Start Game button at the lower right. `ocr` finds them by that layout alone (the picture
changes from load to load), keeps the title, the percentage or button in the cache, and `build` lists them
in a "Loading screens" section (title, game or editor save by matching the save's name, shots, ids). They
count as categorized: `todo` and the UNLABELLED clusters skip them, and `find "loading screen"` lists them.

Labels are ranges of shots, because shots come in clusters of one subject. DIR/labels.tsv, kept by
hand or by a session and never written by this script, one row per range, tab separated:

  first  last  game  topic  what  points of interest  sure  links

first and last are ids and the range is inclusive. A row inside a wider row (or a single shot) is a
per-shot note shown under it. `game` follows the seed-climate-label naming (`-` for none); `topic` is
comma separated words that feed the topic table; `sure` is read (text legible), seen (clear from
the picture) or guess (thumbnail only); `links` are `;`-separated notes. Lines starting with # are
comments.

OCR needs the tesseract binary and Pillow (imported only by `ocr` and `sheets`, like numpy and Pillow
in town_centre.py; see tools/README.md). The other commands use the standard library only.
`--hud-engine rapidocr` reads the bottom bar with the `rapidocr` and `onnxruntime` packages instead
(pip install rapidocr onnxruntime; imported only then, and its models ship inside the wheel). On 4K
frames it read the account, earnings and both totals right where the tesseract bar pass lost the
account figure. When the account is still missing, a digits-only tesseract read of the crop at the bar's
left end fills it in; the crop is placed by fractions of the 4K bar and was only checked at 3840x2160. The bottom
bar of a full-screen game frame gives the HUD figures: treat them as OCR reads and look at a picture
before relying on a number. A pass that takes over 60 s (textured ground with no text) is skipped and the
shot's cache entry says `slow`. A load card shows the save's real date, not the game date.

Privacy: shots show company names, install paths and account folders, and saves have names and
write times. The OCR text is masked on the way in (paths become `<path>`, "<name> Transport" a company
name) and the output prints no folder path, but INDEX.md and the cache are still private working files:
keep DIR out of git, and never copy a company or account name from them into a note or commit.
Reads screenshots and the saves' file times; writes only into DIR and --out.
"""
import argparse
import bisect
import collections
import concurrent.futures
import csv
import datetime as dt
import glob
import io
import json
import os
import re
import subprocess
import sys
import threading

APP_ID = "3493540"
STEAM_ROOTS = ("~/.steam/steam", "~/.local/share/Steam", "~/snap/steam/common/.local/share/Steam",
               "~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
SHOT_DIRS = ("~/Pictures/Screenshots", "~/Pictures")
UTC = dt.timezone.utc
GAP = 120            # seconds between two shots that start a new cluster
SAVE_WINDOW = 240    # seconds either side of a cluster in which a save counts as "around"
OCR_VERSION = 3      # bump to make `ocr` redo cached shots
CONF = 70            # tesseract word confidence kept on the plain pass; 60 on the upscaled pass
TIMEOUT = 60         # seconds for one tesseract pass; textured frames without text can take minutes

NAME_PATTERNS = (    # (regex, groups: date, time) -> local time in the file name
    (re.compile(r"Screenshot_(\d{8})_(\d{6})"), lambda m: m.group(1) + m.group(2)),
    (re.compile(r"Screenshot from (\d{4})-(\d\d)-(\d\d) (\d\d)-(\d\d)-(\d\d)"), lambda m: "".join(m.groups())),
    (re.compile(r"Screenshot[ _](\d{4})-(\d\d)-(\d\d)[ _](\d\d)(\d\d)(\d\d)"), lambda m: "".join(m.groups())),
    (re.compile(r"\d+_(\d{8})(\d{6})_\d+"), lambda m: m.group(1) + m.group(2)),
)
IMAGE_EXT = (".png", ".jpg", ".jpeg")

DATE_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}), (\d{4})\b")
# A town label: name, then the population and the growth arrow (read as a digit or a caret).
LABEL_RE = re.compile(r"\b([A-Z][A-Za-z'.-]+(?: [A-Z][A-Za-z'.-]+){0,3}) \((\d{1,4})(?: ?[\^4])?\)")
NUM_RE = re.compile(r"(?<![\d,])(\d{1,3}(?:,\d{3})+|\d+)(?![\d,])")
TITLE_WORDS = ("Depot", "Station", "Maintenance", "Landing", "Grounds", "Platform", "Dredger", "Crossing",
               "Loading Report", "Industrial Building", "Settings", "Account", "Terrain", "Infrastructure",
               "Traffic Flow", "Towns", "Industries", "Obtained", "Load Game", "Welcome")
PATH_RE = re.compile(r"(?:/home/|/Users/|[A-Za-z]:\\)\S+|\S*userdata/\d+\S*")
COMPANY_RE = re.compile(r"\b[\w'.-]+ Transport\b")
COMPANY_KEEP = ("Public", "Fever")


def redact(line):
    """Mask install paths, account folders and the default company name in text read off a picture."""
    line = PATH_RE.sub("<path>", line)
    return COMPANY_RE.sub(lambda m: m.group(0) if m.group(0).split()[0] in COMPANY_KEEP else "<name> Transport",
                          line)


# ---------------------------------------------------------------- where things are

def lower_priority():
    """Nice 19 and idle I/O for this process and the children it starts; best effort."""
    try:
        os.nice(19)
        subprocess.run(["ionice", "-c3", "-p", str(os.getpid())], check=False, stderr=subprocess.DEVNULL)
    except (OSError, AttributeError):
        pass


def die(msg):
    sys.exit("screenshot_index.py: " + msg)


def work_dir(arg):
    path = arg or os.environ.get("TF3_SCREENSHOT_WORK")
    if not path:
        die("name a work folder with --work DIR (or TF3_SCREENSHOT_WORK); keep it out of git")
    os.makedirs(path, exist_ok=True)
    return path


def has_images(path):
    try:
        return any(True for _ in shot_files(path))
    except OSError:
        return False


def shots_dir(arg):
    cands = [arg or os.environ.get("TF3_SCREENSHOTS")] if (arg or os.environ.get("TF3_SCREENSHOTS")) else SHOT_DIRS
    for c in cands:
        c = os.path.expanduser(c)
        if has_images(c):
            return c
    die("no screenshot folder with images found; name one with --shots DIR (or TF3_SCREENSHOTS)")


def game_dirs(saves_args):
    """[(folder of .sav files, 'game' or 'editor')]: the named folders, else the game's save folders."""
    if saves_args:
        return [(os.path.expanduser(d), "game") for d in saves_args]
    out = []
    for root in STEAM_ROOTS:
        for local in glob.glob(os.path.join(os.path.expanduser(root), "userdata", "*", APP_ID, "local")):
            for sub, kind in (("save", "game"), ("save_maps", "editor")):
                if os.path.isdir(os.path.join(local, sub)):
                    out.append((os.path.join(local, sub), kind))
    return out


def local_to_utc(naive):
    return naive.astimezone(UTC)     # a naive time is read as the system's local time, DST included


Shot = collections.namedtuple("Shot", "id utc path")


def shot_files(folder):
    """(name, path) of the images in `folder` and, below its `tf3` subfolder, in the day folders
    (`tf3/YYYY-MM-DD/`) that older shots are filed into."""
    for f in os.listdir(folder):
        if f.lower().endswith(IMAGE_EXT) and os.path.isfile(os.path.join(folder, f)):
            yield f, os.path.join(folder, f)
    for root, _dirs, names in os.walk(os.path.join(folder, "tf3")):
        for f in names:
            if f.lower().endswith(IMAGE_EXT):
                yield f, os.path.join(root, f)


def list_shots(folder, dates):
    out, seen = [], set()
    for f, path in sorted(shot_files(folder)):      # file name first: a filed shot keeps its id
        naive = None
        for rx, digits in NAME_PATTERNS:
            m = rx.search(f)
            if m:
                naive = dt.datetime.strptime(digits(m), "%Y%m%d%H%M%S")
                break
        if naive is None:
            naive = dt.datetime.fromtimestamp(os.path.getmtime(path))
        sid, n = naive.strftime("%Y%m%d_%H%M%S"), 1
        while sid in seen:
            n += 1
            sid = naive.strftime("%Y%m%d_%H%M%S") + f"-{n}"
        seen.add(sid)
        if not dates or sid[:8] in dates:
            out.append(Shot(sid, local_to_utc(naive), path))
    return sorted(out, key=lambda s: (s.utc, s.id))


def list_saves(dirs):
    rows = []
    for d, kind in dirs:
        for p in glob.glob(os.path.join(d, "*.sav")):
            rows.append((dt.datetime.fromtimestamp(os.path.getmtime(p), UTC), os.path.basename(p)[:-4], kind))
    return sorted(rows)


def load_labels(work):
    rows, path = [], os.path.join(work, "labels.tsv")
    if os.path.exists(path):
        with open(path, newline="") as fh:
            for r in csv.reader(fh, delimiter="\t"):
                if r and not r[0].startswith("#") and len(r) >= 5:
                    rows.append((r + [""] * 8)[:8])
    return rows


def hms(t):
    return t.strftime("%H:%M:%S")


# ---------------------------------------------------------------- OCR

TESS_ENV = dict(os.environ, OMP_THREAD_LIMIT="1")   # one thread per call; the pool supplies the parallelism


def tesseract(img_path, psm, tsv=False):
    """The program's text, or None when the pass took longer than TIMEOUT."""
    cmd = ["tesseract", img_path, "-", "--psm", str(psm)] + (["tsv"] if tsv else [])
    try:
        return subprocess.run(cmd, capture_output=True, text=True, env=TESS_ENV, timeout=TIMEOUT).stdout
    except FileNotFoundError:
        die("the tesseract program is not installed (ocr needs it)")
    except subprocess.TimeoutExpired:
        return None


def tsv_lines(img_path, psm, min_conf):
    """Lines of words above min_conf, or None when tesseract timed out."""
    out = tesseract(img_path, psm, tsv=True)
    if out is None:
        return None
    lines = {}
    for r in csv.DictReader(io.StringIO(out), delimiter="\t", quoting=csv.QUOTE_NONE):
        txt = (r.get("text") or "").strip()
        try:
            conf = float(r["conf"])
        except (TypeError, ValueError):
            continue
        if txt and conf >= min_conf:
            lines.setdefault((r["block_num"], r["par_num"], r["line_num"]), []).append(txt)
    return [" ".join(v) for v in lines.values()]


def to_int(s):
    return int(s.replace(",", "").replace("$", ""))


ACCOUNT_BOX = (0.0, 0.25, 0.14, 0.9)   # the account figure: x as a share of the width, y as a share of the bar


def account_crop(g, tmp):
    """The account figure read alone, digits and commas only, or "" when nothing grouped like a figure comes
    out (a bar with no account, such as under a menu, would otherwise give the "?" button as a digit).
    `g` is the grey frame. The coin icon left of the figure reads as a stray digit with a wider box."""
    from PIL import Image, ImageOps
    w, h = g.size
    bar = h * 0.06
    x0, y0, x1, y1 = ACCOUNT_BOX
    c = ImageOps.autocontrast(g.crop((int(x0 * w), int(h - bar + y0 * bar), int(x1 * w), int(h - bar + y1 * bar))))
    c = ImageOps.expand(c.resize((c.width * 4, c.height * 4), Image.LANCZOS), border=20, fill=0)
    c.save(tmp)
    cmd = ["tesseract", tmp, "-", "--psm", "7", "-c", "tessedit_char_whitelist=0123456789,"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, env=TESS_ENV, timeout=TIMEOUT).stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    return out if re.fullmatch(r"\d{1,3}(?:,\d{3})+", out) else ""


_rapid = None
_rapid_lock = threading.Lock()


def rapidocr_text(img):
    """The bar's text from RapidOCR, boxes joined by " | " in reading order (empty when it found none).
    `img` is a PIL image. One engine is shared; its calls are serialised."""
    global _rapid
    with _rapid_lock:
        if _rapid is None:
            try:
                from rapidocr import RapidOCR
            except ImportError:
                die("--hud-engine rapidocr needs the rapidocr and onnxruntime packages (pip install rapidocr onnxruntime)")
            _rapid = RapidOCR(params={"Global.log_level": "critical"})
        import numpy
        out = _rapid(numpy.asarray(img.convert("RGB")))
    return " | ".join(out.txts) if out.txts else ""


def parse_hud(band_text, text_lines):
    """The bottom bar of a full-screen game frame: earnings, people delivered, cargo delivered (both totals
    since the game started), account, date."""
    hud = {}
    m = re.search(r"Earnings\s*(\$\s*-?|-\s*\$)\s*([\d,]+)", band_text)
    if m:
        hud["earnings"] = to_int(m.group(2)) * (-1 if "-" in m.group(1) else 1)
        tail = band_text[m.end():]
        dm = DATE_RE.search(tail)
        nums = NUM_RE.findall(tail[:dm.start()] if dm else tail)
        if len(nums) >= 2:
            hud["people"], hud["box"] = to_int(nums[0]), to_int(nums[1])
    acc = re.search(r"\d{1,3}(?:,\d{3}){2,}", band_text[:m.start()] if m else band_text)
    if not acc:                                   # the account is a line a few lines after "Account"
        for k, ln in enumerate(text_lines):
            if "Account" in ln:
                for nxt in text_lines[k:k + 12]:
                    acc = re.fullmatch(r"\d{1,3}(?:,\d{3})+", nxt.strip())
                    if acc:
                        break
                break
    if acc:
        hud["account"] = to_int(acc.group(0))
    dm = DATE_RE.search(band_text)
    if dm:
        hud["date"] = dm.group(0)
    return hud


def ocr_one(path, tmp, engine="tesseract"):
    """Tesseract on the frame as it is, on the frame upscaled (small label text), and on the bottom bar."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        die("ocr needs Pillow (pip install pillow); see tools/README.md")
    slow = False
    first = tsv_lines(path, 11, CONF)
    slow = first is None
    text = [redact(x) for x in first or []]
    with Image.open(path) as im:
        w, h = im.size
        g = im.convert("L")
        k = 4 if max(w, h) < 2000 else 3 if max(w, h) < 3000 else 2
        ImageOps.autocontrast(g.resize((w * k, h * k), Image.LANCZOS)).save(tmp)
        seen = {x.lower() for x in text}
        second = tsv_lines(tmp, 11, CONF - 10)
        slow = slow or second is None
        for ln in second or []:
            ln = redact(ln)
            if ln.lower() not in seen:
                text.append(ln)
                seen.add(ln.lower())
        hud, band_text = {}, ""
        if w >= 3000 or (w >= 2000 and h >= 1100):
            if engine == "rapidocr":
                band_text = rapidocr_text(im.crop((0, int(h * .94), w, h)))
            else:
                band = ImageOps.autocontrast(g.crop((0, int(h * .94), w, h)))
                band.resize((band.width * 2, band.height * 2)).save(tmp)
                band_text = tesseract(tmp, 6) or ""
            hud = parse_hud(band_text, text)
            if "earnings" in hud and "account" not in hud:
                acc = account_crop(g, tmp)
                if acc:
                    hud["account"] = to_int(acc)
    date = hud.get("date", "")
    if not date:
        m = DATE_RE.search("\n".join(text))
        date = m.group(0) if m else ""
    return {"v": OCR_VERSION, "text": text, "date": date, "hud": hud, "hud_engine": engine,
            **({"slow": True} if slow else {})}


LOAD_VERSION = 2     # bump to make `ocr` redo the loading-screen pass on cached shots
BAR_DARK = 25        # grey level under which a pixel of a bar counts as black (of 255)


def dark_share(g, box):
    """Share of pixels darker than BAR_DARK in a box given as fractions (x0, y0, x1, y1) of the frame."""
    w, h = g.size
    hist = g.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3]))).histogram()
    return sum(hist[:BAR_DARK]) / max(1, sum(hist))


def detect_loading(path, tmp):
    """The loading-screen layout test: {} for any other shot, else the title read off the top bar and the
    percentage or button at the lower right. The bars are black over almost all their width, the picture
    between them is not."""
    from PIL import Image, ImageOps
    with Image.open(path) as im:
        g = im.convert("L")
        g.thumbnail((384, 384))
        band = 1 - dark_share(g, (0.01, 0.2, 0.99, 0.8))
        if dark_share(g, (0, 0.01, 1, 0.17)) < .9 or dark_share(g, (0, 0.84, 1, 0.99)) < .9 or band < .5:
            return {}
        full = im.convert("L")
    w, h = full.size
    out = {}
    for key, box, psm in (("title", (0.03, 0.05, 0.97, 0.14), 7), ("corner", (0.84, 0.88, 1.0, 0.94), 7)):
        crop = ImageOps.autocontrast(full.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3]))))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        crop.save(tmp)
        out[key] = redact(" ".join((tesseract(tmp, psm) or "").split()))
    m = re.search(r"(\d{1,3}) ?%", out.pop("corner"))
    if m:
        out["progress"] = int(m.group(1))
    else:
        out["button"] = "Start Game"        # no percentage: the card waits for the player
    return out


def load_ocr(work, sid):
    try:
        with open(os.path.join(work, "ocr", sid + ".json")) as fh:
            d = json.load(fh)
    except OSError:
        return None
    d["text"] = [redact(x) for x in d["text"]]       # masked on the way out too
    return d


def cmd_ocr(work, shots, jobs, engine="tesseract"):
    cache = os.path.join(work, "ocr")
    os.makedirs(cache, exist_ok=True)
    todo = [s for s in shots if (load_ocr(work, s.id) or {}).get("v", 0) < OCR_VERSION
            or (load_ocr(work, s.id) or {}).get("hud_engine", "tesseract") != engine]

    def work_one(s):
        d = ocr_one(s.path, os.path.join(cache, f"_tmp_{s.id}.png"), engine)
        os.remove(os.path.join(cache, f"_tmp_{s.id}.png"))
        with open(os.path.join(cache, s.id + ".json"), "w") as fh:
            json.dump(d, fh)

    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        for n, _ in enumerate(ex.map(work_one, todo), 1):
            if n % 50 == 0:
                print(n, "of", len(todo), file=sys.stderr)
    print(f"ocr: {len(todo)} new, {len(shots)} shots in range")
    older = [s for s in shots if (load_ocr(work, s.id) or {}).get("load_v", 0) < LOAD_VERSION]

    def mark(s):
        d = load_ocr(work, s.id)
        d["load_v"] = LOAD_VERSION
        tmp = os.path.join(cache, f"_tmp_{s.id}.png")
        found = detect_loading(s.path, tmp)
        if os.path.exists(tmp):
            os.remove(tmp)
        d.pop("loading", None)
        if found:
            d["loading"] = found
        with open(os.path.join(cache, s.id + ".json"), "w") as fh:
            json.dump(d, fh)
        return bool(found)

    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        n = sum(ex.map(mark, older))
    print(f"loading screens: {len(older)} shots checked, {n} found")


def ocr_summary(work, ids):
    """Game dates, HUD figures, town labels and window titles seen across a cluster's shots."""
    dates, labels, titles, hud = [], {}, {}, {}
    for sid in ids:
        d = load_ocr(work, sid)
        if not d:
            continue
        if d["date"]:
            dates.append(d["date"])
        for k, v in (d.get("hud") or {}).items():
            if k != "date":
                hud.setdefault(k, []).append(v)
        for ln in d["text"]:
            for m in LABEL_RE.finditer(ln):
                if m.group(1).split()[-1] not in ("Mods", "Level", "Phase"):
                    labels[m.group(0)] = labels.get(m.group(0), 0) + 1
            for k in TITLE_WORDS:
                if k in ln and 3 < len(ln) < 60 and not re.search(r"\d{3,}", ln):
                    titles[ln] = titles.get(ln, 0) + 1
    out = []
    names = (("account", "account"), ("earnings", "earnings"), ("people", "people delivered"), ("box", "cargo delivered"))
    parts = [f"{n} {v[0]:,}" if min(v) == max(v) else f"{n} {min(v):,} to {max(v):,}"
             for k, n in names for v in [hud.get(k)] if v]
    if parts:
        out.append("HUD " + ", ".join(parts))
    if dates:
        ds = sorted(set(dates), key=lambda x: dt.datetime.strptime(x, "%b %d, %Y"))
        real = [d for d in ds if d.endswith(str(dt.date.today().year))]     # a load card shows the real date
        game = [d for d in ds if d not in real]
        if game:
            out.append("game date " + (game[0] if len(game) == 1 else f"{game[0]} to {game[-1]}"))
        if real:
            out.append("save-card date " + real[0])
    if labels:
        out.append("labels " + ", ".join(k for k, _ in sorted(labels.items(), key=lambda kv: -kv[1])[:8]))
    if titles:
        out.append("titles " + "; ".join(k for k, _ in sorted(titles.items(), key=lambda kv: -kv[1])[:6]))
    return out


# ---------------------------------------------------------------- labels, clusters, index

def positions(shots, labels):
    pos = {s.id: i for i, s in enumerate(shots)}
    return pos, [r for r in labels if r[0] in pos and r[1] in pos]


def nest(labels, pos):
    """Split label rows into clusters (top) and the per-shot rows inside a wider one (nested)."""
    top, nested = [], {}
    for r in sorted(labels, key=lambda r: (pos[r[0]], -(pos[r[1]] - pos[r[0]]))):
        t = top[-1] if top else None
        if t and pos[r[0]] >= pos[t[0]] and pos[r[1]] <= pos[t[1]] and (pos[r[0]], pos[r[1]]) != (pos[t[0]], pos[t[1]]):
            nested.setdefault(t[0], []).append(r)
        else:
            top.append(r)
    return top, nested


def unlabelled(shots, covered):
    """Runs of uncovered shots (no more than GAP seconds apart), as (first index, last index)."""
    runs, i = [], 0
    while i < len(shots):
        if i in covered:
            i += 1
            continue
        j = i
        while j + 1 < len(shots) and j + 1 not in covered and (shots[j + 1].utc - shots[j].utc).total_seconds() <= GAP:
            j += 1
        runs.append((i, j))
        i = j + 1
    return runs


def save_lines(first, last, saves, times):
    lo, hi = first - dt.timedelta(seconds=SAVE_WINDOW), last + dt.timedelta(seconds=SAVE_WINDOW)
    during = [s for s in saves if lo <= s[0] <= hi]
    out, auto = [], {}
    plain = [n for _, n, _ in during if not n.startswith("autosave_")]
    pre = os.path.commonprefix(plain) if len(plain) > 1 else ""
    pre = pre[:pre.rfind(" ") + 1] if " " in pre else ""
    if pre:
        out.append("series " + pre.strip()[:60])
    for t, n, kind in during:
        if n.startswith("autosave_"):
            auto.setdefault(re.sub(r"_\d+\.?$|_\d{4}-\d{2}-\d{2}.*$", "", n[9:]), []).append(t)
        else:
            out.append(f'{n[len(pre):]} ({hms(t)}{", editor" if kind == "editor" else ""})')
    for k, v in auto.items():
        out.append(f"{len(v)} autosave(s) of {k[:40]} ({hms(v[0])} to {hms(v[-1])})")
    if not during and saves:
        i = bisect.bisect_right(times, first)
        if i:
            out.append(f'none within {SAVE_WINDOW // 60} min; before: {saves[i - 1][1][:60]} ({saves[i - 1][0]:%m-%d %H:%M:%S})')
        k = bisect.bisect_left(times, last)
        if k < len(saves):
            out.append(f"after: {saves[k][1][:60]} ({saves[k][0]:%m-%d %H:%M:%S})")
    return out


def loading_shots(work, shots):
    """Index -> the loading-screen entry of each shot the layout test marked."""
    return {i: d["loading"] for i, s in enumerate(shots) for d in [load_ocr(work, s.id) or {}] if d.get("loading")}


def squash(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_kind(title, saves):
    """Which folders hold a save whose name matches the card's title (the card adds nothing but spacing and
    a date stamp the save name may already carry): game, editor, both, or neither."""
    t = squash(title)
    kinds = {kind for _, name, kind in saves
             for n in [squash(name)] if t and n and (t == n or t.startswith(n) or n.startswith(t))}
    if kinds == {"game"}:
        return "game save"
    if kinds == {"editor"}:
        return "editor save"
    return "game or editor save (both folders hold that name)" if kinds else "unknown (no save of that name found)"


def loading_section(work, shots, loads, saves):
    """Lines of the Loading screens section: runs of shots with one title, with progress or button."""
    L = ["## Loading screens", "",
         "Shots with the game's load-card layout (black bars, picture between, title centred at the top, tip at the",
         "bottom, percentage or Start Game at the lower right), found by `ocr`. Kind: the save of that name is in the",
         "game's save folder (game save) or the map editor's (editor save). Percentages are OCR reads.", "",
         "| Title | Kind | Shots | UTC | ids (local) |", "|---|---|---|---|---|"]
    runs = []
    for i in sorted(loads):
        if runs and runs[-1][0] == loads[i].get("title") and i - runs[-1][2][-1] <= 3:
            runs[-1][2].append(i)
        else:
            runs.append([loads[i].get("title"), loads[i], [i]])
    for title, _, idx in runs:
        prog = [loads[i]["progress"] for i in idx if "progress" in loads[i]]
        shown = (f"{min(prog)}% to {max(prog)}%" if prog and min(prog) != max(prog) else f"{prog[0]}%" if prog else "")
        if any("button" in loads[i] for i in idx):
            shown = (shown + ", " if shown else "") + "Start Game"
        a, b = shots[idx[0]].utc, shots[idx[-1]].utc
        span = f"{a:%m-%d %H:%M:%S}" + ("" if a == b else f" to {b:%H:%M:%S}")
        L.append(f"| {title or '(title not read)'} | {load_kind(title or '', saves)} | {len(idx)} ({shown}) | {span} | "
                 + " ".join(shots[i].id[4:] for i in idx) + " |")
    return L + [""]


def cmd_build(work, shots, saves):
    labels = load_labels(work)
    times = [s[0] for s in saves]
    pos, labels = positions(shots, labels)
    top, nested = nest(labels, pos)
    covered = set()
    for r in top:
        covered.update(range(pos[r[0]], pos[r[1]] + 1))
    loads = loading_shots(work, shots)
    L = ["# Screenshot index", "",
         "Generated by `tools/screenshot_index.py build` from `labels.tsv` (edit the labels there, not here).",
         "Private working file: it holds names and times from the player's saves and pictures. Keep it out of git.",
         "All times are UTC (file names are local time). \"Saves\" are saves written within "
         f"{SAVE_WINDOW // 60} minutes of the cluster (the nearest ones if none).",
         "\"Sure\": read = text legible in the picture, seen = clear from the picture, guess = thumbnail only, look again.",
         "ids line: <HHMMSS in the file name (local)>=<HHMMSS UTC>; the id's date is the local date, so a late",
         "shot can sit under the next UTC day. Company names, account names and paths are masked (`<name> Transport`).",
         "", f"{len(shots)} screenshots, {len(covered)} labelled in {len(top)} clusters, "
         f"{len(loads)} more categorized as loading screens (see the last section).", ""]
    topics = {}
    for r in top:
        for t in re.split(r"\s*,\s*", r[3]):
            if t:
                topics.setdefault(t, []).append(r)
    L += ["## Find by topic", "", "| Topic | Clusters (UTC start, shots) | Where it is written up |", "|---|---|---|"]
    for t in sorted(topics):
        cl = "; ".join(f"{shots[pos[r[0]]].utc:%m-%d %H:%M} ({pos[r[1]] - pos[r[0]] + 1})" for r in topics[t])
        links = sorted({x for r in topics[t] for x in re.split(r"\s*;\s*", r[7]) if x})
        L.append(f'| {t} | {cl} | {"; ".join(links)} |')
    L.append("")
    items = [(pos[r[0]], pos[r[1]], r) for r in top] + [(a, b, None) for a, b in unlabelled(shots, covered | set(loads))]
    cur = None
    for i, j, row in sorted(items, key=lambda x: x[0]):
        t, end = shots[i].utc, shots[j].utc
        if f"{t:%Y-%m-%d}" != cur:
            cur = f"{t:%Y-%m-%d}"
            L += [f"## {cur} (UTC)", ""]
        ids = [shots[k].id for k in range(i, j + 1)]
        if row is None:
            L += [f"### {hms(t)} to {hms(end)}: {len(ids)} shot(s), UNLABELLED", "", "ids: " + " ".join(ids), ""]
            continue
        g, topic, what, poi, sure, links = row[2:8]
        title = re.sub(r"^\d{6}: ", "", what.split(". ")[0])[:90]
        L += [f"### {hms(t)} to {hms(end)}: {title}", "",
              f'- {len(ids)} shot(s). Game: {g or "-"}. Topic: {topic}. Sure: {sure or "-"}.', f"- What: {what}"]
        if poi:
            L.append(f"- Points of interest: {poi}")
        if links:
            L.append(f"- See: {links}")
        sv = save_lines(t, end, saves, times)
        if sv:
            L.append("- Saves: " + "; ".join(sv))
        ob = ocr_summary(work, ids)
        if ob:
            L.append("- Text read off the pictures (OCR): " + "; ".join(ob))
        for n in nested.get(row[0], []):
            a, b = shots[pos[n[0]]], shots[pos[n[1]]]
            span = a.id[9:] if a is b else f"{a.id[9:]} to {b.id[9:]}"
            L.append(f'- Shot {span} ({hms(a.utc)}{"" if a is b else " to " + hms(b.utc)}): {n[4]}'
                     + (f" Points: {n[5]}." if n[5] else ""))
        L.append("- ids (UTC): " + " ".join(f"{s[9:]}={shots[pos[s]].utc:%H%M%S}" for s in ids))
        L.append("")
    if loads:
        L += loading_section(work, shots, loads, saves)
    with open(os.path.join(work, "INDEX.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote INDEX.md: {len(shots)} shots, {len(covered)} labelled, {len(top)} clusters, {len(loads)} loading screens")


CONT_MAX_GAP = 1800  # seconds: past this a shot is not offered as a continuation of the one before
SHARED_DF = 0.05    # a text line counts as distinctive when under this share of all shots hold it
CONT_CORR = 0.5      # edge correlation from which two shots count as the same static view


def edge_corr(path_a, path_b, size=(192, 108)):
    """Correlation of the edge maps of two shots at thumbnail size: about 0 for unrelated pictures,
    0.8 and up for one static view (HUD text and scene in the same places), lower when the camera moved."""
    import numpy as np
    from PIL import Image
    maps = []
    for path in (path_a, path_b):
        im = Image.open(path).convert("L")
        im.draft("L", (size[0] * 2, size[1] * 2))
        a = np.asarray(im.resize(size, Image.BOX), dtype=np.float32)
        e = (np.abs(np.diff(a, axis=1))[:-1] + np.abs(np.diff(a, axis=0))[:, :-1]).ravel()
        maps.append(e - e.mean())
    return float(maps[0] @ maps[1] / (np.linalg.norm(maps[0]) * np.linalg.norm(maps[1]) + 1e-9))


def ceo_bar(path):
    """Fill of the CEO experience bar at the bottom left of a 3840x2160 game frame, 0 to 1, or None (other
    size, no bar). The bar rises very slowly while a company plays, so two shots of one session read close
    together and never fall; a lower value is another company or a rank-up. The crop is placed by pixel
    at 3840x2160 only, the way the account crop is; the bar's blue fill is measured against its 242 px track."""
    import numpy as np
    from PIL import Image
    im = Image.open(path)
    if im.size != (3840, 2160):
        return None
    row = np.asarray(im.convert("RGB").crop((460, 2098, 730, 2108)), dtype=np.int16).mean(axis=0)
    xs = np.where((row[:, 2] - row[:, 0] > 35) & (row[:, 2] > 90))[0]
    if len(xs) < 3 or xs.min() > 30:
        return None
    fill = float((xs.max() - 15 + 1) / 242.0)
    return fill if fill <= 1 else None       # over 100%: not this bar (a menu or another layout)


def text_keys(work, sid):
    """Lines of a shot's OCR text worth comparing: 8 or more characters with letters, not a bare figure."""
    d = load_ocr(work, sid)
    keys = set()
    for line in (d or {}).get("text", []):
        k = re.sub(r"[^a-z0-9 ]", "", line.lower()).strip()
        if len(k) >= 8 and re.search("[a-z]{3}", k) and not re.fullmatch(r"[\d ,$]+", k):
            keys.add(k)
    return keys if d else None


def doc_freq(work, shots):
    """How many shots' OCR text holds each line, so lines every game window has (Basics, Send to Line, ...)
    are not counted as a shared vehicle or line name."""
    df = collections.Counter()
    for s in shots:
        df.update(text_keys(work, s.id) or ())
    return df


def continues_note(work, shots, i, df, hud, total):
    """A `todo` hint: does shot i look like the same view as the shot before it, though a gap over GAP
    split them? Edge correlation of the pictures, plus (when both shots are read) the lines of text they
    share that few other shots have (an open window's vehicle or line name), and the HUD date. The
    labelling decision stays with a person."""
    if i == 0:
        return ""
    prev = shots[i - 1]
    gap = (shots[i].utc - prev.utc).total_seconds()
    if gap > CONT_MAX_GAP:
        return ""
    try:
        c = edge_corr(prev.path, shots[i].path)
    except (ImportError, OSError) as e:
        return f"\t(no continuation check: {type(e).__name__})"
    a, b = text_keys(work, prev.id), text_keys(work, shots[i].id)
    shared = sorted((k for k in a & b if df[k] <= SHARED_DF * total), key=len, reverse=True) if a and b else []
    txt = f", {len(shared)} shared text line(s)" + (f" e.g. '{redact(shared[0])[:30]}'" if shared else "") if a and b else ", text not read"
    bar = ""
    d0, d1 = (hud.get(prev.id) or "?"), (hud.get(shots[i].id) or "?")
    verdict = "likely continues" if c >= CONT_CORR or shared else "new view"
    try:
        e0, e1 = ceo_bar(prev.path), ceo_bar(shots[i].path)
    except (ImportError, OSError):
        e0 = e1 = None
    if e0 is not None and e1 is not None:
        bar = f", CEO bar {e0:.0%} -> {e1:.0%}" + (" (fell or jumped: other game or rank-up?)" if not -0.005 <= e1 - e0 <= 0.05 else "")
    return f"\t{verdict} {prev.id} (gap {gap:.0f} s, edge corr {c:.2f}{txt}, HUD date {d0} -> {d1}{bar})"


def cmd_todo(work, shots, every):
    pos, labels = positions(shots, load_labels(work))
    covered = set(loading_shots(work, shots))        # a loading screen needs no note
    for r in labels:
        covered.update(range(pos[r[0]], pos[r[1]] + 1))
    df = doc_freq(work, every)
    hud = {}
    for sid in (s.id for s in shots):
        d = load_ocr(work, sid)
        hud[sid] = (d or {}).get("date")
    for i, j in unlabelled(shots, covered):
        print(f"{shots[i].id}\t{shots[j].id}\t{j - i + 1} shots\tlocal {shots[i].id[9:11]}:{shots[i].id[11:13]}"
              + continues_note(work, shots, i, df, hud, len(every)))


def cmd_find(work, shots, terms):
    labels = load_labels(work)
    pos, labels = positions(shots, labels)
    hits = 0
    for s in shots:
        d = load_ocr(work, s.id)
        if not d:
            continue
        blob = ("\n".join(d["text"]) + "\n" + d["date"]).lower()
        if d.get("loading"):
            blob += "\nloading screen " + d["loading"].get("title", "").lower()
        if all(x.lower() in blob for x in terms):
            hits += 1
            row = next((r for r in labels if pos[r[0]] <= pos[s.id] <= pos[r[1]]), None)
            snip = next((ln for ln in d["text"] if terms[0].lower() in ln.lower()), "")[:70]
            print(f'{s.id[9:]} {s.utc:%m-%d %H:%M:%S}Z  [{snip}]  {row[4][:60] if row else ""}')
    print(hits, "shot(s)")


def cmd_check(work, shots):
    pos, labels = positions(shots, load_labels(work))
    bad = total = found = 0
    for r in labels:
        ids = [shots[k].id for k in range(pos[r[0]], pos[r[1]] + 1)]
        ocr = [load_ocr(work, i) for i in ids]
        blob = "\n".join("\n".join(d["text"]) + "\n" + d["date"] for d in ocr if d).lower()
        if not blob:
            continue
        facts = set(re.findall(r'"([^"]{4,60})"', r[4])) | {m.group(0) for m in DATE_RE.finditer(r[4])} \
            | set(re.findall(r"\$[\d,]{5,}", r[4]))
        miss = {f for f in facts if f.lower() not in blob and f.lower().replace(",", "") not in blob.replace(",", "")}
        for m in LABEL_RE.finditer(r[4]):        # a town label: the name and the first digits of its number
            facts.add(m.group(0))
            if f"{m.group(1)} ({m.group(2)[:3]}".lower() not in blob:
                miss.add(m.group(0))
        total += len(facts)
        found += len(facts) - len(miss)
        if miss:
            bad += 1
            print(f"{r[0][9:]}-{r[1][9:]}: not in OCR: " + " | ".join(sorted(miss)))
    print(f"recall: {found} of {total} label facts found in OCR text")
    print(bad, "cluster(s) with facts the OCR did not see (OCR misses small text; look at the picture before changing a label)")


def cmd_hud(work, shots):
    n = 0
    with open(os.path.join(work, "hud.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "utc", "game_date", "account", "earnings", "people_delivered", "cargo_delivered"])
        for s in shots:
            d = load_ocr(work, s.id) or {}
            h = d.get("hud") or {}
            if h or d.get("date"):
                n += 1
                w.writerow([s.id, f"{s.utc:%Y-%m-%d %H:%M:%S}", d.get("date", ""), h.get("account", ""),
                            h.get("earnings", ""), h.get("people", ""), h.get("box", "")])
    print(f"wrote hud.csv: {n} rows (OCR reads: look at a picture before relying on a number)")


def cmd_sheets(shots, out, per=12, cols=4, tw=392, th=221):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        die("sheets needs Pillow (pip install pillow); see tools/README.md")
    if not out:
        die("sheets needs --out DIR")
    os.makedirs(out, exist_ok=True)
    rows = (per + cols - 1) // cols
    for k in range(0, len(shots), per):
        sheet = Image.new("RGB", (cols * tw, rows * th), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for j, s in enumerate(shots[k:k + per]):
            with Image.open(s.path) as im:
                im = im.convert("RGB")
                im.thumbnail((tw - 4, th - 4))
            x, y = (j % cols) * tw + 2, (j // cols) * th + 2
            sheet.paste(im, (x, y))
            d.rectangle((x, y, x + 150, y + 16), fill=(0, 0, 0))
            d.text((x + 3, y + 2), s.id[4:], fill=(255, 255, 0))
        sheet.save(os.path.join(out, f"sheet-{k // per:02d}.png"))
    print("sheets written:", (len(shots) + per - 1) // per)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("ocr", "todo", "sheets", "build", "find", "check", "hud"))
    ap.add_argument("terms", nargs="*", help="terms for `find`")
    ap.add_argument("--work")
    ap.add_argument("--shots")
    ap.add_argument("--saves-dir", action="append")
    ap.add_argument("--date", action="append", default=[])
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--out")
    ap.add_argument("--hud-engine", choices=("tesseract", "rapidocr"), default="tesseract")
    ap.add_argument("--no-nice", action="store_true")
    a = ap.parse_args()
    if not a.no_nice:
        lower_priority()
    if a.command == "find" and not a.terms:
        die("find needs at least one term")
    work = work_dir(a.work)
    shots = list_shots(shots_dir(a.shots), set(a.date))
    if a.command == "ocr":
        cmd_ocr(work, shots, a.jobs, a.hud_engine)
    elif a.command == "todo":
        cmd_todo(work, shots, list_shots(shots_dir(a.shots), set()))
    elif a.command == "sheets":
        cmd_sheets(shots, a.out)
    elif a.command == "build":
        cmd_build(work, shots, list_saves(game_dirs(a.saves_dir)))
    elif a.command == "find":
        cmd_find(work, list_shots(shots_dir(a.shots), set()), a.terms)
    elif a.command == "check":
        cmd_check(work, shots)
    elif a.command == "hud":
        cmd_hud(work, shots)


if __name__ == "__main__":
    main()
