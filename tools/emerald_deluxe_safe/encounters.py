#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"

LAND_POOLS = {
    "early_meadow": [
        "SPECIES_ZIGZAGOON", "SPECIES_SENTRET", "SPECIES_STARLY", "SPECIES_POOCHYENA",
        "SPECIES_SHROOMISH", "SPECIES_MAREEP", "SPECIES_RALTS", "SPECIES_WURMPLE",
        "SPECIES_ROCKRUFF", "SPECIES_PAWMI", "SPECIES_RIOLU", "SPECIES_EEVEE",
    ],
    "forest": [
        "SPECIES_CATERPIE", "SPECIES_WURMPLE", "SPECIES_SHROOMISH", "SPECIES_BUDEW",
        "SPECIES_SEWADDLE", "SPECIES_GRUBBIN", "SPECIES_APPLIN", "SPECIES_PHANTUMP",
        "SPECIES_SCYTHER", "SPECIES_PIKACHU", "SPECIES_TAROUNTULA", "SPECIES_ODDISH",
    ],
    "electric": [
        "SPECIES_ELECTRIKE", "SPECIES_MAGNEMITE", "SPECIES_MAREEP", "SPECIES_SHINX",
        "SPECIES_PAWMI", "SPECIES_YAMPER", "SPECIES_TOGEDEMARU", "SPECIES_VOLTORB",
        "SPECIES_PLUSLE", "SPECIES_MINUN", "SPECIES_TADBULB", "SPECIES_PACHIRISU",
    ],
    "desert": [
        "SPECIES_TRAPINCH", "SPECIES_SANDSHREW", "SPECIES_SANDILE", "SPECIES_CACNEA",
        "SPECIES_BALTOY", "SPECIES_HIPPOPOTAS", "SPECIES_DRILBUR", "SPECIES_MUDBRAY",
        "SPECIES_SILICOBRA", "SPECIES_NACLI", "SPECIES_HELIOPTILE", "SPECIES_LARVESTA",
    ],
    "volcano": [
        "SPECIES_NUMEL", "SPECIES_SLUGMA", "SPECIES_TORKOAL", "SPECIES_GROWLITHE",
        "SPECIES_HOUNDOUR", "SPECIES_MAGBY", "SPECIES_DARUMAKA", "SPECIES_SALANDIT",
        "SPECIES_SIZZLIPEDE", "SPECIES_CAPSAKID", "SPECIES_CHARCADET", "SPECIES_ROLYCOLY",
    ],
    "mountain": [
        "SPECIES_ARON", "SPECIES_MACHOP", "SPECIES_GEODUDE", "SPECIES_SWABLU",
        "SPECIES_ROCKRUFF", "SPECIES_RIOLU", "SPECIES_BRONZOR", "SPECIES_ROGGENROLA",
        "SPECIES_PANCHAM", "SPECIES_NACLI", "SPECIES_GLIGAR", "SPECIES_LARVITAR",
    ],
    "wetland": [
        "SPECIES_LOTAD", "SPECIES_MARILL", "SPECIES_WOOPER", "SPECIES_CORPHISH",
        "SPECIES_BUIZEL", "SPECIES_SHELLOS", "SPECIES_TYMPOLE", "SPECIES_FROAKIE",
        "SPECIES_DEWPIDER", "SPECIES_CHEWTLE", "SPECIES_TADBULB", "SPECIES_GOOMY",
    ],
    "rainforest": [
        "SPECIES_ODDISH", "SPECIES_SHROOMISH", "SPECIES_TROPIUS", "SPECIES_KECLEON",
        "SPECIES_SCYTHER", "SPECIES_ROSELIA", "SPECIES_FOONGUS", "SPECIES_GOOMY",
        "SPECIES_FOMANTIS", "SPECIES_APPLIN", "SPECIES_SMOLIV", "SPECIES_DEERLING",
    ],
    "haunted": [
        "SPECIES_DUSKULL", "SPECIES_SHUPPET", "SPECIES_GASTLY", "SPECIES_MISDREAVUS",
        "SPECIES_DRIFLOON", "SPECIES_YAMASK", "SPECIES_LITWICK", "SPECIES_PHANTUMP",
        "SPECIES_MIMIKYU", "SPECIES_SINISTEA", "SPECIES_GREAVARD", "SPECIES_CUBONE",
    ],
}

ROUTE_LAND = {
    101: "early_meadow", 102: "early_meadow", 103: "early_meadow", 104: "forest",
    110: "electric", 111: "desert", 112: "volcano", 113: "volcano",
    114: "mountain", 115: "mountain", 116: "mountain", 117: "early_meadow",
    118: "wetland", 119: "rainforest", 120: "rainforest", 121: "rainforest",
    122: "haunted", 123: "rainforest",
}

WATER_EARLY = [
    "SPECIES_MAGIKARP", "SPECIES_WINGULL", "SPECIES_MARILL", "SPECIES_WOOPER",
    "SPECIES_CORPHISH", "SPECIES_BUIZEL", "SPECIES_SHELLOS", "SPECIES_TYMPOLE",
    "SPECIES_CLAUNCHER", "SPECIES_CHEWTLE", "SPECIES_FINIZEN", "SPECIES_HORSEA",
    "SPECIES_CHINCHOU", "SPECIES_CARVANHA", "SPECIES_WAILMER",
]
WATER_LATE = [
    "SPECIES_LANTURN", "SPECIES_PELIPPER", "SPECIES_FLOATZEL", "SPECIES_SHARPEDO",
    "SPECIES_SEADRA", "SPECIES_MANTINE", "SPECIES_CRAWDAUNT", "SPECIES_GASTRODON",
    "SPECIES_CLAWITZER", "SPECIES_DRAGALGE", "SPECIES_BARRASKEWDA", "SPECIES_DONDOZO",
    "SPECIES_JELLICENT", "SPECIES_STARMIE", "SPECIES_GYARADOS",
]


def fill(table, pool, offset=0):
    mons = table.get("mons", [])
    for i, mon in enumerate(mons):
        mon["species"] = pool[(i + offset) % len(pool)]


def main():
    data = json.loads(WILD.read_text())
    group = next(g for g in data["wild_encounter_groups"] if g.get("label") == "gWildMonHeaders")
    changed = 0

    for enc in group["encounters"]:
        map_name = enc.get("map", "")
        if not map_name.startswith("MAP_ROUTE"):
            continue
        try:
            route = int(map_name.removeprefix("MAP_ROUTE"))
        except ValueError:
            continue

        land_key = ROUTE_LAND.get(route)
        if land_key and enc.get("land_mons"):
            fill(enc["land_mons"], LAND_POOLS[land_key])
            changed += 1

        # Keep ocean progression sensible: later eastern routes get stronger water species.
        pool = WATER_LATE if route >= 124 else WATER_EARLY
        offset = route % len(pool)
        touched_water = False
        for field in ("water_mons", "fishing_mons", "rock_smash_mons"):
            if enc.get(field):
                fill(enc[field], pool, offset)
                offset += len(enc[field].get("mons", []))
                touched_water = True
        if touched_water:
            changed += 1

    WILD.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Applied safe biome encounter variety to {changed} route encounter tables.")


if __name__ == "__main__":
    main()
