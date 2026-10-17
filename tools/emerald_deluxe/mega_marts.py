#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

EVOLUTION_STONES = [
    "ITEM_FIRE_STONE", "ITEM_WATER_STONE", "ITEM_THUNDER_STONE", "ITEM_LEAF_STONE",
    "ITEM_ICE_STONE", "ITEM_SUN_STONE", "ITEM_MOON_STONE", "ITEM_SHINY_STONE",
    "ITEM_DUSK_STONE", "ITEM_DAWN_STONE",
]


def find_mega_stones(items_text: str):
    """Return every item whose item-data block identifies it as a Mega Stone."""
    stones = []
    block_re = re.compile(r"\[(ITEM_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n\s*\},", re.S)
    for m in block_re.finditer(items_text):
        if "HOLD_EFFECT_MEGA_STONE" in m.group(2):
            stones.append(m.group(1))
    return stones


def set_price(items_text: str, item: str, price: int = 1):
    pat = re.compile(rf"(\[{re.escape(item)}\]\s*=\s*\{{.*?\.price\s*=\s*)([^,\n]+)(,)", re.S)
    return pat.subn(rf"\g<1>{price}\3", items_text, count=1)


def normalize_mart(text: str, items):
    """Put each requested item exactly once in every inventory variant in this Mart."""
    item_set = set(items)
    lines = []
    for line in text.splitlines(True):
        m = re.match(r"\s*\.2byte\s+(ITEM_[A-Z0-9_]+)\s*$", line.rstrip("\n"))
        if m and m.group(1) in item_set:
            continue
        lines.append(line)
    text = "".join(lines)
    insert = "".join(f"\t.2byte {item}\n" for item in items)
    return re.sub(r"(?m)^\tpokemartlistend$", insert + "\tpokemartlistend", text)


def main():
    items_path = ROOT / "src/data/items.h"
    items_text = items_path.read_text()
    mega_stones = find_mega_stones(items_text)
    if not mega_stones:
        raise RuntimeError("No Mega Stones found in src/data/items.h")

    priced = 0
    for item in EVOLUTION_STONES + mega_stones:
        items_text, n = set_price(items_text, item, 1)
        priced += n
    items_path.write_text(items_text)

    # Keep the convenience rule simple: every normal Poké Mart sells every evolution
    # stone and every Mega Stone for ₽1. Mega Evolution itself remains story-gated.
    mart_files = sorted(ROOT.glob("data/maps/*_Mart/scripts.inc"))
    shop_items = EVOLUTION_STONES + mega_stones
    changed = 0
    for p in mart_files:
        text = p.read_text()
        new = normalize_mart(text, shop_items)
        if new != text:
            p.write_text(new)
            changed += 1
            print(f"{p.parent.name}: added all evolution stones + {len(mega_stones)} Mega Stones at ₽1")

    # Mega Ring becomes available after Norman / Balance Badge. This prevents ₽1 stones
    # from trivializing the early game while still letting the player plan a team freely.
    gym = ROOT / "data/maps/PetalburgCity_Gym/scripts.inc"
    if gym.exists():
        text = gym.read_text()
        marker = "\tsetflag FLAG_BADGE05_GET\n"
        if "ITEM_MEGA_RING" not in text and marker in text:
            text = text.replace(marker, marker + "\tgiveitem ITEM_MEGA_RING\n", 1)
            gym.write_text(text)
            print("Mega Ring granted after Norman")

    print(f"Priced {priced} evolution/Mega Stones at ₽1; updated {changed} Poké Marts")


if __name__ == "__main__":
    main()
