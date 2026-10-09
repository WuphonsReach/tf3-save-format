# Header

The header starts the decompressed stream. Fields in order. Checked in full on 599, 601 and 604. Format 568 and 585 match up to and including the preview image, then differ (see [versions.md](versions.md)).

The layout follows [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). The meanings marked "ours" were worked out here and are being passed upstream.

| Field | Type | Meaning |
|---|---|---|
| magic | 4 bytes | `tf**` |
| version | u32 | Format version, for example 604 |
| start year | u32 | Year the game was started, not the save date (ours). 1900, 1920, 1930, 1960, 1970, 1990, 2000, 2020 seen |
| map width | u32 | Metres (ours). For example 20480 |
| map height | u32 | Metres (ours). For example 40960 |
| ? | u32 | 2,415,021 to 2,835,101 in the 120 catalog saves (568 to 604). The same in three saves of one map, so it describes the map, not the play state. **Open** |
| money | i64 | Copy of the company balance, shown in the load dialog |
| counter | u32 | Copy of the company's `experience` (ours, **Observed** on 585 and 599 to 604). The first `experience` number in the company progression script state (the one next to `companyState`, `level` and `potentialLevel`) matched the header in 16 of 19 saves and ran 1 to 4 points ahead in the other 3, so the header is probably written just before the state. It grows with play (8563 in the first save of a game started on 1 Jan 1900, rising to 16513 over later saves of that game whose autosaves were all named `_1900-01-01`). 0 to 59,478 in the 120 catalog saves (568 to 604), 0 in one. FORMAT.md calls it `year` |
| info | Lua table | Holds `company.level` (ours). 1 to 15 in 117 of 120 catalog saves (568 to 604); empty in the other 3 and in editor saves |
| mods | vec<mod> | Mods the save uses, see below |
| preview flag | u8 | 0 or 1. Does not say whether a preview is present (ours): 0 in 60 of 120 catalog saves, all with a full preview. Meaning **open** |
| preview width, height | u32, u32 | 640 x 360 in every save checked (120 catalog saves, 568 to 604) |
| preview | str | Raw RGB8, width x height x 3 bytes, **bottom row first** (ours) |
| stats | i64 x 6 | Index 3 is another copy of the money (equal in all 120 catalog saves) |
| stats | i32 x 11, vec<(u32, u32)>, u32 x 2, i64 x 9, u32 x 2 | **Open** |
| labels | vec<(str, u32)> | Text such as `"%d Point(s) for Company Value"` with a number |
| stats | u32, i64 x 2, u32 | **Open** |
| config mods | vec<str> | |
| config resources | vec<(str, str)> | Keys `climate`, `economy`, `nameList`, each a path such as `::/economy/all.eco` |
| config params | vec<(str, Lua table)> | The entry with the empty key holds the game settings, see below |
| mission, kind | str, str | |
| flag | u8 | 1 in two saves started at normal speed, 0 in one started paused. Not the pause state at save time: seven saves of one 604 game, each written with the game paused after a stretch at 4x (the last four after changing the calendar speed and the cycle modes), all read 1 (**Observed**). 0 and 1 are about equally common in the catalog. Calendar speed is not stored here. Meaning **open** |
| value | u32 | The format version the save was first written under, probably (ours, **Observed** on 585 to 604). Equal to the version in 604 saves; 596 to 601 in 601 saves; 585 in a 604 save that was a re-save of a 585 save. Never above the save's own version in 15 saves checked. One editor map (604) held 256 (**open**) |
| id | str | |

Lua tables are encoded as in [lua-values.md](lua-values.md).

## Mod entries

Each mod is five `str` and a u32: id, source, path, display name, extra, flags. Observed on the 120 catalog saves (568 to 604):

- `extra` holds the mod's mod.io page URL in 2,661 of 3,019 entries. It is empty in the rest: every `DLC` entry and most `BuiltInMods` entries.
- `flags` is 0, 1 or 2. Always 1 for source `DLC`, mostly 0 for `BuiltInMods`, any of the three for `mod.io`. Meaning **open**.

## Preview

- Read the preview string whatever the flag byte says. In about half the saves checked the flag is 0 and a full 640 x 360 image is present. Treat it as a preview when its length is `width * height * 3`.
- Rows are stored bottom-up. Flipped, the image matches the `.jpg` next to the save better than as stored in all 113 catalog saves that have one (568 to 604): mean pixel difference 0.9 to 12.5 flipped, 3.9 to 71.9 as stored. Channel order is RGB (closer than red and blue swapped in all 113).
- To write a save back byte for byte, keep the original flag byte.

## Settings

The params entry with the empty key is a nested Lua table. Flattened with dots, keys include `isMapEditor`, `map.size`, `advancedOptions.*` and `townConfig.*`.

- `isMapEditor` is `true` in map editor saves. See [editor-saves.md](editor-saves.md).
- **A setting is stored as its position in the option list plus 1** (**Confirmed** on 604, two games). The New Game settings screen is built from the game's `base/mod.json` in the install directory, where each option has a `key` (the settings key above), a `values` list in screen order and a `defaultIndex` counted from 0. A saved 3 is the third entry. Checked on a game made on the Easy preset (catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1)): the screen showed industry productivity 150%, industry closing Never, vehicle maintenance effect Low, subsidies Often, subsidy risk None, landmark resources Low, inflation Low, every town sensitivity Low, vehicle costs 50%, and the save held `locations.industry.industryProductivity` 4 (list 50, 75, 100, 150, 200%), `economy.industryDevelopment.closureProbability` 1, `advancedOptions.vehicleMaintenanceEffectScale` 2, `subventionMode` 4, `subventionRisk` 1, `landmarkResources` 2, `inflationFactor` 2, `townConfig.sensitivity*` 3 (list Off, Very Low, Low, ...) and `vehiclePurchaseCostScale` 1. A game left on the defaults (catalog save [6417707](https://mod.io/g/transportfever3/m/333151)) held 3 for the options whose default is entry 3 and 4 for the sensitivities, which default to Normal, the fourth of seven. The Hard preset changes the same group of options at once (productivity 75%, closing Sometimes, inflation High, vehicle costs 125%, and so on), so the preset itself is not stored, only its results. The percentage options (`vehiclePurchaseCostScale`, `infrastructurePurchaseCostScale`, `infrastructureMaintenanceScale`, `vehicleMaintenanceScale`, `passengerIncome`, `cargoIncome`) list 50, 75, 100, 125 and 150%, so 1 is 50% and 3 is 100%. Which of these the game applies to which amount is not stored with them.
- `map.size` does not give one size. A value of 3 was 11264 x 11264, 6656 x 19968 and 8192 x 16384 in different saves. Use the header's width and height for the real size.

## Money in the header

**Observed** on 604: in six saves of one game the header money equalled the Account figure in the game exactly, so the lag below does not always show. A third save of that game, with the account at -2,598,471, also matched, so a negative header value can be the true balance.

**Observed** on 604: a catalog save of a played game (6428935, account 3,382,382,812 in the game) was loaded, paused at once, saved again and reloaded. The re-save's header money, the Account figure and the Finances tab's current Bank Account were all 3,382,382,812, and the header counter was unchanged at 15,808. In the stream, far in front of the Lua states, there is a long run of i64 values that each sit within a few percent of the one before and read as a balance history. Three of them, 12 entries apart, equalled the Bank Account row for the last three finished periods on the Finances tab (3,302,688,957, 3,330,544,108, 3,363,416,724). The tab shows six-month periods, so that is about two entries a month. The last entry of the run was 3,382,379,554, which is the header money of the original save and not the re-save's, so the history is sampled and the live balance is not appended to it. It is not the money journal that FORMAT.md describes: that is a separate run of 21-byte bookings, see [finances.md](finances.md). Find it by searching for one of the period-end figures as 8 little-endian bytes. **Observed**, one save.

**Observed**: in one played save the header said 8,932,346 when the game showed 8,920,255, so it tracks the balance but can lag. In catalog save [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) the header holds 0 while the game shows -18,153,221. Why is **open**: negative values are stored too.

**Observed** on the 120 catalog saves (568 to 604): the header money is 0 in 53 and negative in 13. Several negatives are round numbers (-25,000,000 in four saves, -100,000,000, -24,000,000), so the header may not always hold the balance. The real balance is in the money journal (see FORMAT.md).
