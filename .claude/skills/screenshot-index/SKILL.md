---
name: screenshot-index
description: Look up or extend the index of the user's game screenshots (tools/screenshot_index.py, work files in local/screenshots/). Use when a task might already have a picture ("did we screenshot the depot ring", "which shots go with save X"), when the user says they took new screenshots, or when asked to label, rebuild or search the index.
---

# Screenshot index: find a picture before asking for one

Why: the user's screenshots (4K, local time in the file name) hold figures, window titles and layouts the saves do not. Reading them blind costs a lot of context (a first pass over 371 shots cost about 200,000 tokens). The index lets a session look a topic or a UTC time up first. The tool is `tools/screenshot_index.py` (usage and the label format are in its docstring and `tools/README.md`). Its work files (labels, index, OCR text, `hud.csv`) are private: they hold save names and times, and the pictures show company names, install paths and account folders. Keep them in the gitignored `local/screenshots/` and never copy one, a path, a company name or an account name into `docs/`, a commit or tool output.

Every command takes `--work local/screenshots`. The screenshot folder and the game's save folders are found by themselves (`--shots`, `--saves-dir` override). Run as `python3 -I tools/screenshot_index.py --work local/screenshots COMMAND`.

## Look something up (cheap, do this first)

- `local/screenshots/INDEX.md`: a "Find by topic" table, then one section per cluster (UTC range, game, what it shows, points of interest, saves written within 4 minutes, links to the note that used it, OCR text, per-shot UTC ids).
- `find TERM [TERM ...]` searches the text read off every shot (window titles, town labels `Name (123)`, dates, figures) and prints id, UTC time and the cluster's label. Small map labels are sometimes missed, so no hit is not proof.
- `hud` writes `hud.csv` (game date, account, earnings, people delivered and cargo delivered, both totals since the game started, per full-screen shot) when a question is "which shots are from the game at date X".
- Then open only the PNGs that matter, as a crop to the scratchpad (a window title or a label reads well), not the whole 4K frame.
- To tie a picture to a place on the map (view centre, heading, the map point under a pixel), use `.claude/skills/shot-place/SKILL.md`.

## Add new shots

1. `ocr` (cached, about 2 to 6 s a shot with 8 workers), then `todo` for the clusters no label covers (shots more than 2 minutes apart start a new one).
2. The user's rule: shots come in clusters of one subject. Ask the user for a one-line note per cluster (what they were testing) before reading pictures. A note, the OCR text (`find`, or the cluster's `ocr/<id>.json`) and the saves written around it usually label a cluster by themselves.
3. Only then look: `sheets --out DIR` (scratchpad) gives 12-up contact sheets, enough to tell a New Game screen from a map layer; crop for text.
4. Add rows to `local/screenshots/labels.tsv` (columns in the tool's docstring: first, last, game, topic, what, points of interest, sure, links; reuse existing topic words). Label a range, not each shot; add a per-shot row only where one shot differs. Tie a cluster to the saves around it and to the `local/games/<game>/part-N.md` or `docs/` note that used it. Look the game up by seed and climate (header `map_seed`), not by the save-name prefix. Then `build`, and `check` to list label facts the OCR did not see (advisory: look at the picture before changing a label).

## Rules

- Do not trust a thumbnail for numbers or names: a first read gave Chagford "255" for what is "251 ^". Zoom a crop and re-read before writing a figure; mark thumbnail-only reads `guess`. HUD figures are OCR reads too.
- A load card shows the save's real date, not the game date; the index says "save-card date".
- Mask company names, account-derived names and install paths in labels (`<name> Transport`). The editor's import/export window shows a Steam path: describe it, do not copy it.
- Use the game's internal words in labels, as `docs/glossary.md` has them.
- OCR needs the `tesseract` program and Pillow; the other commands use only the standard library.
