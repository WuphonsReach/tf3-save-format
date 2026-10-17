# Towns placed in the map editor

Checked on 604, one map: the [Tiny flat editor game](test-games.md#tiny-flat-editor-game), a blank template, then a hand-drawn road network, then three towns placed one at a time (smallest size, largest size, a middle size), one save after each. Claims are **Observed** unless marked; **Open** items are at the end. The editor file in general: [editor-saves.md](editor-saves.md).

## In short

- **What a new town appends (Observed, 604, one Tiny flat map, three towns).** A town record, names (append-only: the town, its residents and one `no name` slot per building), street edges, junction records and ground polygons, parcels and road-surface strips on its own edges, building records with the new town's id in their `town` field, and model instances (about 74 to 86 per building). Old data is not rewritten except where the new streets cut an old road.
- **The header counter is the number of named people (Observed).** It read 0, 0, 39, 489 and 728 against 39, 450 and 239 people added; residents run a little below the town record's residential capacity.
- **Ids fill gaps (Observed).** A later town's ids can lie below an earlier one's top.
- **Open.** The spare record at the end of the building run, the town centre, why residents fall short of capacity, and a defect in `model_instances.py`.

## What a new town appends

- **A town record** ([town-records.md](town-records.md)), after the earlier ones. The `u32` in front of the first record counts the towns (1, 2, 3 in the three saves).
- **Names** ([entity-names.md](entity-names.md)). The table is append-only: the new town's name goes after the last resident of the town before it, followed by its residents and one `no name` slot per building. The table starts with a `u32` count of entries (1 in the template and the roads save, then 68, 734 and 1,104).
- **Street edges, junction records and ground polygons** for the town's streets, in the same tables as hand-drawn roads. The town streets were the types `town_old_small` and `town_old_xsmall` (the middle town also two `town_old_medium`). Adding a town does not move or rewrite an existing edge, except where its streets join an old road: there the old road's edges are cut at the new junction nodes and replaced by shorter ones (four edges of 92 to 98 m were replaced by shorter ones; one of 98 m became 43.6 and 54.6 m).
- **Parcels and road-surface strips** ([parcels.md](parcels.md)), on the town's own edges. Hand-drawn roads have neither until a town reaches them. The middle town was placed over the hand-drawn roads and took 295 parcel records along 20 of the old edges (12 `town_old_small`, 8 `town_old_medium`); the two earlier towns lay clear of every old road and took none.
- **Building records** ([town-buildings.md](town-buildings.md)), with their `town` field set to the new town's entity id, and one construction record (`buildings`, `capacity`, `cargoTypes`, `parcelFace` strings) and one lot ground polygon per building. Each save also ends the run with one more record that has no parcels (ids 1962, 4999 and 7412 in the three saves) and one more construction record and lot polygon than the scan counts (27, 242, 372 against 26, 241, 371); the next town's first building takes that id (1962 is the largest town's first building, 4999 is in the middle town's list). The counts above leave it out.
- **Model instances** ([models.md](models.md)): houses and shops (`a_res_*`, `a_com_*`, `a_ind_*` models) and, around them, hedges, fences, lamps, barrels, flower pots and similar. About 74 to 86 per building. These are roughly 40 percent of the stream growth. `pedestrian_connection` ground polygons (street crossings) also grow with a town (5, 47, 464, 712 in the four saves).

Old data is not rewritten: 64-byte blocks sampled every 4 KB from the older stream were all found again in the newer one for the first two town steps, and 2,176 of 2,191 for the third (the re-cut roads). The rest of the growth is insertion, spread over the edge table, the junction table, the ground polygons and the entity data.

## The header counter is the number of residents

In these editor saves the header counter (a copy of company experience in a played game, [company.md](company.md#the-header-counter)) is the number of named people: the names table's non-`no name` entries, less the company, the towns, and the two empty strings that end the table. It read 0, 0, 39, 489 and 728, and the people added were 39, 450 and 239. The same count gives 488 on the two-town editor saves `1937` and `1938` once the six industry names (two per industry) are also taken out. Residents run a little below the town record's residential capacity (39 of 42, 450 of 451, 239 of 239; 488 against 247 + 247 on the older map). Whether a resident is simply a filled capacity slot is **Open**.

## Entity ids

New ids are not all above the old ones: the largest town's ids run 1,962 to 4,983 and the middle town's town id is 3,780 with buildings from 4,460, so a later town fills gaps below an earlier one's top. Lowest-free-first is a guess. The free-id list reader (`street_edges.py`, [road-network.md](road-network.md#the-other-tables-a-road-edit-touches)) found no list in these small streams.

## Open

- **The spare record at the end of the building run.** What it is before a town takes it (a reserved building entity, or a placement ghost of the town tool) and what the extra construction record and lot polygon hold; whether the last town of a finished map still has one.
- **The town's centre** is not in the town record or any record read ([town-centre.md](town-centre.md)).
- **Why residents fall short of capacity** in some towns, and whether the free-id list exists in editor saves at all.
- **Tool defect.** `model_instances.py --prefix ''` prints a run of 900 to 1,300 `bird_crane` entries with x 1, y 0, z 0 in these saves. They are not cranes (13 is the real count, [animals.md](animals.md)): the tool reads a table that is not instances there.


## Evidence and tests

### The step in numbers

| | roads only | smallest town | largest town | middle town |
|---|---|---|---|---|
| Stream growth | +3.3 MB | +0.8 MB | +5.6 MB | +4.0 MB |
| Street edges added | 337 | 11 | 65 | 65 (4 old edges re-cut) |
| Parcels added | none | 242 | 1,416 | 1,447 |
| Building records added | none | 26 | 215 | 130 |
| Named residents added | none | 39 | 450 | 239 |
| Town record capacities (residential, commercial, industrial) | none | 42, 52, 47 | 451, 562, 568 | 239, 190, 233 |
| Model instances added (137 bytes each) | none | about 2,300 | about 17,400 | about 9,700 |

The roads-only save already had the junction table and the street ground polygons, but no parcel table, no road-surface strips, no building records and no town record. Those appear with the first town ([road-network.md](road-network.md) for the road tables).

### Autosave

An autosave of the last manual save (clock still 1900-01-01) differed from it in the preview, two bytes in the ground polygons and about 400 bytes near the end of the stream, nothing else.
