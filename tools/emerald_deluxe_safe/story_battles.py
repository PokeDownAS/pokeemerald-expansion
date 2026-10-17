#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"

AQUA_POOL = [
    ("SPECIES_CARVANHA", ["MOVE_BITE", "MOVE_AQUA_JET", "MOVE_ICE_FANG", "MOVE_SCARY_FACE"]),
    ("SPECIES_CORPHISH", ["MOVE_BUBBLE_BEAM", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_LEER"]),
    ("SPECIES_SKRELP", ["MOVE_WATER_PULSE", "MOVE_SLUDGE", "MOVE_SMOKESCREEN", "MOVE_ACID"]),
    ("SPECIES_CROAGUNK", ["MOVE_REVENGE", "MOVE_POISON_JAB", "MOVE_SUCKER_PUNCH", "MOVE_TAUNT"]),
    ("SPECIES_BASCULIN", ["MOVE_AQUA_JET", "MOVE_BITE", "MOVE_HEADBUTT", "MOVE_SCARY_FACE"]),
]
MAGMA_POOL = [
    ("SPECIES_NUMEL", ["MOVE_FLAME_BURST", "MOVE_BULLDOZE", "MOVE_ROCK_TOMB", "MOVE_AMNESIA"]),
    ("SPECIES_HOUNDOUR", ["MOVE_FIRE_FANG", "MOVE_BITE", "MOVE_ROAR", "MOVE_SMOG"]),
    ("SPECIES_SALANDIT", ["MOVE_FLAME_BURST", "MOVE_VENOSHOCK", "MOVE_FAKE_OUT", "MOVE_TORMENT"]),
    ("SPECIES_ROLYCOLY", ["MOVE_ROCK_TOMB", "MOVE_SMACK_DOWN", "MOVE_RAPID_SPIN", "MOVE_SMOKESCREEN"]),
    ("SPECIES_SANDILE", ["MOVE_BITE", "MOVE_BULLDOZE", "MOVE_SAND_ATTACK", "MOVE_TORMENT"]),
]

SIGNATURES = {
    "MAY": [
        (18, "SPECIES_BUDEW", ["MOVE_MEGA_DRAIN", "MOVE_STUN_SPORE", "MOVE_GROWTH", "MOVE_EXTRASENSORY"]),
        (34, "SPECIES_ROSELIA", ["MOVE_GIGA_DRAIN", "MOVE_SLUDGE_BOMB", "MOVE_STUN_SPORE", "MOVE_LEECH_SEED"]),
        (101, "SPECIES_ROSERADE", ["MOVE_ENERGY_BALL", "MOVE_SLUDGE_BOMB", "MOVE_SHADOW_BALL", "MOVE_TOXIC_SPIKES"]),
    ],
    "BRENDAN": [
        (18, "SPECIES_SHINX", ["MOVE_SPARK", "MOVE_BITE", "MOVE_QUICK_ATTACK", "MOVE_LEER"]),
        (34, "SPECIES_LUXIO", ["MOVE_SPARK", "MOVE_BITE", "MOVE_THUNDER_WAVE", "MOVE_FACADE"]),
        (101, "SPECIES_LUXRAY", ["MOVE_WILD_CHARGE", "MOVE_CRUNCH", "MOVE_ICE_FANG", "MOVE_THUNDER_WAVE"]),
    ],
    "WALLY": [
        (24, "SPECIES_RIOLU", ["MOVE_FORCE_PALM", "MOVE_METAL_CLAW", "MOVE_QUICK_ATTACK", "MOVE_COUNTER"]),
        (101, "SPECIES_LUCARIO", ["MOVE_AURA_SPHERE", "MOVE_FLASH_CANNON", "MOVE_DARK_PULSE", "MOVE_EXTREME_SPEED"]),
    ],
}


def split_block(block):
    m = re.match(r"(=== (TRAINER_[A-Z0-9_]+) ===\n)(.*)", block, re.S)
    if not m:
        return None
    header, label, rest = m.groups()
    if "\n\n" not in rest:
        return None
    meta, party = rest.split("\n\n", 1)
    return header, label, meta, party


def max_level(party):
    vals = [int(x) for x in re.findall(r"^Level:\s*(\d+)$", party, re.M)]
    return max(vals) if vals else 5


def mon_chunks(party):
    return [c for c in party.strip().split("\n\n") if c.strip()]


def species_of(chunk):
    first = chunk.splitlines()[0]
    first = first.split(" @ ")[0]
    m = re.search(r"SPECIES_([A-Z0-9_]+)", first)
    if m:
        return m.group(1)
    return re.sub(r"[^A-Z0-9]", "_", first.strip().upper())


def make_mon(species, level, moves, item):
    lines = [
        f"{species} @ {item}",
        f"Level: {level}",
        "IVs: 18 HP / 18 Atk / 18 Def / 18 SpA / 18 SpD / 18 Spe",
    ] + [f"- {m}" for m in moves]
    return "\n".join(lines)


def smart_ai(meta):
    lines = meta.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("AI:"):
            lines[i] = "AI: Check Bad Move / Try To Faint / Check Viability"
            break
    else:
        lines.append("AI: Check Bad Move / Try To Faint / Check Viability")
    return "\n".join(lines)


def choose_signature(name, level):
    for cap, species, moves in SIGNATURES[name]:
        if level < cap:
            return species, moves
    return SIGNATURES[name][-1][1:]


def tune_rival(label, meta, party):
    name = None
    if label.startswith("TRAINER_MAY_"):
        name = "MAY"
    elif label.startswith("TRAINER_BRENDAN_"):
        name = "BRENDAN"
    elif label.startswith("TRAINER_WALLY_"):
        name = "WALLY"
    if not name:
        return meta, party, False

    level = max_level(party)
    species, moves = choose_signature(name, level)
    chunks = mon_chunks(party)
    sig_key = species.replace("SPECIES_", "")
    chunks = [c for c in chunks if species_of(c) not in {"BUDEW", "ROSELIA", "ROSERADE", "SHINX", "LUXIO", "LUXRAY", "RIOLU", "LUCARIO"}]
    item = "ITEM_ORAN_BERRY" if level < 20 else "ITEM_SITRUS_BERRY" if level < 35 else "ITEM_EXPERT_BELT"
    chunks.append(make_mon(species, max(5, level), moves, item))
    if len(chunks) > 6:
        chunks = chunks[:5] + [chunks[-1]]
    return smart_ai(meta), "\n\n".join(chunks), True


def tune_grunt(label, meta, party):
    is_aqua = "GRUNT" in label and ("AQUA" in label or "Class: Team Aqua" in meta)
    is_magma = "GRUNT" in label and ("MAGMA" in label or "Class: Team Magma" in meta)
    if not (is_aqua or is_magma):
        return meta, party, False

    pool = AQUA_POOL if is_aqua else MAGMA_POOL
    level = max_level(party)
    idx = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16) % len(pool)
    species, moves = pool[idx]
    chunks = mon_chunks(party)
    new_key = species.replace("SPECIES_", "")
    if all(species_of(c) != new_key for c in chunks):
        item = "ITEM_ORAN_BERRY" if level < 18 else "ITEM_SITRUS_BERRY" if level < 32 else "ITEM_BLACK_GLASSES" if is_aqua else "ITEM_CHARCOAL"
        chunks.append(make_mon(species, max(5, level - 1), moves, item))
    if len(chunks) > 4:
        chunks = chunks[-4:]
    return meta, "\n\n".join(chunks), True


def tune_archie_maxie(label, meta, party):
    level = max_level(party)
    if label == "TRAINER_ARCHIE":
        team = [
            ("SPECIES_MIGHTYENA", "ITEM_BLACK_GLASSES", ["MOVE_CRUNCH", "MOVE_PLAY_ROUGH", "MOVE_FIRE_FANG", "MOVE_SUCKER_PUNCH"]),
            ("SPECIES_CROBAT", "ITEM_SHARP_BEAK", ["MOVE_CROSS_POISON", "MOVE_AERIAL_ACE", "MOVE_BITE", "MOVE_U_TURN"]),
            ("SPECIES_CRAWDAUNT", "ITEM_EXPERT_BELT", ["MOVE_CRABHAMMER", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_BRICK_BREAK"]),
            ("SPECIES_SHARPEDO", "ITEM_LUM_BERRY", ["MOVE_WATERFALL", "MOVE_CRUNCH", "MOVE_ICE_FANG", "MOVE_POISON_JAB"]),
        ]
    elif label.startswith("TRAINER_MAXIE_"):
        team = [
            ("SPECIES_MIGHTYENA", "ITEM_BLACK_GLASSES", ["MOVE_CRUNCH", "MOVE_PLAY_ROUGH", "MOVE_FIRE_FANG", "MOVE_SUCKER_PUNCH"]),
            ("SPECIES_CROBAT", "ITEM_SHARP_BEAK", ["MOVE_CROSS_POISON", "MOVE_AERIAL_ACE", "MOVE_BITE", "MOVE_U_TURN"]),
            ("SPECIES_CAMERUPT", "ITEM_SOFT_SAND", ["MOVE_LAVA_PLUME", "MOVE_EARTH_POWER", "MOVE_ROCK_SLIDE", "MOVE_YAWN"]),
            ("SPECIES_HOUNDOOM", "ITEM_LUM_BERRY", ["MOVE_FLAMETHROWER", "MOVE_DARK_PULSE", "MOVE_SLUDGE_BOMB", "MOVE_WILL_O_WISP"]),
        ]
    else:
        return meta, party, False

    count = 3 if level < 36 else 4
    built = []
    for species, item, moves in team[:count]:
        built.append(make_mon(species, level, moves, item))
    return smart_ai(meta), "\n\n".join(built), True


def tune_steven(label, meta, party):
    if label != "TRAINER_STEVEN":
        return meta, party, False
    level = max(77, max_level(party))
    team = [
        ("SPECIES_SKARMORY", "ITEM_LEFTOVERS", ["MOVE_STEEL_WING", "MOVE_AERIAL_ACE", "MOVE_SPIKES", "MOVE_ROOST"]),
        ("SPECIES_CLAYDOL", "ITEM_LIGHT_CLAY", ["MOVE_PSYCHIC", "MOVE_EARTH_POWER", "MOVE_REFLECT", "MOVE_LIGHT_SCREEN"]),
        ("SPECIES_AGGRON", "ITEM_EXPERT_BELT", ["MOVE_IRON_HEAD", "MOVE_ROCK_SLIDE", "MOVE_EARTHQUAKE", "MOVE_THUNDER_PUNCH"]),
        ("SPECIES_CRADILY", "ITEM_LEFTOVERS", ["MOVE_GIGA_DRAIN", "MOVE_POWER_GEM", "MOVE_EARTH_POWER", "MOVE_RECOVER"]),
        ("SPECIES_ARMALDO", "ITEM_LUM_BERRY", ["MOVE_X_SCISSOR", "MOVE_ROCK_SLIDE", "MOVE_EARTHQUAKE", "MOVE_AQUA_JET"]),
        ("SPECIES_METAGROSS", "ITEM_LIFE_ORB", ["MOVE_METEOR_MASH", "MOVE_ZEN_HEADBUTT", "MOVE_EARTHQUAKE", "MOVE_BULLET_PUNCH"]),
    ]
    return smart_ai(meta), "\n\n".join(make_mon(s, level + i // 2, m, it) for i, (s, it, m) in enumerate(team)), True


def process(block):
    sp = split_block(block)
    if not sp:
        return block, (0, 0, 0, 0)
    header, label, meta, party = sp
    counts = [0, 0, 0, 0]

    meta2, party2, changed = tune_archie_maxie(label, meta, party)
    if changed:
        counts[2] += 1
    else:
        meta2, party2, changed = tune_steven(label, meta, party)
        if changed:
            counts[3] += 1
        else:
            meta2, party2, changed = tune_rival(label, meta, party)
            if changed:
                counts[0] += 1
            else:
                meta2, party2, changed = tune_grunt(label, meta, party)
                if changed:
                    counts[1] += 1

    if not changed:
        return block, tuple(counts)
    return header + meta2.rstrip() + "\n\n" + party2.rstrip() + "\n\n", tuple(counts)


def main():
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    totals = [0, 0, 0, 0]
    for part in parts:
        new, counts = process(part)
        out.append(new)
        totals = [a + b for a, b in zip(totals, counts)]
    TRAINERS.write_text("".join(out))
    print(f"Story pass: tuned {totals[0]} rival/Wally fights, diversified {totals[1]} Aqua/Magma grunts, tuned {totals[2]} Archie/Maxie fights, and {totals[3]} Steven fight.")


if __name__ == "__main__":
    main()
