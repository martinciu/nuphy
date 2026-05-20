# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

VIA keyboard configuration for the **NuPhy Air75 V2** (vendorId `0x19F5`, productId `0x3246`). VIA is a browser-based keyboard remapping tool (<https://usevia.app>).

Key files:
- `config/nuphy-air75-v2-via3.json` — keyboard definition (matrix layout, lighting menus, custom keycodes). Load this in VIA under "Design" → "Load Draft Definition".
- `config/martinciu.layout.json` — personal keymap export (8 layers, macros). Restore via VIA's "Save+Load" tab.
- `config/presets.json` — named RGB presets (used by `nuphy-rgb.py preset*` commands).

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
uv run nuphy-rgb.py effects                          # list all effects (⌨ marks interactive) — no keyboard needed
uv run nuphy-rgb.py color <hue 0-255> <sat 0-255>   # hue: 0=red 85=green 170=blue
uv run nuphy-rgb.py rgb <r> <g> <b>                 # set color by RGB values
uv run nuphy-rgb.py rgb <#rrggbb>                   # set color by hex
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

Current presets: `warm-white` (effect=1, hue=0, sat=208, brightness=255).

Effect index → name mapping: see README.md for the full table.

## Personal keymap — Fn-layer RGB bindings

From `config/martinciu.layout.json` (Layer 1, Mac Fn). Runs on stock NuPhy firmware.

| Fn + key | Keycode | Action |
|----------|---------|--------|
| Fn + PgUp | `RGB_MOD` | Next effect |
| Fn + PgDn | `RGB_RMOD` | Previous effect |
| Fn + Home | `RGB_SAI` | Saturation + |
| Fn + End | `RGB_SAD` | Saturation − |
| Fn + ↑ | `RGB_VAI` | Brightness + |
| Fn + ↓ | `RGB_VAD` | Brightness − |
| Fn + ← | `RGB_HUD` | Hue − |
| Fn + → | `RGB_HUI` | Hue + |
| Fn + , | `RGB_SPD` | Effect speed − |
| Fn + . | `RGB_SPI` | Effect speed + |
| Fn + M (hold) | `MO(4)` | Side LED controls layer (uses `CUSTOM(12-17)`, see VIA JSON) |

## Editing guidelines

- The definition file (`nuphy-air75-v2-via3.json`) is read-only on the filesystem (mode `444`). Modifications require `chmod u+w` first, or edit a copy.
- Keep layer arrays exactly 102 entries long (6 rows × 17 cols = 102 matrix positions). VIA will reject a layout file with the wrong count.
- `KC_NO` = no key / blocked. `KC_TRNS` = transparent (only valid in layers 1+).
