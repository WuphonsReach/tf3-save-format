# tf3-save-format

Public documentation of the Transport Fever 3 `.sav` format. Licensed MIT OR Apache-2.0, matching tf3-save-editor. The notes in `docs/` are the product; `tools/` holds read-only reference scripts with no support (see `tools/README.md`).

## Related local repos

| Repo | Role |
|---|---|
| `../tf3-save-editor` | Fork of TBK/tf3-save-editor (MIT OR Apache-2.0, used here under both). Its `docs/FORMAT.md` is the base layout for container, header and Lua states. Code in `tools/` follows its readers (`header.rs`, `lua.rs`); the notice is in `THIRD_PARTY_NOTICES.md`. |

## Rules for what goes in

- Facts about the format only. Never commit `.sav` files or decompressed streams; `.gitignore` blocks the common ones.
- Images (`*.jpg`, `*.jpeg`, `*.png`, `*.webp`) are gitignored. Add one only when the user asks for that file, with `git add -f`, and only our own work: diagrams, or screenshots of our own saves. Never extracted previews or screenshots of other people's maps.
- Write notes in our own words. Do not copy text from `tf3-save-editor`'s `FORMAT.md`. Link to it and credit it instead. Code ported from it keeps a pointer to `THIRD_PARTY_NOTICES.md`.
- Cite mod.io catalog saves by mod id and URL. Record only facts read from them (version, map size, start year, mod list, counts). No per-save dumps in the repo.
- Strip local details before committing: home paths, file mtimes, Steam user ids, install paths. Tool output must not contain them either (`mine_saves.py` keeps size and mtime in a gitignored `.mine_state.json`).
- Tag each claim with the format versions it was checked on (for example "568 to 604" or "604 only").
- Label how sure a format claim is: Confirmed, Observed or Open (defined in `docs/README.md`). `docs/versions.md` (dated counts) is exempt.
- Offsets move between saves. Describe how to find a structure by pattern, never by a fixed offset.

## Tools

- Never write or modify a `.sav`. Output (PNGs, JSON summaries) goes to a directory the caller names.
- Standard library only (Python 3.14 for zstd; older Python needs `zstandard`). Shared code is in `tools/tf3save.py`; new scripts import it. Some private scripts import it too, so keep its function names and return shapes stable.
- Test against real saves before committing, with output to a scratch directory outside the repo.

## Game install

- Modder-facing files may be read: `api/tealdef/`, `base/tealdef/`, `base/mod.json`, `vscode-template/`.
- Never read, dump or analyse the native binaries: the `TransportFever3` executable, `model_editor/ModelEditor`, `extra/` and the bundled `.so` libraries. No `strings`, hex dumps, disassemblers, debuggers, or greps that scan them (use `grep -I` in the install). `.claude/hooks/tf3-no-binaries.py` blocks the common forms; it is best effort, so the rule stands without it.

## Testing in the game

- The user's own saves (tests, re-saves) are in the game's `local/save/` folder under Steam userdata for app id 3493540, next to `settings.lua`. The full path on this machine, and how to find it again, are in the gitignored `local/README.md`; never write it, or the Steam id in it, into a committed file. Read these saves, never write them.
- Tests are saves the user makes in the game, one change per save, named by what changed. Compare a save with the one it was loaded from, not with the New Game screen: the Load Game screen rewrites settings and mods in the next save.
- To find what an unnamed field holds, ask for a save made with a distinctive typed value and search the decompressed stream for it. The map seed sat in an undescribed header field (`id`) until a typed seed was searched for; searching for the word "seed" found only construction records.
- Hash a save (sha256) before it is loaded again, so a later re-hash shows whether a load changed it.

## Conventions

- Integers are little-endian unless stated. Use the notation `str` (u32 length + bytes) and `vec<T>` (u32 count + items), matching `FORMAT.md`, so readers can move between the two.
- Hex dumps: lowercase, space-separated bytes, short enough to show the point.
- Put numbers that change (counts of saves, versions seen) in dated notes such as `docs/versions.md`, not in this file or the README.
