# tf3-save-format

Public documentation of the Transport Fever 3 `.sav` format. MIT licensed. Docs only: no tools are published from here.

## Related local repos

| Repo | Role |
|---|---|
| `../tf3-save-editor` | Fork of TBK/tf3-save-editor (MIT OR Apache-2.0). Its `docs/FORMAT.md` is the base layout for container, header and Lua states. |

## Rules for what goes in

- Facts about the format only. Never commit `.sav` files, decompressed streams, extracted preview images, or screenshots of other people's maps. `.gitignore` blocks the common ones.
- Write notes in our own words. Do not copy text from `tf3-save-editor`'s `FORMAT.md` or code. Link to it and credit it instead.
- Cite mod.io catalog saves by mod id and URL. Record only facts read from them (version, map size, start year, mod list, counts). No per-save dumps.
- Strip local details before committing: home paths, file mtimes, Steam user ids, install paths.
- Tag each claim with the format versions it was checked on (for example "568 to 604" or "604 only").
- Say how sure a claim is: confirmed by experiment, inferred from the bytes, or open. Keep open questions in the doc they belong to.
- Offsets move between saves. Describe how to find a structure by pattern, never by a fixed offset.

## Conventions

- Integers are little-endian unless stated. Use the notation `str` (u32 length + bytes) and `vec<T>` (u32 count + items), matching `FORMAT.md`, so readers can move between the two.
- Hex dumps: lowercase, space-separated bytes, short enough to show the point.
- Put numbers that change (counts of saves, versions seen) in dated notes, not in this file or the README.
