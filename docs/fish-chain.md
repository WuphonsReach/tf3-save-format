# The fish chain read through the statistics lists

The fish chain of the [Small subarctic game](test-games.md#small-subarctic-game) followed from the fishing industries to the town buildings with the `items*` lists of [statistics-lists.md](statistics-lists.md), checked against the player's windows: three fishing industries, ship lines to one port, a warehouse and a road line into Todmorden. The game's cement chain, read the same way, is in [cement-chain.md](cement-chain.md). All 604, one game, so every label is **Observed** unless marked.

How to find a group and read its lists is in [statistics-lists.md](statistics-lists.md#finding-a-warehouses-stock). What the lists say about the industries themselves is in [industries.md](industries.md), and the spoiled counts in [spoilage.md](spoilage.md).

**Reading totals at a clock.** Most lists keep every entry from the start of the game, so one late save gives the whole history: read a list's total at any earlier clock as its last entry at or before that clock. The arrival and destination lists (`itemsAtStop<n>_c<cargo>`, `itemsAtDestination<cargo>`, `itemsAtEdge*`) keep only a recent window and start with a carried total ([the trucks note](fish-chain-trucks.md#the-same-chain-after-seven-trucks-replaced-the-carts-drained-stocks-a-second-stop-604)), so differencing them over yearly periods puts the whole carried total into one period.

## In short

All 604, one game, so every label is for that game.

- **Every window of the chain matches a statistics group (Observed).** A warehouse's stock is its unloaded total minus its loaded total; the port, each stop, the industries and the town stop each have a list whose total equals the figure in their window. Groups are found as in [statistics-lists.md](statistics-lists.md#finding-a-warehouses-stock).
- **An `itemsAtEdge<d>_c6` list is a running total of that cargo passing one point of the route (Observed; `d` probably the direction).** The step between neighbouring edge totals is fish in transit, so a stuck vehicle shows as a step growing past the baseline (about four carts, 16 fish, on a working route).
- **The fish a ship line carries equal the fish counted at the destinations (Observed).** The split is by destination, not by which ship line carried the fish. Which building owns a group is Open.
- **Fish leave the port's unloading without entering the warehouse (Observed).** Some of it when the warehouse is full, some when it has room (Why: Open). In the later reading it goes to town buildings through three other destination keys and is counted at the same time as the buildings' deliveries.
- **The stop arrival lists keep only a recent window and start with a carried total (Observed).** The window length is Open; differencing them by period puts the whole carried total in one period.
- **After trucks replaced the carts the chain drained** ([fish-chain-trucks.md](fish-chain-trucks.md)): the warehouse ran empty, the second stop stopped receiving fish, and the industries ran dry.
- **Open:** the road segment each edge group belongs to (the lists give totals and a last time, no position), and which fish a stop refuses.

## Evidence and tests

### A fish chain read end to end: windows, groups, a truck queue (604)

**Observed** on 604 in the Small subarctic game, in three paused saves a few minutes apart (clock about 14.9 million, 15.1 million and 15.6 million), with the player's screenshots of every window in the fish chain taken just before each save. The chain is three fishing industries, each with a ship line to one port, a warehouse by the port, and a road line of horse carts (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`, capacity 4, see [test-games.md](test-games.md#small-subarctic-game)) from a stop at the warehouse to a stop in town. Groups are found as in [Finding a warehouse's stock](statistics-lists.md#finding-a-warehouses-stock), with figures matched to the windows. One game, so every label is **Observed**.

#### Every window matched a group

| Window | Group (cargo id 6) |
|---|---|
| Warehouse | stock 496 = unloaded 1,536 minus loaded 1,040; incoming and outgoing bars equal the period differences of the two lists |
| Port | an unloaded list of 1,589 with a loaded list of 796 that stops growing at clock 11,271,000; its unloaded bars were read off the chart and match period for period |
| Warehouse stop on the road line | one loaded list of 1,045 |
| Town stop on the road line | one unloaded list of 1,024 and a loaded list of 132 that also stops at 11,271,000 |
| Fishing industries | produced 841, 748 and 463 with stocks 178, 98 and 22 |

- The industry stock rule held for the three fishing industries ([industries.md](industries.md#later-readings-the-fish-chain-before-and-after-the-trucks)).
- **A stop's loaded list can lead an industry's by one load.** The stop lists read 967 and 670 where the industries read 957 and 650, which fits a ship still loading at the pause (a load is 10 or 20 fish). The warehouse's loaded list and the road line's warehouse-stop list have the same 121 time stamps and differ at only three early entries (2, 2 and 1 fish more at the stop).

#### What reaches the warehouse and what does not

- **Where an unloading ship puts its cargo (player's observation, not tested here).** The player reports that a ship unloading at the port puts the cargo into the warehouse first, and only when that cannot take it does the ship hand cargo straight to buildings in range of the port. That fits the warehouse reading 445 to 456 of 500 while Ships 8 and 1 unloaded into it, spoiled fish included, with the stock below its cap. It would predict that once the warehouse is at 500 the port's unloaded figure stops matching the warehouse's incoming figure and the difference reaches the buildings' lists. A check: keep the warehouse full for one unloading and compare the port's Unloaded bar, the warehouse's Incoming bar and the consumers' `itemsUnloaded` lists before and after.
- The port's and the warehouse's unloaded lists have the same 111 time stamps, so one ship unloading is one entry in each. At 25 of them the port counted more than the warehouse (53 fish in all, 1 to 6 per entry).
- **13 of those 25 came with a full warehouse**: the stock before the unloading was 482 to 500 and ended at 500 to 509 (the lists stamp a load a little after the fish leave, so the end can pass 500). The warehouse takes what fits and the rest goes elsewhere, which agrees with the player's account that the warehouse comes first and buildings in range of the port take the overflow.
- **The other 12 came with room** (stocks of 160 to 481 before, 24 fish in all). So some fish leave the port's unloading without entering the warehouse even when it has space. Why (a building taking fish first, or an offset between the two lists' stamps) is **Open**.
- **Where the surplus lands was not found here** (found later: town buildings, through three destination keys, see [the reading at 54.6 million](fish-chain-trucks.md#the-fish-chain-at-clock-546-million-an-empty-warehouse-overflow-fish-to-buildings-604)). No building's `itemsUnloaded6` list has an entry at any of the 25 time stamps, and 40 building groups share stamps with the road line's deliveries. A third path, a truck loading straight from a ship, would show as stop loaded above warehouse outgoing; that gap is 5 fish, early, and none later.
- **The fish a ship line carries equal the fish at four destinations.** The ship lines' `itemsTransported6` totals (700, 362 and 152) add to 1,214, and four small groups with `itemsAtDestination6`, each keyed with a 5-digit number, add to the same: 1,024, 155, 22 and 13. The 1,024 is the town stop's unloaded total and its group's key (25,505 here) is probably that stop. The other three keys turned out to be where the port's surplus goes ([the trucks note](fish-chain-trucks.md#the-fish-chain-at-clock-546-million-an-empty-warehouse-overflow-fish-to-buildings-604)). After 490,000 more units the two sums still agreed (1,247 and 1,247) while the shares moved, so the split is by destination, not by which ship line carried the fish.
- **Small groups with `itemsTransported6` and `itemsLost6` break an industry's losses down by key.** One industry's `itemsLost6` total of 149 equals the sum of the lost totals of seven such groups (15, 31, 21, 36, 11, 23 and 12). The keys are 5-digit numbers. In the cement chain the same kind of group matched the consumer buildings one for one ([cement-chain.md](cement-chain.md)).
- **A group keyed like a line that holds one `itemsTransported6` list** matched each ship line's transported total (key 9,640 held 700, 30,784 held 362, 29,601 held 152). The keys were not tied to line names: the lines' name slots (1,293, 1,847 and 1,853) have no arithmetic relation to them, and the two bus lines' ids from [lines.md](lines.md) had no such group.

#### A stuck vehicle: the totals along the route show the queue

The player stopped one of the road line's carts (`horsewagon_1850_v2` and `horsewagon_1850_usa_v2`) for a while and saved (`1659`). Counts of fish in the lists, before and after:

| Point | Before | After |
|---|---|---|
| Warehouse loaded, and the stop beside it | 1,052 and 1,057 | 1,060 and 1,065 |
| `itemsAtEdge*_c6` groups upstream (five of them) | 1,044 to 1,052 | 1,048 and 1,060 |
| The town stop's unloaded total and its `itemsAtStop1_c6` | 1,036 and 1,040 | 1,040 and 1,040 (last time unchanged) |
| One `itemsAtEdge0_c6` group at the town end | 1,040 | 1,040 (last time unchanged) |

- **Each `itemsAtEdge<d>_c<cargo>` list is a running total of that cargo passing one point of a line's route** (`d` is 0 or 1, probably the direction). The groups hold one list each, with keys 0 or 16,777,216, and sit apart from each other. The upstream ones equal what the warehouse has loaded (1,060), the downstream one equals what the town stop has received (1,040).
- **The difference between neighbours is fish in transit.** 1,060 - 1,040 = 20 fish, five carts of 4, and the screenshot showed five carts at 4 of 4 in the queue. So a queue shows up as a step in the edge totals: the segment between the last edge still at the old value and the first at the new one is where the fish wait, and the size of the step is how many.
- Which edge group is which road segment was not worked out here. The lists give totals and a last time, no position, but the last times of a long run of edge groups trace a vehicle along the route ([cement chain](cement-chain.md)).
- **Spoilage while queued is in the vehicles, not in the lists.** Three of the queued carts showed 4, 4 and 3 spoiled of 4 aboard, with an age bar of 0 or 1%, and two showed none (one with a 3% bar). The `itemsAtStopUnsatisfied1_c6` list did not change ([unsatisfied-lists.md](unsatisfied-lists.md#the-15-spoiled-fish-a-candidate-group-and-the-warehouse-keeps-them)).

#### Releasing the stuck cart: the queue drains (604)

**Observed** in the same game, saves `1700` to `1702` (the cart released at `1700`, one cart at the town stop trying to unload at `1701`, `1702` made a few minutes later at 4x speed), compared with `1659`.

- **`1700` equals `1659` in every list read**: same fish totals, same last time (15,665,400 is the latest list time in both). The release changed nothing until time passed.
- **The queue shrinks from the downstream end, to the normal baseline.** Fish totals at the town stop and the downstream edges: 1,040 (`1700`), 1,049 and 1,052 (`1701`), 1,076 (`1702`). The upstream edges and the warehouse's loaded total stayed at 1,060 in `1701` and rose to 1,092 in `1702`. So the step between them fell from 20 fish (five carts) to 16 (four) while the warehouse kept loading: the queue drains slower than the warehouse refills it. The step does not go to zero on a working route: with nothing stuck (`1657`) the town stop had 1,024 and the warehouse had loaded 1,040, so about 16 fish (four carts) were always on the road. Read a queue as the step growing past that baseline (20 in `1659`), not as the step itself.
- **In `1701` the stop's arrivals led its unloaded total by what a cart still held.** The stop's `itemsAtStop1_c6` read 1,052 and its unloaded total 1,049, and the cart the player was watching held 3 of 4 (its window showed 3 spoiled) and was trying to unload. In `1702` the two were equal (1,076). That is the same offset as a ship still unloading ([statistics-bars.md](statistics-bars.md#a-small-new-game-one-fish-line-three-windows-604)), and it fits the player's reading that spoiled fish can sit aboard a cart at a stop. Not tested which fish were refused.
- An "unsatisfied" list appeared at the town stop as the aged carts arrived; it and what became of the spoiled fish are in [unsatisfied-lists.md](unsatisfied-lists.md#unsatisfied-counts-at-the-stops-604).
- **Later saves, the baseline holds** (`1705` and `1706`, clock 17.27 and 17.72 million). The warehouse's loaded total minus the town stop's unloaded total was 16 (1,146 against 1,130) and 15 (1,176 against 1,161), about the pre-jam 16, so the route had settled at four carts in transit. The upstream edge totals read 1,144 and 1,176 at the two saves, one to three loads above the downstream edge ones (1,132 and 1,164), the spread of the carts along the road.
- **The first bar of the 14th period carries a different date label (`1710`, clock 19,268,600, 7 May 1900 on screen).** Once the first fish moved after the boundary (20 in and 20 out at the warehouse, 20 unloaded at the stop), the bars appeared and the warehouse's tooltip read "Outgoing: 20 (4/1900)". Every earlier bar's tooltip reads "(1/1/1900)" and the three axis labels still read 1/1/1900. The 14th period began on 20 April, so the label is the calendar date of the bar's period start, in a month and year form, and the old bars say 1 January 1900 because the day table had no other day then. **Observed**, one chart.
