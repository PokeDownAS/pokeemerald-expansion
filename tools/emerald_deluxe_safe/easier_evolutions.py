#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "src/data/pokemon/species_info"


def lower_level(match):
    level = int(match.group(1))
    original = level
    if level >= 50:
        level = max(42, level - 8)
    elif level >= 40:
        level -= 4
    elif level >= 31:
        level -= 2
    return f"EVO_LEVEL, {level}" if level != original else match.group(0)


def main():
    changed_files = 0
    trade_changes = 0
    level_changes = 0

    for path in SPECIES_DIR.glob("gen_*_families.h"):
        text = path.read_text()
        before = text

        # Pure trade evolutions become level 36 so every player can obtain them solo.
        text, n_trade = re.subn(
            r"EVOLUTION\(\{EVO_TRADE,\s*[^,{}]+,\s*(SPECIES_[A-Z0-9_]+)(?:,\s*[^{}]*)?\}\)",
            lambda m: f"EVOLUTION({{EVO_LEVEL, 36, {m.group(1)}}})",
            text,
        )
        trade_changes += n_trade

        # Reduce only later level evolutions. Early/midgame evolution pacing is preserved.
        def repl(match):
            nonlocal level_changes
            old = int(match.group(1))
            result = lower_level(match)
            if result != match.group(0):
                level_changes += 1
            return result

        text = re.sub(r"EVO_LEVEL,\s*(\d+)", repl, text)

        if text != before:
            path.write_text(text)
            changed_files += 1

    print(f"Easier evolutions applied to {changed_files} files: {trade_changes} trade evolutions made solo-friendly; {level_changes} high-level requirements lowered.")


if __name__ == "__main__":
    main()
