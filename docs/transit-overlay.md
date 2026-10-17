# The Transit Overlay export in the game's log

A mod that prints the player's network, as text lines, into the game's log, and what those lines let us check in a save: a line's id and name, a stop group's id and the buildings in its catchment. Labels as in [README.md](README.md#evidence-labels). The mod is on mod.io (id 6449851) and on GitHub (`axelferb/Transport-Fever-3---Transit-Overlay`), MIT licensed; this note describes its output in our own words.

## In short

- **What it is (Observed, 604, one export of 477 lines).** The mod prints `TFO|` lines into the game's log: lines with their stop groups, stop-group catchments, towns, buildings, stocks, vehicle paths, street and track edges, and a terrain grid. It describes the running game at the click, so match it to the save made at that point and copy the log folder right after an export.
- **It gives what a save does not (Observed, one Tiny game).** A line's id and name, and the line-to-vehicle link: a line's id sits in its vehicles' records, not in the line. A stop group's id occurs once or twice in the stream.
- **Catchment (Observed).** The passenger layer's disc has the group's radius (175 m for both stops, fitted 170 to 191 m), and the group's `C` records list the buildings whose origin lies within about 190 m of the centre.
- **Open.** What the second query form `K` adds, what the three numbers in `D` mean, whether `R` edge ids are street-edge-table ids, and whether the lot polygon touches the circle.

## Where the output goes

The button the mod adds (or a console command with the same exporter) prints lines that start `TFO|` into the game's log, the file [seed.md](seed.md#the-seed-in-the-games-log) names. The game rewrites that file, so **copy the folder it sits in right after an export** if you want to keep it. **Observed**, 604, one session: one export, 477 lines (341 of them the terrain grid), between `TFO|BEGIN|1` and `TFO|END|2`, taken at the last save of a series. The export reads the running game, so it describes the state at the time of the click, not a save; match it to the save made at that point.

## The records

**Observed**, 604, one export, checked against the mod's exporter source (read-only queries, one `print` per line). Fields are `|` separated; names have separators replaced by spaces; ids are plain decimal numbers; a long list is cut into chunks (400 ids, 150 buildings or 120 edges per line).

| Code | Holds |
|---|---|
| `L` | A line: id, name, colour, transport mode numbers, the stop group id of each stop, load slots any stop allows |
| `G` | A stop group: id, name, centre, catchment radius. The centre is the mean of its catchment positions, else of the stations' box centres |
| `C`, `K` | Catchables per group: group id, then ids, in chunks. `C` is the first query form, `K` the second; what the second adds is **Open** (the source does not say) |
| `T` | A town: id and name |
| `B` | Buildings: id, x, y, person capacity, its type (default -1), town id, the capacity entity's id; only buildings with a bounding box |
| `S`, `I` | Stock of a town building; an industry (id, position, level, name, stock) |
| `N` | Cargo index and name, from the game's cargo registry |
| `D` | Per town: slot 1 or 2, then `cargo:a:b:c` entries; what the three numbers are is **Open** |
| `R` | One per vehicle: line id, then the edge ids of its movement path with repeats removed |
| `E` | Street and track edges: id, both node ids, both end positions, tangents, `s` or `t` |
| `W`, `H` | Terrain grid header (origin, step, size, water level) and one row of heights per line (twice the height, rounded) |
| `ERR` | `TFO|ERR|section|message` |

`END` carries the number of stop groups. A line's `L` record shows no vehicle ids; the vehicles appear only through `R` (one record each, so a line with four buses printed four `R` records, two distinct paths of 36 and 13 edges).


## Open

- What the `K` records add to `C`, and the three numbers in a `D` entry.
- Whether the `R` edge ids are the ids of the street edge table.
- Whether a building's lot polygon, not its origin, is what the catchment circle touches.
- What the `0`/`1` word beside a line id in a vehicle record means.

## Evidence and tests

### What matches the save

**Observed**, 604, one Tiny subarctic game ([test-games.md](test-games.md#tiny-subarctic-bus-line-game)), one bus line between two towns, saves before and after its buses were bought.

- **A line's id sits in its vehicles' records, not in the line.** In the save with the line and no buses the line's id (7,096 in the export) was not found as a `u32` anywhere; with four buses it was found four times, one per bus, 1,581 bytes apart, each time in `u32` words `27`, the id, `0` or `1`, then two `0xffffffff` and `512` (the `0`/`1` took the values 1, 0, 0, 1 over the four; its meaning is **Open**). So the export gives the id to name link that [line-ids.md](line-ids.md) could only get from a warning, and the vehicle records give the line to vehicle link for lines with no cargo yet. Whether the `R` edge ids are the ids of the street edge table was not checked (**Open**).
- **The line took a free id below its stops'.** Its stop groups had ids 7,615 and 7,622 and the line 7,096 although made later, the same gap filling [editor-towns.md](editor-towns.md) found for towns.
- **A stop group's id occurs only once or twice** as a `u32` in the stream, a town's id dozens to hundreds of times (35 and 129 here).

### Station catchment

**Observed**, 604, the same game; the export's group radius is 175 m for both stops, and the passenger layer of the game draws the catchment as a green disc round the stop, with the buildings whose lot touches it highlighted (the player's observation: even part of a lot inside the radius counts).

- **The disc's radius is the group's radius.** 17 screenshots in the speed-limit layer with Areas set to Passengers were registered to the street edges (as [town-centre.md](town-centre.md) does for a name label) and a ground disc fitted to the green pixels. With the centre at the export's group centre the radius came out 170 to 185 m at one stop (6 pictures) and 174 to 191 m at the other (11), the fitted centres 2 to 12 m from the export's centre.
- **`C` lists the buildings the disc touches.** The group `C` records held 23 and 8 building ids, all of them ids of `B` records. Every building with its origin within about 190 m of the group centre was listed (23 of 23, 8 of 8) and none farther (the next ones lay 196 and 198 m out). A lot reaching into a 175 m circle puts its origin at most that far outside it, which fits 175 m plus about 15 m. The lot polygon was not tested against the circle (**Open**).
- **The maintenance and depot circles** have their own measurement in [models.md](depots.md).

The camera was not exactly straight down (it cannot be: [town-centre.md](town-centre.md#open) puts its lowest tilt at 5 to 12 degrees), and the fits implied 16 to 36 degrees of pitch from the ratio of their scales, which is rough. The registration fits a perspective mapping, so tilt is inside the fit, but the disc is drawn on hilly ground and its radius read on a flat plane, so the 170 to 191 m spread is about the size of what tilt and relief could do. The pictures were registered with a local script that is not in `tools/`.
