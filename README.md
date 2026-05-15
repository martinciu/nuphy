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
uv run nuphy-rgb.py read                   # read effect, color, brightness, speed from keyboard
uv run nuphy-rgb.py save                   # persist to EEPROM
```

`read` prints the current effect index, hue/sat, brightness, and speed — useful for capturing a state set via VIA before saving it as a preset with `preset-save`.

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

Current presets (`config/presets.json`):

| Name | Effect | Hue | Sat | Brightness |
|------|--------|-----|-----|------------|
| warm-white | 1 (Solid Color) | 0 | 195 | 202 |

### Examples

Solid warm white (hue=0, sat=195, brightness=202):
```fish
uv run nuphy-rgb.py preset warm-white
```

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

| Index | Name | Interactive | Custom color |
|-------|------|-------------|--------------|
| 0 | All Off | | |
| 1 | Solid Color | | ✓ |
| 2 | Gradient Up/Down | | |
| 3 | Gradient Left/Right | | |
| 4 | Breathing | | ✓ |
| 5 | Band Sat. | | |
| 6 | Band Val. | | |
| 7 | Pinwheel Sat. | | |
| 8 | Pinwheel Val. | | |
| 9 | Spiral Sat. | | |
| 10 | Spiral Val. | | |
| 11 | Cycle All | | |
| 12 | Cycle Left/Right | | |
| 13 | Cycle Up/Down | | |
| 14 | Rainbow Moving Chevron | | |
| 15 | Cycle Out/In | | |
| 16 | Cycle Out/In Dual | | |
| 17 | Cycle Pinwheel | | |
| 18 | Cycle Spiral | | |
| 19 | Dual Beacon | | |
| 20 | Rainbow Beacon | | |
| 21 | Rainbow Pinwheels | | |
| 22 | Raindrops | | |
| 23 | Jellybean Raindrops | | |
| 24 | Hue Breathing | | |
| 25 | Hue Pendulum | | |
| 26 | Hue Wave | | |
| 27 | Typing Heatmap | ✓ | ✗ hardcoded blue→red |
| 28 | Digital Rain | | |
| 29 | Reactive Simple | ✓ | ✓ flashes your color, fades out |
| 30 | Reactive | ✓ | ✓ shifts hue on each hit |
| 31 | Reactive Wide | ✓ | ✓ spreads to nearby keys |
| 32 | Reactive Multiwide | ✓ | ✓ spreads to nearby keys |
| 33 | Reactive Cross | ✓ | ✓ spreads to nearby keys |
| 34 | Reactive Multicross | ✓ | ✓ spreads to nearby keys |
| 35 | Reactive Nexus | ✓ | ✓ spreads to nearby keys |
| 36 | Reactive MultiNexus | ✓ | ✓ spreads to nearby keys |
| 37 | Splash | ✓ | ✓ ripple outward, cycles hue |
| 38 | MultiSplash | ✓ | ✓ ripple outward, cycles hue |
| 39 | Solid Splash | ✓ | ✓ ripple in solid color |
| 40 | Solid MultiSplash | ✓ | ✓ ripple in solid color |

## VIA browser (keymap editing)

1. Open <https://usevia.app>
2. Settings → enable "Design tab"
3. Design → Load Draft Definition → `config/nuphy-air75-v2-via3.json`
4. Save+Load tab → load `config/martinciu.layout.json`

## Notes

- `nuphy-rgb.py` preloads `/opt/homebrew/lib/libhidapi.dylib` at startup — requires `brew install hidapi`.
