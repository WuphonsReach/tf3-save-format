# Format versions

The u32 after the `tf**` magic. The game reads older versions. When it re-saves one it writes the current version: a 585 save came back as 604 (**Observed**, one save; the header's `value` field kept 585, see [header.md](header.md)).

## Seen in the mod.io catalog (2026-10-08)

120 public savegames from the Transport Fever 3 catalog on mod.io, read with [tools/save_header.py](../tools/save_header.py):

| Version | Saves | Header |
|---|---|---|
| 604 | 79 | Reads in full |
| 601 | 27 | Reads in full, same layout as 604 |
| 599 | 4 | Reads in full, same layout as 604 |
| 585 | 3 | Same up to the preview, then differs |
| 568 | 7 | Same up to the preview, then differs (fails in the stats block) |

The difference after the preview in 568 and 585 is **open**. After the header, the script states, the calendar speed field and the day table were read on all five versions (see [script-states.md](script-states.md) and [calendar.md](calendar.md)). The money journal and the rest of the entity data were checked on 604 only, apart from the town record counts in [cargo-ids.md](cargo-ids.md).

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

## Platform in the save (2026-10-10)

There is no field that names the platform a save was made on (**Observed**, 568 to 604). The 244 entries above were matched with the uploader's platform from the same mod.io upload records, and searched in full for platform names:

- **Header.** No field reads differently by platform. Checked: the preview flag, the u8 flag before `value`, the open stats fields, the mod list's `source` (`DLC`, `mod.io`, `BuiltInMods` on every platform) and `flags`, and the settings keys and values. Two comparisons were made: console against PC at 601 (39 against 2), and Windows, Mac, Linux and the Epic/GOG build at 604. A value that turned up off Windows only did so in one or two saves.
- **Whole stream.** Searched for the names of the consoles, operating systems and stores, and for the path prefixes of each system. The short ones (`PS5`, `GDK`, `EGS`, `GOG`, `C:\`) occur in nearly every save on every platform, so they are chance byte matches. `steam` and `platform` are game words. The longer hits are names from the name lists, or part of a mod's name.

Two ways a save can still give its platform away:

- **A stored Lua error.** A script error from a mod is kept with its chunk name, which is the mod's full install path. Two catalog saves hold one, both from mod 6422630. In [6429325](https://mod.io/g/transportfever3/m/my-rail-network) (Windows, 604) the path is under the Windows user folder and contains the uploader's account name. In [6431316](https://mod.io/g/transportfever3/m/1990-2) (Xbox, 601) it starts `R:/mod.io/10640/`. Find these by searching for `[string "`. **Observed**, two saves.
- **Mods from outside mod.io.** Mods whose URL points to modwerkstatt.com appear only in PC saves (7 saves, all 604). Consoles probably load mods from mod.io only, so such a mod suggests a PC save (**Open**). A save without one says nothing.

Since console and PC saves also differ in format version (601 against 604), the only same-version comparison so far has two PC saves. A platform code hidden in a field not yet described is not ruled out (**Open**).
