# The map seed

The seed of a game is the last field of the header ([header.md](header.md)), called `id` there. It is the text of the Seed box on the New Game screen. This note covers what the field holds, which seeds the catalog saves carry, whether the seed alone rebuilds the map, and where else the game writes it.

## In short

- **The seed is the header's last field (Confirmed, 604).** It holds exactly the text typed in the New Game dialog's Seed box; 104 of 110 catalog saves hold the 10 random letters the game offers, and 94 values in 110 saves show a seed is not unique.
- **The seed alone does not rebuild the map as far as the save shows (Open).** The sliders that went with it are not stored.
- **The game's log carries it too (Observed, 604):** `Map seed text` on every new game and load, in `stdout.txt` of the `crash_dump` folder; the file is rewritten at each start.
- **Open.** What the editor calls the field, and whether default sliders give the New Game screen's map.

## The `id` field

A `str`, the last field of the header.

- **Confirmed** on 604: a game started with the typed seed `RaazVnK55w` and saved at once holds exactly that string.
- **Observed** on 599 to 604 in the 110 catalog saves whose header reads to the end: 104 hold 10 random letters and digits (the form the game offers), 6 hold typed text such as a town name or `0`. 94 distinct values in 110 saves, so a seed is not unique.
- It is unchanged across re-saves and autosaves of one game, and equal in two catalog saves and the re-saves made from them.
- 568 and 585 headers stop before it (see [versions.md](versions.md)).
- What the editor calls the field is **Open**. Every branch of `tf3-save-editor` read (upstream 0.4.0 and our forks) names it `id`, but the user has heard that an update renamed it, and no such change was found. Our tools call it `map_seed`. Recheck against the editor's newest `header.rs` and `docs/FORMAT.md` before relying on either name.

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
- The same log carries the export of the Transit Overlay mod when its button is pressed: [transit-overlay.md](transit-overlay.md).
- No terrain sliders appeared in the log either, so it does not settle whether the seed alone rebuilds the map.
