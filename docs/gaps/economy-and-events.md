# Gaps: economy and events

Format of an entry: see [README.md](README.md).

## Subsidies

- **What `usedUids` `true` means** (604) Two uids sat at `true` in none of the offer tables. Home: [subsidies.md](../subsidies.md). Needs: new save pair around an offer's lifetime.
- **Which `data` keys each subsidy kind uses, and what `failedSubventions` holds** (604) Home: [subsidies.md](../subsidies.md). Needs: existing saves.
- **What completes a Connect Towns subsidy** (604, one game) It completed on the first boarding with no delivery. Whether a line serving both towns is enough is untested. Home: [subsidies.md](../subsidies.md). Needs: new save.
- **Whether the "2x income" effect shows in the journal, and whether a failed subsidy books a charge** (604, one game) Income bookings after completion were the same size; a failure was not observed (the booking would be -2,610,000, wait past clock 2,678,150). Whether completion halves the offer interval is unknown. Home: [subsidies.md](../subsidies.md). Needs: new save.
- **Whether an advanced option level scales money amounts** (604) Home: [subsidies.md](../subsidies.md). Needs: new save on another level.
- **Whether a reward sets a town's growth rise** (604, one game) Home: [subsidies.md](../subsidies.md). Needs: new save.

## Industries

- **What decides an industry spawning at a half-year tick** (604, one game) Ten industries appeared in eight ticks; when the two secondaries (a food and a steel industry) were created cannot be read. Home: [industries.md](../industries.md), [notifications-in-play.md](../notifications-in-play.md). Needs: existing saves and new saves across several ticks.
- **The closing record's third value** (604) 1 for a processing industry and 5 for a primary one. Home: [industries.md](../industries.md). Needs: existing saves.
- **Whether a closed industry leaves its lists behind** (604) The game was not played through a closure. Home: [industries.md](../industries.md). Needs: new save after a closure.
- **The cement plant's list start** (604, one game) The list begins one tick before 1,948,000, not on a half-year boundary; it was probably created when stone first reached the plant. Home: [industries.md](../industries.md). Needs: existing saves.
- **Why a stock of 300 sits with 6 destroyed units at the start** (604) Home: [industries.md](../industries.md). Needs: new save at the very start of a game.
- **What the climate changes beyond the economy** (Observed) Terrain, vegetation, which industries spawn. Home: [climates-economies.md](../climates-economies.md#open). Needs: new save (same seed, another climate).

## Notifications

- **Issue types and numbering** (604, one game) `lineIssues` types other than 1 (type 0 is probably loaded-nowhere), the `lineProblem` numbering (4 matched), what the number in a `cargo_rtc_warning` mapping really is, and `vehicle2problem` against stuck vehicles. Home: [notifications.md](../notifications.md#params-by-type). Needs: game files (`line_warning.script.tl`, `cargo_rtc_warning.script.tl`) and game window.
- **A stamp older than its entry** (604, one game) One `line2problemTimestamp` key was 22 million units older than its entry; a returning problem may get a new entry and keep the first stamp. Home: [notifications.md](../notifications.md). Needs: existing saves.
- **The second and third numbers of `revision.num`** (604) Home: [notifications.md](../notifications.md). Needs: game files.
- **Repeat entries for one group, and expiry** (604) What makes the game open a second entry for a group, and why old ones expire. Home: [notifications.md](../notifications.md). Needs: existing saves and game files.
- **The balloon entry's layout** (604) It was read before the entry layout was known and not re-read. Home: [notifications.md](../notifications.md), [fun-elements.md](../fun-elements.md#the-notification). Needs: existing saves.
- **Whether `yearTo` ends anything in the "New Vehicles Available" entries** (604) And what a game that skips years does with the models of the years skipped, and whether mod vehicles get entries. Home: [notifications-in-play.md](../notifications-in-play.md). Needs: new save with the calendar set forward.

## Company and Finances

- **Claiming a rank** (604) Comparing the saves before and after a claim was not tested. Home: [company.md](../company.md). Needs: new save pair.
- **Why `level` stays behind `potentialLevel`** (568 to 604) In 60 of 177 catalog saves; 48 of those still at 1. Home: [company.md](../company.md). Needs: existing saves.
- **Why the offers do not renew together in every game** (604) In one Tiny game all four loan offers were replaced together every half year of clock time; in catalog save 6428935 the four `birthDay` values differ by up to 106 days. Calendar speed and play history are the candidates. Home: [company.md](../company.md). Needs: new save.
- **The Finances tab at another calendar speed** (604) Columns were read at 0.50x only; the infrastructure split into roads and buildings has no booking field of its own; the depot booking's category value was not read. Home: [finances.md](../finances.md). Needs: new save at another speed.
- **Where exactly the old bookings are merged** (Observed) The cutoff (a year before the clock or a fixed count). Home: [finances.md](../finances.md). Needs: existing saves.
- **Which setting gives a start with no capital** (604) Home: [header.md](../header.md). Needs: new save from a game started with each money option.
- **What the header's `stats` fields count** (604) The first and sixth of six leading `i64` moved by a vehicle swap's net spend; the last of the four small numbers (`stats3`) went from 11 to 12 in the same swap and its meaning is open. Home: [header.md](../header.md). Needs: existing saves, or a new save pair around one purchase.

- **How a delivery's pay is split between lines** (604, one delivery) The one measured split was 82% to the water line; whether it follows straight-line distance, path length or time per leg is untested. Home: [finances.md](../finances.md#leads-on-the-split-between-lines). Needs: new save with a two-line delivery and known leg lengths, and one with a backwards leg.

## Inflation

- **Whether the 568 and 585 saves lack the multiplier because the mechanism is newer or Inflation was None** Home: [inflation.md](../inflation.md). Needs: existing saves (read their header settings).
- **Whether the multiplier fits high ranks** (604) At Normal rank 13 it would be about 0.79, yet on three large Normal games the player's pay ran 1.33 to 1.69 times a prediction that used the rank-3 value (0.96426), and 1.11 to 1.16 on a small one. Those logs did not record the rank. Home: [inflation.md](../inflation.md#in-a-running-game). Needs: new run on a high-rank save with the company state logged.
- **Passenger income** (604) The scripts apply the multiplier to every ticket, but the logs held cargo arrivals only. Whether Passenger Income has its own factor or shares `difficultyFactor` is open. Home: [inflation.md](../inflation.md#in-a-running-game). Needs: new run with passengers.
- **Whether `difficultyFactor` follows the other Cargo Income steps** (604) Only 100% (1) and 50% (0.5) were seen, not 75%, 125% or 150%. Home: [settings.md](../settings.md#open). Needs: new save per step.
- **Whether the Inflation option adds to running costs** (604) The in-game comparison was confounded; a clean test needs per-vehicle running-cost bookings from the money journal, or a save with one setting changed. Home: [inflation.md](../inflation.md#in-a-running-game). Needs: new save pair.
- **Whether a mod sets a flag or the game applies the year multiplier to every construction's upkeep** (Observed, 604) And whether other buildings' and roads' prices step. Home: [inflation.md](../inflation.md). Needs: new save at a year step.

## Fun elements

- **How the balloon's spawn time and town are chosen, whether more than one can be up, whether `position` moves along `velocity`, how it leaves** (604) Home: [fun-elements.md](../fun-elements.md#open). Needs: new saves a few seconds apart, unpaused.
- **The UFO** (604) What it does and what the save holds while one is up. Home: [fun-elements.md](../fun-elements.md#open). Needs: new save while one is on the map.
