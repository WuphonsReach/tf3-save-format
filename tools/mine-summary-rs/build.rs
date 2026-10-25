//! Puts the commit that last changed this crate into the summary's `tools_commit` and into `--version`, the way
//! `mine_summary.py` names the last commit of its own import closure. "-dirty" is added when a tracked file of
//! the crate has uncommitted changes. Without git (a source archive) the commit is empty and the summary writes
//! null. Adapted from the build script of tf3-save-mapper (same author and licence).

use std::process::Command;

fn git(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    out.status
        .success()
        .then(|| String::from_utf8_lossy(&out.stdout).trim().to_owned())
        .filter(|s| !s.is_empty())
}

fn main() {
    let commit = git(&["log", "-1", "--format=%h", "--abbrev=7", "--", "."]).map(|commit| {
        let dirty = git(&["status", "--porcelain", "--untracked-files=no", "--", "."]).is_some();
        if dirty {
            format!("{commit}-dirty")
        } else {
            commit
        }
    });
    println!(
        "cargo:rustc-env=MINE_SUMMARY_COMMIT={}",
        commit.unwrap_or_default()
    );
    if let Some(dir) = git(&["rev-parse", "--absolute-git-dir"]) {
        println!("cargo:rerun-if-changed={dir}/HEAD");
        println!("cargo:rerun-if-changed={dir}/index");
    }
    println!("cargo:rerun-if-changed=src");
    println!("cargo:rerun-if-changed=Cargo.toml");
    println!("cargo:rerun-if-changed=build.rs");
}
