//! The player's money journal and how long the game has been played, ported from `journal.py`
//! (`docs/finances.md`). The journal is `u32 count`, 21-byte bookings (i64 time, i64 amount, five u8
//! categories: type, construction, maintenance, other, carrier) and an `i64` balance. It sits after the
//! edge-addon name table and is found by that pattern. `journal.py` follows the finder in tf3-save-editor's
//! `crates/lib/src/journal.rs` (see THIRD_PARTY_NOTICES.md).

use crate::json::{Obj, Value};
use crate::stream::find_all;

const ENTRY: usize = 21;
const PERIOD: i64 = 1_461_000;
const EDGE_TABLE_ANCHOR: &[u8] = b"edge_addons/barrier_track_b.edge";
const MAX_IDS: u32 = 1 << 20;
const LATE_START_WINDOW: usize = 64;
/// Booking types that are play: CONSTRUCTION, ACQUISITION, MAINTENANCE, INCOME, SUBSIDY.
const PLAY_TYPES: [u8; 5] = [2, 3, 4, 5, 7];
const INCOME: u8 = 5;

#[derive(Clone, Copy)]
struct Booking {
    time: i64,
    amount: i64,
    kind: u8,
}

fn u32_at(data: &[u8], at: usize) -> Option<u32> {
    data.get(at..at.checked_add(4)?)
        .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
}

fn i64_at(data: &[u8], at: usize) -> i64 {
    i64::from_le_bytes(data[at..at + 8].try_into().unwrap())
}

/// (time, amount, type, construction, maintenance, other, carrier) at `at`.
fn entry(data: &[u8], at: usize) -> (i64, i64, u8, u8, u8, u8, u8) {
    let c = &data[at + 16..at + 21];
    (
        i64_at(data, at),
        i64_at(data, at + 8),
        c[0],
        c[1],
        c[2],
        c[3],
        c[4],
    )
}

fn bad_categories(e: (i64, i64, u8, u8, u8, u8, u8)) -> bool {
    e.2 > 7 || e.3 > 7 || e.4 > 3 || e.5 != 0 || e.6 > 5
}

fn skip_text(data: &[u8], at: usize) -> Option<usize> {
    let n = u32_at(data, at)?;
    if n > 512 {
        return None;
    }
    let end = at + 4 + n as usize;
    if end > data.len() || !data[at + 4..end].iter().all(|b| (0x20..0x7f).contains(b)) {
        return None;
    }
    Some(end)
}

/// The bookings and balance of a journal starting at `at`, or `None` if what is there is not one.
fn read_at(data: &[u8], at: usize) -> Option<(Vec<Booking>, i64)> {
    let n = u32_at(data, at)? as usize;
    if at + 4 + n * ENTRY + 8 > data.len() {
        return None;
    }
    let mut out = Vec::with_capacity(n.min(1 << 16));
    let mut last = -1i64;
    for i in 0..n {
        let e = entry(data, at + 4 + i * ENTRY);
        if e.0 < last || bad_categories(e) {
            return None;
        }
        last = e.0;
        out.push(Booking {
            time: e.0,
            amount: e.1,
            kind: e.2,
        });
    }
    Some((out, i64_at(data, at + 4 + n * ENTRY)))
}

fn sum(entries: &[Booking]) -> i128 {
    entries.iter().map(|e| i128::from(e.amount)).sum()
}

fn find_journal(data: &[u8], header_money: i64) -> Option<(Vec<Booking>, i64)> {
    for hit in find_all(data, EDGE_TABLE_ANCHOR) {
        let mut at = hit + EDGE_TABLE_ANCHOR.len();
        if u32_at(data, at) != Some(5) {
            continue;
        }
        at += 4;
        // Entries added by mods: a name and a path, each a printable `str`, then a u32.
        while let Some(path_at) = skip_text(data, at) {
            let Some(end) = skip_text(data, path_at) else {
                break;
            };
            if !(end > path_at + 4 && u32_at(data, end).is_some()) {
                break;
            }
            at = end + 4;
        }
        let Some(ids) = u32_at(data, at + 4) else {
            continue;
        };
        if ids > MAX_IDS {
            continue;
        }
        let usual = at + 8 + ids as usize * 4 + 4 + 5;
        if u32_at(data, usual - 5) == Some(1)
            && data.get(usual - 1) == Some(&0)
            && let Some(j) = read_at(data, usual)
            && (j.1 == header_money || i128::from(j.1) == sum(&j.0))
        {
            return Some(j);
        }
        for start in usual + 1..usual + LATE_START_WINDOW {
            if let Some(j) = read_at(data, start)
                && !j.0.is_empty()
                && j.1 == header_money
            {
                return Some(j);
            }
        }
    }
    if header_money != 0 {
        find_by_balance(data, header_money)
    } else {
        None
    }
}

/// For saves without the name table: find the balance bytes and walk back over bookings until the stored count
/// equals the number walked and the amounts add up to the balance.
fn find_by_balance(data: &[u8], balance: i64) -> Option<(Vec<Booking>, i64)> {
    let target = balance.to_le_bytes();
    for bal_at in find_all(data, &target) {
        let mut later: Option<i64> = None;
        for k in 1..=bal_at / ENTRY {
            let Some(at) = bal_at.checked_sub(k * ENTRY).filter(|&a| a >= 4) else {
                break;
            };
            let e = entry(data, at);
            if bad_categories(e)
                || e.0 < 0
                || later.is_some_and(|l| e.0 > l)
                || (k == 1 && e.1 == 0)
            {
                break;
            }
            later = Some(e.0);
            if u32_at(data, at - 4) == Some(k as u32) {
                if let Some(j) = read_at(data, at - 4)
                    && i128::from(j.1) == sum(&j.0)
                {
                    return Some(j);
                }
                break;
            }
        }
    }
    None
}

/// The journal's facts for the summary, or `None` where no journal was found.
pub fn play_summary(data: &[u8], header_money: i64) -> Option<Value> {
    let (entries, balance) = find_journal(data, header_money)?;
    let play: Vec<&Booking> = entries
        .iter()
        .filter(|e| PLAY_TYPES.contains(&e.kind))
        .collect();
    let period = |t: i64| t.div_euclid(PERIOD);
    let mut out = Obj::new();
    out.set("bookings", entries.len());
    out.set("balance_stored", balance);
    out.set("balance_sum", sum(&entries));
    out.set("last_time", Value::opt(entries.last().map(|e| e.time)));
    out.set("first_play_time", Value::opt(play.first().map(|e| e.time)));
    out.set("last_play_time", Value::opt(play.last().map(|e| e.time)));
    let (mut pp, mut ap, mut ip) = (0i64, 0usize, 0usize);
    if let (Some(first), Some(last)) = (play.first(), play.last()) {
        pp = period(last.time) - period(first.time) + 1;
        let mut active: Vec<i64> = play.iter().map(|e| period(e.time)).collect();
        active.dedup();
        active.sort_unstable();
        active.dedup();
        ap = active.len();
        let mut income: Vec<i64> = play
            .iter()
            .filter(|e| e.kind == INCOME)
            .map(|e| period(e.time))
            .collect();
        income.sort_unstable();
        income.dedup();
        ip = income.len();
    }
    out.set("play_periods", pp);
    out.set("active_periods", ap);
    out.set("income_periods", ip);
    out.set(
        "income_total",
        entries
            .iter()
            .filter(|e| e.kind == INCOME)
            .map(|e| i128::from(e.amount))
            .sum::<i128>(),
    );
    Some(out.into())
}
