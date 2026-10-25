//! The summary's company, counters, cycles, subsidies and town_states, from the script states of the company,
//! achievements, game time, subsidy and town scripts (`docs/script-states.md`, `docs/town-states.md`,
//! `docs/company.md`), as `summarise_states` in mine_summary.py reads them. Only counts and a few numbers are
//! taken, never the text a mod's script keeps (which can hold an install path).

use crate::json::{Obj, Value};
use crate::lua::{Lua, Table, script_state};

/// Rank names as the company window lists them (English UI, 604); `potentialLevel` is the rank shown.
pub const RANKS: [&str; 15] = [
    "Junior",
    "Mechanic",
    "Engineer",
    "Coordinator",
    "Expert",
    "Team Leader",
    "Supervisor",
    "Manager",
    "Director",
    "Senior Director",
    "CEO",
    "Chairperson",
    "Vice President",
    "President",
    "Tycoon",
];

pub struct States {
    pub company: Value,
    pub counters: Value,
    pub cycles: Value,
    pub subsidies: Value,
    /// The number of town states, or `None` without a town script.
    pub town_states: Option<usize>,
}

fn rank(level: Option<&Lua>) -> Value {
    match level {
        Some(Lua::Num(x)) if x.is_finite() && x.fract() == 0.0 && (1.0..=15.0).contains(x) => {
            Value::Str(format!("{} ({})", *x as i64, RANKS[*x as usize - 1]))
        }
        // Python's bool is an int: True is rank 1.
        Some(Lua::Bool(true)) => Value::Str(format!("True ({})", RANKS[0])),
        Some(v) => v.num_json(),
        None => Value::Null,
    }
}

fn num(v: Option<&Lua>) -> Value {
    v.map_or(Value::Null, Lua::num_json)
}

/// A mode name with the Cycle menu's name after it when that differs (`Automatic (Continuous)`).
fn mode(v: Option<&Lua>, names: &[(&str, &str)]) -> Result<Value, String> {
    match v {
        Some(Lua::Str(s)) => Ok(match names.iter().find(|(k, _)| k == s) {
            Some((k, label)) if k != label => Value::Str(format!("{s} ({label})")),
            _ => Value::Str(s.clone()),
        }),
        Some(Lua::Table(_)) => Err("TypeError: unhashable type: 'dict'".into()),
        // NaN is not equal to itself, so the Python goes on to look it up and fails.
        Some(Lua::Num(x)) if x.is_nan() => Err("KeyError: nan".into()),
        Some(v) => Ok(v.to_json()),
        None => Ok(Value::Null),
    }
}

fn state(data: &[u8], path: &str) -> Result<Option<Table>, String> {
    script_state(data, path)
}

pub fn read_states(data: &[u8]) -> Result<States, String> {
    let prog = state(data, "game_mechanics/company/company_progression.gs")?;
    let company = state(data, "game_mechanics/company/company.gs")?;
    // (prog.get("companyState") or {}).values(), dicts only
    let cs_value = prog.as_ref().and_then(|p| p.get("companyState"));
    let mut cs: Option<&Table> = None;
    let mut any_state = false;
    match cs_value {
        Some(v) if v.truthy() => match v {
            Lua::Table(t) => {
                cs = t.pairs.iter().find_map(|(_, s)| s.as_table());
                any_state = cs.is_some();
            }
            v => {
                return Err(format!(
                    "AttributeError: '{}' object has no attribute 'values'",
                    v.type_name()
                ));
            }
        },
        _ => {}
    }
    let company_v = if any_state || company.as_ref().is_some_and(|c| c.len() > 0) {
        let mut o = Obj::new();
        o.set(
            "rank_earned",
            rank(cs.and_then(|t| t.get("potentialLevel"))),
        );
        o.set("rank_claimed", rank(cs.and_then(|t| t.get("level"))));
        o.set("experience", num(cs.and_then(|t| t.get("experience"))));
        o.set(
            "base_population",
            num(company.as_ref().and_then(|t| t.get("basePopulation"))),
        );
        o.into()
    } else {
        Value::Null
    };

    let counters = match state(data, "game_mechanics/achievements/achievements.gs")? {
        Some(ach) => {
            let skip = ["version", "lastIncomeUpdateTime", "stationGroupEntity"];
            let mut items: Vec<(&str, f64)> = ach
                .pairs
                .iter()
                .filter_map(|(k, v)| match (k, v) {
                    (Lua::Str(k), Lua::Num(x)) if !skip.contains(&k.as_str()) => {
                        Some((k.as_str(), *x))
                    }
                    _ => None,
                })
                .collect();
            items.sort_by(|a, b| a.0.cmp(b.0));
            let mut o = Obj::new();
            for (k, x) in items {
                o.set(k, Lua::Num(x).num_json());
            }
            for k in ["cargoTypesDelivered", "vehiclesUsed", "shipsUsed"] {
                if let Some(Lua::Table(t)) = ach.get(k) {
                    o.set(k, t.len());
                }
            }
            o.into()
        }
        None => Value::Null,
    };

    let cycles = match state(data, "game_mechanics/game_time/game_time.gs")? {
        Some(gt) => {
            let mut o = Obj::new();
            o.set(
                "time_of_day",
                mode(
                    gt.get("timeOfDayMode"),
                    &[
                        ("Dynamic", "Dynamic"),
                        ("Automatic", "Continuous"),
                        ("Constant", "Custom"),
                    ],
                )?,
            );
            o.set(
                "weather",
                mode(
                    gt.get("weatherMode"),
                    &[("Dynamic", "Dynamic"), ("Constant", "Custom")],
                )?,
            );
            o.into()
        }
        None => Value::Null,
    };

    let subsidies = match state(data, "game_mechanics/subventions/subventions.gs")? {
        Some(sub) => {
            let mut o = Obj::new();
            for k in ["proposed", "active", "completed", "failed"] {
                let n = match sub.get(&format!("{k}Subventions")) {
                    Some(Lua::Table(t)) => t.len(),
                    _ => 0,
                };
                o.set(k, n);
            }
            o.into()
        }
        None => Value::Null,
    };

    let town_states =
        state(data, "game_mechanics/towns/town.gs")?.map(|town| match town.get("townStates") {
            Some(Lua::Table(t)) => t.len(),
            _ => 0,
        });

    Ok(States {
        company: company_v,
        counters,
        cycles,
        subsidies,
        town_states,
    })
}
