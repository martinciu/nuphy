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
        elif args.cmd == "read":
            labels = {1: "brightness", 2: "effect", 3: "speed", 4: "color"}
            for idx, label in labels.items():
                resp = query(d, CUSTOM_MENU_GET, CHANNEL, idx)
                if resp is None:
                    print(f"{label}: no response")
                else:
                    values = resp[3:]
                    values = [v for v in values if v != 0] or [0]
                    print(f"{label}: {values}")
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
