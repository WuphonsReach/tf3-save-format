---
name: doc-review
description: Review pass over docs/ for this repo. Runs the lint, the glossary check and the index scripts, then opens only the lines they name. Use when the user asks for a documentation review, consistency pass or cleanup of the notes.
---

# Documentation review pass

The rules are in `CLAUDE.md`. This skill is the order that keeps a pass cheap: tools first, then the lines they name. Do not read whole notes. A pass that did cost over 350,000 tokens.

## 1. Lint

```
python3 -I tools/lint_docs.py                 # working tree
python3 -I tools/lint_docs.py --since REV     # a series of commits
```

Errors must reach 0. Warnings are leads:

- "`term` now in N notes": open the lines with `python3 -I tools/find_dupes.py --where TERM`. It is a duplicate only if the same fact is stated twice. A key used as a name (`cement_plant`, `small_*`) or one source file cited for two different facts is not.
- "A and B share ... and do not link each other": add a link only if one note relies on the other's fact. `glossary.md` shares keys with every note by design.
- "runs of wording in common": `find_dupes.py --prose`, then decide which note is the home.

Never reword only to make a warning go away.

## 2. Glossary

```
python3 -I tools/glossary_check.py            # aliases and labels, with suggested key
python3 -I tools/glossary_check.py --summary
```

For each lead, write the key in code font. Add the label in parentheses only where the note records what the screen showed (an Industries tab list, a window). Leave a lead alone when:

- it is a false positive: a verb ("the timer of the cargo stops"), or a word inside a longer name;
- the word could be two keys and the context does not settle it ("small pier": a landing or `HARBOR_SMALL`?; "stagecoach": `american_post_coach` or `droshky`?). Grep `local/games/` for the test log first, then ask the user. Do not guess.

`--ambiguous` returns hundreds of leads, mostly noise: "field" (a data field), and "stop", "station" and "depot" (words the notes define). Words inside a longer key or label ("sheet metal", "road stop") and words with their key beside them are already skipped. Narrow the run to the words that matter before reading:

```
python3 -I tools/glossary_check.py --ambiguous --word dock --word coach --word carriage --word cart --word wagon --word car --word engine --word oil --word ore --word grain --word food
```

## 3. Size and placement

```
python3 -I tools/facts_index.py                          # sizes, over-limit notes, long sections
python3 -I tools/facts_index.py --outline docs/NOTE.md   # headings with line numbers
python3 -I tools/facts_index.py --outline docs/NOTE.md --bullets   # plan a split
```

Open a section only when a tool names it.

## 4. Apply and check

- Make exact replacements with a small script in the scratchpad that asserts one match per edit, rather than `sed` over prose.
- Re-run step 1 and step 2. Lint must report 0 errors.
- Do not commit unless the user asks. Report what changed, what was left and why, and the questions that need the user.
- When the user corrects a word, add it to `docs/glossary.md`.
