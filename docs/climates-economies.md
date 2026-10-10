# Climates and economies

The header names a climate and an economy in its config resources (`climate`, `economy` and `nameList`, each a path such as `::/economy/all.eco`, see [header.md](header.md)). They come in matched pairs, plus the all-industries economy. How many saves use each pair is counted in [versions.md](versions.md#climates-and-economies-in-the-catalog-2026-10-09). The climate files are `<name>.clima` and the economy files `<name>.eco`.

## The pairs

| Climate | Economy |
|---|---|
| `temperate.clima` | `temperate.eco` |
| `temperate.clima` | `all.eco` |
| `subarctic.clima` | `subarctic.eco` |
| `subarctic.clima` | `all.eco` |
| `tropical.clima` | `tropic.eco` (note `tropic`, not `tropical`) |
| `tropical.clima` | `all.eco` |
| `dry.clima` | `dry.eco` |
| `mission6_tropical.clima` | `tropic.eco` |

## What each economy leaves out of town cargo

**Observed**, 599 to 604 (568 and 585 headers stop before the economy). The ids of [cargo-ids.md](cargo-ids.md) line up with what each economy leaves out of its town cargo:

- `subarctic.eco` has no bricks and no vegetables: its town records use 6, 7 (commercial tier 0) and 13, 15, 20 (industrial tier 0), never 9 or 33.
- `tropic.eco` has no bricks, cement or beverages: commercial 6, 7, 9 and 27, 28 (tier 1), industrial 13, 20, never 15, 33 or 8.
- `dry.eco` has no fish: commercial 7, 9 only (never 6), industrial 13, 20, 33.
- `temperate.eco` has no cement: 15 never appeared in a temperate economy record, while 33 is common.
- `all.eco` has everything, and its records used 15 and 33 both.

Each of those economy files (`economy/<name>.eco.lua` in the install's `base/content/economy.zip`, 604 build) was read to see which cargo it removes. The ids themselves are not in those files and are not in the save: no cargo name string sits next to an id in any of the four climates' saves.

## Open

- What the climate changes in the save beyond this: terrain, vegetation, which industries spawn.
