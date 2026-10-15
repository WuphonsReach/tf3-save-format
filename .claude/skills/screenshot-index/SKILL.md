---
name: screenshot-index
description: Look up or extend the index of the user's game screenshots (local/screenshots/INDEX.md). Use when a task might already have a picture ("did we screenshot the depot ring", "which shots go with save X"), when the user says they took new screenshots, or when asked to label, rebuild or search the index.
---

# Screenshot index: find a picture before asking for one

Why: the user's screenshots (`~/Pictures/Screenshots/Screenshot_YYYYMMDD_HHMMSS.png`, mostly 4K, local time EDT) hold figures, window titles and layouts the saves do not. Reading them blind costs a lot of context (a first pass over 371 shots cost about 200,000 tokens). The index lets a session look a topic or a UTC time up first. It lives in the gitignored `local/` (home paths, other people's names): never copy it, a path or a company or account name into `docs/`, a commit or tool output.

## Look something up (cheap, do this first)

- `local/screenshots/INDEX.md`: "Find by topic" table at the top, then one section per cluster (UTC range, game, what it shows, points of interest, saves written within 4 minutes, links to the docs note, OCR text, per-shot UTC ids).
- `python3 local/screenshot_index.py find TERM [TERM ...]` searches the OCR text of every shot (window titles, town labels `Name (123)`, dates, figures) and prints id, UTC time and the cluster's label. Small text on a map label is often missed by OCR, so no hit is not proof.
- Then open only the PNGs that matter. Zoom with a crop (Pillow, to the scratchpad), not the whole 4K frame; crops of a window title or a label read well.

## Add new shots

1. `python3 local/screenshot_index.py --date YYYYMMDD ocr` (cached in `local/screenshots/ocr/`, about a second a shot), then `todo` to list the unlabelled clusters (shots more than 2 minutes apart start a new one).
2. Read OCR first: `find` or open `screenshots/ocr/<id>.json`. It often names the window, the save and the game date by itself (the 20:48 load dialog and the context panel needed no image view). Only then look at pictures: `sheets --out DIR` (scratchpad) makes 12-up contact sheets, enough to tell a New Game screen from a map layer; crop for text.
3. The user's rule: shots come in clusters, and a cluster is usually one subject. Label a range, not each shot, and add a per-shot row only where one shot differs.
4. Tie each cluster to the saves written around it (the index prints them) and to the `local/games/<game>/part-N.md` or `docs/` note that used it. Look the game up by seed and climate (header `map_seed`), not by the save-name prefix.
5. Add rows to `local/screenshots/labels.tsv` (columns in the script's docstring: first, last, game, topic, what, points of interest, sure, links; `sure` is read, seen or guess; topics are comma-separated and feed the topic table; reuse existing topic words). The 2026-10-14 rows came from `screenshots/make_labels_20261014.py`; a new day can append rows straight to `labels.tsv` instead. Then `build`, and `check` to list facts a label states that OCR did not see (advisory: look at the picture before changing a label).

## Rules

- Do not trust a thumbnail for numbers or names: a first read gave Chagford "255" for what is "251 ^". Zoom and re-read before writing a figure; mark thumbnail-only reads `guess`.
- A load card shows the save's real date (2026), not the game date; the index says "save-card date".
- Mask company names, account-derived names and install paths in labels (`<name> Transport`). The editor's import/export window shows a Steam path: describe it, do not copy it.
- Game names: use the game's internal words in labels, as `docs/glossary.md` has them.
- The script is private (it reads the user's Steam folder), so it is not in `tools/`. If a pass is a few clusters, hand-editing `labels.tsv` is fine. OCR needs only the `tesseract` binary and Pillow (no ML packages).
