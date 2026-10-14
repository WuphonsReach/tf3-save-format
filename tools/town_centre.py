#!/usr/bin/env python3
"""Find a town's centre from screenshots of its name label (docs/town-centre.md).

Usage:
  town_centre.py SAVE.sav --list
  town_centre.py SAVE.sav --town X,Y SHOT.png [SHOT.png ...] [--out DIR] [--json] [options]

The save does not store a town's centre. The game draws the town's name label (a dark rounded box
with the name, the population and the cargo icons) at a fixed distance from it. Take a series of
screenshots of one town with the camera turned round it, looking mostly down, the label in every
picture. This script registers each picture to the save's street edges, carries the label's
anchor point (the middle of the box's bottom edge) onto the map, and fits a circle through the
anchors of the series: the circle's centre is the town's centre, its radius the label's offset.

  --list            list the town street clusters of the save (centre of the bounding box, size)
                    to pick a --town from
  --town X,Y        a point within a few hundred metres of the town, in map metres (x east, y north)
  --out DIR         write a picture of the streets, the anchors and the centre, and the JSON there
  --json            print the result as JSON
  --min-score S     a picture whose fit scores below S (0 to 1, default 0.8) is listed and left out
  --scales A,B,..   zoom levels to try, in screen pixels per metre (default 0.8,1.1,1.4,1.7,2.0,2.3)
  --pitches A,B,..  camera pitches to try, degrees from straight down (default 0,15,30; add 45, 60
                    for strongly tilted pictures)
  --thorough        refine more starting guesses per picture (slower, rescues some tilted pictures)
  --road-min/--road-max V   the grey value range of road pixels (default 85 to 140)
  -j N              pictures fitted in parallel (default: up to 4)

Method, in short: roads are the unsaturated grey pixels, the label the dark box. A first guess
(rotation, scale, shift, pitch) comes from correlating the road mask with the street edges; a
perspective transform is then refined per picture. The anchors are mapped to the ground plane.
Two models are fitted to them: a constant distance on the ground (the circle), and a label at a
height above the centre (a distance of height times tan(pitch), the pitch read from the fitted
transform). Near top-down pictures cannot tell them apart; strongly tilted ones can.

Needs numpy and Pillow, unlike the other scripts here (see tools/README.md). Reads a save and
screenshots; writes only into --out. The save's street edges are read as in street_edges.py.
"""
import argparse
import collections
import concurrent.futures
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from street_edges import load, read_edges  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    np = Image = ImageDraw = ImageFilter = None

N = 1600          # side of the street canvas, in canvas pixels
DS = 2            # screenshot down-scale in the refinement
STREET_WIDTH = 12  # metres, as drawn on the canvas (width only matters for the match)


# ---------------------------------------------------------------- streets

def town_edges(edges):
    return [e for e in edges if e["type"] and e["type"].startswith("town_")]


def clusters(edges):
    """Town street clusters (edges joined by node ids), biggest first."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    town = town_edges(edges)
    for e in town:
        parent[find(e["a"])] = find(e["b"])
    groups = collections.defaultdict(list)
    for e in town:
        groups[find(e["a"])].append(e)
    return sorted(groups.values(), key=len, reverse=True)


def canvas(edges, centre, mpp):
    """The save's streets around `centre` as a blurred grey image, `mpp` metres per pixel."""
    img = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(img)
    reach = N * mpp
    for e in edges:
        if e["family"] != "street":
            continue
        p0, p1 = e["p0"], e["p1"]
        if all(max(abs(p[0] - centre[0]), abs(p[1] - centre[1])) > reach for p in (p0, p1)):
            continue
        d.line([((p0[0] - centre[0]) / mpp + N / 2, -(p0[1] - centre[1]) / mpp + N / 2),
                ((p1[0] - centre[0]) / mpp + N / 2, -(p1[1] - centre[1]) / mpp + N / 2)],
               fill=255, width=max(1, round(STREET_WIDTH / mpp)))
    return img.filter(ImageFilter.GaussianBlur(2 if mpp <= 1 else 1))


# ---------------------------------------------------------------- screenshots

def find_label(im):
    """(x0, x1, y0, y1) of the name label's box: the biggest dark, unsaturated, wide and short blob."""
    mx, mn = im.max(2), im.min(2)
    dark = (mx < 70) & ((mx - mn) < 28)
    rs = dark.sum(1)
    if rs.max() == 0:
        raise ValueError("no label found (no dark box)")
    rows = np.where(rs > 0.5 * rs.max())[0]
    best = None
    for run in np.split(rows, np.where(np.diff(rows) > 2)[0] + 1):
        cols = np.where(dark[run[0]:run[-1] + 1].sum(0) > len(run) * 0.4)[0]
        if not len(cols):
            continue
        c = max(np.split(cols, np.where(np.diff(cols) > 6)[0] + 1), key=len)
        if best is None or len(c) * len(run) > best[0]:
            best = (len(c) * len(run), c[0], c[-1], run[0], run[-1])
    _, x0, x1, y0, y1 = best
    frac = dark[:, x0:x1 + 1].mean(1)
    rows = np.where(frac > 0.12)[0]
    runs = [r for r in np.split(rows, np.where(np.diff(rows) > 1)[0] + 1) if r[0] <= y0 <= r[-1]]
    if runs:
        r = max(runs, key=len)
        y0, y1 = r[0], r[-1]
    cx = (x0 + x1) // 2
    cols = np.where(dark[y0:y1 + 1].sum(0) >= 3)[0]
    runs = [r for r in np.split(cols, np.where(np.diff(cols) > 8)[0] + 1) if r[0] <= cx <= r[-1]]
    r = max(runs, key=len)
    return int(r[0]), int(r[-1]), int(y0), int(y1)


class Shot:
    def __init__(self, path, road_min, road_max, rad=450):
        self.path = path
        self.name = os.path.basename(path)
        im = np.array(Image.open(path).convert("RGB")).astype(int)
        self.H, self.W = im.shape[:2]
        self.label = find_label(im)
        x0, x1, y0, y1 = self.label
        self.anchor = np.array([(x0 + x1) / 2, y1], float)   # middle of the box's bottom edge
        mx, mn = im.max(2), im.min(2)
        mask = ((mx - mn) < 8) & (mx >= road_min) & (mx <= road_max)
        mask[max(0, y0 - 8):y1 + 40, max(0, x0 - 8):x1 + 8] = False
        small = Image.fromarray((mask * 255).astype(np.uint8)).resize(
            (self.W // DS, self.H // DS), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
        self.S = np.array(small, float) / 255
        yy, xx = np.mgrid[0:self.S.shape[0], 0:self.S.shape[1]]
        self.w = (np.hypot(xx * DS - self.anchor[0], yy * DS - self.anchor[1] - 30) < rad).astype(float)
        self.Sw = self.S * self.w


# ---------------------------------------------------------------- fitting

def warp(cv, h, sh):
    a, b, c, d, e, f, g, hh = h
    coeffs = (a * DS, b * DS, c, d * DS, e * DS, f, g * DS, hh * DS)
    out = cv.transform((sh.S.shape[1], sh.S.shape[0]), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    return np.array(out, float) / 255


def score(cv, h, sh):
    t = warp(cv, h, sh) * sh.w
    return float((t * sh.Sw).sum() / math.sqrt((t * t).sum() * (sh.Sw * sh.S).sum() + 1e-9))


def cam_h(s, theta, phi, f, W, H, mpp):
    """Screen to canvas homography of a pinhole camera: `s` pixels per metre at the picture
    centre, heading `theta`, pitch `phi` from straight down, focal length `f` pixels; the canvas
    centre is under the picture centre. Coefficients as PIL's PERSPECTIVE takes them."""
    t = math.tan(phi) / f
    ppx, ppy = W / 2, H / 2
    c, sn, cp = math.cos(theta), math.sin(theta), math.cos(phi)
    xn = np.array([1 / s, 0, -ppx / s])
    yn = np.array([0, -1 / (s * cp), ppy / (s * cp)])
    gx, gy = c * xn - sn * yn, sn * xn + c * yn
    den = np.array([0, t, 1 - t * ppy])
    cxn = gx / mpp + (N / 2) * den
    cyn = -gy / mpp + (N / 2) * den
    k = den[2]
    return [cxn[0] / k, cxn[1] / k, cxn[2] / k, cyn[0] / k, cyn[1] / k, cyn[2] / k, den[0] / k, den[1] / k]


def shift_h(h, kx, ky):
    a, b, c, d, e, f, g, hh = h
    den = 1 - g * kx - hh * ky
    return [a / den, b / den, (c - a * kx - b * ky) / den, d / den, e / den,
            (f - d * kx - e * ky) / den, g / den, hh / den]


def coarse(cv, sh, scales, pitches, mpp, keep):
    """Correlate the road mask with the canvas over heading, scale, pitch and focal length;
    return up to `keep` distinct best guesses as (score, homography)."""
    ds = 4
    small = Image.fromarray((sh.S * 255).astype(np.uint8)).resize((sh.W // ds, sh.H // ds), Image.BILINEAR)
    s4 = np.array(small, float) / 255
    yy, xx = np.mgrid[0:s4.shape[0], 0:s4.shape[1]]
    s4 = s4 * (np.hypot(xx * ds - sh.W / 2, yy * ds - sh.H / 2) < sh.W * 0.45)
    s4z = s4 - s4.mean()
    ns = (s4z ** 2).sum()
    shape2 = (s4.shape[0] * 2, s4.shape[1] * 2)
    G = np.fft.rfft2(s4z, s=shape2)
    found = []
    for s in scales:
        for phi in pitches:
            for fm in ((1.0,) if phi == 0 else (1.0, 1.6)):
                for a in range(0, 360, 5):
                    h = cam_h(s, math.radians(a), math.radians(phi), fm * sh.W, sh.W, sh.H, mpp)
                    co = (h[0] * ds, h[1] * ds, h[2], h[3] * ds, h[4] * ds, h[5], h[6] * ds, h[7] * ds)
                    t = np.array(cv.transform((s4.shape[1], s4.shape[0]), Image.PERSPECTIVE, co,
                                              Image.BILINEAR), float) / 255
                    tz = t - t.mean()
                    cc = np.fft.irfft2(G * np.conj(np.fft.rfft2(tz, s=shape2)), s=shape2)
                    dy, dx = np.unravel_index(np.argmax(cc), cc.shape)
                    p = cc[dy, dx] / math.sqrt((tz ** 2).sum() * ns + 1e-9)
                    if dy > t.shape[0]:
                        dy -= shape2[0]
                    if dx > t.shape[1]:
                        dx -= shape2[1]
                    found.append((p, s, a, phi, fm, shift_h(h, ds * dx, ds * dy)))
    found.sort(key=lambda c: -c[0])
    out = []
    for c in found:
        if all(not (k[1] == c[1] and k[3] == c[3] and k[4] == c[4]
                    and min(abs(k[2] - c[2]), 360 - abs(k[2] - c[2])) <= 10) for k in out):
            out.append(c)
        if len(out) >= keep:
            break
    return [(c[0], c[5]) for c in out]


def refine(cv, sh, h0, iters):
    """Pattern search over the eight homography coefficients for the best match score."""
    h = np.array(h0, float)
    best = score(cv, h, sh)
    steps = np.array([0.004 * (abs(h[0]) + abs(h[1])), 0.004 * (abs(h[0]) + abs(h[1])), 3.0,
                      0.004 * (abs(h[3]) + abs(h[4])), 0.004 * (abs(h[3]) + abs(h[4])), 3.0, 2e-5, 2e-5])
    for _ in range(iters):
        improved = False
        for k in range(8):
            for sgn in (1, -1):
                h2 = h.copy()
                h2[k] += sgn * steps[k]
                sc = score(cv, h2, sh)
                if sc > best + 1e-6:
                    h, best, improved = h2, sc, True
                    break
        if not improved:
            steps *= 0.5
            if steps[2] < 0.05:
                break
    return h, best


_G = {}


def _init(edges, centre, mpp):
    _G["cv"] = canvas(edges, centre, mpp)
    _G["mpp"] = mpp


def fit_shot(args):
    path, road_min, road_max, scales, pitches, keep, iters = args
    cv, mpp = _G["cv"], _G["mpp"]
    try:
        sh = Shot(path, road_min, road_max)
    except ValueError as err:
        return dict(file=os.path.basename(path), error=str(err))
    best = None
    for _, h0 in coarse(cv, sh, scales, pitches, mpp, keep):
        h, sc = refine(cv, sh, h0, iters)
        if best is None or sc > best[1]:
            best = (h, sc)
    h, sc = best
    return dict(file=sh.name, score=sc, h=[float(v) for v in h], anchor_px=sh.anchor.tolist(),
                label=list(sh.label), size=[sh.W, sh.H])


# ---------------------------------------------------------------- geometry

def to_world(h, pt, centre, mpp):
    a, b, c, d, e, f, g, hh = h
    den = g * pt[0] + hh * pt[1] + 1
    px, py = (a * pt[0] + b * pt[1] + c) / den, (d * pt[0] + e * pt[1] + f) / den
    return np.array([centre[0] + (px - N / 2) * mpp, centre[1] - (py - N / 2) * mpp])


def to_screen(h, w, centre, mpp):
    a, b, c, d, e, f, g, hh = h
    m = np.array([[a, b, c], [d, e, f], [g, hh, 1.0]])
    r = np.linalg.inv(m) @ np.array([(w[0] - centre[0]) / mpp + N / 2, -(w[1] - centre[1]) / mpp + N / 2, 1.0])
    return r[:2] / r[2]


def local(h, w, centre, mpp):
    """Where world point `w` appears, the pixels per metre there, the ground direction that
    appears as screen-up, and cos(pitch) read as the ratio of the Jacobian's singular values."""
    j = np.zeros((2, 2))
    for k, dv in enumerate(((1, 0), (0, 1))):
        j[:, k] = (to_screen(h, w + np.array(dv, float), centre, mpp)
                   - to_screen(h, w - np.array(dv, float), centre, mpp)) / 2
    sv = np.linalg.svd(j, compute_uv=False)
    up = np.linalg.solve(j, np.array([0.0, -1.0]))
    return to_screen(h, w, centre, mpp), math.sqrt(sv[0] * sv[1]), up / np.hypot(*up), min(1.0, sv[1] / sv[0])


def circle(points):
    a = np.c_[2 * points[:, 0], 2 * points[:, 1], np.ones(len(points))]
    s = np.linalg.lstsq(a, (points ** 2).sum(1), rcond=None)[0]
    c = s[:2]
    r = math.sqrt(s[2] + c @ c)
    return c, r, np.hypot(*(points - c).T) - r


def height_model(shots, c0, centre, mpp, iters=8):
    """Anchor = centre + Z * tan(pitch) * (ground direction of screen-up); fit centre and Z."""
    c = np.array(c0, float)
    for _ in range(iters):
        a, b = [], []
        for s in shots:
            _, _, up, cphi = local(s["h"], c, centre, mpp)
            tp = math.tan(math.acos(max(cphi, 1e-3)))
            g = s["anchor_world"]
            a += [[1, 0, tp * up[0]], [0, 1, tp * up[1]]]
            b += [g[0], g[1]]
        a, b = np.array(a), np.array(b)
        sol = np.linalg.lstsq(a, b, rcond=None)[0]
        c = sol[:2]
    res = (a @ sol - b).reshape(-1, 2)
    return c, float(sol[2]), math.sqrt((res ** 2).sum(1).mean())


# ---------------------------------------------------------------- output

def plot(path, edges, c, shots, name):
    r, s = 300, 1.0
    w = int(2 * r * s)
    img = Image.new("RGB", (w, w), (246, 246, 242))
    d = ImageDraw.Draw(img)

    def p(q):
        return ((q[0] - c[0]) * s + w / 2, -(q[1] - c[1]) * s + w / 2)
    for e in edges:
        if e["family"] == "street":
            d.line([p(e["p0"]), p(e["p1"])], fill=(125, 125, 125), width=7)
    for sh in shots:
        x, y = p(sh["anchor_world"])
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(220, 60, 40))
    x, y = p(c)
    d.line([x - 10, y, x + 10, y], fill=(0, 90, 220), width=3)
    d.line([x, y - 10, x, y + 10], fill=(0, 90, 220), width=3)
    d.text((8, 8), "%s  centre %.0f, %.0f  (north up, 100 m ticks)" % (name, c[0], c[1]), fill=(0, 0, 0))
    for t in range(-300, 301, 100):
        d.line([(t * s + w / 2, w - 8), (t * s + w / 2, w)], fill=(0, 0, 0))
        d.line([(0, t * s + w / 2), (8, t * s + w / 2)], fill=(0, 0, 0))
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description="Find a town's centre from screenshots of its name label.")
    ap.add_argument("save")
    ap.add_argument("shots", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--town")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-score", type=float, default=0.8)
    ap.add_argument("--scales", default="0.8,1.1,1.4,1.7,2.0,2.3")
    ap.add_argument("--pitches", default="0,15,30")
    ap.add_argument("--thorough", action="store_true")
    ap.add_argument("--road-min", type=int, default=85)
    ap.add_argument("--road-max", type=int, default=140)
    ap.add_argument("--mpp", type=float, default=1.0, help="metres per canvas pixel (default 1)")
    ap.add_argument("-j", type=int, default=min(4, os.cpu_count() or 1))
    args = ap.parse_args()
    if np is None:
        sys.exit("town_centre.py needs numpy and Pillow (pip install numpy pillow); "
                 "the other scripts in tools/ need only the standard library")
    edges = read_edges(load(args.save, False))
    if args.list:
        print("%d street edges; town street clusters (edges, bounding-box centre, size in metres):" % len(edges))
        for k, c in enumerate(clusters(edges)):
            pts = np.array([e["p0"][:2] for e in c] + [e["p1"][:2] for e in c])
            lo, hi = pts.min(0), pts.max(0)
            print("%3d  %4d edges  centre %7.0f %7.0f  size %4.0f x %4.0f" % (
                k, len(c), (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[0] - lo[0], hi[1] - lo[1]))
        return
    if not args.town or not args.shots:
        ap.error("give --town X,Y and at least three screenshots (or use --list)")
    centre = tuple(float(v) for v in args.town.split(","))
    mpp = args.mpp
    scales = [float(v) for v in args.scales.split(",")]
    pitches = [float(v) for v in args.pitches.split(",")]
    job = [(p, args.road_min, args.road_max, scales, pitches, 10 if args.thorough else 3,
            40 if args.thorough else 30) for p in args.shots]
    with concurrent.futures.ProcessPoolExecutor(args.j, initializer=_init,
                                                initargs=(edges, centre, mpp)) as ex:
        fits = list(ex.map(fit_shot, job))
    used = []
    for f in fits:
        if "error" in f:
            print("%s: %s" % (f["file"], f["error"]), file=sys.stderr)
            continue
        f["anchor_world"] = to_world(f["h"], f["anchor_px"], centre, mpp)
        f["used"] = f["score"] >= args.min_score
        if f["used"]:
            used.append(f)
    if len(used) < 3:
        sys.exit("fewer than three pictures fitted (score >= %.2f): %s" % (
            args.min_score, ", ".join("%s %.2f" % (f["file"], f.get("score", 0)) for f in fits)))
    pts = np.array([f["anchor_world"] for f in used])
    c, r, res = circle(pts)
    ch, z, rms_h = height_model(used, c, centre, mpp)
    rows = []
    for f in fits:
        if "score" not in f:
            continue
        h = f["h"]
        _, ppm, _, cphi = local(h, c, centre, mpp)
        pitch = math.degrees(math.acos(cphi))
        rows.append(dict(file=f["file"], score=round(f["score"], 3), used=f["used"], px_per_m=round(ppm, 2),
                         pitch_deg=round(pitch, 1), label_height_px=f["label"][3] - f["label"][2],
                         anchor_world=[round(float(v), 1) for v in f["anchor_world"]]))
    result = dict(save=os.path.basename(args.save), pictures=len(fits), used=len(used),
                  circle=dict(centre=[round(float(v), 1) for v in c], radius_m=round(r, 1),
                              rms_m=round(float(np.sqrt((res ** 2).mean())), 2)),
                  height_model=dict(centre=[round(float(v), 1) for v in ch], height_m=round(z, 1),
                                    rms_m=round(rms_h, 2)),
                  shots=rows)
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "town-centre.json"), "w") as fh:
            json.dump(result, fh, indent=1)
        plot(os.path.join(args.out, "town-centre.png"), edges, c, used, "town")
    if args.json:
        print(json.dumps(result, indent=1))
        return
    print("%s: %d of %d pictures fitted" % (result["save"], len(used), len(fits)))
    for row in rows:
        print("  %-34s score %.3f  %.2f px/m  pitch %4.1f  box %2d px  anchor %s%s" % (
            row["file"], row["score"], row["px_per_m"], row["pitch_deg"], row["label_height_px"],
            row["anchor_world"], "" if row["used"] else "  (left out)"))
    cc = result["circle"]
    print("circle (constant distance on the ground): centre %.1f, %.1f  radius %.1f m  rms %.2f m" % (
        cc["centre"][0], cc["centre"][1], cc["radius_m"], cc["rms_m"]))
    hm = result["height_model"]
    print("height model (distance = height x tan pitch): centre %.1f, %.1f  height %.1f m  rms %.2f m" % (
        hm["centre"][0], hm["centre"][1], hm["height_m"], hm["rms_m"]))


if __name__ == "__main__":
    main()
