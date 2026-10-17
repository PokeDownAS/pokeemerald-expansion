#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"

POOLS = {
    "woods": [
        "SPECIES_SHROOMISH", "SPECIES_WURMPLE", "SPECIES_CATERPIE", "SPECIES_BUDEW",
        "SPECIES_SEWADDLE", "SPECIES_GRUBBIN", "SPECIES_PIKACHU", "SPECIES_APPLIN",
        "SPECIES_PHANTUMP", "SPECIES_TAROUNTULA", "SPECIES_SCYTHER", "SPECIES_ODDISH",
    ],
    "granite": [
        "SPECIES_ZUBAT", "SPECIES_GEODUDE", "SPECIES_MAKUHITA", "SPECIES_ARON",
        "SPECIES_ROGGENROLA", "SPECIES_WOOBAT", "SPECIES_DRILBUR", "SPECIES_NOIBAT",
        "SPECIES_ROCKRUFF", "SPECIES_NACLI", "SPECIES_RIOLU", "SPECIES_SABLEYE",
    ],
    "rusturf": [
        "SPECIES_WHISMUR", "SPECIES_ZUBAT", "SPECIES_GEODUDE", "SPECIES_MACHOP",
        "SPECIES_ROGGENROLA", "SPECIES_NOIBAT", "SPECIES_ROCKRUFF", "SPECIES_NACLI",
        "SPECIES_WOOBAT", "SPECIES_ARON", "SPECIES_RIOLU", "SPECIES_DRILBUR",
    ],
    "fiery": [
        "SPECIES_NUMEL", "SPECIES_SLUGMA", "SPECIES_TORKOAL", "SPECIES_GROWLITHE",
        "SPECIES_HOUNDOUR", "SPECIES_MAGBY", "SPECIES_DARUMAKA", "SPECIES_SALANDIT",
        "SPECIES_SIZZLIPEDE", "SPECIES_ROLYCOLY", "SPECIES_CHARCADET", "SPECIES_CAPSAKID",
    ],
    "meteor": [
        "SPECIES_ZUBAT", "SPECIES_SOLROCK", "SPECIES_LUNATONE", "SPECIES_BAGON",
        "SPECIES_CLEFAIRY", "SPECIES_NOIBAT", "SPECIES_CARBINK", "SPECIES_MINIOR",
        "SPECIES_GLIMMET", "SPECIES_DRILBUR", "SPECIES_LARVITAR", "SPECIES_AXEW",
    ],
    "shoal": [
        "SPECIES_SPHEAL", "SPECIES_SNORUNT", "SPECIES_SEEL", "SPECIES_SWINUB",
        "SPECIES_BERGMITE", "SPECIES_CRYOGONAL", "SPECIES_SANDYGAST", "SPECIES_SNOM",
        "SPECIES_CETODDLE", "SPECIES_CLOBBOPUS", "SPECIES_FRILLISH", "SPECIES_DELIBIRD",
    ],
    "victory": [
        "SPECIES_GOLBAT", "SPECIES_LAIRON", "SPECIES_HARIYAMA", "SPECIES_MEDICHAM",
        "SPECIES_EXCADRILL", "SPECIES_HAXORUS", "SPECIES_GABITE", "SPECIES_GOODRA",
        "SPECIES_KOMMO_O", "SPECIES_CORVIKNIGHT", "SPECIES_BAXCALIBUR", "SPECIES_KINGAMBIT",
    ],
    "seafloor": [
        "SPECIES_GOLBAT", "SPECIES_GRAVELER", "SPECIES_CRAWDAUNT", "SPECIES_SHARPEDO",
        "SPECIES_CARBINK", "SPECIES_BARBARACLE", "SPECIES_GOLISOPOD", "SPECIES_CLOBBOPUS",
        "SPECIES_GLIMMET", "SPECIES_DONDOZO", "SPECIES_DRAGALGE", "SPECIES_WHISCASH",
    ],
    "origin": [
        "SPECIES_GOLBAT", "SPECIES_SABLEYE", "SPECIES_BANETTE", "SPECIES_DUSCLOPS",
        "SPECIES_CHIMECHO", "SPECIES_YAMASK", "SPECIES_PHANTUMP", "SPECIES_MIMIKYU",
        "SPECIES_SINISTEA", "SPECIES_GREAVARD", "SPECIES_GLIMMET", "SPECIES_ABSOL",
    ],
    "new_mauville": [
        "SPECIES_MAGNEMITE", "SPECIES_VOLTORB", "SPECIES_ELECTRIKE", "SPECIES_MAREEP",
        "SPECIES_SHINX", "SPECIES_KLINK", "SPECIES_HELIOPTILE", "SPECIES_TOGEDEMARU",
        "SPECIES_YAMPER", "SPECIES_PAWMI", "SPECIES_TADBULB", "SPECIES_ROTOM",
    ],
}

WATER = {
    "cave_water": [
        "SPECIES_ZUBAT", "SPECIES_WOOPER", "SPECIES_BARBOACH", "SPECIES_CORPHISH",
        "SPECIES_SHELLOS", "SPECIES_TYMPOLE", "SPECIES_DEWPIDER", "SPECIES_CHEWTLE",
        "SPECIES_CLOBBOPUS", "SPECIES_FRILLISH", "SPECIES_WIMPOD", "SPECIES_BASCULIN",
        "SPECIES_WHISCASH", "SPECIES_CRAWDAUNT", "SPECIES_GASTRODON",
    ],
    "shoal_water": [
        "SPECIES_SEEL", "SPECIES_SPHEAL", "SPECIES_SHELLDER", "SPECIES_CHINCHOU",
        "SPECIES_CLAMPERL", "SPECIES_MANTYKE", "SPECIES_FRILLISH", "SPECIES_CLOBBOPUS",
        "SPECIES_ARROKUDA", "SPECIES_FINIZEN", "SPECIES_DEWGONG", "SPECIES_WALREIN",
        "SPECIES_LANTURN", "SPECIES_JELLICENT", "SPECIES_BARRASKEWDA",
    ],
    "seafloor_water": [
        "SPECIES_SHARPEDO", "SPECIES_CRAWDAUNT", "SPECIES_MANTINE", "SPECIES_SEADRA",
        "SPECIES_GASTRODON", "SPECIES_JELLICENT", "SPECIES_CLAWITZER", "SPECIES_DRAGALGE",
        "SPECIES_GOLISOPOD", "SPECIES_BARRASKEWDA", "SPECIES_DONDOZO", "SPECIES_STARMIE",
        "SPECIES_GYARADOS", "SPECIES_WAILORD", "SPECIES_KINGDRA",
    ],
}

TARGETS = [
    (("PETALBURG_WOODS", "PETALBURGWOODS"), "woods", None),
    (("GRANITE_CAVE", "GRANITECAVE"), "granite", "cave_water"),
    (("RUSTURF_TUNNEL", "RUSTURFTUNNEL"), "rusturf", "cave_water"),
    (("FIERY_PATH", "FIERYPATH"), "fiery", None),
    (("METEOR_FALLS", "METEORFALLS"), "meteor", "cave_water"),
    (("SHOAL_CAVE", "SHOALCAVE"), "shoal", "shoal_water"),
    (("VICTORY_ROAD", "VICTORYROAD"), "victory", "cave_water"),
    (("SEAFLOOR_CAVERN", "SEAFLOORCAVERN"), "seafloor", "seafloor_water"),
    (("CAVE_OF_ORIGIN", "CAVEOFORIGIN"), "origin", "cave_water"),
    (("NEW_MAUVILLE", "NEWMAUVILLE"), "new_mauville", "cave_water"),
]


def fill(table, pool, offset=0):
    mons = table.get("mons", [])
    for i, mon in enumerate(mons):
        mon["species"] = pool[(i + offset) % len(pool)]
    return len(mons)


def target_for(map_name):
    upper = map_name.upper()
    for fragments, land_key, water_key in TARGETS:
        if any(fragment in upper for fragment in fragments):
            return land_key, water_key
    return None, None


def main():
    data = json.loads(WILD.read_text())
    group = next(g for g in data["wild_encounter_groups"] if g.get("label") == "gWildMonHeaders")
    touched_maps = []

    for enc in group["encounters"]:
        map_name = enc.get("map", "")
        land_key, water_key = target_for(map_name)
        if not land_key:
            continue

        changed = False
        if enc.get("land_mons"):
            fill(enc["land_mons"], POOLS[land_key])
            changed = True

        if water_key:
            pool = WATER[water_key]
            offset = 0
            for field in ("water_mons", "fishing_mons", "rock_smash_mons"):
                table = enc.get(field)
                if table:
                    offset += fill(table, pool, offset)
                    changed = True

        if changed:
            touched_maps.append(map_name)

    WILD.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Updated {len(touched_maps)} cave/forest/dungeon maps including internal water tables.")
    for name in touched_maps:
        print(name)


if __name__ == "__main__":
    main()
