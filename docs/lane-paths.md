# Lane paths: the saved speed per path and the double slip switch

The save holds a table of path records, apart from the street-edge table: one kind runs along an edge, one lies inside a node. Each carries the path's own length and the speed its bend allows, which is the number the speed-limit layer shows. Labels as in [README.md](README.md#evidence-labels). Everything here is **Observed**: the records on 599 to 604 (catalog 6358716, 599; 6429368, 601; 6433541, 604, and a Giant temperate game of our own, 604); the slip switch in that game only, in four saves made one after another with the clock stopped. `tools/lane_paths.py` reads them.

## The records

A record starts with five `u32`: node, slot, node, slot, and the constant 2. The rest is floats, and three of them sit at the same place in every record seen:

| Float (counted from the first one after the five `u32`) | Content |
|---|---|
| 12 | the path's length in metres |
| 15 | the type's speed in m/s (27.78 for the 100 km/h rail type) |
| 16 | the speed the bend allows, in m/s; 213.9 (770 km/h) when nothing limits it, as on a straight path |

The first two floats are the position of a node of the path. The meaning of the others is **Open**, and so is the float after the bend speed (66 km/h on 683 of 743 rail edge paths read in the Giant game, the bend speed on a bent one).

- **An edge path** has two different nodes: the edge's end nodes in its direction. Between two nodes with two edges each, both slots are 0. Next to a junction the slots are not 0 (1 to 4 were seen), probably the edge's place in the node. Its length is the curve's own: 88.0 m for the 45 degree edges of the rail loop whose chord is 85.7 m, 80.9 m for a chord of 78.5. Edges next to a junction have a shorter length than their chord (6.0 m for a 23.5 m chord), which is **Open**.
- **A node connection** has the same node twice and two slot numbers. A node of four edges where two tracks cross has four, slots 0 to 1, 0 to 2, 0 to 3 and 0 to 4, each 4 to 11 m long; a node of three edges has two (0 to 1 and 0 to 2). What the slots count is **Open**.
- **Finding the table.** It lies far after the street-edge table. Search the stream for the five-`u32` head of a few known edges (node a, 0, node b, 0, 2); the hits lie together and the whole table is a few megabytes around them. Rail edges have one almost always (800 of 843 in the Giant game, 175 of them with a bend speed), street edges hardly ever (12 of about 6,000), and two catalog saves with no rail edges at all (6417290, 6417174) held none.

## The stored speed is the layer's number

The bend speed is saved: the lower number on a bent edge is not only worked out, as an earlier version of [road-speeds.md](road-speeds.md) said (the edge record itself holds only the type's speed).

- **It is the label before rounding.** Edge paths of the rail loop in the Giant game (screenshots of the layer, 604): stored 59.84 and 60.47 against the label 60, 54.47 against 54, 43.96 against 44, and the sharp spur's 43.89 and the shallow spur's 51.92 against 44 and 52. The labels are the stored values rounded to the nearest whole number (43.96 and 51.92 would read 43 and 51 if cut off).
- **The rule fits it.** With A in the rule of [road-speeds.md](road-speeds.md#bends-lower-it-slopes-do-not) taken from the stored value (A is v squared times the largest curvature of the Hermite curve through the end positions and tangents), the 15 rail edges of the Giant game under 100 km/h gave 2.45 to 2.54 for 14 of them (median 2.47) and 2.72 for a 3 m edge, whose label read 44 where the rule at 2.5 gives 42. In three catalog saves (6358716, 6429368, 6433541: 599, 601, 604; 59 to 107 such edges each) the implied A was never below 2.45 and its median 2.46 to 2.87, higher where an edge lies next to a junction.
- **One number can cover several edges.** The two edges of the sharp spur (23.5 m and 53.9 m, bends of 25 and 59 degrees) and the node between them all store 43.9, the shallow spur's three edges and their nodes 51.9. The edge-by-edge curvature gives 42.1 and 51.6, so near a junction the game's number comes from a longer path.

## The double slip switch (604)

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

## Open

- What the slots count, what the floats between the positions and the length are, and why edges next to junctions are shorter than their chord.
- Road edges: they have no path record of this kind, so where the bend speed of a road is saved, if it is, was not found.
- The other crossing in the loop's neighbourhood (another X, 8.6 degrees) was left at No and has four records, as the plain one did before.
