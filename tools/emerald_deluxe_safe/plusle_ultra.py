#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SPECIES_H = ROOT / "include/constants/species.h"
SPECIES_INFO = ROOT / "src/data/pokemon/species_info.h"
GEN3_INFO = ROOT / "src/data/pokemon/species_info/gen_3_families.h"
STARTERS = ROOT / "src/starter_choose.c"

CUSTOM_SPECIES = "SPECIES_PLUSLE_ULTRA"
# Reuse Plusle's existing learnset tables for build-order safety. The custom
# starter keeps its custom stats, typing, ability, identity and starter slot.
LEVEL_SYMBOL = "sPlusleLevelUpLearnset"
TEACH_SYMBOL = "sPlusleTeachableLearnset"


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
        "speciesName": '_("PlusleUltr")',
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
    pat = re.compile(
        r"^(#define\s+FIRE_STARTER\s+\(IS_FRLG\s*\?\s*SPECIES_CHARMANDER\s*:\s*)SPECIES_TORCHIC(\s*\))$",
        re.M,
    )
    text2, count = pat.subn(rf"\g<1>{CUSTOM_SPECIES}\2", text, count=1)
    if count != 1:
        raise RuntimeError("Could not replace Emerald fire starter")
    STARTERS.write_text(text2)


def main():
    patch_species_enum()
    patch_species_info()
    patch_starter()
    print(
        "PlusleUltra pass: custom Electric/Fairy species added with Plusle graphics, "
        "70/65/65/125/85/135 stats, Berserk, Plusle learnset compatibility, "
        "and Torchic starter slot replaced."
    )


if __name__ == "__main__":
    main()
