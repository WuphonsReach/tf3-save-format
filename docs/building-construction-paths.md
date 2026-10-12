# Building construction paths

The construction path string the stream keeps for each town building, and what it gives that the building record ([town-buildings.md](town-buildings.md)) does not: the zone and the footprint.

## The zone and footprint from the construction path (604)

**Observed** on 604 in the Small subarctic game, saves `1035` (410 buildings) and `1824` (1,329). The stream holds one construction path string per building, `buildings/a/<zone><level>/<w>x<d>_<nn>/a_<zone>_l<level>_<w>x<d>_<nn>.con`, where the zone is `res`, `com` or `ind`, for example a 3 by 4 commercial building of level 1.

- **To find them,** search the stream for `.con` strings under `buildings/a/` (a `str`, u32 length then bytes). Among the eight `u32` words just before the length, one or two repeat a building's first id (`a`): the id appears twice, as in `i, id, i+1, id, i+2`, or once after other words.
- **The id is the record's first id.** In `1035` it matched exactly one of the 410 records for all 410 strings, and the second number of the footprint (`<d>`) equalled the record's `depth` for all 410. In `1824`, 1,242 of 1,329 strings had an id of that kind (the others were not looked at). So a building's zone can be read from its path, which no other place in the stream gives so far.
- **The zones in `1035`** were 223 `res`, 95 `com` and 92 `ind`.
- **The path's level is not the record's level.** In `1035`, before any rebuilding, 97 of 410 differed (path level 1 with record level 2 in 49, path level 2 with record level 1 in 48). The 262 + 51 that agree are not a rule. What each field means is **Open**.
- **`b` = 0xffffffff is not "a house".** Of the 223 `res` records 154 have it, but so have 38 of the 95 `com` and 31 of the 92 `ind`. It says only that the record has no second id of its own.

