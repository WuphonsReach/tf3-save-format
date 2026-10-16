# Vehicle classes: carriers, power and load

How the game sorts its vehicles, and how `tools/vehicle_counts.py` turns a save's model instances into counts. Checked on the install that writes 604 saves (its vehicle model files) and on saves 568 to 604.

## Five carriers

**Confirmed against the install, 604 build; Observed in saves 568 to 604.** Every base-game vehicle model file has a `transportVehicle` block in its metadata, and that block names a `carrier`. There are five: `ROAD`, `TRAM`, `RAIL`, `WATER` and `AIR`. The game's own vehicle statistics (`base/vehicle_stats_data.lua` in `base/content/base.zip`) group vehicles the same way, one set of weights each for road, tram, rail and water, and two for air, aircraft and helicopters.

| Carrier | Folders under `vehicle/` | Vehicle modes | Plain words |
|---|---|---|---|
| `ROAD` | `bus`, `truck` | `BUS`, `TRUCK` | road |
| `TRAM` | `tram` | `TRAM`, `ELECTRIC_TRAM`; nine models also `TRAM_TRACK`, `ELECTRIC_TRAM_TRACK` | light rail |
| `RAIL` | `train`, `waggon` | `TRAIN`, `ELECTRIC_TRAIN` | heavy rail |
| `WATER` | `ship` | `SHIP`, `SMALL_SHIP` | water |
| `AIR` | `plane`, `helicopter` | `AIRCRAFT`, `SMALL_AIRCRAFT`, `HELICOPTER` | air |

- **The folder always agrees with the carrier.** Over the 355 model files of the vehicle folders (`base/content/vehicle/<folder>/<name>.zip`, one `.mdl` per car or part), the 306 that have a carrier fall in exactly the folders above, with no exception. The other 49 have no `transportVehicle` block and no carrier: the 46 private cars (`car`) and 3 zeppelins. A save records only the model path, so the folder is all it says about the carrier.
- **Trams run on rails.** The nine models with a `_TRACK` mode (`bombardier_k4000`, `caf_urbos3`, `car_go_tram`, `changchun3000`, `duewag_n8c`, `f_tram_univ`, `skoda_10t`, `stadler_citylink`, `toyama_8000`) are the ones that fit the track templates, which list `TRAM_TRACK` beside `TRAIN` ([street-templates.md](street-templates.md)). The other 46 tram models take only a tram lane in a street. That a line or a depot cares which of the two a tram uses is **Open** ([depots.md](depots.md) serves a tram by mode and distance, whichever track).
- **A street can carry a tram lane, or be tram-only.** Town street types in the install come in a plain form and in `_tram` and `_tram_electrified` forms; the forms with tram have tram lanes beside the car lanes. Three types (`tram_new`, `tram_old`, `tram_old_electrified`) have tram lanes and no car lane. **Observed**, one reading of the install's `street.zip` templates.
- **The player's five-way split is the game's.** Road, light rail, heavy rail, water and air are `ROAD`, `TRAM`, `RAIL`, `WATER` and `AIR`. Helicopters are `AIR`, in their own folder and statistics set. Whether one line can mix carriers (a tram and a train on shared stops) is **Open**: a line's record lists "transport modes" ([transit-overlay.md](transit-overlay.md)) but no save has been exported with a mixed line.

## Powered and unpowered units

**Observed**, install of the 604 build. A land vehicle model's `landVehicle.engines` list is empty for a unit with no engine of its own: every `waggon` (41 of 41), a tram's cargo or passenger wagon, and the middle and end cars of a multiple unit. Locomotives, power cars, buses, trucks, trams with a motor and every ship and aircraft have an engine (ships and aircraft carry `waterVehicle` or `airVehicle` data and no `landVehicle` list, so the tool counts them as powered).

A train or a tram is one model instance per unit ([models.md](models.md#vehicles-people-and-animals-in-one-run)), so a count of instances counts locomotives and wagons separately, which is what the summary does.

## Passenger and cargo

**Observed**, same install. The compartments of a model name the cargo classes they take (`cargoClassesIncluded`): `PASSENGERS`, or `UNIVERSAL`, `BULK`, `FLATBED`, `GOODS`, `LIQUID`. A unit with `PASSENGERS` only is `passenger`; any class but `PASSENGERS` and no `PASSENGERS` is `cargo`; both is `mixed`; no compartment (a locomotive, a steam tram) is `none`.

- `UNIVERSAL` is the class every cargo has beside its one specific class ([industry-chains.md](industry-chains.md#transport-class-of-each-cargo)), so a unit with only `UNIVERSAL` takes any cargo and one with `BULK`, `FLATBED`, `GOODS` or `LIQUID` takes only that kind. The aircraft with only it are freighters (`airbus_a310_300f`, `bae_146_cargo`, `boeing_737_700_cargo`, `douglas_dc10_30_cf` and others); a few old planes take both (`junkers_ju_52`, `short_330`, `bristol_freighter`). The Junkers F 13 (`junkers_f_13`) is `PASSENGERS` only.
- Nine tram models carry cargo: `cargo_a`, `cargo_b`, `cargo_c`, `freightcar_24s`, `f_tram_univ`, `car_go_tram`, `series_x`, `tatra_t4`, `double_horse`. Some are wagons, some powered.
- This is what a model can carry, not what a vehicle carries now.

## What the summary holds

`tools/mine_summary.py` (summary schema 7) has a `vehicles` block built by `tools/vehicle_counts.py`: for each carrier, the units by power (`powered`, `unpowered`, `unknown`) and load (`passenger`, `cargo`, `mixed`, `none`, `unknown`), the helicopters among the air units, the private cars and other town traffic as `ambient`, and `models_unread`. `index.csv` gets eight columns (units per carrier, the cargo-capable trams and aircraft, the unpowered rail units). The meaning of each is in [tools/README.md](../tools/README.md).

- **A mod's vehicle is counted by folder only.** The install has no file for it, so its power and load are `unknown`; a `waggon`-folder model is taken as unpowered. In catalog save 6409998, which has dozens of mods, 91 distinct models were read this way, 295 of its 973 units (power or load unknown), against none in 6431760 with two Urban Games packs. A summary built on a machine without the install classifies nothing by load.
- **Examples.** Catalog save 6431760 (format 601, 96 played periods): rail 538 unpowered passenger and 174 unpowered cargo units with 54 locomotives; tram 470 unpowered passenger and 101 unpowered cargo wagons with 166 powered passenger, 21 powered cargo and 36 unloaded steam units; air 38 powered passenger (the F 13), no cargo aircraft. A tram and plane fleet counted by model is therefore no sign that the planes carry goods.
- **The header counts check the instance counts.** The load dialog's counts ([header.md](header.md#counts-the-load-dialog-shows)) are the player's road vehicles (`i32` index 2), aircraft (index 3) and ships (index 4). **Observed**, four saves, instances of the `bus` and `truck` folders against the road count: equal in 6095814 (568: 575) and 6409998 (604: 285), 8 more in 6431760 (601: 242 in the header) and 72 more in 6417707 (604: 952). Aircraft: equal in 6095814 (3), 6409998 (0) and 6431760 (38), 41 more in 6417707. Ships: equal in 6095814 (13), 8 more in 6431760, 27 more in 6417707, and 2 fewer in 6409998 (12 for 14, possibly mod ships under another folder). What the extra instances are (vehicles not the player's, a stale record) is **Open**.
- **Private cars are not the player's.** 2,390 `car` instances in 6431760 and 5,809 in 6409998 are town traffic. Whether a bus or truck can also be town traffic is **Open**.
- **A vehicle that has been bought has an instance at once** ([vehicles.md](vehicles.md)), so the count includes vehicles standing in a depot. Whether a vehicle is on a line is not in the instance (**Open**, [entity-names.md](entity-names.md)).
