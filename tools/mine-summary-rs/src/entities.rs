//! The entity table and what the summary takes from it, ported from `tools/town_places.py` and the parcel table
//! reader of `tools/parcels.py`: entity counts, the names table's type and free list, the line count, the live
//! towns with a point each, and the town array's header (`docs/entity-table.md`, `docs/town-places.md`,
//! `docs/line-ids.md`, `docs/town-records.md`). Every step keeps the Python's order, so ties and the first match
//! come out the same.

use std::collections::{BTreeSet, HashMap, HashSet};

use crate::stream::{entity_names_at, find_all};

const SLOT: u32 = 0x3fff_ffff;
const FREE: u32 = 0xffff_ffff;
const MAX_PAIRS: u32 = 300;
const MAX_TYPE: u32 = 4096;

fn u32_at(data: &[u8], at: usize) -> Option<u32> {
    data.get(at..at.checked_add(4)?)
        .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
}

fn f32_at(data: &[u8], at: usize) -> Option<f32> {
    u32_at(data, at).map(f32::from_bits)
}

/// One entity: its (type, slot) pairs in stored order, or `None` for a free entity.
pub type Entity = Option<Vec<(u32, u32)>>;

fn get(e: &[(u32, u32)], t: u32) -> Option<u32> {
    e.iter().find(|p| p.0 == t).map(|p| p.1)
}

fn has(e: &[(u32, u32)], t: u32) -> bool {
    e.iter().any(|p| p.0 == t)
}

/// End offset of the entity at q, or `None` when it does not parse as one (`_entity_end`).
fn entity_end(data: &[u8], q: usize) -> Option<usize> {
    if q + 4 > data.len() {
        return None;
    }
    let k = u32_at(data, q)?;
    if k == 0 || k > MAX_PAIRS || q + 4 + 8 * k as usize > data.len() {
        return None;
    }
    let mut seen: Vec<u32> = Vec::with_capacity(k as usize);
    for i in 0..k as usize {
        let t = u32_at(data, q + 4 + 8 * i)?;
        if (t >= MAX_TYPE && t != FREE) || seen.contains(&t) {
            return None;
        }
        seen.push(t);
    }
    Some(q + 4 + 8 * k as usize)
}

fn parses_to(data: &[u8], mut q: usize, n: u32, end: usize) -> bool {
    for _ in 0..n {
        match entity_end(data, q) {
            Some(e) if e <= end => q = e,
            _ => return false,
        }
    }
    q == end
}

/// The trailer after the table's closing count: u32 1, 1, x, 1, 1, y, 1 (x and y any value).
fn is_trailer(data: &[u8], p: usize) -> bool {
    let words = [Some(1), Some(1), None, Some(1), Some(1), None, Some(1)];
    words.iter().enumerate().all(|(i, w)| match w {
        Some(v) => u32_at(data, p + 4 + 4 * i) == Some(*v),
        None => p + 8 + 4 * i <= data.len(),
    })
}

/// Start of the last occurrence of `pat` that lies wholly inside data[lo..end] (Python's `rfind(pat, lo, end)`).
fn rfind(data: &[u8], pat: &[u8], lo: usize, end: usize) -> Option<usize> {
    if end < lo + pat.len() {
        return None;
    }
    memchr::memmem::rfind(&data[lo..end], pat).map(|i| lo + i)
}

/// (offset of the first entity, count) of the entity table, or `None` (`find_entity_table`): the trailers in
/// the last 12 % of the stream (non-overlapping, as the Python's regex takes them), from the last backwards, and
/// for each an earlier copy of its count from which that many entities end exactly at it.
pub fn find_entity_table(data: &[u8]) -> Option<(usize, u32)> {
    let lo = (data.len() as f64 * (1.0 - 0.12)) as usize;
    let mut hits = Vec::new();
    let mut next = lo;
    let one_one = [1u8, 0, 0, 0, 1, 0, 0, 0];
    for q in find_all(data.get(lo + 4..)?, &one_one) {
        let p = lo + q;
        if p < next {
            continue;
        }
        if p + 32 <= data.len() && is_trailer(data, p) {
            hits.push(p);
            next = p + 32;
        }
    }
    for &end in hits.iter().rev() {
        let n = u32_at(data, end)?;
        if !(1000..=20_000_000).contains(&n) {
            continue;
        }
        let pat = n.to_le_bytes();
        let lo2 = end.saturating_sub((4 + 8 * MAX_PAIRS as usize) * n as usize);
        let mut p = rfind(data, &pat, lo2, end);
        while let Some(at) = p {
            if parses_to(data, at + 4, n, end) {
                return Some((at + 4, n));
            }
            p = rfind(data, &pat, lo2, at);
        }
    }
    None
}

/// The n entities from `start` (`read_entities`).
pub fn read_entities(data: &[u8], start: usize, n: u32) -> Vec<Entity> {
    let mut out = Vec::with_capacity(n as usize);
    let mut q = start;
    for _ in 0..n {
        let k = u32_at(data, q).unwrap_or(0) as usize;
        let pairs: Vec<(u32, u32)> = (0..k)
            .map(|i| {
                (
                    u32_at(data, q + 4 + 8 * i).unwrap_or(0),
                    u32_at(data, q + 8 + 8 * i).unwrap_or(0),
                )
            })
            .collect();
        q += 4 + 8 * k;
        out.push(if has(&pairs, FREE) { None } else { Some(pairs) });
    }
    out
}

/// How many entities carry each type.
fn carried(ents: &[Entity]) -> HashMap<u32, usize> {
    let mut c = HashMap::new();
    for e in ents.iter().flatten() {
        for (t, _) in e {
            *c.entry(*t).or_insert(0) += 1;
        }
    }
    c
}

/// The names table: (names, type id, free slots), or `None` (`names_table` with `ents`).
pub struct Names {
    pub names: Vec<String>,
    pub kind: u32,
    pub free: HashSet<u32>,
}

pub fn names_table(data: &[u8], ents: &[Entity]) -> Option<Names> {
    let (start, names) = entity_names_at(data)?;
    let nat = start.checked_sub(4)?;
    let n = u32_at(data, nat)?;
    if n as usize > names.len() {
        return None;
    }
    let mut found: Vec<(u32, HashSet<u32>)> = Vec::new();
    for f in 0..=n as usize {
        let Some(q) = nat.checked_sub(4 + 4 * f) else {
            break;
        };
        if q < 4 {
            break;
        }
        if u32_at(data, q) == Some(f as u32) {
            let v: Vec<u32> = (0..f).filter_map(|i| u32_at(data, q + 4 + 4 * i)).collect();
            let set: HashSet<u32> = v.iter().copied().collect();
            if v.len() == f && v.iter().all(|&x| x < n) && set.len() == f {
                found.push((u32_at(data, q - 4)?, set));
            }
        }
    }
    if found.is_empty() {
        return None;
    }
    let c = carried(ents);
    let fits: Vec<usize> = (0..found.len())
        .filter(|&i| c.get(&found[i].0).copied().unwrap_or(0) == n as usize - found[i].1.len())
        .collect();
    let best = fits.last().copied().unwrap_or(found.len() - 1);
    let (kind, free) = found.swap_remove(best);
    let mut names = names;
    names.truncate(n as usize);
    Some(Names { names, kind, free })
}

/// Every building record found by pattern, as (town entity id, parcel entity ids) (`building_records`). The
/// pattern is 21 bytes and matches do not overlap, as the Python's regex takes them.
pub fn building_records(data: &[u8]) -> Vec<(u32, Vec<u32>)> {
    let mut out = Vec::new();
    let len = data.len();
    let mut p = 0usize;
    while p + 21 <= len {
        let d = &data[p..p + 21];
        let hit = (1..=4).contains(&d[8])
            && d[9] == 0
            && d[10] == 0
            && d[11] == 0
            && d[16] <= 1
            && (1..=4).contains(&d[17])
            && d[18] == 0
            && d[19] == 0
            && d[20] == 0;
        if !hit {
            p += 1;
            continue;
        }
        let a = u32::from_le_bytes(d[0..4].try_into().unwrap());
        let b = u32::from_le_bytes(d[4..8].try_into().unwrap());
        let n = d[17] as usize;
        let start = p;
        p += 21;
        if (b != a && b != FREE) || a == 0 {
            continue;
        }
        let q = start + 21 + 4 * n;
        if q + 20 > len {
            continue;
        }
        let parcels: Vec<u32> = (0..n)
            .map(|i| u32_at(data, start + 21 + 4 * i).unwrap())
            .collect();
        let depth = u32_at(data, q).unwrap();
        let height = f64::from(f32_at(data, q + 4).unwrap());
        let town = u32_at(data, q + 8).unwrap();
        if (1..=4).contains(&depth)
            && height > 2.0
            && height < 120.0
            && town != 0
            && parcels.iter().all(|&x| x != 0)
        {
            out.push((town, parcels));
        }
    }
    out
}

/// The centre of each parcel's first face, `None` for a parcel with no face (`parcels.read_parcels`).
fn parcel_centres(data: &[u8]) -> Vec<Option<(f64, f64)>> {
    let mark = [4u8, 0, 0, 0, 4, 0, 0, 0];
    for pos in find_all(data, &mark) {
        if pos >= 13
            && let Some(c) = parcel_chain(data, pos - 13)
        {
            return c;
        }
    }
    Vec::new()
}

fn parcel_chain(data: &[u8], s: usize) -> Option<Vec<Option<(f64, f64)>>> {
    let n = u32_at(data, s)?;
    if !(1..=2_000_000).contains(&n) {
        return None;
    }
    let mut p = s + 4;
    let mut out = Vec::with_capacity(n as usize);
    for _ in 0..n {
        if p + 13 > data.len() {
            return None;
        }
        let edge = u32_at(data, p)?;
        let left = data[p + 4];
        let curve = f64::from(f32_at(data, p + 5)?);
        let nf = u32_at(data, p + 9)?;
        if edge >= 1 << 24 || left > 1 || !(0.0..=1.0001).contains(&curve) || nf > 8 {
            return None;
        }
        p += 13;
        let mut first = None;
        for i in 0..nf {
            if p + 56 > data.len() {
                return None;
            }
            if u32_at(data, p)? != 4 {
                return None;
            }
            let mut v = [0f64; 12];
            for (k, x) in v.iter_mut().enumerate() {
                *x = f64::from(f32_at(data, p + 4 + 4 * k)?);
                if !x.is_finite() || x.abs() >= 40000.0 {
                    return None;
                }
            }
            if u32_at(data, p + 52)? >= 8 {
                return None;
            }
            if i == 0 {
                let x = (((v[0] + v[3]) + v[6]) + v[9]) / 4.0;
                let y = (((v[1] + v[4]) + v[7]) + v[10]) / 4.0;
                first = Some((x, y));
            }
            p += 56;
        }
        if p + 4 > data.len() {
            return None;
        }
        p += 4;
        out.push(first);
    }
    Some(out)
}

pub struct Town {
    pub id: usize,
    pub name: Option<String>,
    pub record: u32,
    pub buildings: usize,
    pub mean: Option<(f64, f64)>,
}

/// The live towns and the town type id (`_towns`).
fn towns(data: &[u8], ents: &[Entity], nt: &Names) -> (Vec<Town>, Option<u32>) {
    let blds = building_records(data);
    let named = |t: u32| -> Option<&Vec<(u32, u32)>> {
        ents.get(t as usize)
            .and_then(|e| e.as_ref())
            .filter(|e| has(e, nt.kind))
    };
    let owners: BTreeSet<u32> = blds
        .iter()
        .map(|b| b.0)
        .filter(|&t| named(t).is_some())
        .collect();
    if owners.is_empty() {
        return (Vec::new(), None);
    }
    let mut shared: Option<BTreeSet<u32>> = None;
    for &t in &owners {
        let types: BTreeSet<u32> = named(t).unwrap().iter().map(|p| p.0).collect();
        shared = Some(match shared {
            None => types,
            Some(s) => s.intersection(&types).copied().collect(),
        });
    }
    let mut shared = shared.unwrap_or_default();
    shared.remove(&nt.kind);
    if shared.is_empty() {
        return (Vec::new(), None);
    }
    let c = carried(ents);
    // The lowest id on a tie, as the Python's min over the sorted set.
    let town_type = *shared
        .iter()
        .min_by_key(|t| c.get(t).copied().unwrap_or(0))
        .unwrap();
    // The parcel type: the commonest single type among the first 500 buildings' parcels, the first seen on a tie.
    let mut kinds: Vec<(u32, usize)> = Vec::new();
    for (_, ps) in blds.iter().take(500) {
        for &p in ps {
            if let Some(Some(e)) = ents.get(p as usize)
                && e.len() == 1
            {
                let k = e[0].0;
                match kinds.iter_mut().find(|x| x.0 == k) {
                    Some(x) => x.1 += 1,
                    None => kinds.push((k, 1)),
                }
            }
        }
    }
    let mut parcel_type = None;
    let mut best = 0;
    for &(k, n) in &kinds {
        if parcel_type.is_none() || n > best {
            parcel_type = Some(k);
            best = n;
        }
    }
    let centres = parcel_centres(data);
    let mut by_town: HashMap<u32, Vec<usize>> = HashMap::new();
    for (i, b) in blds.iter().enumerate() {
        by_town.entry(b.0).or_default().push(i);
    }
    let mut out = Vec::new();
    for (tid, e) in ents.iter().enumerate() {
        let Some(e) = e else { continue };
        let Some(record) = get(e, town_type) else {
            continue;
        };
        let slot = get(e, nt.kind);
        let name = slot
            .filter(|&s| (s as usize) < nt.names.len() && !nt.free.contains(&s))
            .map(|s| nt.names[s as usize].clone());
        let mut pts: Vec<(f64, f64)> = Vec::new();
        let mut nb = 0;
        if let Some(list) = u32::try_from(tid).ok().and_then(|t| by_town.get(&t)) {
            for &i in list {
                nb += 1;
                for &p in &blds[i].1 {
                    let Some(Some(pe)) = ents.get(p as usize) else {
                        continue;
                    };
                    let Some(pt) = parcel_type else { continue };
                    let Some(s) = get(pe, pt) else { continue };
                    if let Some(Some(c)) = centres.get((s & SLOT) as usize) {
                        pts.push(*c);
                    }
                }
            }
        }
        let mean = if pts.is_empty() {
            None
        } else {
            let (mut sx, mut sy) = (0.0f64, 0.0f64);
            for p in &pts {
                sx += p.0;
                sy += p.1;
            }
            Some((sx / pts.len() as f64, sy / pts.len() as f64))
        };
        out.push(Town {
            id: tid,
            name,
            record,
            buildings: nb,
            mean,
        });
    }
    (out, Some(town_type))
}

/// The line count: entities with exactly six types, among them 10, N, N + 1 and N + 2 (`line_count`).
fn line_count(ents: &[Entity], n: u32) -> usize {
    ents.iter()
        .flatten()
        .filter(|e| e.len() == 6 && [10, n, n + 1, n + 2].iter().all(|&t| has(e, t)))
        .count()
}

pub struct TownHeader {
    pub first_word: u32,
    pub kind: u32,
    pub free: Vec<u32>,
    pub rows: u32,
}

/// The town array's header (`town_table_header`): the town type, a free list that is exactly the rows no live
/// town uses, and a row count of live towns plus free rows; the last match before `before`, else the first.
fn town_table_header(
    data: &[u8],
    kind: u32,
    live: &[u32],
    before: Option<usize>,
) -> Option<TownHeader> {
    let live: HashSet<u32> = live.iter().copied().collect();
    let pat = kind.to_le_bytes();
    let mut hits: Vec<(usize, Vec<u32>, u32)> = Vec::new();
    for q in find_all(data.get(4..)?, &pat) {
        let p = q + 4;
        let Some(f) = u32_at(data, p + 4).filter(|_| p + 8 <= data.len()) else {
            continue;
        };
        if f > 4096 || p + 12 + 4 * f as usize > data.len() {
            continue;
        }
        let n = u32_at(data, p + 8 + 4 * f as usize).unwrap();
        if n as usize != live.len() + f as usize {
            continue;
        }
        let slots: Vec<u32> = (0..f as usize)
            .map(|i| u32_at(data, p + 8 + 4 * i).unwrap())
            .collect();
        let set: HashSet<u32> = slots.iter().copied().collect();
        if set.len() == f as usize
            && set.iter().all(|s| *s < n && !live.contains(s))
            && (0..n).filter(|r| !live.contains(r)).count() == set.len()
        {
            hits.push((p, slots, n));
        }
    }
    let pick = before
        .and_then(|b| hits.iter().rposition(|h| h.0 < b))
        .unwrap_or(0);
    let (p, mut slots, n) = hits.into_iter().nth(pick)?;
    slots.sort_unstable();
    Some(TownHeader {
        first_word: u32_at(data, p - 4)?,
        kind,
        free: slots,
        rows: n,
    })
}

pub struct EntitySummary {
    pub count: usize,
    pub free: usize,
    pub name_type: Option<u32>,
    pub lines: Option<usize>,
    pub towns: Vec<Town>,
    pub town_type: Option<u32>,
    pub town_header: Option<TownHeader>,
}

/// What the summary takes from the entity table, or `None` when no table is found (`entity_summary`).
pub fn entity_summary(data: &[u8], first_record: Option<usize>) -> Option<EntitySummary> {
    let (start, n) = find_entity_table(data)?;
    let ents = read_entities(data, start, n);
    let mut out = EntitySummary {
        count: ents.len(),
        free: ents.iter().filter(|e| e.is_none()).count(),
        name_type: None,
        lines: None,
        towns: Vec::new(),
        town_type: None,
        town_header: None,
    };
    let Some(nt) = names_table(data, &ents) else {
        return Some(out);
    };
    out.name_type = Some(nt.kind);
    out.lines = Some(line_count(&ents, nt.kind));
    let (towns, town_type) = towns(data, &ents, &nt);
    if let Some(tt) = town_type
        && !towns.is_empty()
    {
        let live: Vec<u32> = towns.iter().map(|t| t.record & SLOT).collect();
        out.town_header = town_table_header(data, tt, &live, first_record);
    }
    out.towns = towns;
    out.town_type = town_type;
    Some(out)
}
