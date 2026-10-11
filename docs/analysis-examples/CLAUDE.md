# docs/analysis-examples

Goal: test whether the repo's notes and tools can support a player-style analysis ("where are the bottlenecks on this line?"), and record where they cannot. The root `CLAUDE.md` rules still apply; this file adds what is specific to this folder.

## File names

`<line or topic>-<what it shows>-<mod.io id>.md`, lower case, hyphens. The suffix is the numeric mod.io id of the catalog save the example was read from, since a downloaded save has no name of ours. Example: `clothes-train2-supply-chain-starvation-6425796.md`. For a save of our own, use its game folder label (see `local/games/`) in place of the id.

## What each example holds

- The question as the player asked it, and the figures it started from.
- The method, step by step, each step linking the note that holds the underlying fact.
- What the lists or records said, with Confirmed, Observed or Open and the format version.
- A "Does the repo support this?" table: each need, where the repo covers it, and Supported, Gap or Not tried. A gap is a result, not a failure. Add rows to the table rather than hiding a step that needed a private or throwaway script.
- What the method cannot tell.

## Rules

- Each fact has one home note; link to it and do not restate it. An example adds only the worked reading and the verdict.
- Cite a catalog save by mod id and URL. Record counts and figures read from it, not a dump of the save.
- Give a clock value, not a date, once a save's calendar is stopped ([../calendar.md](../calendar.md#the-day-table)).
- Never write an account name, company name or install path (see the root rules).
- A new example gets a row in `docs/README.md` ("Covers" says what it tests, not only its topic). Run `python3 -I tools/lint_docs.py` before committing.
- A step that only a `local/` or scratchpad script could do goes in the support table as a gap; once the script is promoted to `tools/` (with a row in `tools/README.md`), mark the row Supported.
