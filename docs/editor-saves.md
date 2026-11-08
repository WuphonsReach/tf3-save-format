# Map editor saves

Checked on 604.

## In short

All 604, except the regular-save conversion (checked once on one 34-town save).

- **A map editor save has the same container, header layout and settings keys as a regular save; `isMapEditor` is `true` (Observed).** Header money is 0, the counter is low (or the residents of the towns drawn), the info table is empty, and the set of script states differs.
- **Setting `isMapEditor` to `true` in a regular save and writing it into `save_maps/` makes the game list it under Load Custom Map and open it in the editor (Confirmed once).** It is one byte, so nothing moves. Money, journal and script states stay in the file.
- **A blank template holds almost nothing: counter 0, a 5.0 MB stream, no towns, industries, street edges or parcels (Observed, one Tiny map).** The first save after drawing towns and industries is a different file in kind (13.9 MB, 147 edges, 1,474 parcels).
- **A load and re-save is not a byte copy (Observed, once):** about 2.9 KB longer, with a counter of 8 going to 10 over 1.8 MB of records, 130 small records reordered, 17 ids added to the free-id list and a block of Lua tables added. Compare an edited save with a no-edit re-save first.
- **A delete reaches the street-edge table only with the next new road that brings edges of its own (Observed, five deletes in two series, a farm counts, a tree, a rock and passing days do not).** The delete itself is recorded at once in a list beside the edge-addon names (a count and 21-byte entries), but what the ids name is Open.
- **Drawing re-cuts the roads it meets, keeping their total length, and adds a path without taking any away (Observed);** a bypass leaves the old road in place. Tram roads are street types in the same table.
- **A road drawn beside a farm can remove one of its fields (Observed, once);** find the fields by the string `::/industries/livestock_farm/field.module`.
- **Editing leaves the strip and parcel tables alone for roads in open ground and deleted town-road pieces (Observed, the editor-map series).**
- **A deleted industry keeps its construction record and all its model instances, for three saves at least; only its ids in the free-id list mark it (Observed, 605, one map).** Count or draw industries with that test: [industry-records.md](industry-records.md#deleted-industries).
- **A block of model records near 0,0 is not map content (Observed, 604 and 605: one Giant editor map, a game started from it, and four catalog saves of regular games).** About 1,300 records in the editor map, 21,000 to 115,000 in the catalog saves, within 485 m of the origin; some saves' pages are tilted and scaled. It lists many models (industry, station, infrastructure, landmark, cargo and character parts), laid out in a grid of cells, and the game draws none of it. A map script that reads model instances then shows a phantom industry cluster at 0,0. It can be told apart without position, see [The model preview block](#the-model-preview-block-near-00). What it is for and which action writes it are **Open**.
- **The Towns / Industries dialog's proposals are not in the save (Observed).** The dialog's preview map shows towns in white, existing industries in brown and the industries a Generate would add in gold; the totals follow the density slider and the gold ones have no record until placed.
- **Open:** what the 4-byte counter near the end of the stream counts, what the three growing lists and the delete-list ids hold, and what the editor does with a converted save's money and journal.

## Compared with regular saves

- Same container, same header layout, same settings keys.
- The setting `isMapEditor` is `true` (see [header.md](header.md), "Settings").
- Header money is 0 and the counter is low (0, 1024 and 1678 seen); with towns drawn it counts their residents ([editor-towns.md](editor-towns.md#the-header-counter-is-the-number-of-residents)). The info table is empty.
- A different set of script states, and an empty `townStates` table.
- Town records are in the same layout, so the town component is not editor-only. The last 17 bytes of each record are zero.
- Starting cargo is in two places: the town record and the stock records of the town's existing buildings. Patching only the record changes the export and not the buildings ([building-stocks.md](building-stocks.md)).
- The entity data as a whole was not compared, so other differences are possible.

The game keeps editor saves in `save_maps/` and regular saves in `save/`, both under the game's `local/` folder in Steam userdata.

## Converting a regular save into an editor map

**Confirmed** once, on a 34-town, 53-industry save with a 618 MB stream:

1. Set `isMapEditor` to `true` in the settings. In the stream this is one byte (the boolean payload), so nothing moves.
2. Write the save back (see [container.md](container.md)) into `save_maps/`, with a copy of its `.jpg`.

The game lists it under Load Custom Map and opens it in the map editor. The Towns / Industries export works, with towns and industries at their positions. Money, journal, script states and the rest of the game state stay in the file. What the editor does with them is **open**.

tf3-save-editor's CLI can make the change: `tf3se-cli settings SAVE --set isMapEditor=true -o NEW.sav`.

## The model preview block near 0,0

**Observed**, 604 and 605. A block of bare model instance records, one page after another. It was found in an editor map, but ordinary games carry it too (below):

- Each record is a model id and a 64-byte matrix with nothing around it, 68 bytes after the previous one, so it lacks the repeated rotation that follows a real instance ([models.md](models.md)).
- In the editor map the matrix has no rotation: x scale about 0.08 to 1.5, y scale 0.875 or 1, z scale 1, translation in a grid of 3 columns by 5 rows of cells (x 0, 12, 24, y -7 to 7, z 0), six records to a column.
- Model ids rise by one along a page (pages of 6 to 36 records); between pages sits a trailer of 56 to 124 bytes.
- The models are alphabetical by directory (`cargos`, `characters`, `depots`, `game_mechanics`, `industries`, `infrastructure`, `landmarks`, `model_editor`, `placeholders`, `stations`, `assets`). Industry models alone are 168 records of 16 of the 23 industry directories, which is why a map of industries shows a cluster of every kind at 0,0.

It sits about 5.7 MB into the stream, ahead of the real instances, and appears from one editor save on and then stays (also in a game started from the map). A page's records carry no flag.

- **Regular games carry it too (604 and 605, four catalog saves, `isMapEditor` false).** [6417707](https://mod.io/g/transportfever3/m/333151) holds 114,888 records at 26 to 34 MB into the stream, all without rotation, up to 216 m from the origin. [6481924](https://mod.io/g/transportfever3/m/tropical-paradice-updated) holds 21,596, [6487589](https://mod.io/g/transportfever3/m/suburban-tiny) 99,768 and [6474988](https://mod.io/g/transportfever3/m/artic-start-small-1by-3-all-industries) 52,410.
- **Some pages are tilted and scaled.** In 6487589 and 6474988 long pages mix plain records with tilted ones (a turn about y, x scales from 0.01 to 27), mostly in rows along x at y −2.2 and 7.2, reaching 485 m from the origin: 9,334 and 22,764 records with rotation. 6481924 has 397. They were first read as "model catalogue rows" in tf3-save-mapper.
- **The signature.** A page is a run of two or more records exactly 68 bytes apart with model ids rising by one, whatever the transform: a real instance has more bytes after its matrix, so two never sit that close. A lone record counts only if it has no rotation. The block is pages of six or more, plus short pages within 200 bytes of one. Over the 320 catalog saves no page found this way holds a model tf3map draws (tunnels and bridges, industries, depots, stations, warehouses, vehicles) away from the origin, and every page lies within 485 m of it (tf3-save-mapper PR #48, 2026-11-08, 605 and earlier). [model_instances.py](../tools/model_instances.py) leaves the block out of `read_instances` by this signature, so the maps, `industry_counts.py` and `industry_compass.py` do not show it.

 Why it is written (the model trailers hold world coordinates that look like a camera) and which editor action first writes it are **Open**.

## Evidence and tests

The dated tests are in [editor-saves-tests.md](editor-saves-tests.md): [what editing in the map editor writes](editor-saves-tests.md#what-editing-in-the-map-editor-writes), [a blank template and a road test](editor-saves-tests.md#a-blank-template-and-a-road-test) and [a running clock, a tree, a farm and a rock](editor-saves-tests.md#a-running-clock-a-tree-a-farm-and-a-rock).
