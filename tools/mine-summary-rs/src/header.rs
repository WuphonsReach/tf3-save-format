//! The header at the start of the stream (`docs/header.md`), read in full as `save_header.py` does.
//!
//! The read order follows `save_header.py`, which was ported from tf3-save-editor (`crates/lib/src/header.rs`,
//! https://github.com/TBK/tf3-save-editor, Copyright (c) 2026 TBK, MIT OR Apache-2.0; see THIRD_PARTY_NOTICES.md).
//! Formats 568 and 585 differ after the preview; there the tail does not read and `partial` says why, in the
//! words the Python uses (`EOFError: need 4 bytes at 123`, `ValueError: lua tag 7 at 123`).

/// A header value: the Lua encoding, with tables kept as lists of pairs (the header reader does not merge keys).
#[derive(Debug, Clone)]
pub enum HVal {
    Nil,
    Bool(bool),
    Num(f64),
    Str(String),
    List(Vec<(HVal, HVal)>),
}

#[derive(Debug, Default)]
pub struct Header {
    pub version: u32,
    pub start_year: u32,
    pub map_w_m: u32,
    pub map_h_m: u32,
    pub money: i64,
    pub counter: u32,
    pub mods: Vec<String>,
    /// Why the tail did not read, or `None`.
    pub partial: Option<String>,
    /// Filled in as far as the tail read, as the Python's dict is.
    pub resources: Option<Vec<(String, String)>>,
    pub first_version: Option<u32>,
    pub map_seed: Option<String>,
    /// The flattened New Game settings (`params` entry with the empty name); empty unless the tail read.
    pub settings: Vec<(String, HVal)>,
    pub stream_len: usize,
}

struct R<'a> {
    d: &'a [u8],
    p: usize,
}

type Res<T> = Result<T, String>;

impl<'a> R<'a> {
    fn take(&mut self, n: usize) -> Res<&'a [u8]> {
        if self.p + n > self.d.len() {
            return Err(format!("EOFError: need {n} bytes at {}", self.p));
        }
        let b = &self.d[self.p..self.p + n];
        self.p += n;
        Ok(b)
    }
    fn u8(&mut self) -> Res<u8> {
        Ok(self.take(1)?[0])
    }
    fn u32(&mut self) -> Res<u32> {
        Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn i64(&mut self) -> Res<i64> {
        Ok(i64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn f64(&mut self) -> Res<f64> {
        Ok(f64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn string(&mut self) -> Res<String> {
        let n = self.u32()? as usize;
        Ok(String::from_utf8_lossy(self.take(n)?).into_owned())
    }
    fn value(&mut self) -> Res<HVal> {
        let tag = self.u32()?;
        Ok(match tag {
            0 => HVal::Nil,
            1 => HVal::Bool(self.u8()? != 0),
            2 => HVal::Num(self.f64()?),
            3 => HVal::Str(self.string()?),
            4 => {
                if self.u8()? != 0 {
                    HVal::List(self.table()?)
                } else {
                    HVal::Nil
                }
            }
            _ => return Err(format!("ValueError: lua tag {tag} at {}", self.p - 4)),
        })
    }
    fn table(&mut self) -> Res<Vec<(HVal, HVal)>> {
        let n = self.u32()?;
        let mut out = Vec::new();
        for _ in 0..n {
            let k = self.value()?;
            let v = self.value()?;
            out.push((k, v));
        }
        Ok(out)
    }
}

/// How Python's `str()` writes a key when it is put in front of a nested key (`f"{prefix}{k}"`).
fn key_str(k: &HVal) -> String {
    match k {
        HVal::Nil => "None".into(),
        HVal::Bool(b) => if *b { "True" } else { "False" }.into(),
        HVal::Num(x) => {
            let r = crate::json::float_repr(*x);
            match r.as_str() {
                "NaN" => "nan".into(),
                "Infinity" => "inf".into(),
                "-Infinity" => "-inf".into(),
                _ => r,
            }
        }
        HVal::Str(s) => s.clone(),
        HVal::List(l) => {
            // str() of a list of tuples; not met in a save, written for completeness.
            format!("[{} pairs]", l.len())
        }
    }
}

fn flatten(t: &[(HVal, HVal)], prefix: &str, out: &mut Vec<(String, HVal)>) {
    for (k, v) in t {
        let key = format!("{prefix}{}", key_str(k));
        if let HVal::List(inner) = v {
            flatten(inner, &format!("{key}."), out);
        } else {
            match out.iter_mut().find(|(k2, _)| *k2 == key) {
                Some(slot) => slot.1 = v.clone(),
                None => out.push((key, v.clone())),
            }
        }
    }
}

/// Read the header. An error before the end of the preview ends the summary (`Err` holds the message);
/// one after it is recorded in `partial`.
pub fn read_header(data: &[u8]) -> Res<Header> {
    let mut r = R { d: data, p: 0 };
    if r.take(4)? != b"tf**" {
        return Err("ValueError: not a tf** save".into());
    }
    let mut h = Header {
        version: r.u32()?,
        start_year: r.u32()?,
        map_w_m: r.u32()?,
        map_h_m: r.u32()?,
        ..Header::default()
    };
    let _game_date = r.u32()?;
    h.money = r.i64()?;
    h.counter = r.u32()?;
    r.table()?; // info
    for _ in 0..r.u32()? {
        let id = r.string()?;
        for _ in 0..4 {
            r.string()?; // source, path, name, extra
        }
        r.u32()?; // flags
        h.mods.push(id);
    }
    r.u8()?; // flag before the preview
    r.u32()?;
    r.u32()?; // preview width and height
    let n = r.u32()? as usize;
    r.take(n)?;
    if let Err(e) = read_tail(&mut r, &mut h) {
        h.partial = Some(e);
    }
    h.stream_len = data.len();
    Ok(h)
}

fn read_tail(r: &mut R, h: &mut Header) -> Res<()> {
    for _ in 0..6 {
        r.i64()?;
    }
    for _ in 0..11 {
        r.u32()?;
    }
    for _ in 0..r.u32()? {
        r.u32()?;
        r.u32()?;
    }
    r.u32()?;
    r.u32()?;
    for _ in 0..9 {
        r.i64()?;
    }
    r.u32()?;
    r.u32()?;
    for _ in 0..r.u32()? {
        r.string()?;
        r.u32()?;
    } // labels
    r.u32()?;
    r.i64()?;
    r.i64()?;
    r.u32()?;
    for _ in 0..r.u32()? {
        r.string()?; // config mods
    }
    let mut resources = Vec::new();
    for _ in 0..r.u32()? {
        let k = r.string()?;
        let v = r.string()?;
        resources.push((k, v));
    }
    h.resources = Some(resources);
    let mut params = Vec::new();
    for _ in 0..r.u32()? {
        let k = r.string()?;
        let t = r.table()?;
        params.push((k, t));
    }
    r.string()?; // mission
    r.string()?; // kind
    r.u8()?; // flag
    h.first_version = Some(r.u32()?);
    h.map_seed = Some(r.string()?);
    if let Some((_, t)) = params.iter().find(|(k, _)| k.is_empty()) {
        flatten(t, "", &mut h.settings);
    }
    Ok(())
}
