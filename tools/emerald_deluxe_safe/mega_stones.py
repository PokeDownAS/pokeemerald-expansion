#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ITEMS = ROOT / "src/data/items.h"
LILYCOVE = ROOT / "data/maps/LilycoveCity_DepartmentStore_4F/scripts.inc"

STONE_PRICE = 10000

LATE_HINTS = {
    "CHARIZARDITE_X", "CHARIZARDITE_Y", "GENGARITE", "KANGASKHANITE",
    "GYARADOSITE", "MAWILITE", "MEDICHAMITE", "MANECTITE", "SALAMENCITE",
    "METAGROSSITE", "LATIASITE", "LATIOSITE", "GARCHOMPITE", "LUCARIONITE",
    "TYRANITARITE", "GARDEVOIRITE", "GALLADITE", "DIANCITE", "SCEPTILITE",
    "BLAZIKENITE", "SWAMPERTITE",
}
VERY_LATE_HINTS = {
    "MEWTWONITE_X", "MEWTWONITE_Y", "RAYQUAZITE", "DIANCITE",
    "METAGROSSITE", "SALAMENCITE", "GARCHOMPITE", "TYRANITARITE",
}


def discover_mega_stones(items_text: str):
    stones = []
    block_re = re.compile(r"\[(ITEM_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n\s*\},", re.S)
    for match in block_re.finditer(items_text):
        item, body = match.group(1), match.group(2)
        if "HOLD_EFFECT_MEGA_STONE" in body:
            stones.append(item)
    return stones


def price_mega_stones(items_text: str, stones):
    for item in stones:
        pat = re.compile(rf"(\[{re.escape(item)}\]\s*=\s*\{{.*?\.price\s*=\s*)\d+(\s*,)", re.S)
        items_text, count = pat.subn(rf"\g<1>{STONE_PRICE}\2", items_text, count=1)
        if count != 1:
            raise RuntimeError(f"Could not set price for {item}")
    return items_text


def split_stones(stones):
    early, late, very_late = [], [], []
    for item in stones:
        key = item.replace("ITEM_", "")
        if key in VERY_LATE_HINTS:
            very_late.append(item)
        elif key in LATE_HINTS:
            late.append(item)
        else:
            early.append(item)
    return early, late, very_late


def mart_block(label, stones):
    lines = [f"{label}:"]
    lines += [f"\t.2byte {item}" for item in stones]
    lines.append("\tpokemartlistend")
    return "\n".join(lines)


def patch_lilycove(script: str, stones):
    early, late, very_late = split_stones(stones)

    old_clerk = re.compile(
        r"LilycoveCity_DepartmentStore_4F_EventScript_ClerkRight::.*?\n\s*\.align 2\nLilycoveCity_DepartmentStore_4F_Pokemart_DefenseTMs:.*?\tpokemartlistend",
        re.S,
    )
    new_clerk = (
        "LilycoveCity_DepartmentStore_4F_EventScript_ClerkRight::\n"
        "\tlock\n"
        "\tfaceplayer\n"
        "\tmessage gText_HowMayIServeYou\n"
        "\twaitmessage\n"
        "\tgoto_if_set FLAG_BADGE08_GET, LilycoveCity_DepartmentStore_4F_EventScript_MegaMartFinal\n"
        "\tgoto_if_set FLAG_BADGE07_GET, LilycoveCity_DepartmentStore_4F_EventScript_MegaMartLate\n"
        "\tpokemart LilycoveCity_DepartmentStore_4F_Pokemart_MegaEarly\n"
        "\tgoto LilycoveCity_DepartmentStore_4F_EventScript_MegaMartFinish\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_MegaMartLate::\n"
        "\tpokemart LilycoveCity_DepartmentStore_4F_Pokemart_MegaLate\n"
        "\tgoto LilycoveCity_DepartmentStore_4F_EventScript_MegaMartFinish\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_MegaMartFinal::\n"
        "\tpokemart LilycoveCity_DepartmentStore_4F_Pokemart_MegaFinal\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_MegaMartFinish::\n"
        "\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n\n"
        "\t.align 2\n"
        + mart_block("LilycoveCity_DepartmentStore_4F_Pokemart_MegaEarly", early)
        + "\n\n"
        + mart_block("LilycoveCity_DepartmentStore_4F_Pokemart_MegaLate", early + late)
        + "\n\n"
        + mart_block("LilycoveCity_DepartmentStore_4F_Pokemart_MegaFinal", early + late + very_late)
    )
    script, count = old_clerk.subn(new_clerk, script, count=1)
    if count != 1:
        raise RuntimeError("Could not replace Lilycove right-clerk mart")

    new_gent = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Gentleman::\n"
        "\tlock\n"
        "\tfaceplayer\n"
        "\tcheckitem ITEM_MEGA_RING\n"
        "\tgoto_if_eq VAR_RESULT, TRUE, LilycoveCity_DepartmentStore_4F_EventScript_GentlemanAlreadyHasRing\n"
        "\tgoto_if_unset FLAG_BADGE06_GET, LilycoveCity_DepartmentStore_4F_EventScript_GentlemanTooEarly\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_GiveMegaRing, MSGBOX_DEFAULT\n"
        "\tgiveitem ITEM_MEGA_RING\n"
        "\tgoto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull\n"
        "\trelease\n"
        "\tend\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_GentlemanTooEarly::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_MegaRingTooEarly, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_GentlemanAlreadyHasRing::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_MegaStoneShop, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n"
    )

    # The repository stores the original gentleman script; generated versions only
    # exist in CI workspaces. Support both so this remains repeatable.
    original_gent = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Gentleman::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_AttackOrDefenseTM, MSGBOX_NPC\n"
        "\tend\n"
    )
    if original_gent in script:
        script = script.replace(original_gent, new_gent, 1)
    else:
        generated_gent = re.compile(
            r"LilycoveCity_DepartmentStore_4F_EventScript_Gentleman::.*?(?=\nLilycoveCity_DepartmentStore_4F_EventScript_Woman::)",
            re.S,
        )
        script, count = generated_gent.subn(new_gent.rstrip() + "\n", script, count=1)
        if count != 1:
            raise RuntimeError("Could not patch Mega Ring progression NPC")

    if "LilycoveCity_DepartmentStore_4F_Text_MegaRingTooEarly:" not in script:
        script += (
            "\nLilycoveCity_DepartmentStore_4F_Text_MegaRingTooEarly:\n"
            "\t.string \"Mega Evolution is powerful.\\p\"\n"
            "\t.string \"Come back after you've proven yourself\\n\"\n"
            "\t.string \"with six Gym Badges.$\"\n"
        )
    if "LilycoveCity_DepartmentStore_4F_Text_GiveMegaRing:" not in script:
        script += (
            "\nLilycoveCity_DepartmentStore_4F_Text_GiveMegaRing:\n"
            "\t.string \"You've come at the right time!\\p\"\n"
            "\t.string \"This MEGA RING lets a Trainer draw out\\n\"\n"
            "\t.string \"a Pokemon's hidden Mega power.\\p\"\n"
            "\t.string \"Take it. The clerk's stock expands as\\n\"\n"
            "\t.string \"you earn more Badges.$\"\n\n"
            "LilycoveCity_DepartmentStore_4F_Text_MegaStoneShop:\n"
            "\t.string \"The right-hand clerk stocks MEGA STONES.\\p\"\n"
            "\t.string \"More powerful stones appear after the\\n\"\n"
            "\t.string \"seventh and eighth Badges.$\"\n"
        )
    return script, len(early), len(late), len(very_late)


def main():
    items_text = ITEMS.read_text()
    stones = discover_mega_stones(items_text)
    if not stones:
        raise RuntimeError("No Mega Stones discovered in item data")

    ITEMS.write_text(price_mega_stones(items_text, stones))
    patched, early, late, very_late = patch_lilycove(LILYCOVE.read_text(), stones)
    LILYCOVE.write_text(patched)
    print(f"Mega progression: {early} stones at 6 badges, +{late} at 7 badges, +{very_late} at 8 badges; all priced at {STONE_PRICE}.")


if __name__ == "__main__":
    main()
