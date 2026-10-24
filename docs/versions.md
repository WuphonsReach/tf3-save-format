# Format versions

The u32 after the `tf**` magic. The game reads older versions. When it re-saves one it writes the current version: a 585 save came back as 604 (**Observed**, one save; the header's `value` field kept 585, see [header.md](header.md)).

## In short

- **604 is the PC release format and 601 the console format (Observed).** 568 to 599 are pre-release builds. A re-saved older save comes back as the current version (604, now 605), keeping the old number in the header's `value` field.
- **605 is a newer PC format, first seen on 23 October 2026 (Observed).** In our own saves, a 604 save and the first 605 save sit 28 minutes apart, between the 22 October build 40423 release and the 24 October build 40425. The header reads the same way on 605. A load and re-save of one 604 save on build 40425 also came back 605, and, with no game tick between, its stream differs from the 604 source no more than a re-save of one state varies (about 2% of aligned bytes, **Observed**, coarse); a change in how one record kind is written is **Open**. No catalog save is 605 yet. Details under [Game releases and builds](#game-releases-and-builds-2026-10-24).
- **568 and 585 headers differ after the preview** (Open); everything after the header was read on all five versions except the money journal and entity data (604 only).
- **No field names the platform** ([platform.md](platform.md)).
- The sections below are dated counts of the catalog; they are exempt from the Confirmed / Observed / Open labels.

## Seen in the mod.io catalog (2026-10-08)

120 public savegames from the Transport Fever 3 catalog on mod.io, read with [tools/save_header.py](../tools/save_header.py):

| Version | Saves | Header |
|---|---|---|
| 604 | 79 | Reads in full |
| 601 | 27 | Reads in full, same layout as 604 |
| 599 | 4 | Reads in full, same layout as 604 |
| 585 | 3 | Same up to the preview, then differs |
| 568 | 7 | Same up to the preview, then differs (fails in the stats block) |

The difference after the preview in 568 and 585 is **open**. After the header, the script states, the calendar speed field and the day table were read on all five versions (see [script-states.md](script-states.md), [company.md](company.md) and [calendar.md](calendar.md)). The money journal and the rest of the entity data were checked on 604 only, apart from the town record counts in [cargo-ids.md](cargo-ids.md).

## Calendar speed in the catalog (2026-10-09)

The 120 saves above, read with [tools/calendar_speed.py](../tools/calendar_speed.py) (field described in [calendar.md](calendar.md#the-calendar-speed-field)). The field was found exactly once in each, on every version.

| `millisPerDay` | Meaning | Saves |
|---|---|---|
| 4000 | 1.00x | 70 |
| 16000 | 0.25x (by the rule, not read in the game) | 22 |
| 0 | Paused | 11 |
| 1000 | 4.00x | 10 |
| 8000 | 0.50x | 6 |
| 1,440,000 | no slider step | 1 |

`playSpeed` in the same saves: 0 in 49 (written paused), 1 in 35, 2 in 3, 3 in 3, 4 in 29, 8 in 1.

The day table that follows the field ([calendar.md](calendar.md#the-day-table)) parsed in all 120. 88 had consecutive day numbers and rising ticks; 32 had jumps or repeats. 50 were exactly 4000 ticks per day throughout. Start years: 1900 in 64, 2020 in 20, the rest 1910 to 2010 (two saves start on a day other than 1 January). The header's date field equalled the table's last day in all 120.

## Summarised catalog (2026-10-09)

Every savegame and editor map in the catalog's mod directories, summarised with [tools/mine_saves.py](../tools/mine_saves.py): 244 entries, 180 savegames and 64 editor maps. The catalog had grown since the 120 saves above, which are all among them. Notes that say "the 120 catalog saves" mean the tables above; [cargo-ids.md](cargo-ids.md) counts the 244.

| Version | Savegames | Editor maps |
|---|---|---|
| 604 | 130 | 59 |
| 601 | 36 | 5 |
| 599 | 4 | 0 |
| 585 | 3 | 0 |
| 568 | 7 | 0 |

## Climates and economies in the catalog (2026-10-09)

The 244 entries of the summarised catalog, by the `climate` and `economy` resources in the header ([climates-economies.md](climates-economies.md)):

| Climate | Economy | Saves and maps |
|---|---|---|
| `temperate.clima` | `temperate.eco` | 151 |
| `temperate.clima` | `all.eco` | 16 |
| `subarctic.clima` | `subarctic.eco` | 36 |
| `subarctic.clima` | `all.eco` | 3 |
| `tropical.clima` | `tropic.eco` | 21 |
| `tropical.clima` | `all.eco` | 2 |
| `dry.clima` | `dry.eco` | 4 |
| `mission6_tropical.clima` | `tropic.eco` | 1 |
| none (568 and 585 headers, which parse only partly) | none | 10 |

## Versions and releases (2026-10-10)

The 244 entries above, joined with the upload record that mod.io keeps for each mod in its local cache (`metadata/state.json`: the modfile's upload date and its `metadata_blob`). The blob always names `uploadedFromPlatform`. From launch it also carries `buildVersion`, which is the game version number that Urban Games' [PC release notes](https://wiki.transportfever3.com/doku.php?id=releasenotes) use: 40408 (Steam) and 40393 (Epic and GOG) for the initial release on 29 September 2026, and 40420 for the stability update on 8 October 2026.

| Format | Uploaded (UTC) | Uploaded from | Game build in the blob |
|---|---|---|---|
| 568 | 2026-05-27 to 06-02 | Windows 1, PS5 2, Xbox 4 | none |
| 585 | 2026-07-03 to 07-09 | PS5 3 | none |
| 599 | 2026-09-04 to 09-16 | Linux 1, Xbox 3 | none |
| 601 | 2026-09-16 to 10-10 | PS5 22, Xbox 17, Windows 1, Linux 1 | none |
| 604 | from 2026-09-29 | Windows 173, Mac 10, Linux 6 | 40408 in 162, 40393 in 1, 40420 in 26 |

An upload date is the latest date a save could have been made, not the date it was made.

- **604 is the PC release format** (**Observed**). Every upload that carries a build is 604, and it is 604 on the release builds 40408 and 40393 as well as on 40420. The stability update did not change the format: ten of our own saves made on 40408, before the update installed, are 604, the same as the ones made after it.
- **601 is the console format** (**Observed**). 39 of the 41 entries at 601 came from a PS5 or an Xbox. Console uploads are still 601 after the 8 October update (for example [6436540](https://mod.io/g/transportfever3/m/gehr), uploaded on 9 October), and no console upload is 604. The release notes say the update is not yet out on consoles. Both PC uploads at 601 were made before launch.
- **568 to 599 are pre-release** (**Observed**). Every upload at these versions was made before 29 September. Their dates match the closed beta rounds that Urban Games announced in April 2026, including a console round. Uploads from before launch carry no build number, so these formats cannot be tied to game builds.
- **There are older numbers in the header's `value` field** (see [header.md](header.md)). Some 604 saves hold 543, 555 or 596 there, which suggests their games were started under those versions, so the pre-release numbers seen run at least 543, 555, 568, 585, 596, 599 and 601. No save at 543, 555 or 596 is in the catalog.
- **Builds before release** (**Open**). Mods other than saves carry builds 40358 (uploaded 15 September) and 40380 (22 September), before launch, possibly from early access. Builds 40419 (2 uploads) and 40420 appear from 6 October, two days before the update was released, possibly from a test branch.
- **The game's own build line on Linux** (**Observed**, 2026-10-11). The Linux client's main screen shows "Build 40420 Linux 64-bit", the same number as the stability update's `buildVersion` above, so Linux runs the same build number as the PC uploads. The header does not store it: a save made on that install reads 604, as before the update.

## Game releases and builds (2026-10-24)

PC releases as Urban Games' [release notes](https://wiki.transportfever3.com/doku.php?id=releasenotes) list them (read 2026-10-24):

| Build | Date | What the notes say |
|---|---|---|
| 40408 (Steam), 40393 (Epic, GOG) | 29 September 2026 | Initial release |
| 40420 | Steam 8 October, Epic and GOG 15 October | Rendering and video memory, modding tool and API updates, crash and bug fixes |
| 40423 | 22 October | Performance and graphics memory, modding validation, many crash and bug fixes; save fixes (a crash loading a save after a vehicle's capacity was cut, corrupt saves when the disk filled up, a crash on corrupt saves) |
| 40425 (Steam) | 24 October | A crash on RTX 50 cards with one NVIDIA driver version |

The notes name no save format change for any of them. Our saves say otherwise for 40423 or later:

- **The format went from 604 to 605 between two saves of one game** (**Observed**, 604 and 605). Of the user's saves made since 19 October, every one up to 23 October 02:37 (local time) reads 604, and every one from 23 October 03:05 on reads 605. The first 605 save has a game date between the 604 save at 02:01 and the one at 02:37, so it was played on from the 02:01 save: a manual before and after pair across the change, but with about eight game weeks of play in between.
- **The header parses unchanged** (**Observed**, 605). `save_header.py` reads a 605 header with the same layout, and the preview, mod list and resources look the same. The stream after the header is not compared, so a 605 change inside it is **Open**.
- **A load and re-save on 40425 writes 605, and its stream differs from 604's no more than two re-saves of one state differ from each other** (**Observed**, 604 to 605, one game, coarse). A 604 save of a Large 1 : 1 subarctic game (game date 2000-04-17, one mod) was loaded on 40425 and saved under a new name. A first try ran one game day before the save; the second, from the same 604 save, kept the game clock, date, money and counter unchanged. Header: 604 became 605 and the mod list lost its one entry (the Load Game screen rewrites mods, 154 bytes); no other header field moved. The streams are 928 million bytes each. Aligned by 48-byte anchors, the 605 stream has the same shift points as a second 604 re-save of the same state, at a constant offset from the dropped mod entry, and 2.44% of aligned bytes differ against 2.44% for that 604 control. Re-saving that 605 save once more, with nothing changed and no tick, gives a stream 82 KB longer with 2.8% of aligned bytes different, most of the length change around 57 to 59 million bytes in. So re-saves of one state already vary at the percent level on both versions, and nothing here separates 605 from 604. A change in how one record kind is written, or one that moves few bytes, would need a record-level comparison (**Open**).
- **Build 40425 is on the main screen on 24 October** (**Observed**, Linux): "Build 40425 Linux 64-bit", read from a zoomed screenshot taken as Steam finished the update. Until 18 October the same line read 40420. The re-save above is the first save read from 40425, and it is 605.
- **Which build brought 605 is Open.** The dates fit 40423, but no screenshot or save names the build in use on 23 October.

## Platform in the save (2026-10-10)

There is no field that names the platform a save was made on (**Observed**, 568 to 604). The checks are in [platform.md](platform.md).
