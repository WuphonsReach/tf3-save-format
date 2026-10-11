# Test games

The games of our own that the notes draw on, each described once so a note can name it and link here. All were made on the PC release (format 604). A game is identified by its map seed (the header's `id`, see [seed.md](seed.md)) together with its climate: one seed was played in two climates, and those are different maps. Save names are the ones the game wrote; the notes cite a save by the four-digit time at the end of its name (`1401`), and an autosave by its clock.

## Small subarctic game

The game most notes use, played from a new game for the purpose of these tests.

- Seed `XNGDTtYKhe` (typed), subarctic climate and economy, Small 1 : 3 (4608 x 13824 m), start year 1900, Normal difficulty. Terrain sliders Water Small, Swamps Medium, Mountains Dense ([terrain.md](terrain.md#a-small-subarctic-map)).
- Seven mods: Deluxe Upgrade, Early Road Vehicles, Early Trams, Early Wagons, Early European Locomotives, Boathouse and Vehicles: No End Year ([mods.md](mods.md#seven-mods-in-one-new-game)).
- Three towns, Retford, Bromsgrove and Todmorden, entities 17,912 to 17,914 (the company is 17,911, [entity-names.md](entity-names.md#layout)).
- The calendar stood at 1 January 1900 until about clock 17.25 million and then ran at several speeds; its day table holds that history ([calendar.md](calendar.md#the-calendar-speed-field)).
- The main thread is a fish chain: fishing lines to a port at Todmorden, a warehouse beside it and a road line into the town, horse carts first and trucks from 1912 ([statistics-lists.md](statistics-lists.md#a-fish-chain-read-end-to-end-windows-groups-a-truck-queue-604)).
- Saves are named `test-small-subartic-seriesA-1010-<time>`, some with a word for what changed. One is a crash save the game wrote after an assertion failure ([header.md](header.md#preview)).

Notes that use it: [finances.md](finances.md), [running-costs.md](running-costs.md), [subsidies.md](subsidies.md), [notifications.md](notifications.md), [entity-names.md](entity-names.md), [lines.md](lines.md), [vehicles.md](vehicles.md), [town-records.md](town-records.md), [town-buildings.md](town-buildings.md), [town-states.md](town-states.md), [statistics-lists.md](statistics-lists.md), [industries.md](industries.md), [spoilage.md](spoilage.md), [calendar.md](calendar.md), [header.md](header.md), [terrain.md](terrain.md), [mods.md](mods.md).

## Tiny tropical game

- Seed `RaazVnK55w` (typed), tropical, Asian names, Tiny 1 : 3 (2048 x 6144 m), start year 1900, two towns. Mods Deluxe Upgrade and Vehicles: No End Year.
- Made to test what a load changes: the seed in the header ([seed.md](seed.md)), settings changed on the Load Game screen and the difficulty presets ([settings.md](settings.md)), and a mod switched on and another off ([mods.md](mods.md#switching-mods-on-and-off-when-loading)). The second save switched the climate to temperate and the economy to dry on load, so later saves of this game hold those.
- Its tropical saves also serve [terrain.md](terrain.md#the-terrain-record) and [animals.md](animals.md).
- Saves are named `test-tiny-trop-20261010-<time>`, some with `-add-mod` or `-del-mod`.

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

## Catalog games we re-saved

Three catalog saves were loaded in the game and saved again, so they are tested as well as read. They are cited by mod id; only facts read from them are recorded.

| Catalog save | Map | Used for |
|---|---|---|
| [6417707](https://mod.io/g/transportfever3/m/333151) | Subarctic, 14336 x 14336 m, start 1900, no mods, re-saved from 17 April 2000 on | warehouses, stock lists, landmarks, subsidies, entity names, company rank |
| [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1) | Temperate, 11264 x 22528 m, start 1900, Easy preset, no mods, shown as 18 February 1937 | a second warehouse game, the Paused calendar setting, the Easy preset |
| [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) | Tropical, 8192 x 24576 m, start 1960, no mods, shown as 14 February 2191 | the Finances tab, company rank and loans, entity names, calendar speed |

Our editor maps and a few early saves, among them a giant temperate map, are cited in the notes by description only.
