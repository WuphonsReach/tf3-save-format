# Lines and stop configuration

Where a line's stops keep their load and departure settings, and what a new line leaves in a save. Checked on 604 in one new game, two saves made minutes apart (`1246`, then `1312` with two new ship lines and edited stops), compared with the Configure Stop windows.

## The stop configuration record

**Confirmed** (604): every stop on a line has a record, found by this pattern:

| Field | Type | Meaning |
|---|---|---|
| 37 x | f32 | 1.0 in every record seen. **Open** (it is not the cargo load percentage, which is 100% in the window for a fish stop and absent for the stop that only unloads, and the floats are the same in both) |
| 3 | u8 x 3 | Flags: the first is "Force Unload All Cargo On Arrival" (0 or 1); the other two were 1 in every record, and are the window's "Destroy Cargo On Arrival When Config Changes" and "Replace with Newer Cargo if Available", both ticked by default (which byte is which was not told apart) |
| 3 | f32 x 3 | Minimum stop time, maximum stop time, maximum additional wait, in seconds |

The window lists them in the order Max. Additional Wait, Min. Stop Time, Max. Stop Time; the record stores min, max, wait.

- **Defaults.** A road line's stops held 0, 600, 30 (20 stops in the first save, so the window's default maximum stop time is 10 minutes and the additional wait 30 s), a ship line's 0, 600, 60 (the two stops of the fishing line).
- **One change per stop, tested in the game.** Two new fishing lines each had a fishing stop (loading fish, 100%) and the port stop. On the first the port stop had "Force Unload All Cargo On Arrival" ticked: its record is the only new one with the first flag byte 1 (`01 01 01`), and 4 of the old road stops have it too. On the second the port stop had custom times, minimum 3 s, maximum 3 min 48 s and additional wait 50 s: its record holds the floats 3.0, 228.0 and 50.0. The player made both edits and the window values match the bytes exactly.
- **Pattern.** 37 f32 values of 1.0, then three bytes (`00` or `01`, then `01 01`), then three floats between 0 and 3,600 that are not all 0. A looser pattern (any three flag bytes) gave over 1,200 false hits in the first save, almost all with zero floats, so check the flags and the floats. In the first save it found 22 records (nine lines), in the second 26: four new stops on two new lines.
- **What follows the three floats** differs by stop. The loading stops of all three fishing lines were followed by the same 4 bytes (`59 6b 00 00`), the port stops by `00 10 00 00 01 00 00 80 3f` and then a short list. The load list itself (fish 100%) was not decoded. **Open**.
- **Offsets move.** The records sit near 6.9 MB into a 79 MB stream, in a run ahead of the Lua states and the entity names. Find them by the pattern.

## A new line and its vehicles

**Observed** (604, `1246` against `1312`).

- Each of the two new lines was a fishing stop, then the port stop. The 37 floats of the fishing record and of the port record were 232 bytes apart; the port record of the first new line ran 13 bytes longer before the next line's records (245). Why is **Open**.
- The journal gained 13 `Vehicle purchase (Water)` bookings at the paused clock (5,997,000): 5 of -438,912 (Ship 7 to 11, on the first new line) and 8 of -256,032 (Ship 12 to 19, on the second). Their sum, 4,242,816, is the fall in the account between the saves. The first build-out's four small ships were 4 x 256,032 (the journal merges them to one -1,024,128). So the line with the larger ships paid 438,912 each and the line with the small ones 256,032 each. The larger ship cost 438,891 earlier in the same game ([finances.md](finances.md#a-new-games-journal)) and 438,912 here, 21 more, which was not explained.
- The names of the new lines and ships were appended to the entity names table, line first, see [entity-names.md](entity-names.md#renaming-industries-and-a-new-line-with-its-ships-604).
- The new lines' stops reuse the existing port stop. Nothing was added to the names table for them.

## A vehicle's line and the leg it is on (604)

**Observed** on 604 in the Small 1 : 3 game of [subsidies.md](subsidies.md#a-new-game-an-offer-its-expiry-and-an-accepted-subsidy-604), saves `1437` to `1441`. A bus line of two stops (named by its two towns) carried 80 vehicles in `1438`.

- **The records.** One array of 423 records, each five `u32`: the line's entity id, or `0xffffffff` for a vehicle that has none; two small numbers `a` and `b`; the vehicle's entity id; and 0. The count was 423 in all five saves while the set of vehicles in it changed, so the array is not one record per vehicle that exists. 297 of the 423 held `0xffffffff`. Find it by searching for a line's entity id (from a notification's `simParams.mapping`, [notifications.md](notifications.md)) followed by two small numbers, then a vehicle id and a zero, and step back and forward by 20 bytes while the shape holds.
- **`a` and `b` on a two-stop line are `(0, 1)` or `(1, 0)`**, and they flip as a vehicle reaches an end. In `1438`, 56 of the line's 80 records read `(0, 1)` and 24 read `(1, 0)`; in `1440`, 462 s later, 12 and 74. The three vehicles the player was tracking on the connecting road, heading for the line's second town, read `(0, 1)` in `1437`, `1438` and `1439` (clock 11,324,600 to 11,329,000, the player: "moved slightly towards" that town). The two of them still on the line read `(1, 0)` in `1441`. So the pair reads as the leg: the stop it left and the stop it heads for, counted in the line's stop order. **Observed** for the two-stop line only; I did not check the other direction against a description.
- **On lines with more stops** (an 18-vehicle line) the pairs were `(3, 1)`, `(1, 2)`, `(0, 3)`, `(1, 3)`, `(3, 0)`, `(2, 0)`, `(0, 2)`, `(1, 0)`, `(0, 1)`: not always consecutive stop numbers. What they count is **Open**.
- **Sending a vehicle to a depot.** The order itself changed nothing here: the vehicle (Road Vehicle 27) kept its record in `1439`, saved at the same clock as `1438` right after the order, with the same `(0, 1)`. It was gone from the array in `1440`, after it had driven off the line towards a depot, and in `1441` (parked in the depot) it was not in it. The 423-record array lost it and gained others, so the vehicle's entry is removed without the array shrinking. Where a depot-parked vehicle's data goes is **Open**.
- **A second list.** Another array of `[u64 clock][u64 vehicle id][u32 0 to 4]` entries (111 in `1441`, clocks from 11.9 to 13.4 million, some before and some after the save's 11,983,800) holds the same vehicle ids, and the same vehicle can occur twice. What it schedules is **Open**; it also lost Road Vehicle 27 between `1439` and `1440`.
