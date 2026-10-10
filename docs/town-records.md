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

- The town window of one town (a Small Village) showed a population of 281, "Earn 3,367 Experience Points" to the next level, and a supplies panel with passengers 0 / 281, fish 4 / 68 and fuel 0 / 97. Its fish and fuel icons are the only fish-and-fuel pair among the three records, so it is the third record, whose capacities are 282 / 209 / 275. The cargo told the towns apart, as above.
- The district-size chart of that town read about 281 residential, 203 commercial and 268 industrial. The record's 282 / 209 / 275 are close but not equal, so the record holds target capacities that sit a little above the sizes built. The chart was read by eye, so the differences are not exact. **Observed**, one town.
- The first float of the record was 1.0 for all four in all three towns, even though play had started (the 1.06 above came from a game played for a long time).
- The two floats in the last 8 bytes of the 78 (offsets 70 and 74) differed between the towns: 66.9 and 181.2, 63.0 and 138.3, and 66.1 and 3,555.6. The third town's window said 3,367 points to go, so 3,555.6 less 3,367 is 188.6, but nothing shows that this subtraction is meaningful. **Open**.
- Supply figures 68 (fish) and 97 (fuel) did not equal the commercial and industrial capacities (209 and 275) or any simple ratio of them (68 / 209 = 0.33, 97 / 275 = 0.35). Where they come from is **Open**.
