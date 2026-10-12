#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"

# Each land pool contains at least one species from every generation 1-9.
# Extra choices keep routes at 10+ distinct species while staying biome-appropriate.
LAND_POOLS = {
    "meadow_early": [
        ("SPECIES_RATTATA",1),("SPECIES_SENTRET",2),("SPECIES_ZIGZAGOON",3),
        ("SPECIES_BIDOOF",4),("SPECIES_LILLIPUP",5),("SPECIES_BUNNELBY",6),
        ("SPECIES_YUNGOOS",7),("SPECIES_SKWOVET",8),("SPECIES_LECHONK",9),
        ("SPECIES_PIDGEY",1),("SPECIES_TAILLOW",3),("SPECIES_STARLY",4),
    ],
    "forest_early": [
        ("SPECIES_CATERPIE",1),("SPECIES_LEDYBA",2),("SPECIES_WURMPLE",3),
        ("SPECIES_KRICKETOT",4),("SPECIES_SEWADDLE",5),("SPECIES_SCATTERBUG",6),
        ("SPECIES_GRUBBIN",7),("SPECIES_BLIPBUG",8),("SPECIES_TAROUNTULA",9),
        ("SPECIES_ODDISH",1),("SPECIES_SHROOMISH",3),("SPECIES_BUDEW",4),
    ],
    "coast_early": [
        ("SPECIES_KRABBY",1),("SPECIES_MARILL",2),("SPECIES_WINGULL",3),
        ("SPECIES_SHELLOS",4),("SPECIES_TYMPOLE",5),("SPECIES_BINACLE",6),
        ("SPECIES_DEWPIDER",7),("SPECIES_CHEWTLE",8),("SPECIES_WIGLETT",9),
        ("SPECIES_POLIWAG",1),("SPECIES_CORPHISH",3),("SPECIES_BUIZEL",4),
    ],
    "electric_city": [
        ("SPECIES_MAGNEMITE",1),("SPECIES_MAREEP",2),("SPECIES_ELECTRIKE",3),
        ("SPECIES_SHINX",4),("SPECIES_BLITZLE",5),("SPECIES_HELIOPTILE",6),
        ("SPECIES_TOGEDEMARU",7),("SPECIES_YAMPER",8),("SPECIES_PAWMI",9),
        ("SPECIES_VOLTORB",1),("SPECIES_PLUSLE",3),("SPECIES_PACHIRISU",4),
    ],
    "desert_mid": [
        ("SPECIES_SANDSHREW",1),("SPECIES_PHANPY",2),("SPECIES_TRAPINCH",3),
        ("SPECIES_HIPPOPOTAS",4),("SPECIES_SANDILE",5),("SPECIES_HELIOPTILE",6),
        ("SPECIES_MUDBRAY",7),("SPECIES_SILICOBRA",8),("SPECIES_NACLI",9),
        ("SPECIES_BALTOY",3),("SPECIES_CACNEA",3),("SPECIES_DRILBUR",5),
    ],
    "volcanic_mid": [
        ("SPECIES_GROWLITHE",1),("SPECIES_SLUGMA",2),("SPECIES_NUMEL",3),
        ("SPECIES_MAGBY",4),("SPECIES_DARUMAKA",5),("SPECIES_LITLEO",6),
        ("SPECIES_SALANDIT",7),("SPECIES_SIZZLIPEDE",8),("SPECIES_CAPSAKID",9),
        ("SPECIES_GEODUDE",1),("SPECIES_TORKOAL",3),("SPECIES_ROGGENROLA",5),
    ],
    "ash_mid": [
        ("SPECIES_KOFFING",1),("SPECIES_SLUGMA",2),("SPECIES_SPINDA",3),
        ("SPECIES_BRONZOR",4),("SPECIES_TRUBBISH",5),("SPECIES_ESPURR",6),
        ("SPECIES_SALANDIT",7),("SPECIES_ROLYCOLY",8),("SPECIES_SHROODLE",9),
        ("SPECIES_SKARMORY",2),("SPECIES_NUMEL",3),("SPECIES_SANDILE",5),
    ],
    "mountain_mid": [
        ("SPECIES_GEODUDE",1),("SPECIES_TEDDIURSA",2),("SPECIES_ARON",3),
        ("SPECIES_BRONZOR",4),("SPECIES_ROGGENROLA",5),("SPECIES_PANCHAM",6),
        ("SPECIES_ROCKRUFF",7),("SPECIES_ROLYCOLY",8),("SPECIES_NACLI",9),
        ("SPECIES_MACHOP",1),("SPECIES_SWABLU",3),("SPECIES_RIOLU",4),
    ],
    "meadow_mid": [
        ("SPECIES_PONYTA",1),("SPECIES_MAREEP",2),("SPECIES_ROSELIA",3),
        ("SPECIES_BUNEARY",4),("SPECIES_DEERLING",5),("SPECIES_FLETCHLING",6),
        ("SPECIES_STUFFUL",7),("SPECIES_WOOLOO",8),("SPECIES_FIDOUGH",9),
        ("SPECIES_TAUROS",1),("SPECIES_SKITTY",3),("SPECIES_AUDINO",5),
    ],
    "wetland_mid": [
        ("SPECIES_POLIWAG",1),("SPECIES_WOOPER",2),("SPECIES_LOTAD",3),
        ("SPECIES_SHELLOS",4),("SPECIES_TYMPOLE",5),("SPECIES_FROAKIE",6),
        ("SPECIES_DEWPIDER",7),("SPECIES_CHEWTLE",8),("SPECIES_TADBULB",9),
        ("SPECIES_MARILL",2),("SPECIES_CORPHISH",3),("SPECIES_BUIZEL",4),
    ],
    "rainforest_mid": [
        ("SPECIES_ODDISH",1),("SPECIES_HOOTHOOT",2),("SPECIES_SHROOMISH",3),
        ("SPECIES_CARNIVINE",4),("SPECIES_SEWADDLE",5),("SPECIES_GOOMY",6),
        ("SPECIES_FOMANTIS",7),("SPECIES_APPLIN",8),("SPECIES_SMOLIV",9),
        ("SPECIES_SCYTHER",1),("SPECIES_TROPIUS",3),("SPECIES_FOONGUS",5),
    ],
    "tropical_mid": [
        ("SPECIES_EXEGGCUTE",1),("SPECIES_GIRAFARIG",2),("SPECIES_TROPIUS",3),
        ("SPECIES_BUNEARY",4),("SPECIES_DEERLING",5),("SPECIES_PANCHAM",6),
        ("SPECIES_STUFFUL",7),("SPECIES_APPLIN",8),("SPECIES_SMOLIV",9),
        ("SPECIES_TAUROS",1),("SPECIES_KECLEON",3),("SPECIES_GOGOAT",6),
    ],
    "haunted_mid": [
        ("SPECIES_GASTLY",1),("SPECIES_MISDREAVUS",2),("SPECIES_DUSKULL",3),
        ("SPECIES_DRIFLOON",4),("SPECIES_YAMASK",5),("SPECIES_PHANTUMP",6),
        ("SPECIES_MIMIKYU",7),("SPECIES_SINISTEA",8),("SPECIES_GREAVARD",9),
        ("SPECIES_CUBONE",1),("SPECIES_SHUPPET",3),("SPECIES_LITWICK",5),
    ],
}

# 15 unique marine species per pool so water-only routes still exceed the 10-species target.
WATER_POOLS = {
    "early_a": [
        ("SPECIES_MAGIKARP",1),("SPECIES_WOOPER",2),("SPECIES_WINGULL",3),
        ("SPECIES_BUIZEL",4),("SPECIES_TYMPOLE",5),("SPECIES_CLAUNCHER",6),
        ("SPECIES_WISHIWASHI",7),("SPECIES_ARROKUDA",8),("SPECIES_FINIZEN",9),
        ("SPECIES_POLIWAG",1),("SPECIES_MARILL",2),("SPECIES_CORPHISH",3),
        ("SPECIES_SHELLOS",4),("SPECIES_DUCKLETT",5),("SPECIES_BINACLE",6),
    ],
    "early_b": [
        ("SPECIES_HORSEA",1),("SPECIES_CHINCHOU",2),("SPECIES_CARVANHA",3),
        ("SPECIES_FINNEON",4),("SPECIES_BASCULIN",5),("SPECIES_SKRELP",6),
        ("SPECIES_MAREANIE",7),("SPECIES_CHEWTLE",8),("SPECIES_WIGLETT",9),
        ("SPECIES_KRABBY",1),("SPECIES_REMORAID",2),("SPECIES_WAILMER",3),
        ("SPECIES_MANTYKE",4),("SPECIES_FRILLISH",5),("SPECIES_INKAY",6),
    ],
    "late_a": [
        ("SPECIES_GOLDUCK",1),("SPECIES_LANTURN",2),("SPECIES_PELIPPER",3),
        ("SPECIES_FLOATZEL",4),("SPECIES_BASCULIN",5),("SPECIES_CLAWITZER",6),
        ("SPECIES_WISHIWASHI",7),("SPECIES_BARRASKEWDA",8),("SPECIES_FINIZEN",9),
        ("SPECIES_SEADRA",1),("SPECIES_MANTINE",2),("SPECIES_SHARPEDO",3),
        ("SPECIES_GASTRODON",4),("SPECIES_JELLICENT",5),("SPECIES_DRAGALGE",6),
    ],
    "late_b": [
        ("SPECIES_STARMIE",1),("SPECIES_OCTILLERY",2),("SPECIES_WAILMER",3),
        ("SPECIES_MANTYKE",4),("SPECIES_CARRACOSTA",5),("SPECIES_BARBARACLE",6),
        ("SPECIES_MAREANIE",7),("SPECIES_CRAMORANT",8),("SPECIES_WIGLETT",9),
        ("SPECIES_KINGLER",1),("SPECIES_QWILFISH",2),("SPECIES_CRAWDAUNT",3),
        ("SPECIES_LUMINEON",4),("SPECIES_ALOMOMOLA",5),("SPECIES_MALAMAR",6),
    ],
    "late_c": [
        ("SPECIES_DEWGONG",1),("SPECIES_CORSOLA",2),("SPECIES_CLAMPERL",3),
        ("SPECIES_LUMINEON",4),("SPECIES_SEISMITOAD",5),("SPECIES_DRAGALGE",6),
        ("SPECIES_GOLISOPOD",7),("SPECIES_CRAMORANT",8),("SPECIES_DONDOZO",9),
        ("SPECIES_TENTACRUEL",1),("SPECIES_LANTURN",2),("SPECIES_WHISCASH",3),
        ("SPECIES_GASTRODON",4),("SPECIES_SWANNA",5),("SPECIES_CLAWITZER",6),
    ],
}

ROUTE_LAND = {
    101:"meadow_early",102:"meadow_early",103:"coast_early",104:"forest_early",
    110:"electric_city",111:"desert_mid",112:"volcanic_mid",113:"ash_mid",
    114:"mountain_mid",115:"mountain_mid",116:"mountain_mid",117:"meadow_mid",
    118:"wetland_mid",119:"rainforest_mid",120:"rainforest_mid",121:"tropical_mid",
    122:"haunted_mid",123:"tropical_mid",
}

# Ocean routes alternate curated marine pools so neighboring sea routes are not copies.
ROUTE_WATER = {
    102:"early_a",103:"early_b",104:"early_a",
    105:"early_a",106:"early_b",107:"early_a",108:"early_b",109:"early_a",
    118:"early_b",119:"early_a",120:"early_b",121:"early_a",122:"early_b",123:"early_a",
    124:"late_a",125:"late_b",126:"late_c",127:"late_a",128:"late_b",
    129:"late_c",130:"late_a",131:"late_b",132:"late_c",133:"late_a",134:"late_b",
}


def assign_unique(table, pool):
    mons = table.get("mons", [])
    for i, mon in enumerate(mons):
        mon["species"] = pool[i % len(pool)][0]


def main():
    data = json.loads(WILD.read_text())
    group = next(x for x in data["wild_encounter_groups"] if x.get("label") == "gWildMonHeaders")
    touched = set()

    for enc in group["encounters"]:
        map_name = enc.get("map", "")
        if not map_name.startswith("MAP_ROUTE"):
            continue
        try:
            route = int(map_name.removeprefix("MAP_ROUTE"))
        except ValueError:
            continue
        if not 101 <= route <= 134:
            continue

        land_key = ROUTE_LAND.get(route)
        if land_key and enc.get("land_mons"):
            assign_unique(enc["land_mons"], LAND_POOLS[land_key])

        water_key = ROUTE_WATER.get(route)
        if water_key:
            pool = WATER_POOLS[water_key]
            # Give the combined water/fishing/rock-smash tables a continuous pass through
            # the pool so water-only routes have 15+ distinct species instead of repeats.
            pos = 0
            for field in ("water_mons", "fishing_mons", "rock_smash_mons"):
                table = enc.get(field)
                if not table:
                    continue
                mons = table.get("mons", [])
                for mon in mons:
                    mon["species"] = pool[pos % len(pool)][0]
                    pos += 1

        # Validate the user-facing promise route-by-route using all encounter methods.
        species = []
        for field in ("land_mons", "water_mons", "fishing_mons", "rock_smash_mons"):
            table = enc.get(field)
            if table:
                species.extend(m["species"] for m in table.get("mons", []))
        unique = set(species)
        if len(unique) < 10:
            raise RuntimeError(f"{map_name} has only {len(unique)} species")

        # Validate Gen 1-9 coverage from the curated pool(s) used on this route.
        gens = set()
        if land_key:
            gens.update(g for _, g in LAND_POOLS[land_key])
        if water_key:
            gens.update(g for _, g in WATER_POOLS[water_key])
        if gens and not set(range(1,10)).issubset(gens):
            raise RuntimeError(f"{map_name} is missing generation coverage: {sorted(gens)}")
        touched.add(route)

    expected = set(range(101,135))
    missing = sorted(expected - touched)
    if missing:
        raise RuntimeError(f"No wild encounter record found for routes: {missing}")

    WILD.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Route variety applied to {len(touched)} routes; every route has 10+ species and Gen 1-9 representation in its curated encounter pool.")

if __name__ == "__main__":
    main()
