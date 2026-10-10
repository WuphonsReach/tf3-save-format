# Entity names

One table in the entity data holds a name for every entity: company, people, towns, industries, stations, stops, signals, lines and vehicles. Checked on 604, two played saves, compared with screenshots of the game:

- Catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (tropical, start year 1960, Asian name list). Read from a re-save with the same header counter. 25,524 names in a 751 MB stream.
- Catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (subarctic, start year 1900, European name list). 38,653 names in a 928 MB stream. Its header money matched the Account figure on the game's bottom bar.

Labels are **Observed** (both saves) unless marked.

## Layout

```
u32  n
str  x n
```

- The table sat 44% and 46% of the way into the stream. About 8 zero bytes and a u32 near 171,000 follow it in both saves, then more data. What they are is **Open**.
- `n` is directly before the first string. Parsing exactly `n` strings from there ended where the zero bytes begin in both saves.
- The u32 before `n` is not fixed. It was `n - 1` in the first save and 4,111 (with `n` 38,653) in the second, so ignore it. An earlier version of this note called it `n - 1`; that was a coincidence.
- An entity with no name holds the string `no name` (32% of entries in the first save, 28% in the second). Empty strings are rare: none in the first save, two in the second.
- The first entry is the player company's name. In both saves it was the account's display name followed by ` Transport` (or `user` and digits where there was no display name). It is account-derived, so don't publish dumps of the table.
- The default comes from the platform account on consoles too. In 54 of the 244 catalog saves and maps of [versions.md](versions.md), the uploader's mod.io name followed by ` Transport` was one string: Windows 23, PS5 18, Xbox 7, Linux 5, Mac 1 (**Observed**, 568 to 604, 2026-10-10). The count says nothing about how often the default is kept: a mod.io name that differs from the platform name and a company the player renamed look the same here. In our own saves (604), 32 of the 37 games first written under 604 held the Steam profile name followed by ` Transport`. None of 33 re-saves of catalog games first written under 555 to 596 held it, so loading another player's game keeps their company name (**Observed**). One re-save of a 599 game did hold it (**Open**).
- Position is not the entity id, but it is tied to it for the first entries. In the second save the company entity was id 58,492 and took slot 0, and two towns took slots 2 and 13 while the subsidy state gave them ids 58,494 and 58,505, so id = 58,492 + slot for those three. The table starts with the company followed by the towns. It stops fitting for later entities: an industry had id 38,333 (below the company's) and a line 135,964 (slot 77,472, past the end of a 38,653-entry table). So the table does not index every entity id. The rule for later entities is **Open**. In the same save one line and its two trains sat in consecutive slots, the line first.

## Finding it

There is no marker for the table. A way that worked on both saves:

1. Search the stream for a name you can see in the game, as a `str` (u32 length, then UTF-8 bytes). A town name works.
2. Parse `str` after `str` forwards until a length is not plausible (over a few hundred, or not valid UTF-8). The run was tens of thousands of strings long.
3. Walk backwards the same way: the earlier position whose length field ends exactly where you stand. The step was unambiguous in both saves (one candidate each time). It stops at the table's first string, because nothing before `n` parses as a string ending there.
4. Check that the u32 just before the run equals the number of strings from there to where the forward parse stopped, apart from the two zero words at the end that also parse as empty strings.

## What the names look like

| Entity | Name |
|---|---|
| Vehicle | The vehicle type word and a number: `Road Vehicle 959`, `Train 123`, `Ship 92` in the European save, the Chinese words for tram and road vehicle followed directly by the number in the Asian one (a space in one, none in the other). Numbers are per type and not reused: the first save's 31 trams were 1 to 31 with no gaps, its 257 road vehicles ran up to 265 with gaps (sold vehicles), and the second save's 952 road vehicles ran up to 959. Slot order does not follow the numbers early in the table |
| Signal | `<town> Signal <n>`, with a counter per town (one town reached 162) |
| Stop | In the Asian save, a word for "stop", `#` and a number |
| Station | `<town> <word for station>` in the Asian save, and names like `Bewdley Station Central` in the European one |
| Line | Stop or station names joined by ` - `. A line's name can end in a stray space (the Asian save) or in ` - ` (one line of 329 in the European save). A name of the shape `<place> - <cargo list>` also occurs, for example a town with two cargo names. The entity type was not checked |
| Person | A personal name in the style of the name list |

- Names need not be unique. In the European save 135 entries were one airport's name followed by `1`.
- The default vehicle words are stored as text at creation: the game's UI was English for both screenshots, and the Asian save's Chinese names showed unchanged (as boxes, see below). Whether the words come from the name list or from the language the author's game ran in is **Open**, since the catalog authors' languages are unknown.
- The UI font showed boxes for Chinese characters. Each box is one character, so a screenshot is enough to tell a name's length and shape. A six-stop line shown as six two-box groups joined by dashes matched the one name of that shape in the save.

## Not found

- How a line refers to its vehicles. The tram's id appeared 34 times in the first save, mostly in sorted lists of u64 entity ids (an id then four zero bytes), none close to a candidate line id.
- Where a vehicle keeps its model. The tram model's id, read from the model table ([models.md](models.md#the-model-table)), was not within 400 bytes of the tram's own id. Animals keep their model id in a model instance record with their transform ([models.md](models.md#the-model-instance-record)), not next to their own entity id, and vehicles do the same: see [models.md](models.md#vehicles-people-and-animals-in-one-run).
- A table of resource paths mapped to numbers (cargos first, then vehicle models) sits late in the stream as a Lua table. The number for each model is not the model id. **Open**.

- **Vehicle names and vehicle entity ids run in opposite directions (604, Observed, one game).** In the Small 1 : 3 game of [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604) (save `1441`, 2,264 names) Road Vehicles 21 to 29 sat in consecutive name slots in number order. Their entity ids, read from the `simParams.mapping` of vehicle notifications ([notifications.md](notifications.md)), fall as the number rises inside one purchase: Road Vehicles 19 to 26 are 25,329 down to 25,322, and 27 to 31 (apparently a later purchase) are 25,334 down to 25,330. So a vehicle's number is its name slot, not its entity id, and neither is its slot among the model instances ([models.md](models.md#vehicles-people-and-animals-in-one-run)). The entity id of a vehicle occurred only 4 times in the stream for Road Vehicle 27, all in `happiness_vehicle` statistics entries (an entity reference with revision 1), none in the model instance or next to its position. The link from an entity to its instance slot is still **Open**; a depot's or maintenance station's position fixes it for one vehicle at a time (the road-vehicle bullet of that models.md section).

## What a rename and new building do to the table (604)

**Observed** on 604, one new game, two saves 5,600 units of play and many edits apart (the tables had 1,302 and 1,350 strings, both found with the anchor method above, 1,297 strings before the anchor in each).

- **A rename replaces the string in place.** The player renamed a town (the second string in the table changed from `East Retford` to `Retford`) and two lines (`Line 1` and `Line 2` became `TOD Fish Cargo Truck 1` and `TOD Fishery Boats`), and the string at the same position changed each time. Nothing else moved. Stations built before the town rename kept `East Retford Station` and `East Retford Maintenance Building`, so a name that was built from another name is a plain string afterwards, with no link back.
- **New entities mostly append, but they can take a free slot.** 48 strings were added at the end (the new quarry, depots, warehouse, stations, vehicles, lines and a few people). Seven positions in the middle of the table, which held names of private people in the first save (and one `no name`), held new things in the second: stops (`George Street` twice, `Highfield Road` twice), road vehicles (`Road Vehicle 17`, `18`, `19`) and a line (`RET-TOD Bus 1`). So an entity that is deleted frees its slot, and a later entity can reuse it, which fits "position is tied to the id" above. People are created and removed during play, so the people's slots are the ones reused. **Observed**, once.
- **The default vehicle numbers count per kind, whatever the slot.** The new road vehicles were `Road Vehicle 4` to `Road Vehicle 32` and the new ships `Ship 5` and `Ship 6`, matching 29 road vehicle purchases (4 at one time, 25 at another) and 2 ship purchases in the journal ([finances.md](finances.md#a-new-games-first-batch-of-bookings-while-paused)). Names shown as `Road Vehicle 17` to `19` sat in reused slots, while 20 to 32 were appended, so the number follows creation order and not table position.
- Line names the player chose (`RET-TOD Bus 1`, and the trucks' lines) are plain strings of the same table.

## Renaming industries, and a new line with its ships (604)

**Observed** on 604, the Series A game: save `1246` against `1312` (made right after), with the names table parsed in both (1,849 names, then 1,864).

- **A rename is in place for every entity involved.** The player renamed the four fishing industries near one town (the original Fishing Grounds and the East, South and West ones) to "Todmorden Fishing 1" to "4" and the fishing line "TOD Fishery Boats" to "TOD Fishery 1". Each changed in the slot it was in. An industry's name sat in two slots: the original at slots 7 and 852 (far apart), the three that appeared in play in two adjacent slots each (1,357 and 1,358 for West, 1,391 and 1,392 for South, 1,625 and 1,626 for East). The second slot of each is probably the industry's station, whose stop name in the line window follows the industry's. **Observed**.
- **New lines and their vehicles are appended at the end of the table, line first.** Two new lines ("TOD Fishery 2", "TOD Fishery 3") came after the last entry, each followed by its ships (Ship 7 to 11, then Ship 12 to 19). The ships are numbered on from the last one, (numbers count per kind, see [above](#what-a-rename-and-new-building-do-to-the-table-604)). No other entity was added: the new lines' stops reuse the port's stop.
