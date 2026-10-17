# Road network

The street-edge table (one record per road segment, with its two end nodes, their positions and its street type) and the other tables a road edit touches. What deleting a road, splitting one and building a new one did to them is in [road-edits.md](road-edits.md). All of it is **Observed** on 604, in one map editor game ([the Giant temperate editor game](test-games.md#giant-temperate-editor-game), eleven saves). [tools/street_edges.py](../tools/street_edges.py) lists the table and compares two saves.

## In short

All 604, mostly one map editor game; the rail part 568 to 601.

- **The street-edge table has one record per road edge, found by the repeated string `infrastructure/street/<folder>/<type>.street_template` (Observed, 604, 21,154 records in one stream).** A record is two end node ids, two end positions, two tangents, about 124 bytes of lane data, the street type, a zero and the base street type. The centre line is the cubic Hermite curve through the ends with those tangents (Observed, 599 to 604).
- **There is no separate node list: a node is the end of one or more edges, with one position everywhere it appears (Observed).** Node and edge ids are entity ids and are reused.
- **The table's first record follows a run of small counters, so a reader matching on the previous `.street` misses one edge per save (Observed, 568 to 604, seven saves).** `read_edges` finds it from the second record.
- **Rails are the same table, with `infrastructure/track/...` templates (Observed, 568 to 601, three catalog saves; 604 untested).** Curved lines are many short chords.
- **A road edit touches other tables: junctions, road-surface strips (keyed by edge id, only 161 of 358 edges paired by position), ground-texture polygons and the free-id list (Observed).**
- **What changes in the table when roads are built or deleted is in [road-edits.md](road-edits.md).**
- **Open:** what the lane block holds, whether the 100 m limit depends on the street type, why only some edges have a strip entry, and whether a road on water or a bridge shows in the same table.

## The street-edge table

**Observed, 604, eleven saves of one map.** About 1.6 MB into the stream (0.9 MB after the header), after the model and resource name tables, there is a run of records, one per road edge. Each ends with the edge's street type as text, so the run shows up as a repeated string `infrastructure/street/<folder>/<type>.street_template`. **Observed, 604:** its offset grows with the save (14.4 to 19.3 MB, 21,154 records, in a 946 MB stream). A record, all little-endian:

| Part | Content |
|---|---|
| `u32 a`, `u32 b` | The entity ids of the edge's two end nodes |
| `vec3 f32` twice | The end positions: x, y, z in metres, node `a` first |
| `vec3 f32` twice | The tangents at the two ends. For a straight edge both are the difference vector of the two positions (34.7, 48.2 for a 59 m edge). On a bent edge they differ from it, and the centre line is the cubic Hermite curve through the two positions with these tangents, a Bezier whose inner control points lie a third of each tangent in from its end (**Observed**, 599 to 604, checked in [edge-curves.md](edge-curves.md); [road-speeds.md](road-speeds.md#bends-lower-it-slopes-do-not) uses the same curve for the bend's speed) |
| about 124 bytes | Lane data, mostly not decoded; its sixth float is the type's speed in m/s ([road-speeds.md](road-speeds.md)). The lane count itself comes from the type's template ([street-templates.md](street-templates.md)) |
| `str` | The street type as `.../<type>.street_template` |
| `u32` | 0 |
| `str` | The base street type, `.../<base>.street` (`town_old.street` for `town_old_small`, `country_old.street` for the barrier road) |

A record starts right after the previous record's last string, except the table's first, which follows a run of small counters. **Observed, 568 to 604, seven saves** (mod.io 6098954, 6386889, 6401182, 6425796, 6436164 and two map editor saves of ours): a reader matching on the previous `.street` misses that first record, one edge per save. `read_edges` finds it from the second record: it starts 250 to 400 bytes earlier and its last string ends where the second begins. In one map it was the north arm of a town's main-street junction, so a four-way crossing read as a T with a separate piece 88 m north of it. Find them by the pattern: a `.street` string, then two ids and four vec3 whose first two have a sensible position and a length between 1 m and a few km, as `read_edges` does. The type is read from the template string that follows the lane data. Offsets move between saves.

- **What the unedited map held.** 359 edges (358 before the first record was read, see above): 335 of `town_old_small` and 24 of `town_old_xsmall`. 275 are 88 m long, the rest 64, 120, 56 or 24 m among others, so the towns' streets are laid out in edges of a fixed length with some shorter ones. The roads reach every part of the map (x from -8,445 to 9,016, y from -18,432 to 18,713), not one town.
- **A node's position is the same in every record that names it** (no disagreement over a metre in the first and the last save). The table has no separate node list: a node exists as the end of one or more edges. `street_edges.py --nodes` builds it.
- **Node and edge ids are entity ids and are reused.** A node id freed in one save became a node of a new road in a later one (see [road-edits.md](road-edits.md#what-the-edits-did)), and the id of a deleted road's edge became a node.
- **The type name carries a variant.** `country_old_small_barriers` (label Small Country Road With Noise Barrier) is a street type of its own. Its base type is `country_old`, and the barrier is not an extra record: no separate edge add-on or entity was added with it ([glossary.md](glossary.md#street-types)).

## Rails are in the same table

**Observed, 568 to 601, three catalog saves with rails** (mod.io 6098954 on 568, 6386889 on 599, 6401182 on 601). The 585 and 604 catalog saves and our own 604 saves checked had no track edge, so 604 is untested for rails. A railway edge is a record of the layout above whose template string is `infrastructure/track/<folder>/<type>.street_template` (types seen: `simple`, `standard` and `high_speed`, each also with `_catenary`; `simple` and `standard` in 6098954, `high_speed_catenary` in 6401182), not `infrastructure/street/...`. In 6401182 (14,336 m a side) the table held 8,282 road edges and 4,967 rail edges. Edges are straight chords as for roads, so a curved line is many short edges. `street_edges.py` reads both: `family` is `street` or `track` and `type` the last name. A turntable with stalls (6401182, 601, one place; which mod it comes from was not checked) is 20 `simple` edges of 48.1 m each, whose inner ends lie 16 to 19 m from a common centre and whose outer ends fan out, with no node shared by them: the ring is not in the table, only the stalls and the lead-in edges are. Bridges and tunnels have their own `infrastructure/bridge` and `infrastructure/tunnel` strings in the stream; how they attach to an edge was not read.

## The other tables a road edit touches

These were found by comparing the saves; the first two are written up less firmly than the edge table.

- **The junction table (Observed).** One record per node, holding its turns and, for a node with traffic lights, the light phases. The layout and what the deletes of `0643` to `0646` did to it are in [junctions.md](junctions.md#the-junction-record-604-observed).
- **The road-surface strips (Observed).** A table keyed by edge entity id holds, per edge, quads along the road in rows of two sides (a flag byte 0 or 1), about 8 m long and 18 m apart, so an edge of 88 m has 11 per side. `street_edges.py --ids` pairs these with the street-edge records by position. The stub's entry (`0x7de1`) stays in the table in all later saves, 22 rows, though the road is gone. `0x2c123` (88 m) was replaced in `0646` by `0x21dcd` (7 per side, 55 m) and `0x1b50b` (4 per side, 32 m of the 55 m edge from `7a0e` to `85bf`), so the old entry was replaced by two. The country roads have no entries. The table has 334 entries and the street-edge table 358 edges, and only 161 pair up by position: the rest is **Open**.
- **The ground-texture polygons (Observed).** A list of polygons per `.gtex` texture (`infrastructure/street/shared/*.gtex` for roads, `buildings/...` for lots) holds the points of each road's surface and edge. In `0645` 175 points that lay along the stub (from (-3476, 12299) to (-3420, 12360)) were gone and about 580 new ones appeared at the junction, so this list follows a deletion at once. The deletion made the stream 57 KB longer, not shorter; about 35 KB of that sat in this list (the rest was not traced).
- **A list of free entity ids (Observed).** At the very end of the stream, a `vec<u32>` of tens of thousands of ids. In `0646` it held the stub's edge id `0x7de1`, the dead-end node `85be`, `85dc`, and near its end `0x9020` and `0x2c123`. The three nodes of the `0647` road, `7de1`, `85be` and `85dc`, left the list in that save, together with four other ids (what they are was not read), and the ids new in `0646` (`0x1b50b`, `0x21dcd`, `0x746b`, `0x731f`) had sat side by side in `0645`'s list. So new entities take freed ids from it. In `0654` the road of four edges took the first 13 entries of the list: the five nodes (first five entries, in drawing order), then `2a4e4`, `2a516`, `2a530` and `2a537` (the four edges' own ids: they fill the junction table's turn entries, about 1.73 MB into the stream; which id is which edge was not read), then `2a5bf`, `2a5e6`, `2a5eb` and `2a604`. Two of those four, `2a5bf` and `2a5e6`, were back in the list in the same save, at their sorted places in the long run, so 11 ids were kept; the list's count went from 56,925 to 56,915 (13 taken, three added: those two and `0x1141f`). The road of `0647` took three nodes, two edges and two ids that were not seen again, so a road of n edges takes n + 1 node ids, n edge ids and some extras. The list head is one ascending run of about 400 ids, then three ids (`2a286`, `2a3d6`, `2a41c`) and a long ascending run from 3; a newly freed id was appended after the three, not sorted in. In `0648` (a load and re-save with no edit) 17 ids were added to the list, in ascending order among its entries, among them the old T-junction node `2a78f` and the edge `0x9020`, both deleted two saves earlier, so some freed ids reach the list only when the game loads and saves again. The rest of the list's order was not checked, and is **Open**.

**Observed, 604, a second map.** Leftovers and a marker for most of them: [town-leftovers.md](town-leftovers.md).

## Finding a road in a save

1. Run `street_edges.py SAVE --near X,Y,R` with a coordinate. The town record holds no position ([town-records.md](town-records.md)), so start from a landmark: a bird flock from the animal list, or the end of a road already listed.
2. For a deleted road, compare with the save before: `street_edges.py --diff OLD NEW`. Do not rely on the table in the very next save ([road-edits.md](road-edits.md#what-the-edits-did)): the junction table and the ground polygons show a deletion first.
3. Place a screenshot with two known points. The table and the stream's polygons use the same x, y. In the screenshots of this series a stub's dead end was at the top and screen-right was the map direction (-0.87, +0.5), found from the main road's dead end.

4. Name a segment by its two end node ids in hex, `2a619>342aa` ([signals.md](signals.md) uses it): both ids are in every record and either order names the same edge. The edge's own entity id is known only where the strip table has an entry (above). `terrain_map.py --crop X,Y,R --mpp 1 --label A>B` writes that name along the edges asked for; label only the few that matter, as a curve is many short chords. **Observed**, one 604 save.

## Open

- What the lane block of the edge record holds (the lane count itself is in the templates, [street-templates.md](street-templates.md)), which leftover records a later edit clears, and whether the 100 m limit depends on the street type (four types were drawn).
- Why the strip entry of the stub stays (the junction table's open points are in [junctions.md](junctions.md#open)).
- Why only 162 of 359 edges have a strip entry, and what the other strip entries belong to.
- Whether a road drawn over water or on a bridge shows in the same table (a railway does, see above).
