//! The free-id list (`docs/town-leftovers.md`), as `street_edges.read_free_ids` reads it: a `vec<u32>` near the
//! end of the stream, followed by u32 2, a u32 and a short `str` of digits. Its longest ascending stretch of
//! small values (in the stream's last `TAIL` bytes, at any 4-byte alignment) lies inside the list, mostly at its
//! end. The list ends at the first such trailer from the run's end on, and the count word is the word before the
//! run that reaches that trailer exactly; a candidate with an id twice is not taken.

use std::collections::HashSet;

/// The list sits within the last few megabytes (its end at most 2.3 MB from the stream's end).
const TAIL: usize = 4_000_000;
/// Shortest ascending run taken for the list's sorted part.
const MIN_RUN: usize = 1000;
/// An id is below this (`street_edges.MAX_ID`).
const MAX_ID: u32 = 1 << 24;

/// The free entity ids, or None when no list is found.
pub fn read_free_ids(data: &[u8]) -> Option<HashSet<u32>> {
    let tail = &data[data.len().saturating_sub(TAIL)..];
    for al in 0..4usize.min(tail.len()) {
        let words: Vec<u32> = tail[al..]
            .as_chunks::<4>()
            .0
            .iter()
            .map(|b| u32::from_le_bytes(*b))
            .collect();
        let mut best: Option<(usize, usize)> = None; // (length, start) of the longest ascending run
        let mut start = 0;
        for i in 1..=words.len() {
            if i == words.len() || words[i] <= words[i - 1] || words[i] >= MAX_ID {
                if i - start >= MIN_RUN
                    && words[start] < MAX_ID
                    && best.is_none_or(|(n, _)| i - start > n)
                {
                    best = Some((i - start, start));
                }
                start = i;
            }
        }
        let Some((n, s)) = best else {
            continue;
        };
        for j in s + n..words.len().saturating_sub(3) {
            // the trailer: 2, a u32, a `str` of digits
            if words[j] != 2 || !(1..=32).contains(&words[j + 2]) {
                continue;
            }
            let p = al + 4 * (j + 3);
            let digits = &tail[p.min(tail.len())..(p + words[j + 2] as usize).min(tail.len())];
            if digits.is_empty() || !digits.iter().all(u8::is_ascii_digit) {
                continue;
            }
            for i in (0..s).rev() {
                // the count word: i + 1 + count is the trailer
                if i as u64 + 1 + u64::from(words[i]) != j as u64 {
                    continue;
                }
                let ids: HashSet<u32> = words[i + 1..j].iter().copied().collect();
                if ids.len() == words[i] as usize && ids.iter().all(|&x| x < MAX_ID) {
                    return Some(ids);
                }
            }
        }
    }
    None
}
