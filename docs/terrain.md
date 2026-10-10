# Terrain, the seed and the map sliders

What a save holds of the generated map, found by comparing saves of one seed. All of it is **Observed** on format 604 (Tiny 1 : 4, a 2 x 6 km map, start year 1900), from one save per case, so none of it is **Confirmed**. Sizes are counted from the end of the header (see [header.md](header.md)) to the end of the stream. The location of the heightmap is **Open**.

## What was compared

| Case | What changed from the one before |
|---|---|
| A | New game, seed `ktb5aEVwZg`, Lakes Medium, Rivers Scattered, Mountains Scattered, no mods. Saved at once. |
| B | The same seed and settings again. The game listed one mod (Deluxe Upgrade), so the mod list differs from A. |
| C | B with only Mountains moved to Sparse. |
| D | C with only Mountains moved to Packed. |
| E | D loaded and run to 12 Jan 1900 (4000 ms per day, 11 days), then saved paused. |

The header differs between cases only in the save counter and, between A and B, the mod list. The sliders do not show up there, so they are not stored in the header.

## Results

- **The same seed and sliders give the same bulk (A against B).** About 92% of the body matches byte for byte, including every large block. It shifts by a few KB at several points, where variable-length data differs.
- **A moved slider changes nearly all of it (B against C).** The first 283 KB after the header are identical. After that about 88% of the bytes differ over the next 6.2 MB, a stretch that has the same length in both saves. Later stretches shift by +207 KB and +116 KB, so C is 354 KB longer than B.
- **More mountains, more data (B, C, D).** The body is 14.64 MB for Scattered, 14.99 MB for Sparse and 16.96 MB for Packed. D against C first differs at the same place as B against C (byte 282,774), then shifts by +149 KB near 6.7 MB, -48 KB, -441 KB near 7.1 MB, and +2.0 MB twice from 13.1 MB.
- **Time changes only simulation state (D against E).** 258 of 4,140 4 KB blocks differ. They are one stretch of about 800 KB (four arrays of about 200 KB of tiny floats, around 1e-15, with long runs of one value) and six stretches of 16 to 33 KB. The same four arrays are the only large difference between A and B. The rest, terrain included, is identical.

## Thirteen 64-byte records (Open what they are)

About 283 KB after the header, after a list of model path names (one ends in `barrier_track_b.edge`), there is a run of 13 records of 16 little-endian f32. Fields by index:

| Index | Content |
|---|---|
| 0 to 2 | x, y, z in metres. x within about plus or minus 900, y within about plus or minus 3000 |
| 3, 4 | a pair of numbers, (0.44, 0.90) in B and D, (0.67, 0.74) in C, the same in all 13 records of a save |
| 5, 6 | a second x, y, 3.5 and 2.2 m from the first in B, C and D |
| 7, 8 | 4.5 and 1.396263 (80 degrees in radians) |
| 9, 10 | 1.0 and 1.0 in B and D, 0.8 and 0.8 in C |
| 13 | 0.05 in B and D, 0.04 in C |

Find them by the 8 bytes `00 00 90 40 c2 b8 b2 3f` at byte 28 of a 64-byte record.

- The 13 sit at nearly the same places in all four saves (about -600 / -2180, -424 / -1193, -865 / -743, -870 / -41 and so on). Against B, A is 2.6 to 6.3 m away for all 13, C is within 1 m for 11 and 400 to 550 m away for 2, and D is identical for 8 and 390 to 920 m away for 5. So the places are not simply fixed by the seed.
- **z follows the Mountains slider.** For the same place z was 154 m (B, Scattered), 123 m (C, Sparse) and 227 m (D, Packed). Over the 13 records z ranged 65 to 283 m in B, 65 to 163 m in C and 166 to 285 m in D.
- A has a different shape of record: other numbers in fields 3 and 4 (a direction that varies, such as (0.73, 0.69) and (-1.0, 0.07)), a second point hundreds of metres away, and fields 7 and 8 alternating 4.5 / 1.396 and 2.0 / 1.05. So these records are not simply fixed by the seed; whether the mod list or something else explains it is **Open**.
- A structure of the same size follows them, starting with an x, y, z near -568 / -2824.
- Not found in the two saves of another seed and format (Tiny 1 : 3, seed `RaazVnK55w`) by the pattern above.

They look like terrain-generator feature points (hills or peaks placed by the seed, with a height scaled by the slider), but that is a guess (**Open**). They are not the heightmap: 13 records cannot hold 2 x 6 km of terrain.

## Open

- Where the heightmap is. Not a smooth 16-bit grid that I could find; 1.5 MB to 6.1 MB after the header is float-like records (periods of 24, 72 and 73 bytes), and 6.4 MB, 6.9 MB and 7.2 MB are near-constant data.
- What the 13 records are, and why A and B differ.
- Whether the Ocean and Islands sliders change the same stretches as Mountains, and what Lakes and Rivers do.
- Whether the seed alone, with sliders at their defaults, gives the same map as the New Game screen.
