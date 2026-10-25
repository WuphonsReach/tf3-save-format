//! Pattern reads over the whole stream, ported from `tf3save.py`: the cargo list (`docs/cargo-ids.md`), the
//! 78-byte town records (`docs/town-records.md`), the entity names table and the town names in it
//! (`docs/entity-names.md`), and the game speed component with its day table (`docs/calendar.md`).

use memchr::memmem;

fn u32_at(data: &[u8], at: usize) -> Option<u32> {
    data.get(at..at.checked_add(4)?)
        .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
}

fn u64_at(data: &[u8], at: usize) -> Option<u64> {
    data.get(at..at.checked_add(8)?)
        .map(|b| u64::from_le_bytes(b.try_into().unwrap()))
}

/// Every offset of `needle` in `data`, overlapping ones included (Python's `find(pat, pos + 1)` loop).
pub fn find_all<'a>(data: &'a [u8], needle: &'a [u8]) -> impl Iterator<Item = usize> + 'a {
    let finder = memmem::Finder::new(needle);
    let mut from = 0;
    std::iter::from_fn(move || {
        let i = from + finder.find(data.get(from..)?)?;
        from = i + 1;
        Some(i)
    })
}

// ---------------------------------------------------------------- cargo list

/// One cargo list entry: id, name (the file name without `.cargo`), and the mod that adds it (empty for base).
pub type CargoEntry = (u32, String, String);

/// The save's cargo list in list order, or `None`. The list is a u32 count, then per entry a `str` source mod,
/// a `str` path under `cargos/` and a u32 id that counts from 0. It is found from its first entry, passengers.
pub fn cargo_entries(data: &[u8]) -> Option<Vec<CargoEntry>> {
    let mut first = 34u32.to_le_bytes().to_vec();
    first.extend_from_slice(b"cargos/passengers/passengers.cargo");
    find_all(data, &first).find_map(|pos| read_cargo_list(data, pos))
}

/// The name in a cargo path: `cargos/(<word>/)*<word>.cargo`, words of ASCII letters, digits and `_`.
fn cargo_name(path: &[u8]) -> Option<String> {
    let rest = path.strip_prefix(b"cargos/")?.strip_suffix(b".cargo")?;
    let word =
        |w: &[u8]| !w.is_empty() && w.iter().all(|c| c.is_ascii_alphanumeric() || *c == b'_');
    let mut last = None;
    for part in rest.split(|c| *c == b'/') {
        if !word(part) {
            return None;
        }
        last = Some(part);
    }
    last.map(|w| String::from_utf8_lossy(w).into_owned())
}

fn read_cargo_list(data: &[u8], first: usize) -> Option<Vec<CargoEntry>> {
    if first < 8 {
        return None;
    }
    let count = u32_at(data, first - 8)?;
    if u32_at(data, first - 4)? != 0 || !(2..=1000).contains(&count) {
        return None;
    }
    let mut out = Vec::new();
    let mut p = first - 4;
    for i in 0..count {
        let n = u32_at(data, p)? as usize;
        if n > 200 {
            return None;
        }
        let source = data.get(p + 4..p + 4 + n)?;
        p += 4 + n;
        let n = u32_at(data, p)? as usize;
        let name = if n < 200 {
            // The Python matches a slice that may run short at the stream's end; a short one cannot end in
            // `.cargo` and also have its id after it, so reading it whole changes nothing.
            cargo_name(&data[(p + 4).min(data.len())..(p + 4 + n).min(data.len())])
        } else {
            None
        }?;
        let cid = u32_at(data, p + 4 + n)?;
        p += 4 + n + 4;
        if cid != i {
            return None;
        }
        out.push((cid, name, String::from_utf8_lossy(source).into_owned()));
    }
    Some(out)
}

// ---------------------------------------------------------------- town records

#[derive(Debug, Clone)]
pub struct TownRecord {
    pub offset: usize,
    pub caps: [u32; 3],
    pub floats: [f32; 4],
    pub com: u32,
    pub ind: u32,
}

/// The town records in the 78-byte layout with one commercial and one industrial cargo: caps (3 x u32),
/// 4 x f32, five zero bytes, a cargo count of 1 to 3 as a u32, ... A candidate is any place where the five
/// zeros, the count and its three zero bytes stand; candidates do not overlap (each takes 37 bytes, as the
/// Python's regex match does, whether or not the record then passes the checks). Kept are those with
/// capacities of 10 to 1,000,000, floats of 0.05 to 20, and one cargo each side.
///
/// `Err` is the Python's `struct.error` when a candidate's cargo fields run past the end of the stream.
pub fn scan_records(data: &[u8]) -> Result<Vec<TownRecord>, String> {
    let mut zs: Vec<usize> = Vec::new();
    for v in 1u8..=3 {
        let pat = [0, 0, 0, 0, 0, v, 0, 0, 0];
        let is_at = |z: usize| {
            data.get(z..z + 9)
                .is_some_and(|b| b[..5] == [0; 5] && (1..=3).contains(&b[5]) && b[6..] == [0; 3])
        };
        for z in memmem::find_iter(data, &pat) {
            zs.push(z);
            // memmem skips occurrences that overlap the one it found; the pattern can recur 6 to 8 bytes on.
            for k in 6..=8 {
                if is_at(z + k) {
                    zs.push(z + k);
                }
            }
        }
    }
    zs.sort_unstable();
    zs.dedup();
    let mut recs = Vec::new();
    let mut next_free = 0usize;
    for z in zs {
        let Some(s) = z.checked_sub(28) else { continue };
        if s < next_free {
            continue;
        }
        next_free = s + 37;
        let caps = [0, 1, 2].map(|i| u32_at(data, s + 4 * i).unwrap());
        if !caps.iter().all(|c| (10..=1_000_000).contains(c)) {
            continue;
        }
        let floats = [0, 1, 2, 3]
            .map(|i| f32::from_le_bytes(data[s + 12 + 4 * i..s + 16 + 4 * i].try_into().unwrap()));
        if !floats
            .iter()
            .all(|&x| x.is_finite() && (0.05..=20.0).contains(&f64::from(x)))
        {
            continue;
        }
        if s + 53 > data.len() {
            return Err("error: unpack requires a buffer of 20 bytes".into());
        }
        let com_n = u32_at(data, s + 33).unwrap();
        let com = u32_at(data, s + 37).unwrap();
        let ind_n = u32_at(data, s + 45).unwrap();
        let ind = u32_at(data, s + 49).unwrap();
        if com_n != 1 || ind_n != 1 {
            continue;
        }
        recs.push(TownRecord {
            offset: s,
            caps,
            floats,
            com,
            ind,
        });
    }
    Ok(recs)
}

// ---------------------------------------------------------------- entity names and towns

/// The `str` at p as (text, end), or `None` if it is not one: at most 400 bytes, UTF-8, no control character.
fn str_at(data: &[u8], p: usize) -> Option<(&str, usize)> {
    let n = u32_at(data, p)? as usize;
    if n > 400 || p + 4 + n > data.len() {
        return None;
    }
    let text = std::str::from_utf8(&data[p + 4..p + 4 + n]).ok()?;
    if text.chars().any(|c| (c as u32) < 32) {
        return None;
    }
    Some((text, p + 4 + n))
}

/// Start of the `str` that ends exactly at p.
fn str_before(data: &[u8], p: usize) -> Option<usize> {
    for n in 0..300usize {
        let q = p.checked_sub(4 + n)?;
        if u32_at(data, q) == Some(n as u32) && str_at(data, q).is_some_and(|r| r.1 == p) {
            return Some(q);
        }
    }
    None
}

/// The entity names table, company first, or `None`. Found from the first six `no name` entries: from each,
/// walk back `str` by `str` to the start of the run, keep the longest run (the first on a tie), then read
/// forward from its start for as long as strings read.
pub fn entity_names(data: &[u8]) -> Option<Vec<String>> {
    let mut no_name = 7u32.to_le_bytes().to_vec();
    no_name.extend_from_slice(b"no name");
    let mut best: Option<(usize, usize)> = None;
    for i in find_all(data, &no_name).take(6) {
        let (mut p, mut n) = (i, 0);
        while let Some(q) = str_before(data, p) {
            p = q;
            n += 1;
        }
        if best.is_none_or(|b| n > b.0) {
            best = Some((n, p));
        }
    }
    let (n, mut p) = best?;
    if n < 3 {
        return None;
    }
    let mut names = Vec::new();
    while let Some((text, end)) = str_at(data, p) {
        names.push(text.to_owned());
        p = end;
    }
    Some(names)
}

fn town_run(names: &[String], strict: bool) -> Vec<String> {
    let mut towns: Vec<String> = Vec::new();
    for n in names.iter().skip(1) {
        if n == "no name" || n.is_empty() {
            break;
        }
        let words: Vec<&str> = n.split(' ').collect();
        let built = towns.iter().any(|t| {
            n != t
                && (n.starts_with(&format!("{t} "))
                    || (strict && (words.contains(&t.as_str()) || n.starts_with(&format!("{t}-")))))
        });
        if built {
            break;
        }
        towns.push(n.clone());
    }
    towns
}

fn anchored(names: &[String], towns: &[String]) -> bool {
    let mut hit = vec![false; towns.len()];
    let mut hits = 0;
    let spaced: Vec<String> = towns.iter().map(|t| format!(" {t} ")).collect();
    let hyphen: Vec<String> = towns.iter().map(|t| format!("{t}-")).collect();
    for n in names.iter().skip(1 + towns.len()) {
        if hits == towns.len() {
            break;
        }
        let padded = format!(" {n} ");
        for (i, t) in towns.iter().enumerate() {
            if !hit[i] && n != t && (padded.contains(&spaced[i]) || n.starts_with(&hyphen[i])) {
                hit[i] = true;
                hits += 1;
            }
        }
    }
    hits > 0 && 10 * hits >= towns.len()
}

/// The town names from the entity names table, or `None` when they cannot be told (`tf3save.town_names`):
/// the run from slot 1 to the first `no name` or industry-like name, strict stop first, then lax; the run must
/// reach `min_towns` and at least a tenth of its towns must appear in a later name.
pub fn town_names(data: &[u8], min_towns: usize) -> Option<Vec<String>> {
    let names = entity_names(data)?;
    for strict in [true, false] {
        let towns = town_run(&names, strict);
        if !towns.is_empty() && towns.len() >= min_towns && anchored(&names, &towns) {
            return Some(towns);
        }
    }
    None
}

// ---------------------------------------------------------------- calendar

pub struct GameSpeed {
    pub millis_per_day: u32,
    pub play_speed: u32,
    pub t1: u64,
    /// Offset just after the component, where the day table starts.
    pub end: usize,
}

/// The game speed component: `09 00*7 | 01 00 00 00 | u32 millisPerDay | u32 playSpeed | 00*8 | 01 00 00 00 |
/// 08 00*7 | 01 00 00 00 | u64 t1 | 01 | u64 t2`, 61 bytes. `None` unless it is found exactly once (matches
/// do not overlap, as with the Python's regex).
pub fn find_game_speed(data: &[u8]) -> Option<GameSpeed> {
    const LEN: usize = 61;
    let head: [u8; 12] = [9, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0];
    let fits = |s: usize| {
        let Some(b) = data.get(s..s + LEN) else {
            return false;
        };
        b[20..28] == [0; 8]
            && b[28..32] == [1, 0, 0, 0]
            && b[32..40] == [8, 0, 0, 0, 0, 0, 0, 0]
            && b[40..44] == [1, 0, 0, 0]
            && b[52] == 1
    };
    let mut found = None;
    let mut count = 0;
    let mut next_free = 0;
    for s in memmem::find_iter(data, &head) {
        if s < next_free || !fits(s) {
            continue;
        }
        count += 1;
        next_free = s + LEN;
        if found.is_none() {
            found = Some(s);
        }
    }
    let s = found.filter(|_| count == 1)?;
    Some(GameSpeed {
        millis_per_day: u32_at(data, s + 12).unwrap(),
        play_speed: u32_at(data, s + 16).unwrap(),
        t1: u64_at(data, s + 44).unwrap(),
        end: s + LEN,
    })
}

/// The day table after the game speed component: u32 count, then (u64 tick, u32 Julian day) pairs. `Ok(None)`
/// when the count runs past the stream; `Err` (the Python's `struct.error`) when not even the count is there.
pub fn day_table(data: &[u8], g: &GameSpeed) -> Result<Option<Vec<(u64, u32)>>, String> {
    let p = g.end;
    let n =
        u32_at(data, p).ok_or("error: unpack_from requires a buffer of at least 4 bytes")? as usize;
    if p + 4 + 12 * n > data.len() {
        return Ok(None);
    }
    Ok(Some(
        (0..n)
            .map(|i| {
                (
                    u64_at(data, p + 4 + 12 * i).unwrap(),
                    u32_at(data, p + 12 + 12 * i).unwrap(),
                )
            })
            .collect(),
    ))
}

/// A Julian day number as `YYYY-MM-DD` (proleptic Gregorian, as Python's `date.fromordinal(day - 1721425)`),
/// or `None` outside years 1 to 9999.
pub fn iso_date(day: u32) -> Option<String> {
    let ordinal = i64::from(day) - 1_721_425;
    if !(1..=3_652_059).contains(&ordinal) {
        return None;
    }
    // Days since 0000-03-01, then the civil-from-days method.
    let z = ordinal + 305;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = yoe + era * 400 + i64::from(m <= 2);
    Some(format!("{y:04}-{m:02}-{d:02}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn julian_days_become_dates() {
        assert_eq!(iso_date(2_415_021).as_deref(), Some("1900-01-01"));
        assert_eq!(iso_date(1_721_426).as_deref(), Some("0001-01-01"));
        assert_eq!(iso_date(2_469_808).as_deref(), Some("2050-01-01"));
        assert_eq!(iso_date(2_451_604).as_deref(), Some("2000-02-29"));
        assert_eq!(iso_date(1_721_425), None);
        assert_eq!(
            iso_date(1_721_425 + 3_652_059).as_deref(),
            Some("9999-12-31")
        );
        assert_eq!(iso_date(1_721_425 + 3_652_060), None);
    }

    #[test]
    fn cargo_paths_give_their_name() {
        assert_eq!(
            cargo_name(b"cargos/fish/fish.cargo").as_deref(),
            Some("fish")
        );
        assert_eq!(cargo_name(b"cargos/sugar.cargo").as_deref(), Some("sugar"));
        assert_eq!(cargo_name(b"cargos//sugar.cargo"), None);
        assert_eq!(cargo_name(b"cargos/su-gar.cargo"), None);
    }
}
