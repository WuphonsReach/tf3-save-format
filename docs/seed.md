# The map seed

The seed of a game is the last field of the header ([header.md](header.md)), called `id` there. It is the text of the Seed box on the New Game screen. This note covers what the field holds, which seeds the catalog saves carry, whether the seed alone rebuilds the map, and where else the game writes it.

## The `id` field

A `str`, the last field of the header.

- **Confirmed** on 604: a game started with the typed seed `RaazVnK55w` and saved at once holds exactly that string.
- **Observed** on 599 to 604 in the 110 catalog saves whose header reads to the end: 104 hold 10 random letters and digits (the form the game offers), 6 hold typed text such as a town name or `0`. 94 distinct values in 110 saves, so a seed is not unique.
- It is unchanged across re-saves and autosaves of one game, and equal in two catalog saves and the re-saves made from them.
- 568 and 585 headers stop before it (see [versions.md](versions.md)).

## Does the seed rebuild the map?

Not on its own, as far as the save shows (**Open**).

- The sliders (ocean, islands, mountains) that went with the seed are not in the stream. In a 604 save there is no `mz_layout`, `oceans` or generator path (**Observed**).
- The terrain tests are in [terrain.md](terrain.md): the same seed and sliders give the same bulk of the data, and a changed slider changes nearly all of it (**Observed**, 604).
- Whether the seed with sliders at their defaults gives the same map as the New Game screen is **Open**.

## The seed in the game's log

The seed can also be read without a tool, from the game's log (a tip from the game's subreddit, checked by us). The log is `stdout.txt` in the `crash_dump` folder of the game's user data folder, next to `save/`. **Observed** on 604, in one session of 10 new games and 7 loads of saved games:

- Starting a new game writes a line ending `Seed text: <seed>`, then one ending `Map seed text: <seed>`.
- Loading a save writes only the `Map seed text` line. The log does not name the save, but all 7 loads were of one test series and printed its seed, the value every save of that series holds in `id`. Just before the line the log prints the active mods, the `climate`, `economy` and `nameList` paths and the game settings table, the same values as the header's config fields.
- The file began with that session's startup line and held nothing from earlier sessions, so it seems to be rewritten each time the game starts. To find the seed of an older game, load its save and then search the log for `seed`; the last match is that save's.
- No terrain sliders appeared in the log either, so it does not settle whether the seed alone rebuilds the map.
