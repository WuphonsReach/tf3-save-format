---
name: shot-place
description: Work out where in a save a screenshot of the game was taken (view centre, heading, scale), using the vehicles it shows. Use when a task needs a picture tied to a place on the map ("where is this shot", "which edge or building is that", measuring something from a picture such as a depot's ring), usually after the screenshot index has found the picture.
---

# Placing a screenshot on the map

The save has no camera. The game shows the player no x/y. So the place is found by pairing what the picture shows with what the save holds, and the user's hint ("near the road depot", "SSE of that landmark on the map you showed me") narrows where to look. Tool: `tools/shot_place.py` (usage in its docstring and `tools/README.md`). It needs numpy and Pillow.

## Steps

1. **Find the picture and the save.** `.claude/skills/screenshot-index/SKILL.md` (the index of the user's shots, their UTC times and the saves written around them). The save must hold the game as it was in the picture: a paused game keeps every vehicle where it stood, so an autosave of the same game date works; a game that ran on does not (the vehicles moved).
2. **Get a hint.** Ask for it in the user's words if the index and the cluster note do not give one. Turn it into map metres with a drawn map of the area (`terrain_map.py --crop X,Y,R`, with `--depots --stations` and named things, as in `.claude/skills/area-map/SKILL.md`) and a radius of 500 to 1000 m. A named object (a depot, a station) gives its position from `model_instances.py` or `terrain_map.py --depots`.
3. **Read the vehicles off the picture.** Open a crop of the full-size picture (never judge from a thumbnail) and write down the centre pixel of two or more vehicles, and the direction of the long axis if clear (degrees anticlockwise from screen-right). Ships are the best choice: they sit at water level, which is the one height the fit is exact at, and a ship's heading is stored. Name every ship in the picture (the script penalises a save vehicle that would be in the frame but is not named). Trains and trucks work with `--class vehicle/` or a longer prefix, but their wagons look alike, so name more of them.
4. **Run it** with `--hint`, `--vehicle` (twice or more), `--out` under `local/games/<game>/maps/<topic>/`. Read the ranking: a first row far ahead of the second (the `margin` line) is a placement; close scores mean the picture does not decide, so name another vehicle or add `--in-frame` for a point that must be visible. A hint that is wrong gives no pairing at all.
5. **Check the blend** (`...-blend.png`, 4K crop to read it): the shore, docks and bridge stubs should lie on the picture's. Roads and rails on a viaduct or embankment, roofs and hills will be off, by about their height times the tangent of the camera pitch (the fit is a plane at water level), so judge by the coastline and things at the water. The map draws a road end with a round cap where the game ends it flat.
6. **Use the result.** `--pixel PX,PY` gives the map point under a pixel on the water plane (good to a few metres at the water's edge, worse higher up). The JSON has the view centre, corners, scale and homography. For a zoomed shot of the same place, the establishing shot's view centre is the next shot's hint.

## Limits and rules

- The coastline step is tuned on one temperate daytime picture (a dark blue-green water colour). At night, in another climate or with an overlay layer on, check the water mask before trusting the refinement; `--no-refine` keeps the plain similarity from the vehicles.
- Building and industry footprints on the map are approximations, not metre-exact; do not judge a fit by them. The ship depot's drawn outline is the best current guess of its in-game one.
- Cite no company names, paths or account folders in anything committed; the shots show them.
- Pictures go to `local/` (no permission needed); only a picture the user asks for goes to `docs/images/`.
