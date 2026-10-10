"""Shared helpers for the TF3 save tools: zstd, cargo ids and the town record scan.

See docs/container.md, docs/cargo-ids.md, docs/town-records.md, docs/calendar.md and docs/script-states.md. Standard library
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

# Cargo type ids as seen in base-only games (see docs/cargo-ids.md). A game with a cargo mod
# shifts them: read the save's own list with `cargo_list` instead.
KNOWN_IDS = {"fish": 6, "meat": 7, "beverages": 8, "vegetables": 9, "planks": 13, "vehicles": 14,
             "machines": 16, "fuel": 20, "clothes": 27, "tinned_food": 28, "tools": 30,
             "furniture": 31, "glass": 32, "bricks": 33, "cement": 15}
TEMPERATE_NAMES = {i: n for n, i in KNOWN_IDS.items()}

_CARGO_LIST_FIRST = struct.pack("<I", 34) + b"cargos/passengers/passengers.cargo"
_CARGO_PATH = re.compile(rb"cargos/([A-Za-z0-9_]+)/\1\.cargo\Z")


def cargo_entries(data):
    """The save's cargo list as [(id, name, source)] in list order, or None if no list is found.

    The list sits near the start of the stream: a u32 count, then that many entries of `str`
    source (the id of the mod that adds the cargo, empty for base cargo), `str` path
    (`cargos/<name>/<name>.cargo`) and a u32 id. The ids are 0 to count - 1, each once, in list
    order. A game with a cargo mod has more entries and different ids from the base game. Other
    places in the stream also hold a `cargos/passengers` string, so a list needs at least two
    entries. See docs/cargo-ids.md.
    """
    pos = data.find(_CARGO_LIST_FIRST)
    while pos >= 0:
        entries = _read_cargo_list(data, pos)
        if entries:
            return entries
        pos = data.find(_CARGO_LIST_FIRST, pos + 1)
    return None


def cargo_list(data):
    """The cargo names by id (index 0 is passengers), or None. See `cargo_entries`."""
    entries = cargo_entries(data)
    return [name for _, name, _ in entries] if entries else None


def _read_cargo_list(data, first):
    # `first` is the path of the first entry (passengers); its source string is empty, so the
    # entry starts 4 bytes earlier and the count 4 bytes before that.
    if first < 8:
        return None
    count, source0 = struct.unpack_from("<II", data, first - 8)
    if source0 != 0 or not 2 <= count <= 1000:
        return None
    out, p = [], first - 4
    try:
        for i in range(count):
            n = struct.unpack_from("<I", data, p)[0]
            if n > 200:
                return None
            source = data[p + 4:p + 4 + n]
            p += 4 + n
            n = struct.unpack_from("<I", data, p)[0]
            m = _CARGO_PATH.match(data[p + 4:p + 4 + n]) if n < 200 else None
            if not m:
                return None
            cid = struct.unpack_from("<I", data, p + 4 + n)[0]
            p += 4 + n + 4
            if cid != i:
                return None
            out.append((cid, m.group(1).decode(), source.decode("utf-8", "replace")))
    except struct.error:
        return None
    return out


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
# | 01 00 00 00 | 08 00.. | 01 00 00 00 | u64 t1 | 01 | u64 t2. See docs/calendar.md.
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
    `tick` the game clock value at which that day started. See docs/calendar.md. Use
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


def calendar_speed_label(millis_per_day):
    """Calendar speed as the game shows it, or None for a value that is no slider step."""
    if millis_per_day == 0:
        return "Paused (date stopped)"
    speed = 4000 / millis_per_day
    return f"{speed:.2f}x" if millis_per_day in (1000, 2000, 4000, 8000, 16000) else None


def day_table_regular(table):
    """True if the day table is one entry per day: consecutive day numbers and rising ticks."""
    return all(d2 == d1 + 1 and t2 > t1 for (t1, d1), (t2, d2) in zip(table, table[1:]))


# Lua values (docs/lua-values.md): u32 tag, then 0 nil, 1 bool (u8), 2 number (f64), 3 string
# (`str`), 4 table (u8 flag; 1 is followed by a u32 pair count and the pairs). The same encoding
# tf3-save-editor reads in `lua.rs` (see THIRD_PARTY_NOTICES.md).
def lua_value(data, p):
    """The Lua value at byte p as (value, end). Tables become dicts, numbers floats."""
    tag = struct.unpack_from("<I", data, p)[0]
    p += 4
    if tag == 0:
        return None, p
    if tag == 1:
        return bool(data[p]), p + 1
    if tag == 2:
        return struct.unpack_from("<d", data, p)[0], p + 8
    if tag == 3:
        n = struct.unpack_from("<I", data, p)[0]
        if p + 4 + n > len(data):
            raise ValueError(f"string past the end at {p}")
        return bytes(data[p + 4:p + 4 + n]).decode("utf-8", "replace"), p + 4 + n
    if tag == 4:
        if not data[p]:
            return None, p + 1
        return _lua_pairs(data, p + 1)
    raise ValueError(f"unknown lua tag {tag} at {p - 4}")


def _lua_pairs(data, p):
    n = struct.unpack_from("<I", data, p)[0]
    p += 4
    if n > (len(data) - p) // 8:
        raise ValueError(f"pair count {n} too large at {p - 4}")
    out = {}
    for _ in range(n):
        k, p = lua_value(data, p)
        out[k], p = lua_value(data, p)
    return out, p


def script_state(data, path):
    """The state table of the script at `path` as a dict, or None if it is not found.

    `path` as stored, for example "game_mechanics/company/company.gs". In the saves checked the
    path string (`str`) is followed by one byte, a u32 pair count and the pairs, with no leading
    table tag (docs/script-states.md). Each hit is parsed and the first that reads as a table with
    string keys is taken. Checked on 585 to 604.
    """
    pat = struct.pack("<I", len(path)) + path.encode()
    pos = data.find(pat)
    while pos != -1:
        try:
            state, _ = _lua_pairs(data, pos + len(pat) + 1)
            if all(isinstance(k, str) for k in state):
                return state
        except (ValueError, struct.error, IndexError, RecursionError):
            pass
        pos = data.find(pat, pos + 1)
    return None


# Rank names as the company window lists them (English UI, 604); `potentialLevel` is the rank
# shown. See docs/company.md.
RANKS = ["Junior", "Mechanic", "Engineer", "Coordinator", "Expert", "Team Leader", "Supervisor", "Manager",
         "Director", "Senior Director", "CEO", "Chairperson", "Vice President", "President", "Tycoon"]

# New Game options: settings key -> (default index, labels in screen order). Taken from the
# game's base/mod.json (604 build, desktop lists; where a key has a longer list for the
# experimental map features, that one). A stored setting is its list position plus 1
# (docs/settings.md). English UI names.
SETTING_OPTIONS = {
    "map.size": (2, ["Tiny", "Small", "Medium", "Large", "Very Large", "Huge", "Megalomaniac", "Gigantomaniac"]),
    "map.format": (0, ["1 : 1", "1 : 2", "1 : 3", "1 : 4", "1 : 5"]),
    "locations.towns.frequency": (2, ["Sparse", "Scattered", "Medium", "Dense", "Packed"]),
    "locations.towns.populationDensity": (2, ["50%", "75%", "100%", "150%", "200%"]),
    "locations.industry.initialIndustryDensity": (2, ["Sparse", "Scattered", "Medium", "Dense", "Packed"]),
    "locations.industry.targetIndustryDensity": (2, ["Sparse", "Scattered", "Medium", "Dense", "Packed"]),
    "locations.industry.industryProductivity": (2, ["50%", "75%", "100%", "150%", "200%"]),
    "advancedOptions.vehiclePurchaseCostScale": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.passengerIncome": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.cargoIncome": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.reforestation": (1, ["Off", "On"]),
    "advancedOptions.infrastructurePurchaseCostScale": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.infrastructureMaintenanceScale": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.vehicleMaintenanceScale": (2, ["50%", "75%", "100%", "125%", "150%"]),
    "advancedOptions.vehicleMaintenanceEffectScale": (2, ["None", "Low", "Medium", "High", "Very High"]),
    "economy.industryDevelopment.closureProbability": (1, ["Never", "Rarely", "Sometimes", "Often", "Very Often"]),
    "economy.townDevelopment.cargoNeedsPerTown": (1, ["2 Cargo Types", "Up to 4 Cargo Types", "Up to 6 Cargo Types"]),
    "advancedOptions.trafficSpeedSensitivityScale": (4, ["0%", "25%", "50%", "75%", "100%", "125%", "150%", "175%", "200%"]),
    "advancedOptions.subventionMode": (2, ["Never", "Rarely", "Sometimes", "Often", "Very Often"]),
    "advancedOptions.subventionRisk": (1, ["None", "Fair", "Risky", "Very Risky"]),
    "advancedOptions.landmarkResources": (2, ["None", "Low", "Normal", "High", "Very High"]),
    "advancedOptions.inflationFactor": (2, ["None", "Low", "Normal", "High", "Very High"]),
    "townConfig.sensitivityUrbanCare": (1, ["Off", "On"]),
    "townConfig.sensitivityTrafficCongestion": (3, ["Off", "Very Low", "Low", "Normal", "High", "Very High", "Extreme"]),
    "townConfig.sensitivityPeopleHappiness": (3, ["Off", "Very Low", "Low", "Normal", "High", "Very High", "Extreme"]),
    "townConfig.sensitivityCargoDelivery": (3, ["Off", "Very Low", "Low", "Normal", "High", "Very High", "Extreme"]),
    "townConfig.sensitivityNoise": (3, ["Off", "Very Low", "Low", "Normal", "High", "Very High", "Extreme"]),
    "townConfig.sensitivityPollution": (3, ["Off", "Very Low", "Low", "Normal", "High", "Very High", "Extreme"]),
    "weatherConfig.dynamicWeather": (0, ["Dynamic", "Sunny", "Cloudy", "Rainy"]),
    "gameTimeConfig.timeOfDayMode": (0, ["Dynamic", "Continuous", "Local Time", "Morning", "Day", "Evening", "Night"]),
    "guideSystemConfig.tutorial": (1, ["Off", "On"]),
}


def setting_label(key, value):
    """A stored setting as "3 (100%, default)": the stored number, then its label in the game's
    list. Values of unknown keys, or out of the list, are returned as they are (whole floats as int).
    """
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if key not in SETTING_OPTIONS or not isinstance(value, int) or isinstance(value, bool):
        return value
    default, labels = SETTING_OPTIONS[key]
    if not 1 <= value <= len(labels):
        return value
    return f"{value} ({labels[value - 1]}{', default' if value - 1 == default else ''})"
