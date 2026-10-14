# Junctions

The junction table (one record per road node: which turns the node allows) and the traffic-light block a record carries once a player sets up lights in the Crossing window. **Observed** on 604. The record layout was read in the Tiny subarctic bus-line game ([test-games.md](test-games.md#tiny-subarctic-bus-line-game)); the turn counts of the Giant editor game in [road-network.md](road-network.md) agree with it. The lights were seen only in the Tiny game, in six saves made one after the other with the clock stopped: lights on one junction (Type C), lights on a second (Type A), two more junctions with lights, the same save again with nothing changed, and one junction's six phases edited. The tool for finding the table and reading a record has not been written yet.

## The junction record (604, Observed)

The table is in the entity data, after the street-edge table ([road-network.md](road-network.md#the-street-edge-table)). It is a run of records, and its easiest handle is a 14-byte marker that repeats between them: `00 02 00 00 00 00 00 00 00 ff ff ff ff 00`. A record is:

| Part | Content |
|---|---|
| `u32 n` | The number of turns. A node where k edges meet has k x (k - 1), so 0 for a node of one edge, 2, 6 and 12 for 2, 3 and 4 edges |
| n x 18 bytes | A turn: `u32` edge id A, `u32` 1, `u32` edge id B, `u32` 2, `u16` 1. A to B, every ordered pair, so a default junction lists all of them |
| `vec<u32>` | Edge entity ids, see below |
| trailer | The 14-byte marker, or a signal block (next section) in its place |

- **The turn entries are edge to edge, not lane to lane.** The two constants (1 and 2) and the `u16` (1) held the same value in every entry of one save (156 records). Every record with a full edge list (below) listed each ordered pair of its edges, so no restricted turn was seen. Whether a lane connection edit lands here is **Open**: no save with one has been read.
- **The edge ids are not always filled in.** In the last save of the Tiny game 94 records had turns and an empty list, five had a list of one id with 2 or 6 turns, and 30 (nodes of 2, 3 and 4 edges) had the ids of exactly the edges their pairs name. The first save of the game already had 29 such full records, and the road the player then built between the towns (with a bridge) added 28 records of 2 turns, all with empty lists. The ids are entity ids, not positions in the street-edge table. Why a list is empty is **Open**.
- **What edits did (`0643` to `0646`, Giant editor game, Observed).** In `0643` a T-junction's record had 6 turns and three edge ids. After the stub road off it was deleted (`0645`) the same record had 2 turns and two ids, so the delete showed here at once, while the stub's own street-edge record stayed. A country road drawn from the main road (`0646`) gave the new node a 6-turn record, and the node where the main road was split a 2-turn one with the ids of the two halves.

## Traffic lights (604, Observed)

A node with lights has a signal block where the marker would be, and the next record starts straight after it:

```
00 00 00 00 00   u32 phase count   phase x count   u32 1 or ff ff ff ff   u8 1
phase: u32 k, k x u32 ids, f32 duration, f32 minimum duration, u8 skipping
```

Four 4-way nodes carried one in the last save. At the first junction the turn entries and the edge list were the same before and after the lights, and only the trailer changed.

**The ids.** A signalised 4-way listed 16 ids numbered 0 to 15, always as a permutation of the same set. Read from the order in the full lists: four groups of three (one per approach, probably the left, straight and right movement) and 12 to 15 for what look like the four crossings. In the default phases 1 and 3 hold two opposite groups each and the four crossing ids, phases 2, 4 and 6 hold all 16 and phase 5 the 12 vehicle ids without the crossings. The numbering depends on the node's edge order, so the same id is a different approach at each junction. What a listed id means (green, or allowed) is **Open**.

**The default phases** were the same on all four junctions, with the minimum 1.5 s throughout:

| Phase | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Duration (s) | 18.86 | 6.0 | 18.86 | 6.0 | 3.0 | 9.0 |
| Ids listed | 10 | 16 | 10 | 16 | 12 | 16 |

In the window, phases 1, 3 and 5 show a bright cross button and 2, 4 and 6 a grey one (what it does was not tested), and each phase opens with three rows: Duration, Allow Skipping (Yes or No) and Min. Duration. They are the stored `f32`, `u8` and second `f32`.

**The edit test** (all six phases of the fourth junction changed in one save):

| Phase | Duration | Allow Skipping | Min. Duration | Read from |
|---|---|---|---|---|
| 1 | 24.0 | Yes | 4.0 | window, save |
| 2 | 5.0 | Yes | 7.0 | window, save |
| 3 | 24.0 | No | 1.5 | save |
| 4 | 2.0 | Yes | 19.0 | save |
| 5 | 18.0 | No | 16.0 | save |
| 6 | 41.0 | Yes | 11.5 | window, save |

- The values are in steps of 0.5 s. The game did not hold the minimum below the duration (phases 2 and 4).
- Setting Allow Skipping to No greys the Min. Duration slider (player's observation). The stored value stays: phase 5 kept 16.0. Whether the game uses the minimum when skipping is off is **Open**; the player's reading is that it does not.
- The blocks of the other three junctions did not change in the save with the edit.

**Type A and Type C.** The lights window offers None and two types. The name table of the stream lists four model sets under `infrastructure/traffic_light/`: `traffic_light_a`, `traffic_light_c` and `traffic_light_dry_a` and `_dry_c`, each with a pole, a beam, a vehicle light and a pedestrian light and pole, so a type is a choice of model. The saves differ in one field only: the `u32` before the final byte of the block was 1 at the Type C junction and `ff ff ff ff` at the Type A one and at two more junctions whose type was not noted. The player reads Type A against Type C as the choice of light model. The pairing of the field with the type rests on one junction of each, so it stays **Open**.

## Open

- What a listed id means and which movement each of the 16 is, from the geometry of the node.
- Whether the minimum duration has an effect with skipping off, and what skipping does in play.
- Whether the final `u32` of the block is the type, and what the types look like in the entity data (model instances, [models.md](models.md)).
- Where lane connections are stored, if not in the turn table: a path record per connection inside a node, in a table of its own ([lane-paths.md](lane-paths.md)); a rail crossing's Double Slip Switch setting adds two of them. Whether a lane connection edit of a road lands there too is not known.
- Why the edge list of a record is empty for most nodes.
- Whether a junction with an empty edge list can carry lights, and what removing lights (the None button) leaves behind.
