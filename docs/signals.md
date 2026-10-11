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
- **The name is not here.** A signal's name (`<town> Signal <n>`, [entity-names.md](entity-names.md)) sits in the name table. The id of an existing signal occurs in about ten places of the stream, and none of them is the name table, so the link from id to name is **Open**. Two pairs were matched by position against screenshots: entity 221,428 was `Skipton Signal #14` and entity 196,859 was `Skipton Signal #13`. The player named both.

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

## Placing a stuck train (604, Observed)

The [stuck-vehicle table](notifications.md#bookkeeping-tables) of `1533` held 86 vehicles with a `problemSince` clock. For the 53 that had a `stuck_vehicle` notification the entry's timestamp was exactly the delay the bookkeeping note gives (300,000 units) after `problemSince`, so the delay holds on all 53. The oldest entries, in order of `problemSince`, matched the order of the queue the player read off the map (trains 95, 43, 82, 7, 45, 3, 85, 91).

A vehicle's position comes from its model instance ([vehicles.md](vehicles.md), [models.md](models.md#the-model-instance-record)); the link from entity id to instance is still **Open**, so a train was found by its model and its neighbours: the instance of its engine (`vehicle/train/class_prr_gg1`) with tram or truck instances at the distances the player's screenshots showed. Two engines were found this way, 300 m apart, with the 11 passenger cars of the first (`streamlined_nyc`, 26.1 m apart) between them and the second engine 14 m from the first train's last car. Instances sit near 220 MB into the stream here, so search the whole stream for the model id followed by a 4 x 4 matrix with its last float 1.0 and a translation inside the map.

## Open

- Where a signal's one-way flag, side and position along the edge are stored.
- What the 345 other edge records hold in place of the object list.
- Whether the removed-entities list takes every deletion, and why a deleted track edge stays in the table.
