"""Shared helpers for the TF3 save tools: zstd, cargo ids and the town record scan.

See docs/container.md, docs/cargo-ids.md and docs/town-records.md. Standard library
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

# Cargo type ids as seen in saves from this install (temperate economy).
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
