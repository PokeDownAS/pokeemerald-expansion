#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ITEM_CFG = ROOT / "include/config/item.h"
SUMMARY_CFG = ROOT / "include/config/summary_screen.h"
ITEMS = ROOT / "src/data/items.h"
LILYCOVE = ROOT / "data/maps/LilycoveCity_DepartmentStore_4F/scripts.inc"


def set_define(text: str, name: str, value: str) -> str:
    pat = re.compile(rf"^(#define\s+{re.escape(name)}\s+).*$", re.M)
    text, count = pat.subn(rf"\g<1>{value}", text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not set {name}")
    return text


def set_item_price(text: str, item: str, price: int) -> str:
    # Handle both simple prices and generation-conditional item blocks by replacing
    # the first concrete .price assignment in the item's block.
    block_pat = re.compile(rf"(\[{re.escape(item)}\]\s*=\s*\{{)(.*?)(\n\s*\}},)", re.S)
    m = block_pat.search(text)
    if not m:
        raise RuntimeError(f"Could not find item block for {item}")
    body = m.group(2)
    body2, count = re.subn(r"(\.price\s*=\s*)(?:\([^\n]+\)|\d+)(\s*,)", rf"\g<1>{price}\2", body, count=1)
    if count != 1:
        # Conditional blocks often use several #if price assignments. Normalize all
        # concrete assignments in the block to the QoL price.
        body2, count = re.subn(r"(\.price\s*=\s*)\d+(\s*,)", rf"\g<1>{price}\2", body)
    if count < 1:
        raise RuntimeError(f"Could not set price for {item}")
    return text[:m.start()] + m.group(1) + body2 + m.group(3) + text[m.end():]


def patch_configs():
    item = ITEM_CFG.read_text()
    item = set_define(item, "I_REUSABLE_TMS", "TRUE       // Emerald Deluxe: reusable TMs")
    ITEM_CFG.write_text(item)

    summary = SUMMARY_CFG.read_text()
    for name, value in [
        ("P_SUMMARY_SCREEN_IV_EV_INFO", "TRUE   // Emerald Deluxe: show IV/EV pages"),
        ("P_SUMMARY_SCREEN_IV_EV_VALUES", "TRUE  // Emerald Deluxe: show exact IV values"),
        ("P_ENABLE_MOVE_RELEARNERS", "TRUE   // Emerald Deluxe: free summary-screen relearning"),
        ("P_SORT_MOVES", "TRUE   // Emerald Deluxe: easier move browsing"),
        ("P_PRE_EVO_MOVES", "TRUE   // Emerald Deluxe: include pre-evolution moves"),
    ]:
        summary = set_define(summary, name, value)
    SUMMARY_CFG.write_text(summary)


def patch_prices():
    text = ITEMS.read_text()
    prices = {
        "ITEM_ABILITY_CAPSULE": 5000,
        "ITEM_ABILITY_PATCH": 12000,
        "ITEM_BOTTLE_CAP": 5000,
        "ITEM_GOLD_BOTTLE_CAP": 20000,
        "ITEM_HP_UP": 2000,
        "ITEM_PROTEIN": 2000,
        "ITEM_IRON": 2000,
        "ITEM_CALCIUM": 2000,
        "ITEM_ZINC": 2000,
        "ITEM_CARBOS": 2000,
    }
    mints = [
        "ITEM_LONELY_MINT", "ITEM_ADAMANT_MINT", "ITEM_NAUGHTY_MINT", "ITEM_BRAVE_MINT",
        "ITEM_BOLD_MINT", "ITEM_IMPISH_MINT", "ITEM_LAX_MINT", "ITEM_RELAXED_MINT",
        "ITEM_MODEST_MINT", "ITEM_MILD_MINT", "ITEM_RASH_MINT", "ITEM_QUIET_MINT",
        "ITEM_CALM_MINT", "ITEM_GENTLE_MINT", "ITEM_CAREFUL_MINT", "ITEM_SASSY_MINT",
        "ITEM_TIMID_MINT", "ITEM_HASTY_MINT", "ITEM_JOLLY_MINT", "ITEM_NAIVE_MINT",
        "ITEM_SERIOUS_MINT",
    ]
    for mint in mints:
        prices[mint] = 3000
    for item, price in prices.items():
        text = set_item_price(text, item, price)
    ITEMS.write_text(text)
    return mints


def patch_lilycove(mints):
    script = LILYCOVE.read_text()
    old = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Woman::\n"
        "\tmsgbox LilycoveCity_DepartmentStore_4F_Text_FiftyDifferentTMs, MSGBOX_NPC\n"
        "\tend\n"
    )
    new = (
        "LilycoveCity_DepartmentStore_4F_EventScript_Woman::\n"
        "\tlock\n"
        "\tfaceplayer\n"
        "\tmessage gText_HowMayIServeYou\n"
        "\twaitmessage\n"
        "\tpokemart LilycoveCity_DepartmentStore_4F_Pokemart_QoL\n"
        "\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n"
        "\trelease\n"
        "\tend\n"
    )
    if old not in script:
        raise RuntimeError("Could not replace Lilycove QoL shop NPC")
    script = script.replace(old, new, 1)

    shop = [
        "ITEM_ABILITY_CAPSULE", "ITEM_ABILITY_PATCH",
        "ITEM_BOTTLE_CAP", "ITEM_GOLD_BOTTLE_CAP",
        "ITEM_HP_UP", "ITEM_PROTEIN", "ITEM_IRON", "ITEM_CALCIUM", "ITEM_ZINC", "ITEM_CARBOS",
        *mints,
    ]
    block = "\n\t.align 2\nLilycoveCity_DepartmentStore_4F_Pokemart_QoL:\n"
    block += "\n".join(f"\t.2byte {item}" for item in shop)
    block += "\n\tpokemartlistend\n"
    script += block
    LILYCOVE.write_text(script)
    return len(shop)


def main():
    patch_configs()
    mints = patch_prices()
    shop_count = patch_lilycove(mints)
    print(
        "QoL pass: reusable TMs; exact IV/EV summary pages; free sorted summary-screen move relearning "
        f"with pre-evolution moves; {shop_count} training items added to Lilycove with reduced prices."
    )


if __name__ == "__main__":
    main()
