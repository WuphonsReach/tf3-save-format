# Mods in the save

What a save records about the mods a game uses: the entry in the header's mod list, the mod's options, the script state a mod keeps, and the model and notification entries that carry a mod's id. The first three rows of the table below are header fields. Checked on 568 to 604 unless a line says otherwise.

## What a save records about a mod

| Where | What | Note |
|---|---|---|
| Header, `mods` | One entry per mod: id, source, path, display name, `extra` URL, flags | [below](#the-mod-list-entry) |
| Header, `config mods` | The ids of the same mods | [below](#the-mod-list-entry) |
| Header, `config params` | One entry per mod keyed by its id, holding the mod's options (an empty table when it has none) | [below](#mod-options) |
| Script states | A mod with scripts keeps its state under its own script path, with the mod id string just before it | [script-states.md](script-states.md#mod-script-states-and-stored-errors) |
| Model table | A mod's models carry the mod's id in the source field | [models.md](models.md#the-model-table) |
| Notification entries | The `type` of a mod's notification carries the mod id before `::` | [notifications.md](notifications.md) |

A mod that is switched off before a load leaves nothing at all ([below](#switching-mods-on-and-off-when-loading)).

## The mod list entry

The header field `mods` is a `vec<mod>`. Each mod is five `str` and a u32: id, source, path, display name, extra, flags. Observed on the 120 catalog saves (568 to 604):

- `extra` holds the mod's mod.io page URL in 2,661 of 3,019 entries. It is empty in the rest: every `DLC` entry and most `BuiltInMods` entries.
- `flags` is 0, 1 or 2. Always 1 for source `DLC`, mostly 0 for `BuiltInMods`, any of the three for `mod.io`. Meaning **open**.
- The source is `DLC`, `mod.io` or `BuiltInMods` on every platform. In the one entry added by a test, source `mod.io`, the path was the mod.io id as text (see the Overpass Builder test below).
- **The config mods list repeats the ids** (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). It is the same set as the mod list.
- Mods whose page URL points to modwerkstatt.com instead of mod.io occur only in PC saves (7 saves, all 604). What that says about the platform is in [platform.md](platform.md).

## Mod options

- **Mods keep their options in the config params list** (**Observed** in the 110 catalog saves whose header reads to the end, 599 to 604). Besides the empty key there is exactly one entry per mod, keyed by the mod's id, so the list has one more entry than the config mods. All 3,002 mod entries matched an id in that save's mod list. A mod without options has an empty table; one with options holds its own keys, for example a toll mod's `toll` or a train mod's `acceleration`, `braking` and `curves`. The values are Lua numbers (f64), like the game settings, which are numbers apart from the bool `isMapEditor`. Whether mod values follow the same position-plus-1 rule is **Open**. The order is neither the mod list's order (it matched in 39 of 110 saves) nor sorted, so look entries up by key.
- The entry with the empty key holds the game settings, not a mod's options. See [settings.md](settings.md).

## Switching mods on and off when loading

The Load Game screen has a Mods tab next to the Settings tab described in [settings.md](settings.md#changing-settings-when-loading). A mod can be switched on or off there before the save loads (the tab's heading gains a count and an asterisk once something is changed). The next save then lists the mods as set on that tab, so like the settings, a save's mod list reflects the last load, not the game's start.

**Switching a mod on.** **Confirmed** on 604, one load: a mod.io script mod, Overpass Builder ([6050917](https://mod.io/g/transportfever3/m/overpass-builder)), was activated on a save with two mods and the game was saved under a new name. Against the save before it:

- The header's mod list got a third entry after the existing two: id `move_it_probe_overpass`, source `mod.io`, path `6050917` (the mod.io id as text), the display name, the mod's page URL and flags 0.
- The config-mods list got the id appended.
- The config params got a new entry keyed by the id, holding an empty table (the mod has no options), placed just before the entry with the empty key. The two existing entries kept their order.
- The settings table, the resources, the money, the counter, the seed and the map size were unchanged. The header grew by 182 bytes.
- The mod's id occurs three times in the stream, all in the header (mod list, config-mods list, params key). Nothing after the header names it. The rest of the stream differs from the save before by 32 bytes in length and by some blocks, as every re-save does, and I did not check whether any of that is mod related.

**Switching a mod off.** **Confirmed** on 604, one load: on that three-mod save the built-in script mod Vehicles: No End Year was deactivated (`urbangames_vehicles_no_end_year_1`, source `BuiltInMods`) and the game saved again. All three places lost it: the mod list went from three entries to two, the config-mods list lost the id, and the params entry keyed by it was dropped. The other entries kept their order, the settings and everything else in the header were unchanged, and the header shrank by 218 bytes. Its id (and its path string) occurs nowhere in the stream afterwards, so a deactivated mod leaves no trace behind. Whether a mod that has options loses them (the params table) the same way was not tested, as these two mods had none.

## Mod script states and stored errors

A mod with scripts keeps its state in the same layout as the game's scripts: the script's path string, then its table. How to find and read one is in [script-states.md](script-states.md#finding-a-table), and the mod-specific part is [there too](script-states.md#mod-script-states-and-stored-errors): the mod's id sits just before the path, and a mod can keep a Lua error message whose chunk name is a path on the player's machine. That path can hold an account name. Don't copy it into notes; write it as `<path>/mod.io/10640/mods/<id>/...`.

## Mods with notes of their own

- **Deluxe Upgrade** (`urbangames_deluxe_upgrade_pack`): the hot air balloon's script state, notification and model instance in [fun-elements.md](fun-elements.md); its 31 models in [models.md](models.md#the-model-table); the bison, boar and Komodo dragon it adds to the animal list in [animals.md](animals.md).
- **Mapzilla** (mod.io 6423494): adds a terrain generator and `mz_*` sliders to the New Game screen. Installing it adds nothing to the save. See [terrain.md](terrain.md#generators-and-the-mapzilla-mod).
- **Auto Passenger Cameras** (`dome_wagon_cameras`, mod.io 6422630): the `camera_bridge.gs` state and the error messages it keeps, in [script-states.md](script-states.md#mod-script-states-and-stored-errors).
- **Toll mods** (for example `epod_pay_your_tolls_tf3_1`, script `pyt/pyt_toll.gs`): a `toll` option in the params entry (above) and a script state under the mod's path.
- **Overpass Builder** (mod.io 6050917) and **Vehicles: No End Year** (`urbangames_vehicles_no_end_year_1`): the switching tests above.

## Open

- Whether a deactivated mod with options is dropped together with its options. Only mods with no options were switched on and off.
- What a mod adds to the script states once it has run in the game. Whether any of the stream differences in the Overpass Builder test are mod related was not checked.
- Whether mod options follow the position-plus-1 rule that the game settings follow ([settings.md](settings.md#how-a-setting-is-stored)).
- What `flags` in a mod entry means (0, 1 or 2).
