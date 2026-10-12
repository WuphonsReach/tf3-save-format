# Parcels

The strips of ground along town streets where the town developer can put a building, and what the save keeps about them: a table of parcels with their cells, a flag word on each cell, and what bulldozing a building does to those flags. Checked on 604 in one game, the [Small subarctic game](test-games.md#small-subarctic-game), by reading its first save and seven later ones against the player's screenshots; labels are defined in the [README](README.md#evidence-labels). The building record that names parcels is in [town-buildings.md](town-buildings.md#the-record-and-how-to-list-it). [tools/parcels.py](../tools/parcels.py) lists the table and compares two saves.

## The parcel table (604)

**Observed** in eight saves of one game, from 1 January 1900 to 1920: one table holds every parcel, as a `u32` count followed by that many records.

```
u32  n                  the parcel count
n x
  u32  edge             entity id of the street edge the parcel runs along
  u8   left             1 = on the left of the edge, 0 = on the right
  f32  curve            position along the edge, 0 to 1
  u32  nFaces           4 for 7,282 of 7,327 parcels, 1 to 3 for the rest
  nFaces x
    u32  4              point count of the face
    4 x (f32 x, f32 y, f32 z)    the corners, in map metres
    u32  flags          0 to 3, see below
  f32  tail             8.0 for 5,281 parcels, 7.0 for 2,046
```

- **It matches the game's own component.** `Parcel` in the game's API (`api/engine.d.tl`) has a street segment, a left flag, a curve parameter, an offset and a list of faces, each with points and a collision map. The layout above reads them in a different order (the offset is probably the trailing `f32`; the two values seen are 8 and 7 metres, and what chooses between them is **Open**).
- **To find it,** search the stream for two `u32` fours in a row (the face count of a first record, then the point count of its first face). The count is 13 bytes before that pair. Many other places hold the same two words, so accept a hit only if `n` records parse in a row to the end (every point count 4, finite coordinates, flag at most 7). The table is 1.7 MB in the late save.
- **Where it sits moves.** 23.4 MB into the first save's stream and 53.7 MB into the last one, so describe it by that pattern.
- **A parcel is one cell wide and, usually, four deep.** Its faces are 8 by 8 m squares (86% of the 29,252 faces in the late save, 91% in the first one; the rest are skewed or shortened at junctions and road ends), stacked away from the street, so a full parcel is a strip 8 m wide and 32 m deep. The first face is on the street side (checked on two deleted buildings below, whose doors faced the street the first face touches).
- **Records come in runs, one run per street edge.** A normal 88 m edge has 22 parcels: 11 on one side (`left` 0), then 11 on the other (`left` 1), and `curve` falls from 0.95 to 0.05 in steps of 0.09 along each side, one step per 8 m. The late save has 388 edges in 485 runs (150 runs of 22, 29 of 21, the rest shorter), so some edges have more than one run. A short run is probably an edge cut short by a junction.
- **The table only grew in the tests.** The first save of the game (1 January 1900) held 2,543 parcels on 125 edges; the last one 7,327. The first 2,543 had the same edges, sides, positions and corners in both, and the new ones were appended after them. Whether deleting a road removes its parcels was not tested (**Open**).
- **The parcel's own entity id is not in the table** (see [Parcel ids](#parcel-ids-and-the-building-records) below).

## The flag word

**Observed.** Every face ends in a flag word, and only 0, 1, 2 and 3 occur: in the late save 4,797 faces read 0, 17,950 read 1, 6,487 read 3 and 18 read 2.

- **Bit 0 (value 1): something is standing on the cell.** Bulldozing a building changed that bit from 1 to 0 on the cells it had covered, and on no others (the tests below). It is not only buildings: a cell can read 1 with no building on it (trees are the likely cause, since a house deleted in the 1829 test left the cell behind its yard at 1; **Open**), so a 1 alone does not mean "built".
- **Bit 1 (value 2): another parcel overlaps the cell.** The game's collision map for a face has two entries, `Environment` and `Parcel`. Faces within 4 m of a face of a different street edge were 3,527 of 10,172 in the first save and 13,624 of 29,252 in the late one (a third to nearly half; they gather at junctions and bends), and 1,437 of the 1,669 faces that read 3 in the first save were among them. Value 2 on its own is rare (18 faces). The reading is **Observed** as a fit, not confirmed by a test that changes one overlap.
- **Flags move with the town.** Of the first save's 10,172 faces, 5,869 read 1 in both it and the late save, 1,633 went from 0 to 1, 70 from 1 to 0, 156 from 3 to 1 and 16 from 0 to 3, while 1,513 stayed at 3. The 0-to-1 faces are cells built on (or planted) in twenty game years.

## Deleting a building (604)

**Observed.** The player bulldozed one building at a time with the game paused, and each save was compared with the one before it. The game lets the simulation tick a little during a bulldozer action, so whole-stream differences are noisy; the changes below are only those in the parcel table, the building records and the ground-texture lists.

| Save | The building | What changed in the parcel table |
|---|---|---|
| `1011-1824` | a house | 2 parcels side by side on one edge, faces 0 to 2 cleared (6 cells), 16 by 24 m |
| `1011-1825` | another house in the same town | 2 parcels, faces 0 and 1 (4 cells), 16 by 16 m |
| `1011-1826` | the player ticked Historic Preservation on a commercial building | nothing (only the building record's flag byte changed) |
| `1011-1827` | that commercial building deleted | 29 cells on three street edges, about 960 m² once the overlaps are counted, 36 by 29 m across |
| `1011-1828` | a 1 by 1 commercial plot on a corner | face 0 of one parcel on each of two edges, the cells sharing a side, about 16 by 8 m |
| `1011-1829` | a small house, level 1, one resident, facing west-ish, next to the 1825 house | 1 parcel, faces 0 and 1 (8 by 16 m) |

- **A deleted building's record stays.** In all five deletions the building records (1,329 of them), their flag bytes and the ground-texture polygon lists were byte for byte the same afterwards. The Historic Preservation flag is kept too: the commercial building still showed it after it was gone.
- **The cleared cells are the footprint, yard included, not the lot.** The commercial building's record says 3 parcels wide and 4 deep (a lot of 768 m²), but its cleared cells covered about 960 m² on three edges, so the footprint can lie across parcels of different edges. The player's reading of the 1829 house: it was small enough to sit on the front cell of the two cells that cleared, or a 1 by 1 house whose back yard the game keeps clear so no building crowds it. Either way the flags record the space taken, not the roof.
- **The door side is the first face.** Checked on two buildings, where the first face of the parcel that cleared lay on the street the door faced: the 1828 plot's door faced the street a road vehicle (the player's Road Vehicle 49, in slot 14 of that save) was on, and that is the edge of the parcel that cleared on the plot's own side; the 1829 house's street side was at a compass bearing of about 304° from the cleared cells, north-west, which the player called west-ish.
- **An overlapped cell did not always clear.** In the 1828 test the cell of the other edge that lay on 58 of the 64 m² of the cleared one stayed at 1, so a building does not clear every parcel it overlaps. Something else on that ground (a tree stood just beside the plot) may hold it. The earlier idea that the flag says which of two overlapping parcels hosts the building is therefore **Open**.
- **A cell can read 0 inside a flagged parcel.** Parcel 1266 of the 1829 test read 1 1 0 1 before the house went: the cleared faces were 0 and 1, face 2 was already free and face 3 stayed at 1.

## Parcel ids and the building records

The `parcels` list of a building record ([town-buildings.md](town-buildings.md#the-record-and-how-to-list-it)) holds parcel entity ids. Which table position an id is stands **Open**; what is known:

- **An id is not a table position.** In the first save the building records name parcel ids from 6,544 to 26,038 for a table of 2,543 parcels, and no constant turns an id into a position over the whole table.
- **Inside a normal run the ids look consecutive.** On the four edges examined by hand, with a start chosen to make it work, a building's ids are consecutive numbers (ascending or descending) on one side of one edge, and no building's ids run over the break from one side to the other. That fits ids handed out in a block per run, with the block starting at `b` and the position within the run being `id - b`. The start `b` differs between runs: from the edge id it was +2 on one edge and, as candidates, about +4 on a second and +32 on a third, so it follows no rule from the edge id (the larger node id of the edge plus one fitted 65 of 388 parcel edges, 26 of those failing a position check, so it is not a rule).
- **Only one run was settled with a delete.** Edge 23710 (the 1824 house) fits `b` = 23,712: the house is the record with 2 parcels and depth 3, and the 4-wide, depth-4 building beside it has four cells with all four faces flagged. For the 1828 and 1829 buildings the start was a candidate only (the 1828 plot would be the one-parcel, depth-1 record `22884` on a start of 22,876), and an automatic search for the start of every run was too loose to trust.
- **A record is not paired with its ground-texture polygon by position.** The ground-texture lists (`buildings/a/...` textures, [road-network.md](road-network.md#the-other-tables-a-road-edit-touches)) hold about one polygon per building record (1,330 against 1,329), and in the first save their order and the records' order agreed on the town in 404 of 410 cases. By the late save only 754 of 1,329 agreed, so the two orders drift apart as the town is rebuilt. A record's parcel ids did not sit on its polygon's street run either.
- **Those polygons are not lots.** Most are a door patch of about 2 by 3.4 m and a path strip, and the 12 to 36 m squares among them are a minority. The number in a texture's name (`3x4`) does not give the size of the square it is drawn on. They carry the zone and level in their names (`a_com_l1`, `a_res_l1`), which is the only per-building zone seen so far, but without the pairing above no building is tied to one.

## Open

- **Which table position a parcel id is,** for all runs. A direct test is a deletion on a normal 22-parcel run beside a building whose record can be named, or a game where the town developer builds a single building between two saves.
- **Zone type per parcel** (residential, commercial, industrial): nothing stores it with a parcel. A building's zone is in its construction path ([town-buildings.md](building-construction-paths.md#the-zone-and-footprint-from-the-construction-path-604)), and a record names its parcels, so a built parcel's zone follows from that; an unbuilt parcel has none. The polygon names can still not be paired with a record.
- **What the second flag bit (`Parcel`) clears with,** and whether overlapped cells ever clear together.
- **What `tail` is** (8 or 7) and what chooses it, and whether `left` 1 is the left side of the edge as the API says. One edge was checked.
- **Whether a deleted road removes parcels,** and what a town does with parcels of a deleted building (the building record staying listed means the developer's own bookkeeping was not tested).
- **Whether the table is the same on other versions.** Only 604 was read.
