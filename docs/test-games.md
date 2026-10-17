# Test games

The games of our own that the notes draw on, each described once so a note can name it and link here. All were made on the PC release (format 604). A game is identified by its map seed (the header's `id`, see [seed.md](seed.md)) together with its climate: one seed was played in two climates, and those are different maps. Save names are the ones the game wrote; the notes cite a save by the four-digit time at the end of its name (`1401`), and an autosave by its clock.

## In short

This note is a log by nature: each of our own test games described once, so another note can name it and link here. A game is its seed plus its climate. The main ones:

- **Small subarctic game:** the game most notes use (typed seed, seven mods, three towns, played from 1900).
- **Map-format tests:** a series of new games with every option set by hand and saved at once.
- **Editor games** (Tiny flat, Giant temperate): maps the editor built, edited one change per save.
- **Catalog games we re-saved:** mod.io saves that became test maps when we re-saved them.

## Small subarctic game

The game most notes use, played from a new game for the purpose of these tests.

- Seed `XNGDTtYKhe` (typed), subarctic climate and economy, Small 1 : 3 (4608 x 13824 m), start year 1900, Normal difficulty. Terrain sliders Water Small, Swamps Medium, Mountains Dense ([terrain.md](terrain.md#a-small-subarctic-map)).
- Seven mods: Deluxe Upgrade, Early Road Vehicles, Early Trams, Early Wagons, Early European Locomotives, Boathouse and Vehicles: No End Year ([mods.md](mods.md#seven-mods-in-one-new-game)).
- Three towns, Retford, Bromsgrove and Todmorden, entities 17,912 to 17,914 (the company is 17,911, [entity-names.md](entity-names.md#layout)).
- The calendar stood at 1 January 1900 until about clock 17.25 million and then ran at several speeds; its day table holds that history ([calendar-speed.md](calendar-speed.md#speed-changes-and-stops)).
- The main thread is a fish chain: fishing lines to a port at Todmorden, a warehouse beside it and a road line into the town, horse carts first and trucks from 1912 ([fish-chain.md](fish-chain.md#a-fish-chain-read-end-to-end-windows-groups-a-truck-queue-604)).
- **The horse carts by model (Observed, model instances counted in saves `1127` to `2113` and the autosave of 20 October 1917).** All are `truck` models; the `horsewagon` ones come from the Early Road Vehicles mod. The fish road line had three `horsewagon_1850_v2` from the start and four `horsewagon_1850_usa_v2` from clock 887,400, and all seven were sold in January 1912 for `benz1912_box` trucks. The stone line (quarry to `cement_plant`, from clock 1,095,400) had five `horsewagon_1850_usa_v2` and four `horse_cart_small`, sold in August 1917 for `benz1912_bulk` trucks. The private cars of 1900 are horse coaches too: `car` models `coach_01` to `coach_06`.
- A second chain carries stone from a quarry to a cement plant, and cement to a warehouse and on to Retford, on two road lines ([cement-chain.md](cement-chain.md)).
- Saves are named `test-small-subartic-seriesA-1010-<time>`, some with a word for what changed. One is a crash save the game wrote after an assertion failure ([header.md](header.md#preview)).

Notes that use it: [compass.md](compass.md), [parcels.md](parcels.md), [finances.md](finances.md), [running-costs.md](running-costs.md), [subsidies.md](subsidies.md), [notifications.md](notifications.md), [entity-names.md](entity-names.md), [lines.md](lines.md), [vehicles.md](vehicles.md), [town-records.md](town-records.md), [town-buildings.md](town-buildings.md), [town-states.md](town-states.md), [statistics-lists.md](statistics-lists.md), [fish-chain.md](fish-chain.md), [cement-chain.md](cement-chain.md), [industries.md](industries.md), [spoilage.md](spoilage.md), [calendar.md](calendar.md), [header.md](header.md), [terrain.md](terrain.md), [mods.md](mods.md).

## Large tropical game

- Seed `mSKhWzIuLq`, tropical climate and economy, Large 1 : 2 (10240 x 20480 m), start year 1900, Hard difficulty, Asian names, Town Density Sparse and Industry Density Packed, Ocean Large, Islands Dense, Mountains Sparse (from the New Game screen and the header). 14 mods, among them Deluxe Upgrade, Boathouse and Industry Upgrades.
- Eight towns and 29 industries, saved at once from the New Game screen (`test-large-trop-Caloocan-2610 <date>-<time>`); the screen's preview and the save agree on both counts.
- Used for: the compass words in industry names ([compass.md](compass.md)).

## Tiny tropical game

- Seed `RaazVnK55w` (typed), tropical, Asian names, Tiny 1 : 3 (2048 x 6144 m), start year 1900, two towns. Mods Deluxe Upgrade and Vehicles: No End Year.
- Made to test what a load changes: the seed in the header ([seed.md](seed.md)), settings changed on the Load Game screen and the difficulty presets ([settings.md](settings.md)), and a mod switched on and another off ([mods.md](mods.md#switching-mods-on-and-off-when-loading)). The second save switched the climate to temperate and the economy to dry on load, so later saves of this game hold those.
- Its tropical saves also serve [terrain.md](terrain.md#the-terrain-record) and [animals.md](animals.md).
- Saves are named `test-tiny-trop-20261010-<time>`, some with `-add-mod` or `-del-mod`.

## Map-format tests

Four new games made on 14 October 2026 (format 604), each saved at once from the New Game screen, to see what Map Size and Map Format do to the map ([map-sizes.md](map-sizes.md#tiny)) and whether every setting reads back as set ([settings.md](settings.md#the-options)).

- Seed `ic3DIKAw9j`, tropical, Asian names, Tiny with format 4 selected (2048 x 6144 m, 8 x 24 tiles), start year 1900, Hard difficulty, Deluxe Upgrade only, two towns. Ocean Large, Islands Scattered, Mountains Dense. Two saves were made from that screen, `1x3` and `1x4` in their names; the `1x3` one stored `map.format` 4, so that name was the wrong one. Both were deleted as easy to recreate, so only their header values (read before the deletion) remain here.
- Seed `5IeGyerPPH`, tropical, Asian names, Tiny 1 : 5 (1536 x 7680 m, 6 x 30 tiles), start year 1900, Custom difficulty (the Hard values with landmark resources Very High, inflation Low, delivery Normal, noise Very High and pollution Low, [settings.md](settings.md#difficulty-presets)), Deluxe Upgrade and No Costs, two towns. Same three sliders. The save is `teset-tiny-drop-custom-1x5-1014-0152` (the typos are in the name). Every stored setting matched the New Game screen.
- Seed `600CWy1Z1K`, dry climate with the Subarctic economy, English names, Tiny 1 : 2 (2560 x 5120 m, 10 x 20 tiles), start year 1940, Deluxe Upgrade and No Costs, two towns. Every option set by hand (Sunny, Continuous, Reputation On, all sensitivities Very High, Vehicle Costs 50%, Infrastructure Upkeep 75%, Reforestation Off and so on). Save `test-tiny-dry-1x2-1014`.
- Seed `lMp7WOweMS` (the screenshots show a capital I; the header reads a lowercase L), tropical climate with `all.eco`, Canadian (Ontario) names, Small 1 : 3 (4608 x 13824 m, 18 x 54 tiles), start year 1980, Deluxe Upgrade, No Costs and Canadian Names, five towns. Rainy, Evening, Tutorial On, Reputation Off, Noise Extreme, Pollution Off, Infrastructure Upkeep 150%. It was Tiny first; the tutorial warning ([settings.md](settings.md#the-options)) made the player raise the size. Save `test-trop-1x3-1014-0220`. Ocean and Islands were Medium on the Tiny screen and Very Large and Scattered on the Small one, Mountains Scattered then Sparse. Later the same day it was loaded and saved again as `test-trop-1x3-1014-0220 0349` (paused, 1 January 1980, four screenshots): the Tutorial welcome window opened again on load; the Towns tab listed five towns (Small Hamlet to Small Village, 92 to 312 people, 955 in all) and the Industries tab 15 industries ([industry-lifecycle.md](industry-lifecycle.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604)), matching the save; the company window showed Mechanic at 955 / 1,123 ([company.md](company.md#rank-thresholds)). Against the first save the re-save changed only the clock (1,600 to 3,000), the play speed (1x to paused), `experience` (952 to 955) and the mission state (7 tasks to 9, `isTutorialActive` still true); the towns, industries and names were identical, and loading did not change the first save's file.
- No Load Game screenshot of any of these exists yet. The first Tiny 1 : 4 test saves are gone; the other three are kept, and a new Tiny 1 : 4 game is among those below.

Five more Tiny games the same day, each set by hand on the Gameplay Settings screen and saved at once, with the New Game screens kept (Difficulty: Custom in all three):

- Seed `EKafpdyKC3`, temperate, European names, **Tiny 1 : 1** (4096 x 4096 m, readout 4.0 x 4.0 km), start year 1980, Deluxe Upgrade and No Costs, two towns, five industries on the screen. Cloudy, Morning, Tutorial Off, Reputation Off, Subsidies Rarely with Risk None, Infrastructure Costs 150% and Upkeep 50%, Vehicle Maintenance 50%, Reforestation Off. Save `test-temp-tiny-1x1-1014-0327`.
- Seed `Uwe7xjTzRZ`, subarctic with its own economy, German names, **Tiny 1 : 2** (2560 x 5120 m, readout 2.5 x 5.0 km), start year 1980, Deluxe Upgrade and Advanced Track Patterns, two towns, eight industries on the screen. Water Large, Swamps Scattered, Mountains Medium; Town Density Dense, Industry Density Scattered. Inflation Very High, Subsidies Risk Very Risky, Productivity 150%, Infrastructure Costs 50% and Upkeep 150%. Save `test-tiny-subartic-1x2-1014-0330`.
- Seed `BANeVeklMN` (the screen font shows an I or l; the header reads a lowercase L), tropical climate with the Subarctic economy, Romanian names from a name-list mod, **Tiny 1 : 3** (2048 x 6144 m, readout 2.0 x 6.0 km), start year 1980, Deluxe Upgrade and Advanced Track Patterns, two towns, five industries on the screen. Ocean Very Large, Islands Dense, Mountains Medium; Sunny, Local Time, Reputation On, Productivity 50%, Closing Very Often, Pollution Extreme. The Mods tab read "Mods (2)" while the save lists three. Save `test-tiny-trop-1x3-1014-0333`; its name matches its stored format 3, unlike the first game's `1x3` save, which stored 4. The Mods tab of this game was not photographed; the mod names are from the save.
- Seed `3hgeltiUsw`, dry climate with the Temperate economy, Swedish names, **Tiny 1 : 4** (2048 x 6144 m, readout 2.0 x 6.0 km), start year 1930, Deluxe Upgrade and Advanced Track Patterns, three towns and eight industries on the screen. Lakes Scattered, Rivers Packed, Mountains Sparse; Town Density Packed. Closing Never, Subsidies Risk Risky, Inflation Very High, Delivery, Noise and Pollution Extreme, Infrastructure Costs 50% and Upkeep 150%. Save `test-tiny-dry-1x4-1014-0337`: the stored format is 4 and the shape is 1 : 3 again, which settles the Tiny 1 : 4 case for a new game ([map-sizes.md](map-sizes.md#tiny)).
- Seed `bFMG7SxaPw`, tropical with `all.eco` (the screen reads "All Industries"), Asian names, **Tiny 1 : 5** (1536 x 7680 m, readout 1.5 x 7.5 km), start year 1950, Deluxe Upgrade and Advanced Track Patterns, two towns and six industries on the screen. Ocean Very Large, Islands Dense, Mountains Sparse; Cloudy, Night, Town Density Packed, Traffic Sensitivity Very High, Happiness Low, Delivery Extreme, Cargo Income 125%. Save `test-tiny-trop-1x5-1014-0339`.

The towns on the screens matched the saves in all of today's games; the industries did not always ([industry-lifecycle.md](industry-lifecycle.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604)).

## Tiny desert games

- Seed `ktb5aEVwZg`, dry, Tiny 1 : 4 (2048 x 6144 m), start year 1900: the cases A to G of [terrain.md](terrain.md#what-was-compared), the same seed with the sliders moved one at a time. A has no mods; the others have Deluxe Upgrade. The animals of [animals.md](animals.md) were read from them.
- Seed `sJn73SmfYh`, dry, Tiny, Deluxe Upgrade: one save, a second seed for the animal count.
- Saves are named `test-tiny-dry-...`, with series letters in the name.

## Tiny temperate games

- Seed `ktb5aEVwZg` again, now temperate, Tiny 1 : 4, start year 1900, Deluxe Upgrade, nothing built and no loan taken.
- Saved on 1 January, 11 May (an autosave) and 20 September 1900 and on 2 January 1901 at calendar speed 1.00x: the hot air balloon ([fun-elements.md](fun-elements.md)), loan offers renewing every half year ([company.md](company.md#loans)) and a header money of 0 with no starting capital ([header.md](header.md#money-in-the-header)).
- The same seed and climate are the Lakes pair of [terrain.md](terrain.md#lakes-on-a-temperate-map).
- Saves are named `test-temp-1010-seriesA-<time>` and `test-temp-1010-series-B-<time>`.

## The 2061 game

- Seed `6C7wugBwr8`, temperate, 11264 x 11264 m, no mods, start year 1900, played into 2060 and 2061.
- Saved paused from 6 February 2060 to 21 April 2061 at calendar speeds 4.00x, 2.00x and 0.50x: the rule that the date shown advances by the calendar speed times the clock ([calendar.md](calendar.md#the-game-clock)), script states read against the game's windows ([script-states.md](script-states.md)) and the year in the availability state ([notifications.md](notifications.md#the-availability-state)).
- Saves are named `New Game 20261008-<time>`.

## Tiny flat editor game

- Seed `tgzZmeqUSM`, tropical climate, economy `tropic` and Asian names, Tiny 1 : 3 (2048 x 6144 m), start year 1900, a map editor save (`isMapEditor` true, money 0, no mods). The ground is flat: `terrain_map.py` drew no height lines or bands at 20 m steps.
- Three files in `save_maps/`, named `tiny-flat-1x3` (the blank template), `tiny-flat-1x3 1937` (two towns, three industries and a country road drawn) and `tiny-flat-1x3 1938` (four bypasses added to the road); the numbers are part of the names the player gave, then saves `1939` to `1963` with a descriptive suffix (a delete, a road, a tree, a farm, a rock, bushes and palms from the tree tool, a brush-painted forest, a single click of the solid-circle brush). What they show is in [editor-saves.md](editor-saves-tests.md#a-blank-template-and-a-road-test). A second series from a fresh template of the same seed, `tiny-flat-1x3-1014` with a time and a suffix (`first-roads`, `first-smallest-town`, `add-largest-town`, `add-medium-town-3`) and two autosaves of the last, put a road network and then three towns on the map one at a time ([editor-towns.md](editor-towns.md)). A copy of save `1963` with `isMapEditor` set to false and put in `save/` loaded as a played game, and a re-save two seconds later showed the load dialog's experimental map size notice ([editor-play.md](editor-play.md#a-converted-editor-map-loaded-as-a-played-game)).

## Giant temperate editor game

- Seed `87gEXXsiaA`, temperate climate and economy, European names, Giant (20480 x 40960 m, header `map.size` 8), start year 1900, a map editor save (`isMapEditor` true, money 0). Twelve mods, among them Deluxe Upgrade, the Early Road Vehicles, Trams, Wagons and Locomotives sets, Boathouse, Overpass Builder and Industry Upgrades. 5,034 animals, 1,678 of them with flock offsets ([animals.md](animals.md)).
- Fourteen saves made one after the other in the map editor around the town Hemsworth, one change per save: the baseline, three buildings marked Historic Preservation, a deleted road segment, a new country road, a standalone country road with noise barriers, a load and re-save with no edit, a single house marked Historic Preservation, the town deleted, a load and re-save of that, and a chevron of Large Country Road With Noise Barrier drawn over the old town's ground, and a medium-width country road with noise barriers drawn in three segments to test the cut length, and a curved `town_old_large` road along the coast, then Save and Play (`0655`, saved in the editor) and a pause and save in the played game (`0656`). Each was saved from the game the one before it was. They are the basis of [road-network.md](road-network.md); the building ticks are in [editor-map-buildings.md](editor-map-buildings.md).
- Saves are named `2026-10 Giant Temper 1011-<time>`.

## Very Hard income game

- A temperate Giga map, start year 1900, played from a Normal-settings save and re-saved after changing settings on the Load Game tab ([settings.md](settings.md#changing-settings-when-loading)). Stored values in the new save: Cargo Income and Passenger Income 1 (50%), Inflation 5 (Very High), vehicle and infrastructure purchase cost and maintenance 5 (150%), industry productivity 1 (50%), subsidies 1 (Never).
- Game date January 1900, rank 3 (Engineer), `level` 1.
- Played with a script mod that logs the income function's inputs and results and the company state every so often. Used for: the multiplier in a running game ([inflation.md](inflation.md#in-a-running-game)).

## Tiny subarctic bus-line game

- Seed `Uwe7xjTzRZ`, subarctic climate and economy, German names, Tiny 1 : 2 (2560 x 5120 m), start year 1980, a new game with three mods: Deluxe Upgrade, Advanced Track Patterns (mod.io 6436197) and Transit Overlay (mod.io 6449851, [transit-overlay.md](transit-overlay.md)). Two towns, Kenzingen and Kulmbach.
- Eight saves made one after the other in the first minutes of the game, the clock stopped at 1 January 1980, named `test-tiny-subartic-1x2-1014 <time> <change>`: a loan, a road between the towns (with a bridge), a passenger station (`modular_terminal`, `STATIONS_STREET_PASSENGER`; its window lists Terminals) in one town, a second one in the other, a bus line between them, a road depot, a road maintenance building, and four buses bought. One Transit Overlay export was taken after the last save, and the player's screenshots show the speed-limit layer, the stations' catchment, and the maintenance building's and the depot's window with their circles. Later saves of the same game (a few minutes on): traffic lights added to junctions and their phases changed (`1000` to `1004`, with autosaves), a winding road of 21 edges (`1023`) and a curved rail (`1024`), with screenshots of the speed layer over both ([road-speeds.md](road-speeds.md)). What the first eight show: [line-ids.md](line-ids.md) (the line's id in the vehicle records), [transit-overlay.md](transit-overlay.md) (the export, the station catchment), [models.md](depots.md) (the circles).
- Six more saves in the same game, `0959` to `1004`, named `test-tiny-subartic-1x2-1014 <time> <change>`: traffic lights set up at four junctions (Type C, Type A, then two more), the same save again with no change, and one junction's six phases edited. What they show: [junctions.md](junctions.md#traffic-lights-604-observed).

## Catalog games we re-saved

Three catalog saves were loaded in the game and saved again, so they are tested as well as read. They are cited by mod id; only facts read from them are recorded.

| Catalog save | Map | Used for |
|---|---|---|
| [6417707](https://mod.io/g/transportfever3/m/333151) | Subarctic, 14336 x 14336 m, start 1900, no mods, re-saved from 17 April 2000 on | warehouses, stock lists, landmarks, subsidies, entity names, company rank |
| [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) | Temperate, 11264 x 22528 m, start 1900, Easy preset, no mods, shown as 18 February 1937 | a second warehouse game, the Paused calendar setting, the Easy preset |
| [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) | Tropical, 8192 x 24576 m, start 1960, no mods, shown as 14 February 2191 | the Finances tab, company rank and loans, entity names, calendar speed |

Our other editor maps and a few early saves are cited in the notes by description only.
