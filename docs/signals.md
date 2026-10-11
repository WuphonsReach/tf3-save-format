# Signals

Where a rail signal is stored, what deleting one changes, and how a stuck train was placed on the map. **Observed** on 604, in one game: [catalog save 6425796](test-games.md#catalog-games-we-re-saved) re-saved five times as a test (saves `1533` to `1537`, one change each, the game paused, no mods). The save's own notes are in the [street-edge table](road-network.md); the [stuck-vehicle table](notifications.md#bookkeeping-tables) is where a jam shows first.

## The object list of an edge (604, Observed)

Each record of the street-edge table ([road-network.md](road-network.md#the-street-edge-table)) holds a list of the objects standing on that edge. In a record of the common layout it sits 60 bytes after the record's first node id, after four `ff` bytes:

```
ff ff ff ff   u32 count   count x (u32 entity id, u32 value)   u32 0
```

- **Rail signals are entries of this list.** 300 of the table's track edges carried one entry each in `1533`, and every value was 2. Street edges carry entries too (values 0 and 1, and two entries on 83 of them), which are other things standing on a road.
- **The list does not say where on the edge the signal stands, or on which side of the track.** An edge near the station was 81 m long and carried one entry, and signals stand mid-edge. The value was 2 for every signal seen, left or right, so it is not the one-way flag. Where the one-way flag, the position along the edge and the side are stored is **Open**.
- **About 345 edge records have another layout** (267 of them track) and were not read: the four `ff` bytes are not at 60. A signal on one would be missing from the 300.
- **The name is not here.** A signal's name (`<town> Signal <n>`, [entity-names.md](entity-names.md)) sits in the name table. The id of an existing signal occurs in about ten places of the stream, and none of them is the name table, so the link from id to name is **Open**. Two pairs were matched by position against screenshots: entity 221,428 was `Skipton Signal #14` and entity 196,859 was `Skipton Signal #13`. The player named both. A third pair, entity 383,977 and `Elba Signal #11`, is the signal built in `1544` (below).

## What deleting a signal changed (604, Observed)

| From to | Change | What the stream showed |
|---|---|---|
| `1533` to `1534` | one signal beside a stopped train's engine deleted | The 8-byte entry left its edge (count 1 to 0, record 8 bytes shorter). Edge count, endpoints and every other byte of the 12,374 records unchanged. The name table kept the name |
| `1534` to `1535` | a second signal deleted (221,428) | The same, on another edge. Nothing else moved |
| `1535` to `1536` | the signal 196,859 and the track edge under it deleted | The entry **stayed** in the edge record and the edge stayed in the table, though the game shows both gone after loading this save. See below |
| `1536` to `1537` | loaded and saved again, no edit | Nothing differed |

- **A signal edit while paused still runs a few ticks of the game.** In `1534` the train beside the deleted signal (an engine and 11 cars) moved 5.1 m forward and money fell by 1,255, with the same game date and header counter. `1535` had no vehicle moving and money down by 2,743. A diff after a signal edit therefore carries moves and costs that the edit did not store.
- **A list of removed entities.** Near 700 MB into the stream there is a list of `u32` entity ids. In `1535` it held the first two deleted signals, in the order they were deleted among unidentified ids, and in `1536` it also held 196,859, followed by 307,941. That id was in a record paired with the track edge's end node in `1535` and absent in `1536`, so it is probably the removed edge's own entity id (a guess). Whether every removal in the game goes into this list is **Open**.
- **A track delete is not in the edge table.** After `1536` the edge was still in the table with its signal entry, and the other 12,373 records matched `1535` byte for byte. The game rebuilds the section when it loads, or the table is not rewritten at once. **Open**.
- **The edge records did not merge.** The player expected a deleted signal to rebuild and merge the section; the table showed only the entry gone.

## Building track over the deleted section (604, Observed)

| From to | Change | What the stream showed |
|---|---|---|
| `1537` to `1538` | an 81 m `simple` track placed where the deleted track stood | The table kept 12,374 records and one differed: the stale edge, with the same two node ids and the same ends. Its type became `simple`, its object list empty (the signal entry gone), its speed 27.78 and the flag byte below 0x40 |
| `1538` to `1539` | catenary added to it | The same record again: type `simple_catenary`, flag byte 0xc1, speed unchanged at 27.78. The free-id list below was unchanged |

- **The stale edge was a live slot.** The new track took over the ghost record of the deleted one instead of adding a record, so the table does not show that the old track was gone. A reload had shown it gone in the game and kept it in the table (`1536`, `1537`).
- **After the object list: `u32 decoration count, items, u32 1, f32 speed`.** (The count was 0 on the edge in `1538` and `1539`; see the next section.) The speed is the edge's limit in m/s. In `1538` it read 44.44 on all but a few of the 5,602 `standard_catenary` edges and 27.78 on every `simple` and nearly every `simple_catenary` edge, so it follows the track type. The values below 44.44 on `standard_catenary` edges are not explained.
- **Then `4.0`, `0.53` and `01 80` and a flag byte.** It was 0x40 on the `simple` edge and 0xc1 after catenary was added, so it carries the electrified state (the API's `hasElectricTrack`). The later saves below confirm that the flag, not the type string, is the state: the type stayed `simple_catenary` while the flag fell back to 0x40 and the player saw the wire gone and the electrification view show the section in the other colour. That 156 `simple` edges in `1538` also carry 0xc1 is not explained (the type read from the string window may be wrong for them). Other bits are **Open**.
- **A list of free entity ids, used from the front.** Near the end of the stream there is a `vec<u32>` whose last 23,098 entries are an ascending run (3,877 to about 384,000) and whose first 21 to 28 entries are unsorted ids. Its count read 23,126 in `1538` to `1543`, 23,125 in `1544`, 23,123 in `1545`, 23,122 in `1546` and 23,121 in `1547`. The three deleted signals' ids and 307,941 are in the run. The signals built from `1544` on took the id at the **front** of the unsorted head: 383,977 in `1544`, 383,926 in `1546` (the front of `1545`'s list) and 189,237 in `1547` (the front of `1546`'s list), each then gone from the list and present in the edge record. The ids are not in order, so the head is a queue of recycled ids and not a counter (**Observed**, 604, three signals). Four ids from the front of `1545`'s head (383,928, 383,929, 383,931, 383,972) were out of the list in `1546` and back at its end in `1547`, and the `1545` count fell by two with only a barrier built, so building tools probably borrow ids and give them back. **Open**.

### Catenary, both sides, the outer side and a new signal (`1541` to `1547`)

| Save | What the player did | The edge record (the same edge `34250 > 33fb9`) |
|---|---|---|
| `1540` | barrier between the two tracks | decoration item `04 00 00 00 00`, flag 0xc1 |
| `1541` | tried to add catenary; the wire is not drawn on the section | item unchanged, flag 0xc1 to **0x40**, type string still `simple_catenary` |
| `1542` | tried a barrier on both sides; neither side shows one | decoration count 0, no item, flag 0x40 |
| `1543` | barrier on the outside of the double track; it shows | count 1, item `04 00 00 00 01` |
| `1544` | a two-way block signal near one end of the edge | object list `(383977, 2)`; every other byte of the record the same as `1543` |
| `1545` | a barrier added on the side between the tracks, so both sides have one | count 2, items `04 00 00 00 01` and `04 00 00 00 00`; flag still 0x40 |
| `1546` | a one-way signal added on the same edge (`Elba Signal #12` on screen) | object list `(383977, 2, 383926, 2)`; every other byte of the record the same as `1545` |
| `1547` | another one-way signal added on the same edge (`Elba Signal #13` on screen) | object list `(383977, 2, 383926, 2, 189237, 2)`; the rest of the record unchanged |

- **The item's last byte is the side.** It was 0 for the barrier between the two tracks and 1 for the outside. The other track lies on the right of the edge's `a` to `b` direction (north is +x, east -y, and the edge runs mostly east), so 0 matched the right side and 1 the left. One edge, **Observed**. The `u32` 4 stayed 4 for the same barrier, so it is probably the decoration's index (**Open** until a second kind is built).
- **Both sides are two items.** In `1545` (screenshots before and after with the noise barrier tool: the tool's panel gives Vehicle Noise -65% and says it blocks building) the count was 2 and the items were `04 00 00 00 01` then `04 00 00 00 00`: the outer side, which was already there, then the side between the tracks. The order matches the order they were built in, so the list is probably in build order (**Observed**, one edge). The attempt in `1542` left no item, so a both-sides command on an edge that already had one barrier did not leave one; what it did is **Open**.
- **Barrier and catenary.** In `1540` the barrier was added to an electrified section and the flag stayed 0xc1. In `1541` the catenary command left the flag at 0x40. Whether a barrier blocks the wire is not decided by one edge (the command itself may have toggled the wire off); a barrier on a `standard_catenary` edge elsewhere, and catenary built before the barrier, would test it.
- **A two-way block signal and a one-way signal are the same entry.** Both pairs have the value 2 and nothing else in the record changed in `1544`, `1546` or `1547`, so neither the one-way setting nor the block type is in the edge record's object list or the record (**Observed**, three signals). The new signals' ids gain no record elsewhere in the stream, so where the setting and the signal's position along the edge are stored is **Open** (see the next point).
- **A new signal is thin in the stream.** Its id (383,977 in `1544`, 383,926 in `1546`, 189,237 in `1547`) occurs in the edge record and nowhere new: 383,977 and 383,926 once in the stream, 189,237 also twice more, in places that already held it in `1545` (an id given up by an earlier entity), none created by the signal. An old signal's id occurs 5 to 55 times, in records with component-tag pairs (`0x12`, `0x13`, `0x14` each followed by an id). Those records may be written only after the game has run on; a save made after a few seconds of play would show it. **Open**.
- **The name slot of the first deleted signal was reused.** In `1543` the name table held `Skipton Signal #7` between a person's name and a `no name` entry; in `1544` the same place held `Elba Signal #11`. That fits the first deleted signal (entity 186,604, which the player had called "17") being #7. A screenshot of the new signal (made after `1544`) shows its on-screen name as `Elba Signal #11`, so the name in that slot is the new signal's (**Confirmed**, one signal).

### Switching the direction of a signal (`1548` to `1554`)

| Save | What the player did | The edge record |
|---|---|---|
| `1548` | `Elba Signal #12` (entity 383,926) switched from one-way to two-way (the on-screen icon of a block signal is three white dots, a one-way signal's one white and two black) | object list `(383977, 189237, 383966)`: the entry 383,926 is gone and a new one, 383,966, stands last; the rest of the record and the stream length unchanged |
| `1549` | `Elba Signal #12` set back to one-way | object list `(383977, 189237, 283537)`: the entry 383,966 replaced by 283,537, again last |
| `1550` | `Elba Signal #12` set to two-way again | object list `(383977, 189237, 383947)`, again a new id last |
| `1551` | `Elba Signal #13` set to two-way | object list `(383977, 383947, 383907)`: 189,237 replaced by 383,907, last |
| `1552` | `Elba Signal #13` set back to one-way | object list `(383977, 383947, 383931)`: 383,907 replaced by 383,931, last |
| `1553` | `Skipton Signal #12`, on the sibling track's edge `2a619 > 342aa`, set to two-way | that edge's list `(160715, 2)` became `(383926, 2)`; the Elba edge's list unchanged. The stream was 498 bytes shorter |
| `1554` | `Skipton Signal #12` set back to one-way | that edge's list `(383926, 2)` became `(82586, 2)`; the Elba edge's list unchanged |

- **Switching a signal's direction rebuilds it.** In `1548` the switched signal's old id was removed from the list and a new id appended at the end, so the list is not in position order. The new id, 383,966, was the front of `1547`'s queue; five ids left the front (383,966, 82,586, 245,853, 301,941, 306,872) and five were added at the back, 383,926 among them. The queue's count stayed at 23,121. The signal kept its name: `Elba Signal #12` stands at the same place in the name table in `1547` and `1548`. A signal's name is therefore not tied to its entity id (**Observed**, one signal). The one-way setting still did not show in the edge record: the pair's value is 2 for both (**Observed**, one switch). It is **Open** where the setting is stored; the stream was the same length in both saves, so it is a change of a few bytes in a place not yet identified, among the noise of a running game (hash-ordered data 43 to 102 MB into the stream reorders every save and about 25 million bytes differ).
- **Three saves of one signal, two-way, one-way, two-way (`1548`, `1549`, `1550`).** All three streams were the same length. Outside the header and the hash-ordered block, the places where `1548` and `1550` agree and `1549` differs are mostly runs of entries (an id and a small count, five bytes each) in the same members in another order: the lists reorder at each rebuild, so they follow the parity of the rebuild, not the setting. Left after dropping pure reorders, two single fields repeat in step with the setting: a `u32` of 597 (one-way) or 714 (two-way) at about 18.5 MB, in `6a 10 00 00  28 00 00 00  01 00 00 00  <value>  e8 26 00 00  96 00 00 00`, and a `u32` of 41,444 (one-way) or 41,281 (two-way) at about 222 MB, after `01 01 00 00 00` and before `6d 7d 02 00`. Neither is the id of a signal on the map. The first read 597 in `1537` to `1547`, including `1544` when a two-way signal was built, so it does not follow every signal's setting. It is a candidate for something about the signal switched last, not yet a found flag (**Open**). In `1551`, with `Elba Signal #13` also set to two-way, they read 325 and 41,445, a pair not seen before. So they do not hold one value per signal setting. They repeat exactly whenever the settings recur. With `#12` and `#13` the signals of the Elba edge and `S` the Skipton signal: all one-way read 597 and 41,444 (`1547`, `1549`); `#12` two-way, `#13` and `S` one-way read 714 and 41,281 (`1548`, `1550`, `1552`, `1554`); `#12` and `#13` two-way, `S` one-way read 325 and 41,445 (`1551`); `#12` and `S` two-way, `#13` one-way read 615 and 41,248 (`1553`). The signal on another edge changes them, and switching it back restored the old pair, so they look like a function of the settings of the signals on the map. What the numbers are (an index, a hash, ids of derived entities) is **Open**; so is how one signal's setting could be read from them. In `1553` `S` was entity 160,715, the only signal on its edge, which the player says holds it.

## Open

- Where a signal's one-way flag, side and position along the edge are stored.
- What the 345 other edge records hold in place of the object list.
- Whether the removed-entities list takes every deletion, and why a deleted track edge stays in the table until track is built over it.
- What the flag byte after the speed holds beyond the electrified state.
- What the two fields that change with the signals' settings (see the switching section) hold, and where each signal's own one-way setting is stored.
- The meaning of the decoration item's `u32` and trailing byte (index of the decoration, side).
