#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ITEMS = ROOT / "src/data/items.h"
LILYCOVE = ROOT / "data/maps/LilycoveCity_DepartmentStore_4F/scripts.inc"

STONE_PRICE = 10000


def discover_mega_stones(items_text: str):
    stones = []
    # Read actual item definitions rather than hard-coding a generation list. This
    # automatically includes any Mega Stones supported by this expansion branch.
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


def patch_lilycove(script: str, stones):
    marker = "LilycoveCity_DepartmentStore_4F_Pokemart_DefenseTMs:\n"
    start = script.find(marker)
    if start < 0:
        raise RuntimeError("Could not find Lilycove 4F right-clerk mart")
    end = script.find("\tpokemartlistend", start)
    if end < 0:
        raise RuntimeError("Could not find Lilycove mart list end")

    original_list = script[start + len(marker):end]
    # Remove prior generated Mega Stone lines so the script remains idempotent.
    original_lines = [line for line in original_list.splitlines() if not any(item in line for item in stones)]
    stone_lines = [f"\t.2byte {item}" for item in stones]
    new_list = "\n".join(original_lines + stone_lines) + "\n"
    script = script[:start + len(marker)] + new_list + script[end:]

    old_gent = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Gentleman::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_AttackOrDefenseTM, MSGBOX_NPC\n"
        "\tend\n"
    )
    new_gent = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Gentleman::\n"
        "\tlock\n"
        "\tfaceplayer\n"
        "\tcheckitem ITEM_MEGA_RING\n"
        "\tgoto_if_eq VAR_RESULT, TRUE, LilycoveCity_DepartmentStore_4F_EventScript_GentlemanAlreadyHasRing\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_GiveMegaRing, MSGBOX_DEFAULT\n"
        "\tgiveitem ITEM_MEGA_RING\n"
        "\tgoto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull\n"
        "\trelease\n"
        "\tend\n\n"
        "LilycoveCity_DepartmentStore_4F_EventScript_GentlemanAlreadyHasRing::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_MegaStoneShop, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n"
    )
    if old_gent in script:
        script = script.replace(old_gent, new_gent, 1)
    elif "LilycoveCity_DepartmentStore_4F_EventScript_GentlemanAlreadyHasRing::" not in script:
        raise RuntimeError("Could not patch Mega Ring gift NPC")

    if "LilycoveCity_DepartmentStore_4F_Text_GiveMegaRing:" not in script:
        script += (
            "\nLilycoveCity_DepartmentStore_4F_Text_GiveMegaRing:\n"
            "\t.string \"You've come at the right time!\\p\"\n"
            "\t.string \"This MEGA RING lets a Trainer draw out\\n\"\n"
            "\t.string \"a Pokemon's hidden Mega power.\\p\"\n"
            "\t.string \"Take it. The clerk here stocks the\\n\"\n"
            "\t.string \"MEGA STONES you'll need.$\"\n\n"
            "LilycoveCity_DepartmentStore_4F_Text_MegaStoneShop:\n"
            "\t.string \"The right-hand clerk stocks MEGA STONES.\\p\"\n"
            "\t.string \"Have the matching Pokemon hold its stone,\\n\"\n"
            "\t.string \"then use your MEGA RING in battle.$\"\n"
        )
    return script


def main():
    items_text = ITEMS.read_text()
    stones = discover_mega_stones(items_text)
    if not stones:
        raise RuntimeError("No Mega Stones discovered in item data")

    ITEMS.write_text(price_mega_stones(items_text, stones))
    LILYCOVE.write_text(patch_lilycove(LILYCOVE.read_text(), stones))
    print(f"Made {len(stones)} Mega Stones purchasable in Lilycove for {STONE_PRICE} each and added a free Mega Ring NPC gift.")


if __name__ == "__main__":
    main()
