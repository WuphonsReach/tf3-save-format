//! The industry and vehicle counts made from the model instances (`industry_counts.py`, `vehicle_counts.py`,
//! `docs/vehicle-classes.md`).

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Path, PathBuf};

use crate::json::{Obj, Value};
use crate::reader::instances::{Instances, ModelTable};
use crate::reader::zip::Archive;

/// {model path: industry key}: the main model of each industry folder, `industries/<key>/<key>_sm.mdl`, else
/// the first `_particles.mdl` of the folder; where that model has no instance in `placed` but the key's own
/// `<key>.mdl` has, that one too (`industry_compass.main_models`).
fn main_models<'t>(table: &'t ModelTable, placed: &BTreeSet<&str>) -> HashMap<&'t str, String> {
    let paths: BTreeSet<&str> = table.paths.values().map(String::as_str).collect();
    let keys: BTreeSet<&str> = paths
        .iter()
        .filter(|p| p.starts_with("industries/") && p.matches('/').count() >= 2)
        .map(|p| p.split('/').nth(1).unwrap())
        .collect();
    let mut out = HashMap::new();
    for key in keys {
        let sm = format!("industries/{key}/{key}_sm.mdl");
        let folder = format!("industries/{key}/");
        let main = paths.get(sm.as_str()).copied().or_else(|| {
            paths
                .iter()
                .find(|p| p.starts_with(&folder) && p.ends_with("_particles.mdl"))
                .copied()
        });
        let Some(main) = main else {
            continue;
        };
        let own = format!("industries/{key}/{key}.mdl");
        if !placed.contains(main) {
            if let Some(p) = paths.get(own.as_str()).filter(|p| placed.contains(**p)) {
                out.insert(*p, key.to_owned());
            }
        }
        out.insert(main, key.to_owned());
    }
    out
}

/// An industry construction record (`industry_compass.read_industry_constructions`,
/// `docs/industry-records.md#the-construction-record`): the industry folder, the transform's x and y, and the entity
/// ids of the seven `vec<u32>` after the transform and an i64.
struct Construction {
    key: String,
    x: f32,
    y: f32,
    ids: Vec<u32>,
}

/// A longer id list is not this record's.
const IDS_MAX: usize = 100_000;
const CON_START: &[u8] = b"industries/";

/// The path `industries/<chars>.con` starting at `at` (`industry_compass._CON_PATH`: the shortest run of
/// `[A-Za-z0-9_./-]`, at least one, followed by `.con`), as its end offset.
fn con_path_end(data: &[u8], at: usize) -> Option<usize> {
    let ok = |b: u8| b.is_ascii_alphanumeric() || b"_./-".contains(&b);
    let mut p = at + CON_START.len();
    while p < data.len() && ok(data[p]) {
        p += 1;
        if data.get(p..p + 4) == Some(b".con") {
            return Some(p + 4);
        }
    }
    None
}

fn read_construction(data: &[u8], start: usize, end: usize) -> Option<Construction> {
    let u32_at = |p: usize| {
        data.get(p..p + 4)
            .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
    };
    if start < 4 || u32_at(start - 4)? as usize != end - start {
        return None;
    }
    let (_, q) = crate::lua::pairs(data, end, 0).ok()?;
    let f = |i: usize| {
        data.get(q + 4 * i..q + 4 * i + 4)
            .map(|b| f32::from_le_bytes(b.try_into().unwrap()))
    };
    if f(3)? != 0.0 || f(7)? != 0.0 || f(11)? != 0.0 || f(15)? != 1.0 {
        return None;
    }
    let (x, y) = (f(12)?, f(13)?);
    let mut p = q + 64 + 8; // the transform, then an i64 (0 in editor maps)
    let mut ids = Vec::new();
    for _ in 0..7 {
        let n = u32_at(p)? as usize;
        if n > IDS_MAX {
            return None;
        }
        let list = data.get(p + 4..p + 4 + 4 * n)?;
        ids.extend(
            list.as_chunks::<4>()
                .0
                .iter()
                .map(|b| u32::from_le_bytes(*b)),
        );
        p += 4 + 4 * n;
    }
    let path = std::str::from_utf8(&data[start..end]).ok()?;
    Some(Construction {
        key: path.split('/').nth(1)?.to_owned(),
        x,
        y,
        ids,
    })
}

/// The construction records of industries deleted in the map editor: every id the record lists is in the
/// free-id list (`industry_compass.dead_industries`). Empty when the save has no readable list.
fn dead_industries(data: &[u8]) -> Vec<Construction> {
    let Some(free) = crate::free_ids::read_free_ids(data).filter(|f| !f.is_empty()) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    let mut next_free = 0;
    for at in memchr::memmem::find_iter(data, CON_START) {
        if at < next_free {
            continue;
        }
        let Some(end) = con_path_end(data, at) else {
            continue;
        };
        next_free = end;
        if let Some(c) = read_construction(data, at, end)
            && !c.ids.is_empty()
            && c.ids.iter().all(|i| free.contains(i))
        {
            out.push(c);
        }
    }
    out
}

/// `count`, and `by_key` (industry key to count, keys sorted). One main instance of the same key within 1 m of
/// each deleted industry's record is left out (`industry_compass.live_main_instances`).
pub fn count_industries(data: &[u8], table: &ModelTable, inst: &Instances) -> Value {
    let all = inst.placed(data, table, "industries/");
    let placed: BTreeSet<&str> = all.iter().map(|(m, _, _)| *m).collect();
    let mains = main_models(table, &placed);
    let mut live: Vec<(&str, f32, f32)> = all
        .into_iter()
        .filter_map(|(m, x, y)| Some((mains.get(m)?.as_str(), x, y)))
        .collect();
    for r in dead_industries(data) {
        let dist = |&(_, x, y): &(&str, f32, f32)| {
            (f64::from(x) - f64::from(r.x)).hypot(f64::from(y) - f64::from(r.y))
        };
        let mut nearest: Option<(usize, f64)> = None;
        for (i, item) in live.iter().enumerate() {
            let d = dist(item);
            if item.0 == r.key && d <= 1.0 && nearest.is_none_or(|(_, b)| d < b) {
                nearest = Some((i, d));
            }
        }
        if let Some((i, _)) = nearest {
            live.remove(i);
        }
    }
    let mut by_key: BTreeMap<&str, u64> = BTreeMap::new();
    for (k, _, _) in live {
        *by_key.entry(k).or_default() += 1;
    }
    let mut out = Obj::new();
    out.set("count", by_key.values().sum::<u64>());
    out.set(
        "by_key",
        Value::Obj(
            by_key
                .into_iter()
                .map(|(k, n)| (k.to_owned(), n.into()))
                .collect(),
        ),
    );
    out.into()
}

// ---------------------------------------------------------------- vehicles

const GAME_DIRS: [&str; 4] = [
    ".steam/steam",
    ".local/share/Steam",
    "snap/steam/common/.local/share/Steam",
    ".var/app/com.valvesoftware.Steam/.local/share/Steam",
];

/// The install's `base/content/vehicle` folder: under `game_dir` (the install folder) if given, else under the
/// usual Steam places in the home folder (`vehicle_counts.find_vehicle_dir`).
pub fn find_vehicle_dir(game_dir: Option<&Path>) -> Option<PathBuf> {
    let roots: Vec<PathBuf> = match game_dir {
        Some(d) => vec![d.to_path_buf()],
        None => {
            let home = std::env::var_os("HOME").map(PathBuf::from)?;
            GAME_DIRS
                .iter()
                .map(|d| home.join(d).join("steamapps/common/Transport Fever 3"))
                .collect()
        }
    };
    roots
        .into_iter()
        .map(|r| r.join("base/content/vehicle"))
        .find(|p| p.is_dir())
}

/// What a base-game model file says: its carrier, whether it has an engine (`None` without a land vehicle
/// block) and its load class.
struct ModelInfo {
    carrier: String,
    powered: Option<bool>,
    load: &'static str,
}

fn is_word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// The text between the braces of `key = {` (with a word boundary before the key) in `text`, or `None`.
/// An unclosed block runs to the end of the text, less its last character, as in the Python.
fn block<'a>(text: &'a str, key: &str) -> Option<&'a str> {
    let pat = format!("{key} = {{");
    let mut from = 0;
    let start = loop {
        let i = from + text[from..].find(&pat)?;
        if !text[..i].chars().next_back().is_some_and(is_word) {
            break i + pat.len();
        }
        from = i + 1;
    };
    let mut depth = 1;
    for (i, c) in text[start..].char_indices() {
        match c {
            '{' => depth += 1,
            '}' => depth -= 1,
            _ => {}
        }
        if depth == 0 {
            return Some(&text[start..start + i]);
        }
    }
    let rest = &text[start..];
    Some(
        rest.char_indices()
            .next_back()
            .map_or(rest, |(i, _)| &rest[..i]),
    )
}

/// The word in `carrier = "WORD"`, first occurrence that has one.
fn carrier_of(tv: &str) -> Option<&str> {
    let pat = "carrier = \"";
    let mut from = 0;
    while let Some(i) = tv[from..].find(pat) {
        let s = from + i + pat.len();
        let end = tv[s..]
            .char_indices()
            .find(|&(_, c)| !is_word(c))
            .map_or(tv.len(), |(j, _)| s + j);
        if end > s && tv[end..].starts_with('"') {
            return Some(&tv[s..end]);
        }
        from = from + i + 1;
    }
    None
}

/// The quoted words of each `cargoClassesIncluded = { ... }` group in `tv`.
fn cargo_classes(tv: &str) -> BTreeSet<String> {
    let pat = "cargoClassesIncluded = {";
    let mut out = BTreeSet::new();
    let mut from = 0;
    while let Some(i) = tv[from..].find(pat) {
        let s = from + i + pat.len();
        let Some(close) = tv[s..].find('}') else {
            break;
        };
        let group = &tv[s..s + close];
        let mut j = 0;
        while let Some(q) = group[j..].find('"') {
            let ws = j + q + 1;
            let we = group[ws..]
                .char_indices()
                .find(|&(_, c)| !is_word(c))
                .map_or(group.len(), |(k, _)| ws + k);
            if we > ws && group[we..].starts_with('"') {
                out.insert(group[ws..we].to_owned());
                j = we + 1;
            } else {
                j = ws;
            }
        }
        from = s + close + 1;
    }
    out
}

fn model_info(
    vdir: Option<&Path>,
    path: &str,
    archives: &mut HashMap<PathBuf, Option<Archive>>,
) -> Option<ModelInfo> {
    let parts: Vec<&str> = path.split('/').collect();
    let vdir = vdir?;
    if parts.len() < 4 || parts[0] != "vehicle" {
        return None;
    }
    let zpath = vdir.join(parts[1]).join(format!("{}.zip", parts[2]));
    if !zpath.is_file() {
        return None;
    }
    let zip = archives
        .entry(zpath.clone())
        .or_insert_with(|| Archive::open(&zpath).ok())
        .as_mut()?;
    let text = zip.read_text(&parts[2..].join("/"))?;
    let meta = match text.find("metadata = {") {
        Some(i) => &text[i..],
        // Python's text[-1:]: the last character.
        None => text
            .char_indices()
            .next_back()
            .map_or("", |(i, _)| &text[i..]),
    };
    let tv = block(meta, "transportVehicle")?;
    let carrier = carrier_of(tv)?;
    let powered = block(meta, "landVehicle")
        .map(|land| block(land, "engines").is_some_and(|e| !e.trim().is_empty()));
    let classes = cargo_classes(tv);
    let passengers = classes.contains("PASSENGERS");
    let cargo = classes.iter().any(|c| c != "PASSENGERS");
    let carrier = match carrier {
        "ROAD" => "road".to_owned(),
        "TRAM" => "tram".to_owned(),
        "RAIL" => "rail".to_owned(),
        "WATER" => "water".to_owned(),
        "AIR" => "air".to_owned(),
        c => c.to_lowercase(),
    };
    let load = match (passengers, cargo) {
        (true, true) => "mixed",
        (true, false) => "passenger",
        (false, true) => "cargo",
        (false, false) => "none",
    };
    Some(ModelInfo {
        carrier,
        powered,
        load,
    })
}

fn folder_carrier(folder: &str) -> Option<&'static str> {
    Some(match folder {
        "bus" | "truck" => "road",
        "tram" => "tram",
        "train" | "waggon" => "rail",
        "ship" => "water",
        "plane" | "helicopter" => "air",
        _ => return None,
    })
}

fn bump(o: &mut Obj, key: &str, n: u64) {
    match o.get_mut(key) {
        Some(Value::Int(v)) => *v += i128::from(n),
        _ => o.set(key, n),
    }
}

/// The vehicle units by carrier, power and load (`vehicle_counts.count_vehicles`). `Err` is a Python error the
/// summary does not catch (a helicopter whose model gives another carrier than air, before any air vehicle).
pub fn count_vehicles(
    data: &[u8],
    table: &ModelTable,
    inst: &Instances,
    game_dir: Option<&Path>,
) -> Result<Value, String> {
    let vdir = find_vehicle_dir(game_dir);
    let mut per_model: Vec<(&str, u64)> = Vec::new();
    let mut at: HashMap<&str, usize> = HashMap::new();
    for m in inst.models(data, table, "vehicle/") {
        match at.get(m) {
            Some(&i) => per_model[i].1 += 1,
            None => {
                at.insert(m, per_model.len());
                per_model.push((m, 1));
            }
        }
    }
    let mut from_install = false;
    // carrier -> (power or "helicopters") -> load -> count, in first-seen order
    let mut carriers: Vec<(String, Obj)> = Vec::new();
    let mut ambient = Obj::new();
    let mut unread = 0u64;
    let mut archives = HashMap::new();
    for (path, n) in per_model {
        let folder = path.split('/').nth(1).unwrap_or("");
        let info = match model_info(vdir.as_deref(), path, &mut archives) {
            Some(info) => {
                from_install = true;
                info
            }
            None => match folder_carrier(folder) {
                Some(c) => {
                    unread += 1;
                    ModelInfo {
                        carrier: c.to_owned(),
                        powered: if folder == "waggon" {
                            Some(false)
                        } else {
                            None
                        },
                        load: "unknown",
                    }
                }
                None => {
                    bump(
                        &mut ambient,
                        if folder == "car" { "car" } else { "other" },
                        n,
                    );
                    continue;
                }
            },
        };
        let power = match info.powered {
            None if info.carrier == "water" || info.carrier == "air" => "powered",
            None => "unknown",
            Some(true) => "powered",
            Some(false) => "unpowered",
        };
        let ci = match carriers.iter().position(|(c, _)| *c == info.carrier) {
            Some(i) => i,
            None => {
                carriers.push((info.carrier.clone(), Obj::new()));
                carriers.len() - 1
            }
        };
        let node = &mut carriers[ci].1;
        if node.get_mut(power).is_none() {
            node.set(power, Obj::new());
        }
        if let Some(Value::Obj(loads)) = node.get_mut(power) {
            let mut o = Obj(std::mem::take(loads));
            bump(&mut o, info.load, n);
            *loads = o.0;
        }
        if folder == "helicopter" {
            let Some(ai) = carriers.iter().position(|(c, _)| c == "air") else {
                return Err("KeyError: 'air'".into());
            };
            bump(&mut carriers[ai].1, "helicopters", n);
        }
    }
    let mut out = Obj::new();
    out.set("from_install", from_install);
    for (c, o) in carriers {
        out.set(c, o);
    }
    out.set("ambient", ambient);
    out.set("models_unread", unread);
    Ok(out.into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn model_file_blocks_read_as_in_the_python() {
        let text = "metadata = { transportVehicle = { carrier = \"RAIL\", compartments = { { cargoClassesIncluded = { \"PASSENGERS\" } }, { cargoClassesIncluded = { \"COAL\", \"GRAIN\" } } } }, landVehicle = { engines = { { power = 1 } } } }";
        let tv = block(text, "transportVehicle").unwrap();
        assert_eq!(carrier_of(tv), Some("RAIL"));
        assert_eq!(cargo_classes(tv).len(), 3);
        let land = block(text, "landVehicle").unwrap();
        assert!(block(land, "engines").is_some_and(|e| !e.trim().is_empty()));
        assert_eq!(block("xtransportVehicle = { a }", "transportVehicle"), None);
        assert_eq!(block("k = { a { b }", "k"), Some(" a { b "));
    }
}
