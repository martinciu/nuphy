# NuPhy Air75 V2 — keyboard config & RGB control

VIA keymap and RGB control scripts for the NuPhy Air75 V2 (VID `0x19F5`, PID `0x3246`).

## Files

- `config/nuphy-air75-v2-via3.json` — keyboard definition for VIA
- `config/martinciu.layout.json` — personal keymap (8 layers, macros)
- `config/presets.json` — named RGB presets
- `nuphy-rgb.py` — command-line RGB control script
- `ext/` — external sources (git submodules): `qmk-firmware`, `via/app`, `via/reader`

## RGB control

`nuphy-rgb.py` uses the VIA HID protocol directly. Requires `hidapi` (`brew install hidapi`) and Python via `uv`.

```fish
uv run nuphy-rgb.py effect <0-40>          # set lighting effect
uv run nuphy-rgb.py color <hue> <sat>      # hue/sat 0-255 each
uv run nuphy-rgb.py brightness <0-255>
uv run nuphy-rgb.py speed <0-255>          # effect animation speed
uv run nuphy-rgb.py read                   # read current settings from keyboard
uv run nuphy-rgb.py save                   # persist to EEPROM
```

**Settings revert on power cycle unless you run `save`.** Chain commands:

```fish
uv run nuphy-rgb.py effect 1 && uv run nuphy-rgb.py color 170 255 && uv run nuphy-rgb.py save
```

### Presets

Named snapshots stored in `config/presets.json`:

```fish
uv run nuphy-rgb.py preset <name>       # apply preset + save to EEPROM
uv run nuphy-rgb.py preset-save <name>  # capture current keyboard state as preset
uv run nuphy-rgb.py preset-list         # list all presets
```

### Examples

Typing heatmap:
```fish
uv run nuphy-rgb.py effect 27 && uv run nuphy-rgb.py save
```

### Hue reference

| Hue | Color |
|-----|-------|
| 0 | Red |
| 43 | Yellow |
| 85 | Green |
| 128 | Cyan |
| 170 | Blue |
| 213 | Magenta |

### Effect index reference

| Index | Name | Index | Name |
|-------|------|-------|------|
| 0 | All Off | 21 | Rainbow Pinwheels |
| 1 | Solid Color | 22 | Raindrops |
| 2 | Gradient Up/Down | 23 | Jellybean Raindrops |
| 3 | Gradient Left/Right | 24 | Hue Breathing |
| 4 | Breathing | 25 | Hue Pendulum |
| 5 | Band Sat. | 26 | Hue Wave |
| 6 | Band Val. | 27 | Typing Heatmap |
| 7 | Pinwheel Sat. | 28 | Digital Rain |
| 8 | Pinwheel Val. | 29 | Reactive Simple |
| 9 | Spiral Sat. | 30 | Reactive |
| 10 | Spiral Val. | 31 | Reactive Wide |
| 11 | Cycle All | 32 | Reactive Multiwide |
| 12 | Cycle Left/Right | 33 | Reactive Cross |
| 13 | Cycle Up/Down | 34 | Reactive Multicross |
| 14 | Rainbow Moving Chevron | 35 | Reactive Nexus |
| 15 | Cycle Out/In | 36 | Reactive MultiNexus |
| 16 | Cycle Out/In Dual | 37 | Splash |
| 17 | Cycle Pinwheel | 38 | MultiSplash |
| 18 | Cycle Spiral | 39 | Solid Splash |
| 19 | Dual Beacon | 40 | Solid MultiSplash |
| 20 | Rainbow Beacon | | |

## VIA browser (keymap editing)

1. Open <https://usevia.app>
2. Settings → enable "Design tab"
3. Design → Load Draft Definition → `config/nuphy-air75-v2-via3.json`
4. Save+Load tab → load `config/martinciu.layout.json`

## Notes

- `qmk_hid` is installed but only effect switching works — color/brightness/save are broken due to firmware using VIA v3 custom menu protocol that `qmk_hid` doesn't implement correctly. Use `nuphy-rgb.py` instead.
- `nuphy-rgb.py` preloads `/opt/homebrew/lib/libhidapi.dylib` at startup — requires `brew install hidapi`.
