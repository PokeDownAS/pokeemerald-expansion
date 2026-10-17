#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

EVOLUTION_STONES = [
    "ITEM_FIRE_STONE", "ITEM_WATER_STONE", "ITEM_THUNDER_STONE", "ITEM_LEAF_STONE",
    "ITEM_ICE_STONE", "ITEM_SUN_STONE", "ITEM_MOON_STONE", "ITEM_SHINY_STONE",
    "ITEM_DUSK_STONE", "ITEM_DAWN_STONE",
]

# One featured Mega Stone per regular Poké Mart, roughly ordered from modest to stronger choices.
MEGA_STONES = [
    "ITEM_BEEDRILLITE", "ITEM_PIDGEOTITE", "ITEM_MAWILITE", "ITEM_MANECTITE",
    "ITEM_ALTARIANITE", "ITEM_BANETTITE", "ITEM_ABSOLITE", "ITEM_AGGRONITE",
    "ITEM_GARDEVOIRITE", "ITEM_SCEPTILITE", "ITEM_BLAZIKENITE", "ITEM_SWAMPERTITE",
    "ITEM_GYARADOSITE", "ITEM_LUCARIONITE", "ITEM_GARCHOMPITE", "ITEM_METAGROSSITE",
]

ORDER = [
    "OldaleTown_Mart", "PetalburgCity_Mart", "RustboroCity_Mart", "SlateportCity_Mart",
    "MauvilleCity_Mart", "VerdanturfTown_Mart", "FallarborTown_Mart", "LavaridgeTown_Mart",
    "FortreeCity_Mart", "MossdeepCity_Mart", "SootopolisCity_Mart",
]


def add_to_lists(text: str, items):
    # Add before every pokemartlistend so basic/expanded inventories remain consistent.
    insert = "".join(f"\t.2byte {item}\n" for item in items)
    return re.sub(r"(?m)^\tpokemartlistend$", insert + "\tpokemartlistend", text)


def price_featured_megas():
    # Expansion defines Mega Stones with price 0 because they are normally gifts.
    # Give shop stones meaningful prices; stronger/later stones cost more.
    p = ROOT / "src/data/items.h"
    text = p.read_text()
    changed = 0
    for i, stone in enumerate(MEGA_STONES):
        price = min(30000, 12000 + 1500 * i)
        pat = re.compile(rf"(\[{re.escape(stone)}\]\s*=\s*\{{.*?\.price\s*=\s*)0(,)", re.S)
        text, n = pat.subn(rf"\g<1>{price}\2", text, count=1)
        changed += n
    p.write_text(text)
    print(f"Priced {changed} featured Mega Stones for Poké Mart sale")


def main():
    price_featured_megas()
    mart_files = {p.parent.name: p for p in ROOT.glob("data/maps/*_Mart/scripts.inc")}
    names = [n for n in ORDER if n in mart_files]
    names += sorted(n for n in mart_files if n not in names)

    changed = 0
    for i, name in enumerate(names):
        p = mart_files[name]
        text = p.read_text()
        mega = MEGA_STONES[min(i, len(MEGA_STONES) - 1)]
        if mega in text and all(stone in text for stone in EVOLUTION_STONES):
            continue
        new = add_to_lists(text, EVOLUTION_STONES + [mega])
        if new != text:
            p.write_text(new)
            changed += 1
            print(f"{name}: added evolution stones + {mega}")

    # Mega Ring becomes available after Norman / Balance Badge. Stones can be bought
    # earlier, but cannot be activated until this story milestone.
    gym = ROOT / "data/maps/PetalburgCity_Gym/scripts.inc"
    if gym.exists():
        text = gym.read_text()
        marker = "\tsetflag FLAG_BADGE05_GET\n"
        if "ITEM_MEGA_RING" not in text and marker in text:
            text = text.replace(marker, marker + "\tgiveitem ITEM_MEGA_RING\n", 1)
            gym.write_text(text)
            print("Mega Ring granted after Norman")

    print(f"Mega/evolution mart pass changed {changed} marts")


if __name__ == "__main__":
    main()
