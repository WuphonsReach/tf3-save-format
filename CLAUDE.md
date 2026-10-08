# tf3-save-format

Public documentation of the Transport Fever 3 `.sav` format. MIT licensed. The notes in `docs/` are the product; `tools/` holds read-only reference scripts with no support (see `tools/README.md`).

## Related local repos

| Repo | Role |
|---|---|
| `../tf3-save-editor` | Fork of TBK/tf3-save-editor (MIT OR Apache-2.0, used here under MIT). Its `docs/FORMAT.md` is the base layout for container, header and Lua states. `tools/save_header.py` follows its `header.rs`; the notice is in `THIRD_PARTY_NOTICES.md`. |

## Rules for what goes in

- Facts about the format only. Never commit `.sav` files, decompressed streams, extracted preview images, or screenshots of other people's maps. `.gitignore` blocks the common ones.
- Write notes in our own words. Do not copy text from `tf3-save-editor`'s `FORMAT.md`. Link to it and credit it instead. Code ported from it keeps a pointer to `THIRD_PARTY_NOTICES.md`.
- Cite mod.io catalog saves by mod id and URL. Record only facts read from them (version, map size, start year, mod list, counts). No per-save dumps in the repo.
- Strip local details before committing: home paths, file mtimes, Steam user ids, install paths. Tool output must not contain them either (`mine_saves.py` keeps size and mtime in a gitignored `.mine_state.json`).
- Tag each claim with the format versions it was checked on (for example "568 to 604" or "604 only").
- Label how sure a claim is: Confirmed, Observed or Open (defined in `docs/README.md`).
- Offsets move between saves. Describe how to find a structure by pattern, never by a fixed offset.

## Tools

- Read only. No script in this repo writes a `.sav`.
- Standard library only (Python 3.14 for zstd; older Python needs `zstandard`). Shared code is in `tools/tf3save.py`; new scripts import it.
- Test against real saves before committing, with output to a scratch directory outside the repo.

## Conventions

- Integers are little-endian unless stated. Use the notation `str` (u32 length + bytes) and `vec<T>` (u32 count + items), matching `FORMAT.md`, so readers can move between the two.
- Hex dumps: lowercase, space-separated bytes, short enough to show the point.
- Put numbers that change (counts of saves, versions seen) in dated notes such as `docs/versions.md`, not in this file or the README.
