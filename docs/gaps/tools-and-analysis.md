# Gaps: tools and analysis

Format of an entry: see [README.md](README.md). These are gaps in what the repo's tools and worked examples can do, not in the format.

## Steps that still need a private script

- **Searching the entity-name table** The notification reader was promoted to `tools/notifications.py`; a reader for the name table (find a name, list consecutive slots) is not in `tools/`. Home: [entity-names.md](../entity-names.md), [tools/README.md](../../tools/README.md). Needs: a script, with a row in `tools/README.md`.
- **Reading the trip array, the cargo-unit records and the town and stock records** Each was read with a throwaway script; no tool in `tools/` lists them. Home: [line-ids.md](../line-ids.md), [lines.md](../lines.md), [town-records.md](../town-records.md). Needs: a script once the layout is settled.
- **Tying a statistics group to a stop, station or warehouse** See [owners-and-links.md](owners-and-links.md#statistics-groups). `tools/items_lists.py` lists groups and differences per period but names only industries tied by hand.
- **Rows of the worked example's support table marked Gap or Partly** Which line, which vehicles and why; the line's stops and the departure choice; which stops belong to one station. Home: [analysis-examples](../analysis-examples/clothes-train2-supply-chain-starvation-6425796.md). Update the table as each step stops needing a private script.

## Tool defects

- **`KNOWN_IDS` in `tools/tf3save.py` is wrong for games with cargo mods** Cargo ids are positions in the save's own cargo list; `tf3save.cargo_list` reads that list, `KNOWN_IDS` does not. Home: [cargo-ids.md](../cargo-ids.md). Needs: check each caller, then switch them to the save's list; keep function names and return shapes stable (private scripts import them).
- **`items_lists.py` against a mod game's ids** The lists store each cargo id; whether the script labels them from the save's list in a game with a cargo mod was not tested. Home: [cargo-ids.md](../cargo-ids.md). Needs: a save from the sugar mod game (mod.io 6436164).

- **The model table can skip ids, and `read_model_table` stops on it** (604, one game) Catalog save 6417707 (subarctic, 14336 x 14336, no mods) has 4,473 table entries whose ids rise to 4,486: 14 ids are missing, in six places (one between the quarry's `q_main_building.mdl` and `q_particles.mdl`, one in the airport models, four runs among the water-station models). The user's re-save of it keeps the same ids, and a re-save of 6425796 has none missing. `read_model_table` in `tools/model_instances.py` requires each id to equal its index and raises "no model table found", so `industry_compass.py`, `terrain_map.py --depots` and anything else built on it cannot read this game. The note says the ids are the index into the table, which this save contradicts. Not known: why the ids skip (models dropped after the save was first made is a guess, **Open**), whether other older catalog saves skip too, and whether an instance's model id is the stored id or the index. Home: [models.md](../models.md#the-model-table). Needs: *existing saves* (read the table of each catalog save and count missing ids; check which id a model instance carries against a path whose id differs from its index), then change the reader to return paths by id and fix the note.

## Saves not yet compared

- **Other saves of a catalog game at other play speeds** The game of catalog save 6425796 was re-saved at several play speeds in one clock family; headers (`tools/save_header.py`, `tools/calendar_speed.py`) and what else moved were not compared. Home: [calendar-speed.md](../calendar-speed.md). Needs: existing saves.
