# Models: the model table and model instances

Two structures tie things on the map to 3D models: a table of every model the save can use, and a model instance record for each placed thing that has one. The animals ([animals.md](animals.md)) and the hot air balloon ([fun-elements.md](fun-elements.md#the-model-instance)) use them. The fields match the `ModelInstanceList` component and `ModelInstance` record in `api/tealdef` (a model id, the transform at the previous frame, the transform). **Observed** on 604 in eighteen test saves (the animal test series of [terrain.md](terrain.md#what-was-compared) and others).

## The model table

The first thing after the header ([header.md](header.md)): a `u32` count, then per model

```
str  source mod (empty for the base game)
str  path
u32  id
```

- The ids run 0, 1, 2 and so on in table order. They are the index into the table, and they depend on the models installed, so read them from the save and do not carry them from one save to another.
- The base game's 4,473 models come first, sorted by path, so the 28 models under `animal/` are ids 0 to 27. A mod's models follow, one run per mod in the order of the mod list, and carry the mod's id (a save with seven mods, [mods.md](mods.md#seven-mods-in-one-new-game), had 4,473 base models and 64 from six mods, and one of the seven added none): `urbangames_deluxe_upgrade_pack` adds 31, among them `animal/bison/bison.mdl`, `animal/boar_m/boar_m.mdl` and `vehicle/zeppelin/hot_air_balloon/hot_air_balloon.mdl`.
- An earlier reading as `u64 id, str path` fits the base game's models only because their source string is empty: the previous entry's id and the next entry's empty string make eight bytes. The three-field layout is the right one.

## The model instance record

Somewhere after the header (2.7 to 3.9 MB in the animal test saves) there is one record per placed thing that has a model: a `u32` count of instances, then the instances.

- An instance is 137 bytes. It starts with the `u32` model id, then two 4 x 4 `f32` matrices one byte apart, with the translation in floats 12 to 14. In the instances read, both matrices held the same translation. The other bytes of an instance are **Open**.
- In the animal records the count is one for the animal plus one per flock offset, and 9 bytes separate one record's last instance from the next count (146 bytes for an animal without a flock). The first instance's translation equals the animal's `worldPosition`.
- **Find a record** by searching for the 12 bytes of a known position (as `f32` x, y, z) and reading the model id as the `u32` 52 bytes before it. The balloon's record was found this way.
- The records of the animals are in the order of the animal list. A record for a thing that has left the map is gone: no instance used the balloon's model after it had flown off.

## Vehicles, people and animals in one run

**Observed** on 604, one game (the Small subarctic game of [finances.md](finances.md#a-first-build-out-row-by-row), two saves, 4 ships and 3 horse carts on the map). Vehicles do keep a model instance of the 146-byte kind above, one per vehicle, with its translation in floats 12 to 14. In the later save the run held 572 consecutive instances (stride 146, no gaps) and mixed animals, vehicles and people: an orca, the three horse carts (model `vehicle/road/truck/horsewagon_1850_v2`), the four ships (`vehicle/ship/british_columbia`), then runs of people (`characters/`) and coaches.

- **Find a vehicle** by its model: look up the model's id in the model table (the ships' id was 4192), then scan the stream for that `u32` followed by a 4 x 4 `f32` matrix whose floats 3, 7 and 11 are 0 and float 15 is 1. The four ships gave exactly four hits, 146 bytes apart.
- **Ships keep their order, and the order is the vehicle number.** Before sailing (a save with all four in the depot) the four instances held one identical position and heading, the ship depot's spawn point; later each had its own, so the slot order is stable. Slot 4 is Ship 4: the player described Ship 4 as inbound to the port with a full load, Ship 2 as at the dock and Ships 1 and 3 as empty and heading out, and the saved headings agree (below). The journal agrees as well: the vehicle running-cost bookings come in the same order ([finances.md](finances.md#running-costs-upkeep-loan-payments-and-income-over-ten-minutes)), and the fourth one sums to Ship 4's own figure. The slot with the ship at the dock sat at 410.8 and 4,986.7, 120 to 370 m from the carts at the nearby stop. **Observed**, one game with four ships.
- **Coordinates.** Values ran from -1,548 to 1,427 in x and -4,926 to 5,450 in y over the whole run, with ships at z = 0 (water level) and land things at 3 to 8. The map is 4,608 x 13,824 m, so the origin is probably the map's centre, not a corner. **Open** (no object near an edge was seen).
- The matrix's top-left 2 x 2 holds the heading as a rotation about the vertical axis, and the first row (floats 0 and 1) is the direction the ship faces. In the save the four ships read: slot 1, (1, 0) at x 1,108, y 4,152, the farthest from the port, facing east, away from it; slot 2, (0.27, 0.96) at the dock; slot 3, (0.14, -0.99) 380 m south of the dock, facing south, away from it; slot 4, (-0.99, 0.14) at x 613, y 4,950, facing west towards the dock at x 411. That is outbound, at the dock, outbound and inbound, as the player saw. **Observed**, one save. Slot 1 held the identity rotation exactly, which may only mean it faced due east.
- The second (previous-frame) matrix held the same translation and rotation as the first in all four ships, so the save, made with the game paused, gives no speed or direction of travel apart from the heading. **Observed**, one save.
- The 9 bytes between records and the other bytes of an instance are still **Open**.

This settles the question left in [entity-names.md](entity-names.md#not-found): a vehicle's position and model are in this run, though still not next to its entity id.
