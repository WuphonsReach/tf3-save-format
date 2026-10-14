# Town centre

Where a town's centre is. The save does not store it ([town-records.md](town-records.md) has no position, and no other record found carries one), so the only measure that has worked is the town's name label on the game screen. This note holds how that measure is taken, what the label's offset from the centre is, and the centres it gave. The street clusters' own centres, which did not match, are in [town-boundaries.md](town-boundaries.md).

Everything here is **Observed** (seen in test pictures, not confirmed by a second route; the labels are defined in [README.md](README.md)) and was seen on 604.

## The label hangs a fixed distance above the centre (Observed, 604, four towns in three games)

**Method.** Take a series of pictures of one town with the camera turned round it, looking nearly straight down, the label visible in each. In every picture find the label's box (a dark rounded rectangle with the name, the population and cargo icons) and register the picture to the save's street edges: rotation, scale, shift, and a small perspective term for the camera's tilt. Carry the label's anchor point into map metres. The anchors of one series lie on a circle, and the circle's centre is the town's centre. The street edges place each picture on the map without knowing the camera's heading, so the series needs no fixed north.

**The offset.** The label's bottom edge sits about 17 m (16.6 to 17.2) from the centre, in the direction that is up in the picture, on the ground plane. Measured from the box's top edge the distance grows with the zoom, because the box is a fixed number of pixels tall at these zoom levels and the distance in metres is not.

| Town (game) | Pictures | Zoom (px per m) | Top edge to centre (px) | Bottom edge to centre (px, m) | Circle misfit (rms) |
|---|---|---|---|---|---|
| Chagford (Giant temperate game, 34 towns) | 10 | 1.4 | 58 | 24, 17.2 | 0.3 m |
| NTC Town (Tiny 1 : 3 flat editor map, played) | 12 | 1.8 to 2.1 | 64 to 76 | 26 to 37, 16.6 | 0.9 m |
| HCM City (the same map) | 8 of 9 | 2.1 | 70 to 79 | 31 to 39, 17.2 | 1.7 m |

Inside the NTC series the zoom changed from 2.1 to 1.8 pixels per metre part-way and the pixel distance followed it, which a distance in metres does and a fixed pixel offset does not. The ninth HCM picture was a strongly tilted one the fit could not place.

**Centres found** (game frame, x east and y north, metres; error 3 to 5 m, from comparing the fits below):

| Town | x | y |
|---|---|---|
| Chagford | 7744 | -8544 |
| NTC Town | -189 | -2378 |
| HCM City | -29 | 1923 |
| Nagoya (a second Tiny 1 : 3 flat editor map, three towns, the save made after the third was added) | -426 | 355 |

**Against the streets.** Using the town streets within 500 m, the mean of the street-node positions lies 45 to 56 m from these centres, the middle of the streets' bounding box 45 to 86 m, and the mean of the four-edge nodes 100 to 124 m. None of the three tracks the label point.

## Tilt and camera slips (Observed, 604)

The camera tilts a little as it turns and was sometimes nudged. The registration fits a perspective term per picture, and the pitch it implies was 3 to 22 degrees in the three near-top-down series. There the distance stays constant to within a metre or two, and a first fit that ignored tilt put Chagford's centre 3 m from the fit with tilt.

Strongly tilted pictures break the constant distance. Nagoya's pictures run from about 16 to 43 degrees of pitch (read from the fitted transform, so rough), and there the label's ground position moves 20 to 50 m from the centre. A label hanging at a height above the centre explains it: the ground position of a point at height h seen at pitch p is shifted by about h times tan p in the picture's up direction. A fit with a constant ground offset of about 8 m plus 37 m times the tangent of the pitch put all four towns within 2 to 4 m rms, against 14 m for Nagoya with a constant distance alone. The two numbers are loose because the pitch is noisy. In near-top-down pictures the label's height cannot be told from a flat offset, and the two models agree on the centres to about 3 m for the flat towns and 5 m for Nagoya.

The box also shrinks as the camera moves away: 18 to 43 px tall in Nagoya's pictures against 34 to 40 in the others, so pixel figures taken from it hold only for the sizes seen here.

## Open

- **Is it the game's own town centre?** The label hangs above some point. Whether that point is the one the name compass ([compass.md](compass.md)), town growth or the dashed boundary ([town-boundaries.md](town-boundaries.md)) use is untested. A direct test: a boundary line should be the perpendicular bisector of two centres from this method. The Aylsham and Chagford boundary needs Aylsham's centre the same way.
- **The label's height, and the box's size with distance.** Needs a series at several fixed pitches and zoom levels, one change at a time.
- **A stored position.** A town record has none. A save with a town renamed to a typed string, searched for in the stream, could still find the town entity and its position.
- **The method as a script.** The registration was done with scratch code, not a script in `tools/`.
