# Edge curves: a bent edge's centre line

How a road or rail edge's two stored tangents give its shape, and what was checked. Labels as in [README.md](README.md#evidence-labels). The record layout is in [road-network.md](road-network.md#the-street-edge-table).

## In short

- **The curve (Observed, 599 to 604).** The two stored tangents of an edge are the end derivatives of a cubic Hermite curve through the end positions; a straight edge's tangents equal the chord. Most edges are bent: 161 of 211 in one Tiny game.
- **Checks agree in three ways** (five catalog saves): the curve is smooth across two-edge nodes, a tangent's length is the edge's arc length, and the map picture comes out smooth. It is a fit, not the game's own function; the sharpest bends come out 2 to 3 percent off.
- **Some edges are S-bends (Observed, 568 to 604, 171 of 207 catalog saves).** Their tangents turn the curve to both sides of the chord, so its middle can lie on the chord while the rest bulges, up to 3.6 m on a 93 m edge. How far an edge leaves its chord is bounded by its two inner control points' distance from the chord, not by the middle's.

## The curve

**Observed**, 599 to 604. The two tangents of an edge record are the end derivatives of a cubic Hermite curve through the two end positions: a Bezier whose inner control points lie a third of each tangent in from its end. A straight edge has both tangents equal to the difference vector, so its curve is the chord.

Most edges are not straight. In one Tiny 604 game (a test save) 161 of 211 edges had tangents off the difference vector and 127 bulged more than 0.5 m from their chord, the most 14.5 m on a 43 m street edge.

**S-bends.** An edge whose tangents point to opposite sides of its chord crosses it. With equal tangents of the right size its middle lies exactly on the chord: for ends (0, 0) and (100, 0) and both tangents (100, 60), the middle is (50, 0) but the curve is 5.6 m off the chord a quarter of the way along. The curve stays inside the four control points' hull, so the inner control points' distance from the chord is an upper bound on the bulge; `street_edges.edge_is_curved` tests that.

## Evidence and tests

Five catalog saves of other sizes (mod.io 6358716, 599; 6417174 and 6429368, 601; 6417290 and 6433541, 604; 437 to 5,784 edges) agree in three ways:

- **Shared nodes.** Where a node has exactly two edges, the two tangents point the same way through it to within 1 degree at 98 to 99 percent of the 332 to 4,380 such nodes, and the rest are corners. The curve is smooth across nodes, as in the coast road of [road-edits.md](road-edits.md#what-the-edits-did).
- **Tangent length.** In 6429368 the mean of an edge's two tangent lengths over the length of the Hermite curve they define has median 1.000 (0.95 to 1.33 over 5,784 edges), so a tangent's length is the edge's arc length, where a straight edge's is its chord.
- **Picture.** `terrain_map.py` draws each edge as this curve. The slip roads and a rail curve of 6429368 and the rail loop of the test game come out smooth and meet at the nodes.

The curve is a fit, not the game's own function: the speed rule of [road-speeds.md](road-speeds.md#bends-lower-it-slopes-do-not) uses it too, and its sharpest bends come out 2 to 3 percent off.

**S-bends over the catalog saves** (568 to 604, 207 saves, 941,120 edges, 2026-10-23). 3,446 edges in 171 saves had the curve's middle within 0.25 m of the chord's middle but some point of the curve (sampled at 65 points) more than 0.25 m from the chord: rail types (`simple`, `standard_catenary`, `high_speed_catenary`) and roads (`highway_new_small`, the town types) alike. The worst were highway edges of 92.9 m in mod.io 6437710 and 6437866, whose middle was on the chord and whose curve was 3.6 m off it. In our own 18 saves of one Giant map, 27 edges were S-bends, the largest bulge 1.4 m. The control-point test marks 6 percent more edges as bent than the sampled curve does, edges that bulge less than 0.25 m.
