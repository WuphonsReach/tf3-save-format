# Container

Checked on format versions 568 to 604.

## Reading

A `.sav` is zstd-compressed. The game writes two frames:

1. One frame holding the whole data stream.
2. An empty frame: `28 b5 2f fd 20 00 01 00 00`.

Neither frame has a content checksum. Decompress both (or read across frames) to get the stream. Streams are large: about 190 MB for a mid-size map, over 600 MB for a played giant map.

The stream starts with the magic `tf**` and the format version (see [header.md](header.md)).

## Writing a save back

**Confirmed** on format 604, editor saves and one converted regular save:

- Write one zstd frame (level 3, no checksum) followed by the same empty frame. The game loads it.
- The compressed file will not match the original byte for byte, because the game's compressor settings are not known. The decompressed stream can match exactly.
- Patching values in place (same length) leaves the rest of the stream untouched. Since there are no section sizes or offsets, a section can also be re-encoded at a different length and spliced back between the bytes around it. tf3-save-editor does this for the money journal and script states.

## Preview file

The game writes a `.jpg` next to every save, with the same base name. It is the same picture as the preview in the header, at three times the size. What the game does when the `.jpg` is missing is **open**.
