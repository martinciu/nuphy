#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["hid"]
# ///

"""Control NuPhy Air75 V2 RGB lighting via VIA HID protocol."""

import sys
import os
import json
import argparse
from pathlib import Path

if "/opt/homebrew/lib" not in os.environ.get("DYLD_LIBRARY_PATH", ""):
    os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import hid

VID = 0x19F5
PID = 0x3246
PRESETS_FILE = Path(__file__).parent / "config" / "presets.json"

CUSTOM_MENU_SET = 0x07
CUSTOM_MENU_GET = 0x08
CUSTOM_MENU_SAVE = 0x09
CHANNEL = 3


def rgb_to_hs(r: int, g: int, b: int) -> tuple[int, int]:
    """Convert RGB to keyboard hue/sat bytes (0-255) using inverse of VIA's formula."""
    r_, g_, b_ = r / 255, g / 255, b / 255
    cmax, cmin = max(r_, g_, b_), min(r_, g_, b_)
    delta = cmax - cmin
    if delta == 0:
        h = 0
    elif cmax == r_:
        h = 60 * (((g_ - b_) / delta) % 6)
    elif cmax == g_:
        h = 60 * ((b_ - r_) / delta + 2)
    else:
        h = 60 * ((r_ - g_) / delta + 4)
    h = (h + 360) % 360
    s = delta / cmax if cmax != 0 else 0
    return round(h * 255 / 360), round(s * 255)


def hs_to_rgb(hue_byte: int, sat_byte: int) -> tuple[int, int, int]:
    """Convert keyboard hue/sat (0-255) to RGB using VIA's formula."""
    sat = sat_byte / 255
    hue = round(360 * hue_byte) / 255
    c = sat
    x = c * (1 - abs((hue / 60) % 2 - 1))
    m = 1 - c
    if hue < 60:
        rp, gp, bp = c, x, 0
    elif hue < 120:
        rp, gp, bp = x, c, 0
    elif hue < 180:
        rp, gp, bp = 0, c, x
    elif hue < 240:
        rp, gp, bp = 0, x, c
    elif hue < 300:
        rp, gp, bp = x, 0, c
    else:
        rp, gp, bp = c, 0, x
    return round(255 * (m + rp)), round(255 * (m + gp)), round(255 * (m + bp))


def color_name(hue_byte: int, sat_byte: int) -> str:
    sat = sat_byte / 255
    hue = round(360 * hue_byte) / 255
    if sat < 0.15:
        return "white"
    if sat < 0.45:
        if hue < 30 or hue >= 330:
            return "warm white"
        if hue < 90:
            return "pale yellow"
        if hue < 150:
            return "pale green"
        if hue < 210:
            return "pale cyan"
        if hue < 270:
            return "pale blue"
        return "pale purple"
    if hue < 15 or hue >= 345:
        return "red"
    if hue < 45:
        return "orange"
    if hue < 75:
        return "yellow"
    if hue < 150:
        return "green"
    if hue < 195:
        return "cyan"
    if hue < 255:
        return "blue"
    if hue < 285:
        return "indigo"
    if hue < 330:
        return "purple"
    return "pink"


def find_via_device():
    for info in hid.enumerate(VID, PID):
        if info.get("usage_page") == 0xFF60 and info.get("usage") == 0x61:
            return hid.Device(path=info["path"])
    sys.exit("VIA interface not found. Check USB connection and Input Monitoring permission.")


def send(device, *payload):
    report = bytes([0x00] + list(payload) + [0] * 33)
    device.write(report[:33])


def query(device, *payload):
    send(device, *payload)
    data = device.read(32, timeout=500)
    return list(data) if data else None


def main():
    parser = argparse.ArgumentParser(description="NuPhy Air75 V2 RGB control")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("brightness", help="Set brightness (0-255)")
    p.add_argument("value", type=int, metavar="0-255")

    p = sub.add_parser("effect", help="Set effect index (0-40, see CLAUDE.md for names)")
    p.add_argument("value", type=int, metavar="0-40")

    p = sub.add_parser("speed", help="Set effect speed (0-255)")
    p.add_argument("value", type=int, metavar="0-255")

    p = sub.add_parser("color", help="Set color by hue and saturation (0-255 each)")
    p.add_argument("hue", type=int, metavar="0-255")
    p.add_argument("sat", type=int, metavar="0-255")

    p = sub.add_parser("rgb", help="Set color by R G B values or hex (#rrggbb)")
    p.add_argument("r_or_hex", metavar="R|#hex")
    p.add_argument("g", type=int, metavar="G", nargs="?")
    p.add_argument("b", type=int, metavar="B", nargs="?")

    sub.add_parser("read", help="Read current effect, color, brightness, speed")
    sub.add_parser("save", help="Persist settings to EEPROM")

    p = sub.add_parser("preset", help="Apply a saved preset (also saves to EEPROM)")
    p.add_argument("name", help="Preset name")

    p = sub.add_parser("preset-save", help="Save current keyboard state as a named preset")
    p.add_argument("name", help="Preset name")

    sub.add_parser("preset-list", help="List all saved presets")

    args = parser.parse_args()
    d = find_via_device()

    try:
        if args.cmd == "brightness":
            send(d, CUSTOM_MENU_SET, CHANNEL, 1, args.value)
        elif args.cmd == "effect":
            send(d, CUSTOM_MENU_SET, CHANNEL, 2, args.value)
        elif args.cmd == "speed":
            send(d, CUSTOM_MENU_SET, CHANNEL, 3, args.value)
        elif args.cmd == "color":
            send(d, CUSTOM_MENU_SET, CHANNEL, 4, args.hue, args.sat)
        elif args.cmd == "rgb":
            if args.r_or_hex.startswith("#") or (len(args.r_or_hex) == 6 and all(c in "0123456789abcdefABCDEF" for c in args.r_or_hex)):
                hex_str = args.r_or_hex.lstrip("#")
                r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            elif args.g is not None and args.b is not None:
                r, g, b = int(args.r_or_hex), args.g, args.b
            else:
                sys.exit("Usage: rgb <r> <g> <b>  or  rgb #rrggbb")
            hue, sat = rgb_to_hs(r, g, b)
            send(d, CUSTOM_MENU_SET, CHANNEL, 4, hue, sat)
            print(f"#{r:02x}{g:02x}{b:02x} → hue={hue} sat={sat}")
        elif args.cmd == "read":
            EFFECT_NAMES = [
                "All Off", "Solid Color", "Gradient Up/Down", "Gradient Left/Right",
                "Breathing", "Band Sat.", "Band Val.", "Pinwheel Sat.", "Pinwheel Val.",
                "Spiral Sat.", "Spiral Val.", "Cycle All", "Cycle Left/Right", "Cycle Up/Down",
                "Rainbow Moving Chevron", "Cycle Out/In", "Cycle Out/In Dual", "Cycle Pinwheel",
                "Cycle Spiral", "Dual Beacon", "Rainbow Beacon", "Rainbow Pinwheels",
                "Raindrops", "Jellybean Raindrops", "Hue Breathing", "Hue Pendulum", "Hue Wave",
                "Typing Heatmap", "Digital Rain", "Reactive Simple", "Reactive", "Reactive Wide",
                "Reactive Multiwide", "Reactive Cross", "Reactive Multicross", "Reactive Nexus",
                "Reactive MultiNexus", "Splash", "MultiSplash", "Solid Splash", "Solid MultiSplash",
            ]
            for idx, label in {1: "brightness", 2: "effect", 3: "speed", 4: "color"}.items():
                resp = query(d, CUSTOM_MENU_GET, CHANNEL, idx)
                if resp is None:
                    print(f"{label}: no response")
                elif label == "effect":
                    n = resp[3]
                    name = EFFECT_NAMES[n] if n < len(EFFECT_NAMES) else "Unknown"
                    print(f"effect: {n} ({name})")
                elif label == "color":
                    h, s = resp[3], resp[4]
                    r, g, b = hs_to_rgb(h, s)
                    name = color_name(h, s)
                    print(f"color: hue={h} sat={s} → #{r:02x}{g:02x}{b:02x} ({name})")
                else:
                    print(f"{label}: {resp[3]}")
        elif args.cmd == "save":
            send(d, CUSTOM_MENU_SAVE, CHANNEL)
        elif args.cmd == "preset":
            presets = json.loads(PRESETS_FILE.read_text()) if PRESETS_FILE.exists() else {}
            if args.name not in presets:
                sys.exit(f"Unknown preset '{args.name}'. Available: {', '.join(presets) or '(none)'}")
            p = presets[args.name]
            send(d, CUSTOM_MENU_SET, CHANNEL, 2, p["effect"])
            send(d, CUSTOM_MENU_SET, CHANNEL, 4, p["hue"], p["sat"])
            send(d, CUSTOM_MENU_SET, CHANNEL, 1, p["brightness"])
            send(d, CUSTOM_MENU_SET, CHANNEL, 3, p["speed"])
            send(d, CUSTOM_MENU_SAVE, CHANNEL)
            print(f"Applied preset '{args.name}'")
        elif args.cmd == "preset-save":
            resp = {}
            for idx, key in [(2, "effect"), (1, "brightness"), (3, "speed")]:
                r = query(d, CUSTOM_MENU_GET, CHANNEL, idx)
                resp[key] = r[3] if r else 0
            r = query(d, CUSTOM_MENU_GET, CHANNEL, 4)
            resp["hue"] = r[3] if r else 0
            resp["sat"] = r[4] if r else 0
            presets = json.loads(PRESETS_FILE.read_text()) if PRESETS_FILE.exists() else {}
            presets[args.name] = resp
            PRESETS_FILE.write_text(json.dumps(presets, indent=2) + "\n")
            print(f"Saved preset '{args.name}': effect={resp['effect']} hue={resp['hue']} sat={resp['sat']} brightness={resp['brightness']} speed={resp['speed']}")
        elif args.cmd == "preset-list":
            if not PRESETS_FILE.exists():
                print("No presets saved.")
            else:
                presets = json.loads(PRESETS_FILE.read_text())
                if not presets:
                    print("No presets saved.")
                else:
                    for name, p in presets.items():
                        print(f"  {name}: effect={p['effect']} hue={p['hue']} sat={p['sat']} brightness={p['brightness']} speed={p['speed']}")
    finally:
        d.close()


if __name__ == "__main__":
    main()
