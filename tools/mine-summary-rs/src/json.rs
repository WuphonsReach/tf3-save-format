//! A JSON value and a writer that lays it out as Python's `json.dump(..., indent=2, ensure_ascii=False)` does,
//! so the summary is the same text as the Python one: two-space indent, `", "`-free item separators, `{}` and
//! `[]` for empty containers, floats as Python's `repr`, NaN and infinities as `NaN`, `Infinity`, `-Infinity`.

use std::fmt::Write;

#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i128),
    /// A whole number too large for `Int`, already written out in decimal.
    BigInt(String),
    Float(f64),
    Str(String),
    List(Vec<Value>),
    /// Keys in the order written.
    Obj(Vec<(String, Value)>),
}

impl Value {
    pub fn str(s: impl Into<String>) -> Value {
        Value::Str(s.into())
    }

    pub fn opt<T: Into<Value>>(v: Option<T>) -> Value {
        v.map_or(Value::Null, Into::into)
    }
}

impl From<i64> for Value {
    fn from(v: i64) -> Self {
        Value::Int(v.into())
    }
}
impl From<u64> for Value {
    fn from(v: u64) -> Self {
        Value::Int(v.into())
    }
}
impl From<u32> for Value {
    fn from(v: u32) -> Self {
        Value::Int(v.into())
    }
}
impl From<usize> for Value {
    fn from(v: usize) -> Self {
        Value::Int(v as i128)
    }
}
impl From<i128> for Value {
    fn from(v: i128) -> Self {
        Value::Int(v)
    }
}
impl From<bool> for Value {
    fn from(v: bool) -> Self {
        Value::Bool(v)
    }
}
impl From<String> for Value {
    fn from(v: String) -> Self {
        Value::Str(v)
    }
}
impl From<&str> for Value {
    fn from(v: &str) -> Self {
        Value::Str(v.to_owned())
    }
}

/// An object built key by key; a key written twice keeps its first place and takes the later value, as a
/// Python dict does.
#[derive(Debug, Default, Clone)]
pub struct Obj(pub Vec<(String, Value)>);

impl Obj {
    pub fn new() -> Self {
        Obj(Vec::new())
    }

    pub fn set(&mut self, key: impl Into<String>, value: impl Into<Value>) {
        let key = key.into();
        let value = value.into();
        match self.0.iter_mut().find(|(k, _)| *k == key) {
            Some(slot) => slot.1 = value,
            None => self.0.push((key, value)),
        }
    }

    pub fn get_mut(&mut self, key: &str) -> Option<&mut Value> {
        self.0.iter_mut().find(|(k, _)| k == key).map(|(_, v)| v)
    }
}

impl From<Obj> for Value {
    fn from(o: Obj) -> Self {
        Value::Obj(o.0)
    }
}

/// Python's `repr` of a float: the shortest digits that read back the same, in fixed notation when the
/// decimal point falls within 16 places of the first digit and from -4, else as `1e-05`, `1.5e+16`.
pub fn float_repr(x: f64) -> String {
    if x.is_nan() {
        return "NaN".into();
    }
    if x.is_infinite() {
        return if x > 0.0 { "Infinity" } else { "-Infinity" }.into();
    }
    if x == 0.0 {
        return if x.is_sign_negative() { "-0.0" } else { "0.0" }.into();
    }
    // Rust's `{:e}` gives the shortest round-trip digits, as `-1.2345e-7`.
    let e = format!("{:e}", x.abs());
    let (mant, exp) = e.split_once('e').unwrap();
    let exp: i32 = exp.parse().unwrap();
    let digits: String = mant.chars().filter(|c| *c != '.').collect();
    let decpt = exp + 1; // the value is 0.DIGITS x 10^decpt
    let mut out = String::new();
    if x < 0.0 {
        out.push('-');
    }
    if decpt <= -4 || decpt > 16 {
        out.push_str(&digits[..1]);
        if digits.len() > 1 {
            out.push('.');
            out.push_str(&digits[1..]);
        }
        let _ = write!(out, "e{}{:02}", if exp < 0 { '-' } else { '+' }, exp.abs());
    } else if decpt <= 0 {
        out.push_str("0.");
        for _ in 0..-decpt {
            out.push('0');
        }
        out.push_str(&digits);
    } else {
        let d = decpt as usize;
        if digits.len() <= d {
            out.push_str(&digits);
            for _ in digits.len()..d {
                out.push('0');
            }
            out.push_str(".0");
        } else {
            out.push_str(&digits[..d]);
            out.push('.');
            out.push_str(&digits[d..]);
        }
    }
    out
}

/// A whole float as Python's `int(x)` gives it (exact, however large). `x` must be finite and whole.
pub fn whole_float(x: f64) -> Value {
    if x.abs() < 1e36 {
        return Value::Int(x as i128);
    }
    // mantissa x 2^exp, written out with base-10^9 limbs.
    let bits = x.abs().to_bits();
    let exp = ((bits >> 52) & 0x7ff) as i32 - 1075;
    let mant = (bits & ((1 << 52) - 1)) | (1 << 52);
    let mut limbs: Vec<u64> = vec![
        mant % 1_000_000_000,
        mant / 1_000_000_000 % 1_000_000_000,
        mant / 1_000_000_000_000_000_000,
    ];
    for _ in 0..exp {
        let mut carry = 0;
        for l in limbs.iter_mut() {
            let v = *l * 2 + carry;
            *l = v % 1_000_000_000;
            carry = v / 1_000_000_000;
        }
        if carry > 0 {
            limbs.push(carry);
        }
    }
    while limbs.len() > 1 && *limbs.last().unwrap() == 0 {
        limbs.pop();
    }
    let mut s = String::new();
    if x < 0.0 {
        s.push('-');
    }
    let _ = write!(s, "{}", limbs.last().unwrap());
    for l in limbs.iter().rev().skip(1) {
        let _ = write!(s, "{l:09}");
    }
    Value::BigInt(s)
}

fn write_str(out: &mut String, s: &str) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{8}' => out.push_str("\\b"),
            '\u{c}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

fn indent(out: &mut String, level: usize) {
    out.push('\n');
    for _ in 0..level {
        out.push_str("  ");
    }
}

fn write_value(out: &mut String, v: &Value, level: usize) {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Int(i) => {
            let _ = write!(out, "{i}");
        }
        Value::BigInt(s) => out.push_str(s),
        Value::Float(f) => out.push_str(&float_repr(*f)),
        Value::Str(s) => write_str(out, s),
        Value::List(items) => {
            if items.is_empty() {
                out.push_str("[]");
                return;
            }
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                indent(out, level + 1);
                write_value(out, item, level + 1);
            }
            indent(out, level);
            out.push(']');
        }
        Value::Obj(items) => {
            if items.is_empty() {
                out.push_str("{}");
                return;
            }
            out.push('{');
            for (i, (k, item)) in items.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                indent(out, level + 1);
                write_str(out, k);
                out.push_str(": ");
                write_value(out, item, level + 1);
            }
            indent(out, level);
            out.push('}');
        }
    }
}

/// The value as Python's `json.dump(v, indent=2, ensure_ascii=False)` writes it (no final newline).
pub fn to_string(v: &Value) -> String {
    let mut out = String::new();
    write_value(&mut out, v, 0);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn floats_read_as_python_repr() {
        for (x, s) in [
            (1.0, "1.0"),
            (0.1, "0.1"),
            (1e16, "1e+16"),
            (1e15, "1000000000000000.0"),
            (123456789012345680.0, "1.2345678901234568e+17"),
            (0.0001, "0.0001"),
            (0.00001, "1e-05"),
            (1.5e-7, "1.5e-07"),
            (-2.5, "-2.5"),
            (1e300, "1e+300"),
            (0.05000000074505806, "0.05000000074505806"),
        ] {
            assert_eq!(float_repr(x), s, "{x}");
        }
    }

    #[test]
    fn large_whole_floats_are_exact() {
        assert_eq!(whole_float(1e20), Value::Int(100_000_000_000_000_000_000));
        assert_eq!(
            whole_float(1e40),
            Value::BigInt("10000000000000000303786028427003666890752".into())
        );
    }

    #[test]
    fn layout_follows_python_indent_2() {
        let v = Value::Obj(vec![
            (
                "a".into(),
                Value::List(vec![Value::Int(1), Value::str("x\"\u{1}é")]),
            ),
            ("b".into(), Value::Obj(vec![])),
            ("c".into(), Value::List(vec![])),
        ]);
        assert_eq!(
            to_string(&v),
            "{\n  \"a\": [\n    1,\n    \"x\\\"\\u0001é\"\n  ],\n  \"b\": {},\n  \"c\": []\n}"
        );
    }
}
