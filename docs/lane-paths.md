# Lane paths: the saved speed per path and the double slip switch

The save holds a table of path records, apart from the street-edge table: the lanes along each street edge, a path along each rail edge, and connections inside nodes. A rail path carries its own length and the speed its bend allows, which is the number the speed-limit layer shows. Labels as in [README.md](README.md#evidence-labels). Everything here is **Observed**: the rail records and their speeds on 599 to 604 (catalog 6358716, 599; 6429368, 601; 6433541, 604, and a Giant temperate game of our own, 604); the kinds and the anchor on 568 to 605 (catalog 6090964, 568; 6426596 and 6429325, 604; the [Giga temperate game](test-games.md#giga-temperate-game-wr26a), 605); the slip switch in the Giant game only, in four saves made one after another with the clock stopped. `tools/lane_paths.py` reads the rail records (kind 2).

## In short

- **Path records of three kinds (Observed, 568 to 605).** The fifth `u32` of a record's head is its kind. Kind 3 is a lane along a street edge (four for most edges), kind 2 the path along a rail edge or a connection inside a node, kind 0 a connection inside a street node. Records name node ids and slots, not the edge's own entity id.
- **A rail path carries its bend speed (Observed, 599 to 604).** A kind-2 record holds the path's length, the type's speed and the speed its bend allows, in m/s; 213.9 means nothing limits it. Rail edges have one almost always.
- **Found by an anchor (Observed, 568 to 605).** Most kind-2 and kind-3 records follow two `f32` 1.0. The densest group of those is the table, about 95 % of the way into the stream, 2 to 11 MB long.
- **An edge with no lanes at either end is a leftover (Observed, 568 to 605).** Live roads and tracks have lanes at their end nodes; the roads and sidings of removed industries often do not. Deleted towns keep their lanes, so the test adds to the free-id list and does not replace it: [town-leftovers.md](town-leftovers.md#removed-industries-the-lane-test).
- **The speed-limit layer shows the stored number (Observed, Giant temperate game).** The label is the stored bend speed rounded to the nearest whole number, and the bend rule of [road-speeds.md](road-speeds.md) fits it. One number can cover several edges next to a junction.
- **The Double Slip Switch setting adds two node connections (Observed, one game, four saves).** They are the diagonals, with a bend limit as their speed; no street-edge record changes. The switch was not offered at about 24.7 degrees, so the limit lies between 20.1 and 24.7 degrees (Open).
- **Open.** What the slots count, what the floats between position and length are, whether a road's lanes hold its bend speed, what the short pieces on ids that name no node are, and the angle limit of the slip switch.

## The records

A record starts with five `u32`: node, slot, node, slot, and the kind. Records differ in length (gaps of 105, 109, 121, 125 and 137 bytes between neighbours are common) and do not keep to a 4-byte alignment, so a reader tests every byte offset.

| Kind | Head | What it is |
|---|---|---|
| 3 | an edge's two end nodes, a slot each | a lane along a street edge, spanning the whole edge: four for most edges, two for some, eight for a few |
| 2 | two different nodes | the path along a rail edge, one per edge (below) |
| 2 | the same node twice | a connection inside a node (below) |
| 2 | the same id twice, an id no edge names | short pieces of 1 to 8 m, the slot rising by one from piece to piece: **Open** (lanes inside stations or buildings is a guess) |
| 0 | the same street node twice, slots 0 and 1 | a connection inside a street node, 10 to 13 m |

Kinds 1 and 4 turn up a few dozen times per save, never between an edge's end nodes, and are read as chance matches of the head pattern (**Open**). The first four floats are the positions of the two ends (x, y each). The rest of this section is the kind-2 layout. Kinds 0 and 3 put their length elsewhere (float 8 and float 13 in the few records read; **Open**).

Three floats of a kind-2 record sit at the same place in every record seen:

| Float (counted from the first one after the five `u32`) | Content |
|---|---|
| 12 | the path's length in metres |
| 15 | the type's speed in m/s (27.78 for the 100 km/h rail type) |
| 16 | the speed the bend allows, in m/s; 213.9 (770 km/h) when nothing limits it, as on a straight path |

The meaning of the others is **Open**, and so is the float after the bend speed (66 km/h on 683 of 743 rail edge paths read in the Giant game, the bend speed on a bent one).

- **An edge path** has two different nodes: the edge's end nodes in its direction. Between two nodes with two edges each, both slots are 0. Next to a junction the slots are not 0 (1 to 4 were seen), probably the edge's place in the node. Its length is the curve's own: 88.0 m for the 45 degree edges of the rail loop whose chord is 85.7 m, 80.9 m for a chord of 78.5. Edges next to a junction have a shorter length than their chord (6.0 m for a 23.5 m chord), which is **Open**.
- **A node connection** has the same node twice and two slot numbers. A node of four edges where two tracks cross has four, slots 0 to 1, 0 to 2, 0 to 3 and 0 to 4, each 4 to 11 m long; a node of three edges has two (0 to 1 and 0 to 2). What the slots count is **Open**.
- **Finding the table.** It lies far after the street-edge table. Most kind-2 and kind-3 records follow two `f32` 1.0 (`00 00 80 3f 00 00 80 3f`). Search for that pair followed by a head that passes the checks (node ids under 2^24, slots under 256, finite positions, ends under 500 m apart), and group the hits with gaps under 1 MiB: the largest group is the table. Then scan a little past each end at every byte for the records without the pair. The float check matters: the Giga game's 1105-2304 holds runs of `(id, k), (id, k + 1)` at 403 to 419 MB with no floats after them, a look-alike that is not the table (perhaps vehicle routes).
- **The older way** searches for the five-`u32` head of a few known rail edges (node a, 0, node b, 0, 2) and takes a few megabytes around the hits. It needs rail edges: two catalog saves with none (6417290, 6417174) gave no hit, though the table is there. Rail edges have a kind-2 path almost always (800 of 843 in the Giant game, 175 of them with a bend speed), street edges hardly ever (12 of about 6,000): they have kind-3 lanes instead.

## The stored speed is the layer's number

The bend speed is saved: the lower number on a bent edge is not only worked out, as an earlier version of [road-speeds.md](road-speeds.md) said (the edge record itself holds only the type's speed).

- **It is the label before rounding.** Edge paths of the rail loop in the Giant game (screenshots of the layer, 604): stored 59.84 and 60.47 against the label 60, 54.47 against 54, 43.96 against 44, and the sharp spur's 43.89 and the shallow spur's 51.92 against 44 and 52. The labels are the stored values rounded to the nearest whole number (43.96 and 51.92 would read 43 and 51 if cut off).
- **The rule fits it.** With A in the rule of [road-speeds.md](road-speeds.md#bends-lower-it-slopes-do-not) taken from the stored value (A is v squared times the largest curvature of the Hermite curve through the end positions and tangents), the 15 rail edges of the Giant game under 100 km/h gave 2.45 to 2.54 for 14 of them (median 2.47) and 2.72 for a 3 m edge, whose label read 44 where the rule at 2.5 gives 42. In three catalog saves (6358716, 6429368, 6433541: 599, 601, 604; 59 to 107 such edges each) the implied A was never below 2.45 and its median 2.46 to 2.87, higher where an edge lies next to a junction.
- **One number can cover several edges.** The two edges of the sharp spur (23.5 m and 53.9 m, bends of 25 and 59 degrees) and the node between them all store 43.9, the shallow spur's three edges and their nodes 51.9. The edge-by-edge curvature gives 42.1 and 51.6, so near a junction the game's number comes from a longer path.

## Open

- What the slots count, what the floats between the positions and the length are, and why edges next to junctions are shorter than their chord.
- Road edges: whether their kind-3 lanes hold the bend speed, and the float layout of kinds 0 and 3.
- The kind-2 pieces on ids that name no node or edge (lanes inside stations or buildings is a guess), and whether kinds 1 and 4 exist at all.
- The other crossing in the loop's neighbourhood (another X, 8.6 degrees) was left at No and has four records, as the plain one did before.


## Evidence and tests

### The kinds and the anchor (568 to 605)

Read with a scratch reader that follows the section above (anchor group, then every byte), 2026-11-07. "Same id" counts kind-2 records that name one id twice: node connections and the short pieces together.

| Save | Version | Anchored records | Table at (share of the stream, length) | Kind 3 on a street edge | Kind 2 on a rail edge | Kind 2, same id | Kind 0, same id |
|---|---|---|---|---|---|---|---|
| catalog 6090964 (no rail) | 568 | 14,506 | 0.945 to 0.955, 2.3 MB | 7,162 | 0 | 11,638 | 1,102 |
| catalog 6426596 | 604 | 28,823 | 0.960 to 0.972, 4.4 MB | 10,516 | 705 | 25,300 | 1,278 |
| catalog 6429325 | 604 | 63,215 | 0.957 to 0.972, 9.9 MB | 17,182 | 2,018 | 62,910 | 1,116 |
| Giant subarctic editor map (`WR-2610`, 20261011-2107) | 604 | 32,287 | 0.965 to 0.972, 5.2 MB | 16,980 | 0 | 25,313 | 2,779 |
| Giga game, 1104-1947 | 605 | 62,672 | 0.958 to 0.969, 10.2 MB | 22,720 | 5,304 | 54,434 | 3,198 |
| Giga game, 1105-2304 | 605 | 64,645 | 0.959 to 0.970, 10.6 MB | 22,866 | 6,085 | 56,797 | 3,158 |

- **One group per save.** In every save above all anchored records fell in one group. tf3map's reader found the table at 0.95 to 0.96 of the stream, 1.5 to 10 MB long, in ten catalog saves (6090964, 6397880, 6416304, 6419141, 6423169, 6426596, 6429325, 6431269, 6433718, 6436878; 568 to 604).
- **Lanes per edge (1105-2304).** Street edges kept by the free-id list: 4 lanes (5,547 edges), 2 (171), 8 (11), none (72). Rail edges: one path (6,078), none (451). A kind-3 record's ends are about the edge's own length apart (median 78.5 m).
- **Not the edge's own id.** Of 1,031 edge ids the strip table gives ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)), 6 appear in the table, about what chance gives. The kind-2 same-id pieces (30,339 records on 8,090 ids in 1105-2304) are on ids that are neither node ids nor strip-table edge ids.

### The double slip switch (604)

A crossing of two tracks has a setting, Double Slip Switch, a drop-down in the crossing's window (No or Yes). It is stored as two more node connections.

| Save | What changed | Records at the node |
|---|---|---|
| parent | none (the crossing of two tracks, paths 8.3 degrees apart) | 4 |
| 1517 | slip set to Yes there | 6: the four and slots 1 to 4 and 2 to 3 |
| 1518 | a spur added from the main line, making a new crossing (24.7 degrees); the save's name says it is too sharp for a slip | 4, no slip |
| 1519 | a second spur, crossing at 20.1 degrees, slip on | 6 |
| 1520 | that slip set back to No | 4 |

- **Only the connections change.** No street-edge record is added, removed or changed by the setting (checked on the parent and 1517, and 1519 and 1520). The stream was 886 bytes shorter after the setting was turned off.
- **The two added paths are the diagonals.** Their stored speed is a bend limit: 72.08 km/h on both, 22.6 m long, at the 8.3 degree crossing, and 32.04 and 30.54, 9.4 m long, at the 20.1 degree one. The four plain connections of the first crossing hold 251 to 265 km/h, so nothing limits them.
- **The angle.** The switch was offered at 8.3 and 20.1 degrees and, going by the save's name, not at 24.7, so the limit lies between 20.1 and 24.7 degrees: **Open** (the angle is between the headings of the two paths at the node; the window of the 1518 crossing was not seen).
