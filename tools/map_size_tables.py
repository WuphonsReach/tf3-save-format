#!/usr/bin/env python3
"""Print the two tables of docs/map-sizes.md from a folder of mine_saves.py summaries.

Usage: map_size_tables.py MINED_DIR [--extra SIZE,FORMAT,WxH ...] [--corpus NAME[,NAME] | all]

Read only, no saves. MINED_DIR is the OUT_DIR of mine_saves.py (it is searched for
tf3-save-summary.json). Only the corpus folders named by --corpus are read (default `catalog-saves,catalog-maps`;
`all` adds the player's own saves and maps). A summary with no `settings` (versions 568 and 585) is skipped.

Table 1 has a row for each of the 40 combinations of `map.size` (1 to 8) and `map.format`
(1 to 5) in that order. The width and height of a combination is the one most saves with those
settings have; a combination no save has stays blank, and a tie is reported on stderr (the first
is used). Table 2 lists the saves whose width and height differ from their combination's. It has
the first six columns of table 1, then the combination whose dimensions they are (the first row
of table 1 that has them), then the map's title and mod.io id.

--extra adds a game that is not in MINED_DIR (a save you made yourself, a New Game readout), for
example `--extra 1,2,2560x5120`. It counts like one more save with those settings.

The titles are the public mod.io titles. Paste the output into the note and check it first:
a changed cell is a new fact (or a new oddity) that the surrounding text may need to mention.
"""
import glob
import html
import json
import os
import sys
from collections import Counter, defaultdict

SIZES = ['Tiny', 'Small', 'Medium', 'Large', 'Very Large', 'Huge', 'Megalomaniac', 'Gigantomaniac']
FORMATS = range(1, 6)


def position(label):
    """'3 (Medium, default)' -> 3"""
    return int(str(label).split()[0])


def read(mined, extra, corpora):
    seen = defaultdict(Counter)
    odd_candidates = []
    for path in glob.glob(os.path.join(mined, '*', '**', 'tf3-save-summary.json'), recursive=True):
        if corpora and os.path.relpath(path, mined).split(os.sep)[0] not in corpora:
            continue
        d = json.load(open(path))
        s = d.get('settings')
        if not s or 'map.size' not in s or not d.get('map_w_m'):
            continue
        key = (position(s['map.size']), position(s['map.format']))
        dims = (d['map_w_m'], d['map_h_m'])
        seen[key][dims] += 1
        odd_candidates.append((key, dims, d))
    for spec in extra:
        size, fmt, dims = spec.split(',')
        w, h = dims.lower().split('x')
        seen[(int(size), int(fmt))][(int(w), int(h))] += 1
    return seen, odd_candidates


def modal(seen):
    """The usual dimensions of each combination."""
    out = {}
    for key, c in seen.items():
        top = c.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            print(f'tie for {key}: {top}', file=sys.stderr)
        out[key] = top[0][0]
    return out


def cell(key, usual):
    d = usual.get(key)
    if not d:
        return '', ''
    return f'{d[0]} x {d[1]}', f'{d[0] * d[1] / 1e6:.1f}'


def main(argv):
    extra, args, corpus = [], [], 'catalog-saves,catalog-maps'
    it = iter(argv)
    for a in it:
        if a == '--extra':
            extra.append(next(it))
        elif a == '--corpus':
            corpus = next(it)
        else:
            args.append(a)
    if len(args) != 1:
        sys.exit(__doc__)
    seen, cands = read(args[0], extra, None if corpus == 'all' else corpus.split(','))
    usual = modal(seen)
    head = '| `map.size` | `map.format` | Size | Format | Width x height, m | Area, km² |'
    print(head + '\n|---|---|---|---|---|---|')
    for s in range(1, 9):
        for f in FORMATS:
            dim, area = cell((s, f), usual)
            print(f'| {s} | {f} | {SIZES[s - 1]} | 1 : {f} | {dim} | {area} |')
    first_row = {}
    for s in range(1, 9):
        for f in FORMATS:
            if (s, f) in usual:
                first_row.setdefault(usual[(s, f)], (s, f))
    rows = []
    for key, dims, d in cands:
        if usual[key] != dims:
            rows.append((key, dims, d))
    print('\n' + head[:-1] + '| The dimensions are those of | Map |\n|---|---|---|---|---|---|---|---|')
    for key, dims, d in sorted(rows, key=lambda r: (r[0], r[1], r[2]['mod_id'])):
        s, f = key
        match = first_row.get(dims)
        fits = f'{SIZES[match[0] - 1]} 1 : {match[1]}' if match else ''
        slug = (d.get('url') or '').rstrip('/').split('/')[-1]
        link = f'[{html.unescape(d["name"])}](https://mod.io/g/transportfever3/m/{slug}) ({d["mod_id"]})'
        print(f'| {s} | {f} | {SIZES[s - 1]} | 1 : {f} | {dims[0]} x {dims[1]} | '
              f'{dims[0] * dims[1] / 1e6:.1f} | {fits} | {link} |')


if __name__ == '__main__':
    main(sys.argv[1:])
