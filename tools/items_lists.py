#!/usr/bin/env python3
"""Read the `items*` statistics lists of a TF3 save, per period up to the save's clock.

Usage:
  items_lists.py SAVE.sav (--cargo ID | --list REGEX) [--periods N]
  items_lists.py SAVE.sav --table LABEL=OFFSET:LIST [LABEL=OFFSET:LIST ...] [--from PERIOD]
  items_lists.py SAVE.sav --entries OFFSET:LIST

SAVE may also be a stream already decompressed to a file (add --stream); a whole save takes a few
seconds to decompress, so keep the stream when you run this many times. Output goes to the
terminal. Only reads: no save is written.

First form: every group with a list for the cargo (or a list name matching REGEX) with each
matching list's last total, the time of its last entry, how many periods before the save's clock
that was, and its change in each of the last N periods (default 8). Trailing zeros are kept, so a
stage that stopped shows as zeros. A period is 1,461,000 clock units; the last one printed is
still open. The clock is the newest time in any list. A list's first entry can carry a total from
before the list was kept (docs/spoilage.md, Unsatisfied counts); it lands in that entry's period. Second form: one row per period for the
lists you name, to line stages up. Third form: every entry of one list with its change.

OFFSET is a stream offset printed by the first form (decimal or 0x hex). Offsets move between
saves, so find a group by its figures, never by a remembered offset. Format and method:
docs/statistics-lists.md and docs/analysis-examples/. Which entity owns a group is not known
(docs/statistics-lists.md, Groups); a group is matched by equal totals and per-period figures.
"""
import argparse
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tf3save import decompress  # noqa: E402

PERIOD = 1_461_000
MAX_U64 = 2 ** 64 - 1
NAME_AT = re.compile(rb"[\x05-\x30]\x00\x00\x00items[A-Za-z]+[0-9]*(?:_c[0-9]+)?")


def read_field(data, p):
    """(name, times, totals, end) of the field at p (docs/statistics-lists.md), or None."""
    length = struct.unpack_from("<I", data, p)[0]
    if not 3 <= length <= 48:
        return None
    name = bytes(data[p + 4:p + 4 + length])
    if not re.fullmatch(rb"[A-Za-z0-9_]+", name):
        return None
    q = p + 4 + length
    n = struct.unpack_from("<I", data, q)[0]
    times = struct.unpack_from(f"<{n}Q", data, q + 4)
    q += 4 + 8 * n
    m = struct.unpack_from("<I", data, q)[0]
    totals = struct.unpack_from(f"<{m}Q", data, q + 4)
    q += 4 + 8 * m
    if n != m:
        return None
    return name.decode(), times, totals, q + 1


def find_groups(data):
    """Every run of back-to-back `items*` fields as (offset, key, [(name, times, totals)])."""
    groups = []
    cur = None
    end = -1
    for hit in NAME_AT.finditer(data):
        start = hit.start()
        if start < end:
            continue
        try:
            field = read_field(data, start)
        except (struct.error, ValueError):
            field = None
        if not field:
            continue
        if cur is None or start != end:
            if cur:
                groups.append(cur)
            cur = (start, struct.unpack_from("<I", data, start - 8)[0], [])
        cur[2].append(field[:3])
        end = field[3]
    if cur:
        groups.append(cur)
    return groups


def total_at(times, totals, limit):
    """The list's total at the last entry before `limit` (0 before the first)."""
    value = 0
    for t, v in zip(times, totals):
        if t < limit and t != MAX_U64:
            value = v
    return value


def per_period(times, totals, count):
    """Change in each of periods 1..count (period k ends at k * PERIOD)."""
    out = []
    prev = 0
    for k in range(1, count + 1):
        value = total_at(times, totals, k * PERIOD)
        out.append(value - prev)
        prev = value
    return out


def newest_time(groups):
    return max((t for _, _, fields in groups for _, times, _ in fields for t in times if t != MAX_U64), default=0)


def cargo_pattern(cargo):
    return re.compile(rf"items[A-Za-z]+{cargo}|items[A-Za-z]*\d?_c{cargo}")


def locate(groups, spec):
    """The (times, totals) of `OFFSET:LIST`."""
    offset, _, name = spec.partition(":")
    for start, _, fields in groups:
        if start == int(offset, 0):
            for fname, times, totals in fields:
                if fname == name:
                    return times, totals
    sys.exit(f"no list {spec} (offsets move between saves; run the first form again)")


def main():
    ap = argparse.ArgumentParser(description="Read the items* statistics lists per period.")
    ap.add_argument("save")
    ap.add_argument("--stream", action="store_true", help="SAVE is an already decompressed stream")
    ap.add_argument("--cargo", help="cargo id (from the save's own cargo list)")
    ap.add_argument("--list", dest="regex", help="regex a whole list name must match")
    ap.add_argument("--periods", type=int, default=8, help="periods to print, newest last (default 8)")
    ap.add_argument("--table", nargs="+", metavar="LABEL=OFFSET:LIST")
    ap.add_argument("--from", dest="first", type=int, default=1, help="first period of --table (default 1)")
    ap.add_argument("--entries", metavar="OFFSET:LIST")
    args = ap.parse_args()

    with open(args.save, "rb") as f:
        raw = f.read()
    data = raw if args.stream else decompress(raw)
    groups = find_groups(data)
    now = newest_time(groups)
    count = now // PERIOD + 1
    print(f"newest list time {now}, period {count} (still open)")

    if args.entries:
        times, totals = locate(groups, args.entries)
        prev = 0
        for t, v in zip(times, totals):
            print(t, v - prev, v)
            prev = v
    elif args.table:
        cols = []
        for item in args.table:
            label, _, spec = item.partition("=")
            times, totals = locate(groups, spec)
            cols.append((label, per_period(times, totals, count)))
        print("period " + " ".join(f"{label[:10]:>10}" for label, _ in cols))
        for k in range(args.first, count + 1):
            print(f"{k:>6} " + " ".join(f"{d[k - 1]:>10}" for _, d in cols))
    else:
        if args.regex:
            want = re.compile(args.regex)
        elif args.cargo:
            want = cargo_pattern(args.cargo)
        else:
            ap.error("give --cargo, --list, --table or --entries")
        for start, key, fields in groups:
            rows = []
            for name, times, totals in fields:
                if want.fullmatch(name) and times:
                    ago = (now - times[-1]) / PERIOD
                    rows.append((name, totals[-1], times[-1], ago, per_period(times, totals, count)[-args.periods:]))
            if rows:
                print(f"{start:#x} key {key}")
                for name, total, last, ago, per in rows:
                    print(f"  {name} total {total} last entry {last} ({ago:.1f} periods ago) per period {per}")


if __name__ == "__main__":
    main()
