#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"

# Ordinary trainer classes get a small identity pool. This pass runs after all
# story/boss scripts and deliberately skips those trainers.
CLASS_POOLS = [
    ("Hiker", [
        ("SPECIES_ROGGENROLA", ["MOVE_ROCK_TOMB", "MOVE_HEADBUTT", "MOVE_MUD_SLAP", "MOVE_SAND_ATTACK"]),
        ("SPECIES_DRILBUR", ["MOVE_BULLDOZE", "MOVE_METAL_CLAW", "MOVE_ROCK_TOMB", "MOVE_RAPID_SPIN"]),
        ("SPECIES_NOSEPASS", ["MOVE_ROCK_TOMB", "MOVE_THUNDER_WAVE", "MOVE_BLOCK", "MOVE_BULLDOZE"]),
    ]),
    ("Bird Keeper", [
        ("SPECIES_STARAVIA", ["MOVE_AERIAL_ACE", "MOVE_QUICK_ATTACK", "MOVE_FACADE", "MOVE_DOUBLE_TEAM"]),
        ("SPECIES_FLETCHINDER", ["MOVE_AERIAL_ACE", "MOVE_FLAME_CHARGE", "MOVE_QUICK_ATTACK", "MOVE_ROOST"]),
        ("SPECIES_CORVISQUIRE", ["MOVE_AERIAL_ACE", "MOVE_HONE_CLAWS", "MOVE_TAUNT", "MOVE_FURY_ATTACK"]),
    ]),
    ("Bug", [
        ("SPECIES_JOLTIK", ["MOVE_STRUGGLE_BUG", "MOVE_ELECTROWEB", "MOVE_THUNDER_WAVE", "MOVE_SUCKER_PUNCH"]),
        ("SPECIES_DEWPIDER", ["MOVE_BUBBLE_BEAM", "MOVE_BUG_BITE", "MOVE_BITE", "MOVE_AQUA_RING"]),
        ("SPECIES_VENIPEDE", ["MOVE_BUG_BITE", "MOVE_POISON_TAIL", "MOVE_ROLLOUT", "MOVE_PROTECT"]),
    ]),
    ("Fisherman", [
        ("SPECIES_CORPHISH", ["MOVE_BUBBLE_BEAM", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_LEER"]),
        ("SPECIES_BASCULIN", ["MOVE_AQUA_JET", "MOVE_BITE", "MOVE_HEADBUTT", "MOVE_SCARY_FACE"]),
        ("SPECIES_CLAUNCHER", ["MOVE_WATER_PULSE", "MOVE_AQUA_JET", "MOVE_SMACK_DOWN", "MOVE_SWORDS_DANCE"]),
    ]),
    ("Swimmer", [
        ("SPECIES_WINGULL", ["MOVE_WATER_PULSE", "MOVE_WING_ATTACK", "MOVE_QUICK_ATTACK", "MOVE_SUPERSONIC"]),
        ("SPECIES_FRILLISH", ["MOVE_WATER_PULSE", "MOVE_HEX", "MOVE_WILL_O_WISP", "MOVE_RECOVER"]),
        ("SPECIES_MARILL", ["MOVE_AQUA_TAIL", "MOVE_PLAY_ROUGH", "MOVE_ROLLOUT", "MOVE_AQUA_RING"]),
    ]),
    ("Black Belt", [
        ("SPECIES_MIENFOO", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_ROCK_TOMB", "MOVE_U_TURN"]),
        ("SPECIES_MACHOKE", ["MOVE_REVENGE", "MOVE_ROCK_TOMB", "MOVE_KNOCK_OFF", "MOVE_BULK_UP"]),
        ("SPECIES_HAWLUCHA", ["MOVE_BRICK_BREAK", "MOVE_AERIAL_ACE", "MOVE_ROCK_TOMB", "MOVE_ENCORE"]),
    ]),
    ("Battle Girl", [
        ("SPECIES_MIENFOO", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_ROCK_TOMB", "MOVE_U_TURN"]),
        ("SPECIES_MEDITITE", ["MOVE_FORCE_PALM", "MOVE_CONFUSION", "MOVE_FAKE_OUT", "MOVE_DETECT"]),
        ("SPECIES_HAWLUCHA", ["MOVE_BRICK_BREAK", "MOVE_AERIAL_ACE", "MOVE_ROCK_TOMB", "MOVE_ENCORE"]),
    ]),
    ("Psychic", [
        ("SPECIES_ESPURR", ["MOVE_PSYBEAM", "MOVE_FAKE_OUT", "MOVE_LIGHT_SCREEN", "MOVE_CHARM"]),
        ("SPECIES_GOTHITA", ["MOVE_PSYBEAM", "MOVE_FAKE_TEARS", "MOVE_CHARM", "MOVE_ROCK_TOMB"]),
        ("SPECIES_SIGILYPH", ["MOVE_PSYCHIC", "MOVE_AIR_SLASH", "MOVE_LIGHT_SCREEN", "MOVE_REFLECT"]),
    ]),
    ("Hex Maniac", [
        ("SPECIES_SHUPPET", ["MOVE_SHADOW_SNEAK", "MOVE_KNOCK_OFF", "MOVE_WILL_O_WISP", "MOVE_NIGHT_SHADE"]),
        ("SPECIES_MISDREAVUS", ["MOVE_HEX", "MOVE_PSYBEAM", "MOVE_CONFUSE_RAY", "MOVE_THUNDER_WAVE"]),
        ("SPECIES_LAMPENT", ["MOVE_HEX", "MOVE_FLAME_BURST", "MOVE_WILL_O_WISP", "MOVE_CONFUSE_RAY"]),
    ]),
    ("Aroma Lady", [
        ("SPECIES_ROSELIA", ["MOVE_GIGA_DRAIN", "MOVE_SLUDGE", "MOVE_STUN_SPORE", "MOVE_LEECH_SEED"]),
        ("SPECIES_PETILIL", ["MOVE_MEGA_DRAIN", "MOVE_SLEEP_POWDER", "MOVE_GROWTH", "MOVE_SYNTHESIS"]),
        ("SPECIES_FLOETTE", ["MOVE_MAGICAL_LEAF", "MOVE_FAIRY_WIND", "MOVE_WISH", "MOVE_GRASSY_TERRAIN"]),
    ]),
    ("Ninja Boy", [
        ("SPECIES_SKORUPI", ["MOVE_POISON_FANG", "MOVE_BUG_BITE", "MOVE_BITE", "MOVE_ACUPRESSURE"]),
        ("SPECIES_CROAGUNK", ["MOVE_REVENGE", "MOVE_POISON_JAB", "MOVE_SUCKER_PUNCH", "MOVE_TAUNT"]),
        ("SPECIES_SALANDIT", ["MOVE_FLAME_BURST", "MOVE_VENOSHOCK", "MOVE_FAKE_OUT", "MOVE_TORMENT"]),
    ]),
]

SKIP_LABEL_WORDS = (
    "ROXANNE", "BRAWLY", "WATTSON", "FLANNERY", "NORMAN", "WINONA", "TATE_AND_LIZA",
    "JUAN", "SIDNEY", "PHOEBE", "GLACIA", "DRAKE", "WALLACE", "STEVEN", "WALLY",
    "MAY_", "BRENDAN_", "ARCHIE", "MAXIE", "SHELLY", "MATT", "TABITHA", "COURTNEY",
    "GRUNT", "AQUA", "MAGMA",
)


def split_block(block):
    m = re.match(r"(=== (TRAINER_[A-Z0-9_]+) ===\n)(.*)", block, re.S)
    if not m or "\n\n" not in m.group(3):
        return None
    header, label, rest = m.groups()
    meta, party = rest.split("\n\n", 1)
    return header, label, meta, party


def get_class(meta):
    m = re.search(r"^Class:\s*(.+)$", meta, re.M)
    return m.group(1).strip() if m else ""


def max_level(party):
    vals = [int(x) for x in re.findall(r"^Level:\s*(\d+)$", party, re.M)]
    return max(vals) if vals else 5


def chunks(party):
    return [c.strip() for c in party.strip().split("\n\n") if c.strip()]


def species_key(chunk):
    first = chunk.splitlines()[0].split(" @ ")[0]
    m = re.search(r"SPECIES_([A-Z0-9_]+)", first)
    if m:
        return m.group(1)
    return re.sub(r"[^A-Z0-9]", "_", first.strip().upper())


def themed_pool(trainer_class):
    for needle, pool in CLASS_POOLS:
        if needle.lower() in trainer_class.lower():
            return pool
    return None


def make_mon(species, level, moves, item):
    return "\n".join([
        f"{species} @ {item}",
        f"Level: {level}",
        "IVs: 12 HP / 12 Atk / 12 Def / 12 SpA / 12 SpD / 12 Spe",
        *[f"- {move}" for move in moves],
    ])


def strengthen_ai(meta, level):
    if level < 28:
        return meta
    wanted = "AI: Check Bad Move / Try To Faint" if level < 40 else "AI: Check Bad Move / Try To Faint / Check Viability"
    if re.search(r"^AI:", meta, re.M):
        return re.sub(r"^AI:.*$", wanted, meta, flags=re.M)
    return meta.rstrip() + "\n" + wanted


def polish(block):
    parsed = split_block(block)
    if not parsed:
        return block, (0, 0, 0)
    header, label, meta, party = parsed
    if any(word in label for word in SKIP_LABEL_WORDS):
        return block, (0, 0, 0)
    trainer_class = get_class(meta)
    pool = themed_pool(trainer_class)
    level = max_level(party)
    mons = chunks(party)
    if not mons:
        return block, (0, 0, 0)

    changed = False
    deduped = 0
    seen = set()
    for i, mon in enumerate(mons):
        key = species_key(mon)
        if key not in seen:
            seen.add(key)
            continue
        if not pool:
            continue
        start = int(hashlib.sha256(f"{label}:{i}".encode()).hexdigest()[:8], 16) % len(pool)
        replacement = None
        for off in range(len(pool)):
            species, moves = pool[(start + off) % len(pool)]
            if species.replace("SPECIES_", "") not in seen:
                replacement = (species, moves)
                break
        if replacement:
            item = "ITEM_ORAN_BERRY" if level < 22 else "ITEM_SITRUS_BERRY" if level < 38 else "ITEM_EXPERT_BELT"
            mons[i] = make_mon(replacement[0], level, replacement[1], item)
            seen.add(replacement[0].replace("SPECIES_", ""))
            changed = True
            deduped += 1

    # Give themed ordinary trainers a second distinct Pokemon if they are still
    # a one-mon filler battle, without bloating route teams beyond four.
    expanded = 0
    if pool and len(mons) == 1 and level >= 12:
        start = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16) % len(pool)
        for off in range(len(pool)):
            species, moves = pool[(start + off) % len(pool)]
            if species.replace("SPECIES_", "") not in seen:
                item = "ITEM_ORAN_BERRY" if level < 22 else "ITEM_SITRUS_BERRY" if level < 38 else "ITEM_EXPERT_BELT"
                mons.append(make_mon(species, max(5, level - 1), moves, item))
                changed = True
                expanded = 1
                break

    meta2 = strengthen_ai(meta, level)
    ai_changed = int(meta2 != meta)
    changed = changed or bool(ai_changed)
    if not changed:
        return block, (0, 0, 0)
    return header + meta2.rstrip() + "\n\n" + "\n\n".join(mons) + "\n\n", (deduped, expanded, ai_changed)


def main():
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    totals = [0, 0, 0]
    touched = 0
    for part in parts:
        new, stats = polish(part)
        out.append(new)
        if new != part:
            touched += 1
        totals = [a + b for a, b in zip(totals, stats)]
    TRAINERS.write_text("".join(out))
    print(f"Route trainer polish: touched {touched} ordinary trainers; replaced {totals[0]} duplicate Pokemon, expanded {totals[1]} one-Pokemon filler teams, upgraded AI on {totals[2]} later trainers.")


if __name__ == "__main__":
    main()
