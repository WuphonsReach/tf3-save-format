//! mine-summary: print the JSON summary of one Transport Fever 3 save, the same as `tools/mine_summary.py`
//! writes it (schema v8). Reads the save and, for the vehicle classes, the game install's model files; writes
//! nothing but standard output. The Python is the reference; see README.md.

mod counts;
mod header;
mod journal;
mod json;
mod lua;
mod reader;
mod states;
mod stream;
mod summary;

use std::io::Write;
use std::path::PathBuf;
use std::process::ExitCode;

const USAGE: &str = "usage: mine-summary SAVE [--mod-id ID] [--kind KIND] [--game DIR]

Prints the summary of SAVE as JSON, as tools/mine_summary.py SAVE does.
  --mod-id ID   the mod.io id to write in `mod_id` (default null)
  --kind KIND   `kind`: savegame (default) or map
  --game DIR    the game install folder, for the vehicle model files (default: the usual Steam places)
  --version     print the version and the commit the summary records as `tools_commit`";

fn commit() -> Option<&'static str> {
    Some(env!("MINE_SUMMARY_COMMIT")).filter(|c| !c.is_empty())
}

fn main() -> ExitCode {
    let mut args = std::env::args().skip(1);
    let (mut save, mut mod_id, mut kind, mut game) = (
        None::<PathBuf>,
        None::<String>,
        "savegame".to_owned(),
        None::<PathBuf>,
    );
    while let Some(a) = args.next() {
        match a.as_str() {
            "--version" => {
                println!(
                    "mine-summary {} ({})",
                    env!("CARGO_PKG_VERSION"),
                    commit().unwrap_or("no commit")
                );
                return ExitCode::SUCCESS;
            }
            "-h" | "--help" => {
                println!("{USAGE}");
                return ExitCode::SUCCESS;
            }
            "--mod-id" | "--kind" | "--game" => {
                let Some(v) = args.next() else {
                    eprintln!("{a} needs a value\n{USAGE}");
                    return ExitCode::from(2);
                };
                match a.as_str() {
                    "--mod-id" => mod_id = Some(v),
                    "--kind" => kind = v,
                    _ => game = Some(v.into()),
                }
            }
            _ if save.is_none() && !a.starts_with("--") => save = Some(a.into()),
            _ => {
                eprintln!("{USAGE}");
                return ExitCode::from(2);
            }
        }
    }
    let Some(save) = save else {
        eprintln!("{USAGE}");
        return ExitCode::from(2);
    };
    let opts = summary::Options {
        mod_id: mod_id.as_deref(),
        kind: &kind,
        game_dir: game.as_deref(),
        tools_commit: commit(),
    };
    let text = json::to_string(&summary::summarise(&save, &opts));
    let mut out = std::io::stdout().lock();
    if writeln!(out, "{text}").and_then(|_| out.flush()).is_err() {
        return ExitCode::FAILURE;
    }
    ExitCode::SUCCESS
}
