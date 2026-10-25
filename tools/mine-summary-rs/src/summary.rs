//! The summary of one save, field for field as `summarise_save` in mine_summary.py writes it (schema v8,
//! `tools/schema/tf3-save-summary.v8.schema.json`). Every key is written, in the schema's order; where the save
//! cannot be read, the save-derived keys are null and `error` says why (`TypeName: message`).

use std::path::Path;

use crate::header::{HVal, Header, read_header};
use crate::json::{Obj, Value, whole_float};
use crate::reader::instances::{Instances, read_model_table};
use crate::stream::{
    TownRecord, cargo_entries, day_table, find_game_speed, iso_date, scan_records, town_names,
};
use crate::{counts, journal, states};

pub const SCHEMA_VERSION: u32 = 8;
pub const SCHEMA_URL: &str = "https://raw.githubusercontent.com/WuphonsReach/tf3-save-format/main/tools/schema/tf3-save-summary.v8.schema.json";

/// Every key, in the order written.
pub const FIELDS: [&str; 41] = [
    "$schema",
    "schema_version",
    "name",
    "mod_id",
    "kind",
    "source_name",
    "source_size",
    "author",
    "tags",
    "url",
    "tools_commit",
    "error",
    "version",
    "first_version",
    "map_seed",
    "start_year",
    "map_w_m",
    "map_h_m",
    "header_money",
    "header_counter",
    "climate",
    "economy",
    "name_list",
    "is_map_editor",
    "header_partial",
    "stream_bytes",
    "calendar",
    "journal",
    "vehicles",
    "industries",
    "company",
    "counters",
    "cycles",
    "subsidies",
    "town_states",
    "town_records",
    "towns",
    "settings",
    "mods",
    "cargo_list",
    "cargo_from_mods",
];

/// What comes from outside the save: the catalog id and kind given by the caller.
pub struct Options<'a> {
    pub mod_id: Option<&'a str>,
    pub kind: &'a str,
    pub game_dir: Option<&'a Path>,
    pub tools_commit: Option<&'a str>,
}

/// Python's `os.path.splitext(basename)[0]`: leading dots do not start an extension.
fn stem(name: &str) -> &str {
    let lead = name.len() - name.trim_start_matches('.').len();
    match name[lead..].rfind('.') {
        Some(i) => &name[..lead + i],
        None => name,
    }
}

/// New Game options: settings key -> (default index, labels in screen order), from the game's base/mod.json
/// (604 build), as `SETTING_OPTIONS` in tf3save.py. A stored setting is its list position plus 1.
const SETTING_OPTIONS: &[(&str, usize, &[&str])] = &[
    (
        "map.size",
        2,
        &[
            "Tiny",
            "Small",
            "Medium",
            "Large",
            "Very Large",
            "Huge",
            "Megalomaniac",
            "Gigantomaniac",
        ],
    ),
    (
        "map.format",
        0,
        &["1 : 1", "1 : 2", "1 : 3", "1 : 4", "1 : 5"],
    ),
    (
        "locations.towns.frequency",
        2,
        &["Sparse", "Scattered", "Medium", "Dense", "Packed"],
    ),
    (
        "locations.towns.populationDensity",
        2,
        &["50%", "75%", "100%", "150%", "200%"],
    ),
    (
        "locations.industry.initialIndustryDensity",
        2,
        &["Sparse", "Scattered", "Medium", "Dense", "Packed"],
    ),
    (
        "locations.industry.targetIndustryDensity",
        2,
        &["Sparse", "Scattered", "Medium", "Dense", "Packed"],
    ),
    (
        "locations.industry.industryProductivity",
        2,
        &["50%", "75%", "100%", "150%", "200%"],
    ),
    (
        "advancedOptions.vehiclePurchaseCostScale",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    (
        "advancedOptions.passengerIncome",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    (
        "advancedOptions.cargoIncome",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    ("advancedOptions.reforestation", 1, &["Off", "On"]),
    (
        "advancedOptions.infrastructurePurchaseCostScale",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    (
        "advancedOptions.infrastructureMaintenanceScale",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    (
        "advancedOptions.vehicleMaintenanceScale",
        2,
        &["50%", "75%", "100%", "125%", "150%"],
    ),
    (
        "advancedOptions.vehicleMaintenanceEffectScale",
        2,
        &["None", "Low", "Medium", "High", "Very High"],
    ),
    (
        "economy.industryDevelopment.closureProbability",
        1,
        &["Never", "Rarely", "Sometimes", "Often", "Very Often"],
    ),
    (
        "economy.townDevelopment.cargoNeedsPerTown",
        1,
        &[
            "2 Cargo Types",
            "Up to 4 Cargo Types",
            "Up to 6 Cargo Types",
        ],
    ),
    (
        "advancedOptions.trafficSpeedSensitivityScale",
        4,
        &[
            "0%", "25%", "50%", "75%", "100%", "125%", "150%", "175%", "200%",
        ],
    ),
    (
        "advancedOptions.subventionMode",
        2,
        &["Never", "Rarely", "Sometimes", "Often", "Very Often"],
    ),
    (
        "advancedOptions.subventionRisk",
        1,
        &["None", "Fair", "Risky", "Very Risky"],
    ),
    (
        "advancedOptions.landmarkResources",
        2,
        &["None", "Low", "Normal", "High", "Very High"],
    ),
    (
        "advancedOptions.inflationFactor",
        2,
        &["None", "Low", "Normal", "High", "Very High"],
    ),
    ("townConfig.sensitivityUrbanCare", 1, &["Off", "On"]),
    (
        "townConfig.sensitivityTrafficCongestion",
        3,
        &[
            "Off",
            "Very Low",
            "Low",
            "Normal",
            "High",
            "Very High",
            "Extreme",
        ],
    ),
    (
        "townConfig.sensitivityPeopleHappiness",
        3,
        &[
            "Off",
            "Very Low",
            "Low",
            "Normal",
            "High",
            "Very High",
            "Extreme",
        ],
    ),
    (
        "townConfig.sensitivityCargoDelivery",
        3,
        &[
            "Off",
            "Very Low",
            "Low",
            "Normal",
            "High",
            "Very High",
            "Extreme",
        ],
    ),
    (
        "townConfig.sensitivityNoise",
        3,
        &[
            "Off",
            "Very Low",
            "Low",
            "Normal",
            "High",
            "Very High",
            "Extreme",
        ],
    ),
    (
        "townConfig.sensitivityPollution",
        3,
        &[
            "Off",
            "Very Low",
            "Low",
            "Normal",
            "High",
            "Very High",
            "Extreme",
        ],
    ),
    (
        "weatherConfig.dynamicWeather",
        0,
        &["Dynamic", "Sunny", "Cloudy", "Rainy"],
    ),
    (
        "gameTimeConfig.timeOfDayMode",
        0,
        &[
            "Dynamic",
            "Continuous",
            "Local Time",
            "Morning",
            "Day",
            "Evening",
            "Night",
        ],
    ),
    ("guideSystemConfig.tutorial", 1, &["Off", "On"]),
];

fn hval_json(v: &HVal) -> Value {
    match v {
        HVal::Nil => Value::Null,
        HVal::Bool(b) => Value::Bool(*b),
        HVal::Num(x) => Value::Float(*x),
        HVal::Str(s) => Value::Str(s.clone()),
        HVal::List(_) => unreachable!("flattened"),
    }
}

/// A stored setting as "3 (100%, default)"; other values as they are, whole numbers as ints.
fn setting_label(key: &str, v: &HVal) -> Value {
    let HVal::Num(x) = v else { return hval_json(v) };
    if !(x.is_finite() && x.fract() == 0.0) {
        return Value::Float(*x);
    }
    let Some((_, default, labels)) = SETTING_OPTIONS.iter().find(|(k, _, _)| *k == key) else {
        return whole_float(*x);
    };
    if !(1.0..=labels.len() as f64).contains(x) {
        return whole_float(*x);
    }
    let i = *x as usize - 1;
    Value::Str(format!(
        "{} ({}{})",
        i + 1,
        labels[i],
        if i == *default { ", default" } else { "" }
    ))
}

fn calendar(data: &[u8]) -> Result<Value, String> {
    let Some(g) = find_game_speed(data) else {
        return Ok(Value::Null);
    };
    let table = day_table(data, &g)?.unwrap_or_default();
    let (mpd, ps) = (g.millis_per_day, g.play_speed);
    let date = |d: Option<&(u64, u32)>| Value::opt(d.and_then(|(_, day)| iso_date(*day)));
    let speed = match mpd {
        0 => "Paused".to_owned(),
        1000 | 2000 | 4000 | 8000 | 16000 => format!("{:.2}x", 4000.0 / f64::from(mpd)),
        _ => "not a slider step".to_owned(),
    };
    let mut o = Obj::new();
    o.set("date", date(table.last()));
    o.set("start_date", date(table.first()));
    o.set("calendar_speed", format!("{mpd} ({speed})"));
    o.set(
        "play_speed",
        if ps == 0 {
            format!("{ps} (paused)")
        } else {
            format!("{ps} ({ps}x)")
        },
    );
    o.set("clock", g.t1);
    o.set("day_table_entries", table.len());
    o.set(
        "day_table_regular",
        table
            .windows(2)
            .all(|w| u64::from(w[1].1) == u64::from(w[0].1) + 1 && w[1].0 > w[0].0),
    );
    Ok(o.into())
}

fn town_records(data: &[u8], recs: &[TownRecord], cargo: Option<&[String]>) -> Value {
    let start: Vec<&TownRecord> = recs.iter().filter(|r| r.floats == [1.0; 4]).collect();
    let (mut run, mut best) = (0usize, 0usize);
    for w in recs.windows(2) {
        run = if w[1].offset - w[0].offset == 78 {
            run + 1
        } else {
            0
        };
        best = best.max(run + 1);
    }
    let mut o = Obj::new();
    o.set("records", recs.len());
    o.set("starting_layout", start.len());
    o.set("longest_78_byte_run", best);
    o.set(
        "table_count",
        Value::opt(
            recs.first()
                .filter(|r| r.offset >= 4)
                .map(|r| u32::from_le_bytes(data[r.offset - 4..r.offset].try_into().unwrap())),
        ),
    );
    if !start.is_empty() {
        for (kind, pick) in [
            ("com", (|r: &TownRecord| r.com) as fn(&TownRecord) -> u32),
            ("ind", |r| r.ind),
        ] {
            // Count per id, then write by name in id order; a later id with the same name replaces the value
            // (the Python's Counter is by id, the dict it writes by name).
            let mut per_id: Vec<(u32, u64)> = Vec::new();
            for r in &start {
                let id = pick(r);
                match per_id.iter_mut().find(|(i, _)| *i == id) {
                    Some(e) => e.1 += 1,
                    None => per_id.push((id, 1)),
                }
            }
            per_id.sort_unstable();
            let mut c = Obj::new();
            for (id, n) in per_id {
                let name = match cargo {
                    Some(names) if (id as usize) < names.len() => names[id as usize].clone(),
                    _ => id.to_string(),
                };
                c.set(name, n);
            }
            o.set(format!("{kind}_cargo"), c);
        }
        let totals: Vec<Value> = (0..3)
            .map(|k| Value::from(start.iter().map(|r| u64::from(r.caps[k])).sum::<u64>()))
            .collect();
        o.set("capacity_totals", Value::List(totals));
    }
    o.into()
}

/// The save-derived fields, or the error that stops them. They are read in the Python's order, so the first
/// error met is the same one.
#[allow(clippy::vec_init_then_push)]
fn read_fields(data: &[u8], opts: &Options) -> Result<Vec<(&'static str, Value)>, String> {
    let h: Header = read_header(data)?;
    let res = h.resources.clone().unwrap_or_default();
    let resource = |key: &str| {
        res.iter()
            .rev()
            .find(|(k, _)| k == key)
            .map(|(_, v)| v.clone())
    };
    let entries = cargo_entries(data);
    let cargo_names: Option<Vec<String>> = entries
        .as_ref()
        .map(|e| e.iter().map(|(_, n, _)| n.clone()).collect());
    let st = states::read_states(data)?;
    let mut f: Vec<(&'static str, Value)> = Vec::new();
    f.push(("version", h.version.into()));
    f.push(("first_version", Value::opt(h.first_version)));
    f.push(("map_seed", Value::opt(h.map_seed.clone())));
    f.push(("start_year", h.start_year.into()));
    f.push(("map_w_m", h.map_w_m.into()));
    f.push(("map_h_m", h.map_h_m.into()));
    f.push(("header_money", h.money.into()));
    f.push(("header_counter", h.counter.into()));
    f.push((
        "climate",
        Value::opt(resource("climate").map(|c| c.rsplit('/').next().unwrap_or("").to_owned())),
    ));
    f.push(("economy", Value::opt(resource("economy"))));
    f.push(("name_list", Value::opt(resource("nameList"))));
    f.push((
        "is_map_editor",
        h.settings
            .iter()
            .find(|(k, _)| k == "isMapEditor")
            .map_or(Value::Null, |(_, v)| hval_json(v)),
    ));
    f.push(("header_partial", Value::opt(h.partial.clone())));
    f.push(("stream_bytes", h.stream_len.into()));
    f.push(("calendar", calendar(data)?));
    f.push((
        "journal",
        journal::play_summary(data, h.money).unwrap_or(Value::Null),
    ));
    let (vehicles, industries) = match read_model_table(data) {
        Some(table) => {
            let inst = Instances::scan(data, &table);
            (
                counts::count_vehicles(data, &table, &inst, opts.game_dir)?,
                counts::count_industries(data, &table, &inst),
            )
        }
        None => (Value::Null, Value::Null),
    };
    f.push(("vehicles", vehicles));
    f.push(("industries", industries));
    f.push(("company", st.company));
    f.push(("counters", st.counters));
    f.push(("cycles", st.cycles));
    f.push(("subsidies", st.subsidies));
    f.push(("town_states", Value::opt(st.town_states)));
    let recs = scan_records(data)?;
    f.push((
        "town_records",
        town_records(data, &recs, cargo_names.as_deref()),
    ));
    let towns = town_names(data, recs.len().max(st.town_states.unwrap_or(0))).map(|names| {
        let mut o = Obj::new();
        o.set("count", names.len());
        o.set(
            "names",
            Value::List(names.into_iter().map(Value::Str).collect()),
        );
        Value::from(o)
    });
    f.push(("towns", Value::opt(towns)));
    let settings = if h.settings.is_empty() {
        Value::Null
    } else {
        let mut s: Vec<&(String, HVal)> = h.settings.iter().collect();
        s.sort_by(|a, b| a.0.cmp(&b.0));
        Value::Obj(
            s.into_iter()
                .map(|(k, v)| (k.clone(), setting_label(k, v)))
                .collect(),
        )
    };
    f.push(("settings", settings));
    f.push((
        "mods",
        Value::List(h.mods.iter().map(|m| Value::str(m.as_str())).collect()),
    ));
    f.push((
        "cargo_list",
        Value::opt(cargo_names.map(|n| Value::List(n.into_iter().map(Value::Str).collect()))),
    ));
    let from_mods = entries.as_ref().map(|e| {
        let mut o = Obj::new();
        for (_, n, m) in e {
            if !m.is_empty() {
                o.set(n.clone(), m.clone());
            }
        }
        Value::from(o)
    });
    f.push(("cargo_from_mods", Value::opt(from_mods)));
    Ok(f)
}

/// The summary of the save at `path`.
pub fn summarise(path: &Path, opts: &Options) -> Value {
    let source_name = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let mut out: Vec<(String, Value)> = FIELDS
        .iter()
        .map(|k| (k.to_string(), Value::Null))
        .collect();
    let mut set = |key: &str, v: Value| {
        out.iter_mut().find(|(k, _)| k == key).unwrap().1 = v;
    };
    set("$schema", SCHEMA_URL.into());
    set("schema_version", SCHEMA_VERSION.into());
    set("name", stem(&source_name).into());
    set("mod_id", Value::opt(opts.mod_id));
    set("kind", opts.kind.into());
    set("source_name", source_name.as_str().into());
    set("tags", Value::List(Vec::new()));
    set("tools_commit", Value::opt(opts.tools_commit));
    let size = match std::fs::metadata(path) {
        Ok(m) => m.len(),
        Err(e) => {
            set("error", format!("{}: {e}", io_error_name(&e)).into());
            return Value::Obj(out);
        }
    };
    set("source_size", size.into());
    // Decompressed straight from the file, so the compressed bytes are never held whole beside the stream.
    let result = std::fs::File::open(path)
        .map_err(|e| format!("{}: {e}", io_error_name(&e)))
        .and_then(|file| {
            crate::reader::container::decompress(std::io::BufReader::with_capacity(1 << 20, file))
                .map_err(|e| zstd_error(&e))
        })
        .and_then(|data| read_fields(&data, opts));
    match result {
        Ok(fields) => {
            for (k, v) in fields {
                set(k, v);
            }
        }
        Err(e) => set("error", e.into()),
    }
    Value::Obj(out)
}

/// A decompression error in the words of Python's `compression.zstd`, which the Python summaries carry: a cut-off
/// file (or an empty one) and bytes that are not zstd. Other errors keep the zstd library's text.
fn zstd_error(e: &std::io::Error) -> String {
    let text = e.to_string();
    match text.as_str() {
        "incomplete frame" => {
            "ZstdError: Compressed data ended before the end-of-stream marker was reached".into()
        }
        t => format!("ZstdError: Unable to decompress Zstandard data: {t}"),
    }
}

fn io_error_name(e: &std::io::Error) -> &'static str {
    match e.kind() {
        std::io::ErrorKind::NotFound => "FileNotFoundError",
        std::io::ErrorKind::PermissionDenied => "PermissionError",
        _ => "OSError",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stem_is_python_splitext() {
        assert_eq!(stem("a.sav"), "a");
        assert_eq!(stem("a.b.sav"), "a.b");
        assert_eq!(stem(".sav"), ".sav");
        assert_eq!(stem("..sav"), "..sav");
        assert_eq!(stem("noext"), "noext");
    }

    #[test]
    fn settings_read_as_labels() {
        assert_eq!(
            setting_label("map.size", &HVal::Num(3.0)),
            Value::str("3 (Medium, default)")
        );
        assert_eq!(setting_label("map.size", &HVal::Num(9.0)), Value::Int(9));
        assert_eq!(setting_label("other", &HVal::Num(2.5)), Value::Float(2.5));
        assert_eq!(
            setting_label("map.size", &HVal::Bool(true)),
            Value::Bool(true)
        );
    }
}
