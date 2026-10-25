---
name: mine-saves
description: Rebuild or refresh local/mined (the summary JSON per save, in four corpora - mod.io catalog saves and maps, the user's own saves and map-editor maps - and index.csv) with tools/mine_saves.py, and use the result (top_saves.py, index.csv columns). Use when the user asks to "run the mining", rebuild the summaries or the index, when a new summary field or index column was added, when new catalog saves were downloaded, or when the user has made new saves or maps to mine.
---

# Mining saves

`tools/mine_saves.py` reads saves and writes one `tf3-save-summary.json` per save (and, unless `--no-maps`, a terrain map) into `local/mined/<corpus>/`, then rewrites `local/mined/index.csv` from all the summaries. Layout, columns and the lookup recipes are in `local/README.md` ("Finding things in `mined/`") and the script's docstring. The corpus is what was mined: `catalog-saves` and `catalog-maps` (mod.io mods' `savegames/` and `maps/`), `own-saves` and `own-maps` (the game's `local/save/` and `local/save_maps/`, path in `local/README.md`). Output is other people's data (own saves carry the user's company name): it stays in gitignored `local/`, and nothing from it goes into `docs/`, a commit or tool output beyond mod ids, keys and counts.

## Which run

| Goal | Command |
|---|---|
| Index only (a new `index_row` column built from fields the summaries already hold) | `python3 -I tools/mine_saves.py --no-maps local/mined` (no save arguments: moves summaries to their seed folder, rewrites `index.csv`; reads no save, takes seconds) |
| Summaries only (new summary field, new tools commit) | rebuild the crate, then the batch below with `--no-maps`, then the index-only command once |
| Summaries and maps | the batch below without `--no-maps` (the default drawer is the Rust `tf3map`, about a second a save: `--tf3map BIN`, else `$TF3MAP`, else the PATH, else the sibling mapper's `target/release/tf3map`; build main first with `cargo build --release` there, and the key is that build's commit). `--mapper python` draws with `terrain_map.py` instead (a Giant map takes about 40 s and 2.5 GB). A change of drawer or of the tf3map commit redraws every map |

The summaries come from the Rust `tools/mine-summary-rs` (build: `cargo build --release` there, from a git checkout so `--version` names a commit; `--summary python` runs `mine_summary.py` instead, about 100 times slower). A change to the crate (or, with `--summary python`, to `mine_summary.py` or what it imports) changes `tools_commit`, so every save is read again: that is a full rebuild, about 8 minutes for ~1,100 saves with the Rust reader. The two readers must give the same summary: a change to one is made in the other in the same commit, and checked by comparing both over a few saves. Ask the user before starting a full rebuild unless they just asked for it. Only saves whose tools commit or file changed are read again, so a repeat run is cheap.

## The batch

```
ls -d <mod.io mods dir>/*/ | xargs -P8 -n4 python3 -I tools/mine_saves.py --no-maps local/mined
python3 -I tools/mine_saves.py --no-maps local/mined        # once, alone, after the batch
```

- Own corpora (the user's saves and map-editor maps; the folders are `<game local>/save` and `<game local>/save_maps`, path in `local/README.md`, never in a committed file): `python3 -I tools/mine_saves.py local/mined <game local>/save` and the same with `save_maps`, which `xargs` cannot split by folder, so give the files: `ls <game local>/save/*.sav | xargs -d '\n' -P8 -n4 python3 -I tools/mine_saves.py local/mined`, likewise `save_maps/*.sav`. A bare `.sav` is an own save unless its folder is named `save_maps`. Re-run it after the user makes new saves: only new or changed files are read (with the Rust reader the whole own set, ~520 files, takes minutes: first full run 2026-10-24). Both own folders in one pipe: `ls <game local>/save_maps/*.sav <game local>/save/*.sav | xargs -d '\n' -P8 -n4 python3 -I tools/mine_saves.py local/mined`. Autosaves are mined too; the game prunes them (20 in all), so their folders outlive the files and the index keeps their rows (delete a folder by hand to drop it).
- The mods dir is the mod.io `10640/mods` folder (`local/saves.txt` shows the paths; `tools/terrain_map.py` `MOD_DIRS` lists the usual places). Do not write the path into a committed file.
- `-P8` is the settled default (timed: `-P12` is only 1.27x faster than `-P6`; the user finds `-P10` and up disruptive). Keep `-n4`.
- The script lowers its own priority (nice 19, idle I/O; `--no-nice` turns it off), so no `nice` prefix is needed. Parallel runs race on `index.csv`; that is why the last call runs alone.
- Run it in the background with the output in the scratchpad (`> $SCRATCH/mine.log 2>&1`) and wait for the completion notice; do not poll.
- Back up `index.csv` into the scratchpad first if a column changed.
- Do not edit `tools/` files while the batch runs (each worker starts a fresh `python3`, so a half-finished edit is read mid-run; do not rebuild the crate either). Do not `pkill -f` or `pgrep -f` a pattern that is in your own shell command line (it kills the shell); kill by PID, and kill the `xargs` parent and its children both.

## Check afterwards

- The last line of the log: `N read, M unchanged, K failed; R rows`. A failed save is reported; `error` rows in `index.csv` have `header` = `error`.
- Row count equals the number of summaries, and the `corpus` column of each row is its first folder under `local/mined/` (`find local/mined -name tf3-save-summary.json | wc -l`).
- Every `tools_commit` in the index is the same (a mixed column means a partial run: run the batch again). Known exception: summaries of catalog mods whose folders are gone from the mod.io folder (unsubscribed; 23 on 2026-10-24) keep their old commit, and nothing re-reads them; that is not a partial run.
- `mods` count equals the number of keys in `mod_list` on each row.

## Use the result

- Rankings and size tables describe the catalog: `top_saves.py` and `map_size_tables.py` read only the two `catalog-*` corpora unless given `--corpus all` or a list.
- `python3 -I tools/top_saves.py local/mined/index.csv [--out local/mined/top-play-periods-DATE.md]` ranks saves by play periods among those whose mods you have (read at run time from the mod.io folder and the install's `mods/release` and `dlcs`); `--owned` lists the `urbangames_` and `ug_` keys and whether you have each (the pre-order pack has no `dlcs/` folder).
- The game's load list shows a save by its file name (`source_name`), not the mod.io title (`name`); several catalog saves share a file name, so give both.
- Read `index.csv` with `csv` (names hold commas), not `awk -F,`.
