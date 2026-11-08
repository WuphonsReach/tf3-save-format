# Warehouse layout: module keys, model positions and ground

Where a warehouse's modules stand, read from the keys of its construction record ([warehouses.md](warehouses.md#the-construction-record)) and tied to its model instances ([models.md](models.md)). The rules come from `warehouses/warehouse.script.lua` in the install's `base/content/warehouses.zip`. The key decoding was checked against model instances in seven catalog saves (604 and 605). The other placement rules and the ground faces are from the script only. [tf3map](https://github.com/WuphonsReach/tf3-save-mapper) draws warehouses from these rules.

## In short

- **A module key is the module's cell on an 8 m grid in the construction's own axes, plus a type digit (Observed, 123 base-game records in seven catalog saves, 604 and 605; formula read in the script).** `key = 10 * (250000 * (y + 250) + (x + 250)) + type`. The type is 0 for a module (`warehouse_large`) and 2 for the entrance's slot.
- **The construction's origin is 3 m along the entrance model's +y from its instance, and the axes are the instance's (Observed, the same records).** Each module's centre piece stands at `origin + 8 * (x, y)`, within 0.01 m in every base record checked.
- **The first module goes in cell (0, 3), 24 m from the origin (Observed: every base record checked holds that cell; from the script's template).** Further modules sit at steps of 4 cells (32 m), with sideways offsets of up to 3 cells, no more than 20 cells from the origin.
- **Each module lays a 40 m square ground face, so neighbours on the 32 m pitch overlap by 8 m; the entrance lays a 40 × 24 m face on the origin (script only).**
- **The drive-in warehouses mod (`drive_in_warehouses_1`) breaks the rule (Observed, five catalog saves, 604 and 605).** Its records carry `drive_in_*` keys. In those whose first module is (0, 4), the module stands one cell nearer the entrance than the base rule puts it. Its gate is a type-2 key in `modules`. In the one 605 save with gates, each gated warehouse's entrance instance has an all-zero transform.
- **Open:** what the mod's frame is exactly, where the modules of its records with an empty `modules` table are kept, and why the entrances of its gated warehouses have zero transforms (hidden by scaling to zero is a guess).

## Module keys

- **Decoding.** Take `type = key % 10`, then `r = key // 10`; `x = r % 250000 − 250` and `y = r // 250000 − 250`. A key difference of 10 is one cell along x, and 2,500,000 is one cell along y. The keys [warehouses.md](warehouses.md#the-construction-record) quotes decode as 622,502,550 → cell (5, −1) and 672,502,500 → cell (0, 19).
- **Types.** The script's type list is `warehouse_large` 0, `warehouse_small` 1 (its slots are commented out, so it is never offered) and `warehouse_entrance` 2. The entrance's own slot is cell (0, 0), type 2. It is not a key in a base record's `modules`: every base record checked held type 0 only.
- **Where new slots are offered.** The first module's row offers cells x −3 to 3 at y = 3. Each placed module offers slots 4 cells away on each side, with the same sideways spread. Slots past 20 cells from the origin either way are dropped (`maxSlotCoord`). Cells such as (5, −1), (3, 11) and (−2, 7) in the saves are these sideways offsets.
- **Finding a warehouse's modules in the instances.** Take the `warehouses/entrance/entrance_sm.mdl` instance. Its first transform row is the construction's x axis, and y is a quarter turn anticlockwise from it. Step 3 m along y to the origin, then 8 m per cell. A module's centre piece is `wh_bulk_center` (bulk), `wh_flatbed_rails` (flatbed), `wh_liquid` (liquid), `wh_universal_sm` (universal) or, for goods, its one `top*_right*` corner piece. The piece's folder matched the record's `::/warehouses/wh_<class>.module` in every base record checked.

## Where each module's models stand

From the script only; the saves matched the centre pieces (above), not each rule here.

- Every piece of a module is placed at its centre, `8 * (x, y)`, except:
  - **Bulk:** `wh_bulk_center` turns a half turn on alternate bands of 4 rows (by `floor(y / 4) % 2`).
  - **Liquid:** `wh_liquid` turns a half turn when `(x/4 + y/4) % 2` is 1.
  - **Flatbed:** the crane (`wh_flatbed`) and its trolley stand on the module with no flatbed neighbour 4 cells along +y, at a seeded offset of −8 to +8 m along y. `wh_flatbed_start` and `wh_flatbed_end` mark the ends of a run of flatbed modules.
  - **Universal:** the shack (`wh_universal_shack`) appears only when `(x + y) % 8` is 3 or less.
  - **Goods:** four corner pieces, `top`/`bot` by `left`/`right`, each taking a `_c` or `_diag` form by which neighbours 4 cells away are goods too. A goods module therefore has exactly one `top*_right*` piece.
  - **Liquid connectors:** `wh_liquid_con_1` to `_4` (bottom, left, top, right) where a liquid neighbour is 4 cells away.
- **Stock places are `industries/shared/stock_lane_1.mdl` instances:** 6 per goods module, 14 per flatbed and 12 per universal (`wh_goods_stocks.lua`, `wh_flatbed_stocks.lua`, `wh_universal_stocks.lua`). They do not count as industries in [industry_counts.py](../tools/industry_counts.py), which counts only each kind's main model: `shared` was an industry kind in none of 1,148 mined summaries. A tool counting every `industries/` instance would count them.
- Set dressing is under `assets/`, not `warehouses/`.

## Ground faces and model boxes

- **Modules.** Each lays a square ground face (terrain alignment and collider) of half size 16 m plus half a cell, 20 m each way from its centre. On the 32 m pitch, neighbours overlap by 8 m.
- **Entrance.** A 40 × 24 m face centred on the origin. `entrance_sm` stands 3 m before the origin, at (0, −3). The snap point to the street is at (0, −18). A metal fence runs round the cells next to the occupied ones.
- **Model files hold more than one box.** `wh_bulk_center.mdl` and `wh_liquid.mdl` list their `cargoBay` boxes after `boundingInfo`, so the last `bbMin`/`bbMax` pair in such a file is a bay, not the model. Bulk has two bunkers, each 11.5 × 23.3 m (format `BUNKER_11x21`, capacity 325). Liquid has one bay of ±9.8 m (format `CIRCLE_8`). Take a model's box from its `boundingInfo` block, as [station-pieces.md](station-pieces.md#sizes-and-drawing) does. No reader in `tools/` reads `.mdl` boxes.

## Evidence and tests

### Keys against model instances (604 and 605, Observed)

Each record's keys were decoded, each cell placed from the entrance instance as above, and the nearest centre piece compared, checking its folder against the module type.

- **Catalog [6417707](https://mod.io/g/transportfever3/m/333151) (604):** 38 of 38 records matched, every module within 0.01 m, records of 1 to 15 modules. Every record holds cell (0, 3).
- **Catalog [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) (604):** 23 of 23 matched, the same way.
- **Catalog [6487589](https://mod.io/g/transportfever3/m/suburban-tiny) (605, mods include `drive_in_warehouses_1`):** 9 of 13 records matched with the base rule. The other 4 are the gated records below.
- **Three more saves with the drive-in mod:** [6474988](https://mod.io/g/transportfever3/m/artic-start-small-1by-3-all-industries), [6446221](https://mod.io/g/transportfever3/m/optimal) and [6444792](https://mod.io/g/transportfever3/m/schnbau-b) (604): 9, 3 and 19 records without the mod's (0, 4) start matched the base rule.
- **Catalog [6481924](https://mod.io/g/transportfever3/m/tropical-paradice-updated) (604, the same mod):** the 22 records with modules matched. Its other 6 records carry `drive_in_*` keys and an empty `modules` table, so where their modules are kept is not known.

### The drive-in warehouses mod (604 and 605, Observed)

- **Keys.** With `drive_in_warehouses_1` in the mod list, records can carry `drive_in_access`, `drive_in_layout` and in some saves `drive_in_tram` (numbers 0 to 2). In [6474988](https://mod.io/g/transportfever3/m/artic-start-small-1by-3-all-industries) 9 of 18 records carry the keys and 9 start at cell (0, 4); in [6446221](https://mod.io/g/transportfever3/m/optimal) all 7 carry them and 4 start at (0, 4). In [6444792](https://mod.io/g/transportfever3/m/schnbau-b) 21 records carry the keys, 19 of them with `drive_in_layout` 2 and cell (0, 3), and only 2 start at (0, 4).
- **One cell off.** In 6474988 (9 records), 6446221 (4) and 6444792 (2), each one-module record at cell (0, 4) had its centre piece exactly 8 m from where the base rule puts it. In 6444792 the layout-0 one stands 27 m along the entrance's y: where a base (0, 3) module stands.
- **Gate module (605, 6487589).** Four records hold `drive_in_warehouses_1::/drive_in_warehouses/drive_in_gate.module` under a type-2 key, at cell (0, 21) in the one decoded. Their modules start at (0, 4). Each of the 4 fits exactly one entrance instance when the origin is 3 m from it and the axes come from the module pieces.
- **All-zero entrances.** Those four entrances (slots 150134, 151540, 250020 and 359706 in that save, as `model_instances.py` prints them) have a 3 × 3 rotation of all zeros, z axis too. Their translation is right and their modules' pieces have ordinary unit transforms. The 604 saves with the mod have no gate module and no such entrance among their warehouses. The 605 save [6496984](https://mod.io/g/transportfever3/m/nordstavic-slowed-train-issue) has the mod but only one warehouse, with no `drive_in_*` keys.
- **Spread out.** In 6487589 the gated warehouse whose entrance is at about (−435, −3081) has 7 modules in two blocks, at x = 0 and x = 6 to 10 cells. Its faces do not meet. The base slot rules do not offer a 6-cell step, so the gap is the mod's layout or a removed module. Open.

### Placement seen in 6487589 (605, Observed)

- **Side by side:** two warehouses with their entrance faces touching, entrances 40.1 m apart along their x, at about (268.5, −3224) and (268.5, −3264).
- **Back to back:** two pairs with origins 24 m apart and entrances facing away from each other, at about (1189, −5274) and (1171, −5275), and (1161, −5156) and (1179, −5156).
- **Preview block.** The tilted pages of the model preview block at the map's centre ([editor-saves.md](editor-saves.md#the-model-preview-block-near-00)) include warehouse models, among them an `entrance_sm` at about (140.5, 7.2) and a zero-transform one at about (15.6, −2.2); neither belongs to a record. `read_instances` leaves them out; a count of warehouses by raw entrance instances would include them, so count construction records instead.
