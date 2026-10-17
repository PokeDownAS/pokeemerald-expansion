#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SPECIES_H = ROOT / "include/constants/species.h"
SPECIES_INFO = ROOT / "src/data/pokemon/species_info.h"
GEN3_INFO = ROOT / "src/data/pokemon/species_info/gen_3_families.h"
LEVELSETS = ROOT / "src/data/pokemon/level_up_learnsets/gen_3.h"
STARTERS = ROOT / "src/starter_choose.c"

CUSTOM_SPECIES = "SPECIES_PLUSLE_ULTRA"
LEVEL_SYMBOL = "sPlusleUltraLevelUpLearnset"
TEACH_SYMBOL = "sPlusleUltraTeachableLearnset"

LEVEL_MOVES = [
    (1, "MOVE_NUZZLE"),
    (1, "MOVE_QUICK_ATTACK"),
    (5, "MOVE_FAIRY_WIND"),
    (8, "MOVE_GRASS_KNOT"),
    (11, "MOVE_SHOCK_WAVE"),
    (14, "MOVE_DRAINING_KISS"),
    (18, "MOVE_ELECTRO_BALL"),
    (21, "MOVE_MUD_SHOT"),
    (24, "MOVE_VOLT_SWITCH"),
    (27, "MOVE_WATER_PULSE"),
    (30, "MOVE_DAZZLING_GLEAM"),
    (33, "MOVE_AURA_SPHERE"),
    (36, "MOVE_DISCHARGE"),
    (40, "MOVE_SHADOW_BALL"),
    (44, "MOVE_CALM_MIND"),
    (48, "MOVE_THUNDERBOLT"),
    (52, "MOVE_MOONBLAST"),
    (57, "MOVE_ENERGY_BALL"),
    (62, "MOVE_THUNDER"),
]

EXTRA_TEACHABLE = [
    "MOVE_THUNDERBOLT", "MOVE_THUNDER", "MOVE_VOLT_SWITCH", "MOVE_CHARGE_BEAM",
    "MOVE_DAZZLING_GLEAM", "MOVE_PLAY_ROUGH", "MOVE_GRASS_KNOT", "MOVE_ENERGY_BALL",
    "MOVE_WATER_PULSE", "MOVE_AURA_SPHERE", "MOVE_SHADOW_BALL", "MOVE_PSYCHIC",
    "MOVE_CALM_MIND", "MOVE_LIGHT_SCREEN", "MOVE_REFLECT", "MOVE_PROTECT",
    "MOVE_SUBSTITUTE", "MOVE_REST", "MOVE_SLEEP_TALK", "MOVE_THUNDER_WAVE",
    "MOVE_TOXIC", "MOVE_SIGNAL_BEAM", "MOVE_U_TURN",
]


def extract_braced_block(text: str, marker: str):
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Could not find {marker}")
    line_start = text.rfind("\n", 0, start) + 1
    open_brace = text.find("{", start)
    if open_brace < 0:
        raise RuntimeError(f"Could not find opening brace after {marker}")
    depth = 0
    i = open_brace
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                while end < len(text) and text[end] in " \t":
                    end += 1
                if end < len(text) and text[end] == ",":
                    end += 1
                if end < len(text) and text[end] == ";":
                    end += 1
                return line_start, end, text[line_start:end]
        i += 1
    raise RuntimeError(f"Unclosed block for {marker}")


def patch_species_enum():
    text = SPECIES_H.read_text()
    if CUSTOM_SPECIES not in text:
        anchor = "    // Add any custom species between here and SPECIES_CUSTOM_END\n"
        if anchor not in text:
            raise RuntimeError("Could not find custom species insertion marker")
        text = text.replace(anchor, anchor + f"    {CUSTOM_SPECIES},\n", 1)
        SPECIES_H.write_text(text)


def patch_name_length():
    for path in (ROOT / "include/config").glob("*.h"):
        text = path.read_text(errors="ignore")
        if re.search(r"^#define\s+P_LONG_POKEMON_NAMES\s+", text, re.M):
            text2, count = re.subn(
                r"^(#define\s+P_LONG_POKEMON_NAMES\s+).*$",
                r"\g<1>GEN_9 // Emerald Deluxe: PlusleUltra uses an 11-character species name",
                text,
                count=1,
                flags=re.M,
            )
            if count:
                path.write_text(text2)
                return
    raise RuntimeError("Could not find P_LONG_POKEMON_NAMES config")


def patch_level_learnset():
    text = LEVELSETS.read_text()
    if LEVEL_SYMBOL in text:
        return
    block = "\n\n// Emerald Deluxe custom starter\n"
    block += f"static const struct LevelUpMove {LEVEL_SYMBOL}[] = {{\n"
    for level, move in LEVEL_MOVES:
        block += f"    LEVEL_UP_MOVE({level:2d}, {move}),\n"
    block += "    LEVEL_UP_END\n};\n"
    LEVELSETS.write_text(text + block)


def find_teachable_definition():
    symbol = "sPlusleTeachableLearnset"
    candidates = []
    for base in [ROOT / "src", ROOT / "include"]:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in {".h", ".c", ".inc"}:
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if symbol in text and re.search(rf"\b{symbol}\s*\[\s*\]", text):
                candidates.append((path, text))
    if not candidates:
        raise RuntimeError("Could not locate definition of sPlusleTeachableLearnset")
    return candidates[0]


def patch_teachable_learnset():
    path, text = find_teachable_definition()
    if TEACH_SYMBOL in text:
        return path
    start, end, original = extract_braced_block(text, "sPlusleTeachableLearnset")
    cloned = original.replace("sPlusleTeachableLearnset", TEACH_SYMBOL, 1)

    existing = set(re.findall(r"MOVE_[A-Z0-9_]+", cloned))
    moves_constants = (ROOT / "include/constants/moves.h").read_text(errors="ignore")
    additions = [m for m in EXTRA_TEACHABLE if m not in existing and m in moves_constants]

    close = cloned.rfind("}")
    if close < 0:
        raise RuntimeError("Malformed Plusle teachable learnset")
    before = cloned[:close]
    after = cloned[close:]

    terminator_matches = list(re.finditer(r"^\s*(?:MOVE_UNAVAILABLE|MOVE_NONE|TEACHABLE_LEARNSET_END)\s*,?\s*$", before, re.M))
    insertion = "".join(f"    {move},\n" for move in additions)
    if terminator_matches:
        pos = terminator_matches[-1].start()
        cloned = before[:pos] + insertion + before[pos:] + after
    else:
        cloned = before.rstrip() + "\n" + insertion + after

    text = text[:end] + "\n\n// Emerald Deluxe custom starter\n" + cloned + text[end:]
    path.write_text(text)
    return path


def set_field(block: str, field: str, value: str):
    pat = re.compile(rf"^(\s*\.{re.escape(field)}\s*=\s*).+?(,\s*)$", re.M)
    block2, count = pat.subn(rf"\g<1>{value}\2", block, count=1)
    if count != 1:
        raise RuntimeError(f"Could not set species field {field}")
    return block2


def patch_species_info():
    target = SPECIES_INFO.read_text()
    if f"[{CUSTOM_SPECIES}]" in target:
        return

    source = GEN3_INFO.read_text()
    _, _, plusle = extract_braced_block(source, "[SPECIES_PLUSLE]")
    custom = plusle.replace("[SPECIES_PLUSLE]", f"[{CUSTOM_SPECIES}]", 1)
    fields = {
        "baseHP": "70",
        "baseAttack": "65",
        "baseDefense": "65",
        "baseSpeed": "135",
        "baseSpAttack": "125",
        "baseSpDefense": "85",
        "types": "MON_TYPES(TYPE_ELECTRIC, TYPE_FAIRY)",
        "catchRate": "45",
        "expYield": "180",
        "abilities": "{ ABILITY_BERSERK, ABILITY_NONE, ABILITY_NONE }",
        "speciesName": '_("PlusleUltra")',
        "levelUpLearnset": LEVEL_SYMBOL,
        "teachableLearnset": TEACH_SYMBOL,
    }
    for field, value in fields.items():
        custom = set_field(custom, field, value)

    egg_marker = "    [SPECIES_EGG] ="
    if egg_marker not in target:
        raise RuntimeError("Could not find SPECIES_EGG insertion point")
    insertion = "\n    // Emerald Deluxe player-exclusive custom starter\n" + custom + "\n\n"
    target = target.replace(egg_marker, insertion + egg_marker, 1)
    SPECIES_INFO.write_text(target)


def patch_starter():
    text = STARTERS.read_text()
    pat = re.compile(r"^(#define\s+STARTER_MON_MIDDLE\s+).*$", re.M)
    text2, count = pat.subn(rf"\g<1>{CUSTOM_SPECIES}", text, count=1)
    if count != 1:
        raise RuntimeError("Could not replace middle starter")
    STARTERS.write_text(text2)


def main():
    patch_species_enum()
    patch_name_length()
    patch_level_learnset()
    teach_path = patch_teachable_learnset()
    patch_species_info()
    patch_starter()
    print(
        "PlusleUltra pass: custom Electric/Fairy species added with Plusle graphics, "
        "70/65/65/125/85/135 stats, Berserk, custom Gym-coverage level learnset, "
        f"expanded Plusle teachable compatibility in {teach_path.relative_to(ROOT)}, and Torchic starter slot replaced."
    )


if __name__ == "__main__":
    main()
