# Gaps: towns and buildings

Format of an entry: see [README.md](README.md).

## Town records

- **The record's third and fourth floats, the floats at offsets 70 and 74, and the trailing u32** (604) The floats keep growing in play and are not the experience earned (a town with "No Experience Earned Last Year" saw the second float rise by about 5,500). The u32 of value 1 near the end is unexplained. Home: [town-records.md](../town-records.md). Needs: game window (a town's points to the next level next to the record) plus existing saves.
- **The Towns tab's per-town figures** (604) The supply figures (68 fish, 97 fuel) match neither the commercial and industrial capacities nor a simple ratio; the car-icon column tracks about half the commercial plus industrial capacities (correlation 0.96, typical error 20, outliers up to 90); the per-town demand was not rebuilt from the stocks. The 32-record catalog save 6430076 does not fit the figures once attributed to it. Home: [town-records.md](../town-records.md), [building-stocks.md](../building-stocks.md#open). Needs: game window (the tab read in a save we also hold).
- **Town windows against records and script states** (604, one game) Population, growth levels and XP-to-next were checked for the first town record only. Home: [town-states.md](../town-states.md), [town-records.md](../town-records.md). Needs: game window.
- **What `constructionBoni` holds** (604) Home: [town-states.md](../town-states.md). Needs: existing saves.
- **The Town Authority label** (604, one game) A town with an `authorityScore` of 0.859 read "None" in the window, so the label is not the score alone. Home: [town-states.md](../town-states.md). Needs: game window.
- **What the Delivery Time factor of 1.5 depends on** (604, one game) The tooltips equal the cargo files' `timeToDeliverInSeconds` times 1.5; it may depend on difficulty or `townConfig.sensitivityCargoDelivery`. Home: [delivery-times.md](../delivery-times.md). Needs: new save on another preset.
- **What the economy and climate do to town cargo slots** (604) See [cargo-and-warehouses.md](cargo-and-warehouses.md#cargo-ids).

## Town buildings

- **Where the town boundary runs** (604, one game) The `town` field is the owning town (Confirmed, two buildings); six buildings carrying a neighbouring town's id were ticked as part of another town, and whether the field is the town of the street shown is open. Home: [town-buildings.md](../town-buildings.md). Suggested test: new save with a building deep inside a town ticked, and buildings on each side of the maintenance building where the boundary crosses a road.
- **What fields `a`, `b` and `d` point to** (604) And whether industrial, commercial and residential buildings can be told apart (the construction entity may carry a position). Home: [town-buildings.md](../town-buildings.md). Needs: existing saves.
- **The three small tail entries** (604) `[u32 id][u32 kind][u32 n][u32 flag][u32 count][count x (i32, u32)]` changed when three buildings were ticked for Historic Preservation; which of the three ids is the home is unknown. Home: [town-buildings.md](../town-buildings.md). Suggested test: new save with one building ticked alone, to see which record the entries follow.
- **The record's `year`** (604) See [cargo-and-warehouses.md](cargo-and-warehouses.md#warehouses).
- **Whether the game repairs a building that disagrees with its town** (604) On load or on a level change. Home: [building-stocks.md](../building-stocks.md#open). Needs: new save with a stock record patched.

## Stock records

- **The constant block between stock records, the float that follows, and where a building's customer count is kept** (604) Home: [building-stocks.md](../building-stocks.md#open). Needs: existing saves.
- **Whether picking the cargo a record already holds triggers the building update, and how stock capacity follows level and cargo weight** (604) Home: [building-stocks.md](../building-stocks.md#open). Needs: new save (one town changed in the Editor tab, loaded and saved).
- **Residential buildings** (604) No pick was changed, so none were read. Home: [building-stocks.md](../building-stocks.md#open). Needs: new save.

## Landmarks

- **The remaining sites, the requirements and the input stocks** (604, one game) Six more sites with round totals (200 to 1,200 per cargo): whether they are finished is unknown; the requirements (300 and 600) and the input stocks were not found as numbers and are probably in the site's entity data. Home: [landmarks.md](../landmarks.md). Needs: existing saves (statistics lists may hold the stocks, as they do for warehouses) plus game window.
- **`town2carrier2modifiers`** (604, one game) Probably the effects of finished landmarks (pollution 0.8, noise 0.75, comfort 1.25, topSpeed 1.2). Home: [landmarks.md](../landmarks.md). Needs: new save before and after finishing a landmark.
- **The counters in `celebrations.gs`** Not written up. Home: [script-states.md](../script-states.md). Needs: existing saves.
