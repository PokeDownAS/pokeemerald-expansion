#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"
SPECIES_DIR = ROOT / "src/data/pokemon/species_info"
FIELDS = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons")


def catalog():
    info = {}
    marker = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=")
    for gen in range(1, 10):
        path = SPECIES_DIR / f"gen_{gen}_families.h"
        if not path.exists():
            continue
        text = path.read_text()
        marks = list(marker.finditer(text))
        for i, match in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            block = text[match.start():end]
            stats = []
            for key in ("baseHP", "baseAttack", "baseDefense", "baseSpeed", "baseSpAttack", "baseSpDefense"):
                sm = re.search(rf"\.{key}\s*=\s*(\d+)", block)
                stats.append(int(sm.group(1)) if sm else 80)
            cm = re.search(r"\.catchRate\s*=\s*(\d+)", block)
            catch = int(cm.group(1)) if cm else 45
            bst = sum(stats)
            if catch <= 10 or bst >= 600:
                rank = 4
            elif catch <= 45 or bst >= 530:
                rank = 3
            elif bst >= 450:
                rank = 2
            elif bst >= 350:
                rank = 1
            else:
                rank = 0
            info[match.group(1)] = rank
    return info


def map_tier(name):
    if any(x in name for x in ("ARTISAN_CAVE", "ALTERING_CAVE", "DESERT_UNDERPASS", "BATTLE_FRONTIER")):
        return 4
    if any(x in name for x in ("VICTORY_ROAD", "SKY_PILLAR", "EVER_GRANDE", "CAVE_OF_ORIGIN", "SEAFLOOR_CAVERN", "SHOAL_CAVE")):
        return 3
    m = re.search(r"MAP_ROUTE(\d+)", name)
    if m:
        route = int(m.group(1))
        if route >= 124:
            return 3
        if route >= 111:
            return 2
        if route >= 105:
            return 1
        return 0
    if any(x in name for x in ("MT_PYRE", "METEOR_FALLS", "FIERY_PATH", "JAGGED_PASS", "NEW_MAUVILLE", "MT_CHIMNEY")):
        return 2
    if any(x in name for x in ("GRANITE_CAVE", "RUSTURF_TUNNEL")):
        return 1
    if "PETALBURG_WOODS" in name:
        return 0
    return 2


def desired_min_tier(rank):
    if rank >= 4:
        return 3
    if rank == 3:
        return 1
    return 0


def slot_floor(tier):
    return (3, 10, 20, 30, 42)[tier]


def main():
    ranks = catalog()
    data = json.loads(WILD.read_text())
    group = next(x for x in data["wild_encounter_groups"] if x.get("label") == "gWildMonHeaders")
    slots = []
    before_species = []
    for enc in group["encounters"]:
        tier = map_tier(enc.get("map", ""))
        for field in FIELDS:
            table = enc.get(field)
            if not table:
                continue
            mons = table.get("mons", [])
            for idx, mon in enumerate(mons):
                before_species.append(mon["species"])
                slots.append({"mon": mon, "tier": tier, "field": field, "idx": idx, "map": enc.get("map", "")})

    moved = 0
    # Move truly powerful/rare species out of maps that are too early by swapping
    # them with ordinary Pokemon from later maps. Swapping preserves complete dex coverage.
    offenders = [s for s in slots if s["tier"] < desired_min_tier(ranks.get(s["mon"]["species"], 0))]
    for early in offenders:
        rank = ranks.get(early["mon"]["species"], 0)
        need = desired_min_tier(rank)
        candidates = []
        for late in slots:
            late_rank = ranks.get(late["mon"]["species"], 0)
            if late["tier"] < need:
                continue
            if late_rank > 1:
                continue
            same_field = int(late["field"] == early["field"])
            rare_slot = late["idx"]
            candidates.append((same_field, late["tier"], rare_slot, late))
        if not candidates:
            continue
        late = max(candidates, key=lambda x: (x[0], x[1], x[2]))[3]
        early["mon"]["species"], late["mon"]["species"] = late["mon"]["species"], early["mon"]["species"]
        moved += 1

    # Smooth encounter levels by area. Common Pokemon remain a bit below local trainer
    # levels; rare species get a small premium, and late-game areas stop spawning
    # inexplicably low-level catches.
    adjusted = 0
    for slot in slots:
        mon = slot["mon"]
        tier = slot["tier"]
        rank = ranks.get(mon["species"], 0)
        floor = slot_floor(tier) + min(rank, 3) * 2
        old_min = int(mon.get("min_level", floor))
        old_max = int(mon.get("max_level", old_min + 2))
        new_min = max(old_min, floor)
        new_max = max(old_max, new_min + 2)
        if new_min != old_min or new_max != old_max:
            mon["min_level"] = new_min
            mon["max_level"] = new_max
            adjusted += 1

    after_species = [s["mon"]["species"] for s in slots]
    if sorted(before_species) != sorted(after_species):
        raise RuntimeError("Encounter progression changed species coverage instead of only relocating species")

    remaining_bad = []
    for slot in slots:
        rank = ranks.get(slot["mon"]["species"], 0)
        if slot["tier"] < desired_min_tier(rank):
            remaining_bad.append((slot["map"], slot["mon"]["species"], slot["tier"], rank))
    if remaining_bad:
        print(f"Encounter progression warning: {len(remaining_bad)} powerful encounters could not be relocated; first few: {remaining_bad[:5]}")

    WILD.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Encounter progression: relocated {moved} early powerful encounters and adjusted levels in {adjusted} slots while preserving all species coverage.")


if __name__ == "__main__":
    main()
