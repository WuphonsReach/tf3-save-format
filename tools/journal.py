#!/usr/bin/env python3
"""Read the player's money journal from a TF3 save and say how long the game has been played.

Usage: journal.py SAVE.sav            (prints the play summary as JSON)

Reads only. The journal layout and its place in the entity data are in tf3-save-editor's FORMAT.md; this follows the
finder in its `crates/lib/src/journal.rs` (notice: THIRD_PARTY_NOTICES.md). docs/finances.md covers periods and the
way old bookings are merged. mine_summary.py imports `play_summary`; it lives in its own module so that a change here
rebuilds the summaries and leaves the map pictures alone (mine_saves.py).

A booking is 21 bytes: i64 time, i64 amount, five u8 categories (type, construction, maintenance, other, carrier).
The journal is `u32 count`, the bookings, `i64 balance`. It sits after the edge-addon name table, so it is found by
that pattern, not by an offset, and it is found when the header money is 0 as well.

How much a game has been played:
- The clock is the game's own millisecond clock (docs/calendar.md). A period is 1,461,000 clock units, the column
  width of the Finances tab (docs/finances.md#periods).
- The starting capital and loan bookings are not play. Play is a booking of type CONSTRUCTION, ACQUISITION,
  MAINTENANCE, INCOME or SUBSIDY. `play_periods` is the span from the period of the first to the period of the
  last of those, counted in whole periods (0 where there is none).
- Old bookings are merged by month and later by year, so a booking count says little about play, but the merged
  bookings keep their period. `active_periods` counts the periods that hold at least one play booking and
  `income_periods` those that hold an income booking.
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

ENTRY = struct.Struct("<qqBBBBB")
PERIOD = 1_461_000
EDGE_TABLE_ANCHOR = b"edge_addons/barrier_track_b.edge"
MAX_IDS = 1 << 20
LATE_START_WINDOW = 64

# type byte: LOAN 0, INTEREST 1, CONSTRUCTION 2, ACQUISITION 3, MAINTENANCE 4, INCOME 5, OTHER 6, SUBSIDY 7
PLAY_TYPES = {2, 3, 4, 5, 7}
INCOME = 5


def _u32(data, at):
    return struct.unpack_from("<I", data, at)[0] if 0 <= at <= len(data) - 4 else None


def _skip_text(data, at):
    n = _u32(data, at)
    if n is None or n > 512:
        return None
    end = at + 4 + n
    if end > len(data) or not all(0x20 <= b < 0x7f for b in data[at + 4:end]):
        return None
    return end


def read_at(data, at):
    """(entries, balance) of the journal starting at `at`, or None if what is there is not a journal."""
    n = _u32(data, at)
    if n is None or at + 4 + n * ENTRY.size + 8 > len(data):
        return None
    entries = list(ENTRY.iter_unpack(memoryview(data)[at + 4:at + 4 + n * ENTRY.size]))
    last = -1
    for t, _a, ty, co, ma, ot, ca in entries:
        if t < last or ty > 7 or co > 7 or ma > 3 or ot != 0 or ca > 5:
            return None
        last = t
    return entries, struct.unpack_from("<q", data, at + 4 + n * ENTRY.size)[0]


def find_journal(data, header_money):
    """(offset, entries, balance) of the player's journal, or None.

    By position: after the edge-addon name table (the base game's last entry `barrier_track_b.edge` with index 5,
    then entries added by mods, a u32, a vec<u32>, a u32 and the bytes 01 00 00 00 00). The stored balance must equal
    the header money or the sum of the amounts; a start up to 64 bytes later is accepted when the balance equals the
    header money."""
    pos = 0
    while (hit := data.find(EDGE_TABLE_ANCHOR, pos)) >= 0:
        pos = hit + 1
        at = hit + len(EDGE_TABLE_ANCHOR)
        if _u32(data, at) != 5:
            continue
        at += 4
        while (path_at := _skip_text(data, at)) is not None and (end := _skip_text(data, path_at)) is not None \
                and end > path_at + 4 and _u32(data, end) is not None:
            at = end + 4
        ids = _u32(data, at + 4)
        if ids is None or ids > MAX_IDS:
            continue
        usual = at + 8 + ids * 4 + 4 + 5
        if _u32(data, usual - 5) == 1 and data[usual - 1:usual] == b"\0":
            j = read_at(data, usual)
            if j and (j[1] == header_money or j[1] == sum(e[1] for e in j[0])):
                return usual, *j
        for start in range(usual + 1, usual + LATE_START_WINDOW):
            j = read_at(data, start)
            if j and j[0] and j[1] == header_money:
                return start, *j
    return _find_by_balance(data, header_money) if header_money else None


def _find_by_balance(data, balance):
    """Fallback for saves without the name table (568): search the balance bytes, then walk back over 21-byte
    bookings until the stored count equals the number walked and the amounts sum to the balance. The newest booking
    must have a non-zero amount, which keeps runs of zero bytes from becoming long walks."""
    target = struct.pack("<q", balance)
    pos = 0
    while (bal_at := data.find(target, pos)) >= 0:
        pos = bal_at + 1
        later = None
        for k in range(1, bal_at // ENTRY.size + 1):
            at = bal_at - k * ENTRY.size
            if at < 4:
                break
            t, a, ty, co, ma, ot, ca = ENTRY.unpack_from(data, at)
            if ty > 7 or co > 7 or ma > 3 or ot != 0 or ca > 5 or t < 0 or (later is not None and t > later) \
                    or (k == 1 and a == 0):
                break
            later = t
            if _u32(data, at - 4) == k:
                j = read_at(data, at - 4)
                if j and j[1] == sum(e[1] for e in j[0]):
                    return at - 4, *j
                break
    return None


def play_summary(data, header_money):
    """The journal's facts as a dict for the mining summary, or None where no journal was found."""
    found = find_journal(data, header_money)
    if found is None:
        return None
    _, entries, balance = found
    play = [e for e in entries if e[2] in PLAY_TYPES]
    total = sum(e[1] for e in entries)
    out = {
        "bookings": len(entries),
        "balance_stored": balance,
        "balance_sum": total,
        "last_time": entries[-1][0] if entries else None,
        "first_play_time": play[0][0] if play else None,
        "last_play_time": play[-1][0] if play else None,
        "play_periods": 0,
        "active_periods": 0,
        "income_periods": 0,
        "income_total": sum(e[1] for e in entries if e[2] == INCOME),
    }
    if play:
        out["play_periods"] = play[-1][0] // PERIOD - play[0][0] // PERIOD + 1
        out["active_periods"] = len({e[0] // PERIOD for e in play})
        out["income_periods"] = len({e[0] // PERIOD for e in play if e[2] == INCOME})
    return out


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".sav"):
        sys.exit("usage: journal.py SAVE.sav")
    data = decompress(open(sys.argv[1], "rb").read())
    from save_header import read_header
    json.dump(play_summary(data, read_header(sys.argv[1], data)["money"]), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
