---
name: mine-saves
description: Rebuild or refresh local/mined (the summary JSON per mod.io catalog save and index.csv) with tools/mine_saves.py, and use the result (top_saves.py, index.csv columns). Use when the user asks to "run the mining", rebuild the summaries or the index, when a new summary field or index column was added, or when new catalog saves were downloaded.
---

# Mining the catalog saves

`tools/mine_saves.py` reads the mod.io saves and writes one `tf3-save-summary.json` per save (and, unless `--no-maps`, a terrain map) into `local/mined/`, then rewrites `local/mined/index.csv` from all the summaries. Layout, columns and the lookup recipes are in `local/README.md` ("Finding things in `mined/`") and the script's docstring. Output is other people's data: it stays in gitignored `local/`, and nothing from it goes into `docs/`, a commit or tool output beyond mod ids, keys and counts.

## Which run

| Goal | Command |
|---|---|
| Index only (a new `index_row` column built from fields the summaries already hold) | `python3 -I tools/mine_saves.py --no-maps local/mined` (no save arguments: moves summaries to their seed folder, rewrites `index.csv`; reads no save, takes seconds) |
| Summaries only (new summary field, new tools commit) | the batch below with `--no-maps`, then the index-only command once |
| Summaries and maps | the batch below without `--no-maps` (the default drawer is the Rust `tf3map`, about a second a save: `--tf3map BIN`, else `$TF3MAP`, else the PATH, else the sibling mapper's `target/release/tf3map`; build main first with `cargo build --release` there, and the key is that build's commit). `--mapper python` draws with `terrain_map.py` instead (a Giant map takes about 40 s and 2.5 GB). A change of drawer or of the tf3map commit redraws every map |

A change to `mine_summary.py` or what it imports changes `tools_commit`, so every save is read again: that is a full rebuild. Ask the user before starting one unless they just asked for it. Only saves whose tools commit or file changed are read again, so a repeat run is cheap.

## The batch

```
ls -d <mod.io mods dir>/*/ | xargs -P8 -n4 python3 -I tools/mine_saves.py --no-maps local/mined
python3 -I tools/mine_saves.py --no-maps local/mined        # once, alone, after the batch
```

- The mods dir is the mod.io `10640/mods` folder (`local/saves.txt` shows the paths; `tools/terrain_map.py` `MOD_DIRS` lists the usual places). Do not write the path into a committed file.
- `-P8` is the settled default (timed: `-P12` is only 1.27x faster than `-P6`; the user finds `-P10` and up disruptive). Keep `-n4`.
- The script lowers its own priority (nice 19, idle I/O; `--no-nice` turns it off), so no `nice` prefix is needed. Parallel runs race on `index.csv`; that is why the last call runs alone.
- Run it in the background with the output in the scratchpad (`> $SCRATCH/mine.log 2>&1`) and wait for the completion notice; do not poll.
- Back up `index.csv` into the scratchpad first if a column changed.
- Do not edit `tools/` files while the batch runs (each worker starts a fresh `python3`, so a half-finished edit is read mid-run). Do not `pkill -f` or `pgrep -f` a pattern that is in your own shell command line (it kills the shell); kill by PID, and kill the `xargs` parent and its children both.

## Check afterwards

- The last line of the log: `N read, M unchanged, K failed; R rows`. A failed save is reported; `error` rows in `index.csv` have `header` = `error`.
- Row count equals the number of summaries (`find local/mined -name tf3-save-summary.json | wc -l`).
- Every `tools_commit` in the index is the same (a mixed column means a partial run: run the batch again).
- `mods` count equals the number of keys in `mod_list` on each row.

## Use the result

- `python3 -I tools/top_saves.py local/mined/index.csv [--out local/mined/top-play-periods-DATE.md]` ranks saves by play periods among those whose mods you have (read at run time from the mod.io folder and the install's `mods/release` and `dlcs`); `--owned` lists the `urbangames_` and `ug_` keys and whether you have each (the pre-order pack has no `dlcs/` folder).
- The game's load list shows a save by its file name (`source_name`), not the mod.io title (`name`); several catalog saves share a file name, so give both.
- Read `index.csv` with `csv` (names hold commas), not `awk -F,`.
