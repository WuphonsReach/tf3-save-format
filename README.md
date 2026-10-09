# tf3-save-format

Notes on the Transport Fever 3 `.sav` file format. Unofficial, and not affiliated with or endorsed by Urban Games or Paradox Interactive.

Everything here was worked out from the outside: by reading saves the game writes, changing saves and loading them in the game, and looking at the game's moddable data files. No game files or code are copied into this repo, and nothing comes from the developer or publisher. The game changes the format between releases, so each note says which format versions it was checked against.

## Status

Early. Expect gaps and corrections.

The notes are the product. [tools/](tools/) has the small read-only Python scripts used to check them, as reference code with no support. For a working reader and writer, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

## What is covered

Start at [docs/README.md](docs/README.md).

- Container: zstd framing, writing a save back.
- Header: start year, date shown, map size, money, company experience counter, mods, preview image, settings.
- Calendar: the game clock, calendar speed and the day table.
- Lua value encoding, and the script states: town ratings, weather, company rank, loans, counters, subsidies, landmarks.
- Entity data: town records, warehouses, the statistics lists behind stocks and yearly charts, entity names, and searches that failed.
- The Finances tab against the money journal.
- Cargo type ids and how climates and economies pair.
- Map editor saves, and converting a regular save into one.
- Format versions seen in the wild.

## Evidence

Claims are checked against:

- Saves written on our own install (Linux, Steam).
- Public savegames on the game's mod.io catalog, cited by mod id and link (for example `6430076`). Only facts read from those saves are recorded here: format version, map size, start year, mod list, record counts, and similar. Their files, preview images and other content are not copied into this repo.

If you uploaded a save that is cited here and want it removed, please open an issue.

## Acknowledgements

The container, header and Lua state layout build on [TBK/tf3-save-editor](https://github.com/TBK/tf3-save-editor) and its `docs/FORMAT.md` (MIT OR Apache-2.0, © 2026 TBK). Code in `tools/` follows its readers; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Corrections found here are passed back to that project.

## License

Copyright (c) 2026 WuphonsReach. Licensed under either of

* Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
* MIT license ([LICENSE-MIT](LICENSE-MIT))

at your option.

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in this work, as defined in the Apache-2.0 license,
shall be dual licensed as above, without any additional terms or conditions.

Transport Fever 3 is a trademark of its respective owners.
