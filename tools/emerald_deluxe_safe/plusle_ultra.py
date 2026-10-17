#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SPECIES_H = ROOT / "include/constants/species.h"
SPECIES_INFO = ROOT / "src/data/pokemon/species_info.h"
GEN3_INFO = ROOT / "src/data/pokemon/species_info/gen_3_families.h"
LEVELSET_DIR = ROOT / "src/data/pokemon/level_up_learnsets"
STARTERS = ROOT / "src/starter_choose.c"
BATTLE_SETUP = ROOT / "src/battle_setup.c"

CUSTOM_SPECIES = "SPECIES_PLUSLE_ULTRA"
LEVEL_SYMBOL = "sPlusleUltraLevelUpLearnset"
TEACH_SYMBOL = "sPlusleTeachableLearnset"

LEVEL_MOVES = """static const struct LevelUpMove sPlusleUltraLevelUpLearnset[] = {
    LEVEL_UP_MOVE( 1, MOVE_NUZZLE),
    LEVEL_UP_MOVE( 1, MOVE_QUICK_ATTACK),
    LEVEL_UP_MOVE( 5, MOVE_FAIRY_WIND),
    LEVEL_UP_MOVE( 8, MOVE_GRASS_KNOT),
    LEVEL_UP_MOVE(11, MOVE_SHOCK_WAVE),
    LEVEL_UP_MOVE(14, MOVE_DRAINING_KISS),
    LEVEL_UP_MOVE(18, MOVE_ELECTRO_BALL),
    LEVEL_UP_MOVE(21, MOVE_MUD_SHOT),
    LEVEL_UP_MOVE(24, MOVE_VOLT_SWITCH),
    LEVEL_UP_MOVE(27, MOVE_WATER_PULSE),
    LEVEL_UP_MOVE(30, MOVE_DAZZLING_GLEAM),
    LEVEL_UP_MOVE(33, MOVE_AURA_SPHERE),
    LEVEL_UP_MOVE(36, MOVE_DISCHARGE),
    LEVEL_UP_MOVE(40, MOVE_SHADOW_BALL),
    LEVEL_UP_MOVE(44, MOVE_CALM_MIND),
    LEVEL_UP_MOVE(48, MOVE_THUNDERBOLT),
    LEVEL_UP_MOVE(52, MOVE_MOONBLAST),
    LEVEL_UP_MOVE(57, MOVE_ENERGY_BALL),
    LEVEL_UP_MOVE(62, MOVE_THUNDER),
    LEVEL_UP_END
};
"""


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


def patch_levelup_learnsets():
    levelset_files = sorted(LEVELSET_DIR.glob("gen_*.h"))
    if not levelset_files:
        raise RuntimeError("Could not find generation learnset headers")

    patched = 0
    for path in levelset_files:
        text = path.read_text()
        if LEVEL_SYMBOL in text:
            continue
        anchor = "#if P_FAMILY_PLUSLE\n"
        if anchor not in text:
            raise RuntimeError(f"Could not find Plusle learnset insertion point in {path.name}")
        text = text.replace(
            anchor,
            "// Emerald Deluxe player-exclusive custom starter\n" + LEVEL_MOVES + "\n" + anchor,
            1,
        )
        path.write_text(text)
        patched += 1
    print(f"PlusleUltra learnset available in {len(levelset_files)} generation tables ({patched} patched).")


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
    if CUSTOM_SPECIES in text:
        return
    pat = re.compile(
        r"^(#define\s+FIRE_STARTER\s+\(IS_FRLG\s*\?\s*SPECIES_CHARMANDER\s*:\s*)SPECIES_TORCHIC(\s*\))$",
        re.M,
    )
    text2, count = pat.subn(rf"\g<1>{CUSTOM_SPECIES}\2", text, count=1)
    if count != 1:
        raise RuntimeError("Could not replace Emerald fire starter")
    STARTERS.write_text(text2)


def patch_starter_initial_moves():
    text = BATTLE_SETUP.read_text()
    marker = "// Emerald Deluxe PlusleUltra guaranteed starting moves"
    if marker in text:
        return

    if '#include "pokemon.h"\n' not in text:
        include_anchor = '#include "palette.h"\n'
        if include_anchor not in text:
            raise RuntimeError("Could not find battle_setup include insertion point")
        text = text.replace(include_anchor, include_anchor + '#include "pokemon.h"\n', 1)

    if '#include "constants/moves.h"\n' not in text:
        include_anchor = '#include "constants/items.h"\n'
        if include_anchor not in text:
            raise RuntimeError("Could not find constants include insertion point")
        text = text.replace(include_anchor, include_anchor + '#include "constants/moves.h"\n', 1)

    anchor = "    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n"
    if anchor not in text:
        raise RuntimeError("Could not find starter ScriptGiveMon call")

    forced_moves = (
        anchor
        + f"    {marker}\n"
        + f"    if (starterMon == {CUSTOM_SPECIES})\n"
        + "    {\n"
        + "        SetMonMoveSlot(&gPlayerParty[0], MOVE_NUZZLE, 0);\n"
        + "        SetMonMoveSlot(&gPlayerParty[0], MOVE_QUICK_ATTACK, 1);\n"
        + "    }\n"
    )
    text = text.replace(anchor, forced_moves, 1)
    BATTLE_SETUP.write_text(text)


def main():
    patch_species_enum()
    patch_levelup_learnsets()
    patch_species_info()
    patch_starter()
    patch_starter_initial_moves()
    print(
        "PlusleUltra pass: custom Electric/Fairy species added with Plusle graphics, "
        "70/65/65/125/85/135 stats, Berserk, dedicated custom level-up learnset, "
        "Plusle teachable compatibility, Torchic starter slot replaced, and "
        "Nuzzle + Quick Attack forced onto the level-5 starter after creation."
    )


if __name__ == "__main__":
    main()
