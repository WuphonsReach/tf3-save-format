# Map sizes

How the Map Size and Map Format options set the map's width and height in a save. Read from the header's width and height and the stored `map.size` and `map.format` of the mod.io catalog saves and our own. **Observed**, 599 to 604 for the settings; the sizes alone also fit on 568 and 585 (no settings stored there). Labels are defined in [README.md](README.md).

## The rule

**Observed (599 to 604):** each Map Size is a set area in km², and Map Format only changes the shape of that area. Take the 1:1 map of a size: its 1:2 and 1:3 maps hold about the same area, as a longer, narrower rectangle. The two are not exactly equal, because every side is a whole number of 256 m tiles (every size seen is a multiple of 256), so the area of one size differs by up to a few percent between formats.

The settings are stored as 1-based positions in the lists of [settings.md](settings.md#the-options): `map.size` 1 is Tiny and 8 is Gigantomaniac, `map.format` 1 is 1 : 1 and 5 is 1 : 5. The header's width and height ([header.md](header.md)) are in metres.

All 40 combinations, in the order of the stored settings. [tools/map_size_tables.py](../tools/map_size_tables.py) prints both tables of this note from the mined summaries. A row with no size is a combination no save or New Game screen has shown yet.

| `map.size` | `map.format` | Size | Format | Width x height, m | Area, km² |
|---|---|---|---|---|---|
| 1 | 1 | Tiny | 1 : 1 |  |  |
| 1 | 2 | Tiny | 1 : 2 | 2560 x 5120 | 13.1 |
| 1 | 3 | Tiny | 1 : 3 | 2048 x 6144 | 12.6 |
| 1 | 4 | Tiny | 1 : 4 | 2048 x 6144 | 12.6 |
| 1 | 5 | Tiny | 1 : 5 | 1536 x 7680 | 11.8 |
| 2 | 1 | Small | 1 : 1 | 8192 x 8192 | 67.1 |
| 2 | 2 | Small | 1 : 2 | 5632 x 11264 | 63.4 |
| 2 | 3 | Small | 1 : 3 | 4608 x 13824 | 63.7 |
| 2 | 4 | Small | 1 : 4 |  |  |
| 2 | 5 | Small | 1 : 5 |  |  |
| 3 | 1 | Medium | 1 : 1 | 11264 x 11264 | 126.9 |
| 3 | 2 | Medium | 1 : 2 | 8192 x 16384 | 134.2 |
| 3 | 3 | Medium | 1 : 3 | 6656 x 19968 | 132.9 |
| 3 | 4 | Medium | 1 : 4 |  |  |
| 3 | 5 | Medium | 1 : 5 |  |  |
| 4 | 1 | Large | 1 : 1 | 14336 x 14336 | 205.5 |
| 4 | 2 | Large | 1 : 2 | 10240 x 20480 | 209.7 |
| 4 | 3 | Large | 1 : 3 | 8192 x 24576 | 201.3 |
| 4 | 4 | Large | 1 : 4 |  |  |
| 4 | 5 | Large | 1 : 5 |  |  |
| 5 | 1 | Very Large | 1 : 1 | 16384 x 16384 | 268.4 |
| 5 | 2 | Very Large | 1 : 2 | 11264 x 22528 | 253.8 |
| 5 | 3 | Very Large | 1 : 3 | 9216 x 27648 | 254.8 |
| 5 | 4 | Very Large | 1 : 4 |  |  |
| 5 | 5 | Very Large | 1 : 5 |  |  |
| 6 | 1 | Huge | 1 : 1 | 20480 x 20480 | 419.4 |
| 6 | 2 | Huge | 1 : 2 | 14336 x 28672 | 411.0 |
| 6 | 3 | Huge | 1 : 3 |  |  |
| 6 | 4 | Huge | 1 : 4 |  |  |
| 6 | 5 | Huge | 1 : 5 |  |  |
| 7 | 1 | Megalomaniac | 1 : 1 | 24576 x 24576 | 604.0 |
| 7 | 2 | Megalomaniac | 1 : 2 | 16896 x 33792 | 570.9 |
| 7 | 3 | Megalomaniac | 1 : 3 |  |  |
| 7 | 4 | Megalomaniac | 1 : 4 |  |  |
| 7 | 5 | Megalomaniac | 1 : 5 | 10752 x 53760 | 578.0 |
| 8 | 1 | Gigantomaniac | 1 : 1 | 28672 x 28672 | 822.1 |
| 8 | 2 | Gigantomaniac | 1 : 2 | 20480 x 40960 | 838.9 |
| 8 | 3 | Gigantomaniac | 1 : 3 | 16384 x 49152 | 805.3 |
| 8 | 4 | Gigantomaniac | 1 : 4 |  |  |
| 8 | 5 | Gigantomaniac | 1 : 5 | 12800 x 64000 | 819.2 |

Three 1 : 5 maps were seen apart from Tiny's: Megalomaniac, 10752 x 53760 m (578 km², 601, mod.io [6386596](https://mod.io/g/transportfever3/m/cargo-transfer)), Gigantomaniac, 12800 x 64000 m (819 km², 604, mod.io [6436516](https://mod.io/g/transportfever3/m/funnntimes)), and the Tiny one, 1536 x 7680 m ([below](#tiny)). The Tiny 1 : 4 row repeats the 1 : 3 shape. The default Map Size is Medium and the default format 1 : 1 ([settings.md](settings.md#the-options)), which is 11264 x 11264 m.

## Tiny

**Observed (604):** Tiny 1 : 3 and Tiny 1 : 4 both give 2048 x 6144 m (8 x 24 tiles), see [the terrain note](terrain.md#the-terrain-record). Tiny 1 : 2 gives 2560 x 5120 m (10 x 20 tiles, 13.1 km²) and Tiny 1 : 5 gives 1536 x 7680 m (6 x 30 tiles, 11.8 km²), one save each. The New Game screen's own size readout agreed with each save: 2.5 x 5.0 km with 1 : 2 selected, 2.0 x 6.0 km with 1 : 3 and 1 : 4, and 1.5 x 7.5 km with 1 : 5, so the shape comes from the game's setup and not from anything a save changes.

- A 1 : 4 map of the 12.6 km² would be about 1792 x 7168 m (7 x 28 tiles), which no save has. Tiny 1 : 4 comes out as the 1 : 3 shape. Why is **Open**.
- 2048 m is not a minimum width: the 1 : 5 map is 1536 m wide. The 1 : 5 area is 6% under the 1 : 3 one, within the tile rounding of the rule above.

## Saves that disagree with their settings

**Observed (604, 601):** Some catalog saves store a size or format that does not match their real dimensions. Every one so far is a played save: no catalog editor map disagrees with its settings. Each row below has the same columns as the table above up to the area, with the settings as stored and the dimensions as in the header. The next column names the table row that has those dimensions. In every case that row exists in the table above, so the dimensions are a normal size and the stored settings are the odd part. Mostly the stored size is smaller than the real one; in a few only the format differs. Whether these were made in the map editor, edited by hand, or had their settings rewritten on a load is **Open**. For a map's size, trust the header and the terrain record, not the stored settings.

| `map.size` | `map.format` | Size | Format | Width x height, m | Area, km² | The dimensions are those of | Map |
|---|---|---|---|---|---|---|---|
| 2 | 1 | Small | 1 : 1 | 11264 x 11264 | 126.9 | Medium 1 : 1 | [kaspars](https://mod.io/g/transportfever3/m/kaspars) (6432023) |
| 3 | 1 | Medium | 1 : 1 | 10240 x 20480 | 209.7 | Large 1 : 2 | [Brasil](https://mod.io/g/transportfever3/m/brasil1) (6423816) |
| 3 | 1 | Medium | 1 : 1 | 8192 x 24576 | 201.3 | Large 1 : 3 | [autosave_Emerald Shores_1965-07-29](https://mod.io/g/transportfever3/m/autosave-emerald-shores-1965-07-29) (6419141) |
| 3 | 1 | Medium | 1 : 1 | 8192 x 24576 | 201.3 | Large 1 : 3 | [LXYY](https://mod.io/g/transportfever3/m/na263651) (6422633) |
| 3 | 1 | Medium | 1 : 1 | 14336 x 14336 | 205.5 | Large 1 : 1 | [Redrock Bends](https://mod.io/g/transportfever3/m/redrock-bends2) (6425276) |
| 3 | 1 | Medium | 1 : 1 | 16384 x 16384 | 268.4 | Very Large 1 : 1 | [YF-EL](https://mod.io/g/transportfever3/m/oresund-strait-eng1) (6435288) |
| 3 | 1 | Medium | 1 : 1 | 16384 x 16384 | 268.4 | Very Large 1 : 1 | [xyfel](https://mod.io/g/transportfever3/m/xyfel) (6440248) |
| 3 | 3 | Medium | 1 : 3 | 11264 x 11264 | 126.9 | Medium 1 : 1 | [20260929](https://mod.io/g/transportfever3/m/20260929) (6414660) |
| 4 | 2 | Large | 1 : 2 | 20480 x 20480 | 419.4 | Huge 1 : 1 | [汉化 Mt Fuji & Hakone chinese 汉化工业补充版](https://mod.io/g/transportfever3/m/mt-fuji-hakone-chinese1) (6418114) |
| 5 | 1 | Very Large | 1 : 1 | 28672 x 28672 | 822.1 | Gigantomaniac 1 : 1 | [Niqqow Aussie Aussie Aussie](https://mod.io/g/transportfever3/m/niqqow-aussie-aussie-aussie) (6437320) |
| 5 | 2 | Very Large | 1 : 2 | 16384 x 16384 | 268.4 | Very Large 1 : 1 | [Deutschland Map](https://mod.io/g/transportfever3/m/deutschland-map) (6440867) |
| 8 | 2 | Gigantomaniac | 1 : 2 | 28672 x 28672 | 822.1 | Gigantomaniac 1 : 1 | [MAPA BRASIL](https://mod.io/g/transportfever3/m/mapa-brasil) (6433003) |

## The experimental notice in the load dialog

**Confirmed (604):** the Load Game dialog shows a yellow line, "The map size is experimental.", for a save whose stored `map.size` is 1 (Tiny) or 6 to 8 (Huge, Megalomaniac, Gigantomaniac). It shows "The map format is experimental." for `map.format` 4 or 5, and one line naming both when both are out of range. It is not a separate flag in the header and not tied to the map editor: the game script that draws it (`gui/menu/savegame_react_util.tl` in `base/content/gui.zip`) compares the two stored settings with the range the desktop New Game options allow without the experimental map features: `map.size` 2 to 5 (Small to Very Large) and `map.format` 1 to 3. `base/mod.json` lists those two parameter sets, one without the tag `experimentalMapFeatures` and one with it. The header's width and height are not read.

Eleven saves seen in the dialog agree with that rule: notice on Tiny 1 : 3 (a converted editor map, see [editor-saves.md](editor-play.md#a-converted-editor-map-loaded-as-a-played-game)) and Gigantomaniac 1 : 2; none on Small 1 : 3 (two saves), Medium 1 : 3 (two), Medium 1 : 1, Large 1 : 2, Very Large 1 : 1 and a Very Large 1 : 1 save with missing mods. **Open:** a save with `map.size` rewritten to 2 and a Tiny-sized terrain was not loaded, which would show that the width and height really are ignored; no 1 : 4 or 1 : 5 save was in the screenshots (the Tiny 1 : 5 save of the [map-format tests](test-games.md#map-format-tests) is kept, with a Tiny 1 : 2; a 1 : 4 one must be made again).

## File size

A save's file size follows the area class (a log-log correlation of 0.88 between area and file size over all the saves read), then what is built. The file is about 28% of the decompressed stream (median; 9% to 46%). Within one size the spread is wide: 14336 x 14336 m saves run from 26 to 297 MB. A Tiny save is 4 to 6 MB, a Small one 14 to 41 MB (median 28), and the largest sizes 100 to 350 MB.

## Open

- The blank rows of the table: Tiny 1 : 1, Small 1 : 4 and 1 : 5, every 1 : 4 except Tiny, Medium to Very Large 1 : 5, Huge 1 : 3 to 1 : 5 and Megalomaniac 1 : 3 and 1 : 4.
- Why the saves above disagree with their settings.
- Why Tiny 1 : 4 gives the 1 : 3 shape while Tiny 1 : 5 follows the area rule.
