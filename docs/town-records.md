# Town records

Each town has a record in the entity data, far into the stream (about 390 MB into a 400 MB stream on a giant map). Checked on 604, editor saves and played saves.

The record has no name, id or position. To tie a record to a town, match its capacities and cargo ids against the map editor's Towns export of the same save. Two towns can share capacities, but in every case seen their cargo told them apart. Records are in entity order, not alphabetical.

## Table header

The records sit in one contiguous run, after four u32s. The last is the town count:

| Save | Values |
|---|---|
| 18-town giant editor map of ours | 12800, 29, 0, 18 |
| Catalog save [6421140](https://mod.io/g/transportfever3/m/marschbahn-westerland-niebll-ohne-mods) | 4096, 24, 0, 27 |

The first three values are **open**.

## Starting layout (78 bytes)

A town with one commercial and one industrial cargo, as the game creates them:

| Offset | Type | Meaning |
|---|---|---|
| 0 | u32 x 3 | Target district capacities: residential, commercial, industrial. The editor export's `sizeFactors` are these divided by 100 |
| 12 | f32 x 4 | 1.0 in new towns. Change during play. **Open** |
| 28 | 5 bytes | Zero. Probably an empty residential cargo list plus a byte |
| 33 | u32 | Commercial cargo count (1) |
| 37 | u32 | Commercial cargo type id, see [cargo-ids.md](cargo-ids.md) |
| 41 | f32 | Commercial cargo weight: 1.0 for tier 0 cargo, 0.5 tier 1, 0.25 vehicles |
| 45 | u32 | Industrial cargo count (1) |
| 49 | u32 | Industrial cargo type id |
| 53 | f32 | Industrial cargo weight |
| 57 | u32 | 1. **Open** |
| 61 | 17 bytes | Zero in editor saves. Not zero in played saves, **open** |

**Confirmed**: changing the cargo ids and weights in place in an editor save changes the towns' starting cargo. The game loads the save, and its Towns export shows the new cargo with positions and sizes unchanged.

## Longer records

The two cargo lists are each a u32 count followed by `(u32 id, f32 weight)` pairs, so a town with more cargo has a longer record.

In catalog save [6421140](https://mod.io/g/transportfever3/m/marschbahn-westerland-niebll-ohne-mods), a hand-built map, one town has capacities 1600 / 1600 / 1600, a first float of 1.5, nine entries in the first list (fish, meat, beverages, vegetables, machines, fuel, clothes, furniture, glass) and none in the second. That record is 134 bytes. The cargo icons on its in-game label match all nine. So the first list is not strictly commercial. In that save the last 17 bytes of every record are nine zeros, the f32 63.0, then four bytes that differ per town.

Played saves show more shapes: gaps of 110 bytes between records, and floats such as 13.2, 11.0 and 7.8. Those layouts are **open**.

## Finding the records

A strict scan for the starting layout (four floats exactly 1.0) misses towns that have changed. A looser scan, validated on a 34-town played save with no false hits:

1. Three u32 capacities, each between 10 and 1,000,000.
2. Four f32 values, each finite and between 0.05 and 20.
3. Five zero bytes.
4. A u32 cargo count of 1 to 3.

Loosening the floats further (any value) gave 24,872 false hits in a 618 MB stream. `scan_records` in [tools/tf3save.py](../tools/tf3save.py) implements this scan and keeps only records with one commercial and one industrial cargo.

In that 34-town save one town (the player's starting town) had runtime values: a first float of 1.06 and capacities 424 / 667 / 475 where the editor showed 449 / 668 / 476. The other 33 matched the export exactly. So capacities and floats are live state in a played save.

## A new game's three towns against the town window

**Observed** on 604, one new Small 1 : 3 subarctic game ([finances.md](finances.md#a-first-build-out-row-by-row)), paused at 1 January 1900 with almost nothing built. `scan_records` found three records, 78 bytes apart, with capacities 396 / 418 / 268 (fish and cement), 164 / 98 / 115 (meat and planks) and 282 / 209 / 275 (fish and fuel).

- The town window of one town (a Small Village) showed a population of 281, "Earn 3,367 Experience Points" to the next level, and a supplies panel with passengers 0 / 281, fish 4 / 68 and fuel 0 / 97. Its fish and fuel icons are the only fish-and-fuel pair among the three records, so it is the third record, whose capacities are 282 / 209 / 275. The records follow the entity order, and the names table puts this game's towns in slots 1 to 3 as Retford, Bromsgrove and Todmorden ([subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604)), so the third record being Todmorden agrees. The cargo told the towns apart, as above.
- The district-size chart of that town read about 281 residential, 203 commercial and 268 industrial. The record's 282 / 209 / 275 are close but not equal, so the record holds target capacities that sit a little above the sizes built. The chart was read by eye, so the differences are not exact. **Observed**, one town.
- The first float of the record was 1.0 for all four in all three towns, even though play had started (the 1.06 above came from a game played for a long time).
- The two floats in the last 8 bytes of the 78 (offsets 70 and 74) differed between the towns: 66.9 and 181.2, 63.0 and 138.3, and 66.1 and 3,555.6. The third town's window said 3,367 points to go, so 3,555.6 less 3,367 is 188.6, but nothing shows that this subtraction is meaningful. **Open**.
- Supply figures 68 (fish) and 97 (fuel) did not equal the commercial and industrial capacities (209 and 275) or any simple ratio of them (68 / 209 = 0.33, 97 / 275 = 0.35). Where they come from is **Open**.

## The same three towns after play (604)

**Observed** on 604 in the same game at clock 5,997,000 (save `1246`), against the three town windows.

- **All three records matched their windows by cargo.** The first record (fish and cement) is the town whose supplies panel showed fish and cement, the second (meat and planks) the one showing meat and planks, the third (fish and fuel, see below) the one showing fish, a tin and fuel. The records are still in the order Retford, Bromsgrove, Todmorden, as the names table has the towns. The three target capacities were unchanged from the new game (396 / 418 / 268, 164 / 98 / 115, 282 / 209 / 275), so they are fixed targets and not live counts, at least in a game of this length.
- **A town can gain a commercial cargo and its record grows.** The third record (Todmorden, a "Village" of 482 people, growing) now holds two commercial cargos, fish with weight 1.0 and tinned_food (id 28) with 0.5, so it is 8 bytes longer than the other two (86 against 78). Its supplies panel showed a tin icon beside the fish with its own demand (88 against fish 177, the weights' 1 : 2). It was a 78-byte record in the new game with fish only. The other two records stayed at 78 bytes. `scan_records` in [tools/tf3save.py](../tools/tf3save.py) keeps only records with exactly one cargo in each list, so it finds only the first two of these three.
- **The second float is the population over the first residential capacity.** The record's four floats were 1.0, 1.2025, 1.0669, 1.1203 for the first town (475 people, capacity 396), 1.0 four times for the second (161 people, capacity 164) and 1.0, 1.7057, 2.3288, 1.2277 for the third (482 people, capacity 282). The window populations divided by the capacities are 1.1995, 0.98 and 1.709, so the second float follows the population (to about 0.3%), with a floor of 1.0 for the stagnant town. **Observed**, three towns. The first float stayed 1.0 in all three, and what the third (2.33) and fourth floats measure is **Open**: the supplies panel's demand figures (fish 146, cement 99 in the first town, fish 177, tin 88 and fuel 122 in the third) are 0.33 to 0.36 of the capacity times the float for the commercial cargo (fish) and the industrial one, but not exactly, so no formula is claimed.
- **The last 8 bytes of the 78 kept growing.** The pairs (offset 70 and 74) were 72.7 and 3,251.0 for the first town, 67.1 and 5,642.1 for the second and 71.0 and 10,614.5 for the third, up from 66.9 and 181.2, 63.0 and 138.3, and 66.1 and 3,555.6 in the new game. The second town's window said "No Experience Earned Last Year" and showed 2,250 points to the next level, yet its second float rose by about 5,500, so the second float is not the experience earned. The windows' experience to go (Retford 2,471, Bromsgrove 2,250) matches none of the figures by a plain difference. **Open**.

## Town buildings and "Historic Preservation" (604)

**Observed** on 604 in the Small 1 : 3 game, saves `1427` (clock 11,239,800), `1428` and `1429` (both 11,324,600), with the player's screenshots of a commercial building in the catchment of the port.

- **The window.** A commercial building's window showed a first row of its level (1), the supply of each cargo it takes (fish 100% or 83%, tinned food 0%) and the year (1900), then "Input Stocks" (fish 2 of 2, tinned food 0 of 1), "Customers" (6 of 6, then 5 of 6 at the later look) and a "Historic Preservation" checkbox, whose tooltip reads that it keeps the building's appearance but it can still level up. The player ticked it between `1427` and `1428`.
- **What the game's API says it is.** The `TownBuilding` component (`api/engine.d.tl`) holds `personCapacity`, `stockList` and `construction` (entities), `level` (1 to 4), `parcels` (entities), `depth` (1 to 4), `height`, `town` (entity), `timeBuilt` (clock) and `blockedDevelopment` (boolean, "block town developer from changing this building"). The command that the checkbox runs, `makeTownBuildingSetBlockedDevelopmentCmd` (`api/cmd.d.tl`), sets that boolean, and the game's own comment calls such a building "Historic". So the flag is `blockedDevelopment`, and the building's customers and stocks sit in the entities it points to.
- **Confirmed on 604 (one game, two buildings): the flag is one byte in the building's record, and the records can be listed.** Saves `1428` (the 5 of 6 building ticked, clock 11,324,600) and `1429` (the 8 of 8 building also ticked, same clock 11,324,600, paused throughout) differed in 124 places, and one of them was a single byte going 0 to 1 inside the record below. `1427` had no record with the byte set, `1428` one and `1429` two, so the byte is the "Historic Preservation" tick (`blockedDevelopment`). The player's count agrees: only two buildings on the map had been ticked by `1429`, and the scan finds exactly two set bytes among 569 records.

```
u32  a            an entity id
u32  b            the same id again, or 0xffffffff
u32  level        1 to 4 by the API; 1 and 2 only in this game
u32  d            an entity id (often a - 1)
u8   blockedDevelopment   0 or 1
vec<u32> parcels  u32 n (1 to 4 here), then n entity ids
u32  depth        1 to 4
f32  height       metres
u32  town         the town's entity id
u64  timeBuilt    a clock value, see calendar.md
```

- **The records follow each other with nothing between them.** A record is 41 + 4n bytes, and the distances between consecutive flag bytes were 45, 49, 53 and 57 (n = 1 to 4) for nearly all of 569 records. The order differs from the API's list (the flag sits straight after `level` and one entity, before the parcels). The scan took a `level` byte, an entity, a flag byte of 0 or 1 and a count of 1 to 16, then checked depth, height, a town id and a build time; a find-by-pattern, not by offset.
- **What the 569 were.** Three towns (entity ids 17,912, 17,913 and 17,914, with 181, 82 and 306 records), every building of the game, not only commercial ones. `1427` held 566 records and `1428` 569: the three buildings built in the 91st month. The two ticked buildings are both in town 17,914: the 5 of 6 one has height 23.3 and `timeBuilt` 9,936,000, the 8 of 8 one (the larger) height 25.7 and `timeBuilt` 7,440,000. Build times run from 0 to 11,304,000, and several buildings share one value (5,017,600 for example), so they come in batches. What `a`, `b` and `d` point to was not followed.
- **Save `1430` (clock 11,324,600 again, paused) after the player ticked a group of buildings.** The scan paired its 569 records with those of `1429` in order: every field other than the flag was equal, 14 flags went from 0 to 1 and none went back, so 16 were set (the player's count was "a whole bunch more"). Of the 14, 12 were in town 17,914 and 2 in town 17,912; 7 had level 1 and 7 level 2, 1 to 4 parcels, depth 1 to 4, heights 5.5 to 22.1 m, and `timeBuilt` of 0 (three buildings that stood at the start), 1,968,000 to 5,712,000 (eleven), 8,256,000 and 10,464,000. The streams differed in length by about 17,000 bytes, so records were paired by order, not offset. The player confirms 14 and says they were random buildings across the town area, a mix of industrial, commercial and residential, so the ticks are not tied to a street. The whole table of 569 records spans about 32,000 bytes and the 16 set flags span 17,700 of them (341 records between the first and last), which is what a scattered pick over a table that size looks like; the record order was not shown to follow position. **Observed**, one game.
- **Save `1431` (clock still 11,324,600): five houses ticked.** Again every other field was equal and exactly 5 flags went 0 to 1, so 21 were set. All five had `b` = 0xffffffff, level 1, 1 to 4 parcels and heights 6.0 to 26.8 m. Of the 21 set records, 12 had `b` equal to `a` and 9 had `b` = 0xffffffff, and the player's 14 of `1430` were a mix of industrial, commercial and residential. Over all 569 records, 253 had `b` equal to `a` and 316 had `b` = 0xffffffff, in all three towns. So `b` probably is the `stockList` of the API (a building that takes cargo has one; a house has none, written as 0xffffffff) and `a`, equal to it when there is one, would be the capacity entity that then doubles as the stock holder; this fits both ticked commercial buildings and all five houses, but only the 5 houses and the 2 commercial buildings were known by type. **Observed**, one game.
- **The five houses were not close together in the table.** The player ticked them "along the same street". Their record numbers were 34, 390, 462, 504 and 517 of 569 and three of them were in town 17,912 and two in 17,914, so neither the table order nor the `town` field puts them together. Either the street runs along a town border, or the `town` field is not the town the player means; which was not settled.
- **Save `1432` (clock still 11,324,600): two more houses.** Exactly 2 flags went 0 to 1, both records with `b` = 0xffffffff (houses), level 1, 1 and 4 parcels, heights 7.2 and 28.0 m, and again one in each of towns 17,912 and 17,914; 23 were set. The player's screenshots showed the window of such a house: its level (1) and year (1900), a "Noise" rating (Excellent), "Residents" (3 of 3) and the ticked "Historic Preservation" box. So a house's window has no input stocks or customers, which fits it having no stock entity in its record. The player had marked these along one street, yet again one is in town 17,912 and one in 17,914, as with the five of `1431`; whether the `town` field is the town the street shown belongs to is **Open**.
- **What the flag does in the game (screenshot only).** With the bulldozer over a stretch of road beside highlighted buildings, the tooltip read "Costs: $225,000", "Reputation: -4%" and "2 Historic Buildings Will Be Removed". The reputation figure matches the `DemolishedTownBuilding` penalty reason of the town states ([town-states.md](town-states.md)); the road cost includes the buildings. Save `1433` (clock still 11,324,600) is the same stretch after the player unticked those two houses: exactly those two records (the ones ticked in `1432`) went from 1 to 0 and nothing else changed, 21 flags remained, and the same preview read "Costs: $225,000" and "Reputation: -4%" without the historic line. So the flag is reversible with the same byte, the preview cost and reputation were the same with the two buildings historic and not, and the extra line is what the flag adds. Whether the actual demolition then costs or loses more with the flag on was not tried. **Observed**, one stretch.
- **The bulldozer takes a whole road segment (player's observation, not verified).** The player can remove only a whole segment of the street, not part of it, which would explain why the preview lists the buildings along the full stretch (the highlight in the screenshot runs from one junction to the next). That would make the street segment one entity, with the "Historic Buildings Will Be Removed" count taken over every building beside it.
