# Pollution and noise

What gives off pollution and noise, how the map layer and the cursor number show it, the wind, and how a town turns them into its Pollution and Noise ratings. A save keeps the result in the town state's `cachedRatings` ([town-states.md](town-states.md#fields-per-town)) and the emissions script's own state (`emissions`, schema version 2, [lua-overview.md](lua-overview.md)). Checked on 605. The game files named below are in `base/content/game_mechanics.zip`, `gui.zip` and `depots/*.zip`, and in the install's `api/tealdef/`. Most of the reading, and every test, was done while the Depot Retrofits mod was built. Its written source is the mod's [findings.md](https://github.com/WuphonsReach/tf3-depot-retrofits/blob/4d35bf96b195c42aed55bc8fd15d0ade44139499/docs/design/findings.md) (tf3-depot-retrofits, at commit 4d35bf9).

## In short

- **Each building is an emitter with a pollution and a noise power (Confirmed in the files, 605).**
  - A construction declares two emission states, idle and full, in its subconstruction's `metadata.emissions`.
  - `game_mechanics/emission/emissions.script.tl` sets every emitter's power every few updates. A depot's power slides between its two states with the vehicles in maintenance against its pool. An industry's follows its production.
  - Passing vehicles are emitters of their own.
- **The map shows decibels, averaged over time (Confirmed in the files, Observed on one building, 605).**
  - Pollution has 12 steps from 57 to 80 dB, and noise 12 steps from 63 to 85 dB.
  - The averaged value follows the live one with a time constant of about 190,000 clock units ([calendar.md](calendar.md) has the clock).
  - At an isolated building, the live pollution is 10 log10(power) + 63.13 dB. So cutting a building's power by 45% is −2.6 dB, about 1.4 map steps.
- **Wind moves pollution, not noise (Confirmed in the files, Observed, 605).** One wind vector covers the whole map, and the pollution layer draws it as an arrow.
- **Town ratings (Confirmed in the files, 605).**
  - Pollution is summed over the town's area, averaged over at least 5 km² and at most 10 km², and mapped from 60 dB (best) to 74 dB (worst).
  - Noise is the engine's noise at the town's buildings, mapped from 65 dB (best) to 80 dB (worst), with no division by area.
  - The town's sensitivity setting shifts both before the mapping.
  - The town window's source rows are shares of the town's total.
- **Open.**
  - Whether and how the wind changes in play.
  - Whether the average follows game time or the calendar.
  - How much of the pollution beside a busy depot comes from its vehicles.
  - What each sensitivity step multiplies by.
  - Whether the embedded tables with `noise` and `pollution` keys in the stream ([lua-overview.md](lua-overview.md)) are the constructions' emission states.

## Emitters and their states

| Building | Pollution idle → full | Noise idle → full |
|---|---|---|
| Rail depot | 100 → 120 | 50 → 100 |
| Road, tram and water depot | 80 → 100 | 40 → 80 |
| Road maintenance building | 40 → 80 | 20 → 40 |
| Rail and water maintenance building | 50 → 100 | 20 → 40 |

- **Depots.** The values above are from each depot's update script, for example `rail/rail_depot.script.lua` and `road/road_maint_station.script.lua`. The state is placed between idle and full by the vehicles in maintenance against the pool, so a larger pool lowers the emissions by itself. For example, a building with 6 of 24 in maintenance sits a quarter of the way from idle to full. A depot's pool and upkeep are in [depots.md](depots.md#radius-pool-and-modes).
- **Industries.** An industry's emission level is 1 when idle and 2 when producing. Each of its two production boosts adds 1, and the level is halved while its output store is full. Processing industries reach 250 to 750 pollution, and mines 10 to 30.
- **The eco factor reaches industries only.** Depots, stations and warehouses always get factor 1.
- **Base tools against pollution.**
  - The Industry Greenification tool (`gui/construction/tools/industry_greenify_tool.script.tl`) cuts an industry's emissions by 80% per eco level (`emissionReductionPerEcoLevel` 0.8 in `emission/emission_config.tl`, about −7 dB). Its permits come at ranks 3, 6, 9, 12 and 15.
  - The Cleaning Plant (rank 10) removes up to 10,000 pollution at full output and uses machines.
  - Nothing in the base game lowers a depot's emissions.
- **A rebuilt building reads 0 for a moment.** After a construction is rebuilt ([construction-scripts.md](construction-scripts.md#rebuilds)), its emitter is empty until the emissions script next sets it, a few updates later. Those updates do not run while the game is paused, so the town window's Depots and Maintenance Buildings rows vanished in a paused game and came back about 6 s after unpausing (Observed, 605).

## The grid and the map layer

- **One emission grid holds the field.** `api.engine.system.emissionGridSystem.getInterpolatedEmission(position, useAverage, type)` reads it at a point, and `api.util.powerToDecibel` turns power into dB. The grid has 16 m cells: the town rating counts cells of 16 by 16 m (`game_mechanics/towns/town_util.tl`).
- **The layer and the cursor number show the average.** `gui/layers/layer_pollution.tl` colours the ground from the averaged value, and the cursor number (`gui/main/game_tooltips.tl`) reads it with `useAverage` true.
- **The scale.** `emission/emission_config.tl` sets 12 steps from `pollutionLowerBoundDB` 57 to `pollutionUpperBoundDB` 80 for pollution, about 1.9 dB a step, and 12 steps from 63 to 85 dB for noise, about 1.8 dB a step.
- **What the cursor number means.** For pollution, n from 1 to 11 means 57 + 1.92n to 57 + 1.92(n + 1) dB. 12 means 80 dB or more, so it is only a bound, and 0 means below about 59 dB.
- **A change in power moves the map by 10 log10 of its factor.** ×0.95 is −0.2 dB, ×0.75 is −1.2 dB, ×0.55 is −2.6 dB and ×0.25 is −6.0 dB.

## Wind

- **One wind vector for the whole map.** The emission grid component (`EMISSION_GRID`, record `EmissionGrid` in `api/tealdef/api/engine.d.tl`) has `wind : Vec2f`, described there as the global wind direction. A crash log once showed entity 0 carrying only this component ([entity-model.md](entity-model.md)), so the grid is probably entity 0.
- **Only pollution drifts with it.** The pollution layer draws the wind as an arrow with a figure in m/s in its lower right corner (`windRenderableConfig` in `layer_pollution.tl`). A building's pollution field is an oval blown downwind, so a cursor reading beside it depends on the side. The noise layer draws no arrow, and a building's noise field is a circle.
- **A command can set it.** `api.cmd.makeWorldChangeWindCmd(emissionGridEntity, wind)` exists in `api/tealdef/api/cmd.d.tl`, but no base script calls it. The wind read 2.27 m/s in every shot of one session (Observed, 605). Whether it ever changes is Open.

## Town ratings

- **Pollution is town-wide.**
  - `town_util.getRatingPollution` (`game_mechanics/towns/town_util.tl`) takes the pollution summed over the town's area and divides it by the area's cell count. The area is clamped to between 5 and 10 km² (`pollutionRatingAreaMinSquareKm`, `pollutionRatingAreaMaxSquareKm`).
  - It turns the result into dB and maps 60 dB to a rating of 1 and 74 dB to 0 (`pollutionRatingLowerBoundDB`, `pollutionRatingUpperBoundDB`), clamped. On the 0 to 1000 scale of the graph, one point is 0.014 dB, so 1% is 0.14 dB.
  - Every depot inside the town's border counts. The config's comment says the cells sampled are those of the town's Voronoi polygon.
- **Noise is local.** `town_util.getRatingNoise` takes the engine's noise for the town (`api.engine.util.town.getTownEmissionDB`) and maps 65 dB to 1 and 80 dB to 0, with no division by area. The config's comment says the dB is sampled at the buildings' positions and averaged. The town window splits noise by district, residential and commercial, each with its capacity (`getTownNoisePerDistrict` in `town_react_util.tl`).
- **Sensitivity shifts the dB.**
  - The town's sensitivity for each rating comes from the Pollution and Noise Sensitivity settings ([settings.md](settings.md)), or from a per-town `ratingSensitivity` in the town state.
  - It adds 10 log10(sensitivity) dB before the mapping, and a sensitivity of 0 (Off) gives a rating of 1.
  - A random offset per town is in the code, but its range is set to {0, 0} in `emission_config.tl`.
- **The window's source rows are shares.** `town_util.getTownEmissionEmitters` sums the pollution of each category of source inside the area and divides each by the total. "Depots" are `VEHICLE_DEPOT`s with in and out nodes, and "Maintenance Buildings" those without. So every row jumps when an industry starts or stops producing, even when its own sources have not changed.
- **The graph is the rating.** The Pollution Rating graph on the town window's pollution card plots the town's `pollution` log, 0 to 1000 (`gui/entity_window/town/town_eow.script.tl`), with no live value added. New points came about every 30 s at 4x and kept coming while the calendar was paused, all labelled with the paused year (Observed, 605). Hovering a point shows its value. For one town it is the best gauge of a change.

## Evidence and tests

All on 605, in the Giga temperate game ([test-games.md](test-games.md#giga-temperate-game-wr26a)) with the Depot Retrofits mod scaling the emission states of chosen buildings. The tests are in the mod's findings.md under "Test results" (tf3-depot-retrofits, at commit 4d35bf9).

### One building in an open field (605)

- **The setup.** A rail maintenance building with no other source nearby, in save `WR26A Giga-Tv3 1912`, with the calendar slowed so the date stayed 12 January 1915. Its pollution power was cut from 50 to 40 and then to 27.5.
- **The live value.** The live value at the building fell by exactly 10 log10 of the power: −0.97 dB for 50 to 40, −1.63 dB for 40 to 27.5, −2.60 dB in all. It read 80.12, 79.15 and 77.52 dB for 50, 40 and 27.5, so the live dB is 10 log10(power) + 63.13 to within 0.01 dB, at a wind of 2.27 m/s.
- **The average.** The average lagged like an exponential with a time constant of about 190,000 clock units (fits from 172,000 to 195,000). At 1x that is about 3 minutes of play, or 48 game days at calendar speed 1x. It got two thirds of the way in about 3 minutes and settled in about 10 (77.52 live and averaged).
- **The map.** The cursor number went from 11 to 10.
- **Three more buildings.** Three rail maintenance buildings in another part of the map went from 50 to 27.5 power. Their cursor number dropped from 12, which is only a bound, to 11 in about 30 s, and to 10 after about a minute, with a train passing.
- **Whether the clock or the calendar drives it.** This was not separated: the fit is in clock units on a save whose calendar barely moved.

### Two towns (605)

- **A town of 302 residents.** Its three buildings (a ship depot, a road depot and a road maintenance building) were cut by 45%. The graph rose from about 80% to 87–89% within about 3 minutes at 4x, against a wobble of about ±2 points. That is −1.0 to −1.3 dB; the shares had predicted about +7 points.
  - With the calendar paused, the Industries row read 20%, 44–45% and 62–66% in three moments as industries started and stopped.
  - The depots stayed about 41% of the rest throughout, so the depots' own pollution had not changed.
- **A town of about 1,150 residents (save `WR26A Giga-Tv3 1974-test`, rank 11).** All 12 depots and maintenance buildings were cut by 55%; they gave off a third of the town's pollution.
  - The graph was flat at about 41% (40 to 42% from 1954 to 1973). It then read 45% for 1974, the year of the change, 49% for 1975, 50% for 1976, 49% for 1977 and 47% for 1978. Over those years the town's industries grew from 6% to 14% of its total, and company vehicles from 4% to 8%.
  - The shares predicted +6 points (−0.87 dB).
  - Each building's live value fell by 2 to 4.5 dB; two empty rail depots fell by −3.46 and −3.48 dB against the −3.47 expected for 55%.
  - Stations (29 to 38%) and tracks (24 to 31%) were about half of the town's pollution.
  - The rating label stayed "Mediocre", and the town's "pollution is decreasing" notice stayed on throughout.
