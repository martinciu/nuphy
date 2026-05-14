# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

VIA keyboard configuration for the **NuPhy Air75 V2** (vendorId `0x19F5`, productId `0x3246`). VIA is a browser-based keyboard remapping tool (<https://usevia.app>).

Key files:
- `config/nuphy-air75-v2-via3.json` — keyboard definition (matrix layout, lighting menus, custom keycodes). Load this in VIA under "Design" → "Load Draft Definition".
- `config/martinciu.layout.json` — personal keymap export (8 layers, macros). Restore via VIA's "Save+Load" tab.
- `config/presets.json` — named RGB presets (used by `nuphy-rgb.py preset*` commands).
- `ext/` — git submodules: `qmk-firmware` (ryodeushii fork), `via/app`, `via/reader`.

## Key concepts

**Matrix coordinates** — keys are addressed as `"row,col"` (e.g. `"0,0"`). The matrix is 6 rows × 17 cols. Not every cell maps to a physical key; unused positions appear as `KC_NO` in the layout file.

**Layers** — `martinciu.layout.json` has 8 layers (indices 0–7). `KC_TRNS` means "transparent" (fall through to the layer below). Layer switching uses `MO(n)` (momentary) in the keymap.

**Custom keycodes** — `CUSTOM(n)` references the `customKeycodes` array in the definition file (0-indexed). For example, `CUSTOM(6)` = "Mac Task", `CUSTOM(7)` = "Mac Search".

**Macros** — `MACRO(n)` references the `macros` array in the layout file. The first three are defined; the rest are empty strings.

**`vendorProductId`** in the layout file is the decimal encoding of `(vendorId << 16) | productId`: `0x19F5 * 65536 + 0x3246 = 435499590`.

## RGB control — nuphy-rgb.py

`nuphy-rgb.py` controls RGB lighting via the VIA v3 HID protocol. Requires `brew install hidapi`.

```fish
uv run nuphy-rgb.py effect <0-40>
uv run nuphy-rgb.py color <hue 0-255> <sat 0-255>   # hue: 0=red 85=green 170=blue
uv run nuphy-rgb.py brightness <0-255>
uv run nuphy-rgb.py speed <0-255>
uv run nuphy-rgb.py read                             # read effect, color, brightness, speed from keyboard
uv run nuphy-rgb.py save
```

`read` prints current keyboard state — useful for capturing settings applied via VIA before saving as a preset with `preset-save`.

**`save` is not implicit** — settings revert on power cycle without it. Chain commands:

```fish
uv run nuphy-rgb.py effect 1 && uv run nuphy-rgb.py color 170 255 && uv run nuphy-rgb.py save
```

**Presets** — named snapshots stored in `config/presets.json`:

```fish
uv run nuphy-rgb.py preset <name>       # apply preset + save to EEPROM
uv run nuphy-rgb.py preset-save <name>  # capture current keyboard state as preset
uv run nuphy-rgb.py preset-list         # list all presets
```

Current presets: `warm-white` (effect=1, hue=0, sat=195, brightness=202).

Effect index → name mapping: see README.md for the full table.

## ryodeushii/qmk-firmware — community fork

Cloned at `qmk-firmware/`. Branch: `nuphy-keyboards`. Synced to QMK `0.32.7`.

**Build and flash:**
```
make nuphy/air75v2/ansi:via
make nuphy/air75v2/ansi:via:flash
```

Alternatively flash a pre-built `.bin` via [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases) — simpler, no build environment needed.

**Bootloader entry (two methods):**
- Hold `Esc` and plug in USB
- Remove the CapsLock keycap, hold the small button underneath, then plug in

**VIA JSON for this fork:** `qmk-firmware/keyboards/nuphy/air75v2/ansi/keymaps/default/NuPhy Air75 V2 via3.json` — use this instead of `config/nuphy-air75-v2-via3.json` when running community firmware.

**Layer layout** (Mac keymap — Windows identical except F-row and SOCD keys):
- Layer 0: Mac base
- Layer 1: Mac Fn (hold `Fn`)
- Layer 2: Win base
- Layer 3: Win Fn (hold `Fn`)
- Layer 4: Side LED controls (hold `Fn+M`)
- Layer 5: Ambient LED controls (hold `Fn+N`)

**Key Fn-layer bindings** (`keyboards/nuphy/air75v2/ansi/keymaps/default/keymap.c`):

| Keys | Action |
|------|--------|
| Fn+1/2/3 | BLE profile 1/2/3 |
| Fn+4 | RF (2.4GHz dongle) |
| Fn+Y/U/I | Press debounce −/show/+ |
| Fn+H/J/K | Release debounce −/show/+ |
| Fn+S/D/F | Sleep timeout −/show/+ |
| Fn+O | Toggle deep sleep |
| Fn+P | Toggle USB sleep |
| Fn+A | Toggle CapsLock indicator mode |
| Fn+[ | Device reset |
| Fn+C | RGB test |
| Fn+↑/↓/←/→ | RGB brightness+/−, next effect, hue+ |
| Fn+,/. | RGB effect speed −/+ |
| Fn+M (hold) | Side LED controls layer |
| Fn+N (hold) | Ambient (logo) LED controls layer |
| Fn+F3/F4/F5 | SOCD on/off/toggle (Win layer only) |

**Side LED controls** (while holding `Fn+M`): ←=mode, ↑=brightness+, ↓=brightness−, ,/.=speed, →=hue+

**Ambient LED controls** (while holding `Fn+N`): same layout as side controls

**Notable fixes over stock firmware:**
- Print Screen actually sends `KC_PSCR` (stock sent Win+Shift+S)
- First keystrokes on wireless wake no longer dropped
- Left Ctrl backlight LED lit correctly
- White LED flash on deep-sleep wake eliminated

## Editing guidelines

- The definition file (`nuphy-air75-v2-via3.json`) is read-only on the filesystem (mode `444`). Modifications require `chmod u+w` first, or edit a copy.
- Keep layer arrays exactly 102 entries long (6 rows × 17 cols = 102 matrix positions). VIA will reject a layout file with the wrong count.
- `KC_NO` = no key / blocked. `KC_TRNS` = transparent (only valid in layers 1+).
