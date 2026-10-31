# Mods in the save: tests

The tests behind [mods.md](mods.md): what one load with a mod switched on or off changed in the header and the stream, two loads of a 14-mod save, and what each kind of mod left in a new game with seven. The conclusions are in "In short" there.

## What the tests showed

- **A switch on the Load Game screen's Mods tab reaches all three header places (Confirmed, 604, one load each way).** The mod list, the config-mods list and the params entry gain or lose the mod together, and nothing else in the stream names it.
- **The gear button does not deactivate a mod; the `Activated` button does (Observed, 604).**
- **Model mods leave their models in the model table; only the Deluxe Upgrade left a script state (Observed, 604, one new game).**

## Switching a mod on

**Switching a mod on.** **Confirmed** on 604, one load: a mod.io script mod, Overpass Builder ([6050917](https://mod.io/g/transportfever3/m/overpass-builder)), was activated on a save with two mods and the game was saved under a new name. Against the save before it:

- The header's mod list got a third entry after the existing two: id `move_it_probe_overpass`, source `mod.io`, path `6050917` (the mod.io id as text), the display name, the mod's page URL and flags 0.
- The config-mods list got the id appended.
- The config params got a new entry keyed by the id, holding an empty table (the mod has no options), placed just before the entry with the empty key. The two existing entries kept their order.
- The settings table, the resources, the money, the counter, the seed and the map size were unchanged. The header grew by 182 bytes.
- The mod's id occurs three times in the stream, all in the header (mod list, config-mods list, params key). Nothing after the header names it. The rest of the stream differs from the save before by 32 bytes in length and by some blocks, as every re-save does, and I did not check whether any of that is mod related.

## Switching a mod off

**Confirmed** on 604, one load: on that three-mod save the built-in script mod Vehicles: No End Year was deactivated (`urbangames_vehicles_no_end_year_1`, source `BuiltInMods`) and the game saved again. All three places lost it: the mod list went from three entries to two, the config-mods list lost the id, and the params entry keyed by it was dropped. The other entries kept their order, the settings and everything else in the header were unchanged, and the header shrank by 218 bytes. Its id (and its path string) occurs nowhere in the stream afterwards, so a deactivated mod leaves no trace behind. These mods had no options; a mod with options and a game script lost its params entry the same way on 605 ([In short](mods.md#in-short)).

## Two loads of one 14-mod save

Observed, 604, a Giant subarctic save. The Mods tab shows one card per mod, each with an `Activated` button and a gear button beside it, plus Mod Hub, Save Preset, Load Preset, Disable All Mods and a heading that gains an asterisk (`Mods (13) *`) once the list is changed.

- **First load.** Mods were deactivated with the gear icon, and the game was saved. The new save lists the same 14 mods, with the same flags, config-mods list and params keys, so nothing was deactivated and the game said nothing. Which mods were touched was not recorded.
- **Second load.** One mod was switched off on the tab (the heading read `Mods (13) *`). The new save has 13 mods: `urbangames_vehicles_no_end_year_1` was gone from the mod list, the config-mods list and the params keys, the order of the rest unchanged, the settings the same, and the header 218 bytes shorter, the same as in the switch-off test above.

- **Third load.** Two more were switched off on the tab (`Mods (11) *`): Early Road Vehicles and Early Trams (`ug_legacy_road_1850`, `ug_legacy_trams_1850`), two vehicle model mods, in a save with no vehicles. The next save has 11 mods, with both gone from the three places, the others in order, the settings unchanged and the achievements flag still 1 (the force mod is still in the list).

So the gear button does not deactivate: it opens the mod's details page, not its settings (the player's report), and the `Activated` button switches the mod off.

## Seven mods in one new game

A new game (604, subarctic, Normal difficulty) with seven mods active, saved at once (the first save of the [Small subarctic game](test-games.md#small-subarctic-game)), shows what each kind of mod leaves. **Observed**, one save.

| Mod | Header | Models in the table | Script state |
|---|---|---|---|
| Deluxe Upgrade (`urbangames_deluxe_upgrade_pack`) | yes | 31 | `fun_elements/balloon.gs` and a notification script entry, `balloon_notification.script` ([fun-elements.md](fun-elements.md)) |
| Early Road Vehicles (`ug_legacy_road_1850`) | yes | 8 | none seen |
| Early Trams (`ug_legacy_trams_1850`) | yes | 5 | none seen |
| Early Wagons (`ug_legacy_waggon_1850`) | yes | 3 | none seen |
| Early European Locomotives (`ug_legacy_rail_eu_1850`) | yes | 5 | none seen |
| Boathouse (`ingo_boathouse_asset`) | yes | 12 | none seen |
| Vehicles: No End Year (`urbangames_vehicles_no_end_year_1`) | yes | 0 | none |

- Every mod's id occurs three times in the header (mod list, config mods, config params). All seven params entries were empty tables.
- The model table, 272 KB after the header, held 4,537 entries: the base game's 4,473 (ids 0 to 4472) and then the mods' in the order of the table above (ids 4473 to 4536), each mod's models in one run. A mod's id then also occurs once per model in the table. The legacy vehicle mods add the vehicles' `_v2.mdl` models; Boathouse adds the boathouse and its fittings.
- Vehicles: No End Year has no models and no state, so it is only in the header, as the switching test above found. A mod that adds only rules or only data may leave nothing else.
- Mapzilla was installed and not activated, and left no trace.
- The mod entries are listed in the order the mods were activated in the game's mod list, and the config params entries come in the reverse order (**Observed**, this save; the order in the catalog was not checked against the activation order).
