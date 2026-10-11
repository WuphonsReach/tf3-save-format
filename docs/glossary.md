# Glossary: the game's internal names and what players call them

Checked against the base game files of the build that writes 604 saves (the resource files under `base/content` and the English string catalog in `base/strings`). Keys and labels are **Observed** (read from the install, not from a save). The "players say" column is a writing aid, not a format fact.

**Rule: write the game's internal name.** A thing has a **key** (the identity the game and the save use: a resource folder or file name such as `cement`, `food_factory`, `water_depot`, or, for things with no resource of their own, the string id such as `HARBOR_SMALL`) and a **label** (the English text on screen). Notes, commit messages and tool output use the key, in code font where it stands for the thing itself. The label comes second, only to help a reader match the screen. If a player's message says "concrete", write `cement`; if it says "boat", write `ship`. When a loose word could be two keys (see [Ambiguous words](#ambiguous-words)), look at the context or ask.

## Cargo

All 37 base cargo keys with their ids are in [cargo-ids.md](cargo-ids.md). The key is the folder under `cargos/` in the install and the file name in a save's cargo list. Rows here are only the ones where the label or the player's word differs from the key.

| Key | Label | Players say |
|---|---|---|
| `cement` | Cement | concrete |
| `vegetables` | Vegetables | veg, vegs, veggies, cabbage, lettuce, produce |
| `tinned_food` | Canned Food | canned food, cans, tins, food (ambiguous) |
| `sheet_metal` | Sheet Metal | sheet steel, plate |
| `crude_oil` | Crude Oil | oil (ambiguous) |
| `iron_ore` | Iron Ore | iron (ambiguous), ore (ambiguous) |
| `tires` | Tires | tyres |
| `passengers` | Passengers | pax, people (ambiguous), commuters |
| `machines` | Machines | machinery |
| `planks` | Planks | lumber, boards, timber (ambiguous) |
| `logs` | Logs | wood (ambiguous), timber (ambiguous) |

The base game has no cabbage or lettuce cargo; the crop farm's `vegetables` stand for them.

Each cargo file lists `cargoClasses`: `UNIVERSAL` plus one of `BULK`, `FLATBED`, `GOODS`, `LIQUID`, and `PASSENGERS` alone for passengers. These decide the warehouse module and cargo-station preset a cargo fits. Use the class names only in that sense.

## Industries

The key is the zip name under `industries/`. The label differs from the key more often than for cargo, so use the key.

| Key | Label | Players say |
|---|---|---|
| `saw_mill` | Saw Mill | sawmill, lumber mill |
| `food_factory` | Canning Factory | cannery, food factory, food plant |
| `farm` | Crop Farm | crop farm, field (ambiguous) |
| `forest` | Logging Camp | lumber camp, logging |
| `sand_excavator` | Sand Dredger | dredger, sand dredge |
| `printing_press` | Printing Factory | print works |
| `tool_factory` | Tools Factory | tool factory |
| `bricks_works` | Brickworks | brick works, brickyard |
| `glass_works` | Glassworks | glass works |
| `oil_platform` | Oil Platform | oil rig |
| `fishing_grounds` | Fishing Grounds | fishery, fishing port, fish farm |
| `cement_plant` | Cement Plant | concrete plant, cement works |

The other keys (`brewery`, `chemical_plant`, `clay_pit`, `coal_mine`, `cotton_farm`, `furniture_factory`, `iron_ore_mine`, `livestock_farm`, `machine_factory`, `oil_refinery`, `oil_well`, `paper_mill`, `quarry`, `rubber_farm`, `sand_pit`, `steel_mill`, `textile_factory`, `tire_factory`, `vehicle_factory`, `weaving_mill`) read as their labels. What each takes and gives is in [industry-chains.md](industry-chains.md).

## Stops, stations, ports and depots

The save and the Lua API call a built stop or station a **station group** (an entity with one or more terminals). Notes say "station" for the whole group and "stop" for one terminal.

The game has no separate truck stop, bus stop or bus station building. There are two road-side builds, and what a stop serves comes from the line's vehicles:

- `small_*` (`street/small_stops/`: `small_old`, `small_mid`, `small_new` and the `_twosided` variants), label Road Stop or Two-Sided Road Stop. This is the "bus stop" and "truck stop".
- `modular_terminal` (`street/modular_street_station/`), the bigger station. Its presets are string ids: `STATIONS_STREET_PASSENGER` (label Bus/Tram Station) and `STATIONS_STREET_CARGO_UNIVERSAL`, `_BULK`, `_FLATBED`, `_GOODS`, `_LIQUID` (Universal Cargo Station and so on). The cargo platforms are the modules `cargo_platform` and `cargo_platform_bulk`, `_flatbed`, `_goods`, `_liquid`.

| Key | Label | Players say |
|---|---|---|
| `small_*` | Road Stop | truck stop, bus stop, cargo stop, stop (ambiguous) |
| `modular_terminal`, `STATIONS_STREET_PASSENGER` | Bus/Tram Station | bus station, bus terminal |
| `modular_terminal`, `STATIONS_STREET_CARGO_UNIVERSAL` | Universal Cargo Station | truck station, cargo station, cargo terminal, truck terminal, loading station |
| `harbor_modular`, `HARBOR_SMALL`, `HARBOR_LARGE` | Small or Large Passenger/Cargo Port | harbor, harbour, dock (ambiguous), quay, ship stop |
| `STATIONS_WATER_SMALL_PIER`, `STATIONS_WATER_MEDIUM_PIER` | Small Landing, Large Landing | pier, jetty |
| `modular_station` (`rail/`) | rail station build | train station, railway station |
| `road_depot` | Road Depot | bus garage, truck depot, garage |
| `water_depot` (string `DEPOTS_WATER_SHIPYARD`) | Ship Depot | shipyard, boat depot, dock (ambiguous) |
| `rail_depot` | Train Depot | train shed, engine shed |
| `tram_depot` | Tram Depot | tram shed |
| `road_maint_station`, `rail_maint_station`, `water_maint_station` | Road, Train, Ship Maintenance Building | service station, repair shop |

Our notes already say "port" and "ship depot"; those match the labels. "Depot" means a vehicle building only: a warehouse is not a depot, although the airport's hangar is labelled "Depot" in the game's strings. Airport parts keep their keys (`airport`, `airfield`, `helipad`, `heliport`).

## Warehouses

Key `warehouse` (`warehouses/warehouse.con`) with the modules `wh_bulk`, `wh_flatbed`, `wh_goods`, `wh_liquid` and `wh_universal` (see [warehouses.md](warehouses.md)). Labels: Bulk, Flatbed, Goods, Liquid and Universal Warehouse. Players say storage, store, silo (bulk), tank (liquid).

## Vehicles

The categories are the folders under `vehicle/`: `bus`, `car`, `helicopter`, `plane`, `ship`, `train`, `tram`, `truck`, `waggon` (the wagons, spelled with two g in the folder) and `zeppelin`. A model is a folder within one, for example `vehicle/ship/british_columbia`.

| Key | Players say | Note |
|---|---|---|
| `ship` | boat, vessel, watercraft, cargo ship, freighter, barge | one category for every water vehicle; ship, boat and vessel are used loosely for it |
| `vehicle/ship/british_columbia` | trawler, fishing boat | a model (label Canadian Trawler), not a type |
| `damen_tanker`, `votrans_tanker` | tanker | labels Damen Tanker 800, Votrans Towboat Tanker |
| `damen_ferry`, `hong_kong_ferry_boat` | ferry | labels Damen Fast Ferry, Meridian Ferry |
| `herkules_xi_universal`, `virgo_universal`, `votrans_universal` | tug, towboat | labels Hercules XI Towboat, Virgo Towboat, Votrans Towboat Cargo |
| `truck` | lorry, hauler, wagon (cargo) (ambiguous) | a model's label ends in Box, Bulk, Tank or Stake, or has no suffix |
| `truck` models `horse_cart_small`, `horse_cart_medium`, `horse_cart_barrels` | cart (ambiguous), wagon (ambiguous), dray, carriage (ambiguous) | the labels say "Horse Carriage"; they carry cargo, not people |
| `bus` | coach (ambiguous), omnibus, minibus, shuttle | a bus model can be a motor bus or horse-drawn |
| `bus` models `droshky`, `american_post_coach` | carriage (ambiguous), coach (ambiguous), stagecoach, cab, horse bus | horse-drawn passenger carriages; American Post Coach is labelled Stagecoach (`obeissante`, L'Obéissante, is an early steam bus, not horse-drawn) |
| `tram` model `double_horse` | horse tram | label Horse Tram, in the `tram` category |
| `train` | loco, locomotive, engine (ambiguous), railcar | the wagons are `waggon` |
| `waggon` | wagon (ambiguous), freight car, boxcar, coach (rail) (ambiguous) | a train's cargo or passenger wagon |
| `tram` | streetcar, trolley | a bus model is labelled Wright StreetCar, yet it is in `bus` |
| `car` | car, automobile | private cars in the `car` folder (not a train car or tram car) |

A line is a `line`; players also say route. "Car" alone is ambiguous: a private `car`, a tram car (labels such as Box Car, Closed Car) or a train car.

## Ambiguous words

Do not pick a key for these without context:

- **oil**: `crude_oil` (what a well or platform makes) or `fuel` (what the refinery makes).
- **wood, timber**: `logs`, `planks` or `sawdust`.
- **food**: `tinned_food`, or the commercial cargo `fish`, `meat` and `vegetables`.
- **iron, metal, steel**: `iron_ore`, `steel` or `sheet_metal`.
- **grain, crops**: `grain`, or `vegetables` (the `farm` makes both).
- **port**: the `harbor_modular` station, or an industry on the water.
- **depot**: a vehicle depot (`road_depot`, `rail_depot`, `water_depot`), never a `warehouse`.
- **station**: one terminal or a whole station group.
- **carriage, coach, wagon, cart**: a horse-drawn passenger `bus`, a horse-drawn cargo `truck`, a rail `waggon` or a tram car; the words overlap in English (a cart has two wheels, a carriage carries people, a coach is large and enclosed, a wagon is a utility vehicle), and the game's labels do not follow them. Read the cargo or passenger context.
- **car**: a private `car`, a tram car or a train car.
- **cargo platform**: a module of `modular_terminal`, not a separate station.
- **dock**: `harbor_modular` or `water_depot`.

If a message uses a word you cannot place, say so rather than guessing, and add the word to this note once the user has answered.

Sources for the word senses: community usage of "truck station", "truck stop" and "cargo terminal" is from [Steam discussions for Transport Fever 2](https://steamcommunity.com/app/1066780/discussions/0/1746772488905106339), and the senses of cart, carriage, coach, wagon and droshky from [Wikipedia: Horse-drawn vehicle](https://en.wikipedia.org/wiki/Horse-drawn_vehicle) and [Wiktionary: droshky](https://en.wiktionary.org/wiki/droshky). The game's own labels win where they differ.
