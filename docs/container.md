# Container

Checked on format versions 568 to 604.

## Reading

A `.sav` is zstd-compressed. The game writes two frames:

1. One frame holding the whole data stream.
2. An empty frame: `28 b5 2f fd 20 00 01 00 00`.

Neither frame has a content checksum. Decompress both (or read across frames) to get the stream. Expect hundreds of megabytes once decompressed; a played giant map of ours came to over 600 MB.

The stream starts with the magic `tf**` and the format version (see [header.md](header.md)).

## No second layer

**Observed** on 568 and 604 in three catalog saves (the first is 568, the other two 604), [6104655](https://mod.io/g/transportfever3/m/beta-save), [6414325](https://mod.io/g/transportfever3/m/multiplayerpanda) and [6426500](https://mod.io/g/transportfever3/m/boi-vs-luca-02) (200 to 335 MB decompressed). The stream begins at once with `tf**` and the version, and nothing inside it is a second compressed layer:

- No zstd frame magic, no LZ4 frame magic and no legacy LZ4 magic anywhere in the stream. The only picture magics are the header's preview JPEG.
- The stretches of near-random bytes (64 KB blocks above 7.2 bits per byte, a few MB each, mostly early in the stream) are not compressed data. zstd shrinks them by 5 to 12%, and in the 4-byte lanes one lane is far less random than the other three, the pattern of an array of 32-bit floats.
- A raw LZ4 block has no magic, so a hidden one was not ruled out by decoding. The two checks above make it very unlikely.

## No footer

**Observed** on 568, 585, 601 and 604 in four catalog saves: [6105772](https://mod.io/g/transportfever3/m/autosave-map-1-2003-10-13) (568), [6204931](https://mod.io/g/transportfever3/m/empty-quarter) (585), [6420121](https://mod.io/g/transportfever3/m/subarctic-002) (601) and [6104655](https://mod.io/g/transportfever3/m/beta-save) (568). The stream ends with the music player's table ([script-states.md](script-states.md#the-music-player-state)); the last 64 bytes are the same in all four, so nothing after it records the stream's length or a checksum. The stream length does not appear as a u32 or u64 in the first 4 KB or the last 256 bytes. The last four bytes match neither the CRC-32 nor the Adler-32 of the stream before them (tried with the last 4 to 16 bytes left out); xxHash, the hash the older games' LZ4 used, was not tried. So a reader finds the end by parsing every structure in order.

The older games differ. A 2016 forum thread, ["Train Fever Savegame Format"](https://www.transportfever.net/thread/4659-train-fever-savegame-format/) (eis_os, Transport Fever Community, Modding board), says Train Fever saves are LZ4-compressed twice, and a 2017 [Steam modding thread](https://steamcommunity.com/app/446800/discussions/2/2592234299565766774/) says the same of Transport Fever. Both are forum claims, not checked here. The Train Fever thread also lays out a header starting `tf**` plus a version, followed by a mod list and a key/value settings dictionary, and its author published a codec at [eis-os/TFSavCodec](https://github.com/eis-os/TFSavCodec/). No Transport Fever 2 save was tested, so its container is **Open**.

## Writing a save back

**Confirmed** on format 604, editor saves and one converted regular save:

- Write one zstd frame (level 3, no checksum) followed by the same empty frame. The game loads it.
- The compressed file will not match the original byte for byte, because the game's compressor settings are not known. The decompressed stream can match exactly.
- Patching values in place (same length) leaves the rest of the stream untouched. Nothing in the stream records where a section starts or how long it is, so a section may also grow or shrink: write the new encoding in place of the old one and keep everything before and after it unchanged. tf3-save-editor does this for the money journal and script states.

## Preview file

The game writes a `.jpg` next to every save, with the same base name. It is the same picture as the preview in the header, at three times the size. What the game does when the `.jpg` is missing is **open**.
