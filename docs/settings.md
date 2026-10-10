# Settings

The game settings of a save: the options of the New Game screen (and of the Settings tab on the Load Game screen), the difficulty presets, and what a load does to them. They sit in the header, in the params entry with the empty key (see [header.md](header.md#settings)), as a flat Lua table of numbers. Checked on format 604 unless a line says otherwise.

## How a setting is stored

**A setting is stored as its position in the option list plus 1** (**Confirmed** on 604, two catalog games and the test saves). The New Game screen is built from the game's `base/mod.json` in the install directory. Each option there has a `key` (the settings key below), a `values` list in screen order and a `defaultIndex` counted from 0. A stored 3 is the third entry.

- A game made on the Easy preset (catalog save [6425796](https://mod.io/g/transportfever3/m/mynewsavenotfinished1)): the screen showed industry productivity 150%, industry closing Never, vehicle maintenance effect Low, subsidies Often, subsidy risk None, landmark resources Low, inflation Low, every town sensitivity Low and vehicle costs 50%. The save held 4, 1, 2, 4, 1, 2, 2, 3 and 1 for those keys.
- A game left on the defaults (catalog save [6417707](https://mod.io/g/transportfever3/m/333151)) held 3 for the options whose default is the third entry, and 4 for the sensitivities, which default to Normal, the fourth of seven.
- The same options can have lists of different length, so a number alone does not say what it means. The percentage options list 50, 75, 100, 125 and 150%, so 1 is 50% and 3 is 100%. The game does not store which amount an entry stands for.
- Values are Lua numbers (f64) apart from the bool `isMapEditor`. Mod options in the same list are covered in [mods.md](mods.md#mod-options).
- `map.size` does not give one size. A value of 3 was 11264 x 11264, 6656 x 19968 and 8192 x 16384 in different saves. Use the header's width and height ([header.md](header.md)) for the real size.

## The options

Keys as stored: the settings table is flat and the dotted names are the keys (see [header.md](header.md#settings)). Screen names are English, read from the New Game and Load Game screens (604). The default is bold. The list is the 604 build's `base/mod.json`, desktop lists; where a key has a longer list for the experimental map features, the longer one is shown. `tools/tf3save.py` carries the same data as `SETTING_OPTIONS` and turns a stored number into a label with `setting_label`.

| Key | Screen name | List (default in bold) |
|---|---|---|
| `map.size` | Map Size | Tiny, Small, **Medium**, Large, Very Large, Huge, Megalomaniac, Gigantomaniac |
| `map.format` | Map Format | **1 : 1**, 1 : 2, 1 : 3, 1 : 4, 1 : 5 |
| `locations.towns.frequency` | Town Density | Sparse, Scattered, **Medium**, Dense, Packed |
| `locations.towns.populationDensity` | Population | 50%, 75%, **100%**, 150%, 200% |
| `locations.industry.initialIndustryDensity` | Industry Density | Sparse, Scattered, **Medium**, Dense, Packed |
| `locations.industry.targetIndustryDensity` | Industry Target Density | Sparse, Scattered, **Medium**, Dense, Packed |
| `locations.industry.industryProductivity` | Industry Productivity | 50%, 75%, **100%**, 150%, 200% |
| `economy.industryDevelopment.closureProbability` | Industry Closing Frequency | Never, **Rarely**, Sometimes, Often, Very Often |
| `advancedOptions.vehicleMaintenanceEffectScale` | Vehicle Maintenance Effect | None, Low, **Medium**, High, Very High |
| `advancedOptions.subventionMode` | Subsidies Availability | Never, Rarely, **Sometimes**, Often, Very Often |
| `advancedOptions.subventionRisk` | Subsidies Risk | None, **Fair**, Risky, Very Risky |
| `advancedOptions.landmarkResources` | Landmark Required Resources | None, Low, **Normal**, High, Very High |
| `advancedOptions.inflationFactor` | Inflation | None, Low, **Normal**, High, Very High |
| `townConfig.sensitivityUrbanCare` | Reputation (probably, not toggled) | Off, **On** |
| `townConfig.sensitivityTrafficCongestion` | Traffic Sensitivity | Off, Very Low, Low, **Normal**, High, Very High, Extreme |
| `townConfig.sensitivityPeopleHappiness` | Happiness Sensitivity | Off, Very Low, Low, **Normal**, High, Very High, Extreme |
| `townConfig.sensitivityCargoDelivery` | Delivery Sensitivity | Off, Very Low, Low, **Normal**, High, Very High, Extreme |
| `townConfig.sensitivityNoise` | Noise Sensitivity | Off, Very Low, Low, **Normal**, High, Very High, Extreme |
| `townConfig.sensitivityPollution` | Pollution Sensitivity | Off, Very Low, Low, **Normal**, High, Very High, Extreme |
| `advancedOptions.vehiclePurchaseCostScale` | Vehicle Costs | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.vehicleMaintenanceScale` | Vehicle Maintenance | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.infrastructurePurchaseCostScale` | Infrastructure Costs | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.infrastructureMaintenanceScale` | Infrastructure Upkeep | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.passengerIncome` | Passenger Income | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.cargoIncome` | Cargo Income | 50%, 75%, **100%**, 125%, 150% |
| `advancedOptions.reforestation` | Reforestation | Off, **On** |
| `weatherConfig.dynamicWeather` | Weather | **Dynamic**, Sunny, Cloudy, Rainy |
| `gameTimeConfig.timeOfDayMode` | Time of Day | **Dynamic**, Continuous, Local Time, Morning, Day, Evening, Night |
| `guideSystemConfig.tutorial` | Tutorial | Off, **On** |
| `economy.townDevelopment.cargoNeedsPerTown` | not seen on a screen | 2 Cargo Types, **Up to 4 Cargo Types**, Up to 6 Cargo Types |
| `advancedOptions.trafficSpeedSensitivityScale` | not seen on a screen | 0%, 25%, 50%, 75%, **100%**, 125%, 150%, 175%, 200% |
| `isMapEditor` | | bool; `true` in map editor saves ([editor-saves.md](editor-saves.md)) |

The key-to-screen-name pairs come from comparing screenshots with the saved numbers. For the options moved during the tests (the presets, the six hand-set options, population, passenger and cargo income) the screen value and the stored entry changed together (**Confirmed** on 604); Infrastructure Costs and Infrastructure Upkeep were told apart in a save where one read 50% and the other 100%. The rest (town density, initial industry density, weather, time of day, tutorial, reforestation, map size, map format) were matched on a single value each (**Observed**).

## Difficulty presets

The Difficulty row (Easy, Normal, Hard, Very Hard) on the New Game screen and on the Load Game settings tab writes a fixed group of options. **The preset itself is not stored**, only the values it wrote (**Confirmed** on 604): there is no preset key, and a save cannot tell you which button was pressed last. The New Game screen showed "Difficulty: Custom" once options had been set by hand.

Each preset was clicked in turn on one test game (Easy, Normal, Hard, Very Hard, each loaded and saved once) and the saved header was read. Stored entry and label:

| Key | Easy | Normal | Hard | Very Hard |
|---|---|---|---|---|
| `locations.industry.industryProductivity` | 4 (150%) | 3 (100%) | 2 (75%) | 1 (50%) |
| `economy.industryDevelopment.closureProbability` | 1 (Never) | 2 (Rarely) | 3 (Sometimes) | 5 (Very Often) |
| `advancedOptions.vehicleMaintenanceEffectScale` | 2 (Low) | 3 (Medium) | 4 (High) | 5 (Very High) |
| `advancedOptions.subventionMode` | 4 (Often) | 3 (Sometimes) | 2 (Rarely) | 1 (Never) |
| `advancedOptions.subventionRisk` | 1 (None) | 2 (Fair) | 3 (Risky) | 4 (Very Risky) |
| `advancedOptions.landmarkResources` | 2 (Low) | 3 (Normal) | 4 (High) | 5 (Very High) |
| `advancedOptions.inflationFactor` | 2 (Low) | 3 (Normal) | 4 (High) | 5 (Very High) |
| `townConfig.sensitivity*` (the five) | 3 (Low) | 4 (Normal) | 5 (High) | 6 (Very High) |
| `advancedOptions.vehiclePurchaseCostScale` | 1 (50%) | 3 (100%) | 4 (125%) | 5 (150%) |
| `advancedOptions.vehicleMaintenanceScale` | 1 (50%) | 3 (100%) | 4 (125%) | 5 (150%) |
| `advancedOptions.infrastructurePurchaseCostScale` | 1 (50%) | 3 (100%) | 4 (125%) | 5 (150%) |
| `advancedOptions.infrastructureMaintenanceScale` | 1 (50%) | 3 (100%) | 4 (125%) | 5 (150%) |

- Normal is the default entry of every row, so the Normal preset and "a game left on the defaults" are the same values.
- From Easy to Very Hard the values step one list entry at a time, except the four finance options (50%, 100%, 125%, 150%, so 75% is skipped) and industry closing (Never, Rarely, Sometimes, Very Often, so Often is skipped).
- The 16 options in the table are the ones a preset writes. Easy was the first click after the options had been changed by hand, and it changed 11 of them; the other 5 already held its values. Normal, Hard and Very Hard each changed all 16.
- **Not touched by any preset:** the target and initial industry density, town density, the tutorial and time-of-day options, the weather option, reforestation, the map size and format, the seed, and the Industries and Climate choices below. The target industry density stayed on a hand-set Dense through all four clicks.
- Population, passenger income and cargo income read 100% after all four clicks. Only the Easy click moved them (from 50%, 75% and 125% to 100%). Whether Normal, Hard and Very Hard would also reset them is **Open**: they already held 100% when those were clicked.

## Changing settings when loading

**The stored settings are those of the last load, not of the New Game screen** (**Confirmed** on 604, one game, one load per change). The Load Game screen has a Settings tab (headed "Save Settings") for the chosen save. A banner "Achievements cannot be earned" shows once something differs from the saved values.

- A new game was made (Tiny, 1 : 3, tropical, a typed seed), saved, loaded, six options were changed on that tab and the game was saved under a new name. The new header held the changed values and no others: of 32 settings values, 26 were equal. The changes were subsidy risk Risky to Fair, vehicle costs 75% to 100%, industry productivity 150% to 75%, industry target density Packed to Dense, population 150% to 50% and delivery sensitivity Low to High.
- Every value on the load screen matched the new header, and each settings key occurs once in the stream, in the header. There is no second copy.
- The tab's **Experimental** group has **Industries** and **Climate**. Setting them to Dry and Temperate changed the header's `economy` resource from `tropic.eco` to `dry.eco` and `climate` from `tropical.clima` to `temperate.clima` (see [header.md](header.md) for the resources and [cargo-ids.md](cargo-ids.md) for the pairs).
- Map size, map format and the seed are not on that screen and did not change.
- So the saves of one game can hold different settings, and what a save says is only known to be in force from its last load.

### The Mods tab

The Load Game screen also has a Mods tab. A mod switched on or off there is added to or dropped from the header's mod list, the config-mods list and the params list in the next save (**Confirmed** on 604, one load each). Details: [mods.md](mods.md#switching-mods-on-and-off-when-loading).

The Load Game list shows the loaded save's own values: its Difficulty row read "Very Hard" for a save written right after the Very Hard preset, so the label is derived from the stored values, not read from a stored preset name (**Observed**, one save). It also shows the saved climate, map size and format, date, population, rank and counts of stations, lines and vehicles.

## Open

- Whether the changes act in play: for example whether a higher infrastructure upkeep applies to buildings that already exist, or only to new ones. The in-play effect was not tested.
- What a mod adds to the script states once it has run in the game, and whether a deactivated mod with options is dropped with its options. Only mods with no options were switched on and off ([mods.md](mods.md#open)).
- Whether the saves a load starts from stay byte for byte as they were. The first test save was not hashed before the load.
- Whether the terrain and the existing industries change when the climate is switched on load. `tropical` occurred 13 times in the stream before the switch and 11 times after.
- Where the "Achievements cannot be earned" state is kept, if it is kept at all.
- Whether `townConfig.sensitivityUrbanCare` is the Reputation toggle, and what `cargoNeedsPerTown` and `trafficSpeedSensitivityScale` appear as on a screen.
- Whether mod options follow the position-plus-1 rule ([mods.md](mods.md#mod-options)).
