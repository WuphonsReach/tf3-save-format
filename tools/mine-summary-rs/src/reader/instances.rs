//! The model table and model instances (`docs/models.md` in tf3-save-format).
//!
//! Copied from tf3-save-mapper's `crates/tf3-save-mapper-core/src/instances.rs` at commit bfe77c7 (same author,
//! MIT OR Apache-2.0) and changed to what the summary needs: the table's lookup returns `Option`, and
//! `Instances` keeps the record scan so several prefixes are listed from one scan, with the model path only.
//!
//! The model table comes right after the header: a u32 count, then per model a `str` source mod, a `str` path
//! and a u32 id that starts at 0 and rises along the table (it skips ahead where a mod's models are). An
//! instance is a model id followed by a 4 x 4 f32 transform whose floats 3, 7 and 11 are 0 and float 15 is 1;
//! it is found by that pattern after the table.

use std::collections::{BTreeMap, BTreeSet, HashMap};

use memchr::memmem;

/// One instance record: the model id and the 16 floats.
const RECORD_BYTES: usize = 4 + 64;
/// 1.0 as f32: the transform's last float.
const ONE: [u8; 4] = [0x00, 0x00, 0x80, 0x3f];
/// The table is searched for this far before its first `animal/` path.
const TABLE_REACH: usize = 2000;
/// Fewest records in a run that counts as a page of the editor's preview block.
const BLOCK_RUN: usize = 6;

/// The model table: each model's path by its id, and the offset just after it.
pub struct ModelTable {
    pub paths: BTreeMap<u32, String>,
    pub end: usize,
}

fn u32_at(data: &[u8], at: usize) -> Option<u32> {
    Some(u32::from_le_bytes(
        data.get(at..at.checked_add(4)?)?.try_into().unwrap(),
    ))
}

/// The model table: a u32 count, then per model a `str` source mod, a `str` path and a u32 id that starts at
/// 0 and rises along the table. Found from the first `animal/` path, which the base game's table sorts first.
pub fn read_model_table(data: &[u8]) -> Option<ModelTable> {
    let first = memmem::find(data, b"animal/")?;
    (first.saturating_sub(TABLE_REACH)..first).find_map(|start| table_at(data, start))
}

fn table_at(data: &[u8], start: usize) -> Option<ModelTable> {
    let n = u32_at(data, start)?;
    if !(101..100_000).contains(&n) {
        return None;
    }
    let mut p = start + 4;
    let mut paths = BTreeMap::new();
    let mut last: Option<u32> = None;
    for k in 0..n {
        let mod_len = u32_at(data, p)? as usize;
        p = p.checked_add(4 + mod_len)?;
        let len = u32_at(data, p)? as usize;
        let path = std::str::from_utf8(data.get(p + 4..p.checked_add(4 + len)?)?).ok()?;
        p += 4 + len;
        let id = u32_at(data, p)?;
        if id < k || last.is_some_and(|l| id <= l) || (k == 0 && id != 0) {
            return None;
        }
        p += 4;
        paths.insert(id, path.to_owned());
        last = Some(id);
    }
    Some(ModelTable { paths, end: p })
}

fn record(data: &[u8], at: usize) -> (u32, [f32; 16]) {
    let id = u32::from_le_bytes(data[at..at + 4].try_into().unwrap());
    let mut m = [0f32; 16];
    for (i, f) in m.iter_mut().enumerate() {
        let o = at + 4 + 4 * i;
        *f = f32::from_le_bytes(data[o..o + 4].try_into().unwrap());
    }
    (id, m)
}

/// Offsets of every instance record after `from`, in stream order and not overlapping: an id, then a
/// transform whose floats 3, 7 and 11 are zero and whose float 15 is 1.0.
pub fn find_records(data: &[u8], from: usize) -> Vec<usize> {
    let Some(tail) = data.get(from..) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    let mut next_free = 0;
    for one in memmem::find_iter(tail, &ONE) {
        let Some(start) = one.checked_sub(RECORD_BYTES - 4) else {
            continue;
        };
        if start < next_free {
            continue;
        }
        let zero = |o: usize| tail[start + o..start + o + 4] == [0; 4];
        if zero(16) && zero(32) && zero(48) {
            out.push(from + start);
            next_free = start + RECORD_BYTES;
        }
    }
    out
}

/// The indexes (into `matches`) of the records of the map editor's model preview block
/// (`docs/editor-saves.md`): pages of records exactly 68 bytes apart with no rotation and ids rising by one,
/// at least `BLOCK_RUN` long, and a shorter page next to such a page with at most 200 bytes between them.
fn preview_block(data: &[u8], matches: &[usize]) -> BTreeSet<usize> {
    let mut pages: Vec<Vec<usize>> = Vec::new();
    let mut run: Vec<usize> = Vec::new();
    let mut prev: Option<(usize, u32)> = None;
    for (k, &at) in matches.iter().enumerate() {
        let (id, m) = record(data, at);
        let plain = [1, 2, 4, 6, 8, 9].iter().all(|&i| m[i] == 0.0);
        if plain
            && prev.is_some_and(|(p, pid)| {
                at - p == RECORD_BYTES && u64::from(id) == u64::from(pid) + 1
            })
        {
            run.push(k);
        } else {
            if !run.is_empty() {
                pages.push(std::mem::take(&mut run));
            }
            if plain {
                run.push(k);
            }
        }
        prev = Some((at, id));
    }
    if !run.is_empty() {
        pages.push(run);
    }
    let mut keep: Vec<bool> = pages.iter().map(|p| p.len() >= BLOCK_RUN).collect();
    let near = |a: usize, b: usize| {
        let gap = matches[pages[b][0]] as i64
            - matches[*pages[a].last().unwrap()] as i64
            - RECORD_BYTES as i64;
        0 < gap && gap <= 200
    };
    for i in 1..pages.len() {
        keep[i] = keep[i] || (keep[i - 1] && near(i - 1, i));
    }
    for i in (0..pages.len().saturating_sub(1)).rev() {
        keep[i] = keep[i] || (keep[i + 1] && near(i, i + 1));
    }
    pages
        .into_iter()
        .zip(keep)
        .filter(|(_, k)| *k)
        .flat_map(|(p, _)| p)
        .collect()
}

/// The model paths of the instances whose path starts with one of `prefixes`, in stream order, with the
/// preview block left out and records with a non-finite position or facing dropped (`read_instances` in
/// model_instances.py). The record scan is shared by the callers: pass `records = find_records(...)` and
/// `skip = preview_block(...)` once.
pub struct Instances {
    records: Vec<usize>,
    skip: BTreeSet<usize>,
}

impl Instances {
    pub fn scan(data: &[u8], table: &ModelTable) -> Instances {
        let records = find_records(data, table.end);
        let skip = preview_block(data, &records);
        Instances { records, skip }
    }

    pub fn models<'t>(&self, data: &[u8], table: &'t ModelTable, prefix: &str) -> Vec<&'t str> {
        let wanted: HashMap<u32, &str> = table
            .paths
            .iter()
            .filter(|(_, p)| p.starts_with(prefix))
            .map(|(&id, p)| (id, p.as_str()))
            .collect();
        let mut out = Vec::new();
        for (k, &at) in self.records.iter().enumerate() {
            let (id, m) = record(data, at);
            let Some(model) = wanted.get(&id) else {
                continue;
            };
            if self.skip.contains(&k) {
                continue;
            }
            if ![m[12], m[13], m[14], m[0], m[1]]
                .iter()
                .all(|v| v.is_finite())
            {
                continue;
            }
            out.push(*model);
        }
        out
    }
}
