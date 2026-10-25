# Climate reference

One page to look up what a climate (strictly, its economy file) offers: which industries a new map can place, which of them dig or pump a raw resource, and which cargo a town can ask for. The pairs of climate and economy are in [climates-economies.md](climates-economies.md); recipes and boosters are in [industry-chains.md](industry-chains.md). Everything here is **base-game data** read from the 604 build's files, not from a save, and is **Observed**. Mods can change any of it.

## In short

- **The list of industries a map can place is the economy's placement table (Observed, 604 files).** `economy/placementparamsutil.lua` in `economy.zip` holds one entry per industry; each `economy/<name>.eco.lua` removes the ones its climate lacks. `all.eco` removes none. [tools/industry_chains.py](../tools/industry_chains.py) prints the result as the tables below.
- **Raw resources per climate (Observed):** nine extractive industries in dry, ten in subarctic, twelve in temperate and in tropical. Only tropical has rubber, only dry and temperate have clay, only temperate and tropical have cotton.
- **What a town can ask for is the economy's cargo-category list (Observed):** a category with a district type (commercial or industrial) and a tier is a possible town cargo. An economy that removes the category is the economy whose town records never use that cargo, which matches the saves in [climates-economies.md](climates-economies.md#what-each-economy-leaves-out-of-town-cargo) (599 to 604).
- **Not known (Open):** what `Weight`, `Order` and `Needs nearby` do in the placement, whether a map really spawns every industry listed, and the biome rules (see [Open](#open)).

## Industries by climate

An `x` means the industry is in that economy's placement table. Kind comes from the recipe: extractive means the industry takes nothing in. "Order", "Tier", "Weight" and "Needs nearby" are the default values from the shared table; a climate's own override is in brackets.

| Industry | Kind | Order | Tier | Weight | Needs nearby (default) | temperate | dry | tropic | subarctic |
|---|---|---|---|---|---|---|---|---|---|
| farm | extractive | 10 | 0 | 25 | | x | x | x (weight 20) | x |
| fishing_grounds | extractive | 20 | 0 | 15 | | x | | x | x |
| oil_refinery | processing | 30 | 0 | 10 | oil_well, oil_platform | x (needs oil_platform) | x | x (needs oil_platform) | x |
| oil_platform | extractive | 40 | 0 | 10 | | x | x (weight 10) | x | x (weight 10) |
| bricks_works | processing | 50 | 0 | 10 | clay_pit | x | x | | |
| clay_pit | extractive | 60 | 0 | 20 | | x | x | | |
| cement_plant | processing | 70 | 0 | 10 | quarry | | | | x |
| quarry | extractive | 80 | 0 | 20 | | x | x | x | x |
| livestock_farm | processing | 90 | 0 | 10 | farm | x | x | x | x |
| chemical_plant | processing | 110 | 1 | 10 | oil_refinery | x | x | x | x |
| tool_factory | processing | 120 | 1 | 10 | saw_mill, chemical_plant | x | x | x | x |
| saw_mill | processing | 130 | 0 | 10 | forest | x | x | x (order 50) | x |
| forest | extractive | 140 | 0 | 10 | | x | x | x (order 60) | x |
| furniture_factory | processing | 150 | 1 | 10 | glass_works, saw_mill | x | x | x | x |
| glass_works | processing | 160 | 1 | 10 | sand_pit, sand_excavator | x (needs sand_excavator) | x | x (needs sand_excavator) | x (needs sand_excavator) |
| sand_excavator | extractive | 170 | 1 | 20 | | x | | x | x |
| sand_pit | extractive | 180 | 1 | 20 | | x | x | x | x |
| brewery | processing | 190 | 1 | 10 | glass_works, farm | x | x | | x |
| machine_factory | processing | 200 | 1 | 20 | steel_mill, chemical_plant | x | x | x | x |
| steel_mill | processing | 210 | 1 | 20 | iron_ore_mine, coal_mine | x | x | x | x |
| iron_ore_mine | extractive | 220 | 1 | 40 | | x | x | x | x |
| coal_mine | extractive | 230 | 1 | 40 | | x | x | x | x |
| food_factory | processing | 240 | 1 | 10 | fishing_grounds, livestock_farm, steel_mill | x | x | x | x |
| textile_factory | processing | 250 | 1 | 10 | weaving_mill, chemical_plant | x | x | x | x |
| weaving_mill | processing | 260 | 1 | 10 | cotton_farm, livestock_farm | x | x | x | x |
| vehicle_factory | processing | 270 | 2 | 10 | tire_factory, machine_factory | x | x | x | x |
| tire_factory | processing | 280 | 2 | 10 | rubber_farm | | | x | |
| rubber_farm | extractive | 290 | 2 | 20 | | | | x | |
| printing_press | processing | 300 | 1 | 10 | paper_mill, chemical_plant | | | | x |
| paper_mill | processing | 310 | 1 | 10 | saw_mill | | | | x |
| oil_well | extractive | 320 | 0 | 10 | | x | x | x | x |
| cotton_farm | extractive | 330 | 1 | 10 | | x | | x | |

Reading it:

- **Raw resources, by climate.** Extractive rows with an `x`: temperate has farm, fishing_grounds, oil_platform, clay_pit, quarry, forest, sand_excavator, sand_pit, iron_ore_mine, coal_mine, oil_well and cotton_farm. Dry has farm, oil_platform, clay_pit, quarry, forest, sand_pit, iron_ore_mine, coal_mine and oil_well. Tropical has the temperate list without clay_pit and with rubber_farm. Subarctic has the temperate list without clay_pit and cotton_farm.
- **Water and shore industries.** fishing_grounds, oil_platform and sand_excavator are the extractive ones without the `TYPE_RAW` tag the others carry. Each economy also sets `waterIndustryFraction`; its use is Open ([industry-chains.md](industry-chains.md#which-climates-have-which-industry)).
- **Stand-ins.** Temperate and tropical map an `oil_platform` to an `oil_well`, and temperate, tropical and subarctic map a `sand_excavator` to a `sand_pit`, through `industryPlacementFallbacks`. Dry has none, and also lacks the excavator, so a dry `glass_works` uses `sand_pit`.
- **Livestock_farm** counts as processing here because it takes grain; the economy table puts it with the farms (order 90, needs a farm).

## Town cargo by climate

A cargo is a possible town cargo when its category has a district type. The tier and factor are the game's own; how a town picks among them as it grows is in [cargo-ids.md](cargo-ids.md#how-the-game-adds-cargo-to-a-town).

| Cargo | District | Tier | Factor | temperate | dry | tropic | subarctic |
|---|---|---|---|---|---|---|---|
| fish | commercial | 0 | 1 | x | | x | x |
| meat | commercial | 0 | 1 | x | x | x | x |
| vegetables | commercial | 0 | 1 | x | x | x | |
| bricks | industrial | 0 | 1 | x | x | | |
| cement | industrial | 0 | 1 | | | | x |
| fuel | industrial | 0 | 1 | x | x | x | x |
| planks | industrial | 0 | 1 | x | x | x | x |
| beverages | commercial | 1 | 0.5 | x | x | | x |
| books | commercial | 1 | 0.5 | | | | x |
| clothes | commercial | 1 | 0.5 | x | x | x | x |
| tinned_food | commercial | 1 | 0.5 | x | x | x | x |
| furniture | industrial | 1 | 0.5 | x | x | x | x |
| machines | industrial | 1 | 0.5 | x | x | x | x |
| tools | industrial | 1 | 0.5 | x | x | x | x |
| vehicles | industrial | 2 | 0.25 | x | x | x | x |

- **Cement in temperate and bricks in tropical** are absent, which agrees with the town records in saves. `tropic.eco` removes the bricks category together with beverages, cement and clay, while the cargo's own file still lists tropical (see [Evidence and tests](#evidence-and-tests)).
- **Books** is a commercial tier 1 category, present only in subarctic and all-industries games. That agrees with the town records, where id 35 turns up only in those games ([cargo-ids.md](cargo-ids.md#the-ids-across-economies)); the tier table in that note lacks books.
- **Chemicals** has a tier and a factor in the file but no district type, so it is not a town cargo.

## Open

- What the weight, order and nearby requirement do when the map places industries ([industry-chains.md](industry-chains.md#which-climates-have-which-industry) has the file-side Open items). A guess is that a heavier weight is placed more often, a lower order earlier, and a processing industry only near one of the named ones; none of that is tested.
- Whether a new map actually spawns every industry in a climate's column. The only count we have is [industry-lifecycle.md](industry-lifecycle.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604) (eight Tiny and Small games); a count of industry kinds per climate across the catalog saves is not done.
- The `biome0` to `biome4` weights each industry carries in the shared table: they name the biome data maps of the terrain ([terrain.md](terrain.md)), but how strongly each steers placement, and which terrain each map stands for, is not read.
- Why the dry and subarctic economy files remove `wool`, which is not in the shared category table (so the removal does nothing we can see), and why paper, which also has no category there, still turns up in town records of subarctic and all-industries games.

## Evidence and tests

**Observed**, 604 build files only (`economy/placementparamsutil.lua`, `economy/<climate>.eco.lua` in `base/content/economy.zip`), read at run time by [tools/industry_chains.py](../tools/industry_chains.py).

- **The industry files and the economy placement tables agree** for every industry and climate, and the tool warns if a build ever breaks that.
- **The cargo files and the economy category lists differ in one case that matters for towns:** `cargos/bricks` lists tropical, while `tropic.eco` removes the bricks category (and has no bricks_works or clay_pit). The saves agree with the economy file: tropical town records never use bricks (id 33). The tool warns about this one. The dry and subarctic files also remove a `wool` category that the shared table does not have, and wool is made there by the livestock farm.
- **The subarctic file removes vegetables with an undefined name instead of `nil`** (`cargoCategories.vegetables = nin`, a typo; Lua reads an unset name as nil). The effect is the same as the other removals, and no subarctic town record uses vegetables (id 9).
