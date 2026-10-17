#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"

HEADER_RE = re.compile(r"^=== (TRAINER_[A-Z0-9_]+) ===$", re.M)
LEVEL_RE = re.compile(r"^Level:\s*(\d+)\s*$", re.M)
CLASS_RE = re.compile(r"^Class:\s*(.+?)\s*$", re.M)
AI_RE = re.compile(r"^AI:\s*(.+?)\s*$", re.M)

BOSSES = {
    "TRAINER_ROXANNE_1", "TRAINER_BRAWLY_1", "TRAINER_WATTSON_1",
    "TRAINER_FLANNERY_1", "TRAINER_NORMAN_1", "TRAINER_WINONA_1",
    "TRAINER_TATE_AND_LIZA_1", "TRAINER_JUAN_1", "TRAINER_SIDNEY",
    "TRAINER_PHOEBE", "TRAINER_GLACIA", "TRAINER_DRAKE", "TRAINER_WALLACE",
}

# species, low/mid/high moves. The pools are intentionally practical rather than
# competitive-perfect: STAB first, one useful coverage move, then utility.
POOLS = {
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
        ("SPECIES_LILLIPUP", ["MOVE_BITE", "MOVE_TACKLE", "MOVE_WORK_UP", "MOVE_SAND_ATTACK"]),
        ("SPECIES_HERDIER", ["MOVE_TAKE_DOWN", "MOVE_CRUNCH", "MOVE_WORK_UP", "MOVE_ROAR"]),
        ("SPECIES_STOUTLAND", ["MOVE_RETURN", "MOVE_CRUNCH", "MOVE_PLAY_ROUGH", "MOVE_THUNDER_FANG"]),
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
    "steel": [
        ("SPECIES_ARON", ["MOVE_METAL_CLAW", "MOVE_ROCK_TOMB", "MOVE_HEADBUTT", "MOVE_MUD_SLAP"]),
        ("SPECIES_LAIRON", ["MOVE_IRON_HEAD", "MOVE_ROCK_SLIDE", "MOVE_BULLDOZE", "MOVE_ROAR"]),
        ("SPECIES_AGGRON", ["MOVE_IRON_HEAD", "MOVE_ROCK_SLIDE", "MOVE_EARTHQUAKE", "MOVE_THUNDER_PUNCH"]),
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
    ("Dragon Tamer", "dragon"), ("Aroma Lady", "grass"), ("Triathlete", "general"),
    ("Pokefan", "fairy"), ("Team Aqua", "water"), ("Aqua", "water"),
    ("Team Magma", "fire"), ("Magma", "fire"), ("Collector", "general"),
    ("Cooltrainer", "general"), ("Ace Trainer", "general"), ("Youngster", "normal"),
    ("Lass", "fairy"), ("School Kid", "general"), ("Gentleman", "normal"),
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


def tier_for(level: int) -> int:
    if level < 22:
        return 0
    if level < 38:
        return 1
    return 2


def is_species_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith(("- ", "===", "#", "//", "/*", "*", "*/")):
        return False
    if ":" in s:
        return False
    return True


def species_key(line: str) -> str:
    m = re.search(r"SPECIES_([A-Z0-9_]+)", line)
    if m:
        return m.group(1)
    token = line.split("@")[0].strip().split("(")[0].strip()
    return re.sub(r"[^A-Z0-9]", "_", token.upper())


def choose_theme(label: str, cls: str) -> str:
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
        if needle.lower() in cls.lower():
            return theme
    return "general"


def pick_candidate(label: str, cls: str, level: int, existing: set[str]):
    if label in BOSS_ADD and BOSS_ADD[label][0].replace("SPECIES_", "") not in existing:
        return BOSS_ADD[label]

    theme = choose_theme(label, cls)
    tier = tier_for(level)
    themes = [theme, "general", "normal", "flying", "water", "grass"]
    # Deterministic rotation prevents every trainer of one class from receiving the same mon.
    offset = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)
    for theme_name in themes:
        pool = POOLS[theme_name]
        for step in range(len(pool)):
            idx = min(2, max(0, tier + ((offset + step) % 3) - 1))
            species, moves = pool[idx]
            if species.replace("SPECIES_", "") not in existing:
                return species, moves
    return POOLS["general"][tier]


def improve_ai(block: str, first_mon_pos: int, boss: bool, max_level: int) -> str:
    wanted = ["Check Bad Move"]
    if boss or max_level >= 24:
        wanted.append("Try To Faint")
    if boss:
        wanted.append("Check Viability")

    m = AI_RE.search(block)
    if m:
        flags = [p.strip() for p in m.group(1).split("/") if p.strip()]
        low = {f.lower() for f in flags}
        flags.extend(w for w in wanted if w.lower() not in low)
        return block[:m.start()] + "AI: " + " / ".join(flags) + block[m.end():]

    insert = "AI: " + " / ".join(wanted) + "\n\n"
    return block[:first_mon_pos] + insert + block[first_mon_pos:]


def upgrade_block(block: str):
    hm = HEADER_RE.search(block)
    if not hm or hm.group(1) == "TRAINER_NONE":
        return block, False, False
    label = hm.group(1)
    lines = block.splitlines(keepends=True)
    mon_indices = [i for i, line in enumerate(lines) if is_species_line(line)]
    if not mon_indices:
        return block, False, False

    existing = {species_key(lines[i]) for i in mon_indices}
    levels = [int(x) for x in LEVEL_RE.findall(block)] or [5]
    max_level = max(levels)
    cls_m = CLASS_RE.search(block)
    cls = cls_m.group(1) if cls_m else ""
    species, moves = pick_candidate(label, cls, max_level, existing)
    new_level = max(2, max_level if label in BOSSES else max_level - 1)

    entry = [
        f"{species}\n",
        f"Level: {new_level}\n",
        "IVs: 12 HP / 12 Atk / 12 Def / 12 SpA / 12 SpD / 12 Spe\n" if label not in BOSSES else
        "IVs: 20 HP / 20 Atk / 20 Def / 20 SpA / 20 SpD / 20 Spe\n",
    ]
    entry += [f"- {move}\n" for move in moves]
    entry_text = "\n" + "".join(entry)

    # Six is the party cap. Full teams get their last slot replaced so every trainer
    # still receives a genuinely new Pokemon rather than producing an invalid 7-mon party.
    if len(mon_indices) >= 6:
        cut_line = mon_indices[-1]
        prefix = "".join(lines[:cut_line]).rstrip() + "\n"
        block = prefix + entry_text
    else:
        block = block.rstrip() + "\n" + entry_text

    # Recompute first Pokemon location after the party edit, then modestly improve AI.
    lines2 = block.splitlines(keepends=True)
    cursor = 0
    first_pos = None
    for line in lines2:
        if is_species_line(line):
            first_pos = cursor
            break
        cursor += len(line)
    if first_pos is not None:
        block = improve_ai(block, first_pos, label in BOSSES, max_level)

    return block.rstrip() + "\n\n", True, label in BOSSES


def main():
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    changed = []
    total = bosses = 0
    for part in parts:
        new_part, did_change, was_boss = upgrade_block(part)
        changed.append(new_part)
        total += int(did_change)
        bosses += int(did_change and was_boss)
    TRAINERS.write_text("".join(changed))
    print(f"Upgraded {total} trainer parties with one themed new Pokemon; {bosses} major bosses received curated additions and stronger AI.")


if __name__ == "__main__":
    main()
