#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECIES_DIR = ROOT / "src/data/pokemon/species_info"

# Existing level evolutions keep their normal pacing (with the previous late-game
# reductions). Any other real evolution method becomes a normal level-up evolution.
DEFAULT_SPECIAL_LEVEL = 30


def adjusted_existing_level(level):
    if level >= 50:
        return max(42, level - 8)
    if level >= 40:
        return level - 4
    if level >= 31:
        return level - 2
    return level


def split_top_level_args(text):
    """Split a C initializer on commas without splitting nested macros/arrays."""
    args = []
    start = 0
    paren = bracket = brace = 0
    in_string = False
    escaped = False

    for i, ch in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
        elif ch == "," and paren == 0 and bracket == 0 and brace == 0:
            args.append(text[start:i].strip())
            start = i + 1

    args.append(text[start:].strip())
    return args


def convert_entry(entry_body, branch_index, branch_count):
    args = split_top_level_args(entry_body)
    if len(args) < 3:
        return None, False

    method = args[0].strip()
    target = args[2].strip()
    if not re.fullmatch(r"SPECIES_[A-Z0-9_]+", target):
        return None, False

    # EVO_NONE is a sentinel used for unavailable/alternate form paths rather than
    # a normal evolution. Turning it into EVO_LEVEL would create bogus evolutions.
    if method == "EVO_NONE":
        return None, False

    if method == "EVO_LEVEL" and re.fullmatch(r"\d+", args[1].strip()):
        level = adjusted_existing_level(int(args[1].strip()))
        changed_special = False
    else:
        # Branching evolutions get distinct levels so every branch remains reachable:
        # cancel the earlier evolution if you want a later branch.
        level = DEFAULT_SPECIAL_LEVEL if branch_count == 1 else 20 + branch_index * 5
        changed_special = method != "EVO_LEVEL"

    return f"{{EVO_LEVEL, {level}, {target}}}", changed_special


def convert_evolution_content(content):
    """Convert outer { ... } evolution entries while preserving all surrounding C text."""
    groups = []
    depth = 0
    start = None
    in_string = False
    escaped = False

    for i, ch in enumerate(content):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                groups.append((start, i + 1))
                start = None

    if not groups:
        return content, 0, 0

    out = []
    cursor = 0
    special_converted = 0
    processed = 0
    branch_count = len(groups)

    for branch_index, (start, end) in enumerate(groups):
        out.append(content[cursor:start])
        original = content[start:end]
        replacement, changed_special = convert_entry(
            original[1:-1], branch_index, branch_count
        )
        if replacement is None:
            out.append(original)
        else:
            out.append(replacement)
            processed += 1
            special_converted += int(changed_special)
        cursor = end

    out.append(content[cursor:])
    return "".join(out), processed, special_converted


def convert_all_evolution_calls(text):
    """Find EVOLUTION(...) calls using balanced parentheses, not a fragile regex."""
    marker = "EVOLUTION("
    out = []
    cursor = 0
    total_entries = 0
    special_entries = 0

    while True:
        start = text.find(marker, cursor)
        if start == -1:
            out.append(text[cursor:])
            break

        out.append(text[cursor:start])
        open_paren = start + len(marker) - 1
        depth = 0
        in_string = False
        escaped = False
        end = None

        for i in range(open_paren, len(text)):
            ch = text[i]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = i
                    break

        if end is None:
            # Never emit a partially rewritten C expression.
            out.append(text[start:])
            break

        content = text[open_paren + 1:end]
        converted, processed, specials = convert_evolution_content(content)
        total_entries += processed
        special_entries += specials
        out.append("EVOLUTION(" + converted + ")")
        cursor = end + 1

    return "".join(out), total_entries, special_entries


def main():
    changed_files = 0
    total_entries = 0
    special_entries = 0

    for path in SPECIES_DIR.glob("gen_*_families.h"):
        text = path.read_text()
        before = text
        text, processed, specials = convert_all_evolution_calls(text)
        total_entries += processed
        special_entries += specials

        if text != before:
            path.write_text(text)
            changed_files += 1

    print(
        f"Universal level evolutions applied across {changed_files} files: "
        f"{total_entries} evolution entries processed; "
        f"{special_entries} special-method entries converted to level-up."
    )


if __name__ == "__main__":
    main()
