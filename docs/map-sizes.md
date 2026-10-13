# Map sizes

How the Map Size and Map Format options set the map's width and height in a save. Read from the header's width and height and the stored `map.size` and `map.format` of 445 saves (208 mod.io catalog saves and 237 of our own). **Observed**, 599 to 604 for the settings; the sizes alone also fit on 568 and 585 (no settings stored there). Labels are defined in [README.md](README.md).

## The rule

**Observed (599 to 604):** each Map Size is a set area in km², and Map Format only changes the shape of that area. Take the 1:1 map of a size: its 1:2 and 1:3 maps hold about the same area, as a longer, narrower rectangle. The two are not exactly equal, because every side is a whole number of 256 m tiles (all 20 sizes seen are multiples of 256), so the area of one size differs by up to a few percent between formats.

The settings are stored as 1-based positions in the lists of [settings.md](settings.md#the-options): `map.size` 1 is Tiny and 8 is Gigantomaniac, `map.format` 1 is 1 : 1 and 5 is 1 : 5. The header's width and height ([header.md](header.md)) are in metres.

| `map.size` | 1 : 1 | 1 : 2 | 1 : 3 | Area, km² |
|---|---|---|---|---|
| 1 Tiny | not seen | not seen | 2048 x 6144 | 12.6 |
| 2 Small | 8192 x 8192 | not seen | 4608 x 13824 | 64 to 67 |
| 3 Medium | 11264 x 11264 | 8192 x 16384 | 6656 x 19968 | 127 to 134 |
| 4 Large | 14336 x 14336 | 10240 x 20480 | 8192 x 24576 | 201 to 210 |
| 5 Very Large | 16384 x 16384 | 11264 x 22528 | 9216 x 27648 | 254 to 268 |
| 6 Huge | 20480 x 20480 | 14336 x 28672 | not seen | 411 to 419 |
| 7 Megalomaniac | 24576 x 24576 | 16896 x 33792 | not seen | 571 to 604 |
| 8 Gigantomaniac | 28672 x 28672 | 20480 x 40960 | 16384 x 49152 | 805 to 839 |

One 1 : 5 map was seen: Megalomaniac, 10752 x 53760 m (578 km², 601, mod.io [6386596](https://mod.io/g/transportfever3/m/cargo-transfer)). The default Map Size is Medium and the default format 1 : 1 ([settings.md](settings.md#the-options)), which is 11264 x 11264 m.

## Tiny

**Observed (604):** Tiny 1 : 3 and Tiny 1 : 4 both give 2048 x 6144 m (8 x 24 tiles), see [the terrain note](terrain.md#the-terrain-record). A 1 : 4 map of 12.6 km² would be about 1792 x 7168 m, so 2048 m may be a minimum width. **Open:** no Tiny 1 : 1 or 1 : 2 save was seen.

## Saves that disagree with their settings

**Observed (604, 601):** 11 of the 208 catalog saves store a size or format that does not match their real dimensions, for example a 28672 x 28672 m map stored as `map.size` 5, or a 16384 x 16384 m map stored as size 3. Mod.io ids: [6419141](https://mod.io/g/transportfever3/m/autosave-emerald-shores-1965-07-29), [6423816](https://mod.io/g/transportfever3/m/brasil), [6425276](https://mod.io/g/transportfever3/m/redrock-bends), [6432023](https://mod.io/g/transportfever3/m/kaspars), [6433003](https://mod.io/g/transportfever3/m/mapa-brasil), [6435288](https://mod.io/g/transportfever3/m/yf-el), [6440248](https://mod.io/g/transportfever3/m/xyfel), [6440867](https://mod.io/g/transportfever3/m/deutschland-map), and 6414660, 6418114 and 6437320 (links not checked). Whether these were made in the map editor, edited by hand, or had their settings rewritten on a load is **Open**. For a map's size, trust the header and the terrain record, not the stored settings.

## The experimental notice in the load dialog

**Confirmed (604):** the Load Game dialog shows a yellow line, "The map size is experimental.", for a save whose stored `map.size` is 1 (Tiny) or 6 to 8 (Huge, Megalomaniac, Gigantomaniac). It shows "The map format is experimental." for `map.format` 4 or 5, and one line naming both when both are out of range. It is not a separate flag in the header and not tied to the map editor: the game script that draws it (`gui/menu/savegame_react_util.tl` in `base/content/gui.zip`) compares the two stored settings with the range the desktop New Game options allow without the experimental map features: `map.size` 2 to 5 (Small to Very Large) and `map.format` 1 to 3. `base/mod.json` lists those two parameter sets, one without the tag `experimentalMapFeatures` and one with it. The header's width and height are not read.

Eleven saves seen in the dialog agree with that rule: notice on Tiny 1 : 3 (a converted editor map, see [editor-saves.md](editor-play.md#a-converted-editor-map-loaded-as-a-played-game)) and Gigantomaniac 1 : 2; none on Small 1 : 3 (two saves), Medium 1 : 3 (two), Medium 1 : 1, Large 1 : 2, Very Large 1 : 1 and a Very Large 1 : 1 save with missing mods. **Open:** a save with `map.size` rewritten to 2 and a Tiny-sized terrain was not loaded, which would show that the width and height really are ignored; no 1 : 4 or 1 : 5 save was in the screenshots.

## File size

A save's file size follows the area class (a log-log correlation of 0.88 between area and file size over the 445 saves), then what is built. The file is about 28% of the decompressed stream (median; 9% to 46%). Within one size the spread is wide: 14336 x 14336 m saves run from 26 to 297 MB. A Tiny save is 4 to 6 MB, a Small one 14 to 41 MB (median 28), and the largest sizes 100 to 350 MB.

## Open

- Tiny 1 : 1 and 1 : 2, Huge 1 : 3 and Megalomaniac 1 : 3: not seen.
- Why the 11 saves above disagree with their settings.
- Whether 2048 m is a minimum width.
