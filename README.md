# tf3-save-format

Notes on the Transport Fever 3 `.sav` file format. Unofficial, and not affiliated with or endorsed by Urban Games.

Everything here was worked out by reading save files written by the game. Nothing comes from the game's code or from Urban Games. The game changes the format between releases, so each note says which format versions it was checked against.

## Status

Early. Expect gaps and corrections.

This repo is documentation only. It does not ship a parser or editor, and it does not offer support for one. For a working reader and writer, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

## What is covered

Planned, filled in as the notes are written up:

- Container: zstd framing and the trailing empty frame.
- Header: version, money, play-time counter, mod list, preview image, settings.
- Lua script states.
- Town records: layout, starting cargo demand, capacities.
- Cargo type ids for the temperate economy.
- Differences between map editor saves and regular saves.
- Format versions seen in the wild and how they differ.

## Evidence

Claims are checked against:

- Saves written on our own install (Linux, Steam).
- Public savegames on the game's mod.io catalog, cited by mod id and link (for example `6430076`). Only facts read from those saves are recorded here: format version, map size, start year, mod list, record counts, and similar. Their files, preview images and other content are not copied into this repo.

If you uploaded a save that is cited here and want it removed, open an issue.

## Acknowledgements

The container, header and Lua state layout build on [TBK/tf3-save-editor](https://github.com/TBK/tf3-save-editor) and its `docs/FORMAT.md` (MIT OR Apache-2.0, © 2026 TBK). Corrections found here are passed back to that project.

## License

MIT, see [LICENSE](LICENSE).

Transport Fever 3 is a trademark of its respective owners.
