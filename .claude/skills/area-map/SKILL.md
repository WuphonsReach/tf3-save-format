---
name: area-map
description: Draw a close map of a place in a save (200 to 500 m around a signal, station, junction, train or truck) with named rail and road segments and the vehicles near it, so the user and the session can point at the same thing. Use when the user asks "which segment", wants a place or a jam looked at, or when a test needs to know where a vehicle or an edge is.
---

# Area map: name the segment, show the vehicles

Why: "which road or rail segment are you talking about" keeps coming up. A picture with the segments and vehicles named settles it. The tools are `tools/terrain_map.py` (the picture) and `tools/model_instances.py` (the vehicle list); their rows in `tools/README.md` have every option. Rules in `CLAUDE.md` apply (no saves written, no paths or account-derived names in committed files).

## Names to use

- **A segment** is its two end node ids in hex, `2a619>342aa` (either order). Node ids are entity ids and every edge has both. An edge's own entity id is known only where the strip table has an entry (`--edge-ids`), so do not use it as the name.
- **A vehicle** is its model and slot (`class_prr_gg1`, slot 2258) until the user's number is known. Show default names short: `Road Vehicle 279` is `RV279`, `Train 58` `RR58`, `Ship 106` `S106`, `Tram 62` `TRM62`, `Aircraft 6` `AIR6` (`--name` does this by itself; other text stays as given).
- The slot is the vehicle's place in the stream's list of `vehicle/` instances. It is only good inside one save: another autosave of the same game moves it.

## Steps

1. **Find the place.** From a coordinate, a signal's edge (`street_edges.py SAVE --near X,Y,R` lists edges with node ids and positions) or a landmark. North is +x, east is -y, so west is +y and the picture has +x up.
2. **First pass: list, do not label.** `terrain_map.py OUT SAVE --crop X,Y,R --mpp 1 --zoom 3 --vehicles --grid 50`. It prints every vehicle drawn (slot, model, position, facing) and draws them unnamed. Use `--mpp 2` for R above about 300 m. For a close crop (R about 60 m) use `--grid 25`: a step under a fifth of the picture's width crowds the labels. One run is about a minute on a big save (it reads the whole stream), so do the choosing from the printed list and a quick look, not by re-running.
3. **Pick what to name.** `--label A>B` for the few edges worth talking about (a curve is many short chords; labelling all of them hides the picture). `--name SLOT="Train 18"` for vehicles. The user may not want a name shown (private cars, for example): leave it unnamed, it can be added later.
4. **Match a slot to the player's vehicle** only with evidence, and keep a `?` on the name until the user confirms. What worked: the user's in-game screenshots of the vehicle selected (read the PNGs from `~/Pictures/Screenshots`, newest by `ls -t`), then three checks together: the order of vehicles along the road or track, the lane side, and the facing (the triangle end of the shape is the front). Two vehicles of one model 80 m apart were told apart this way. A vehicle's number or entity id is not stored next to its position (docs/entity-names.md), so position alone does not name it. Do not write a person's name from a tooltip (private cars carry their owner's name) into any committed file; in your working output it is fine.
5. **Second pass with the names**, then look at the picture. Vehicle shapes are sized by class (the save holds no length), so do not read lengths off them.

## Reading the picture

Roads dark grey, rails red, grid labels `x` and `y` in map metres. Each vehicle is a pentagon whose pointed end is its front. Interior: train engine dark orange, trailing train car light orange, tram purple, truck dark blue, bus dark green, ship dark grey, car grey. Trains and trams have a mid-dark grey outline, the rest white. A truck's colour says nothing about its load (the save does not say).

## Where the output goes, and what stays out of git

- Pictures of a test map go to `local/games/<seed>-<climate>-<label>/maps/<topic>/` (gitignored; the folder rules are in `local/README.md`). Put the SVG there; it is the picture the user gets. Make no PNG unless the user asks for one. Name `<topic>` for the question (`skipton-train18-rv40-rv44`).
- Never commit a picture (`*.svg` is not ignored; keep them under `local/`) or a screenshot. Only the user's own saves; a catalog save's picture stays local too.
- A format fact learned from a map goes to `docs/` in our own words, tagged with the version, with a reference map cited by mod id.

## SVG first, PNG only on request

Give the user the SVG and tell them to open it in Firefox or Chrome (the vector layers stay sharp when zoomed, and the browser shows the data-URI terrain that other viewers drop). Do not write `--png`, and do not leave a PNG next to the SVG, unless the user asks for a PNG. An SVG is superior in most cases, so offer nothing else by default.

To check a picture yourself, the Read tool needs a raster. Take a headless browser screenshot into the scratchpad directory, not into `local/games/`, so it is not left for the user. The command: `firefox --headless --no-remote --profile DIR --window-size W,H --screenshot out.png file://…/map.svg`, where DIR is an empty profile folder the browser can write to (a snap-packaged Firefox cannot use `/tmp`; use a folder under its own `common` directory) and `W,H` are the SVG's width and height plus about 90 px. Look at it with the Read tool.

## Known limits

- Vehicles need `--crop`. A vehicle in a depot with no line has no instance and is not drawn.
- Only edges asked for get a label; there is no auto-label.
- `model_instances.py` can pick up a stray match in other data; the model id must be inside the table, which keeps it rare.
- Checked on 604 only (and rail edges on 568 to 604 in `docs/road-network.md`).
