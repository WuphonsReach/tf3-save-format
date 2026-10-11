# Industry chains

What each industry takes in and gives out, which climates have it, and how each cargo travels. This is **base-game data** read from the install's files (604 build), not from a save. **Observed** unless a line says otherwise: read from the files, not changed in the game. Mods can change any of it, see [Mods](#mods).

Sources, all under `base/content/` in the install: `industries/<name>.zip` (the `<name>/<name>.con.lua` file of each industry), `economy.zip` (`economy/<climate>.eco.lua`, `economy/placementparamsutil.lua`) and `cargos/<name>.zip` (`<name>/<name>.cargo.lua`). Cargo names are the resource names; the numeric ids a save uses are in [cargo-ids.md](cargo-ids.md). [tools/industry_chains.py](../tools/industry_chains.py) rebuilds all the tables below from the user's own install, and warns where the industry files and the economy files disagree.

## How a recipe is written

Each industry file has a stock list and a list of rules:

- A stock is `INPUT_STOCK` or `OUTPUT_STOCK` with a cargo and a capacity.
- A rule has `input`, `output` and `capacity`. `input` is a list of amounts, one per input stock in the order the stocks are declared. `output` maps a cargo to an amount. One cycle of the rule consumes the inputs and yields the outputs.
- `capacity` carries the comment "duration" in the file, so it is the cycle length in some game time unit. **Open**: which unit.
- An extractive industry has an input of 0 (it needs nothing). Its input stock, if any, is a booster: a second rule with `booster = true` takes the stock in amounts of 12, 13, 15 or 17 per cycle and outputs nothing.
- The food factory has two rules, each with `requiredInput` naming one input stock (fish in the first, meat in the second), so it takes fish or meat, plus sheet metal. **Observed** reading of `requiredInput`, **Open** on how the game picks when both are in stock.

## Recipes

Amounts per cycle, 604 build. Inputs are in stock order.

| Industry | Takes | Gives |
|---|---|---|
| saw_mill | 4 logs | 8 planks, 4 sawdust |
| steel_mill | 6 iron_ore, 6 coal | 3 steel, 4 sheet_metal |
| cement_plant | 4 stone | 2 cement |
| glass_works | 4 sand | 2 glass |
| bricks_works | 4 clay | 4 bricks |
| paper_mill | 4 sawdust | 2 paper |
| oil_refinery | 4 crude_oil | 2 fuel, 1 fertilizer, 4 chemicals |
| chemical_plant | 6 chemicals | 2 dyes, 5 plastic |
| weaving_mill | 4 wool | 4 fabric |
| textile_factory | 4 fabric, 2 dyes | 3 clothes |
| printing_press | 4 paper, 2 dyes | 4 books |
| brewery | 8 grain, 3 glass | 8 beverages |
| livestock_farm | 8 grain | 4 meat, 5 wool |
| food_factory | 2 fish or 2 meat, plus 1 sheet_metal | 2 tinned_food |
| furniture_factory | 4 planks, 1 glass | 2 furniture |
| tool_factory | 4 planks, 2 plastic | 5 tools |
| machine_factory | 7 steel, 4 plastic | 7 machines |
| tire_factory | 4 rubber | 2 tires |
| vehicle_factory | 1 tires, 4 sheet_metal, 1 machines | 1 vehicles |

Extractive industries, no input needed:

| Industry | Gives | Booster (per cycle) |
|---|---|---|
| quarry | 16 stone | 12 tools |
| coal_mine | 16 coal | 13 tools |
| iron_ore_mine | 16 iron_ore | 15 machines |
| forest | 8 logs | 15 machines |
| sand_pit | 8 sand | 12 tools |
| sand_excavator | 8 sand | 15 machines |
| clay_pit | 16 clay | 12 tools |
| fishing_grounds | 12 fish | 12 tools |
| oil_well | 6 crude_oil | 15 machines |
| oil_platform | 4 crude_oil | 12 machines |
| farm | 16 vegetables, 24 grain | 17 fertilizer |
| cotton_farm | 12 wool | 17 fertilizer |
| rubber_farm | 32 rubber | 17 fertilizer |

Reading it as a graph: tools come from the tool_factory, machines from the machine_factory and fertilizer from the oil_refinery, so the boosters tie the extractive industries back into the manufacturing ones. Towns and the wonders consume the finished goods ([cargo-ids.md](cargo-ids.md#tiers-and-weights)).

**Checked against a save**: the cement ratio matches the statistics lists of a subarctic game, where a cement plant consumed 36 and 28 stone for 18 and 14 cement ([cargo-ids.md](cargo-ids.md#the-ids-across-economies)), and the same plant's totals at clock 54.6 million were 1,852 stone for 926 cement ([cement-chain.md](cement-chain.md)), so 2 stone per cement. Reading a recipe's ratio off a save's `itemsConsumed` and `itemsProduced` lists ([statistics-lists.md](statistics-lists.md)) is the quickest way to see what a particular game uses.

## Which climates have which industry

The `categoryList` in each industry file names the economies it appears in; the economy files remove the same industries from their placement table. The two agree. `all.eco` has every industry.

- All four climates: saw_mill, forest, steel_mill, coal_mine, iron_ore_mine, quarry, glass_works, sand_pit, oil_refinery, oil_well, oil_platform, chemical_plant, farm, livestock_farm, weaving_mill, textile_factory, food_factory, furniture_factory, tool_factory, machine_factory, vehicle_factory.
- Not dry: fishing_grounds, sand_excavator.
- Not tropical: brewery.
- Temperate and dry only: bricks_works, clay_pit.
- Temperate and tropical only: cotton_farm.
- Subarctic only: cement_plant, paper_mill, printing_press.
- Tropical only: rubber_farm, tire_factory.

The matching cargo files list the economies each cargo exists in. Sawdust, paper, books and cement are subarctic only; tires and rubber tropical only; clay temperate and dry only. Four more are missing from one climate each: vegetables and bricks from subarctic, beverages from tropical, fish from dry. What each economy leaves out of town cargo, as seen in saves, is in [climates-economies.md](climates-economies.md#what-each-economy-leaves-out-of-town-cargo). **Open**: some rules still name a cargo their climate lacks (the saw_mill's sawdust and the vehicle_factory's tires outside those climates, the farm's vegetables in subarctic). How the game treats an input whose cargo the economy lacks is not in the files read; it presumably drops that stock.

Each economy file also holds:

- Placement tweaks: `glass_works` needs a sand_excavator nearby in temperate, subarctic and tropical (a sand_pit stands in through `industryPlacementFallbacks`); `oil_refinery` needs an oil_platform in temperate and tropical; `initWeight` is set to 10 for oil_platform in dry and subarctic and to 20 for farm in tropical (**Open**: the default and what the weight does).
- `waterIndustryFraction`, the share of industries placed on water. **Open**: the exact use.
- `cargoRequiredIndustries` (per cargo, a weight for each industry in its chain) and `companyRankRequiredIndustries` (below). **Open**: what the weights mean.

### Industries tied to company rank

`companyRankRequiredIndustries` lists industries by rank, each with the value 0.01 (**Open**: the meaning of the value; the table looks like the industries the map must have for that rank). The same in every economy except where noted:

| Rank | Industries |
|---|---|
| 2 | quarry |
| 3 | steel_mill, iron_ore_mine, coal_mine |
| 5 | oil_refinery, oil_platform (oil_well too in dry and subarctic) |
| 7 | forest, saw_mill |
| 10 | chemical_plant |
| 13 | furniture_factory, glass_works, sand_excavator (sand_pit in dry) |

Rank thresholds and what earns a rank are in [company.md](company.md).

## Transport class of each cargo

Each cargo file has `cargoClasses`: a universal class plus one of the four that decide which vehicles and warehouse modules carry it.

| Class | Cargo |
|---|---|
| BULK | stone, sand, sawdust, coal, iron_ore, clay, cement, grain, fertilizer |
| LIQUID | crude_oil, fuel, chemicals, dyes, rubber |
| FLATBED | logs, planks, steel, sheet_metal, machines, vehicles |
| GOODS | everything else: fish, meat, vegetables, wool, fabric, glass, plastic, paper, books, bricks, clothes, furniture, beverages, tinned_food, tools, tires |

Passengers have their own class; every other cargo lists `UNIVERSAL` as well. Rubber and dyes are the liquids you would not guess.

## Mods

A mod can change a recipe, change which economies an industry or cargo appears in, or add whole industries and cargo, so none of the tables above holds for every game. The mod list in the save says which mods a game had ([mods.md](mods.md)); the numbers in a game's own `itemsConsumed` and `itemsProduced` lists are what that game really uses. **Open**: not tested here. No modded industry file has been read yet, and neither has the way a mod's files override the base ones.
