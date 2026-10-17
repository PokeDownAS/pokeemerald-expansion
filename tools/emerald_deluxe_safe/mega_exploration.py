#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_ROOT = ROOT / "data/maps"
ITEMS = ROOT / "src/data/items.h"

# Each entry replaces one ordinary item ball in a thematically appropriate area.
# The Lilycove shop remains as a fallback, so none of these stones become missable.
PLACEMENTS = [
    (("NewMauville",), "ITEM_MANECTITE"),
    (("MagmaHideout", "JaggedPass"), "ITEM_CAMERUPTITE"),
    (("AquaHideout",), "ITEM_SHARPEDONITE"),
    (("MeteorFalls",), "ITEM_SALAMENCITE"),
    (("VictoryRoad",), "ITEM_GALLADITE"),
    (("ShoalCave",), "ITEM_GLALITITE"),
    (("SafariZone",), "ITEM_HERACRONITE"),
    (("SkyPillar",), "ITEM_ALTARIANITE"),
]


def supported_stones():
    text = ITEMS.read_text()
    result = set()
    block_re = re.compile(r"\[(ITEM_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n\s*\},", re.S)
    for m in block_re.finditer(text):
        if "HOLD_EFFECT_MEGA_STONE" in m.group(2):
            result.add(m.group(1))
    return result


def candidate_scripts(needles):
    files = []
    for path in MAP_ROOT.glob("*/scripts.inc"):
        map_name = path.parent.name
        if any(n.lower() in map_name.lower() for n in needles):
            files.append(path)
    return sorted(files)


def patch_one(path, stone):
    text = path.read_text()
    # Prefer a normal item-ball script; preserve the object's flag and event wiring.
    patterns = [
        re.compile(r"(\titemball\s+)ITEM_[A-Z0-9_]+"),
        re.compile(r"(\tgiveitem\s+)ITEM_[A-Z0-9_]+"),
    ]
    for pat in patterns:
        new, count = pat.subn(rf"\g<1>{stone}", text, count=1)
        if count:
            path.write_text(new)
            return True
    return False


def main():
    supported = supported_stones()
    placed = []
    skipped = []
    used_paths = set()

    for needles, stone in PLACEMENTS:
        if stone not in supported:
            skipped.append((stone, "unsupported"))
            continue
        done = False
        for path in candidate_scripts(needles):
            if path in used_paths:
                continue
            if patch_one(path, stone):
                used_paths.add(path)
                placed.append((stone, path.parent.name))
                done = True
                break
        if not done:
            skipped.append((stone, "no item ball found"))

    if len(placed) < 5:
        raise RuntimeError(f"Only placed {len(placed)} curated Mega Stones; expected at least 5. Details: {skipped}")

    print("Curated Mega Stone exploration placements:")
    for stone, area in placed:
        print(f"  {stone} -> {area}")
    if skipped:
        print("Skipped optional placements:", skipped)


if __name__ == "__main__":
    main()
