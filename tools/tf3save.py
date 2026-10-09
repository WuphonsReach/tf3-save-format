"""Shared helpers for the TF3 save tools: zstd, cargo ids and the town record scan.

See docs/container.md, docs/cargo-ids.md, docs/town-records.md and docs/script-states.md. Standard library
only (Python 3.14 for zstd; older Python needs the `zstandard` package).
"""
import math
import re
import struct

try:
    from compression import zstd  # Python 3.14+
    decompress = zstd.decompress
    compress = lambda b: zstd.compress(b, level=3)
except ImportError:
    import io
    import zstandard
    decompress = lambda b: zstandard.ZstdDecompressor().stream_reader(io.BytesIO(b), read_across_frames=True).read()
    compress = lambda b: zstandard.ZstdCompressor(level=3, write_checksum=False).compress(b)

# The game writes the data frame followed by this empty frame.
EMPTY_FRAME = bytes.fromhex("28b52ffd2000010000")

# Cargo type ids as seen in saves (the same ids hold in every economy; see docs/cargo-ids.md).
KNOWN_IDS = {"fish": 6, "meat": 7, "beverages": 8, "vegetables": 9, "planks": 13, "vehicles": 14,
             "machines": 16, "fuel": 20, "clothes": 27, "tinned_food": 28, "tools": 30,
             "furniture": 31, "glass": 32, "bricks": 33, "cement": 15}
TEMPERATE_NAMES = {i: n for n, i in KNOWN_IDS.items()}

RECORD_SIZE = 78
# caps (3 x u32), 4 x f32, 5 zero bytes, then a small cargo count. Validated in scan_records.
_LOOSE = re.compile(rb"(?s)(.{12})(.{16})\x00\x00\x00\x00\x00([\x01-\x03])\x00\x00\x00")


def scan_records(data):
    """Town records in the 78-byte layout that has one commercial and one industrial cargo.

    Returns dicts with `offset`, `caps` (res, com, ind), `floats`, `com_count`, `ind_count`,
    `id` ({"com", "ind"} cargo type ids), `id_off` and `w_off` (byte offsets of the id and
    weight fields). The pattern is checked for plausible capacities (10 to 1,000,000) and
    floats (0.05 to 20) so it does not match unrelated data. On a 34-town played save it finds
    all 34, including a town whose floats are not 1.0. Towns that have run for a while use
    other record shapes and are not found.
    """
    recs = []
    for m in _LOOSE.finditer(data):
        caps = struct.unpack("<3I", m.group(1))
        floats = struct.unpack("<4f", m.group(2))
        if not all(10 <= c <= 1_000_000 for c in caps):
            continue
        if not all(math.isfinite(x) and 0.05 <= x <= 20 for x in floats):
            continue
        s = m.start()
        com_n, com, ind_n, ind = struct.unpack("<II4xII", data[s + 33:s + 53])
        if com_n != 1 or ind_n != 1:
            continue
        recs.append(dict(offset=s, caps=caps, floats=floats, com_count=com_n, ind_count=ind_n,
                         id={"com": com, "ind": ind},
                         id_off={"com": s + 37, "ind": s + 49}, w_off={"com": s + 41, "ind": s + 53}))
    return recs


# The game speed component: ... 09 00.. | 01 00 00 00 | u32 millisPerDay | u32 playSpeed | 8 zero bytes
# | 01 00 00 00 | 08 00.. | 01 00 00 00 | u64 t1 | 01 | u64 t2. See docs/script-states.md.
_GAME_SPEED = re.compile(rb"(?s)\x09\0{7}\x01\0\0\0(.{4})(.{4})\0{8}\x01\0\0\0\x08\0{7}\x01\0\0\0(.{8})\x01(.{8})")


def _game_speed_match(data):
    hits = list(_GAME_SPEED.finditer(data))
    return hits[0] if len(hits) == 1 else None


def find_game_speed(data):
    """The calendar speed field and its neighbours, or None if the pattern is not found once.

    Returns a dict: `offset` (of the millisPerDay u32), `millis_per_day` (4000 at 1.00x, 0 when
    the calendar is stopped), `play_speed` (0 when the game was paused), `t1` and `t2` (clock
    values; t1 minus t2 is 200 times play_speed). Found exactly once in every stream checked
    (format 568 to 604); a second match makes this return None rather than guess.
    """
    h = _game_speed_match(data)
    if h is None:
        return None
    return dict(offset=h.start(1), millis_per_day=struct.unpack("<I", h.group(1))[0],
                play_speed=struct.unpack("<I", h.group(2))[0],
                t1=struct.unpack("<Q", h.group(3))[0], t2=struct.unpack("<Q", h.group(4))[0])


def find_day_table(data):
    """The tick-to-date table that follows the game speed component, or None.

    A list of (tick, day) pairs: `day` is a Julian day number (2415021 is 1 January 1900) and
    `tick` the game clock value at which that day started. See docs/script-states.md. Use
    `date_of_day` to turn a day number into a date. Entries are appended when the date changes;
    in a game that never had its date set they are one per day with consecutive day numbers.
    """
    h = _game_speed_match(data)
    if h is None:
        return None
    p = h.end()
    n = struct.unpack_from("<I", data, p)[0]
    if p + 4 + 12 * n > len(data):
        return None
    return [struct.unpack_from("<QI", data, p + 4 + 12 * i) for i in range(n)]


def date_of_day(day):
    """Julian day number (as in the day table) to a datetime.date, or None if out of range."""
    import datetime
    try:
        return datetime.date.fromordinal(day - 1721425)
    except (ValueError, OverflowError):
        return None
