# tf3-save-format

Notes on the Transport Fever 3 `.sav` file format. Unofficial, and not affiliated with or endorsed by Urban Games.

Everything here was worked out by reading save files written by the game. Nothing comes from the game's code or from Urban Games. The game changes the format between releases, so each note says which format versions it was checked against.

## Status

Early. Expect gaps and corrections.

The notes are the product. [tools/](tools/) has the small read-only Python scripts used to check them, as reference code with no support. For a working reader and writer, see [tf3-save-editor](https://github.com/TBK/tf3-save-editor).

## What is covered

Start at [docs/README.md](docs/README.md).

- Container: zstd framing, writing a save back.
- Header: start year, map size, money, play-time counter, mods, preview image, settings.
- Lua value encoding and the town rating state.
- Town records: capacities and starting cargo.
- Cargo type ids for the temperate economy.
- Map editor saves, and converting a regular save into one.
- Format versions seen in the wild.

## Evidence

Claims are checked against:

- Saves written on our own install (Linux, Steam).
- Public savegames on the game's mod.io catalog, cited by mod id and link (for example `6430076`). Only facts read from those saves are recorded here: format version, map size, start year, mod list, record counts, and similar. Their files, preview images and other content are not copied into this repo.

If you uploaded a save that is cited here and want it removed, open an issue.

## Acknowledgements

The container, header and Lua state layout build on [TBK/tf3-save-editor](https://github.com/TBK/tf3-save-editor) and its `docs/FORMAT.md` (MIT OR Apache-2.0, © 2026 TBK). The header reader in `tools/` follows its read order; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Corrections found here are passed back to that project.

## License

MIT, see [LICENSE](LICENSE).

Transport Fever 3 is a trademark of its respective owners.
