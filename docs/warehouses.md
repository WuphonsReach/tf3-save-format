# Warehouses: modules and cargo slots

Each warehouse is a construction record with a list of modules, and each module holds one cargo slot. Checked on 604, one save: catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (subarctic, start year 1900) in a later manual save, compared with the game's warehouse window and build toolbar tooltips. Labels are **Observed** (one save) unless marked.

## The construction record

- Each warehouse has a record that starts with the resource path `warehouses/warehouse.con`. The save had 38 of them, and 38 entries named `... Warehouse` in the names table ([entity-names.md](entity-names.md)), so it looks like one record per warehouse.
- After the path comes a Lua table (see [lua-values.md](lua-values.md)) of named values. The key `modules` holds the modules as a table from a number to `{name, variant}`, where `name` is a path such as `::/warehouses/wh_bulk.module`. `variant` was 0 in the two records read in full. After the modules come `paramX` and `paramY` (both -0 here), `seed` and `tagToCargoType`.
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

- The running cost on the warehouse window was $3,750,000 a year, and the build tooltip gave $250,000 a year for each specialized module (Bulk, Flatbed, Goods, Liquid), against $125,000 for the Universal Warehouse. 15 modules times $250,000 is $3,750,000, so the yearly cost is the sum over the modules. The building prices were $150,000 (Universal) and $300,000 (specialized). **Observed**, one warehouse.
- The Warehouses tab (one row per warehouse, towns have several and share names) shows Stored, Capacity, Utilization and Upkeep. For the rows compared with a record, Capacity was 500 times the module count and Upkeep $250,000 times the module count: a one-module record (a bulk coal module) read 500 and $250,000, two flatbed modules (steel and sheet metal) 1,000 and $500,000, six goods and bulk modules 3,000 and $1,500,000, and the 15-module warehouse 7,500 and $3,750,000. **Observed**, four warehouses. Stored is the sum of the slots: a six-slot warehouse with 11, 1, 11, 40, 2 and 52 showed 117.
- Noise and pollution on the tooltips: Universal 20 and 25, the specialized ones 20 and 50.

## Not found

The stock levels in each slot and the yearly incoming and outgoing totals are not in this record. They are not stored as plain numbers elsewhere either, see [entity-stats.md](entity-stats.md).
