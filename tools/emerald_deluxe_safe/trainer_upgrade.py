#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"
HEADER_RE = re.compile(r"^=== (TRAINER_[A-Z0-9_]+) ===$")
LEVEL_RE = re.compile(r"^Level:\s*(\d+)\s*$", re.M)

BOSSES = {
    "TRAINER_ROXANNE_1", "TRAINER_BRAWLY_1", "TRAINER_WATTSON_1",
    "TRAINER_FLANNERY_1", "TRAINER_NORMAN_1", "TRAINER_WINONA_1",
    "TRAINER_TATE_AND_LIZA_1", "TRAINER_JUAN_1", "TRAINER_SIDNEY",
    "TRAINER_PHOEBE", "TRAINER_GLACIA", "TRAINER_DRAKE", "TRAINER_WALLACE",
}

# Three progression tiers per theme. Added Pokemon always receive four useful,
# level-appropriate moves: STAB, coverage, and a little utility rather than
# competitive-perfect optimization.
THEMES = {
    "rock": [
        ("SPECIES_ROGGENROLA", ["MOVE_ROCK_TOMB", "MOVE_HEADBUTT", "MOVE_MUD_SLAP", "MOVE_SAND_ATTACK"]),
        ("SPECIES_BOLDORE", ["MOVE_ROCK_SLIDE", "MOVE_BULLDOZE", "MOVE_HEADBUTT", "MOVE_STEALTH_ROCK"]),
        ("SPECIES_GIGALITH", ["MOVE_ROCK_SLIDE", "MOVE_EARTHQUAKE", "MOVE_HEAVY_SLAM", "MOVE_STEALTH_ROCK"]),
    ],
    "fighting": [
        ("SPECIES_MIENFOO", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_ROCK_TOMB", "MOVE_U_TURN"]),
        ("SPECIES_HAWLUCHA", ["MOVE_BRICK_BREAK", "MOVE_AERIAL_ACE", "MOVE_ROCK_TOMB", "MOVE_ENCORE"]),
        ("SPECIES_MIENSHAO", ["MOVE_DRAIN_PUNCH", "MOVE_U_TURN", "MOVE_ROCK_SLIDE", "MOVE_FAKE_OUT"]),
    ],
    "electric": [
        ("SPECIES_PAWMI", ["MOVE_SPARK", "MOVE_NUZZLE", "MOVE_ARM_THRUST", "MOVE_QUICK_ATTACK"]),
        ("SPECIES_LUXIO", ["MOVE_SPARK", "MOVE_BITE", "MOVE_THUNDER_WAVE", "MOVE_FACADE"]),
        ("SPECIES_LUXRAY", ["MOVE_WILD_CHARGE", "MOVE_CRUNCH", "MOVE_ICE_FANG", "MOVE_THUNDER_WAVE"]),
    ],
    "fire": [
        ("SPECIES_HOUNDOUR", ["MOVE_FIRE_FANG", "MOVE_BITE", "MOVE_WILL_O_WISP", "MOVE_ROAR"]),
        ("SPECIES_HOUNDOOM", ["MOVE_FLAMETHROWER", "MOVE_CRUNCH", "MOVE_WILL_O_WISP", "MOVE_SNARL"]),
        ("SPECIES_CHANDELURE", ["MOVE_FLAMETHROWER", "MOVE_SHADOW_BALL", "MOVE_ENERGY_BALL", "MOVE_WILL_O_WISP"]),
    ],
    "normal": [
        ("SPECIES_LILLIPUP", ["MOVE_BITE", "MOVE_HEADBUTT", "MOVE_WORK_UP", "MOVE_SAND_ATTACK"]),
        ("SPECIES_HERDIER", ["MOVE_TAKE_DOWN", "MOVE_CRUNCH", "MOVE_WORK_UP", "MOVE_ROAR"]),
        ("SPECIES_STOUTLAND", ["MOVE_BODY_SLAM", "MOVE_CRUNCH", "MOVE_PLAY_ROUGH", "MOVE_THUNDER_FANG"]),
    ],
    "flying": [
        ("SPECIES_STARLY", ["MOVE_WING_ATTACK", "MOVE_QUICK_ATTACK", "MOVE_DOUBLE_TEAM", "MOVE_ENDEAVOR"]),
        ("SPECIES_STARAVIA", ["MOVE_AERIAL_ACE", "MOVE_FACADE", "MOVE_QUICK_ATTACK", "MOVE_DOUBLE_TEAM"]),
        ("SPECIES_BRAVIARY", ["MOVE_BRAVE_BIRD", "MOVE_CRUSH_CLAW", "MOVE_ROCK_SLIDE", "MOVE_TAILWIND"]),
    ],
    "psychic": [
        ("SPECIES_ESPURR", ["MOVE_CONFUSION", "MOVE_FAKE_OUT", "MOVE_LIGHT_SCREEN", "MOVE_CHARM"]),
        ("SPECIES_SIGILYPH", ["MOVE_PSYBEAM", "MOVE_AIR_CUTTER", "MOVE_LIGHT_SCREEN", "MOVE_REFLECT"]),
        ("SPECIES_SIGILYPH", ["MOVE_PSYCHIC", "MOVE_AIR_SLASH", "MOVE_ENERGY_BALL", "MOVE_REFLECT"]),
    ],
    "water": [
        ("SPECIES_CORPHISH", ["MOVE_AQUA_JET", "MOVE_KNOCK_OFF", "MOVE_BUBBLE_BEAM", "MOVE_LEER"]),
        ("SPECIES_CRAWDAUNT", ["MOVE_CRABHAMMER", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_SWORDS_DANCE"]),
        ("SPECIES_CLAWITZER", ["MOVE_SURF", "MOVE_DARK_PULSE", "MOVE_AURA_SPHERE", "MOVE_ICE_BEAM"]),
    ],
    "dark": [
        ("SPECIES_SANDILE", ["MOVE_BITE", "MOVE_BULLDOZE", "MOVE_SAND_ATTACK", "MOVE_TORMENT"]),
        ("SPECIES_KROKOROK", ["MOVE_CRUNCH", "MOVE_DIG", "MOVE_ROCK_TOMB", "MOVE_TORMENT"]),
        ("SPECIES_KROOKODILE", ["MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_BRICK_BREAK"]),
    ],
    "ghost": [
        ("SPECIES_SHUPPET", ["MOVE_SHADOW_SNEAK", "MOVE_KNOCK_OFF", "MOVE_WILL_O_WISP", "MOVE_NIGHT_SHADE"]),
        ("SPECIES_BANETTE", ["MOVE_SHADOW_CLAW", "MOVE_KNOCK_OFF", "MOVE_WILL_O_WISP", "MOVE_SUCKER_PUNCH"]),
        ("SPECIES_MIMIKYU", ["MOVE_SHADOW_CLAW", "MOVE_PLAY_ROUGH", "MOVE_SHADOW_SNEAK", "MOVE_WILL_O_WISP"]),
    ],
    "ice": [
        ("SPECIES_SNORUNT", ["MOVE_ICY_WIND", "MOVE_BITE", "MOVE_HEADBUTT", "MOVE_PROTECT"]),
        ("SPECIES_SNEASEL", ["MOVE_ICE_SHARD", "MOVE_FEINT_ATTACK", "MOVE_AERIAL_ACE", "MOVE_TAUNT"]),
        ("SPECIES_FROSMOTH", ["MOVE_ICE_BEAM", "MOVE_BUG_BUZZ", "MOVE_GIGA_DRAIN", "MOVE_QUIVER_DANCE"]),
    ],
    "dragon": [
        ("SPECIES_AXEW", ["MOVE_DRAGON_RAGE", "MOVE_BITE", "MOVE_SCARY_FACE", "MOVE_DUAL_CHOP"]),
        ("SPECIES_FRAXURE", ["MOVE_DRAGON_CLAW", "MOVE_SLASH", "MOVE_ROCK_TOMB", "MOVE_DRAGON_DANCE"]),
        ("SPECIES_DRAGALGE", ["MOVE_DRAGON_PULSE", "MOVE_SLUDGE_BOMB", "MOVE_SURF", "MOVE_THUNDERBOLT"]),
    ],
    "grass": [
        ("SPECIES_BUDEW", ["MOVE_MEGA_DRAIN", "MOVE_STUN_SPORE", "MOVE_GROWTH", "MOVE_EXTRASENSORY"]),
        ("SPECIES_ROSELIA", ["MOVE_GIGA_DRAIN", "MOVE_SLUDGE", "MOVE_STUN_SPORE", "MOVE_LEECH_SEED"]),
        ("SPECIES_ROSERADE", ["MOVE_ENERGY_BALL", "MOVE_SLUDGE_BOMB", "MOVE_SHADOW_BALL", "MOVE_TOXIC_SPIKES"]),
    ],
    "bug": [
        ("SPECIES_JOLTIK", ["MOVE_STRUGGLE_BUG", "MOVE_ELECTROWEB", "MOVE_THUNDER_WAVE", "MOVE_SUCKER_PUNCH"]),
        ("SPECIES_GALVANTULA", ["MOVE_BUG_BUZZ", "MOVE_DISCHARGE", "MOVE_ENERGY_BALL", "MOVE_THUNDER_WAVE"]),
        ("SPECIES_SCOLIPEDE", ["MOVE_X_SCISSOR", "MOVE_POISON_JAB", "MOVE_ROCK_SLIDE", "MOVE_PROTECT"]),
    ],
    "poison": [
        ("SPECIES_SKORUPI", ["MOVE_POISON_FANG", "MOVE_BUG_BITE", "MOVE_BITE", "MOVE_ACUPRESSURE"]),
        ("SPECIES_DRAPION", ["MOVE_CROSS_POISON", "MOVE_CRUNCH", "MOVE_BUG_BITE", "MOVE_TOXIC_SPIKES"]),
        ("SPECIES_DRAPION", ["MOVE_POISON_JAB", "MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_TOXIC_SPIKES"]),
    ],
    "fairy": [
        ("SPECIES_CLEFAIRY", ["MOVE_DISARMING_VOICE", "MOVE_SING", "MOVE_MAGICAL_LEAF", "MOVE_ENCORE"]),
        ("SPECIES_TOGEKISS", ["MOVE_AIR_SLASH", "MOVE_DAZZLING_GLEAM", "MOVE_AURA_SPHERE", "MOVE_THUNDER_WAVE"]),
        ("SPECIES_TOGEKISS", ["MOVE_AIR_SLASH", "MOVE_MOONBLAST", "MOVE_AURA_SPHERE", "MOVE_THUNDER_WAVE"]),
    ],
    "general": [
        ("SPECIES_SHINX", ["MOVE_SPARK", "MOVE_BITE", "MOVE_LEER", "MOVE_QUICK_ATTACK"]),
        ("SPECIES_LUCARIO", ["MOVE_FORCE_PALM", "MOVE_METAL_CLAW", "MOVE_BONE_RUSH", "MOVE_QUICK_ATTACK"]),
        ("SPECIES_FLYGON", ["MOVE_DRAGON_CLAW", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_CRUNCH"]),
    ],
}

CLASS_THEMES = [
    ("Hiker", "rock"), ("Ruin Maniac", "rock"), ("Rocker", "electric"),
    ("Guitarist", "electric"), ("Bird Keeper", "flying"), ("Swimmer", "water"),
    ("Fisherman", "water"), ("Sailor", "water"), ("Bug Catcher", "bug"),
    ("Bug Maniac", "bug"), ("Ninja Boy", "poison"), ("Hex Maniac", "ghost"),
    ("Black Belt", "fighting"), ("Battle Girl", "fighting"), ("Psychic", "psychic"),
    ("Dragon Tamer", "dragon"), ("Aroma Lady", "grass"), ("Pokefan", "fairy"),
    ("Team Aqua", "water"), ("Aqua", "water"), ("Team Magma", "fire"),
    ("Magma", "fire"), ("Youngster", "normal"), ("Gentleman", "normal"),
]

BOSS_ADD = {
    "TRAINER_ROXANNE_1": ("SPECIES_ROGGENROLA", ["MOVE_ROCK_TOMB", "MOVE_BULLDOZE", "MOVE_HEADBUTT", "MOVE_STEALTH_ROCK"]),
    "TRAINER_BRAWLY_1": ("SPECIES_MIENFOO", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_ROCK_TOMB", "MOVE_U_TURN"]),
    "TRAINER_WATTSON_1": ("SPECIES_PAWMO", ["MOVE_SPARK", "MOVE_NUZZLE", "MOVE_ARM_THRUST", "MOVE_QUICK_ATTACK"]),
    "TRAINER_FLANNERY_1": ("SPECIES_HOUNDOOM", ["MOVE_FLAMETHROWER", "MOVE_CRUNCH", "MOVE_WILL_O_WISP", "MOVE_SNARL"]),
    "TRAINER_NORMAN_1": ("SPECIES_URSARING", ["MOVE_FACADE", "MOVE_CRUNCH", "MOVE_BRICK_BREAK", "MOVE_AERIAL_ACE"]),
    "TRAINER_WINONA_1": ("SPECIES_GLIGAR", ["MOVE_AERIAL_ACE", "MOVE_BULLDOZE", "MOVE_KNOCK_OFF", "MOVE_QUICK_ATTACK"]),
    "TRAINER_TATE_AND_LIZA_1": ("SPECIES_SIGILYPH", ["MOVE_PSYCHIC", "MOVE_AIR_SLASH", "MOVE_LIGHT_SCREEN", "MOVE_REFLECT"]),
    "TRAINER_JUAN_1": ("SPECIES_CLAWITZER", ["MOVE_SURF", "MOVE_DARK_PULSE", "MOVE_AURA_SPHERE", "MOVE_ICE_BEAM"]),
    "TRAINER_SIDNEY": ("SPECIES_KROOKODILE", ["MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_BRICK_BREAK"]),
    "TRAINER_PHOEBE": ("SPECIES_MIMIKYU", ["MOVE_SHADOW_CLAW", "MOVE_PLAY_ROUGH", "MOVE_SHADOW_SNEAK", "MOVE_WILL_O_WISP"]),
    "TRAINER_GLACIA": ("SPECIES_FROSMOTH", ["MOVE_ICE_BEAM", "MOVE_BUG_BUZZ", "MOVE_GIGA_DRAIN", "MOVE_QUIVER_DANCE"]),
    "TRAINER_DRAKE": ("SPECIES_DRAGALGE", ["MOVE_DRAGON_PULSE", "MOVE_SLUDGE_BOMB", "MOVE_SURF", "MOVE_THUNDERBOLT"]),
    "TRAINER_WALLACE": ("SPECIES_PRIMARINA", ["MOVE_SURF", "MOVE_MOONBLAST", "MOVE_ICE_BEAM", "MOVE_PSYCHIC"]),
}


def tier(level):
    return 0 if level < 22 else 1 if level < 38 else 2


def theme_for(label, trainer_class):
    if "AQUA" in label:
        return "water"
    if "MAGMA" in label:
        return "fire"
    if "SIDNEY" in label:
        return "dark"
    if "PHOEBE" in label:
        return "ghost"
    if "GLACIA" in label:
        return "ice"
    if "DRAKE" in label:
        return "dragon"
    for needle, theme in CLASS_THEMES:
        if needle.lower() in trainer_class.lower():
            return theme
    return "general"


def species_key(entry):
    first = entry.splitlines()[0]
    m = re.search(r"SPECIES_([A-Z0-9_]+)", first)
    if m:
        return m.group(1)
    token = first.split("@")[0].strip().split("(")[0].strip()
    return re.sub(r"[^A-Z0-9]", "_", token.upper())


def choose_addition(label, trainer_class, level, existing):
    if label in BOSS_ADD:
        species, moves = BOSS_ADD[label]
        if species.replace("SPECIES_", "") not in existing:
            return species, moves
    theme = theme_for(label, trainer_class)
    start = tier(level)
    # Try the intended tier first, then nearby tiers so we do not duplicate a Pokemon
    # already on the trainer's team.
    for idx in [start, max(0, start - 1), min(2, start + 1)]:
        species, moves = THEMES[theme][idx]
        if species.replace("SPECIES_", "") not in existing:
            return species, moves
    # Deterministic fallback for the rare case that all three thematic choices exist.
    idx = int(hashlib.sha256(label.encode()).hexdigest()[:4], 16) % 3
    return THEMES["general"][idx]


def upgrade_ai(meta, boss, level):
    wanted = ["Check Bad Move"]
    if level >= 24 or boss:
        wanted.append("Try To Faint")
    if boss:
        wanted.append("Check Viability")

    ai_index = None
    for i, line in enumerate(meta):
        if line.startswith("AI:"):
            ai_index = i
            break

    if ai_index is None:
        meta.append("AI: " + " / ".join(wanted))
        return meta

    flags = [x.strip() for x in meta[ai_index][3:].split("/") if x.strip()]
    seen = {x.lower() for x in flags}
    flags.extend(x for x in wanted if x.lower() not in seen)
    meta[ai_index] = "AI: " + " / ".join(flags)
    return meta


def upgrade_block(block):
    raw_lines = block.strip("\n").splitlines()
    if not raw_lines:
        return block, False, False
    hm = HEADER_RE.match(raw_lines[0])
    if not hm or hm.group(1) == "TRAINER_NONE":
        return block, False, False
    label = hm.group(1)

    # Trainer metadata ends at the first blank line. Keeping this boundary explicit
    # prevents trainerproc's required separator from ever being swallowed by regexes.
    try:
        sep = raw_lines.index("")
    except ValueError:
        return block, False, False
    meta = raw_lines[:sep]
    body = "\n".join(raw_lines[sep + 1:]).strip()
    if not body:
        return block, False, False

    entries = [e.strip() for e in re.split(r"\n\s*\n", body) if e.strip()]
    if not entries:
        return block, False, False

    levels = [int(x) for x in LEVEL_RE.findall(body)] or [5]
    max_level = max(levels)
    trainer_class = ""
    for line in meta:
        if line.startswith("Class:"):
            trainer_class = line.split(":", 1)[1].strip()
            break

    existing = {species_key(e) for e in entries}
    species, moves = choose_addition(label, trainer_class, max_level, existing)
    new_level = max_level if label in BOSSES else max(2, max_level - 1)
    iv = 20 if label in BOSSES else 12
    new_entry = "\n".join([
        species,
        f"Level: {new_level}",
        f"IVs: {iv} HP / {iv} Atk / {iv} Def / {iv} SpA / {iv} SpD / {iv} Spe",
        *[f"- {move}" for move in moves],
    ])

    if len(entries) >= 6:
        entries[-1] = new_entry
    else:
        entries.append(new_entry)

    meta = upgrade_ai(meta, label in BOSSES, max_level)
    rebuilt = "\n".join(meta) + "\n\n" + "\n\n".join(entries) + "\n\n"
    return rebuilt, True, label in BOSSES


def main():
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    total = bosses = 0
    for part in parts:
        new_part, changed, was_boss = upgrade_block(part)
        out.append(new_part)
        total += int(changed)
        bosses += int(changed and was_boss)
    TRAINERS.write_text("".join(out))
    print(f"Upgraded {total} trainer parties with one themed new Pokemon; {bosses} major bosses received curated additions and stronger AI.")


if __name__ == "__main__":
    main()
