# Editor maps played in the game

Checked on 604. How an editor map becomes a played game (header fields: [header.md](header.md)): the editor's Save and Play button, and a flag flip made by hand on a copy. What the editor writes and how a map is converted the other way is in [editor-saves.md](editor-saves.md).

## In short

Both sections are single tests (Observed, 604), so this note is a log by nature. The conclusions:

- **Save and Play from an editor map** (Giant temperate game): the game loads the editor re-save as a played game; the header gains a `company` entry (`level` 1.0) and `isMapEditor` goes to false; the town state table gains an entry; no road, building or town record changes. The stream shrinks by about 200 KB in two stretches whose content is Open.
- **A flag flip by hand is enough (Tiny flat game).** Setting `isMapEditor` false in the settings and the stream byte made the editor map loadable and playable; the game added the `company` entry on the next save.
- **Open.** Whether the extra bytes of an editor save are editor-only data the game drops, why one map kept its start year and the other did not, and what the in-place hunks hold.

## Save and play: from an editor map to a played game

**Observed** on 604, once (`0654` to `0656` of the [Giant temperate editor game](test-games.md#giant-temperate-editor-game)): the editor's Save and Play button saved `0655`, the game loaded it as a played game at 1x speed, and the player paused and saved `0656`. This was the first map-to-game cycle of the series. No road, building or town record was changed on the way.

- **`0655` is an editor re-save.** Header and stream length equal `0654`'s, `isMapEditor` still true, the calendar block at tick 0. Only 523 stream bytes differ: about 106 bytes (one byte, +1, here and there) in the 691,200-byte 640 x 360 preview image that opens the stream, a 4-byte value near the calendar block (70,815 to 72,493, not the header counter, meaning **Open**), and about 415 bytes of Lua-encoded script state (the Deluxe music mod's track time and index, and the name of one event handler in a list). The preview differs because it is a fresh screenshot of the same view.
- **`0656` header.** `isMapEditor` false; the money (0), start date, counter, mods and resources were the same as in `0655`, and the header grew by 49 bytes (see next).
- **A settings table gained a `company` entry.** At the start of the stream a small table of 4 bytes (a count of 0) in `0655` was 53 bytes in `0656`: one entry, `company`, holding `level` 1.0. A key `isMapEditor`, in a table about 695 KB into the stream (the next key starts with `locations.in`), went from 1 to 0 as well. A new company starts at level 1 ([company.md](company.md)).
- **The play clock.** `calendar_speed.py` read the date 1900-01-01, play speed 0 (paused) and 1,400 ticks since the day began; the editor saves said 0 ticks.
- **The town state table.** `town_states.py` read 0 entries in `0655` and 1 in `0656`, a town with authority 0.987; the table follows [town-states.md](town-states.md) (a played save holds an entry only for a town that has state).
- **The stream was 200,589 bytes shorter.** The street-edge table was identical (all edges, same ids). The shrink came as two stretches: about 139 KB lost in a table roughly 1 MB into the stream, after the resource-name tables, where the editor save kept long runs of fixed-size records and the played save kept lists of `u32` ids (for one edge model, a record list against a list of 19 ids), and about 62 KB lost further on (after 8.4 MB). Dozens of 5- to 24-byte in-place changes lay between. What these tables are, and whether the editor's extra bytes are editor-only data the game drops when it starts a game, is **Open**.


## A converted editor map loaded as a played game

**Observed** on 604, once ([Tiny flat editor game](test-games.md#tiny-flat-editor-game); the map-editor side is in [editor-saves.md](editor-saves.md)): `tiny-flat-1x3 1963-place-random-forest-single-click-of-heavy-circle` from `save_maps/`, converted as above (`isMapEditor` false in the settings and in the stream byte, nothing else changed), put in `save/`, loaded, and saved after about two seconds of play (`1013-0514`, paused). **The game loaded it and ran it.** The Load Game dialog listed it as a manual save with the editor's calendar date (1901-03-23), population 488, 0 stations, lines and vehicles, money $0 and "Mods 0". It also showed "The map size is experimental." ([map-sizes.md](map-sizes.md#the-experimental-notice-in-the-load-dialog)).

Between the converted copy and the played re-save:

- **Header.** Start year 1901 became 1900 (the Save and Play map above kept its start year; why this one differs is **Open**). Date +1 day (1901-03-24); money 0 and counter 488 unchanged; the `info` table went from empty to one entry, `company.level` 1.0, so the header grew by 49 bytes, as in Save and Play. The preview is a new picture (645,116 of 691,200 bytes differ). `isMapEditor` and the settings were otherwise the same.
- **Calendar.** `calendar_speed.py` read play speed 1 and 3,800 ticks into the day before, play speed 0 (paused) and 1,800 ticks into the next day after, 2,000 ticks (2 s at 1x) apart. The day table went from 447 to 448 entries: an editor map keeps a day table from 1900-01-01 up to its own clock.
- **Stream.** 16,582,081 bytes became 16,585,083: 49 from the header, 2,953 in the body. Of the body, one stretch of about 800 KB (6% to 11% of the stream) changed in place with no size change, 180,000 small hunks, many of them +20 on one byte of a 4-byte value (floats or counters, **Open**); about 100 records of 500 to 570 bytes between 38% and 41% each changed 100 bytes in a regular layout (**Open**); the last 2% held Lua script state, with two inserts of 1 to 2 KB (one with the keys `cargosToDeliver`, `delivered` and `effectDuration`, which match a subsidy offer in [subsidies.md](subsidies.md)) and 32-byte inserts at five places. Which scripts those states belong to was not checked.

So the flag flip alone is enough to make an editor map loadable and playable: the game accepted this save without the `company` settings entry that Save and Play writes, and added the entry on the next save.
