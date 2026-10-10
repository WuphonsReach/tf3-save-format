# Entity names

One table in the entity data holds a name for every entity: company, people, towns, industries, stations, stops, signals, lines and vehicles. Checked on 604, two played saves, compared with screenshots of the game:

- Catalog save [6428935](https://mod.io/g/transportfever3/m/emerald-shores3) (tropical, start year 1960, Asian name list). Read from a re-save with the same header counter. 25,524 names in a 751 MB stream.
- Catalog save [6417707](https://mod.io/g/transportfever3/m/333151) (subarctic, start year 1900, European name list). 38,653 names in a 928 MB stream. Its header money matched the Account figure on the game's bottom bar.

Labels are **Observed** (both saves) unless marked.

## Layout

```
u32  n
str  x n
```

- The table sat 44% and 46% of the way into the stream. About 8 zero bytes and a u32 near 171,000 follow it in both saves, then more data. What they are is **Open**.
- `n` is directly before the first string. Parsing exactly `n` strings from there ended where the zero bytes begin in both saves.
- The u32 before `n` is not fixed. It was `n - 1` in the first save and 4,111 (with `n` 38,653) in the second, so ignore it. An earlier version of this note called it `n - 1`; that was a coincidence.
- An entity with no name holds the string `no name` (32% of entries in the first save, 28% in the second). Empty strings are rare: none in the first save, two in the second.
- The first entry is the player company's name. In both saves it was the account's display name followed by ` Transport` (or `user` and digits where there was no display name). It is account-derived, so don't publish dumps of the table.
- The default comes from the platform account on consoles too. In 54 of the 244 catalog saves and maps of [versions.md](versions.md), the uploader's mod.io name followed by ` Transport` was one string: Windows 23, PS5 18, Xbox 7, Linux 5, Mac 1 (**Observed**, 568 to 604, 2026-10-10). The count says nothing about how often the default is kept: a mod.io name that differs from the platform name and a company the player renamed look the same here. In our own saves (604), 32 of the 37 games first written under 604 held the Steam profile name followed by ` Transport`. None of 33 re-saves of catalog games first written under 555 to 596 held it, so loading another player's game keeps their company name (**Observed**). One re-save of a 599 game did hold it (**Open**).
- Position is not the entity id, but it is tied to it for the first entries. In the second save the company entity was id 58,492 and took slot 0, and two towns took slots 2 and 13 while the subsidy state gave them ids 58,494 and 58,505, so id = 58,492 + slot for those three. The table starts with the company followed by the towns. It stops fitting for later entities: an industry had id 38,333 (below the company's) and a line 135,964 (slot 77,472, past the end of a 38,653-entry table). So the table does not index every entity id. The rule for later entities is **Open**. In the same save one line and its two trains sat in consecutive slots, the line first.

## Finding it

There is no marker for the table. A way that worked on both saves:

1. Search the stream for a name you can see in the game, as a `str` (u32 length, then UTF-8 bytes). A town name works.
2. Parse `str` after `str` forwards until a length is not plausible (over a few hundred, or not valid UTF-8). The run was tens of thousands of strings long.
3. Walk backwards the same way: the earlier position whose length field ends exactly where you stand. The step was unambiguous in both saves (one candidate each time). It stops at the table's first string, because nothing before `n` parses as a string ending there.
4. Check that the u32 just before the run equals the number of strings from there to where the forward parse stopped, apart from the two zero words at the end that also parse as empty strings.

## What the names look like

| Entity | Name |
|---|---|
| Vehicle | The vehicle type word and a number: `Road Vehicle 959`, `Train 123`, `Ship 92` in the European save, the Chinese words for tram and road vehicle followed directly by the number in the Asian one (a space in one, none in the other). Numbers are per type and not reused: the first save's 31 trams were 1 to 31 with no gaps, its 257 road vehicles ran up to 265 with gaps (sold vehicles), and the second save's 952 road vehicles ran up to 959. Slot order does not follow the numbers early in the table |
| Signal | `<town> Signal <n>`, with a counter per town (one town reached 162) |
| Stop | In the Asian save, a word for "stop", `#` and a number |
| Station | `<town> <word for station>` in the Asian save, and names like `Bewdley Station Central` in the European one |
| Line | Stop or station names joined by ` - `. A line's name can end in a stray space (the Asian save) or in ` - ` (one line of 329 in the European save). A name of the shape `<place> - <cargo list>` also occurs, for example a town with two cargo names. The entity type was not checked |
| Person | A personal name in the style of the name list |

- Names need not be unique. In the European save 135 entries were one airport's name followed by `1`.
- The default vehicle words are stored as text at creation: the game's UI was English for both screenshots, and the Asian save's Chinese names showed unchanged (as boxes, see below). Whether the words come from the name list or from the language the author's game ran in is **Open**, since the catalog authors' languages are unknown.
- The UI font showed boxes for Chinese characters. Each box is one character, so a screenshot is enough to tell a name's length and shape. A six-stop line shown as six two-box groups joined by dashes matched the one name of that shape in the save.

## Not found

- How a line refers to its vehicles. The tram's id appeared 34 times in the first save, mostly in sorted lists of u64 entity ids (an id then four zero bytes), none close to a candidate line id.
- Where a vehicle keeps its model. The model table near the start of the stream was first read as `u64 id, str path` entries; it is `str` source mod, `str` path, `u32` id, which reads the same way while the mod string is empty (see [terrain.md](terrain.md#which-animals-they-are), 604). The tram model's id from it was not within 400 bytes of the tram's own id. Animals keep their model id in a model instance record with their transform, not next to their own entity id, so a vehicle may do the same (**Open**).
- A table of resource paths mapped to numbers (cargos first, then vehicle models) sits late in the stream as a Lua table. The number for each model is not the model id. **Open**.
