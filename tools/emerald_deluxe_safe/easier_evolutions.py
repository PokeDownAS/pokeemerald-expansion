#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "src/data/pokemon/species_info"

# Reasonable default levels for evolution stages. Existing level evolutions are
# retained but late requirements are lowered. Every special method becomes level-up.
DEFAULT_SPECIAL_LEVEL = 30


def adjusted_existing_level(level):
    if level >= 50:
        return max(42, level - 8)
    if level >= 40:
        return level - 4
    if level >= 31:
        return level - 2
    return level


def split_evolution_args(body):
    # Evolution entries in species data are simple comma-separated macro args.
    # Preserve the final SPECIES_* target and discard special method parameters.
    target = re.search(r"(SPECIES_[A-Z0-9_]+)\s*$", body.strip())
    if not target:
        return None
    return target.group(1)


def convert_block(match):
    content = match.group(1)
    entries = re.findall(r"\{([^{}]+)\}", content)
    if not entries:
        return match.group(0)

    converted = []
    branch_count = len(entries)
    for i, entry in enumerate(entries):
        target = split_evolution_args(entry)
        if not target:
            converted.append("{" + entry + "}")
            continue

        level_match = re.match(r"\s*EVO_LEVEL\s*,\s*(\d+)\s*,", entry)
        if level_match:
            level = adjusted_existing_level(int(level_match.group(1)))
        else:
            # Single special evolutions land around the late-20s/early-30s.
            # Branches are staggered so every entry remains representable using
            # level-up only; players can cancel an earlier branch to reach a later one.
            if branch_count == 1:
                level = DEFAULT_SPECIAL_LEVEL
            else:
                level = 20 + i * 5
        converted.append(f"{{EVO_LEVEL, {level}, {target}}}")

    return "EVOLUTION(" + ", ".join(converted) + ")"


def main():
    changed_files = 0
    total_entries = 0
    special_entries = 0

    for path in SPECIES_DIR.glob("gen_*_families.h"):
        text = path.read_text()
        before = text

        # Count before conversion for reporting.
        for evo in re.finditer(r"EVOLUTION\((.*?)\)", text, re.S):
            entries = re.findall(r"\{([^{}]+)\}", evo.group(1))
            total_entries += len(entries)
            special_entries += sum(1 for e in entries if not re.match(r"\s*EVO_LEVEL\s*,", e))

        text = re.sub(r"EVOLUTION\((.*?)\)", convert_block, text, flags=re.S)

        if text != before:
            path.write_text(text)
            changed_files += 1

    print(
        f"Universal level evolutions applied across {changed_files} files: "
        f"{total_entries} evolution entries processed; {special_entries} special-method entries converted to level-up."
    )


if __name__ == "__main__":
    main()
