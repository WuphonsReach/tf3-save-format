# Mods in the save

What a save records about the mods a game uses: the entry in the header's mod list, the mod's options, the script state a mod keeps, and the model and notification entries that carry a mod's id. The first three rows of the table below are header fields. Checked on 568 to 604 unless a line says otherwise.

## In short

- **Three places in the header (Observed, 568 to 604).** A mod has an entry in the `mods` list, its id in the config-mods list, and a keyed entry in the config params list that holds its options (an empty table when it has none). Mods that add content also leave their id in the model table's source field, in a script-state path and in notification types.
- **Switching on or off at load (Confirmed, 604, one load each).** The Mods tab on the Load Game screen adds a mod to, or drops it from, all three places in the next save, so a save's mod list reflects the last load. A deactivated mod left no trace elsewhere in the stream. On 604 tested only on mods with no options and no models in use; a mod with options on 605 (next bullet but one).
- **Removal warnings** follow the manifest's `severityRemove` (Observed, 306 manifests read).
- **A mod with options and a game script drops out whole (Observed, 605, one load).** Deactivated on Load Game and saved, it left no `params` entry (mods 21 to 20), so re-activating it later starts from its defaults.
- **Every mod option is stored as a 1-based list position (Observed, 605).** Sliders, drop-down lists and check boxes alike: the save and the mod's scripts get the position in the option's `values` list, never the shown value. A save without a value gets the option's default, so inserting an entry in a list moves old saves to another entry ([Mod options](#mod-options)).
- **Loading without a mod that had a game script removes the script's entity (Observed, 605, twice),** state and event subscriptions with it ([below](#mod-script-states-and-stored-errors)).
- **A mod's files are found through its `_content.json` (Observed, 605).** A file the list leaves out cannot be loaded ([Loading a mod's files](#loading-a-mods-files)). What a game script can and cannot do in play is in [game-scripts.md](game-scripts.md).
- **A mod entry's last field is the mod's `severityRemove` (Observed, 599 to 605).** 0 None, 1 Warning, 2 Critical, as set in the mod's `mod.json`: the warning level shown before the mod is removed ([The mod list entry](#the-mod-list-entry)). Whether a mod may still earn achievements (`cosmetic`) is not kept per mod; it feeds the save's one achievements flag ([header.md](header.md#the-two-flags)).
- **Open.** Models in use, and the value the game gives a mod whose `mod.json` has no `severityRemove`.

## What a save records about a mod

| Where | What | Note |
|---|---|---|
| Header, `mods` | One entry per mod: id, source, path, display name, `extra` URL, `severityRemove` (`flags`) | [below](#the-mod-list-entry) |
| Header, `config mods` | The ids of the same mods | [below](#the-mod-list-entry) |
| Header, `config params` | One entry per mod keyed by its id, holding the mod's options (an empty table when it has none) | [below](#mod-options) |
| Script states | A mod with scripts keeps its state under its own script path, with the mod id string just before it | [script-states.md](script-states.md#mod-script-states-and-stored-errors) |
| Model table | A mod's models carry the mod's id in the source field | [models.md](models.md#the-model-table), and [below](#seven-mods-in-one-new-game) |
| Notification entries | The `type` of a mod's notification carries the mod id before `::` | [notifications.md](notifications.md) |

A mod that is switched off before a load leaves nothing at all ([below](#switching-mods-on-and-off-when-loading)).

## The mod list entry

The header field `mods` is a `vec<mod>`. Each mod is five `str` and a u32: id, source, path, display name, extra, flags. Observed on the 120 catalog saves (568 to 604):

- `extra` holds the mod's mod.io page URL in 2,661 of 3,019 entries. It is empty in the rest: every `DLC` entry and most `BuiltInMods` entries.
- **`flags` is the mod's `severityRemove`** (**Observed**): 0 for `None`, 1 for `Warning`, 2 for `Critical`, the levels of `Mod.ModDesc.severityRemove` in the game's type definitions (`api/tealdef/api/type/mod.d.tl`, where `GameModDesc` lists a mod's id, source, mod hub id, name and `severityRemove`, the same fields as this entry). It matched on every mod whose installed `mod.json` sets the key: 25 mods in 60 of our own saves (605), the one `Critical` mod (`amos_weapons_industry_1`) stored as 2, and 24 mods in the catalog saves (599 to 604). Two mods with no key in their `mod.json` (`maikc_depot_modern`, `deadeye_tpf3_bus_bay`) were stored as 1 in our saves, so the default may be `Warning`, but one catalog save has 2 for the second, perhaps from an older revision (**Open**). DLC entries are always 1, `BuiltInMods` mostly 0, and four catalog mods changed value between saves, which fits a manifest changed between revisions. The tools keep the name `flags`. The removal warning itself is described [below](#switching-mods-on-and-off-when-loading).
- The source is `DLC`, `mod.io` or `BuiltInMods` on every platform. In the one entry added by a test, source `mod.io`, the path was the mod.io id as text (see the Overpass Builder test below).
- **The config mods list repeats the ids** (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). It is the same set as the mod list.
- Mods whose page URL points to modwerkstatt.com instead of mod.io occur only in PC saves (7 saves, all 604). What that says about the platform is in [platform.md](platform.md).

## Mod options

- **Mods keep their options in the config params list** (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). Besides the empty key there is exactly one entry per mod, keyed by the mod's id, so the list has one more entry than the config mods. All 3,002 mod entries matched an id in that save's mod list. A mod without options has an empty table; one with options holds its own keys, for example a toll mod's `toll` or a train mod's `acceleration`, `braking` and `curves`. The values are Lua numbers (f64), like the game settings, which are numbers apart from the bool `isMapEditor`. A `CheckBox` option (`"uiType": "CheckBox"`, values `["Off","On"]`, `defaultIndex` 1) is stored as a list position plus 1 like a settings slider: 1 unticked, 2 ticked (**Observed**, 605, one save: a mod's `...staleWarnings` key held 1.0 for unticked). The mod manager shows it that way (`gui/menu/mod_manager_react_util.tl`, `gui/main/script_param_util.tl` in `gui.zip`: the shown value is the stored one minus 1). The order is neither the mod list's order (it matched in 39 of 110 saves) nor sorted, so look entries up by key.
- The entry with the empty key holds the game settings, not a mod's options. See [settings.md](settings.md).
- **Sliders and lists follow the same rule (Observed, 605).** A `Slider` or `ComboBox` option reaches the mod's scripts, and is stored, as its 1-based position in `values`. Sliders of 21 and 41 values (5% steps) were checked on five saves and a list on two: the settings dialog, the header and the values the script logged agreed on every one. A list stored 2 and 3 for its second and third entries. A param's `numbers` array is not passed to scripts, so a mod keeps its own table from position to value. A game script reads the options with `api.engine.config.getModParams()`, keyed by mod id with the game settings under the empty key; a mod's `preRunFn` gets the same table as `allModParams`.
- **Where the player sets them.** In the dialog behind the mod's gear on the Mods tab, on New Game and on Load Game, not under Gameplay Settings. Load Game opens it with the save's own values. A value changed there before the load reaches the scripts, and the next save stores it. The dialog never shows a param's `tooltip`: its rows are built from the type, default, name and values only (`gui/menu/mod_manager_react_util.tl`), and hovering a setting shows nothing.
- **Missing and extra keys (Observed, 605).** A save with no value for an option shows and hands the scripts the `mod.json` default, and the next save writes it. That covers a save made before the mod had the option and a save that never had the mod, and a script cannot tell such a value from a chosen default. A key the mod no longer declares is ignored, and the next save leaves it out (two saves). Because only positions are stored, inserting an entry in a list moves old saves to another entry: a save that stored 2 on a three-entry list loaded as the new second entry once the list had four (one save).

Source for the last three bullets: the Best Before mod's [findings.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/findings.md#what-a-mod-can-and-cannot-do) ("What a mod can and cannot do"), with the test tables in [changing-settings.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/changing-settings.md) and the list renumbering in [TODO.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/TODO.md#half-bonus-for-non-perishable-cargo) (tf3-best-before-mod, at commit 5f4b203).

## Switching mods on and off when loading

The Load Game screen has a Mods tab next to the Settings tab described in [settings.md](settings.md#changing-settings-when-loading). A mod can be switched on or off there before the save loads (the tab's heading gains a count and an asterisk once something is changed). The next save then lists the mods as set on that tab, so like the settings, a save's mod list reflects the last load, not the game's start.

A switch reaches the load through the params table: the dialog script (`gui/menu/savegame_react_util.tl` in `base/content/gui.zip`) hands the load the save's `info` with only `modParams` replaced by the tab's edited copy, so a deactivated mod's key is missing and the load drops the mod from all three places. The tests are under [Evidence and tests](#switching-a-mod-on).

**Warnings on removal.** Removing some mods first shows a warning, and not others: none for `urbangames_vehicles_no_end_year_1`, `ingo_boathouse_asset`, `bobdike_achievements_unbound` or `advanced_track_patterns`, a warning for the `ug_legacy_*` vehicle mods, the Deluxe Upgrade and `stardorn_industry_upgrades`. That matches the `severityRemove` key in each mod's `mod.json` (`None`, `Warning` or `Critical`; the API says a value above 0 raises the message, `api/tealdef/api/type/mod.d.tl`), which was `Warning` in 22 of the 306 manifests read here, `Critical` in one and absent or `None` in the rest. A mod may carry `severityAdd` the same way (`stardorn_industry_upgrades` has `Warning`). **Open:** whether a mod with a script state (`advanced_track_patterns`, `stardorn_industry_upgrades`) or with models the save uses (a vehicle or asset on the map) can be switched off the same way; the model mods dropped here had nothing placed. A first look at the other case (**Observed**, 604, once, the load not saved): loading a Giant temperate editor map with `urbangames_deluxe_upgrade_pack` switched off showed a Loading Report saying that the pack's `boar_m` and `boar_y` model instances (`/animal/boar_m/boar_m.mdl`, `/animal/boar_y/boar_y.mdl`) would be replaced by placeholders. So models the save uses are named at load, not dropped silently.

## Mod script states and stored errors

A mod with scripts keeps its state in the same layout as the game's scripts: the script's path string, then its table. How to find and read one is in [script-states.md](script-states.md#finding-a-table), and the mod-specific part is [there too](script-states.md#mod-script-states-and-stored-errors): the mod's id sits just before the path, and a mod can keep a Lua error message whose chunk name is a path on the player's machine. That path can hold an account name. Don't copy it into notes; write it as `<path>/mod.io/10640/mods/<id>/...`.

**Without its mod (Observed, 605, twice).** Loading a save made without a mod that had a game script logs `Removing entity <id> for GameScript <mod id>::/<script>.gs which is no longer available`. The script's state and its event subscriptions go with the entity and nothing else fails. A shown notification of a type that mod registered is the exception ([notifications.md](notifications.md#persistent-warnings)).

## Loading a mod's files

**Observed** on 605 while one script mod was built and published. Source: the Best Before mod's [findings.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/findings.md#what-a-mod-can-and-cannot-do), [publishing.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/docs/publishing.md) and the 1.0.1 entry of [CHANGELOG.md](https://github.com/WuphonsReach/tf3-best-before-mod/blob/5f4b203e701cda7de243e0d16bdc8997e298dadc/CHANGELOG.md) (tf3-best-before-mod, at commit 5f4b203).

- **The file index is `_content.json`.** The game builds a mod's file index from the list in `_content.json`, not from the folder. A file on disk that the list leaves out is not found (`module '<mod id>::/settings.tl' not found`). When a mod's first script fails that way the game answers "Could not initialize game: try removing the mod" and goes back to the main menu. The mod's first published file had that fault, and a list naming every file fixed it.
- **A mod loads its own modules with `ug_require "<mod id>::/file.tl"`.** The shorthand `::/file.tl` does not resolve in `mod.script`, and a failing load there aborts initialisation the same way.
- **Two copies with one id: the staging copy wins.** With a copy in the game's `staging_area` folder and a subscribed mod.io copy of the same id, the game logs `Multiple (2) mods with same id found <id>, the one from .../staging_area/<id>/ has been selected` and runs the staging copy. The Mods list shows one card (seen once).
- **The number on an activated mod's card is its activation order** on the Mods tab sorted by Activation Order.
- **Publishing goes only through the game's uploader** (Mod Hub, My Mods), which reads `_metadata/modinfo.json`; the mod.io website refuses uploads for this game. mod.io labels every file uploaded this way "1.0", whatever the mod's `revision` (seen on three uploads); the game's log names the revision as `rev. <revision>`.

## Mods with notes of their own

- **Deluxe Upgrade** (`urbangames_deluxe_upgrade_pack`): the hot air balloon's script state, notification and model instance in [fun-elements.md](fun-elements.md); its music playlist in [script-states.md](script-states.md#the-music-player-state); its 31 models in [models.md](models.md#the-model-table); the bison, boar and Komodo dragon it adds to the animal list in [animals.md](animals.md).
- **Canadian Names** (`spearin_names_canadian`, mod.io 5860216): choosing the name list Canadian (Ontario) on the New Game screen put it in the header's mod list (source `mod.io`, flags 1) and the config-mods list, and the `nameList` resource became `canada_on.names`. The Mods tab on that screen still read "Mods (2)" (Deluxe Upgrade and No Costs) while the save listed three, so a name-list mod is counted in the save and not on the tab (**Observed**, two saves: also a Romanian list from the mod `dh106_names_romania` on a Tiny 1 : 3 game, 604; the Asian, English, European and German lists added no mod).
- **Mapzilla** (mod.io 6423494): adds a terrain generator and `mz_*` sliders to the New Game screen. Installing it adds nothing to the save. See [terrain.md](terrain.md#generators-and-the-mapzilla-mod).
- **Auto Passenger Cameras** (`dome_wagon_cameras`, mod.io 6422630): the `camera_bridge.gs` state and the error messages it keeps, in [script-states.md](script-states.md#mod-script-states-and-stored-errors).
- **Toll mods** (for example `epod_pay_your_tolls_tf3_1`, script `pyt/pyt_toll.gs`): a `toll` option in the params entry (above) and a script state under the mod's path.
- **Overpass Builder** (mod.io 6050917) and **Vehicles: No End Year** (`urbangames_vehicles_no_end_year_1`): the switching tests under [Evidence and tests](#switching-a-mod-on).

## Open

- Whether mods with models in use on the map drop out the way the no-option ones did (a mod with a game script did, on 605).
- A deactivated mod with options was tested once, on 605 ([In short](#in-short)), a mod without a game script and with options not at all.
- What a mod adds to the script states once it has run in the game. Whether any of the stream differences in the Overpass Builder test are mod related was not checked.
- What the game stores for a mod whose `mod.json` has no `severityRemove` (two mods: 1 in our saves, 2 in one catalog save).

## Evidence and tests

### Switching a mod on

**Switching a mod on.** **Confirmed** on 604, one load: a mod.io script mod, Overpass Builder ([6050917](https://mod.io/g/transportfever3/m/overpass-builder)), was activated on a save with two mods and the game was saved under a new name. Against the save before it:

- The header's mod list got a third entry after the existing two: id `move_it_probe_overpass`, source `mod.io`, path `6050917` (the mod.io id as text), the display name, the mod's page URL and flags 0.
- The config-mods list got the id appended.
- The config params got a new entry keyed by the id, holding an empty table (the mod has no options), placed just before the entry with the empty key. The two existing entries kept their order.
- The settings table, the resources, the money, the counter, the seed and the map size were unchanged. The header grew by 182 bytes.
- The mod's id occurs three times in the stream, all in the header (mod list, config-mods list, params key). Nothing after the header names it. The rest of the stream differs from the save before by 32 bytes in length and by some blocks, as every re-save does, and I did not check whether any of that is mod related.

### Switching a mod off

**Confirmed** on 604, one load: on that three-mod save the built-in script mod Vehicles: No End Year was deactivated (`urbangames_vehicles_no_end_year_1`, source `BuiltInMods`) and the game saved again. All three places lost it: the mod list went from three entries to two, the config-mods list lost the id, and the params entry keyed by it was dropped. The other entries kept their order, the settings and everything else in the header were unchanged, and the header shrank by 218 bytes. Its id (and its path string) occurs nowhere in the stream afterwards, so a deactivated mod leaves no trace behind. These mods had no options; a mod with options and a game script lost its params entry the same way on 605 ([In short](#in-short)).

### Two loads of one 14-mod save

Observed, 604, a Giant subarctic save. The Mods tab shows one card per mod, each with an `Activated` button and a gear button beside it, plus Mod Hub, Save Preset, Load Preset, Disable All Mods and a heading that gains an asterisk (`Mods (13) *`) once the list is changed.

- **First load.** Mods were deactivated with the gear icon, and the game was saved. The new save lists the same 14 mods, with the same flags, config-mods list and params keys, so nothing was deactivated and the game said nothing. Which mods were touched was not recorded.
- **Second load.** One mod was switched off on the tab (the heading read `Mods (13) *`). The new save has 13 mods: `urbangames_vehicles_no_end_year_1` was gone from the mod list, the config-mods list and the params keys, the order of the rest unchanged, the settings the same, and the header 218 bytes shorter, the same as in the switch-off test above.

- **Third load.** Two more were switched off on the tab (`Mods (11) *`): Early Road Vehicles and Early Trams (`ug_legacy_road_1850`, `ug_legacy_trams_1850`), two vehicle model mods, in a save with no vehicles. The next save has 11 mods, with both gone from the three places, the others in order, the settings unchanged and the achievements flag still 1 (the force mod is still in the list).

So the gear button does not deactivate: it opens the mod's details page, not its settings (the player's report), and the `Activated` button switches the mod off.

### Seven mods in one new game

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
