# Header

The header starts the decompressed stream. Fields in order. Checked in full on 599, 601 and 604. Format 568 and 585 match up to and including the preview image, then differ (see [versions.md](versions.md)).

The layout follows [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). The meanings marked "ours" were worked out here and are being passed upstream. Where a field's name or reading here differs from that file's, [tf3-save-editor.md](tf3-save-editor.md) lists it.

| Field | Type | Meaning |
|---|---|---|
| magic | 4 bytes | `tf**` |
| version | u32 | Format version, for example 604 |
| start year | u32 | Year the game was started, not the save date (ours). 1900 to 2020 seen, mostly whole decades, 1900 and 2020 most often. In three catalog saves it differs from the day table's first day, see [calendar.md](calendar.md#the-game-clock) |
| map width | u32 | Metres (ours). For example 20480 |
| map height | u32 | Metres (ours). For example 40960. The settings' `map.size` does not give the size, see [settings.md](settings.md#how-a-setting-is-stored) |
| date | u32 | The date shown in the game, as a Julian day number (ours). Equal to the day table's last day in the 120 catalog saves (568 to 604, **Observed**) and to the date on screen in three (**Confirmed** on 604). See [calendar.md](calendar.md#the-date-in-the-header) |
| money | i64 | Copy of the company balance, shown in the load dialog |
| counter | u32 | Copy of the company's `experience` (ours, **Observed** on 585 and 599 to 604). It can trail the state by a few points or by more, and grows with play. Details and numbers: [company.md](company.md#the-header-counter). In map editor saves it is the number of residents instead ([editor-towns.md](editor-towns.md#the-header-counter-is-the-number-of-residents)) |
| info | Lua table | Holds `company.level` (ours). 1 to 15 in 117 of 120 catalog saves (568 to 604); empty in the other 3 and in editor saves |
| mods | vec<mod> | Mods the save uses: per mod id, source, path, display name and extra (`str`), then flags (u32). See [mods.md](mods.md#the-mod-list-entry) |
| flag before the preview | u8 | 1 if achievements can be earned, 0 if not (**Confirmed**, [below](#the-two-flags)). It does not say whether a preview follows: 0 in 60 of 120 catalog saves, all with a full preview. Always equal to the u8 `flag` further down ([below](#the-two-flags)). [tf3-save-editor.md](tf3-save-editor.md#the-flag-before-the-preview) has the name it was given elsewhere |
| preview width, height | u32, u32 | 640 x 360 in every save checked (120 catalog saves, 568 to 604) |
| preview | str | Raw RGB8, width x height x 3 bytes, **bottom row first** (ours) |
| stats | i64 x 6 | Index 3 is another copy of the money (equal in all 120 catalog saves) |
| stats | i32 x 11, vec<(u32, u32)>, u32 x 2, i64 x 9, u32 x 2 | Mostly **open**. Three of the counts the load dialog shows are in here, see [below](#counts-the-load-dialog-shows) |
| labels | vec<(str, u32)> | Text such as `"%d Point(s) for Company Value"` with a number |
| stats | u32, i64 x 2, u32 | **Open** |
| config mods | vec<str> | The ids of the save's mods, the same set as the mod list above (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). See [mods.md](mods.md#the-mod-list-entry) |
| config resources | vec<(str, str)> | Keys `climate`, `economy`, `nameList`, each a path such as `::/economy/all.eco` |
| config params | vec<(str, Lua table)> | The entry with the empty key holds the game settings; every other entry is one mod's own options, keyed by its id. See [mods.md](mods.md#mod-options) |
| mission, kind | str, str | |
| flag | u8 | The same value as the flag before the preview: 1 if achievements can be earned, 0 if not ([below](#the-two-flags)). It is not the pause state at save time and not the start speed (**Observed**: seven saves of one 604 game, each written paused after a stretch at 4x, all read 1; the one new game that read 0 had seven mods). Calendar speed is not stored here |
| value | u32 | The format version the save was first written under, probably (ours, **Observed** on 585 to 604). Equal to the version in 604 saves; 596 to 601 in 601 saves; 585 in a 604 save that was a re-save of a 585 save. Never above the save's own version in the catalog saves and maps summarised in [versions.md](versions.md). One editor map (604) held 256 (**open**) |
| id | str | The **map seed**: the text of the Seed box in the New Game dialog (ours, **Confirmed** on 604). Details, the catalog's seeds and the game's log: [seed.md](seed.md) |

Lua tables are encoded as in [lua-values.md](lua-values.md).

## Preview

- Read the preview string whatever the flag before it says. In about half the saves checked the flag is 0 and a full 640 x 360 image is present. Treat it as a preview when its length is `width * height * 3`.
- Rows are stored bottom-up. Flipped, the image matches the `.jpg` next to the save better than as stored in all 113 catalog saves that have one (568 to 604): mean pixel difference 0.9 to 12.5 flipped, 3.9 to 71.9 as stored. Channel order is RGB (closer than red and blue swapped in all 113).
- To write a save back byte for byte, keep the original flag byte.
- A crash save has no preview (**Observed**, 604, one save). After an in-game assertion failure the game wrote `crash_<save name>_<date>.sav` in the save folder. Its preview size reads 0 x 0 with an empty preview string, so the header ends after a few KB instead of about 700 KB, and no `.jpg` was written beside it. The Load Game screen lists it as "Recovery Save" and draws a flat blue-violet square in place of the picture. Whether the label comes from the `crash_` prefix or from something in the file is **open**; the rest of the header reads as in any other 604 save. A save made from it in the game, after loading it and pausing two game days later, had the normal 640 x 360 preview and a `.jpg` beside it, so the empty preview is not carried over (**Observed**, 604).

### The two flags

The flag before the preview and the u8 `flag` after `mission, kind` always hold the same value. **Observed** on 599 to 604 in 182 saves: none differ. Neither says anything about the preview.

**Confirmed (604):** the value is the save's "achievements can be earned" state, 1 for earnable and 0 for not. The Load Game dialog's "Achievements cannot be earned." line is drawn from it, and the game's API names the field `GameMetadata.achievementsEarnable` (`api/tealdef/api/type.d.tl`; the dialog script is `gui/menu/savegame_react_util.tl` in `base/content/gui.zip`). What the script does: a save whose value is 0 is shown as unachievable at once; a save whose value is 1 is checked again against its mod list; a save whose value is 0 but whose list holds a force-enable mod is also checked again (not tested). Why the old tests found nothing: it follows which mods are in the list, not how many.

The first test, one save each way with only the two flag bytes changed (the header's byte before the preview and the `flag`, 604): a Tiny save with no mods and value 1 (no line) set to 0 showed the line; a Small save with seven mods and value 0 (line shown) set to 1 still showed it, which fits the second rule, since its list has mods that are not cosmetic.

**The game writes the value again at each save** (**Confirmed** on 604, once each way). Both test saves were loaded and saved without any other change. The Tiny save (value 0, no mods) was written with 0: an empty mod list did not bring it back to 1. The Small save (value 1, seven mods) was written with 0 in both places: the game took the 1 we set and cleared it. So a save is written with 1 when the mod list holds a force mod, or when the value it was loaded with was 1 and every mod is cosmetic (next paragraphs). That explains the saves that read 0 with no mods (below) and why no save with a non-cosmetic mod reads 1.

**A force mod keeps the value at 1** (**Confirmed** on 604, once): a Giant subarctic save with 14 mods, four of them not cosmetic (`urbangames_vehicles_no_end_year_1`, `ingo_boathouse_asset`, `advanced_track_patterns`, `stardorn_industry_upgrades`) and `bobdike_achievements_unbound` among them, read 1 and showed no line. Loaded and saved again, its mod list still the same 14, it was written with 1 and showed no line. The same game two saves later, after `urbangames_vehicles_no_end_year_1` and the two `ug_legacy_*` vehicle mods `ug_legacy_road_1850` and `ug_legacy_trams_1850` were switched off on the Mods tab, still read 1. Then `bobdike_achievements_unbound` was switched off as well (10 mods left, three of them not cosmetic: `ingo_boathouse_asset`, `advanced_track_patterns` and `stardorn_industry_upgrades`) and the save made from that load was written with 0 in both places, and its Load Game screen showed "Achievements cannot be earned." So the force mod is what held the 1, and the value drops at the first save after it goes. Put back, it restores the value: the save made after `bobdike_achievements_unbound` was switched on again (the 0 save above, 11 mods) was written with 1 in both places, and its Load Game screen showed no line (**Confirmed**, once). So a 0 stays 0 only while no force mod is in the list.

Each installed mod's `mod.json` can carry `cosmetic` (true in 25 of 320 mods installed on one machine; missing means false) and, rarely, `forceActivateAchievements` (one of the 320, `bobdike_achievements_unbound`; a second mod with a similar name, `unlocker_achivements`, is in 3 saves, all reading 1; its manifest was not seen). The rule that fits the saves: the value is 1 when a force mod is present, or when it was already 1 and every mod is cosmetic (an empty list counts as all cosmetic); a 0 does not come back without a force mod.

- Of 253 saves (catalog and ours, 599 to 604) whose mods all had a manifest here, 135 had a mod that is not cosmetic and no force mod, and all 135 read 0. 104 read 1 with the rule predicting 1. No save with `bobdike_achievements_unbound` read 0 (53 read 1).
- 14 read 0 although the rule says 1. Ten have no mods: catalog save 6417707 (`333`) has an empty mod list and 0, and our eight re-saves of it keep 0; an `Emerald Shores` re-save does too. So the value stays 0 after the mods that set it are gone, as the re-save test above reproduced (the way it first became 0 in 333 was not found). Four catalog saves with no mods or only the two Urban Games packs read 0 the same way.
- Map editor saves (`isMapEditor` true) follow the same rule (**Observed**, 604, 99 editor saves of one machine's `save_maps` folder, header only). The two that read 0 have two mods, `urbangames_deluxe_upgrade_pack` and `urbangames_vehicles_no_end_year_1`, and no force mod. The 49 saves with `bobdike_achievements_unbound` (3, 11, 12 or 14 mods) all read 1. The 48 with no mods (33) or only `urbangames_deluxe_upgrade_pack` (15) read 1, among them the saves of one editor map made after every other mod was switched off on load (a force mod had held the 1 before). Whether that pack's manifest is cosmetic was not read: if it is, those 1s fit "already 1 and every mod cosmetic"; if not, an editor save may start at 1 and keep it.
- The dialog in seven screenshots (Small 1 : 3 with seven mods, Medium 1 : 3 with nine, both 0 and with the line; a Tiny map, a Gigantomaniac map and the tutorial save, all 1 and without it) agreed.

**Open:** what else sets it to 0 besides a non-cosmetic mod (a cheat such as a hand-edited balance, for one). Whether a cosmetic mod's name is checked against the installed copy or the saved list at save time was not tested. The tools keep the key `flag_before_preview`, a name from before the meaning was known.

## Settings

The params entry with the empty key is a flat Lua table: one layer, with the dotted names stored as the keys (**Observed** on 599 to 604, 22 catalog saves and ours). Keys include `isMapEditor`, `map.size`, `advancedOptions.*` and `townConfig.*`.

- `isMapEditor` is `true` in map editor saves. See [editor-saves.md](editor-saves.md).
- How a value is stored (its place in the option list), the option lists, the difficulty presets and how a load rewrites them are in [settings.md](settings.md).

## Counts the load dialog shows

**Observed** on 604, one game (the [Small subarctic game](test-games.md#small-subarctic-game); five saves, three of them one purchase apart). The Load Game screen showed 22 stations, 11 lines and 88 vehicles for one of them. Positions are in the order the fields are read, counting from 0:

| Field | Value in that save | What it tracks |
|---|---|---|
| `i32` index 2 of the 11-`i32` run | 69 | Road vehicles |
| `i32` index 4 | 19 | Ships. 69 + 19 is the 88 the screen shows |
| `i32` index 5 | 22 | Stations |
| first `u32` of the two `u32` after the nine `i64` | 11 | Lines |

The game total on screen is the sum of the first two rows, not one stored number.

**Buying vehicles shows in the header at once, with the game paused** (**Observed**, same game). Five road vehicles were bought and the game was saved paused before any simulation time passed. Against the save made just before, the road vehicle count went from 69 to 74, the first of the six leading `i64` rose by the purchase price (285,690, as in the buy button), the sixth fell by the same amount, and the header money fell by it too. So the header counts a new vehicle before the player has seen it reach a stop of its line. In the next save, made after about a second of game time at 1x, the first `i64` was 75 lower and the rest were unchanged (the lowering looks like wear on the vehicle value, **open**). Selling seven vehicles of one line and deleting a line in the save before took the road vehicle count from 76 to 69 and the line count from 12 to 11.

**A swap in one paused session** (**Observed**, same game, saves `1958` and `1959` at the same clock): seven old horse carts (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`) sold and seven trucks bought. The road vehicle count stayed 83. The first of the six leading `i64` rose by the net spend (1,600,728 to 3,850,045, +2,249,317), the sixth fell by the same (2,446,422 to 197,105) and the header money fell by it. The net is the purchases less the sales ([finances.md](finances.md#selling-a-vehicle-is-a-positive-booking-in-the-purchase-category-604)). One small number changed by one, the last of the four numbers `save_header.py` prints as `stats3` (11 to 12); nothing else in the header did; what it counts is **Open**.

## Money in the header

**Observed** on 604: in six saves of one game the header money equalled the Account figure in the game exactly, so the lag below does not always show. In one of them the account was -2,598,471, so a negative header value can be the true balance.

**Observed** on 604: a catalog save of a played game (6428935, account 3,382,382,812 in the game) was loaded, paused at once, saved again and reloaded. The re-save's header money, the Account figure and the Finances tab's current Bank Account were all 3,382,382,812, and the header counter was unchanged at 15,808. The stream also holds a long run of balance samples, see [finances.md](finances.md#the-balance-history-run).

**Observed**: in one played save the header said 8,932,346 when the game showed 8,920,255, so it tracks the balance but can lag. In catalog save [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) the header holds 0 while the game shows -18,153,221. Why is **open**: negative values are stored too.

**Observed** on 604, one game (the [Tiny temperate game](test-games.md#tiny-temperate-games), with nothing built and no loan taken): the header money was 0 in saves on 1 January 1900, 20 September 1900 and 2 January 1901, and the game's Account read 0 with Earnings $0 on 2 January 1901. That game had no starting capital, and with nothing built the balance did not move over a year. Which setting gives a start with no capital is **Open**.

**Observed** on the 120 catalog saves (568 to 604): the header money is 0 in 53 and negative in 13. Several negatives are round numbers (-25,000,000 in four saves, -100,000,000, -24,000,000), so the header may not always hold the balance. The real balance is in the money journal ([finances.md](finances.md#finding-the-journal)).
