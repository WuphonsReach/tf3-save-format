//! Just enough of the zip format to read text files out of the game's
//! content archives: the central directory, and entries stored without
//! compression (the game stores its scripts and model files that way).
//! An archive is read in place with seeks; nothing is extracted to disk.
//!
//! Copied unchanged from tf3-save-mapper's `crates/tf3-save-mapper-core/src/zip.rs` at commit bfe77c7 (same
//! author, MIT OR Apache-2.0).

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read, Seek, SeekFrom};
use std::path::Path;

const END_SIGNATURE: u32 = 0x0605_4b50;
const ENTRY_SIGNATURE: u32 = 0x0201_4b50;
const LOCAL_SIGNATURE: u32 = 0x0403_4b50;
/// The end record is 22 bytes and its comment at most 65535.
const END_REACH: u64 = 22 + 65_535;
/// No text file we read is near this size.
const MAX_ENTRY: u32 = 64 << 20;

struct Entry {
    method: u16,
    flags: u16,
    size: u32,
    local_header: u32,
}

pub struct Archive {
    file: File,
    entries: HashMap<String, Entry>,
    /// Entry names in directory order.
    names: Vec<String>,
}

fn u16_at(b: &[u8], at: usize) -> u16 {
    u16::from_le_bytes([b[at], b[at + 1]])
}

fn u32_at(b: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(b[at..at + 4].try_into().unwrap())
}

fn bad(what: &str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, what.to_owned())
}

impl Archive {
    pub fn open(path: &Path) -> io::Result<Archive> {
        let mut file = File::open(path)?;
        let len = file.seek(SeekFrom::End(0))?;
        let reach = len.min(END_REACH);
        file.seek(SeekFrom::Start(len - reach))?;
        let mut tail = vec![0; reach as usize];
        file.read_exact(&mut tail)?;
        let end = (0..tail.len().saturating_sub(21))
            .rev()
            .find(|&i| u32_at(&tail, i) == END_SIGNATURE)
            .ok_or_else(|| bad("no zip end record"))?;
        let (count, size, offset) = (
            u16_at(&tail, end + 10),
            u32_at(&tail, end + 12),
            u32_at(&tail, end + 16),
        );
        if count == u16::MAX || size == u32::MAX || offset == u32::MAX {
            return Err(bad("zip64 archives are not read"));
        }
        if u64::from(offset) + u64::from(size) > len {
            return Err(bad("zip directory lies outside the file"));
        }
        file.seek(SeekFrom::Start(u64::from(offset)))?;
        let mut dir = vec![0; size as usize];
        file.read_exact(&mut dir)?;
        let mut entries = HashMap::new();
        let mut names = Vec::new();
        let mut p = 0;
        for _ in 0..count {
            if p + 46 > dir.len() || u32_at(&dir, p) != ENTRY_SIGNATURE {
                return Err(bad("broken zip directory"));
            }
            let name_len = usize::from(u16_at(&dir, p + 28));
            let extra_len = usize::from(u16_at(&dir, p + 30));
            let comment_len = usize::from(u16_at(&dir, p + 32));
            let name_bytes = dir
                .get(p + 46..p + 46 + name_len)
                .ok_or_else(|| bad("broken zip directory"))?;
            let name = String::from_utf8_lossy(name_bytes).into_owned();
            entries.insert(
                name.clone(),
                Entry {
                    flags: u16_at(&dir, p + 8),
                    method: u16_at(&dir, p + 10),
                    size: u32_at(&dir, p + 20),
                    local_header: u32_at(&dir, p + 42),
                },
            );
            names.push(name);
            p += 46 + name_len + extra_len + comment_len;
        }
        Ok(Archive {
            file,
            entries,
            names,
        })
    }

    pub fn names(&self) -> &[String] {
        &self.names
    }

    pub fn contains(&self, name: &str) -> bool {
        self.entries.contains_key(name)
    }

    /// The entry's text, or `None` when it is missing, compressed, encrypted
    /// or unreadable. Bytes that are not UTF-8 are replaced.
    pub fn read_text(&mut self, name: &str) -> Option<String> {
        let e = self.entries.get(name)?;
        // Method 0 is stored; bit 0 of the flags is encryption.
        if e.method != 0 || e.flags & 1 != 0 || e.size > MAX_ENTRY || e.size == u32::MAX {
            return None;
        }
        let (size, at) = (e.size, u64::from(e.local_header));
        let mut local = [0u8; 30];
        self.file.seek(SeekFrom::Start(at)).ok()?;
        self.file.read_exact(&mut local).ok()?;
        if u32_at(&local, 0) != LOCAL_SIGNATURE {
            return None;
        }
        let skip = u64::from(u16_at(&local, 26)) + u64::from(u16_at(&local, 28));
        self.file.seek(SeekFrom::Start(at + 30 + skip)).ok()?;
        let mut data = vec![0; size as usize];
        self.file.read_exact(&mut data).ok()?;
        Some(String::from_utf8_lossy(&data).into_owned())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A zip with stored entries, built by hand.
    fn build(entries: &[(&str, &[u8], u16)]) -> Vec<u8> {
        let mut out = Vec::new();
        let mut dir = Vec::new();
        for (name, data, method) in entries {
            let at = out.len() as u32;
            out.extend_from_slice(&LOCAL_SIGNATURE.to_le_bytes());
            out.extend_from_slice(&[20, 0, 0, 0]);
            out.extend_from_slice(&method.to_le_bytes());
            out.extend_from_slice(&[0; 8]); // time, date, crc
            out.extend_from_slice(&(data.len() as u32).to_le_bytes());
            out.extend_from_slice(&(data.len() as u32).to_le_bytes());
            out.extend_from_slice(&(name.len() as u16).to_le_bytes());
            out.extend_from_slice(&3u16.to_le_bytes()); // extra
            out.extend_from_slice(name.as_bytes());
            out.extend_from_slice(&[0xee; 3]);
            out.extend_from_slice(data);

            dir.extend_from_slice(&ENTRY_SIGNATURE.to_le_bytes());
            dir.extend_from_slice(&[20, 0, 20, 0, 0, 0]);
            dir.extend_from_slice(&method.to_le_bytes());
            dir.extend_from_slice(&[0; 8]);
            dir.extend_from_slice(&(data.len() as u32).to_le_bytes());
            dir.extend_from_slice(&(data.len() as u32).to_le_bytes());
            dir.extend_from_slice(&(name.len() as u16).to_le_bytes());
            dir.extend_from_slice(&[0; 2 + 2 + 2 + 2 + 4]);
            dir.extend_from_slice(&at.to_le_bytes());
            dir.extend_from_slice(name.as_bytes());
        }
        let offset = out.len() as u32;
        out.extend_from_slice(&dir);
        out.extend_from_slice(&END_SIGNATURE.to_le_bytes());
        out.extend_from_slice(&[0; 4]);
        out.extend_from_slice(&(entries.len() as u16).to_le_bytes());
        out.extend_from_slice(&(entries.len() as u16).to_le_bytes());
        out.extend_from_slice(&(dir.len() as u32).to_le_bytes());
        out.extend_from_slice(&offset.to_le_bytes());
        out.extend_from_slice(&[0; 2]);
        out
    }

    #[test]
    fn stored_entries_read_and_compressed_ones_do_not() {
        let dir = std::env::temp_dir().join(format!("tf3map-zip-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("a.zip");
        std::fs::write(
            &path,
            build(&[("x/a.lua", b"return 1", 0), ("x/b.lua", b"packed", 8)]),
        )
        .unwrap();
        let mut zip = Archive::open(&path).unwrap();
        assert_eq!(zip.names(), ["x/a.lua", "x/b.lua"]);
        assert_eq!(zip.read_text("x/a.lua").as_deref(), Some("return 1"));
        assert_eq!(zip.read_text("x/b.lua"), None);
        assert_eq!(zip.read_text("x/c.lua"), None);
        std::fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn a_directory_that_lies_outside_the_file_is_refused() {
        let dir = std::env::temp_dir().join(format!("tf3map-zip-big-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("a.zip");
        // Only an end record, claiming a 4 GB directory.
        let mut end = END_SIGNATURE.to_le_bytes().to_vec();
        end.extend_from_slice(&[0; 4]);
        end.extend_from_slice(&1u16.to_le_bytes());
        end.extend_from_slice(&1u16.to_le_bytes());
        end.extend_from_slice(&0xFFFF_FF00u32.to_le_bytes());
        end.extend_from_slice(&0u32.to_le_bytes());
        end.extend_from_slice(&[0; 2]);
        std::fs::write(&path, &end).unwrap();
        let err = Archive::open(&path).err().unwrap();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        std::fs::remove_dir_all(&dir).unwrap();
    }
}
