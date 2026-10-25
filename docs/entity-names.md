# Entity names

One table in the entity data holds a name for every entity: company, people, towns, industries, stations, stops, signals, lines and vehicles. Checked on 604, two played saves, compared with screenshots of the game:

- Catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (tropical, start year 1960, Asian name list). Read from a re-save with the same header counter. 25,524 names in a 751 MB stream.
- Catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (subarctic, start year 1900, European name list). 38,653 names in a 928 MB stream. Its header money matched the Account figure on the game's bottom bar.

Labels are **Observed** (both saves) unless marked.

## In short

All 604. The table was read in two catalog saves and then six of ours.

- **One table of `u32 n` then `n` `str` holds a name for every entity: company, people, towns, industries, stations, stops, signals, lines and vehicles (Observed).** It has no marker; find it by parsing `str` after `str` from a name seen in the game, then backwards to the count.
- **The first entry is the company name, which defaults to the account's display name plus ` Transport` (Observed),** so do not publish dumps. Loading another player's game keeps their company name.
- **The towns follow the company in slot order, and industries follow with names built on their town's (Observed).** `tf3save.town_names` takes the run; the Giant editor map keeps its town names elsewhere (Open).
- **Position is tied to the entity id only for the first entries (company and towns); later entities do not index into the table (Observed).** The rule is Open. On 605, 26 lines with known ids and names showed no stored link at all: no constant offset, no nearby record, no parallel id list, no lookup by id ([line-ids.md](line-ids.md#605-26-lines-named-by-a-mods-log)).
- **A vehicle's number is its name slot, not its entity id, and ids within a purchase are the slot plus a constant that differs between batches (Observed, one game).** The link from an entity to its model instance slot is Open.
- **Open:** what the zero bytes and the `u32` of about 171,000 after the table are, the resource-path table late in the stream, how a line refers to its vehicles, and whether the default vehicle words come from the name list or the author's language.
- What changes when something is renamed, built or sold: [entity-name-edits.md](entity-name-edits.md).

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
- Position is not the entity id, but it is tied to it for the first entries. In the second save the company entity was id 58,492 and took slot 0, and two towns took slots 2 and 13 while the subsidy state gave them ids 58,494 and 58,505, so id = 58,492 + slot for those three. The table starts with the company followed by the towns. It stops fitting for later entities: an industry had id 38,333 (below the company's) and a line 135,964 (slot 77,472, past the end of a 38,653-entry table). So the table does not index every entity id. The rule for later entities is **Open**. In the same save one line and its two trains sat in consecutive slots, the line first. That holds only for a line bought together with its vehicles: in the [Wool1 game](line-ids.md) a train line sat 10,000 slots before its train, and no slot number was found beside an entity id.

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

## Town names (604)

**Observed** on 604, six saves of ours (new, played and editor): in a new or played game the towns are the names directly after the company, in slot order, and the industries follow with names built on their town's (`<town> Crop Farm`). `tf3save.entity_names` finds the table (the longest run of `str` around a `no name` entry) and `tf3save.town_names` takes the run from slot 1 up to the first `no name` or the first name that holds an earlier town's name as a whole word (`East Retford Crop Farm`) or starts with it and a hyphen. The run is dropped when it is shorter than the town records or town states found, or when fewer than a tenth of its names appear in a later name (`<town> Station`, `Farm <town>`). That is how it refuses the Giant editor map, whose table held only five person names after the company although the map has 18 town records; where an editor map keeps its town names is **Open**. Also **Open**: a town whose name holds an earlier town's name as a word ends the run early, and towns renamed in play (catalog save 6433459, Chinese names) let industries on the old names, and people, join the run (16 names, 3 towns).

Position and population are not in the table, and the town record has neither ([town-records.md](town-records.md)). The mined summaries carry the names as `towns` ([tools/README.md](../tools/README.md)).

## Not found

- How a line refers to its vehicles. (For road vehicles in 604 the records that name a line and a vehicle are trip records whose owner is not found, [trip-plans.md](trip-plans.md#trip-plans-line-stops-and-vehicle-or-a-building-604); a vehicle's own line assignment was not found. The tram case below was not rechecked.) The tram's id appeared 34 times in the first save, mostly in sorted lists of u64 entity ids (an id then four zero bytes), none close to a candidate line id.
- A table of resource paths mapped to numbers (cargos first, then vehicle models) sits late in the stream as a Lua table. The number for each model is not the model id. **Open**.

## Vehicles: model, name slot and entity id

- **The model is not next to the vehicle's entity id.** The tram model's id, read from the model table ([models.md](models.md#the-model-table)), was not within 400 bytes of the tram's own id. Vehicles keep their model id in a model instance record with their transform, as animals do ([vehicles.md](vehicles.md#vehicle-instances-604)).
- **Vehicle names and vehicle entity ids run in opposite directions (604, Observed, one game).** In the [Small subarctic game](test-games.md#small-subarctic-game) (save `1441`, 2,264 names) Road Vehicles 21 to 29 sat in consecutive name slots in number order. Their entity ids, read from the `simParams.mapping` of vehicle notifications ([notifications.md](notifications.md)), fall as the number rises inside one purchase: Road Vehicles 19 to 26 are 25,329 down to 25,322, and 27 to 31 (apparently a later purchase) are 25,334 down to 25,330. So a vehicle's number is its name slot, not its entity id, and neither is its slot among the model instances ([vehicles.md](vehicles.md#vehicle-instances-604)). The entity id of a vehicle occurred only 4 times in the stream for Road Vehicle 27, all in `happiness_vehicle` statistics entries (an entity reference with revision 1), none in the model instance or next to its position. The link from an entity to its instance slot is still **Open**; a depot's or maintenance station's position fixes it for one vehicle at a time (the road-vehicle bullet of that models.md section).
- **Within a batch of new vehicles the entity id is the name slot plus a constant (604, Observed, one game).** In the same game (save `1401`) the vehicle-condition entries of [notifications.md](notifications.md) name vehicles in `simParams.mapping`, which gives pairs of entity id and name. Ships 12 to 19 sat in slots 1,854 to 1,861 (Ship 12 to 16 and 19 are in the mapping, Ship 17 in another save) and had ids 33,640 to 33,647, so id minus slot was 31,786 for all of them, and a ship's number and its id rose together. Ship 8 (id 33,629, slot 1,849) and Ship 11 (id 33,632, slot 1,852) give 31,780. So the offset is the same inside one purchase and differs between the two: Ship 11 is id 33,632 and Ship 12 is id 33,640, eight ids apart for slots two apart (the second line's name sits in slot 1,853), so six ids more than the slots explain belong to entities that took no slot there. What they are is **Open**. The first offset must not be applied across batches: it gives the name of a person (slot 1,843) for the id of Ship 8. Ships bought together in one batch can therefore be read from the name table by slot once one id of the batch is known. The opposite direction seen for the road vehicles above (ids fall as numbers rise) did not hold for these ships, so the direction depends on the purchase.
