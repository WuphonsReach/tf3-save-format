# Edge curves: a bent edge's centre line

How a road or rail edge's two stored tangents give its shape, and what was checked. Labels as in [README.md](README.md#evidence-labels). The record layout is in [road-network.md](road-network.md#the-street-edge-table).

## The curve

**Observed**, 599 to 604. The two tangents of an edge record are the end derivatives of a cubic Hermite curve through the two end positions: a Bezier whose inner control points lie a third of each tangent in from its end. A straight edge has both tangents equal to the difference vector, so its curve is the chord.

Most edges are not straight. In one Tiny 604 game (a test save) 161 of 211 edges had tangents off the difference vector and 127 bulged more than 0.5 m from their chord, the most 14.5 m on a 43 m street edge.

## Checks

Five catalog saves of other sizes (mod.io 6358716, 599; 6417174 and 6429368, 601; 6417290 and 6433541, 604; 437 to 5,784 edges) agree in three ways:

- **Shared nodes.** Where a node has exactly two edges, the two tangents point the same way through it to within 1 degree at 98 to 99 percent of the 332 to 4,380 such nodes, and the rest are corners. The curve is smooth across nodes, as in the coast road of [road-network.md](road-network.md#what-the-edits-did).
- **Tangent length.** In 6429368 the mean of an edge's two tangent lengths over the length of the Hermite curve they define has median 1.000 (0.95 to 1.33 over 5,784 edges), so a tangent's length is the edge's arc length, where a straight edge's is its chord.
- **Picture.** `terrain_map.py` draws each edge as this curve. The slip roads and a rail curve of 6429368 and the rail loop of the test game come out smooth and meet at the nodes.

The curve is a fit, not the game's own function: the speed rule of [road-speeds.md](road-speeds.md#bends-lower-it-slopes-do-not) uses it too, and its sharpest bends come out 2 to 3 percent off.
