# Road speeds: the speed layer's numbers

The number the game's speed-limit layer draws on each road or rail edge, where it comes from in the save, and the rule that lowers it on bends. Labels as in [README.md](README.md#evidence-labels). Everything here is **Observed** on 604 unless it says otherwise, from one Tiny subarctic new game ([test-games.md](test-games.md#tiny-subarctic-bus-line-game)) in three saves (town and country roads; a winding road of 21 new edges; 31 rail edges) and the player's screenshots of the layer, registered or matched to the edges: about 60 labels read by eye. The edge record itself is in [road-network.md](road-network.md).

## What the layer shows

- **One number per edge, at the edge's middle.** A long road drawn as several edges has a label per edge (80, 80, 43, 65, 80 along one bend). The build tool's tooltip shows the same number for each segment being drawn (27 on two segments), with each segment's slope (-2 and -5 percent) beside it.
- **The colour follows the number.** Pink at 30, purple at 50, blue at 80, in-between values in between, as the bar in the layer's window shows (green above that). Town streets of the `town_new_small` type were purple, `town_new_xsmall` pink, `country_new_small` blue.

## The stored speed is the type's

The sixth `f32` after the two tangents of the edge record (inside the lane data, 56 bytes after the record's first node id) is the type's speed in m/s, the same for every edge of a type, on street and track edges alike:

| Type | Stored | km/h |
|---|---|---|
| `country_new_small`, `ind_country_new_small` | 22.22 | 80 |
| `town_new_small`, `entrance_new`, `ind_entrance_new_country` | 13.89 | 50 |
| `town_new_xsmall` | 8.33 | 30 |
| track `simple` and `simple_catenary` | 27.78 | 100 |
| track `standard_catenary` (catalog 6098954, 568) | 44.44 | 160 |

An editor save with the older types gave 60 km/h for `country_old_small` and `town_old_large`, 40 for `town_old_small` and 20 for `town_old_xsmall`. The barrier road types hold nothing at that place, and nor do 4,929 of the 4,937 `high_speed_catenary` edges of catalog 6401182 (601; the other eight read 120 or 40): **Open**, where theirs is. A bent edge's record holds the same value as a straight one of its type; the lower number on screen is saved elsewhere, in a path record per edge ([lane-paths.md](lane-paths.md#the-stored-speed-is-the-layers-number)).

## Bends lower it, slopes do not

On a straight edge the label is the type's speed. On a bent one it is lower, and the numbers fit one rule on road and rail alike: the shown speed is the smaller of the type's speed and 3.6 times the square root of A divided by k, with k the largest curvature of the cubic Hermite curve through the edge's two end positions with its two stored tangents, and A near 2.5 m/s^2, rounded to a whole number.

- **Winding road (21 new edges, one save).** Read in order along it, 18 labels below 80 came out at 0.99 to 1.01 of the rule's value for 16 of them, and 0.975 for the two edges of the sharpest pair (27 against 27.7, bends of 99 and 69 degrees). The mean ratio was 1.000. Examples: 74 on two 19 degree edges, 59, 60 and 59 on three 45 to 51 degree edges, 36 on edges of 44 to 85 degrees, 27 on a 136 degree edge.
- **Earlier edges.** 29 on a 101 degree edge (0.98 of the rule), 46 on 55 degrees, 43 on 37, 56 on two 35 degree edges, 71 on 22 and 65 on 9 degrees gave A from 2.41 to 2.56.
- **Rail (31 edges, 19 of them below the type's 100).** The rule gave 54.2 for five edges of 21 to 36 degrees (labels 54), 62.8 to 63.4 for six (labels 63, 63, 62, 62, 63, 62), 72.2 for four 26 degree edges (72) and 82.2 for four 25 degree edges (82); straight and 13 to 15 degree edges kept 100.
- **A slope does not enter.** The rail edges slope from -8.4 to +5.1 percent: an edge at 100 slopes -8.4 percent, the edges at 54 slope -5 to -8 and those at 63 slope -4 to +3, with no pattern. On the winding road a -2 percent edge of 136 degrees fit the rule exactly, so the 0.975 of the sharpest pair is not a slope effect. This agrees with the player's view that a slope does not change the limit and that rail drops on bends as roads do. The rule uses the bend in the horizontal plane only.

Other measures of the bend (the radius from the chord and the turn, the curvature at the middle) did not fit: they gave A from 1.4 to 2.6 for the same edges. The game saves the number ([lane-paths.md](lane-paths.md#the-stored-speed-is-the-layers-number)), and the stored values answer two of these: the label is the stored value rounded to the nearest whole number, and the Hermite rule with A about 2.47 fits 14 of 15 rail edges under 100 km/h within 0.1 (the sharpest-bend 2 to 3 percent of the first fits were not seen again). What stays **Open**: why a 3 m edge reads 4 percent higher than the rule, how the number is computed across a junction (the pieces of a spur all store one value, 43.9 and 51.9 where the edge by edge rule gives 42.1 and 51.6), the other road families, and whether the vehicles drive at the number the layer shows.

`tools/edge_speeds.py` prints the stored and predicted numbers for every street edge of a save (`--family track` for rails, `--curved` for the lowered ones, `--near` for a place).
