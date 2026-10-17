#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_ROOT = ROOT / "data/maps"
ITEMS = ROOT / "src/data/items.h"

# Replace one ordinary visible item ball in each thematic area. The original
# object's flag is retained because it only controls whether that pickup was used.
# Lilycove remains a shop fallback, so these exploration rewards are bonuses.
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


def candidate_maps(needles):
    files = []
    for path in MAP_ROOT.glob("*/map.json"):
        map_name = path.parent.name
        if any(n.lower() in map_name.lower() for n in needles):
            files.append(path)
    return sorted(files)


def patch_one(path, stone):
    data = json.loads(path.read_text())
    events = data.get("object_events") or []
    for event in events:
        if (
            event.get("graphics_id") == "OBJ_EVENT_GFX_ITEM_BALL"
            and event.get("script") == "Common_EventScript_FindItem"
            and str(event.get("trainer_sight_or_berry_tree_id", "")).startswith("ITEM_")
        ):
            old = event["trainer_sight_or_berry_tree_id"]
            event["trainer_sight_or_berry_tree_id"] = stone
            path.write_text(json.dumps(data, indent=2) + "\n")
            return old
    return None


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
        for path in candidate_maps(needles):
            if path in used_paths:
                continue
            old = patch_one(path, stone)
            if old:
                used_paths.add(path)
                placed.append((stone, path.parent.name, old))
                done = True
                break
        if not done:
            skipped.append((stone, "no normal item ball found"))

    if len(placed) < 5:
        raise RuntimeError(f"Only placed {len(placed)} curated Mega Stones; expected at least 5. Details: {skipped}")

    print("Curated Mega Stone exploration placements:")
    for stone, area, old in placed:
        print(f"  {stone} -> {area} (replaced {old})")
    if skipped:
        print("Skipped optional placements:", skipped)


if __name__ == "__main__":
    main()
