# Company rank and loans

The company's progression state: experience, the rank earned and claimed, how the game works out the rank thresholds, and the loan offers. The income cut that rises with rank is in [inflation.md](inflation.md). Script-state basics (finding a state, game-clock times) are in [script-states.md](script-states.md).

## In short

- **What drives the rank.** `experience` follows the towns' population, not deliveries or time (Observed, 604). The game turns it into a rank with thresholds it computes from `basePopulation` each time; they are not stored (Confirmed, 604, five figures from company windows). The rank earned is `potentialLevel`; `level` is the rank the player has claimed and can be lower (Confirmed, 604, one save; Observed on 177 catalog saves, 568 to 604).
- **Where it sits.** Two script states under `game_mechanics/company/` (Observed, 585 and 604). The header's experience counter is a copy of the first `experience` in the progression state (Observed, 585 and 599 to 604); it can run behind or ahead of it.
- **A new game.** `basePopulation` is the starting population, equal to the first `experience` (Observed, 604, eight new games).
- **Loans.** Four offers (`Small`, `Medium`, `Large`, `ExtraLarge`) with a rate that is a total over the term. Their durations are stored in the game clock and shown halved at 0.50x calendar speed (Observed, 604, one save). In one Tiny game all four were replaced every half year of clock time (Observed, 604, one game).
- **Not known.** What claiming a rank changes in the save (never compared before and after); which loan table is which; why offers renew together in one game and not in a catalog save. The list is in the [gaps](gaps/economy-and-events.md).

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
- `companyLevelUpCount` in the achievements state counts ranks earned, not claimed (**Observed**, [evidence](#evidence-and-tests)).
- `experience` moves with population, not with deliveries or time (**Observed**, 604, one game).
- The game's company window lists 15 ranks in this order: Junior, Mechanic, Engineer, Coordinator, Expert, Team Leader, Supervisor, Manager, Director, Senior Director, CEO, Chairperson, Vice President, President, Tycoon. Rank 2 is Mechanic and the last is Tycoon, rank 15 (listed in a 604 game; names are the English UI).
- The bottom bar shows progress inside the current rank, not toward the next threshold from zero (**Observed**, 604, one save).

### The header counter

The counter in the header ([header.md](header.md)) is a copy of `experience` (**Observed** on 585 and 599 to 604). It is the first `experience` number in the progression state, the one next to `companyState`, `level` and `potentialLevel`. The header is probably written just before the state, so the counter can run ahead; the gap is not always small.

### Rank thresholds

The thresholds the game shows ("Reach a Population of N") are not stored. The game computes them from `basePopulation` each time (`company_progression_util.tl` in `game_mechanics.zip`, growth factor in `scripts/util/town_growth_function.tl` in `scripts.zip`, 604 build). **Confirmed** on 604 against five figures read from company windows in different games:

- Rank 1 needs `basePopulation` itself.
- For rank r, the game takes a base that slides from a fixed 725 at rank 1 to `basePopulation` at rank 15, multiplies it by a growth factor, a cubic in r that is 1 at rank 1 and 12.5 at rank 15 (coefficients 0.001, 0.027398, 0.14221 and 0.829392 for r³, r², r and 1), and adds the difference between `basePopulation` and that base. The base and the product are rounded down.
- The rank is the highest whose threshold `experience` has reached. That gives `potentialLevel`.
- In a new game `basePopulation` is the starting population, and `experience` is the sum of the Towns tab's populations (**Observed**, 604).

## Loans

In the progression state, under `availableLoans` and the table after it. Fields seen: `amount`, `birthDay`, `duration`, `percentage`, `type` (`Small`, `Medium`, `Large`, `ExtraLarge`), `freeId`, and on a taken loan `lastPayDay` and `timesPaid`. **Observed** on 585 and 604. Which table is which is **open**.

- `duration` is in the game clock ([calendar.md](calendar.md)). The Loans tab shows it halved at 0.50x calendar speed, which is the rule for durations in [calendar.md](calendar.md#the-game-clock), seen here at 0.50x only.
- `percentage` is a fraction (0.03 shown as 3%) and a total, not a yearly rate: the "per Year" figure on an offer is `amount` times (1 + `percentage`) divided by the length in years shown, with one year as the least.
- `birthDay` is when the offer was made, as a clock value.
- **Offers renew every half year of clock time** (**Observed**, 604, one game). All four offers get new amounts, rates and durations together, and `Small` is not always the smallest. A half year of clock is 730,500 (182.625 days at 4000), and each renewal came 100 or 200 ticks after the half-year mark. Other games can differ (**Open**).

## Evidence and tests

### Rank: earned against claimed

- **Observed** on 568 to 604: `potentialLevel` followed the rank shown in the game (rank 2 was shown as Mechanic). `level` was never above `potentialLevel`. It was equal in 117 and behind in 60 of the 177 catalog saves that hold the state, and 48 of those 60 were still at 1, 12 of them with Tycoon earned (for example [6387008](https://mod.io/g/transportfever3/m/my-1st-sandbox-with-mods-v7), 601). `level` was 1 in a 585 save and 2 after the same game was re-saved by a 604 game, which fits a rank claimed in between. Claiming a rank and comparing the saves before and after was not tested in the game (**Open**).
- `companyLevelUpCount` in the achievements state equalled `potentialLevel` minus 1 in 157 of those 177 saves, whatever `level` was. It was 0 in 19 saves from 568 to 601, and 1 at rank 1 in one 604 save (**Observed**).
- **Confirmed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, start year 1960, no mods): `level` 10, `potentialLevel` 13, `experience` 15,808 (equal to the header counter). The game showed Vice President, which is rank 13 in the list above, so `potentialLevel` is the rank shown and `level` is not: three earned ranks had not been claimed. `companyLevelUpCount` was 12, which is 13 minus the starting rank 1. A second save, 6429423, has the same split (7 and 8) and was not loaded in the game.
- In the same game the Vice President entry read "Reach a Population of 14,842" with the bar full, and `basePopulation` was 1,685. The formula gives 14,842.
- `experience` did not change over two weeks of play in which `cargoDeliveredCount` rose by 9. It moved with population, not with deliveries or time.
- **Observed** on catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (604): `experience` 23,547 equalled the rank screen's progress figure ("23,547/24,037" toward President), `level` and `potentialLevel` were both 13 (Vice President, which the bottom bar showed), and `basePopulation` was 2,301. The header counter was 23,305, 242 behind `experience`. The bottom bar read 88%, not 23,547 / 24,037 (98%): it shows progress inside the current rank. The formula puts Vice President at 19,949 and President at 24,037, and (23,547 − 19,949) / (24,037 − 19,949) is 0.88.

### Header counter

- It matched the header in 16 of 19 saves and ran 1 to 4 points ahead in the other 3. In catalog save 6417707 it ran 242 ahead.
- It grows with play: 8563 in the first save of a game started on 1 Jan 1900, rising to 16513 over later saves of that game, whose autosaves were all named `_1900-01-01`.
- It was 0 to 59,478 in the 120 catalog saves (568 to 604), and 0 in one.

### Rank thresholds

- Checks against company windows: rank 1 at 1,355 with `basePopulation` 1,355; rank 2 at 1,622 with 1,443; Vice President (13) at 14,842 with 1,685 (6428935); President (14) at 24,037 with 2,301 (6417707), plus that save's 88% bar above. All four match exactly. A fifth, from our own new game (Small 1 : 3, five towns, 604): `basePopulation` 952 gives 1,123 for Mechanic (rank 2), the figure its company window showed, with a progress bar of 955 / 1,123.
- **New games (Observed, 604, eight new games of ours):** `basePopulation` equalled the first `experience` in each of them (109, 98, 952, 319, 224, 105, 86 and 134). In the Small game `experience` was 127 + 312 + 146 + 278 + 92 = 955 after a few seconds of play, where the first save had 952.

### Loans

- **Observed** on catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (604, calendar speed 0.50x, no loans taken), compared with the Loans tab. The four offers were stored as `Small` 12,000,000, `Medium` 59,000,000, `Large` 82,000,000 and `ExtraLarge` 124,000,000, in that order, with `percentage` 0.03, 0.05, 0.08 and 0.12 (shown as 3%, 5%, 8%, 12%).
- `duration` was 1,461,000, 5,844,000, 17,532,000 and 20,454,000, which is 1, 4, 12 and 14 times 365.25 days. The tab showed 6, 24, 72 and 84 months, exactly half of that in years, which is the 0.50x calendar speed applied to the stored duration.
- The "per Year" figures were 12,360,000, 30,975,000, 14,760,000 and 19,840,000.
- `birthDay` of the four was 383,174,000, 383,247,200, 383,259,800 and 382,834,400, against a newest timestamp of about 383,515,000 in the same save: 64 to 170 days of stored time before the save. The four differ by up to 106 days, so offers there were not renewed together.
- **Renewal in the [Tiny temperate game](test-games.md#tiny-temperate-games)** (**Observed**, 604, 1.00x, nothing built, no loan taken; saves on 1 January, 11 May, 20 September 1900 and 2 January 1901): all four offers had the same `birthDay` in each save, 0, then 730,600 (2 July 1900), then 1,461,200 (1 January 1901). Amounts were 6, 2, 12 and 4 million, then 4, 9, 16 and 20 million, then 3, 10, 12 and 22 million (`Small` to `ExtraLarge`). Why the two games differ (calendar speed, play history or something else) is **Open**.
