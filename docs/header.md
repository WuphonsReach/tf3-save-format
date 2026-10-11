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
| counter | u32 | Copy of the company's `experience` (ours, **Observed** on 585 and 599 to 604). It can trail the state by a few points or by more, and grows with play. Details and numbers: [company.md](company.md#the-header-counter) |
| info | Lua table | Holds `company.level` (ours). 1 to 15 in 117 of 120 catalog saves (568 to 604); empty in the other 3 and in editor saves |
| mods | vec<mod> | Mods the save uses: per mod id, source, path, display name and extra (`str`), then flags (u32). See [mods.md](mods.md#the-mod-list-entry) |
| flag before the preview | u8 | 0 or 1, meaning **open**. It does not say whether a preview follows: 0 in 60 of 120 catalog saves, all with a full preview. Always equal to the u8 `flag` further down ([below](#the-two-flags)). [tf3-save-editor.md](tf3-save-editor.md#the-flag-before-the-preview) has the name it was given elsewhere |
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
| flag | u8 | 1 in two saves started at normal speed, 0 in one started paused. Not the pause state at save time: seven saves of one 604 game, each written with the game paused after a stretch at 4x (the last four after changing the calendar speed and the cycle modes), all read 1 (**Observed**). 0 and 1 are about equally common in the catalog. Calendar speed is not stored here. Always equal to the flag before the preview ([below](#the-two-flags)). Meaning **open** |
| value | u32 | The format version the save was first written under, probably (ours, **Observed** on 585 to 604). Equal to the version in 604 saves; 596 to 601 in 601 saves; 585 in a 604 save that was a re-save of a 585 save. Never above the save's own version in the catalog saves and maps summarised in [versions.md](versions.md). One editor map (604) held 256 (**open**) |
| id | str | The **map seed**: the text of the Seed box in the New Game dialog (ours, **Confirmed** on 604). Details, the catalog's seeds and the game's log: [seed.md](seed.md) |

Lua tables are encoded as in [lua-values.md](lua-values.md).

## Preview

- Read the preview string whatever the flag before it says. In about half the saves checked the flag is 0 and a full 640 x 360 image is present. Treat it as a preview when its length is `width * height * 3`.
- Rows are stored bottom-up. Flipped, the image matches the `.jpg` next to the save better than as stored in all 113 catalog saves that have one (568 to 604): mean pixel difference 0.9 to 12.5 flipped, 3.9 to 71.9 as stored. Channel order is RGB (closer than red and blue swapped in all 113).
- To write a save back byte for byte, keep the original flag byte.
- A crash save has no preview (**Observed**, 604, one save). After an in-game assertion failure the game wrote `crash_<save name>_<date>.sav` in the save folder. Its preview size reads 0 x 0 with an empty preview string, so the header ends after a few KB instead of about 700 KB, and no `.jpg` was written beside it. The Load Game screen lists it as "Recovery Save" and draws a flat blue-violet square in place of the picture. Whether the label comes from the `crash_` prefix or from something in the file is **open**; the rest of the header reads as in any other 604 save. A save made from it in the game, after loading it and pausing two game days later, had the normal 640 x 360 preview and a `.jpg` beside it, so the empty preview is not carried over (**Observed**, 604).

### The two flags

The flag before the preview and the u8 `flag` after `mission, kind` always hold the same value. **Observed** on 599 to 604 in 182 saves: 110 catalog saves and 72 of our own, 73 with both 0 and 109 with both 1, none that differ. Formats 568 and 585 were not compared, because their headers do not read to that point. That they are one value stored twice, or two views of one state, is a guess from the match. What it records is **open**, and neither flag says anything about the preview.

Checked against it, none of these split the 182 saves into 0 and 1 (the best single setting still got about 30% wrong): format version, platform (see [platform.md](platform.md)), the map editor setting, number of mods, climate, economy, autosave or not, start year, map size and every stored game setting, so it does not follow the difficulty options. Saves of one game keep the value through a series of re-saves, including re-saves made after a load. One new game (604, Small 1 : 3, subarctic, seven mods, Normal difficulty, saved at once) read 0, and whether it started paused was not noted, so "0 means started paused" from the `flag` row above is not settled. A test that would settle it: two new games with identical settings, one started paused and one not, each saved at once.

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
