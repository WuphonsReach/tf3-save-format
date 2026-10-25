# Signals

Where a rail signal is stored, what deleting one changes, and how a stuck train was placed on the map. **Observed** on 604, in one game: [catalog save 6425796](test-games.md#catalog-games-we-re-saved) re-saved five times as a test (saves `1533` to `1537`, one change each, the game paused, no mods). The save's own notes are in the [street-edge table](road-network.md); the [stuck-vehicle table](notifications.md#bookkeeping-tables) is where a jam shows first.

## In short

All 604, one game (catalog save 6425796 re-saved), so every label is for that game.

- **A rail signal is an entry of the object list in its street-edge record: `(u32 entity id, u32 value)`, value 2 for every signal (Observed, 300 track edges).** The list sits 60 bytes after the record's first node id, after four `ff` bytes. Deleting a signal removes the 8-byte entry and nothing else in the table.
- **The list does not say where on the edge the signal stands or on which side (Open).** A two-way block signal and a one-way signal are the same entry (Observed, three signals), and switching a signal's direction rebuilds it: the old id leaves the list and a new one goes last, while the name stays (Observed, one signal), so a name is not tied to the entity id.
- **A signal's name sits in the name table and the link from id to name is Open** (two pairs were matched by position against screenshots). A new signal reuses a free name slot (Confirmed, one signal).
- **A deleted track edge stays in the table until track is built over it (Observed).** The new track takes the ghost record's slot. The game shows it gone after loading, so the table is not rewritten at once or the game rebuilds the section (Open).
- **After the object list: `u32` decoration count, the decoration items, `u32` 1, `f32` speed (m/s), then `4.0`, `0.53`, `01 80` and a flag byte (Observed).** The speed follows the track type; the flag byte carries the electrified state (0xc1 electrified, 0x40 not), not the type string. In the record layout of [road-network.md](road-network.md#the-street-edge-table) these are the decoration list, the lane count and the one lane; the flag byte is the second byte of the lane's transport-mode word, whose ELECTRIC_ bits make 0xc1. A barrier item is `04 00 00 00 <side>` with side 0 between two tracks and 1 on the outside, in build order (Observed, one edge).
- **Free entity ids are a `vec<u32>` near the end of the stream, used from the front (Observed, three signals).** The front is a queue of recycled ids, not a counter; building tools probably borrow ids and give them back (Open).
- **A signal edit while paused still runs a few ticks of the game,** so a diff carries moves and costs the edit did not store.
- **About 345 edge records have another layout (267 track) and were not read,** so a signal on one is missing from the 300.
- **Open:** where a signal's one-way flag, side and position along the edge are stored; two fields (a `u32` near 18.5 MB and one near 222 MB) change as a function of the signals' settings, and what they hold is not known; whether the removed-entities list takes every deletion; what the flag byte holds beyond the electrified state; the meaning of the decoration item's `u32` (probably an index) and the other flag bits.

## The object list of an edge (604, Observed)

Each record of the street-edge table ([road-network.md](road-network.md#the-street-edge-table)) holds a list of the objects standing on that edge. In a record of the common layout it sits 60 bytes after the record's first node id, after four `ff` bytes:

```
ff ff ff ff   u32 count   count x (u32 entity id, u32 value)   u32 0
```

- **Rail signals are entries of this list.** 300 of the table's track edges carried one entry each in `1533`, and every value was 2. Street edges carry entries too (values 0 and 1, and two entries on 83 of them), which are other things standing on a road.
- **The list does not say where on the edge the signal stands, or on which side of the track.** An edge near the station was 81 m long and carried one entry, and signals stand mid-edge. The value was 2 for every signal seen, left or right, so it is not the one-way flag. Where the one-way flag, the position along the edge and the side are stored is **Open**.
- **About 345 edge records start differently** (267 of them track) and were not read here: the four `ff` bytes are not at 60. Their first two words are 1 or 2 and a small number, and the object list follows at the same place (Observed, 568 to 604, [road-network.md](road-network.md#the-street-edge-table)), so a signal on one is missing from the 300 only because this test skipped them.
- **The name is not here.** A signal's name (`<town> Signal <n>`, [entity-names.md](entity-names.md)) sits in the name table. The id of an existing signal occurs in about ten places of the stream, and none of them is the name table, so the link from id to name is **Open**. Two pairs were matched by position against screenshots: entity 221,428 was `Skipton Signal #14` and entity 196,859 was `Skipton Signal #13`. The player named both. A third pair, entity 383,977 and `Elba Signal #11`, is the signal built in `1544` (below).

## Evidence and tests

### What deleting a signal changed (604, Observed)

| From to | Change | What the stream showed |
|---|---|---|
| `1533` to `1534` | one signal beside a stopped train's engine deleted | The 8-byte entry left its edge (count 1 to 0, record 8 bytes shorter). Edge count, endpoints and every other byte of the 12,374 records unchanged. The name table kept the name |
| `1534` to `1535` | a second signal deleted (221,428) | The same, on another edge. Nothing else moved |
| `1535` to `1536` | the signal 196,859 and the track edge under it deleted | The entry **stayed** in the edge record and the edge stayed in the table, though the game shows both gone after loading this save. See [signals-tests.md](signals-tests.md#building-track-over-the-deleted-section-604-observed) |
| `1536` to `1537` | loaded and saved again, no edit | Nothing differed |

- **A signal edit while paused still runs a few ticks of the game.** In `1534` the train beside the deleted signal (an engine and 11 cars) moved 5.1 m forward and money fell by 1,255, with the same game date and header counter. `1535` had no vehicle moving and money down by 2,743. A diff after a signal edit therefore carries moves and costs that the edit did not store.
- **A list of removed entities.** Near 700 MB into the stream there is a list of `u32` entity ids. In `1535` it held the first two deleted signals, in the order they were deleted among unidentified ids, and in `1536` it also held 196,859, followed by 307,941. That id was in a record paired with the track edge's end node in `1535` and absent in `1536`, so it is probably the removed edge's own entity id (a guess). Whether every removal in the game goes into this list is **Open**.
- **A track delete is not in the edge table.** After `1536` the edge was still in the table with its signal entry, and the other 12,373 records matched `1535` byte for byte. The game rebuilds the section when it loads, or the table is not rewritten at once. **Open**.
- **The edge records did not merge.** The player expected a deleted signal to rebuild and merge the section; the table showed only the entry gone.

The building-over, catenary and direction-switch tests (`1537` to `1554`) are in [signals-tests.md](signals-tests.md).
