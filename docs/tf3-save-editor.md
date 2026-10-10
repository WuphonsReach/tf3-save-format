# Where these notes differ from tf3-save-editor

These notes build on [tf3-save-editor](https://github.com/TBK/tf3-save-editor), its `docs/FORMAT.md` and its reader in `crates/lib/src/header.rs` (MIT OR Apache-2.0, see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)). The container, the header layout, the Lua values and the money journal are read the same way in both and are not repeated here. This file lists the places where a name or a reading differs, what we saw, and why we changed it, so that someone moving between the two can tell which one to trust for that field.

Our tools use the names these notes establish, and follow upstream's names only where the meaning is still open or the name is not misleading. The names `tools/save_header.py` changed on 2026-10-10 are listed in the sections below.

The upstream side was read at its release 0.2.0 (main branch, 2026-10-10). It may have moved since. Upstream's reader was read as code and not run on these saves, so what it does with them is **Observed** from the source only. The saves checked are the ones named in each section.

## Names and readings that differ

| Field | Upstream | Here | Details |
|---|---|---|---|
| Byte before the preview size | `has preview`, read as "a preview follows" | Meaning **open**; it does not say whether a preview follows | [below](#the-flag-before-the-preview) |
| Preview row order | top-down | bottom row first | [below](#the-preview-image) |
| The four `u32` after the version | unknown | start year, map width, map height, date | [below](#the-four-u32-after-the-version) |
| Header `year` (a `u32` after the money) | the in-game year | a copy of the company's experience | [below](#the-year-field) |
| `info` table | usually empty | holds `company.level` in most saves | [below](#the-info-table) |

## The flag before the preview

Upstream's table names the `u8` before the preview's width and height `has preview`, and its reader drops the image when the byte is 0. It also reports an error if the byte is 0 and the width or height is not.

What the saves show (**Observed**, 599 to 604): the byte is 0 in 60 of 120 catalog saves and in 18 of 72 of ours, and a full 640 x 360 image follows in every one of them. It also always equals the `u8` `flag` after `mission, kind`. Neither says anything about the preview, and what the value records is **open**. The evidence is in [header.md](header.md#the-two-flags).

So the name was a guess that the saves do not support, and it is not used here. These notes call the field "the flag before the preview", which says only where it is. The same goes for `tools/save_header.py`, whose key was `has_preview` and is now `flag_before_preview` (a field with an unknown meaning gets a name that says only where it is). By the source, upstream's reader would not show the preview of the saves whose byte is 0, and it would fail on them with a size error. I did not run it on one, so that is a reading of the code and not a test.

## The preview image

Upstream says the rows are top-down. In all 113 catalog saves that have a `.jpg` beside them, the image matches the `.jpg` better with the rows flipped (mean pixel difference 0.9 to 12.5 flipped against 3.9 to 71.9 as stored), so the first row stored is the bottom one (**Observed**, 568 to 604). The numbers and the channel order are in [header.md](header.md#preview).

## The four u32 after the version

Upstream lists them as unknown. Here they are the start year, the map width in metres, the map height in metres and the date as a Julian day number. The first three are **Observed** in the catalog saves and the date is **Confirmed** on 604 in three saves ([header.md](header.md), [calendar.md](calendar.md#the-date-in-the-header)). `tools/save_header.py` calls the fourth one `game_date` in its output and dict key (the date shown in the game when the save was made, not the real-world date and not the start date, which is `start_year`); it was `unknown` until 2026-10-10.

## The year field

The `u32` after the money is documented upstream as the in-game year. In these notes it is a copy of the company's `experience`, which grows with play and trails the state by a few points or more (**Observed** on 585 and 599 to 604; [company.md](company.md#the-header-counter)). It is not a year. The field is called `counter` in `tools/save_header.py`, which is neutral.

## The info table

Upstream says the table is usually empty. In 117 of 120 catalog saves (568 to 604) it holds `company.level`, a number from 1 to 15. It is empty in the other 3 and in editor saves.

## Fields upstream leaves unexplained

These are not disagreements. Upstream gives no meaning and these notes do:

- The `str` at the very end of the header is the map seed: the text of the New Game dialog's Seed box (**Confirmed** on 604, [seed.md](seed.md)). It is `map_seed` in `tools/save_header.py` (upstream's `id`).
- The `u32` `value` after the `u8` `flag` is probably the format version the save was first written under (**Observed** on 585 to 604, [header.md](header.md)). It is `first_version` in `tools/save_header.py`, as in the save summaries.
- The game settings in the params entry with the empty key, their option lists and defaults, and how the Load Game screen rewrites them ([settings.md](settings.md)).
