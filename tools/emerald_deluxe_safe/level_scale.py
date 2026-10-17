#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"

BOSS_LABELS = {
    "TRAINER_ROXANNE_1", "TRAINER_BRAWLY_1", "TRAINER_WATTSON_1",
    "TRAINER_FLANNERY_1", "TRAINER_NORMAN_1", "TRAINER_WINONA_1",
    "TRAINER_TATE_AND_LIZA_1", "TRAINER_JUAN_1", "TRAINER_SIDNEY",
    "TRAINER_PHOEBE", "TRAINER_GLACIA", "TRAINER_DRAKE", "TRAINER_WALLACE",
}

HEADER_RE = re.compile(r"^=== (TRAINER_[A-Z0-9_]+) ===$", re.M)
LEVEL_RE = re.compile(r"^Level:\s*(\d+)\s*$", re.M)


def scale_block(block: str) -> str:
    match = HEADER_RE.search(block)
    if not match or match.group(1) == "TRAINER_NONE":
        return block
    bump = 3 if match.group(1) in BOSS_LABELS else 2
    return LEVEL_RE.sub(lambda m: f"Level: {min(100, int(m.group(1)) + bump)}", block)


def main() -> None:
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    TRAINERS.write_text("".join(scale_block(part) for part in parts))
    print("Applied safe trainer level scaling: +2 normal trainers, +3 major bosses.")


if __name__ == "__main__":
    main()
