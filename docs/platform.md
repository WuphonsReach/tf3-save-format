# Platform in the save

Checked 2026-10-10 on the 244 catalog entries of [versions.md](versions.md#summarised-catalog-2026-10-09). There is no field that names the platform a save was made on (**Observed**, 568 to 604). The entries were matched with the uploader's platform from the mod.io upload records ([versions.md](versions.md#versions-and-releases-2026-10-10)), and searched in full for platform names:

- **Header.** No field reads differently by platform. Checked: the preview flag, the u8 flag before `value`, the open stats fields, the mod list's `source` (`DLC`, `mod.io`, `BuiltInMods` on every platform) and `flags`, and the settings keys and values. Two comparisons were made: console against PC at 601 (39 against 2), and Windows, Mac, Linux and the Epic/GOG build at 604. A value that turned up off Windows only did so in one or two saves.
- **Whole stream.** Searched for the names of the consoles, operating systems and stores, and for the path prefixes of each system. The short ones (`PS5`, `GDK`, `EGS`, `GOG`, `C:\`) occur in nearly every save on every platform, so they are chance byte matches. `steam` and `platform` are game words. The longer hits are names from the name lists, or part of a mod's name.

Two ways a save can still give its platform away:

- **A stored Lua error.** A mod can keep a Lua error message in its script state, and the message starts with the mod file's install path. In [6429325](https://mod.io/g/transportfever3/m/my-rail-network) (Windows, 604) the path is under a Windows user folder. In [6431316](https://mod.io/g/transportfever3/m/1990-2) (Xbox, 601) it starts `R:/mod.io/10640/`. Both come from one mod. Layout, search and counts are in [script-states.md](script-states.md#mod-script-states-and-stored-errors). **Observed**, two saves.
- **Mods from outside mod.io.** Mods whose URL points to modwerkstatt.com appear only in PC saves (7 saves, all 604). Consoles probably load mods from mod.io only, so such a mod suggests a PC save (**Open**). A save without one says nothing.

Since console and PC saves also differ in format version (601 against 604), the only same-version comparison so far has two PC saves. A platform code hidden in a field not yet described is not ruled out (**Open**).
