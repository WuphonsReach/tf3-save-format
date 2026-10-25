//! Readers copied from tf3-save-mapper's core crate (same author, MIT OR Apache-2.0), kept apart from the
//! summary code so the folder can be swapped for a shared crate later. Each file names its origin.

pub mod container;
pub mod instances;
// The mapper's archive reader, whole; the summary does not list or test entries.
#[allow(dead_code)]
pub mod zip;
