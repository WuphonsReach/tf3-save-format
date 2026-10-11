# Map editor saves

Checked on 604.

## Compared with regular saves

- Same container, same header layout, same settings keys.
- The setting `isMapEditor` is `true` (see [header.md](header.md), "Settings").
- Header money is 0 and the counter is low (0, 1024 and 1678 seen). The info table is empty.
- A different set of script states, and an empty `townStates` table.
- Town records are in the same layout, so the town component is not editor-only. The last 17 bytes of each record are zero.
- Starting cargo is in two places: the town record and the stock records of the town's existing buildings. Patching only the record changes the export and not the buildings ([building-stocks.md](building-stocks.md)).
- The entity data as a whole was not compared, so other differences are possible.

The game keeps editor saves in `save_maps/` and regular saves in `save/`, both under the game's `local/` folder in Steam userdata.

## Converting a regular save into an editor map

**Confirmed** once, on a 34-town, 53-industry save with a 618 MB stream:

1. Set `isMapEditor` to `true` in the settings. In the stream this is one byte (the boolean payload), so nothing moves.
2. Write the save back (see [container.md](container.md)) into `save_maps/`, with a copy of its `.jpg`.

The game lists it under Load Custom Map and opens it in the map editor. The Towns / Industries export works, with towns and industries at their positions. Money, journal, script states and the rest of the game state stay in the file. What the editor does with them is **open**.

tf3-save-editor's CLI can make the change: `tf3se-cli settings SAVE --set isMapEditor=true -o NEW.sav`.

## What editing in the map editor writes

Observed on 604, one Giant temperate editor map, twelve saves one change apart. Road edits (a deleted segment, a split road, a new road, a new street type) are in the street-edge table and the tables around it: [road-network.md](road-network.md). Ticking Historic Preservation on three buildings changed three flag bytes and nothing else in their records ([town-buildings.md](editor-map-buildings.md)). The animal list was the same in the saves compared, and changed by one bird's height after a town was deleted, so its positions can serve as landmarks. Deleting a town left its roads, buildings and town record in the stream ([road-network.md](road-network.md#deleting-the-town)).

### Loading an editor save and saving it at once

**Observed** on 604, once: a save loaded in the game and saved with no edit (`0648` from `0647` of the [Giant temperate editor game](test-games.md#giant-temperate-editor-game)). The header was the same in every field read (money 0, counter 1678, the 12 mods, the settings), the street-edge table and the animal list were identical, and the stream was 2,870 bytes longer. The differences were:

- A 4-byte value inside records of 12 bytes, over about 1.8 MB near the end of the stream (some 120,000 values), went from 8 to 10. What it counts is **Open**.
- In about 130 places in two tables in the middle of the stream a record of 40 or 27 bytes moved past its neighbours (the stream grew by its size at one point and shrank by it a record later), so these look like sets whose order changed.
- 17 ids joined the free-id list ([road-network.md](road-network.md#the-other-tables-a-road-edit-touches)).
- A block of Lua-encoded table data, 2.8 KB, was added at the end of the stream, with the keys `ProgressPage`, `saved` and `trackLists`; which state it belongs to was not checked.

So a load and re-save is not a byte copy, and a diff between an edited save and the one before it holds these changes too; compare with a no-edit re-save first.

### Save and play: from an editor map to a played game

**Observed** on 604, once (`0654` to `0656` of the [Giant temperate editor game](test-games.md#giant-temperate-editor-game)): the editor's Save and Play button saved `0655`, the game loaded it as a played game at 1x speed, and the player paused and saved `0656`. This was the first map-to-game cycle of the series. No road, building or town record was changed on the way.

- **`0655` is an editor re-save.** Header and stream length equal `0654`'s, `isMapEditor` still true, the calendar block at tick 0. Only 523 stream bytes differ: about 106 bytes (one byte, +1, here and there) in the 691,200-byte 640 x 360 preview image that opens the stream, a 4-byte value near the calendar block (70,815 to 72,493, not the header counter, meaning **Open**), and about 415 bytes of Lua-encoded script state (the Deluxe music mod's track time and index, and the name of one event handler in a list). The preview differs because it is a fresh screenshot of the same view.
- **`0656` header.** `isMapEditor` false; the money (0), start date, counter, mods and resources were the same as in `0655`, and the header grew by 49 bytes (see next).
- **A settings table gained a `company` entry.** At the start of the stream a small table of 4 bytes (a count of 0) in `0655` was 53 bytes in `0656`: one entry, `company`, holding `level` 1.0. A key `isMapEditor`, in a table about 695 KB into the stream (the next key starts with `locations.in`), went from 1 to 0 as well. A new company starts at level 1 ([company.md](company.md)).
- **The play clock.** `calendar_speed.py` read the date 1900-01-01, play speed 0 (paused) and 1,400 ticks since the day began; the editor saves said 0 ticks.
- **The town state table.** `town_states.py` read 0 entries in `0655` and 1 in `0656`, a town with authority 0.987; the table follows [town-states.md](town-states.md) (a played save holds an entry only for a town that has state).
- **The stream was 200,589 bytes shorter.** The street-edge table was identical (all edges, same ids). The shrink came as two stretches: about 139 KB lost in a table roughly 1 MB into the stream, after the resource-name tables, where the editor save kept long runs of fixed-size records and the played save kept lists of `u32` ids (for one edge model, a record list against a list of 19 ids), and about 62 KB lost further on (after 8.4 MB). Dozens of 5- to 24-byte in-place changes lay between. What these tables are, and whether the editor's extra bytes are editor-only data the game drops when it starts a game, is **Open**.

