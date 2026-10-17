#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "src/data/trainers.party"

# The goal is variety and readable counterplay, not competitive-perfect or omniscient AI.
# Each major boss' added Emerald Deluxe Pokemon receives a small tactical identity.
BOSS_SETS = {
    "TRAINER_ROXANNE_1": ("SPECIES_ROCKRUFF", "ITEM_ORAN_BERRY", ["MOVE_STEALTH_ROCK", "MOVE_ROCK_TOMB", "MOVE_BITE", "MOVE_HOWL"]),
    "TRAINER_BRAWLY_1": ("SPECIES_CROAGUNK", "ITEM_ORAN_BERRY", ["MOVE_FAKE_OUT", "MOVE_LOW_SWEEP", "MOVE_POISON_JAB", "MOVE_TAUNT"]),
    "TRAINER_WATTSON_1": ("SPECIES_BELLIBOLT", "ITEM_SITRUS_BERRY", ["MOVE_DISCHARGE", "MOVE_MUD_SHOT", "MOVE_THUNDER_WAVE", "MOVE_CHARGE"]),
    "TRAINER_FLANNERY_1": ("SPECIES_HOUNDOOM", "ITEM_SITRUS_BERRY", ["MOVE_SUNNY_DAY", "MOVE_FLAMETHROWER", "MOVE_SNARL", "MOVE_WILL_O_WISP"]),
    "TRAINER_NORMAN_1": ("SPECIES_BEWEAR", "ITEM_SITRUS_BERRY", ["MOVE_BULK_UP", "MOVE_FACADE", "MOVE_PAYBACK", "MOVE_PROTECT"]),
    "TRAINER_WINONA_1": ("SPECIES_GLISCOR", "ITEM_SITRUS_BERRY", ["MOVE_ACROBATICS", "MOVE_BULLDOZE", "MOVE_U_TURN", "MOVE_ROOST"]),
    "TRAINER_TATE_AND_LIZA_1": ("SPECIES_METAGROSS", "ITEM_SITRUS_BERRY", ["MOVE_ZEN_HEADBUTT", "MOVE_METEOR_MASH", "MOVE_ROCK_SLIDE", "MOVE_PROTECT"]),
    "TRAINER_JUAN_1": ("SPECIES_LAPRAS", "ITEM_LEFTOVERS", ["MOVE_RAIN_DANCE", "MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_SING"]),
    "TRAINER_SIDNEY": ("SPECIES_KINGAMBIT", "ITEM_BLACK_GLASSES", ["MOVE_KOWTOW_CLEAVE", "MOVE_IRON_HEAD", "MOVE_SUCKER_PUNCH", "MOVE_SWORDS_DANCE"]),
    "TRAINER_PHOEBE": ("SPECIES_ANNIHILAPE", "ITEM_SITRUS_BERRY", ["MOVE_RAGE_FIST", "MOVE_DRAIN_PUNCH", "MOVE_BULK_UP", "MOVE_TAUNT"]),
    "TRAINER_GLACIA": ("SPECIES_BAXCALIBUR", "ITEM_NEVER_MELT_ICE", ["MOVE_ICICLE_CRASH", "MOVE_DRAGON_CLAW", "MOVE_ICE_SHARD", "MOVE_SWORDS_DANCE"]),
    "TRAINER_DRAKE": ("SPECIES_DRAGAPULT", "ITEM_DRAGON_FANG", ["MOVE_DRAGON_DARTS", "MOVE_SHADOW_BALL", "MOVE_U_TURN", "MOVE_THUNDER_WAVE"]),
    "TRAINER_WALLACE": ("SPECIES_PALAFIN", "ITEM_MYSTIC_WATER", ["MOVE_FLIP_TURN", "MOVE_JET_PUNCH", "MOVE_ICE_PUNCH", "MOVE_BULK_UP"]),
}


def replace_ai(meta: str, flags: str) -> str:
    if re.search(r"(?m)^AI:.*$", meta):
        return re.sub(r"(?m)^AI:.*$", f"AI: {flags}", meta, count=1)
    return meta.rstrip() + f"\nAI: {flags}\n"


def avg_level(party: str) -> float:
    vals = [int(x) for x in re.findall(r"(?m)^Level:\s*(\d+)\s*$", party)]
    return sum(vals) / len(vals) if vals else 1


def style_boss(part: str, label: str) -> str:
    if label not in BOSS_SETS or "\n\n" not in part:
        return part
    meta, party = part.split("\n\n", 1)
    # Strong decision-making without hidden-information omniscience.
    meta = replace_ai(meta, "Basic Trainer / HP Aware / Smart Mon Choices / Prefer Status Moves")
    species, item, moves = BOSS_SETS[label]
    blocks = party.strip().split("\n\n")
    for i, block in enumerate(blocks):
        if re.match(rf"^{re.escape(species)}(?:\s|$)", block):
            lines = block.splitlines()
            lines[0] = f"{species} @ {item}"
            # Moves are always last in trainerproc syntax; replace any existing explicit set.
            lines = [ln for ln in lines if not ln.startswith("- ")]
            lines.extend(f"- {mv}" for mv in moves)
            blocks[i] = "\n".join(lines)
            break
    return meta + "\n\n" + "\n\n".join(blocks) + "\n\n"


def style_regular(part: str) -> str:
    if "\n\n" not in part:
        return part
    meta, party = part.split("\n\n", 1)
    if "Class:" not in meta:
        return part
    cm = re.search(r"(?m)^Class:\s*(.+)$", meta)
    cls = cm.group(1).strip() if cm else ""
    lvl = avg_level(party)

    # Later ordinary trainers should make sensible choices, but should not read the
    # player's full set or constantly switch like competitive AI.
    if lvl >= 28:
        flags = ["Basic Trainer", "HP Aware"]
        if any(k in cls for k in ("Cooltrainer", "Expert", "Team Aqua", "Team Magma")):
            flags.append("Smart Mon Choices")
        if any(k in cls for k in ("Psychic", "Hex", "Aroma", "Ninja")):
            flags.append("Prefer Status Moves")
        meta = replace_ai(meta, " / ".join(flags))
    elif lvl >= 18 and any(k in cls for k in ("Cooltrainer", "Expert", "Team Aqua", "Team Magma")):
        meta = replace_ai(meta, "Basic Trainer")
    return meta + "\n\n" + party


def main():
    text = PATH.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    bosses = 0
    upgraded = 0
    for part in parts:
        m = re.match(r"^=== (TRAINER_[A-Z0-9_]+) ===$", part, flags=re.M)
        if not m:
            out.append(part)
            continue
        label = m.group(1)
        if label in BOSS_SETS:
            new = style_boss(part, label)
            bosses += new != part
        else:
            new = style_regular(part)
            upgraded += new != part
        out.append(new)
    PATH.write_text("".join(out))
    print(f"Strategic trainer pass: {bosses} bosses themed, {upgraded} ordinary trainers upgraded")


if __name__ == "__main__":
    main()
