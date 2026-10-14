# Terrain edits

What sculpting the ground in the map editor changes in the save, and what it leaves alone. Checked on 604 in one editor map, an 18-town giant temperate map, by comparing the manual save made before a sculpting session with the one after it. The heightmap itself is in [terrain.md](terrain.md#the-heightmap).

## What a sculpting session changed (604)

**Observed**, one pair of saves. Between them the player dug a new river channel between two lakes and raised two hills beside it; the game's own screen was not photographed, so the shapes below are read from the saves.

- **Only heightmap values and a few parcel flags changed.** Of the 52.4 million grid points (80 by 160 tiles of 65 by 65, 4 m apart), 698,266 (1.3%) had a different value. The changes lay in a box about 5.4 km across (x from 2.3 to 7.7 km) and 4.6 km deep (y from -20.5 to -15.9 km) in the map's metres, and the sizes ran from -1,140 to +646 units, that is -57 m to +32 m at 0.05 m per unit. The box is not filled: a river channel and two hills fill small parts of it.
- **The picture shows it.** Drawn from the heightmap (`terrain_map.py --crop`, vector terrain with 5 m height lines, see [tools/README.md](../tools/README.md)), the new save has a channel from the north-west lake running south-east into the big lake and narrowing along the way, two new hills on its south side and a ridge on the far shore of the big lake. Nothing else in the picture moved.
- **The tiles still agree at their edges.** Each tile repeats the last row and column of its neighbour; in both saves all 25,360 shared edges matched, so the game rewrote the overlap on both sides of an edge it crossed.
- **Roads, buildings and stocks were not touched.** The street edge table (0 added, removed or changed by `street_edges.py --diff`), all 1,173 building records and all 599 stock blocks ([building-stocks.md](building-stocks.md)) were the same before and after.
- **The stream grew by 1,254,341 bytes** (400,046,708 to 401,301,049), and the heightmap sat 1,286,457 bytes later in the stream, so the extra data lies in front of the heightmap. A heightmap is a fixed size, so the growth is not the heightmap. What it is stays **Open** (the whole-stream differences of a manual editor save are noisy, see [building-stocks.md](building-stocks.md#method-pitfalls)).

## Parcel cells near the changed ground (604)

**Observed**, the same pair. Eight parcels on three street edges at the east end of the box, beside the shore, each lost the "something stands on the cell" bit ([parcels.md](parcels.md#the-flag-word)) on one cell: the flag word went 1 to 0 on the third face of five parcels and the fourth of two, and on the fourth face of an eighth that read `0 0 0 1`, and on no other parcel anywhere. No building was removed. Thousands of heightmap points within a few hundred metres of them had changed.

- **What follows:** ground edits can clear bit 0 of a flag word without a building going, so a 1 to 0 on a lone far cell is not a demolition. A deleted building clears its whole footprint, three or four faces on each of several parcels ([parcels.md](parcels.md#deleting-a-building-604)).
- **What decides it is Open.** The cleared cells were all deep in their parcels (the third and fourth faces) and near the shore, but the saves do not say whether the rule is the water's edge, the slope, or a tree that went with the ground.

## How to repeat the comparison

- Read the heightmap of both saves with `read_terrain` and `read_heightmap` of `tools/terrain_map.py` and compare the rows. Whole rows that match can be skipped, so a session of edits is found in a few seconds even on a 400 MB stream. A point (c, r) is at x = 4c - width / 2 and y = 4r - height / 2 (the map's centre is 0, 0), with the map's own width and height from the header.
- To look at the change, render both saves with `terrain_map.py OUT_DIR OLD NEW --crop X,Y,R --contour 5 --index 4` (add `--stream` for a stream already decompressed) and compare the two pictures. A crop of half-width 2,200 m at 4 m per pixel shows a channel of a few hundred metres clearly.
- The comparison needs two manual saves, one change between them. Autosaves from the same session carry more noise.

## Open

- What the extra 1.25 MB in front of the heightmap is, and whether it grows with the size of the edit (one edit was measured).
- The rule that clears a parcel cell during an edit.
- Whether sculpting under a building changes the building's `height` field (no building stood in the changed ground here).
- Whether the water level or the lake tables (the shape of a lake follows the heightmap in the pictures) store anything of their own that changes with an edit: only the heightmap was compared.
