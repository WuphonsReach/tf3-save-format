# Company rank and loans

The company's progression state: experience, the rank earned and claimed, how the game works out the rank thresholds, and the loan offers. The income cut that rises with rank is in [inflation.md](inflation.md). Script-state basics (finding a state, game-clock times) are in [script-states.md](script-states.md).

## Company and rank

Two states, both **Observed** on 585 and 604.

- `game_mechanics/company/company.gs`: `basePopulation`, `companyStates` and `companyEntity`.
- `game_mechanics/company/company_progression.gs`: `companyState` with `experience`, `level` and `potentialLevel`, plus loan tables (below).

What goes with what:

- The header's counter is a copy of the first `experience` after the progression path ([below](#the-header-counter)).
- `potentialLevel` is the rank **earned** and `level` the rank **claimed**. From the game's scripts (`game_mechanics/company/company_growth.script.tl` and `company.tl` in `base/content/game_mechanics.zip`, 604 build):
  - The game works out `potentialLevel` from `experience` and `basePopulation`, raises a rank-up notification for each rank gained, and sets `ticketPriceMultiplier` in the same `companyState` from it (see [the income multiplier](inflation.md#the-income-multiplier)).
  - `level` rises only when the player opens an earned but unclaimed rank in the company window, which sends an `applyLevel` event and plays the unlock animation. It is never set above `potentialLevel`. Rank rewards such as permits are counted from `level`.
  - The company window draws ranks up to `level` as unlocked, ranks above that up to `potentialLevel` as earned but not claimed, and the rest as locked. A new company starts with both at 1.
- **Observed** on 568 to 604: `potentialLevel` followed the rank shown in the game (rank 2 was shown as Mechanic). `level` was never above `potentialLevel`. It was equal in 117 and behind in 60 of the 177 catalog saves that hold the state, and 48 of those 60 were still at 1, 12 of them with Tycoon earned (for example [6387008](https://mod.io/g/transportfever3/m/my-1st-sandbox-with-mods-v7), 601). `level` was 1 in a 585 save and 2 after the same game was re-saved by a 604 game, which fits a rank claimed in between. Claiming a rank and comparing the saves before and after was not tested in the game (**Open**).
- `companyLevelUpCount` in the achievements state counts ranks earned, not claimed: it equalled `potentialLevel` minus 1 in 157 of those 177 saves, whatever `level` was. It was 0 in 19 saves from 568 to 601, and 1 at rank 1 in one 604 save (**Observed**).
- The game's company window lists 15 ranks in this order: Junior, Mechanic, Engineer, Coordinator, Expert, Team Leader, Supervisor, Manager, Director, Senior Director, CEO, Chairperson, Vice President, President, Tycoon. Rank 2 is Mechanic, as above, and the last is Tycoon, rank 15 (listed in a 604 game; names are the English UI).
- **Confirmed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, start year 1960, no mods): `level` 10, `potentialLevel` 13, `experience` 15,808 (equal to the header counter, [below](#the-header-counter)). The game showed Vice President, which is rank 13 in the list above, so `potentialLevel` is the rank shown and `level` is not: three earned ranks had not been claimed. `companyLevelUpCount` in the achievements state was 12, which is 13 minus the starting rank 1. A second save, 6429423, has the same split (7 and 8) and was not loaded in the game.
- In the same game the Vice President entry read "Reach a Population of 14,842" with the bar full, and `basePopulation` was 1,685. The formula below gives 14,842.
- `experience` did not change over two weeks of play in which `cargoDeliveredCount` rose by 9. It moved with population, not with deliveries or time.
- **Observed** on catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (604): `experience` 23,547 equalled the rank screen's progress figure ("23,547/24,037" toward President), `level` and `potentialLevel` were both 13 (Vice President, which the bottom bar showed), and `basePopulation` was 2,301. The header counter was 23,305, 242 behind `experience`. The bottom bar read 88%, not 23,547 / 24,037 (98%): it shows progress inside the current rank. The formula below puts Vice President at 19,949 and President at 24,037, and (23,547 − 19,949) / (24,037 − 19,949) is 0.88.

### The header counter

The counter in the header ([header.md](header.md)) is a copy of `experience` (**Observed** on 585 and 599 to 604). It is the first `experience` number in the progression state, the one next to `companyState`, `level` and `potentialLevel`.

- It matched the header in 16 of 19 saves and ran 1 to 4 points ahead in the other 3, so the header is probably written just before the state. In catalog save 6417707 it ran 242 ahead, so the gap is not always small.
- It grows with play: 8563 in the first save of a game started on 1 Jan 1900, rising to 16513 over later saves of that game, whose autosaves were all named `_1900-01-01`.
- It was 0 to 59,478 in the 120 catalog saves (568 to 604), and 0 in one.

### Rank thresholds

The thresholds the game shows ("Reach a Population of N") are not stored. The game computes them from `basePopulation` each time (`company_progression_util.tl` in `game_mechanics.zip`, growth factor in `scripts/util/town_growth_function.tl` in `scripts.zip`, 604 build). **Confirmed** on 604 against four figures read from company windows in different games:

- Rank 1 needs `basePopulation` itself.
- For rank r, the game takes a base that slides from a fixed 725 at rank 1 to `basePopulation` at rank 15, multiplies it by a growth factor, a cubic in r that is 1 at rank 1 and 12.5 at rank 15 (coefficients 0.001, 0.027398, 0.14221 and 0.829392 for r³, r², r and 1), and adds the difference between `basePopulation` and that base. The base and the product are rounded down.
- Checks: rank 1 at 1,355 with `basePopulation` 1,355; rank 2 at 1,622 with 1,443; Vice President (13) at 14,842 with 1,685 (6428935); President (14) at 24,037 with 2,301 (6417707), plus that save's 88% bar above. All four match exactly.
- The rank is the highest whose threshold `experience` has reached. That gives `potentialLevel`.

## Loans

In the progression state, under `availableLoans` and the table after it. Fields seen: `amount`, `birthDay`, `duration`, `percentage`, `type` (`Small`, `Medium`, `Large`, `ExtraLarge`), `freeId`, and on a taken loan `lastPayDay` and `timesPaid`. **Observed** on 585 and 604. Which table is which is **open**.

- **Observed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, calendar speed 0.50x, no loans taken), compared with the Loans tab. The four offers were stored as `Small` 12,000,000, `Medium` 59,000,000, `Large` 82,000,000 and `ExtraLarge` 124,000,000, in that order, with `percentage` 0.03, 0.05, 0.08 and 0.12 (a fraction, shown as 3%, 5%, 8%, 12%).
- `duration` is in the game clock ([calendar.md](calendar.md)): 1,461,000, 5,844,000, 17,532,000 and 20,454,000. That is 1, 4, 12 and 14 times 365.25 days. The tab showed 6, 24, 72 and 84 months, exactly half of that in years, which is the 0.50x calendar speed applied to the stored duration. That is the rule for durations in [calendar.md](calendar.md#the-game-clock), seen here at 0.50x only.
- `percentage` is a total, not a yearly rate: the "per Year" figure on each offer was `amount` times (1 + `percentage`) divided by the length in years shown, with one year as the least (12,360,000, 30,975,000, 14,760,000 and 19,840,000).
- `birthDay` is when the offer was made, as a clock value. The four were 383,174,000, 383,247,200, 383,259,800 and 382,834,400, against a newest timestamp of about 383,515,000 in the same save: 64 to 170 days of stored time before the save.
- **Offers renew every half year of clock time** (**Observed**, 604, one game: a temperate test game at 1.00x with nothing built and no loan taken, saves on 1 January, 11 May, 20 September 1900 and 2 January 1901). All four offers had the same `birthDay` in each save: 0, then 730,600 (2 July 1900), then 1,461,200 (1 January 1901). Each time all four were replaced with new amounts, rates and durations. Amounts were 6, 2, 12 and 4 million, then 4, 9, 16 and 20 million, then 3, 10, 12 and 22 million (`Small` to `ExtraLarge`), so `Small` is not always the smallest. A half year of clock is 730,500 (182.625 days at 4000), and each renewal came 100 or 200 ticks after the half-year mark. In catalog save 6428935 above, the four `birthDay` values differ by up to 106 days, so offers there were not renewed together. Why the two games differ (calendar speed, play history or something else) is **Open**.
