# Map editor saves

Checked on 604.

## Compared with regular saves

- Same container, same header layout, same settings keys.
- The setting `isMapEditor` is `true` (see [header.md](header.md), "Settings").
- Header money is 0 and the counter is low (0, 1024 and 1678 seen). The info table is empty.
- A different set of script states, and an empty `townStates` table.
- Town records are in the same layout, so the town component is not editor-only. The last 17 bytes of each record are zero.
- Starting cargo is in two places: the town record and the stock records of the town's existing buildings. Patching only the record changes the export and not the buildings ([building-stocks.md](building-stocks.md)).
- The entity data as a whole was not compared, so other differences are possible.

The game keeps editor saves in `save_maps/` and regular saves in `save/`, both under the game's `local/` folder in Steam userdata.

## Converting a regular save into an editor map

**Confirmed** once, on a 34-town, 53-industry save with a 618 MB stream:

1. Set `isMapEditor` to `true` in the settings. In the stream this is one byte (the boolean payload), so nothing moves.
2. Write the save back (see [container.md](container.md)) into `save_maps/`, with a copy of its `.jpg`.

The game lists it under Load Custom Map and opens it in the map editor. The Towns / Industries export works, with towns and industries at their positions. Money, journal, script states and the rest of the game state stay in the file. What the editor does with them is **open**.

tf3-save-editor's CLI can make the change: `tf3se-cli settings SAVE --set isMapEditor=true -o NEW.sav`.

## What editing in the map editor writes

Observed on 604, one Giant temperate editor map, twelve saves one change apart. Road edits (a deleted segment, a split road, a new road, a new street type) are in the street-edge table and the tables around it: [road-network.md](road-network.md). Ticking Historic Preservation on three buildings changed three flag bytes and nothing else in their records ([town-buildings.md](editor-map-buildings.md)). The animal list was the same in the saves compared, and changed by one bird's height after a town was deleted, so its positions can serve as landmarks. Deleting a town left its roads, buildings and town record in the stream ([road-network.md](road-network.md#deleting-the-town)).

### Loading an editor save and saving it at once

**Observed** on 604, once: a save loaded in the game and saved with no edit (`0648` from `0647` of the [Giant temperate editor game](test-games.md#giant-temperate-editor-game)). The header was the same in every field read (money 0, counter 1678, the 12 mods, the settings), the street-edge table and the animal list were identical, and the stream was 2,870 bytes longer. The differences were:

- A 4-byte value inside records of 12 bytes, over about 1.8 MB near the end of the stream (some 120,000 values), went from 8 to 10. What it counts is **Open**.
- In about 130 places in two tables in the middle of the stream a record of 40 or 27 bytes moved past its neighbours (the stream grew by its size at one point and shrank by it a record later), so these look like sets whose order changed.
- 17 ids joined the free-id list ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)).
- A block of Lua-encoded table data, 2.8 KB, was added at the end of the stream, with the keys `ProgressPage`, `saved` and `trackLists`; which state it belongs to was not checked.

So a load and re-save is not a byte copy, and a diff between an edited save and the one before it holds these changes too; compare with a no-edit re-save first.

### Save and play: from an editor map to a played game

**Observed** on 604, once (`0654` to `0656` of the [Giant temperate editor game](test-games.md#giant-temperate-editor-game)): the editor's Save and Play button saved `0655`, the game loaded it as a played game at 1x speed, and the player paused and saved `0656`. This was the first map-to-game cycle of the series. No road, building or town record was changed on the way.

- **`0655` is an editor re-save.** Header and stream length equal `0654`'s, `isMapEditor` still true, the calendar block at tick 0. Only 523 stream bytes differ: about 106 bytes (one byte, +1, here and there) in the 691,200-byte 640 x 360 preview image that opens the stream, a 4-byte value near the calendar block (70,815 to 72,493, not the header counter, meaning **Open**), and about 415 bytes of Lua-encoded script state (the Deluxe music mod's track time and index, and the name of one event handler in a list). The preview differs because it is a fresh screenshot of the same view.
- **`0656` header.** `isMapEditor` false; the money (0), start date, counter, mods and resources were the same as in `0655`, and the header grew by 49 bytes (see next).
- **A settings table gained a `company` entry.** At the start of the stream a small table of 4 bytes (a count of 0) in `0655` was 53 bytes in `0656`: one entry, `company`, holding `level` 1.0. A key `isMapEditor`, in a table about 695 KB into the stream (the next key starts with `locations.in`), went from 1 to 0 as well. A new company starts at level 1 ([company.md](company.md)).
- **The play clock.** `calendar_speed.py` read the date 1900-01-01, play speed 0 (paused) and 1,400 ticks since the day began; the editor saves said 0 ticks.
- **The town state table.** `town_states.py` read 0 entries in `0655` and 1 in `0656`, a town with authority 0.987; the table follows [town-states.md](town-states.md) (a played save holds an entry only for a town that has state).
- **The stream was 200,589 bytes shorter.** The street-edge table was identical (all edges, same ids). The shrink came as two stretches: about 139 KB lost in a table roughly 1 MB into the stream, after the resource-name tables, where the editor save kept long runs of fixed-size records and the played save kept lists of `u32` ids (for one edge model, a record list against a list of 19 ids), and about 62 KB lost further on (after 8.4 MB). Dozens of 5- to 24-byte in-place changes lay between. What these tables are, and whether the editor's extra bytes are editor-only data the game drops when it starts a game, is **Open**.


## A blank template and a road test

**Observed** on 604, one Tiny tropical map ([Tiny flat editor game](test-games.md#tiny-flat-editor-game)): the template as the editor saves it, and two saves made from it by hand.

- **The blank template holds almost nothing.** Counter 0, a 5.0 MB stream, no town records, no industries, no street edges and no parcel table (`street_edges.py`, `parcels.py` and `tf3save.scan_records` find none). The ground is the heightmap alone. Find a blank template by that: a map-size header with no town, edge or parcel table.
- **The first save after drawing is a different file in kind.** With two towns, three industries (a farm, a forest, a saw mill), a country road between the towns and short spurs to the industries, the stream was 13.9 MB, the counter 488, the street-edge table held 147 edges and the parcel table 1,474 parcels on 67 street edges. The header was otherwise unchanged, `isMapEditor` still true.
- **Drawing bypasses re-cuts the road they leave.** The next save added four new curves joining the country road at both ends, of the types `town_old_medium`, `town_old_large`, `town_old_small` and the `country_old_*_barriers` types, 53 edges in all. Eight of the 147 edges went and none of the others changed: the 80 m edges of the road at each junction were replaced by edges ending at the new junction nodes, with the same total length (80 + 80 became 95 + 65; 160 m between two old nodes became 71 + 89). The old road stayed in its place, so a bypass adds a path and takes none away. The parcel table was identical in both saves: the new roads ran through open ground and added no parcel.
- **A node id was reused (once).** The node at 591 m south of the origin in the first save was gone from the second, and the same id stood 790 m further south as a four-edge junction. Whether the game reuses the ids of removed nodes in general is **Open** ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches) holds the free-id list).

The edge layout and street types are in [road-network.md](road-network.md) and the glossary has the labels ([glossary.md](glossary.md)).

### A delete reaches the edge table with the next new road

**Observed** on 604, one Tiny tropical editor map, eight saves one step apart after the road test above: a save with no edit, a deleted road piece, a three-edge wide road drawn, its middle edge deleted, a short isolated road drawn, then a save with no edit, a deleted piece (the isolated road) and a save with no edit. (Another map: [road-network.md](road-network.md#what-the-edits-did).)

- **A no-edit re-save differs from its parent in the preview and about 13 small places.** The stream length was the same; the first 691 KB (the preview picture, 640 x 360 x 3 bytes) changed and under 200 other bytes in about a dozen short runs. The street-edge and parcel tables were identical.
- **A deleted road piece was still in the street-edge table in the save made seconds after the delete.** Three deletes (a piece of a 90 m town road, one of three 86 m wide-road edges, and the 34 m isolated road) had gone from the screen when the save was made, yet each edge table equalled its parent's. The first two edges went from the table in the save that also held the next new road. After the third delete, two saves (the second with no edit) still held the edge, so a save alone does not clear it; whether the next road drawn anywhere does is the likeliest reading, as both clears came with a road drawn 50 m or more from the deleted piece.
- **A counter beside the edge-addon names counts the deletes at once.** The table of `infrastructure/edge_addons/*.edge` names (`barrier_a.edge` and others, each with an index) is followed by a one-byte value that was 2 in the first three saves and went to 3, 4 and 5 in the saves made right after the three deletes, and in no other save. So the delete is recorded straight away, while the edge table lags. What the value counts is **Open**; find it from the byte after the name `barrier_track_b.edge` and a 20-byte run that starts `05 00 00 00 12 00 00 00`.
- **The new edge took the deleted edge's slot.** In both cases that had a new road the first new edge was written at the byte offset where the deleted record had stood (to a few bytes, the records differing in size); further new edges were appended at the end of the table.
- **The dead end stays.** The nodes at both ends of a deleted piece stayed in the table as one-edge nodes; nothing joined their neighbours.
- **A drawn road takes node ids from gaps.** The wide road's four nodes were three ids below the highest in use (in runs of unused ids) and one above it, so ids are not handed out in order. The isolated road's two nodes were both above the highest.
- **The junction table showed two of the three deletes at once** (`road-network.md` has its layout). Its record count followed the nodes drawn (178, 182, 184 patterns across the saves) and did not drop at a delete, because the dead ends stayed. After the first delete the record of the node between the deleted piece and its neighbour lost its edge id and its two turns (66 bytes to 26); after the second, the last two records (nodes of the wide road, from 6 turns to 0, 130 bytes to 22) lost all their turns and six other records held the same ids in another order (same length; which nodes they are was not read). After the third delete, of an isolated road, no record changed.
- **The strip table did not change in any of the eight saves** (64 entries, 1,297 rows): none of the roads drawn or deleted, country roads among them, touched it.
- **The parcel table did not change in any of the eight saves.** A deleted piece of a town road and roads in open ground touched no parcel.
- **Each edit made the stream 56 to 74 KB longer, in three places** (found by matching 48-byte anchors between neighbouring saves; the three saves after the first delete show the same three). First the ground-texture polygon list (`*.gtex` names, [road-network.md](road-network.md#the-other-tables-a-road-edit-touches)), 13.6 to 15.7 KB: a delete added the same 13,559 bytes of records twice, for two different edges (the first at a 90 m piece, the second at an 86 m one), and a drawn road 14.6 to 15.7 KB. Then two unnamed lists of binary floats, one about 7 KB at roughly 40 per cent of the stream and one 37 to 50 KB at 85 to 95 per cent, each growing in every edit. What they hold is **Open**. A save with no edit grew none of them, and the third delete (the isolated road) changed none of the three: its saves held the same polygon records and the same stream length to within 31 bytes.
