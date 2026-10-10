# Subsidies

The subsidy offers, active and finished subsidies, and what they pay. A subsidy shows up in two places: as a notification entry ([notifications.md](notifications.md)) and in the state of `game_mechanics/subventions/subventions.gs`, described here. The game's own word for them is "subventions".

## The notification entry

A subsidy is a notification entry of type `subvention_notification.script`. Its `params` hold a resource path under `::/game_mechanics/subventions/` (for example `deliver_cargo/deliver_cargo.res`), `stockListEntity`, and `simParams.mapping` with the name of the industry or town. The other fields are in [notifications.md](notifications.md#entry-fields). **Observed** on 585 and 604.

## Active and completed subsidies

State of `game_mechanics/subventions/subventions.gs`, read from catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (604, start year 1900, calendar speed 1.00x, loaded paused as 17 April 2000) and compared with the game's subsidy popups. **Observed**, one save. The pair count is 8 here ([script-states.md](script-states.md#finding-a-table) for the layout).

- Top-level keys: `activeSubventions`, `completedSubventions`, `failedSubventions` (16 entries), `proposedSubventions` (empty), `lastSpawnTime`, `spawnIntervalModifier`, `usedUids` and `version` (2).
- An entry has `id` (a resource path under `::/game_mechanics/subventions/`, for example `deliver_workers/deliver_workers.res`), `uid`, `spawnTime`, `acceptedTime`, on a completed one `completedTime`, and a `data` table. In `data`: `name`, `upfront`, `complete`, `failure`, `effectDuration`, `expireDuration`, `expireDurationProposed`, and the targets (`to`, `from`, `lineEntity`, `townEntity`, `cargoType`, `toDeliver`, `delivered`, depending on the kind).
- Targets are `{entity, revision.num}` with an entity id and three numbers. Entity ids here ran up to 135,964.
- Payments match the popup to the dollar. For an active worker-transport subsidy, `upfront` 16,950,000 was "On Acceptance", `complete` 27,980,000 was "On Fulfillment", and the two `failure` amounts (16,950,000 and 31,130,000) added up to the 48,080,000 fine. In every entry here the first `failure` amount equalled `upfront`. In the other `failure` slot the money fine and a `Reputation` entry with a `townEntity` (a fraction such as 0.7) both occurred.
- Reward types seen in `complete`: `Money`, and `TownExperience` with a fraction (0.55 and 0.8) and a `townEntity`. A completed "Connect Towns" entry held 0.55 and 0.8 for its two towns, and the popup showed "55% Level Progress" and "80% Level Progress" for them.
- Times use the game clock ([calendar.md](calendar.md)). At 1.00x, with the shown date taken as 17 April 2000 (146,524,000, which is 36,631 days from 1 January 1900), the numbers fit the screens: `expireDuration` 2,556,750 is 639 days and showed as "1 Year 9 Months"; `acceptedTime` + `expireDuration` fell 93 days after the save and the progress bar read "3 Months"; `effectDuration` 365,250 is a quarter of a year and showed as "3 Months"; a completed entry's `completedTime` + `effectDuration` (a 5-year effect, 7,305,000) fell 1,633.3 days after, and the popup showed "4 Years 5 Months 19 Days", which is 1,633 days. The date was taken from the screen, so this checks the unit and the 1.00x rule against one save, not the start of the count.
- Which `data` keys each kind uses, and what `failedSubventions` holds, were not worked out. **Open**.

### The offer itself

State of `game_mechanics/subventions/subventions.gs`. **Observed** on 604, one save with a proposed industry-supply offer checked against the game's offer window.

- A proposed entry has `id` (a resource path such as `::/game_mechanics/subventions/deliver_cargo/deliver_cargo.res`), `uid`, `spawnTime`, and a `data` table. In `data`: `name` (the offer's title, "Supply Industry"), `stockListEntity` (the industry's entity id), `toDeliver` (the amount of cargo, 80 in the offer checked), `cargosToDeliver`, `delivered`, `upfront`, `failure`, `effectDuration`, `expireDuration` and `expireDurationProposed`.
- `upfront` and `failure` hold `params` tables of `amount` and `type` (`Money` in the ones seen). In the offer checked, the payment on acceptance equalled `upfront`'s 6,300,000, and the fine shown (27,000,000) equalled the two `failure` amounts added, 6,300,000 and 20,700,000. In other saves the `failure` list also held small non-money amounts (under 1), which were not decoded.
- Durations shown in the offer window equalled the stored numbers divided by 4000 (days) and then multiplied by the calendar speed, 0.50x at the time: `expireDuration` 4,626,500 showed as "1 Year 7 Months" and `effectDuration` 7,305,000 as "2 Years 6 Months". That is the rule for durations in [calendar.md](calendar.md#the-game-clock).
- The `advancedOptions.*` settings are stored as small level numbers (1 to 5 seen in the catalog saves, not multipliers): the option's position in the list plus 1, see [settings.md](settings.md#how-a-setting-is-stored). Whether a level scales the stored money amounts was not shown: at the levels in the save checked (`subventionRisk` 2, `subventionMode` 3) the shown money equalled the stored money. Across a few other 604 saves with the default levels the fine against the payment varied from offer to offer, so the fine is not a fixed multiple of the payment. **Open**.
