#!/usr/bin/env python3
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"
SPECIES_DIR = ROOT / "src/data/pokemon/species_info"

# Every numbered Gen 1-9 Pokemon gets a wild location. Temporary battle forms are
# naturally avoided because we keep only the first species entry for each NatDex number.
# Regional/cosmetic forms sharing a NatDex number are not required for completion here.


def species_catalog():
    rows = []
    seen_dex = set()
    marker = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=")
    for gen in range(1, 10):
        p = SPECIES_DIR / f"gen_{gen}_families.h"
        if not p.exists():
            continue
        text = p.read_text()
        marks = list(marker.finditer(text))
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            block = text[m.start():end]
            species = m.group(1)
            dm = re.search(r"\.natDexNum\s*=\s*(NATIONAL_DEX_[A-Z0-9_]+)", block)
            if not dm or dm.group(1) == "NATIONAL_DEX_NONE" or dm.group(1) in seen_dex:
                continue
            seen_dex.add(dm.group(1))
            stats = []
            for key in ("baseHP", "baseAttack", "baseDefense", "baseSpeed", "baseSpAttack", "baseSpDefense"):
                sm = re.search(rf"\.{key}\s*=\s*(\d+)", block)
                stats.append(int(sm.group(1)) if sm else 80)
            cm = re.search(r"\.catchRate\s*=\s*(\d+)", block)
            catch = int(cm.group(1)) if cm else 45
            tm = re.search(r"\.types\s*=\s*MON_TYPES\(([^)]*)\)", block)
            types = set(re.findall(r"TYPE_[A-Z]+", tm.group(1))) if tm else set()
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
            rows.append({"species": species, "dex": dm.group(1), "bst": bst, "catch": catch, "types": types, "rank": rank})
    return rows


def map_tier(name):
    if any(x in name for x in ("ARTISAN_CAVE", "ALTERING_CAVE", "DESERT_UNDERPASS", "BATTLE_FRONTIER")):
        return 4
    if any(x in name for x in ("VICTORY_ROAD", "SKY_PILLAR", "EVER_GRANDE", "CAVE_OF_ORIGIN", "SEAFLOOR_CAVERN", "SHOAL_CAVE")):
        return 3
    m = re.search(r"MAP_ROUTE(\d+)", name)
    if m:
        r = int(m.group(1))
        if r >= 124: return 3
        if r >= 111: return 2
        if r >= 105: return 1
        return 0
    if any(x in name for x in ("MT_PYRE", "METEOR_FALLS", "FIERY_PATH", "JAGGED_PASS", "NEW_MAUVILLE", "MT_CHIMNEY")):
        return 2
    if any(x in name for x in ("GRANITE_CAVE", "RUSTURF_TUNNEL")):
        return 1
    if "PETALBURG_WOODS" in name:
        return 0
    return 2


def theme_types(name):
    if any(x in name for x in ("DESERT", "JAGGED", "MT_CHIMNEY", "FIERY_PATH")):
        return {"TYPE_FIRE", "TYPE_GROUND", "TYPE_ROCK"}
    if "PETALBURG_WOODS" in name:
        return {"TYPE_GRASS", "TYPE_BUG", "TYPE_POISON", "TYPE_FAIRY"}
    if "MT_PYRE" in name:
        return {"TYPE_GHOST", "TYPE_DARK", "TYPE_PSYCHIC"}
    if "NEW_MAUVILLE" in name:
        return {"TYPE_ELECTRIC", "TYPE_STEEL"}
    if "SHOAL_CAVE" in name:
        return {"TYPE_ICE", "TYPE_WATER", "TYPE_ROCK"}
    if "VICTORY_ROAD" in name:
        return {"TYPE_FIGHTING", "TYPE_DRAGON", "TYPE_ROCK", "TYPE_STEEL"}
    if "SKY_PILLAR" in name:
        return {"TYPE_DRAGON", "TYPE_FLYING", "TYPE_PSYCHIC"}
    if any(x in name for x in ("SEAFLOOR", "UNDERWATER", "ABANDONED_SHIP")):
        return {"TYPE_WATER", "TYPE_GHOST", "TYPE_STEEL"}
    return set()


def field_score(info, slot):
    types = info["types"]
    field = slot["field"]
    score = 0
    if field in ("water_mons", "fishing_mons"):
        score += 6 if "TYPE_WATER" in types else (-4 if types else 0)
        if "TYPE_ICE" in types: score += 2
    elif field == "rock_smash_mons":
        if types & {"TYPE_ROCK", "TYPE_GROUND", "TYPE_STEEL", "TYPE_FIGHTING"}: score += 4
    else:
        if "TYPE_WATER" in types and len(types) == 1: score -= 2
        if types & {"TYPE_GRASS", "TYPE_BUG", "TYPE_NORMAL", "TYPE_FLYING"}: score += 1
    themed = theme_types(slot["map"])
    if themed and types & themed:
        score += 4
    return score


def route_reserved(map_name, field, idx):
    m = re.search(r"MAP_ROUTE(\d+)", map_name)
    if not m:
        return False
    route = int(m.group(1))
    if route >= 124:
        return False
    # Keep most of the hand-curated route identity; use rare slots for dex coverage.
    limits = {"land_mons": 8, "water_mons": 3, "rock_smash_mons": 3, "fishing_mons": 6}
    return idx < limits.get(field, 0)


def main():
    catalog = species_catalog()
    target = {x["species"] for x in catalog}
    data = json.loads(WILD.read_text())
    group = next(x for x in data["wild_encounter_groups"] if x.get("label") == "gWildMonHeaders")

    counts = Counter()
    all_slots = []
    for enc in group["encounters"]:
        map_name = enc.get("map", "")
        tier = map_tier(map_name)
        for field in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons"):
            table = enc.get(field)
            if not table:
                continue
            for idx, mon in enumerate(table.get("mons", [])):
                counts[mon["species"]] += 1
                all_slots.append({"mon": mon, "map": map_name, "tier": tier, "field": field, "idx": idx})

    existing = target & set(counts)
    missing = [x for x in catalog if x["species"] not in existing]
    # Strong/rare Pokemon are allocated first because they have fewer reasonable late-game slots.
    missing.sort(key=lambda x: (-x["rank"], -x["bst"], x["dex"]))

    available = []
    for slot in all_slots:
        old = slot["mon"]["species"]
        if route_reserved(slot["map"], slot["field"], slot["idx"]):
            continue
        # Never erase the only existing location for a target species.
        if old in target and counts[old] <= 1:
            continue
        available.append(slot)

    used = set()
    placed = 0
    for info in missing:
        min_tier = 3 if info["rank"] == 4 else max(0, info["rank"] - 1)
        choices = []
        for j, slot in enumerate(available):
            if j in used or slot["tier"] < min_tier:
                continue
            # Prefer a tier close to the Pokemon's intended progression point, then biome/method fit.
            tier_penalty = abs(slot["tier"] - min(4, info["rank"]))
            choices.append((field_score(info, slot) - 2 * tier_penalty, slot["tier"], -j, j))
        if not choices:
            raise RuntimeError(f"No reasonable encounter slot remains for {info['species']} (placed {placed}/{len(missing)})")
        _, _, _, j = max(choices)
        slot = available[j]
        used.add(j)
        mon = slot["mon"]
        old = mon["species"]
        counts[old] -= 1
        mon["species"] = info["species"]
        counts[info["species"]] += 1
        placed += 1

        # Keep rare/powerful catches late enough to feel special without making them postgame-only by default.
        floor = {0: 3, 1: 12, 2: 22, 3: 32, 4: 45}[info["rank"]]
        if slot["tier"] >= 4 and info["rank"] >= 4:
            floor = 50
        mon["min_level"] = max(mon.get("min_level", floor), floor)
        mon["max_level"] = max(mon.get("max_level", floor + 2), mon["min_level"] + 2)

    final_species = set()
    for enc in group["encounters"]:
        for field in ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons"):
            table = enc.get(field)
            if table:
                final_species.update(m["species"] for m in table.get("mons", []))
    still_missing = sorted(target - final_species)
    if still_missing:
        raise RuntimeError(f"Catchable dex validation failed; {len(still_missing)} missing: {still_missing[:20]}")

    WILD.write_text(json.dumps(data, indent=2) + "\n")
    ranks = Counter(x["rank"] for x in catalog)
    print(f"Catchable dex: {len(catalog)} Gen 1-9 Pokemon represented; placed {placed} previously missing species")
    print(f"Progression ranks: {dict(sorted(ranks.items()))}; curated early-route common slots preserved")


if __name__ == "__main__":
    main()
