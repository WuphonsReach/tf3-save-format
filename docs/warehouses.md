# Warehouses: modules and cargo slots

Each warehouse is a construction record with a list of modules, and each module holds one cargo slot. Checked on 604, one save: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (subarctic, start year 1900) in a later manual save, compared with the game's warehouse window and build toolbar tooltips. Labels are **Observed** (one save) unless marked.

## The construction record

- Each warehouse has a record that starts with the resource path `warehouses/warehouse.con`. The save had 38 of them, and 38 entries named `... Warehouse` in the names table ([entity-names.md](entity-names.md)), so it looks like one record per warehouse.
- After the path comes a Lua table (see [lua-values.md](lua-values.md)) of named values. The key `modules` holds the modules as a table from a number to `{name, variant}`, where `name` is a path such as `::/warehouses/wh_bulk.module`. `variant` was 0 in the two records read in full. After the modules come `paramX` and `paramY` (both -0 here), `seed` and `tagToCargoType`. In a May 2000 autosave of the same game all records also had `upgrade` and `year`, and most `constructOpt56` and `constructOpt78` (see the second game below).
- `tagToCargoType` maps the same numbers to a cargo resource path, for example `::/cargos/grain/grain.cargo`. In 37 of 38 records the two tables had the same keys. In the other, a goods module (2 modules, 1 tag) had no cargo set.
- The same module type can appear many times in one warehouse. A record with 15 modules held 5 bulk, 5 flatbed, 4 goods and 1 liquid, and that is what the game's window for the matching warehouse listed: 15 stock slots, grouped under Bulk, Flatbed, Goods and Liquid headings. Records held 1 to 15 modules (counts seen: 1, 2, 3, 4, 5, 6, 8, 12, 15).
- Module types seen: `wh_bulk`, `wh_flatbed`, `wh_goods`, `wh_liquid`. The window's "Specialization" is the module type. The cargos assigned to each type were disjoint:

| Module | Cargos seen (subarctic) |
|---|---|
| `wh_bulk` | cement, coal, grain, iron_ore, sand, sawdust, stone |
| `wh_flatbed` | logs, machines, planks, sheet_metal, steel, vehicles |
| `wh_goods` | beverages, books, clothes, fish, furniture, glass, meat, plastic, tinned_food, tools, wool |
| `wh_liquid` | chemicals, crude_oil, dyes, fuel |

  The build tooltips list more icons than these (8 for bulk, 13 for goods, 6 for flatbed, 4 for liquid), so a warehouse can take more cargos than any one save used.
- The 15-module record fits the warehouse window by count and by cargo icons, as read by eye from screenshots: the goods slots were fish, plastic, books and tinned food (16, 106, 0 and 12 in the window), and the only liquid slot was fuel. One slot was checked in the game: hovering the open-book icon showed the tooltip "Books", the cargo the record tags on one of its goods modules. The match of the other slots was not checked one by one.
- The module keys are large numbers (622,502,550 to 672,502,500 seen) that differ by 40 or 50 within a warehouse, in groups. They look like packed two-part positions, since the leading digits step 62, 63, 64, ... across modules and the tail ran from 2,502,340 to 2,502,660. What they encode is **Open**.
- The module keys also occur as u32 in the entity data after the record (all 15 keys of the 15-module warehouse sat together within 4 KB, starting about 1.3 KB after the record, and again in other places 100 KB to 15 MB further on). The values next to them looked like placement data (f32 16.0 and 1.0 and a run that looks like a transform), not stock. **Observed**, one warehouse in one later save. This means the keys tie a module to its model placement, not to its stock.
- Before the path the record has a string like `__module_` plus digits and a list of entity ids (12 in the 15-module record, so not one per module). What they are is **Open**.

## Cost

- The running cost on the warehouse window was $3,750,000 a year, and the build tooltip gave $250,000 a year for each specialized module (Bulk, Flatbed, Goods, Liquid), against $125,000 for the Universal Warehouse. 15 modules times $250,000 is $3,750,000, so the yearly cost is the sum over the modules. The building prices were $150,000 (Universal) and $300,000 (specialized). **Observed**, one warehouse. How the journal books the upkeep (in batches through the year) is in [finances.md](finances.md#running-costs-upkeep-loan-payments-and-income-over-ten-minutes).
- The Warehouses tab (one row per warehouse, towns have several and share names) shows Stored, Capacity, Utilization and Upkeep. For the rows compared with a record, Capacity was 500 times the module count and Upkeep $250,000 times the module count: a one-module record (a bulk coal module) read 500 and $250,000, two flatbed modules (steel and sheet metal) 1,000 and $500,000, six goods and bulk modules 3,000 and $1,500,000, and the 15-module warehouse 7,500 and $3,750,000. **Observed**, four warehouses. Stored is the sum of the slots: a six-slot warehouse with 11, 1, 11, 40, 2 and 52 showed 117.
- Noise and pollution on the tooltips: Universal 20 and 25, the specialized ones 20 and 50.

## A second game: records without cargo tags

Checked on 604, catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) (temperate, European names, start year 1900, map 11264 x 22528 m, no mods, shown as 18 February 1937) in a paused re-save, against the whole Warehouses tab (23 rows). **Observed**, one game.

- The save had 23 records with the path `warehouses/warehouse.con` and the tab had 23 rows. The path is followed by a Lua table whose pairs are written as tagged keys and values (see [lua-values.md](lua-values.md)); parsing pairs until a key is not a string reads it.
- Its keys were only `modules`, `seed`, `year` and, in the 14 records with more than one module, `upgrade` (the 9 one-module records had no `upgrade`). There was **no `tagToCargoType`, `paramX`, `paramY` or `constructOpt*`**, and the string `tagToCargoType` did not occur anywhere in the stream. The records of a May 2000 autosave of the first game (catalog 6417707, 604) all had `tagToCargoType`, `upgrade` and `year`, most also `paramX`, `paramY`, `constructOpt56` and `constructOpt78`. So the record's shape depends on the game, and which cargo a module is set to is **not** always in the record. The cargo a warehouse holds shows in its statistics lists instead, which matched 15 rows of this game's tab ([statistics-lists.md](statistics-lists.md)): the tab's icon column showed single cargos for some warehouses, for example fish only, and the record held nothing about fish while the lists held id 6. Where the cargo a module is set to (as opposed to what it holds) is kept is **Open**.
- `year` ran from 1906 to 1930 here and 1900 to 1977 in the first game (6417707), never past the game's date. It looks like the year the warehouse was built; **Open**.
- A fifth module type, `::/warehouses/wh_universal.module`, appeared once (in a 5-module record: 2 goods, flatbed, bulk, universal). The tab showed that row at capacity 2,500 and upkeep $168,750. With $37,500 a year for each specialized module that is 4 x $37,500 + $18,750, so a universal module cost half of a specialized one, as in the build tooltips above (125,000 against 250,000), and still gave 500 capacity.
- The module counts matched the tab as a group: records of 1, 2, 3, 4, 5 and 8 modules numbered 9, 5, 3, 3, 2 and 1, and the rows with capacity 500, 1,000, 1,500, 2,000, 2,500 and 4,000 numbered the same. Capacity was 500 times the module count in every row, so the rule above held in a second game. Pairing single rows with single records was not done.
- Upkeep per specialized module was $37,500 here (1937) against $250,000 in the first game (2000), a factor of 6.7. The two games' settings differ (see [settings.md](settings.md)): `infrastructureMaintenanceScale` was 1 here (50%) and 3 in the first game (100%), which would account for a factor of 2 if warehouse upkeep follows that setting, leaving 3.3. Inflation was Low here and Normal in the first game, but that option only cuts income by rank ([inflation.md](inflation.md#the-income-multiplier)), so it does not touch upkeep.
- **The date probably explains the remaining 3.3** (**Open**). The game scales construction costs by year in 20-year steps, which gives a factor of 3.33 between 1937 and 2000. The table, the players' reports and a test that would settle it are in [inflation.md](inflation.md#the-year-cost-table).

## Not found

The stock levels in each slot and the yearly incoming and outgoing totals are not in this record. They are not stored as plain numbers elsewhere either: a stock is the difference of two running totals and the yearly bars are differences of the same totals, see [statistics-lists.md](statistics-lists.md). Searches that failed first are in [entity-stats.md](entity-stats.md).
