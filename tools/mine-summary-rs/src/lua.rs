//! Lua values as the save stores them (`docs/lua-values.md`): a u32 tag, then 0 nil, 1 bool (u8), 2 number
//! (f64), 3 string (`str`), 4 table (u8 flag; 1 is followed by a u32 pair count and the pairs). The same
//! encoding tf3-save-editor reads in `lua.rs` (see THIRD_PARTY_NOTICES.md).
//!
//! A table is kept the way the Python reference holds it, as a dict: a key met twice keeps its first place and
//! takes the later value, `true` is the same key as 1 and `false` as 0, and every NaN key is a key of its own.
//! A table used as a key cannot be held (the Python raises TypeError); that is a hard error here too.

use std::collections::HashMap;

use crate::json::{Value, float_repr, whole_float};

#[derive(Debug, Clone)]
pub enum Lua {
    Nil,
    Bool(bool),
    Num(f64),
    Str(String),
    /// A table whose flag byte is 1; a flag of 0 reads as `Nil`.
    Table(Table),
}

#[derive(Debug, Clone, Default)]
pub struct Table {
    pub pairs: Vec<(Lua, Lua)>,
    index: HashMap<KeyId, usize>,
    nan_keys: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
enum KeyId {
    Nil,
    Num(u64),
    NaN(usize),
    Str(String),
}

/// Why a read stopped. `Soft` is what the Python catches and steps past (bad tag, past the end, too deep);
/// `Hard` is what it does not catch and so ends the whole summary with an error.
#[derive(Debug, Clone)]
pub enum LuaError {
    Soft,
    Hard(String),
}

impl Table {
    pub fn len(&self) -> usize {
        self.pairs.len()
    }

    fn insert(&mut self, k: Lua, v: Lua) -> Result<(), LuaError> {
        let id = match &k {
            Lua::Nil => KeyId::Nil,
            Lua::Bool(b) => KeyId::Num(if *b { 1f64 } else { 0f64 }.to_bits()),
            Lua::Num(x) if x.is_nan() => {
                self.nan_keys += 1;
                KeyId::NaN(self.nan_keys)
            }
            Lua::Num(x) => KeyId::Num(if *x == 0.0 { 0f64 } else { *x }.to_bits()),
            Lua::Str(s) => KeyId::Str(s.clone()),
            Lua::Table(_) => {
                return Err(LuaError::Hard("TypeError: unhashable type: 'dict'".into()));
            }
        };
        match self.index.get(&id) {
            Some(&i) => self.pairs[i].1 = v,
            None => {
                self.index.insert(id, self.pairs.len());
                self.pairs.push((k, v));
            }
        }
        Ok(())
    }

    /// The value under a string key.
    pub fn get(&self, key: &str) -> Option<&Lua> {
        self.index
            .get(&KeyId::Str(key.to_owned()))
            .map(|&i| &self.pairs[i].1)
    }

    pub fn all_keys_str(&self) -> bool {
        self.pairs.iter().all(|(k, _)| matches!(k, Lua::Str(_)))
    }
}

impl Lua {
    /// Python truth: nil, false, 0, "" and an empty table are false.
    pub fn truthy(&self) -> bool {
        match self {
            Lua::Nil => false,
            Lua::Bool(b) => *b,
            Lua::Num(x) => *x != 0.0,
            Lua::Str(s) => !s.is_empty(),
            Lua::Table(t) => t.len() > 0,
        }
    }

    pub fn as_table(&self) -> Option<&Table> {
        match self {
            Lua::Table(t) => Some(t),
            _ => None,
        }
    }

    /// The Python type name, for the error texts that name it.
    pub fn type_name(&self) -> &'static str {
        match self {
            Lua::Nil => "NoneType",
            Lua::Bool(_) => "bool",
            Lua::Num(_) => "float",
            Lua::Str(_) => "str",
            Lua::Table(_) => "dict",
        }
    }

    /// The value as `json.dump` writes the Python object (numbers stay floats).
    pub fn to_json(&self) -> Value {
        match self {
            Lua::Nil => Value::Null,
            Lua::Bool(b) => Value::Bool(*b),
            Lua::Num(x) => Value::Float(*x),
            Lua::Str(s) => Value::Str(s.clone()),
            Lua::Table(t) => Value::Obj(
                t.pairs
                    .iter()
                    .map(|(k, v)| (key_text(k), v.to_json()))
                    .collect(),
            ),
        }
    }

    /// `num()` of mine_summary.py: a whole number as an int, everything else as it is.
    pub fn num_json(&self) -> Value {
        match self {
            Lua::Num(x) if x.is_finite() && x.fract() == 0.0 => whole_float(*x),
            v => v.to_json(),
        }
    }
}

/// How `json.dump` writes a dict key that is not a string.
fn key_text(k: &Lua) -> String {
    match k {
        Lua::Nil => "null".into(),
        Lua::Bool(b) => if *b { "true" } else { "false" }.into(),
        Lua::Num(x) => float_repr(*x),
        Lua::Str(s) => s.clone(),
        Lua::Table(_) => unreachable!("tables are refused as keys"),
    }
}

/// Deeper than this, the Python's recursion limit stops the read (two frames per level of 1,000).
const MAX_DEPTH: usize = 490;

fn u32_at(data: &[u8], p: usize) -> Result<u32, LuaError> {
    data.get(p..p + 4)
        .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
        .ok_or(LuaError::Soft)
}

/// The value at `p` and the offset after it.
pub fn value(data: &[u8], p: usize, depth: usize) -> Result<(Lua, usize), LuaError> {
    let tag = u32_at(data, p)?;
    let p = p + 4;
    match tag {
        0 => Ok((Lua::Nil, p)),
        1 => Ok((Lua::Bool(*data.get(p).ok_or(LuaError::Soft)? != 0), p + 1)),
        2 => {
            let b = data.get(p..p + 8).ok_or(LuaError::Soft)?;
            Ok((Lua::Num(f64::from_le_bytes(b.try_into().unwrap())), p + 8))
        }
        3 => {
            let n = u32_at(data, p)? as usize;
            let s = data.get(p + 4..p + 4 + n).ok_or(LuaError::Soft)?;
            Ok((Lua::Str(String::from_utf8_lossy(s).into_owned()), p + 4 + n))
        }
        4 => {
            if *data.get(p).ok_or(LuaError::Soft)? == 0 {
                return Ok((Lua::Nil, p + 1));
            }
            let (t, end) = pairs(data, p + 1, depth + 1)?;
            Ok((Lua::Table(t), end))
        }
        _ => Err(LuaError::Soft),
    }
}

/// A table body at `p`: a u32 pair count, then key and value for each.
pub fn pairs(data: &[u8], p: usize, depth: usize) -> Result<(Table, usize), LuaError> {
    if depth > MAX_DEPTH {
        return Err(LuaError::Soft);
    }
    let n = u32_at(data, p)? as usize;
    let mut p = p + 4;
    if n > (data.len() - p) / 8 {
        return Err(LuaError::Soft);
    }
    let mut t = Table::default();
    for _ in 0..n {
        let (k, q) = value(data, p, depth)?;
        let (v, q) = value(data, q, depth)?;
        t.insert(k, v)?;
        p = q;
    }
    Ok((t, p))
}

/// The state table of the script at `path` ("game_mechanics/company/company.gs"): the path as a `str`, one byte,
/// then a table body, with no tag before it (`docs/script-states.md`). Every place the path string occurs is
/// tried, and the first that reads as a table with string keys is taken.
pub fn script_state(data: &[u8], path: &str) -> Result<Option<Table>, String> {
    let mut pat = (path.len() as u32).to_le_bytes().to_vec();
    pat.extend_from_slice(path.as_bytes());
    let finder = memchr::memmem::Finder::new(&pat);
    let mut from = 0;
    while let Some(i) = finder.find(&data[from..]) {
        let pos = from + i;
        match pairs(data, pos + pat.len() + 1, 0) {
            Ok((t, _)) if t.all_keys_str() => return Ok(Some(t)),
            Ok(_) | Err(LuaError::Soft) => {}
            Err(LuaError::Hard(e)) => return Err(e),
        }
        from = pos + 1;
    }
    Ok(None)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn num(out: &mut Vec<u8>, x: f64) {
        out.extend_from_slice(&2u32.to_le_bytes());
        out.extend_from_slice(&x.to_le_bytes());
    }

    fn string(out: &mut Vec<u8>, s: &str) {
        out.extend_from_slice(&3u32.to_le_bytes());
        out.extend_from_slice(&(s.len() as u32).to_le_bytes());
        out.extend_from_slice(s.as_bytes());
    }

    #[test]
    fn keys_merge_as_in_a_python_dict() {
        let mut b = 4u32.to_le_bytes().to_vec();
        num(&mut b, 1.0);
        string(&mut b, "a");
        b.extend_from_slice(&1u32.to_le_bytes());
        b.push(1); // true, the same key as 1
        string(&mut b, "b");
        num(&mut b, f64::NAN);
        num(&mut b, 2.0);
        num(&mut b, f64::NAN);
        num(&mut b, 3.0);
        b.extend_from_slice(&[0; 16]);
        let (t, _) = pairs(&b, 0, 0).unwrap();
        assert_eq!(t.len(), 3);
        assert!(matches!(&t.pairs[0].1, Lua::Str(s) if s == "b"));
    }
}
