# Road speeds: the speed layer's numbers

The number the game's speed-limit layer draws on each road edge, where it comes from in the save, and the rule that lowers it on bends. Labels as in [README.md](README.md#evidence-labels). Everything here is **Observed** on 604 unless it says otherwise: the first game is a Tiny subarctic new game ([test-games.md](test-games.md#tiny-subarctic-bus-line-game); 158 street edges, 27 of them bent enough to be lowered), two crops of the layer in registered screenshots (a Kenzingen bend and the Kulmbach streets), plus the lowered labels found elsewhere in the pictures, about 35 labels read by eye. The edge record itself is in [road-network.md](road-network.md).

## What the layer shows

- **One number per edge, at the edge's middle.** In the pictures each label sat on the midpoint of its edge: a long road drawn as several edges has a label per edge (80, 80, 43, 65, 80 along one bend).
- **The colour follows the number.** Pink at 30, purple at 50, blue at 80, in-between values in between, as the bar in the layer's window shows. Town streets of the `town_new_small` type were purple, `town_new_xsmall` pink, `country_new_small` blue.

## The stored speed is the type's

The sixth `f32` after the two tangents of the edge record (inside the lane data, 56 bytes after the record's first node id) is the type's speed in m/s, the same for every edge of a type. All 158 edges of the first game read it:

| Type | Stored | km/h |
|---|---|---|
| `country_new_small`, `ind_country_new_small` | 22.22 | 80 |
| `town_new_small`, `entrance_new`, `ind_entrance_new_country` | 13.89 | 50 |
| `town_new_xsmall` | 8.33 | 30 |

An editor save with the older types gave 60 km/h for `country_old_small` and `town_old_large`, 40 for `town_old_small` and 20 for `town_old_xsmall`. The three barrier types (`country_old_*_barriers`) gave no speed at that place (**Open**: where theirs is). A bent edge stores the same value as a straight one of its type: the lower number on screen is worked out, not saved.

## Bends lower it

On a straight edge the label is the type's speed. On a bent one it is lower, and at six edges of the first game the numbers fit this rule: the shown speed is the smaller of the type's speed and 3.6 times the square root of A divided by k, with k the largest curvature of the cubic Hermite curve through the edge's two end positions with its two stored tangents, and A near 2.5 m/s^2, rounded to a whole number.

| Turn along the edge | Length | Label | A that gives it |
|---|---|---|---|
| 101 degrees | 49 m | 29 | 2.41 |
| 55 degrees | 68 m | 46 | 2.51 |
| 37 degrees | 48 m | 43 | 2.54 |
| 35 degrees (two edges) | 57 m | 56 | 2.56 |
| 22 degrees | 111 m | 71 | 2.53 |
| 9 degrees | 34 m | 65 | 2.51 |

The other labels read, about 25 in one crop of Kulmbach, were the type's speed as predicted: every town street at 50, the pink road at 30, the country road at 80. Other measures of the bend (the radius from the chord and the turn, the curvature at the middle) did not fit: they gave A from 1.4 to 2.6 for the same edges, a spread of nearly two to one. What stays **Open**: the exact measure the game uses (A runs 2.41 to 2.56, which is more than rounding allows for the sharpest bend, so it is not exactly this curve), whether it rounds or cuts off, how it treats junctions, rails and the other road families, and whether the vehicles drive at the number the layer shows.

**Reported by the player, not tested here:** the limit drops as a road bends and the same holds for rail, and a slope does not lower it. The rule above uses the bend in the horizontal plane only, so it agrees with the second part. No track edge was read: the tool takes street edges only, and no rail label was compared (**Open**).

`tools/edge_speeds.py` prints the stored and predicted numbers for every street edge of a save (`--curved` for the lowered ones, `--near` for a place).
