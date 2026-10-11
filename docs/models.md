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

**Observed** on 604, one game (the [Small subarctic game](test-games.md#small-subarctic-game), two saves, 4 ships and 3 horse carts on the map). Vehicles do keep a model instance like the animals' above (137 bytes, 146 apart with the 9 bytes between records), one per vehicle, with its translation in floats 12 to 14. In the later save the run held 572 consecutive instances (stride 146, no gaps) and mixed animals, vehicles and people: an orca, the three horse carts (model `vehicle/road/truck/horsewagon_1850_v2`), the four ships (`vehicle/ship/british_columbia`), then runs of people (`characters/`) and private cars (`car` models `coach_01` to `coach_03`, horse coaches).

- **A train is one instance per unit (Observed, 604, one train).** In an autosave of catalog game 6425796 a stopped passenger train (the `class_prr_gg1` unit at the front and 8 `streamlined_nyc` cars, the 8 the player's window showed) was nine instances in nine places of the run, not next to one another in it. The cars lay 24.8 to 25.6 m apart along the track behind the `class_prr_gg1`, all facing the way it did (-y, first transform row about -0.1, -1), so the facing is the direction of travel and the unit's length is not in the instance. [terrain_map.py](../tools/terrain_map.py) `--vehicles` draws each unit as a five-sided shape (a rectangle with a pointed front end).

How to find a vehicle's instance, and what a depot, a line, a purchase or a sale does to it, is in [vehicles.md](vehicles.md).

## Road maintenance buildings and depots: origin, facing, footprint and coverage

**Observed** on 604 in the Small subarctic game (save `1930`: eight maintenance buildings and two road depots; the footprint checked against the player's top-down screenshots of two maintenance buildings). Footprints, radii and pools are from the construction scripts in `base/content/depots/road.zip` (`road/road_maint_station.script.lua`, `road/road_depot/road_depot.script.lua`, `road/tram_depot/tram_depot.script.lua`).

- **One instance per building.** The models are `depots/road/road_maint_station/road_maint_station.mdl`, `.../road_depot/road_depot.mdl` and `.../tram_depot/tram_depot.mdl`. A road depot also has a `road_depot_sm` instance at the same point ([vehicles.md](vehicles.md) notes it), so count `road_depot` only. The translation is the construction's origin and the first two floats of the matrix (the "facing" that `tools/model_instances.py` prints) are the map image of the model's x axis. The model's y axis is that pair turned a quarter turn: for a facing (fx, fy) the point at local (a, b) lies at the origin plus a times (fx, fy) plus b times (-fy, fx).
- **The ground face is a rectangle in local coordinates, off centre from the origin.** Maintenance building 26.3 by 26.05 m (local x -12.5 to 13.8, y -15.0 to 11.05, centre about 2 m from the origin); road depot 56.2 by 40.0 m (x -17.7 to 38.5, y -20.1 to 19.9); tram depot 32.0 by 72.4 m (x -9.3 to 22.7, y -22.0 to 50.3). Drawn from the saved origin and facing, the maintenance face matched both screenshots (edges within about 5 degrees of the outlines, a corner touching the road at one building and a couple of metres clear at the other), and a road depot's entrance road ended at its face's edge. No tram depot was in the save, so that one is unchecked. Which way a building's front faces was not checked.
- **Each kind declares a catchment radius, a maintenance pool and the vehicle modes it serves.** The maintenance building: 600 m (the script's default; it can be overridden), pool 16, `BUS`, `TRUCK`, `TRAM`, `ELECTRIC_TRAM`. The road depot: 400 m, pool 12, `BUS`, `TRUCK`. The tram depot: 400 m, pool 12, `TRAM`, `ELECTRIC_TRAM`. So a depot has a pool for its own modes, and only the maintenance building serves buses, trucks and trams together. The other carriers have their own: rail depot 800 m, pool 6, and rail maintenance building 800 m, pool 12 (`TRAIN`, `ELECTRIC_TRAIN`); ship depot 1000 m, pool 8, and ship maintenance building 1400 m, pool 12; air: hangar modules of the airfield and airport 550 m, pool 16, and the heliport 800 m, pool 4. The 16 matches the "0/16" and "2/16" in the windows.
- **The modes are vehicle modes, not lane modes.** Street templates list `TRAM` and `ELECTRIC_TRAM` on tram lanes, and the rail track templates (`simple`, `standard`, `high_speed`, with catenary variants) list `TRAM_TRACK` and `ELECTRIC_TRAM_TRACK` beside `TRAIN`, so trams can run on rails. No depot script lists a `_TRACK` mode, so by the scripts a tram is served by mode and distance whichever it runs on. That the game really measures it so, and from the origin, is **Open**.
- **What decides which building a vehicle is listed under is Open.** A truck 504 m from one maintenance building and 411 m from another was listed only under the farther one.
