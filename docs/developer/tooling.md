# Tooling: what to use for what

Not a format note: this is about working in the repo. The scripts in `tools/` need only Python (see [tools/README.md](../../tools/README.md)); the programs below are for looking at what they write, and none is a dependency of a script.

| Need | Use | Notes |
|---|---|---|
| Read a save, list edges, draw a map | `python3 -I tools/<script>.py` | Python 3.14 or later (zstd in the standard library); older Python needs the `zstandard` package. Standard library by default; `town_centre.py` and `screenshot_index.py` also use numpy, Pillow or the `tesseract` program, loaded only by the commands that need them |
| Look at an SVG a script wrote, as a person | A browser (Firefox or Chrome) | The vector layers stay sharp when zoomed and the layers can be toggled by a page script |
| Look at an SVG as a session (the Read tool wants a raster) | `rsvg-convert -w 1400 map.svg -o map.png` (Ubuntu package `librsvg2-bin`, version 2.61 tried) | A small command-line renderer, no browser: 0.07 s for a crop, draws paths, text, the grid and the embedded PNG terrain of `--raster` files. Write the PNG to the scratchpad, never next to the SVG. `-w` sets the output width in pixels whatever the SVG's own size |
| Same, if the page needs a real browser | `firefox --headless --no-remote --profile DIR --window-size W,H --screenshot out.png file://...` | `DIR` must be an empty folder the browser can write to; a snap Firefox cannot use `/tmp` (use a folder under its `common` directory). It stops with "already running, but is not responding" when a profile folder has a stale lock or a headless run is still alive, and a run then hangs until `timeout`: use a new empty profile folder each time, or use `rsvg-convert` |
| Check the docs before a commit | `python3 -I tools/lint_docs.py` | Must report 0 errors. Other index scripts: [CLAUDE.md](../../CLAUDE.md) |
| Cross-check a reader | `tf3se-cli`, from the sibling `../tf3-save-editor` | Read-only subcommands only; never write a real save |

## Pitfalls

- **Killing a stray browser.** `pkill -f` or `pgrep -f` with the profile name in the pattern matches the shell that runs it (the pattern is in its own command line) and kills it. Look the process up by id instead, or skip it and take a fresh profile folder.
- **A slow step in the foreground.** For a map, use `tf3map` from the sibling `tf3-save-mapper` (0.1 to 2.6 s on 14 to 394 MB saves, about 100 times faster than `terrain_map.py`, 2026-10-24); the rest of this line is the Python script. A Giant map takes about 40 s and a render of a crop up to a minute with a large save; wrap long runs in `timeout` below the tool's limit, or run them in the background.
- **Where pictures go.** Pictures of a test map under `local/games/...` (gitignored), checking pictures under the scratchpad. Nothing from a catalog save goes into the repo ([CLAUDE.md](../../CLAUDE.md)).

## Why tesseract for OCR

`tools/screenshot_index.py` reads text off screenshots with the `tesseract` program (5.5 when chosen, 2026-10-14). It was picked because it was already installed on the working machine and needs no Python package: the path of least resistance, not the result of a comparison.

A test on 2026-10-15 (376 shots from one day, 4K, bottom bar only) added two things. A digits-only crop of the account figure fills the account when the bar pass misses it. `--hud-engine rapidocr` reads the bar with RapidOCR (PP-OCR models on ONNX Runtime, about 370 MB installed with OpenCV). On 40 bars RapidOCR found 157 of 160 figures where the plain tesseract bar pass found 144; the three misses were a wrong reference value. The finished tesseract pipeline (extra full-frame passes) and RapidOCR then agreed on every figure except one shot where tesseract split a dollar amount, and each missed a few zero totals the other read. So RapidOCR is a cross-check, not a replacement. Full-frame text was compared only by counts, not against labels. All of it was checked at 3840x2160 only.
