# Header

The header starts the decompressed stream. Fields in order. Checked in full on 599, 601 and 604. Format 568 and 585 match up to and including the preview image, then differ (see [versions.md](versions.md)).

The layout follows [tf3-save-editor's FORMAT.md](https://github.com/TBK/tf3-save-editor/blob/main/docs/FORMAT.md). The meanings marked "ours" were worked out here and are being passed upstream.

| Field | Type | Meaning |
|---|---|---|
| magic | 4 bytes | `tf**` |
| version | u32 | Format version, for example 604 |
| start year | u32 | Year the game was started, not the save date (ours). 1900 to 2020 seen, mostly whole decades, 1900 and 2020 most often. In three catalog saves it differs from the day table's first day, see [calendar.md](calendar.md#the-game-clock) |
| map width | u32 | Metres (ours). For example 20480 |
| map height | u32 | Metres (ours). For example 40960 |
| date | u32 | The date shown in the game, as a Julian day number (ours). Equal to the day table's last day in the 120 catalog saves (568 to 604, **Observed**) and to the date on screen in three (**Confirmed** on 604). See [calendar.md](calendar.md#the-date-in-the-header) |
| money | i64 | Copy of the company balance, shown in the load dialog |
| counter | u32 | Copy of the company's `experience` (ours, **Observed** on 585 and 599 to 604). The first `experience` number in the company progression script state (the one next to `companyState`, `level` and `potentialLevel`) matched the header in 16 of 19 saves and ran 1 to 4 points ahead in the other 3, so the header is probably written just before the state. In catalog save 6417707 it ran 242 ahead, so the gap is not always small (see [script-states.md](script-states.md#company-and-rank)). It grows with play (8563 in the first save of a game started on 1 Jan 1900, rising to 16513 over later saves of that game whose autosaves were all named `_1900-01-01`). 0 to 59,478 in the 120 catalog saves (568 to 604), 0 in one. FORMAT.md calls it `year` |
| info | Lua table | Holds `company.level` (ours). 1 to 15 in 117 of 120 catalog saves (568 to 604); empty in the other 3 and in editor saves |
| mods | vec<mod> | Mods the save uses, see below |
| preview flag | u8 | 0 or 1. Does not say whether a preview is present (ours): 0 in 60 of 120 catalog saves, all with a full preview. Meaning **open** |
| preview width, height | u32, u32 | 640 x 360 in every save checked (120 catalog saves, 568 to 604) |
| preview | str | Raw RGB8, width x height x 3 bytes, **bottom row first** (ours) |
| stats | i64 x 6 | Index 3 is another copy of the money (equal in all 120 catalog saves) |
| stats | i32 x 11, vec<(u32, u32)>, u32 x 2, i64 x 9, u32 x 2 | **Open** |
| labels | vec<(str, u32)> | Text such as `"%d Point(s) for Company Value"` with a number |
| stats | u32, i64 x 2, u32 | **Open** |
| config mods | vec<str> | The ids of the save's mods, the same set as the mod list above (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604) |
| config resources | vec<(str, str)> | Keys `climate`, `economy`, `nameList`, each a path such as `::/economy/all.eco` |
| config params | vec<(str, Lua table)> | The entry with the empty key holds the game settings; every other entry is one mod's own options, keyed by its id. See below |
| mission, kind | str, str | |
| flag | u8 | 1 in two saves started at normal speed, 0 in one started paused. Not the pause state at save time: seven saves of one 604 game, each written with the game paused after a stretch at 4x (the last four after changing the calendar speed and the cycle modes), all read 1 (**Observed**). 0 and 1 are about equally common in the catalog. Calendar speed is not stored here. Meaning **open** |
| value | u32 | The format version the save was first written under, probably (ours, **Observed** on 585 to 604). Equal to the version in 604 saves; 596 to 601 in 601 saves; 585 in a 604 save that was a re-save of a 585 save. Never above the save's own version in the catalog saves and maps summarised in [versions.md](versions.md). One editor map (604) held 256 (**open**) |
| id | str | The **map seed**: the text of the Seed box in the New Game dialog (ours). **Confirmed** on 604: a game started with the typed seed `RaazVnK55w` and saved at once holds exactly that string. **Observed** on 599 to 604 in the 110 catalog saves whose header reads to the end: 104 hold 10 random letters and digits (the form the game offers), 6 hold typed text such as a town name or `0`. Unchanged across re-saves and autosaves of one game, and equal in two catalog saves and the re-saves made from them. 94 distinct values in 110 saves, so not unique. The sliders (ocean, islands, mountains) that went with it are not in the stream (**Observed**, 604: no `mz_layout`, `oceans` or generator path), so the seed alone may not rebuild the same map (**Open**). The terrain tests (same seed twice, a changed Mountains slider, a game run for 11 days) are in [terrain.md](terrain.md): the same seed and sliders give the same bulk of the data, a changed slider changes nearly all of it (**Observed**, 604). The game also writes it to its log, see [below](#the-seed-in-the-games-log) |

Lua tables are encoded as in [lua-values.md](lua-values.md).

## The seed in the game's log

The seed can also be read without a tool, from the game's log (a tip from the game's subreddit, checked by us). The log is `stdout.txt` in the `crash_dump` folder of the game's user data folder, next to `save/`. **Observed** on 604, in one session of 10 new games and 7 loads of saved games:

- Starting a new game writes a line ending `Seed text: <seed>`, then one ending `Map seed text: <seed>`.
- Loading a save writes only the `Map seed text` line. The log does not name the save, but all 7 loads were of one test series and printed its seed, the value every save of that series holds in `id`. Just before the line the log prints the active mods, the `climate`, `economy` and `nameList` paths and the game settings table, the same values as the header's config fields.
- The file began with that session's startup line and held nothing from earlier sessions, so it seems to be rewritten each time the game starts. To find the seed of an older game, load its save and then search the log for `seed`; the last match is that save's.
- No terrain sliders appeared in the log either, so it does not settle whether the seed alone rebuilds the map.

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
- **A setting is stored as its position in the option list plus 1** (**Confirmed** on 604). The option lists, defaults, difficulty presets and the effect of changing settings on the Load Game screen are in [settings.md](settings.md).
- **Mods keep their options in the same list** (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). Besides the empty key there is exactly one entry per mod, keyed by the mod's id, so the list has one more entry than the config mods. All 3,002 mod entries matched an id in that save's mod list. A mod without options has an empty table; one with options holds its own keys, for example a toll mod's `toll` or a train mod's `acceleration`, `braking` and `curves`. The values are Lua numbers (f64), like the game settings, which are numbers apart from the bool `isMapEditor`. Whether mod values follow the same position-plus-1 rule is **Open**. The order is neither the mod list's order (it matched in 39 of 110 saves) nor sorted, so look entries up by key.
- **The stored settings are those of the last load, not of the New Game screen** (**Confirmed** on 604). Changing options on the Load Game settings tab rewrites them in the next save, and the Industries and Climate choices there rewrite the `economy` and `climate` resources above. Details and open questions in [settings.md](settings.md#changing-settings-when-loading).
- `map.size` does not give one size. A value of 3 was 11264 x 11264, 6656 x 19968 and 8192 x 16384 in different saves. Use the header's width and height for the real size.

## Money in the header

**Observed** on 604: in six saves of one game the header money equalled the Account figure in the game exactly, so the lag below does not always show. In one of them the account was -2,598,471, so a negative header value can be the true balance.

**Observed** on 604: a catalog save of a played game (6428935, account 3,382,382,812 in the game) was loaded, paused at once, saved again and reloaded. The re-save's header money, the Account figure and the Finances tab's current Bank Account were all 3,382,382,812, and the header counter was unchanged at 15,808. In the stream, far in front of the Lua states, there is a long run of i64 values that each sit within a few percent of the one before and read as a balance history. Three of them, 12 entries apart, equalled the Bank Account row for the last three finished periods on the Finances tab (3,302,688,957, 3,330,544,108, 3,363,416,724). The tab shows six-month periods, so that is about two entries a month. The last entry of the run was 3,382,379,554, which is the header money of the original save and not the re-save's, so the history is sampled and the live balance is not appended to it. It is not the money journal that FORMAT.md describes: that is a separate run of 21-byte bookings, see [finances.md](finances.md). Find it by searching for one of the period-end figures as 8 little-endian bytes. **Observed**, one save.

**Observed**: in one played save the header said 8,932,346 when the game showed 8,920,255, so it tracks the balance but can lag. In catalog save [6430076](https://mod.io/g/transportfever3/m/gigantomanisch-fjpjcl8aod-start-bearbeitet) the header holds 0 while the game shows -18,153,221. Why is **open**: negative values are stored too.

**Observed** on 604, one game (a temperate test game with nothing built and no loan taken): the header money was 0 in saves on 1 January 1900, 20 September 1900 and 2 January 1901, and the game's Account read 0 with Earnings $0 on 2 January 1901. That game had no starting capital, and with nothing built the balance did not move over a year. Which setting gives a start with no capital is **Open**.

**Observed** on the 120 catalog saves (568 to 604): the header money is 0 in 53 and negative in 13. Several negatives are round numbers (-25,000,000 in four saves, -100,000,000, -24,000,000), so the header may not always hold the balance. The real balance is in the money journal (see FORMAT.md).
