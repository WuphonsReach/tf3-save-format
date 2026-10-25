# mine-summary (Rust)

A Rust port of [`../mine_summary.py`](../mine_summary.py): it reads one Transport Fever 3 `.sav` and prints the same JSON summary (schema v8, [`../schema/tf3-save-summary.v8.schema.json`](../schema/tf3-save-summary.v8.schema.json)), with the same keys in the same order and the same number and string formats. It reads the save and, for the vehicle classes, the model files in the game install's `base/content/vehicle` archives (text metadata, read at run time, nothing kept). It writes nothing but standard output. Unofficial fan tool, MIT OR Apache-2.0.

The Python is the reference. When the two disagree, the Python's reading (and the notes in `docs/`) decide, and the port follows. Like the scripts, this is reference code with no support.

## Build and run

```
cargo build --release
target/release/mine-summary SAVE.sav [--mod-id ID] [--kind savegame|map] [--game DIR]
target/release/mine-summary --version
```

Rust 1.99 or later (edition 2024). Crates: `memchr` and `zstd` (the zstd C library, built by `zstd-sys`).

- Without options the output equals `mine_summary.py SAVE.sav`: `name` is the file name without `.sav`, `mod_id`, `author` and `url` are null, `tags` is empty, `kind` is `savegame`. `--mod-id` and `--kind` fill those two the way `mine_saves.py` passes them; the mod.io fields (`name`, `author`, `tags`, `url`) are left to the caller.
- `--game DIR` names the install folder; without it the usual Steam places in the home folder are tried, as `vehicle_counts.py` does.
- `tools_commit` is the last commit that changed this folder (`-dirty` with uncommitted changes), not the Python's script commit. `--version` prints it.

## Layout

- `src/reader/`: readers copied from tf3-save-mapper's core crate (same author and licence; each file names its origin): the zstd container, the model table and instances, the zip reader. Kept apart so the folder can be swapped for a shared crate.
- `src/header.rs`, `stream.rs`, `lua.rs`, `states.rs`, `journal.rs`, `counts.rs`: ports of `save_header.py`, `tf3save.py`, `journal.py`, `vehicle_counts.py`, `industry_counts.py` and `summarise_states`, in the Python's order of reading, so the first error met is the same.
- `src/json.rs`: writes JSON as Python's `json.dump(indent=2, ensure_ascii=False)` does (floats as Python's `repr`).
- `tests/synthetic.rs`: a hand-built stream with one of each structure, checked against the Python's summary of it (`tests/synthetic-expected.json`). No real save is used.
