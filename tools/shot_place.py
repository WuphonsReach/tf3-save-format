#!/usr/bin/env python3
"""Place a screenshot on the map from the vehicles it shows (skill: .claude/skills/shot-place/SKILL.md).

Usage:
  shot_place.py SAVE.sav SHOT.png --vehicle PX,PY[,DEG] --vehicle PX,PY[,DEG] [--vehicle ...]
                --hint X,Y[,R] [--class PREFIX] [--map MAP.png] [--out DIR] [options]

The save has no camera, but a paused game keeps every vehicle where the shot shows it. Name two or
more vehicles you can see in the picture (pixel position in the full-size picture, x right and y
down from the top-left corner, and optionally the direction of the vehicle's long axis, degrees
anticlockwise from screen-right, any end: it is taken modulo 180). The script pairs the first two
with every ordered pair of the save's vehicles of that class inside the hint circle, solves scale
and heading from each pairing (a similarity transform), drops the ones outside the scale range or
the hint circle or that put a `--in-frame` point outside the picture, and ranks the rest by
heading error, by how far the third and later vehicles land from a vehicle of the save, and by how
many vehicles of the save would be in the frame but are not named (a visible ship should be named).
The ranking is printed with the runners-up, so an ambiguous picture shows as close scores.

  --vehicle PX,PY[,DEG]  a vehicle in the picture (two or more; the first two make the pairing)
  --hint X,Y[,R]         map metres (x east, y north) and radius (default 1000): the picture's
                         centre is searched inside this circle; the pairing candidates too
  --class PREFIX         model path prefix of the vehicles named (default vehicle/ship/)
  --in-frame X,Y         a map point that must lie inside the picture (repeatable)
  --covered X0,Y0,X1,Y1  a picture box (pixels) the game's window hides: a save vehicle there is not
                         counted as missing from the names (repeatable)
  --ui                   cover the right-hand building window, the top icon bar and the bottom bar
  --scale-range A,B      pixels per metre at the picture centre for a 3840-wide picture, scaled
                         with the picture's width (default 3.5,11)
  --map PNG              a `terrain_map.py --png --mpp 1` picture that covers the view (its
                         tf3map:view record gives the frame); without it the script draws one
                         around the best pairing (about a minute, needs the install for nothing)
  --pick N               use ranking row N (default 1) for the fit
  --no-refine            keep the similarity transform (a flat top-down camera)
  --pixel PX,PY          print the map point under a picture pixel (repeatable)
  --badges               read the `n/m` load badges over vehicles (tesseract) and give each one's
                         picture position; with --project, the save's vehicles nearest each
  --project PREFIX       project the save's model instances whose path starts with PREFIX (for
                         example vehicle/) into the picture with the fit and count those in frame
                         (repeatable); with --badges, name the three nearest to each badge
  --out DIR              write the blend (map over the picture, 50 percent), the list of vehicles
                         projected into the picture and the result as JSON there
  --json                 print the result as JSON

Refinement: the similarity transform is a top-down camera. The real camera tilts, so the ground at
the top of the picture is farther away and a constant scale is wrong there. The script then adds
the two perspective terms of a homography, searched against the map's coastline (the shot's water
is picked out by colour, dark blue-green, tuned on one temperate daytime picture, 604; its edge is
matched to the water edge of the map picture), and for every pair of terms solves the similarity
that sends the two named vehicles exactly to their places in the save. It prints the coastline
score before and after, and how much the scale changes from the bottom of the picture to the top.
The fit is a plane at one height: the water (the vehicles named should be ships, or other things at
water level). Anything above that plane (a viaduct, a roof, a hill) is shifted along screen-up by
about its height times the tangent of the camera's pitch, and the more the camera tilts the more it
moves, so such things will not line up in the blend; use the coastline and things at the water.

Needs numpy and Pillow (see tools/README.md); the map picture is made by terrain_map.py when not
given. Reads a save, a picture and the map picture; writes only into --out. The frame and the
fitting functions come from town_centre.py.
"""
import argparse
import csv
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402
from model_instances import read_instances  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageFilter
    import town_centre as tc
except ImportError:
    np = Image = ImageFilter = tc = None

UNLISTED_PENALTY = 15.0     # degrees of ranking score per save vehicle in the frame that is not named
MISSING_PENALTY = 150.0     # pixels of residual for a named vehicle with no save vehicle near it


def parse_pt(text, n=2):
    v = [float(t) for t in text.split(",")]
    if len(v) < n:
        raise argparse.ArgumentTypeError("expected %d numbers: %s" % (n, text))
    return v


def d180(a, b):
    d = (a - b) % 180.0
    return min(d, 180.0 - d)


class Similarity:
    """Picture (u right, v up, pixels) to map metres: scale `s` px/m, rotation `th`, anchored on
    a picture point `a` that lies on world point `w`."""

    def __init__(self, a, w, s, th):
        self.a, self.w, self.s, self.th = a, w, s, th

    def to_world(self, u, v):
        x, y = (u - self.a[0]) / self.s, (v - self.a[1]) / self.s
        c, sn = math.cos(-self.th), math.sin(-self.th)
        return self.w[0] + x * c - y * sn, self.w[1] + x * sn + y * c

    def to_screen(self, x, y):
        dx, dy = x - self.w[0], y - self.w[1]
        c, sn = math.cos(self.th), math.sin(self.th)
        return (dx * c - dy * sn) * self.s + self.a[0], (dx * sn + dy * c) * self.s + self.a[1]


def hypotheses(cands, picks, size, hint, scale_range, in_frame, covered=()):
    """Rank pairings of the first two picks with the save's vehicles `cands` (instance rows)."""
    W, H = size
    k = W / 3840.0
    lo, hi = scale_range[0] * k, scale_range[1] * k
    (a, b) = picks[0], picks[1]
    A = (a["px"], -a["py"])
    B = (b["px"], -b["py"])
    D = (B[0] - A[0], B[1] - A[1])
    LD = math.hypot(*D)
    out = []
    for i, j in itertools.permutations(range(len(cands)), 2):
        ci, cj = cands[i], cands[j]
        d = (cj["x"] - ci["x"], cj["y"] - ci["y"])
        ld = math.hypot(*d)
        if ld < 1e-6:
            continue
        s = LD / ld
        if not lo <= s <= hi:
            continue
        th = math.atan2(D[1], D[0]) - math.atan2(d[1], d[0])
        sim = Similarity(A, (ci["x"], ci["y"]), s, th)
        cen = sim.to_world(W / 2, -H / 2)
        if math.hypot(cen[0] - hint[0], cen[1] - hint[1]) > hint[2]:
            continue

        def inside(x, y, margin=0):
            u, v = sim.to_screen(x, y)
            return margin < u < W - margin and -H + margin < v < -margin
        if not all(inside(x, y) for x, y in in_frame):
            continue
        he = 0.0
        for pk, cv_ in ((a, ci), (b, cj)):
            if pk.get("deg") is not None:
                he += d180(math.degrees(math.atan2(cv_["fy"], cv_["fx"])) + math.degrees(th), pk["deg"])
        extra = 0.0
        used = {i, j}
        for pk in picks[2:]:
            best, bi = None, None
            for m, cm in enumerate(cands):
                if m in used:
                    continue
                u, v = sim.to_screen(cm["x"], cm["y"])
                r = math.hypot(u - pk["px"], v + pk["py"])
                if best is None or r < best:
                    best, bi = r, m
            if best is None or best > MISSING_PENALTY:
                extra += MISSING_PENALTY
            else:
                extra += best
                used.add(bi)
        def hidden(x, y):             # under the game's window or bars: the picture cannot show a vehicle there
            u, v = sim.to_screen(x, y)
            return any(x0 <= u <= x1 and y0 <= -v <= y1 for x0, y0, x1, y1 in covered)
        unlisted = sum(1 for m, cm in enumerate(cands)
                       if m not in used and inside(cm["x"], cm["y"]) and not hidden(cm["x"], cm["y"]))
        score = he + extra / 10.0 + UNLISTED_PENALTY * unlisted
        out.append(dict(score=score, i=i, j=j, heading_err=he, extra_px=extra, unlisted=unlisted,
                        scale=s, rot=math.degrees(th), centre=cen, sim=sim))
    out.sort(key=lambda r: r["score"])
    return out


def make_map(save, out_dir, centre, radius=800):
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, "-I", os.path.join(here, "terrain_map.py"), out_dir, save,
           "--crop", "%d,%d,%d" % (round(centre[0]), round(centre[1]), radius), "--mpp", "1",
           "--png", "--rose", "off", "--no-grid"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        sys.exit("terrain_map.py failed: " + res.stderr.strip()[-300:])
    line = [ln for ln in res.stdout.splitlines() if ln.strip()][-1]
    return line.split("  ")[0].strip()


def load_map(path):
    im = Image.open(path)
    view = json.loads(im.info["tf3map:view"])
    ref = np.array(im.convert("RGB")).astype(int)
    return ref, view


def edge(mask, sigma=2):
    b = np.array(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma)), float) / 255
    gy, gx = np.gradient(b)
    return np.hypot(gx, gy)


def shot_water(path):
    im = np.array(Image.open(path).convert("RGB")).astype(float) / 255
    mx, mn = im.max(2), im.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    wat = (g >= r) & (b >= r * 0.9) & (mx < 0.45) & (sat > 0.18) & (b > g * 0.8)
    H, W = wat.shape
    ui = np.zeros_like(wat)       # the game's top, bottom and left bars
    ui[:int(0.095 * H)] = True
    ui[int(0.91 * H):] = True
    ui[:, :int(0.03 * W)] = True
    return wat & ~ui, ~ui


def pinned_h(pins, g, hh, size):
    """Homography (picture pixel to canvas pixel, tc's eight coefficients) that sends the two pins
    (picture pixel, canvas pixel) exactly to each other: a perspective step with terms `g`, `hh`
    about the picture centre, then the similarity the two pins fix."""
    W, H = size
    cx, cy = W / 2, H / 2
    r = []
    for (px, py), _ in pins:
        x, y = px - cx, py - cy
        den = 1 + g * x + hh * y
        r.append(complex(x / den, y / den))
    c = [complex(*q) for _, q in pins]
    a = (c[1] - c[0]) / (r[1] - r[0])
    b = c[0] - a * r[0]
    S = np.array([[a.real, -a.imag, b.real], [a.imag, a.real, b.imag], [0, 0, 1]])
    P = np.array([[1, 0, 0], [0, 1, 0], [g, hh, 1]])
    T = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
    M = S @ P @ T
    M = M / M[2, 2]
    return np.array([M[0, 0], M[0, 1], M[0, 2], M[1, 0], M[1, 1], M[1, 2], M[2, 0], M[2, 1]])


def fit_pinned(cv, sh, pins, size, iters=3):
    """Search the two perspective terms for the best coastline score with the pins held exact:
    a grid, then two finer grids round the best cell. Returns (h, score)."""
    best = (-1.0, 0.0, 0.0)
    g_step, h_step = 2.5e-5, 2e-5
    g0, h0 = 0.0, 0.0
    ng, nh = 4, 15
    for _ in range(iters):
        for i in range(-ng, ng + 1):
            for j in range(-nh, nh + 1):
                g, hh = g0 + i * g_step, h0 + j * h_step
                sc = tc.score(cv, pinned_h(pins, g, hh, size), sh)
                if sc > best[0]:
                    best = (sc, g, hh)
        g0, h0 = best[1], best[2]
        g_step, h_step = g_step / 4, h_step / 4
        ng, nh = 4, 4
    return pinned_h(pins, best[1], best[2], size), best[0]


def read_badges(path):
    """The `n/m` load badges the game draws over vehicles, read with tesseract from three
    versions of the picture (as it is, brightness, and brightest channel, the last two doubled in
    size and limited to digits and the slash, which finds the small or coloured ones the first
    pass misses). Returns dicts text, px, py (the middle of the text, full-size picture pixels)
    and conf, strongest first, one per place. A badge's text sits above or beside its vehicle, 40
    to 120 pixels away, so it is a loose anchor; a coloured one can come out with a digit missing."""
    if not shutil.which("tesseract"):
        sys.exit("--badges needs the tesseract program")
    im = Image.open(path).convert("RGB")
    arr = np.array(im)
    big = (im.width * 2, im.height * 2)
    variants = [("rgb", im, 1, False),
               ("lum", im.convert("L").resize(big, Image.LANCZOS), 2, True),
               ("max", Image.fromarray(arr.max(2)).resize(big, Image.LANCZOS), 2, True)]
    found = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, img, k, digits in variants:
            f = os.path.join(tmp, name + ".png")
            img.save(f)
            cmd = ["tesseract", f, os.path.join(tmp, name), "--psm", "11"]
            if digits:
                cmd += ["-c", "tessedit_char_whitelist=0123456789/"]
            subprocess.run(cmd + ["tsv"], capture_output=True)
            with open(os.path.join(tmp, name + ".tsv"), newline="") as fh:
                for row in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
                    t = (row.get("text") or "").strip().strip(",.;:")
                    if not re.fullmatch(r"\d{1,3}/\d{1,3}", t) or float(row["conf"]) < 40:
                        continue
                    x, y = int(row["left"]), int(row["top"])
                    w, h = int(row["width"]), int(row["height"])
                    found.append(dict(text=t, px=(x + w / 2) / k, py=(y + h / 2) / k, conf=float(row["conf"])))
    found.sort(key=lambda b: -b["conf"])
    out = []
    for b in found:
        if all(math.hypot(b["px"] - o["px"], b["py"] - o["py"]) > 30 for o in out):
            out.append(b)
    return out


class Shot:
    """What tc.refine and tc.score read of a picture: the water edge, half size."""

    def __init__(self, wat, keep):
        H, W = wat.shape
        self.W, self.H = W, H
        small = Image.fromarray((wat * 255).astype(np.uint8)).resize(
            (W // tc.DS, H // tc.DS), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
        s0 = np.array(small, float) / 255
        gy, gx = np.gradient(s0)
        e = np.clip(np.hypot(gx, gy) * 4, 0, 1)
        self.S = np.array(Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), float) / 255
        self.w = np.array(Image.fromarray((keep * 255).astype(np.uint8)).resize(
            (W // tc.DS, H // tc.DS)), float) / 255
        self.Sw = self.S * self.w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("save")
    ap.add_argument("shot")
    ap.add_argument("--vehicle", action="append", required=True, type=lambda t: parse_pt(t, 2))
    ap.add_argument("--hint", required=True, type=lambda t: parse_pt(t, 2))
    ap.add_argument("--class", dest="cls", default="vehicle/ship/")
    ap.add_argument("--in-frame", action="append", default=[], type=lambda t: parse_pt(t, 2))
    ap.add_argument("--covered", action="append", default=[], type=lambda t: parse_pt(t, 4))
    ap.add_argument("--ui", action="store_true")
    ap.add_argument("--scale-range", default="3.5,11", type=lambda t: parse_pt(t, 2))
    ap.add_argument("--map")
    ap.add_argument("--pick", type=int, default=1)
    ap.add_argument("--no-refine", action="store_true")
    ap.add_argument("--badges", action="store_true")
    ap.add_argument("--project", action="append", default=[])
    ap.add_argument("--pixel", action="append", default=[], type=lambda t: parse_pt(t, 2))
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if np is None:
        sys.exit("shot_place.py needs numpy and Pillow")
    if len(args.vehicle) < 2:
        sys.exit("name at least two vehicles with --vehicle")
    hint = args.hint if len(args.hint) >= 3 else args.hint + [1000.0]
    picks = [dict(px=v[0], py=v[1], deg=v[2] if len(v) > 2 else None) for v in args.vehicle]
    W, H = Image.open(args.shot).size

    data = decompress(open(args.save, "rb").read())
    cands = [r for r in read_instances(data, (args.cls,))
             if math.hypot(r["x"] - hint[0], r["y"] - hint[1]) <= hint[2] + 1000]
    if len(cands) < 2:
        sys.exit("fewer than two %s instances near the hint" % args.cls)
    covered = [tuple(c) for c in args.covered]
    if args.ui:                   # the open building window, top icon bar and bottom bar, as fractions of the frame
        covered += [(0.75 * W, 0.0, W, 0.68 * H), (0.27 * W, 0.0, 0.73 * W, 0.045 * H), (0.0, 0.915 * H, W, H)]
    ranked = hypotheses(cands, picks, (W, H), hint, args.scale_range, [tuple(p) for p in args.in_frame], covered)
    if not ranked:
        sys.exit("no pairing fits the scale range, the hint circle and the --in-frame points")
    print("%d vehicles of the class near the hint, %d pairings kept" % (len(cands), len(ranked)))
    print("rank score heading-err px/m rot centre_x centre_y unlisted-in-frame")
    for n, r in enumerate(ranked[:args.top], 1):
        print("%4d %6.1f %5.1f %6.2f %5.0f %8.0f %8.0f %d" % (
            n, r["score"], r["heading_err"], r["scale"], r["rot"], r["centre"][0], r["centre"][1], r["unlisted"]))
    if len(ranked) > 1:
        print("margin to the runner-up: %.1f" % (ranked[1]["score"] - ranked[0]["score"]))
    r = ranked[args.pick - 1]
    sim = r["sim"]

    result = dict(shot=os.path.basename(args.shot), size=[W, H], pairing=[r["i"], r["j"]],
                  scale_px_per_m=r["scale"], rotation_deg=r["rot"], view_centre=list(r["centre"]),
                  margin=(ranked[1]["score"] - ranked[0]["score"]) if len(ranked) > 1 else None)
    h = None

    def screen_of(x, y):                  # a map point in the picture, similarity until a fit exists
        u, v = sim.to_screen(x, y)
        return u, -v
    if args.out or not args.no_refine:
        map_png = args.map or make_map(args.save, args.out or ".", r["centre"])
        ref, view = load_map(map_png)
        mpp, xmin, ymax = view["metres-per-pixel"], view["x-min"], view["y-max"]
        N = max(ref.shape[:2])
        tc.N = N
        cx, cy = xmin + (N / 2) * mpp, ymax - (N / 2) * mpp      # the world point at the canvas centre

        def canvas_px(x, y):
            return (x - cx) / mpp + N / 2, -(y - cy) / mpp + N / 2

        def h_from(fn):
            p0, p1, p2 = fn(0, 0), fn(1, 0), fn(0, 1)
            return [p1[0] - p0[0], p2[0] - p0[0], p0[0], p1[1] - p0[1], p2[1] - p0[1], p0[1], 0.0, 0.0]
        h0 = np.array(h_from(lambda px, py: canvas_px(*sim.to_world(px, -py))))
        water = ref[..., 2] - ref[..., 0] > 55
        cv_arr = np.zeros((N, N))
        cv_arr[:ref.shape[0], :ref.shape[1]] = np.clip(edge(water) * 6, 0, 1)
        cv = Image.fromarray((cv_arr * 255).astype(np.uint8))
        wat, keep = shot_water(args.shot)
        h = h0
        if not args.no_refine and 0.02 < wat.mean() < 0.98:
            sh = Shot(wat, keep)
            s0 = tc.score(cv, h0, sh)
            pins = [((pk["px"], pk["py"]), canvas_px(c["x"], c["y"]))
                    for pk, c in ((picks[0], cands[r["i"]]), (picks[1], cands[r["j"]]))]
            h, s1 = fit_pinned(cv, sh, pins, (W, H))
            result.update(score_before=s0, score_after=s1)
            print("coastline match: %.3f from the pairing, %.3f after refinement" % (s0, s1))
        elif not args.no_refine:
            print("no usable water in the picture; kept the similarity transform")
        h = np.array(h, float)
        centre = (cx, cy)
        cen = tc.to_world(h, (W / 2, H / 2), centre, mpp)
        result["view_centre"] = [float(cen[0]), float(cen[1])]
        _, pxm, up, _ = tc.local(h, cen, centre, mpp)
        top = tc.local(h, tc.to_world(h, (W / 2, 0.15 * H), centre, mpp), centre, mpp)[1]
        bottom = tc.local(h, tc.to_world(h, (W / 2, 0.85 * H), centre, mpp), centre, mpp)[1]
        result.update(scale_px_per_m=float(pxm), screen_up_dir=[float(up[0]), float(up[1])],
                      scale_top_over_bottom=float(top / bottom),
                      corners=[[float(v) for v in tc.to_world(h, p, centre, mpp)]
                               for p in ((0, 0), (W, 0), (W, H), (0, H))])
        result["homography"] = [float(v) for v in h]
        res_list = []
        for pk, c in ((picks[0], cands[r["i"]]), (picks[1], cands[r["j"]])):
            sp = tc.to_screen(h, np.array([c["x"], c["y"]]), centre, mpp)
            res_list.append(dict(picked=[pk["px"], pk["py"]], projected=[float(sp[0]), float(sp[1])],
                                 error_px=float(math.hypot(sp[0] - pk["px"], sp[1] - pk["py"])), slot=c["slot"]))
        result["vehicles"] = res_list
        print("view centre (%.0f, %.0f), %.2f px/m at the centre, %.2f times as many px/m 15%% from the top "
              "as 15%% from the bottom, screen-up toward (%.2f, %.2f)" % (
                  cen[0], cen[1], pxm, top / bottom, up[0], up[1]))
        for v in res_list:
            print("  vehicle slot %s: picked %s, save puts it at %s, %.0f px off" % (
                v["slot"], [round(t) for t in v["picked"]], [round(t) for t in v["projected"]], v["error_px"]))
        for p in args.pixel:
            w = tc.to_world(h, (p[0], p[1]), centre, mpp)
            print("pixel %.0f,%.0f is at map %.0f, %.0f (on the ground plane)" % (p[0], p[1], w[0], w[1]))
            result.setdefault("pixels", []).append(dict(pixel=p[:2], map=[float(w[0]), float(w[1])]))

        def screen_of(x, y):              # noqa: F811 -- the fitted homography replaces the similarity
            sp = tc.to_screen(h, np.array([x, y]), centre, mpp)
            return float(sp[0]), float(sp[1])
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            sh2 = Shot(wat, keep)
            cols = [tc.warp(Image.fromarray(ref[..., k].astype(np.uint8)), h, sh2) for k in range(3)]
            col = np.stack(cols, -1) * 255
            small = np.array(Image.open(args.shot).convert("RGB").resize((W // tc.DS, H // tc.DS))).astype(float)
            valid = (col.sum(2) > 0)[..., None]
            blend = np.where(valid, 0.5 * col + 0.5 * small, small).astype(np.uint8)
            name = os.path.splitext(os.path.basename(args.shot))[0]
            Image.fromarray(blend).save(os.path.join(args.out, name + "-blend.png"))
            with open(os.path.join(args.out, name + "-place.json"), "w") as f:
                json.dump(result, f, indent=1)
    if args.badges or args.project:
        badges = read_badges(args.shot) if args.badges else []
        proj = []
        for prefix in args.project:
            for v in read_instances(data, (prefix,)):
                u, w_ = screen_of(v["x"], v["y"])
                if 0 <= u < W and 0 <= w_ < H:
                    proj.append(dict(model=v["model"].rsplit("/", 1)[-1][:-4], slot=v["slot"], px=u, py=w_))
        for b in badges:
            near = sorted(proj, key=lambda q: math.hypot(q["px"] - b["px"], q["py"] - b["py"]))[:3]
            b["nearest"] = [dict(model=q["model"], slot=q["slot"], dx=q["px"] - b["px"], dy=q["py"] - b["py"],
                                 dist=math.hypot(q["px"] - b["px"], q["py"] - b["py"])) for q in near]
            b["within_150px"] = sum(1 for q in proj if math.hypot(q["px"] - b["px"], q["py"] - b["py"]) <= 150)
            print("badge %s at (%.0f, %.0f), conf %.0f: %s" % (
                b["text"], b["px"], b["py"], b["conf"],
                "; ".join("%s slot %s %+.0f,%+.0f px" % (q["model"], q["slot"], q["dx"], q["dy"]) for q in b["nearest"])
                or "no projected vehicle"))
        if proj:
            print("%d projected vehicles in the picture" % len(proj))
        result["badges"] = badges
        result["projected"] = proj
        if args.out:
            name = os.path.splitext(os.path.basename(args.shot))[0]
            with open(os.path.join(args.out, name + "-place.json"), "w") as f:
                json.dump(result, f, indent=1)
    if args.json:
        print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
