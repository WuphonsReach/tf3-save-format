# The tutorial

What a game started with Tutorial On leaves in the save, and the open question of why its town and industry counts differ from the New Game screen. **Observed**, 604, one game of ours with Tutorial On ([the Small tropical game](test-games.md#map-format-tests), two saves) against our games started with it Off. Labels are defined in [README.md](README.md).

## What the save keeps

- **The option.** `guideSystemConfig.tutorial` is 2 for On and 1 for Off ([settings.md](settings.md#the-options)). The Start Game button is greyed on a map without enough water ([settings.md](settings.md#the-options)).
- **Two script states hold the tutorial's tasks:** `mission/mission.gs` and `mission/guide_system.gs` ([script-states.md](script-states.md)). Both have the same keys: `bootTypes`, `guiTimeSeconds`, `lastCompletedTime`, `nextUid`, `nonBulldozableEntities`, `notificationFilter`, `tasks` and `version` (5). `mission.gs` of the Tutorial On game also has `isTutorialActive`, true; no Tutorial Off save has that key.
- **Tasks.** With Tutorial Off both `tasks` tables are empty. In the Tutorial On game, saved at the start, `mission.gs` held 7 tasks and `guide_system.gs` 18; after about 1,400 clock units of play (a third of a day at the usual 4,000 a day) `mission.gs` held 9 and `guide_system.gs` still 18. What each task is was not read.
- **The welcome window** opened at the start and again when the save was loaded; loading it did not change the first save's file.

## Open: the town and industry counts

The New Game screen shows a Towns and an Industries figure for the map it will make ([industry-lifecycle.md](industry-lifecycle.md#the-industry-count-on-the-new-game-screen-and-in-the-save-604)). In eight games saved at once the Towns figure matched the save every time. The Industries figure matched in three games and was off by one in four, but in the Tutorial On game it read 8 and the save, and the loaded game's Industries tab, held 15.

- **A lead, not a finding.** The tutorial game is the only one with a large gap, and the only one with the tutorial states filled. But the Tutorial Off games differ by one too, so the tutorial cannot be the whole story: the preview may also be built before the game places and flattens the industries.
- **Not found in the install.** The mission scripts in `base/content/mission.zip` (`mission/tutorial/guide_system/`) were searched for calls that create industries, and none turned up. The search was by guessed name, so this does not rule it out.
- **The test.** Two New Games with the same seed, map size and sliders (a size with enough water, such as the Small 1 : 3 of that game), one with Tutorial On and one Off, each saved at once, with the New Game screens kept. Compare the Industries figure, the industries in each save and the two states above. If both saves hold 15, the gap is the preview and not the tutorial.
