#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINERS = ROOT / "src/data/trainers.party"

BOSS_TEAMS = {
    "TRAINER_ROXANNE_1": [
        ("SPECIES_GEODUDE", 15, "ITEM_ORAN_BERRY", ["MOVE_ROCK_TOMB", "MOVE_BULLDOZE", "MOVE_ROCK_POLISH", "MOVE_TACKLE"]),
        ("SPECIES_ROGGENROLA", 16, "ITEM_ORAN_BERRY", ["MOVE_ROCK_TOMB", "MOVE_HEADBUTT", "MOVE_MUD_SLAP", "MOVE_STEALTH_ROCK"]),
        ("SPECIES_NOSEPASS", 18, "ITEM_SITRUS_BERRY", ["MOVE_ROCK_TOMB", "MOVE_THUNDER_WAVE", "MOVE_BLOCK", "MOVE_BULLDOZE"]),
    ],
    "TRAINER_BRAWLY_1": [
        ("SPECIES_MACHOP", 19, "ITEM_ORAN_BERRY", ["MOVE_BULK_UP", "MOVE_KARATE_CHOP", "MOVE_ROCK_TOMB", "MOVE_FOCUS_ENERGY"]),
        ("SPECIES_MIENFOO", 20, "ITEM_ORAN_BERRY", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_ROCK_TOMB", "MOVE_U_TURN"]),
        ("SPECIES_MAKUHITA", 22, "ITEM_SITRUS_BERRY", ["MOVE_BULK_UP", "MOVE_ARM_THRUST", "MOVE_KNOCK_OFF", "MOVE_SMELLING_SALTS"]),
    ],
    "TRAINER_WATTSON_1": [
        ("SPECIES_VOLTORB", 24, "ITEM_MAGNET", ["MOVE_VOLT_SWITCH", "MOVE_ROLLOUT", "MOVE_THUNDER_WAVE", "MOVE_LIGHT_SCREEN"]),
        ("SPECIES_PAWMO", 25, "ITEM_SITRUS_BERRY", ["MOVE_SPARK", "MOVE_NUZZLE", "MOVE_ARM_THRUST", "MOVE_QUICK_ATTACK"]),
        ("SPECIES_MAGNETON", 25, "ITEM_EVIOLITE", ["MOVE_SHOCK_WAVE", "MOVE_MIRROR_SHOT", "MOVE_THUNDER_WAVE", "MOVE_SUPERSONIC"]),
        ("SPECIES_MANECTRIC", 27, "ITEM_SITRUS_BERRY", ["MOVE_SHOCK_WAVE", "MOVE_BITE", "MOVE_FLAME_BURST", "MOVE_QUICK_ATTACK"]),
    ],
    "TRAINER_FLANNERY_1": [
        ("SPECIES_NUMEL", 29, "ITEM_CHARCOAL", ["MOVE_LAVA_PLUME", "MOVE_BULLDOZE", "MOVE_ROCK_TOMB", "MOVE_AMNESIA"]),
        ("SPECIES_HOUNDOOM", 30, "ITEM_SITRUS_BERRY", ["MOVE_FLAMETHROWER", "MOVE_CRUNCH", "MOVE_WILL_O_WISP", "MOVE_SNARL"]),
        ("SPECIES_CAMERUPT", 30, "ITEM_SOFT_SAND", ["MOVE_LAVA_PLUME", "MOVE_EARTH_POWER", "MOVE_ROCK_SLIDE", "MOVE_YAWN"]),
        ("SPECIES_TORKOAL", 32, "ITEM_SITRUS_BERRY", ["MOVE_OVERHEAT", "MOVE_BODY_SLAM", "MOVE_PROTECT", "MOVE_SUNNY_DAY"]),
    ],
    "TRAINER_NORMAN_1": [
        ("SPECIES_VIGOROTH", 32, "ITEM_SITRUS_BERRY", ["MOVE_SLASH", "MOVE_BULK_UP", "MOVE_SHADOW_CLAW", "MOVE_ENCORE"]),
        ("SPECIES_URSARING", 33, "ITEM_SILK_SCARF", ["MOVE_FACADE", "MOVE_CRUNCH", "MOVE_BRICK_BREAK", "MOVE_AERIAL_ACE"]),
        ("SPECIES_ZANGOOSE", 33, "ITEM_EXPERT_BELT", ["MOVE_SLASH", "MOVE_X_SCISSOR", "MOVE_BRICK_BREAK", "MOVE_SWORDS_DANCE"]),
        ("SPECIES_SLAKING", 35, "ITEM_SITRUS_BERRY", ["MOVE_FACADE", "MOVE_SHADOW_CLAW", "MOVE_ROCK_SLIDE", "MOVE_YAWN"]),
    ],
    "TRAINER_WINONA_1": [
        ("SPECIES_SWELLOW", 35, "ITEM_SHARP_BEAK", ["MOVE_AERIAL_ACE", "MOVE_FACADE", "MOVE_U_TURN", "MOVE_QUICK_ATTACK"]),
        ("SPECIES_GLIGAR", 35, "ITEM_EVIOLITE", ["MOVE_AERIAL_ACE", "MOVE_BULLDOZE", "MOVE_KNOCK_OFF", "MOVE_ROCK_TOMB"]),
        ("SPECIES_PELIPPER", 36, "ITEM_DAMP_ROCK", ["MOVE_SURF", "MOVE_AIR_SLASH", "MOVE_ROOST", "MOVE_RAIN_DANCE"]),
        ("SPECIES_SKARMORY", 36, "ITEM_SITRUS_BERRY", ["MOVE_STEEL_WING", "MOVE_AERIAL_ACE", "MOVE_SPIKES", "MOVE_ROOST"]),
        ("SPECIES_ALTARIA", 38, "ITEM_SITRUS_BERRY", ["MOVE_DRAGON_CLAW", "MOVE_AERIAL_ACE", "MOVE_EARTHQUAKE", "MOVE_DRAGON_DANCE"]),
    ],
    "TRAINER_TATE_AND_LIZA_1": [
        ("SPECIES_CLAYDOL", 42, "ITEM_LIGHT_CLAY", ["MOVE_PSYCHIC", "MOVE_EARTH_POWER", "MOVE_LIGHT_SCREEN", "MOVE_REFLECT"]),
        ("SPECIES_SIGILYPH", 42, "ITEM_SITRUS_BERRY", ["MOVE_PSYCHIC", "MOVE_AIR_SLASH", "MOVE_ENERGY_BALL", "MOVE_TAILWIND"]),
        ("SPECIES_SOLROCK", 43, "ITEM_SITRUS_BERRY", ["MOVE_ROCK_SLIDE", "MOVE_ZEN_HEADBUTT", "MOVE_FLAMETHROWER", "MOVE_SUNNY_DAY"]),
        ("SPECIES_LUNATONE", 43, "ITEM_SITRUS_BERRY", ["MOVE_PSYCHIC", "MOVE_POWER_GEM", "MOVE_ICE_BEAM", "MOVE_CALM_MIND"]),
    ],
    "TRAINER_JUAN_1": [
        ("SPECIES_LANTURN", 45, "ITEM_LEFTOVERS", ["MOVE_SURF", "MOVE_DISCHARGE", "MOVE_ICE_BEAM", "MOVE_THUNDER_WAVE"]),
        ("SPECIES_CLAWITZER", 45, "ITEM_EXPERT_BELT", ["MOVE_SURF", "MOVE_DARK_PULSE", "MOVE_AURA_SPHERE", "MOVE_ICE_BEAM"]),
        ("SPECIES_KINGDRA", 46, "ITEM_LUM_BERRY", ["MOVE_SURF", "MOVE_DRAGON_PULSE", "MOVE_ICE_BEAM", "MOVE_RAIN_DANCE"]),
        ("SPECIES_WHISCASH", 46, "ITEM_RINDO_BERRY", ["MOVE_WATERFALL", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_DRAGON_DANCE"]),
        ("SPECIES_MILOTIC", 48, "ITEM_LEFTOVERS", ["MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_RECOVER", "MOVE_TOXIC"]),
    ],
    "TRAINER_SIDNEY": [
        ("SPECIES_MIGHTYENA", 51, "ITEM_CHOICE_BAND", ["MOVE_CRUNCH", "MOVE_PLAY_ROUGH", "MOVE_FIRE_FANG", "MOVE_SUCKER_PUNCH"]),
        ("SPECIES_SHIFTRY", 52, "ITEM_LIFE_ORB", ["MOVE_LEAF_BLADE", "MOVE_KNOCK_OFF", "MOVE_ROCK_SLIDE", "MOVE_FAKE_OUT"]),
        ("SPECIES_CRAWDAUNT", 52, "ITEM_EXPERT_BELT", ["MOVE_CRABHAMMER", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_BRICK_BREAK"]),
        ("SPECIES_KROOKODILE", 53, "ITEM_SOFT_SAND", ["MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_BRICK_BREAK"]),
        ("SPECIES_ABSOL", 53, "ITEM_SCOPE_LENS", ["MOVE_NIGHT_SLASH", "MOVE_PSYCHO_CUT", "MOVE_PLAY_ROUGH", "MOVE_SWORDS_DANCE"]),
        ("SPECIES_HOUNDOOM", 54, "ITEM_LUM_BERRY", ["MOVE_DARK_PULSE", "MOVE_FLAMETHROWER", "MOVE_SLUDGE_BOMB", "MOVE_NASTY_PLOT"]),
    ],
    "TRAINER_PHOEBE": [
        ("SPECIES_DUSCLOPS", 52, "ITEM_EVIOLITE", ["MOVE_SHADOW_PUNCH", "MOVE_WILL_O_WISP", "MOVE_PAIN_SPLIT", "MOVE_ICE_PUNCH"]),
        ("SPECIES_BANETTE", 52, "ITEM_SPELL_TAG", ["MOVE_SHADOW_CLAW", "MOVE_KNOCK_OFF", "MOVE_WILL_O_WISP", "MOVE_SUCKER_PUNCH"]),
        ("SPECIES_MISMAGIUS", 53, "ITEM_LIFE_ORB", ["MOVE_SHADOW_BALL", "MOVE_MYSTICAL_FIRE", "MOVE_POWER_GEM", "MOVE_THUNDERBOLT"]),
        ("SPECIES_MIMIKYU", 53, "ITEM_LUM_BERRY", ["MOVE_SHADOW_CLAW", "MOVE_PLAY_ROUGH", "MOVE_SHADOW_SNEAK", "MOVE_SWORDS_DANCE"]),
        ("SPECIES_DUSKNOIR", 54, "ITEM_LEFTOVERS", ["MOVE_SHADOW_PUNCH", "MOVE_EARTHQUAKE", "MOVE_ICE_PUNCH", "MOVE_PAIN_SPLIT"]),
        ("SPECIES_CHANDELURE", 54, "ITEM_EXPERT_BELT", ["MOVE_SHADOW_BALL", "MOVE_FLAMETHROWER", "MOVE_ENERGY_BALL", "MOVE_PSYCHIC"]),
    ],
    "TRAINER_GLACIA": [
        ("SPECIES_FROSLASS", 53, "ITEM_FOCUS_SASH", ["MOVE_ICE_BEAM", "MOVE_SHADOW_BALL", "MOVE_THUNDERBOLT", "MOVE_SPIKES"]),
        ("SPECIES_WALREIN", 53, "ITEM_LEFTOVERS", ["MOVE_ICE_BEAM", "MOVE_SURF", "MOVE_BODY_SLAM", "MOVE_PROTECT"]),
        ("SPECIES_FROSMOTH", 54, "ITEM_LIFE_ORB", ["MOVE_ICE_BEAM", "MOVE_BUG_BUZZ", "MOVE_GIGA_DRAIN", "MOVE_QUIVER_DANCE"]),
        ("SPECIES_MAMOSWINE", 54, "ITEM_NEVER_MELT_ICE", ["MOVE_ICICLE_CRASH", "MOVE_EARTHQUAKE", "MOVE_ICE_SHARD", "MOVE_ROCK_SLIDE"]),
        ("SPECIES_GLALIE", 55, "ITEM_LUM_BERRY", ["MOVE_ICE_BEAM", "MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_EXPLOSION"]),
        ("SPECIES_WEAVILE", 55, "ITEM_EXPERT_BELT", ["MOVE_ICICLE_CRASH", "MOVE_KNOCK_OFF", "MOVE_ICE_SHARD", "MOVE_BRICK_BREAK"]),
    ],
    "TRAINER_DRAKE": [
        ("SPECIES_FLYGON", 54, "ITEM_SOFT_SAND", ["MOVE_DRAGON_CLAW", "MOVE_EARTHQUAKE", "MOVE_ROCK_SLIDE", "MOVE_U_TURN"]),
        ("SPECIES_DRAGALGE", 54, "ITEM_BLACK_SLUDGE", ["MOVE_DRAGON_PULSE", "MOVE_SLUDGE_BOMB", "MOVE_SURF", "MOVE_THUNDERBOLT"]),
        ("SPECIES_KINGDRA", 55, "ITEM_LUM_BERRY", ["MOVE_DRAGON_PULSE", "MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_AGILITY"]),
        ("SPECIES_ALTARIA", 55, "ITEM_LEFTOVERS", ["MOVE_DRAGON_CLAW", "MOVE_EARTHQUAKE", "MOVE_ROOST", "MOVE_DRAGON_DANCE"]),
        ("SPECIES_HAXORUS", 56, "ITEM_EXPERT_BELT", ["MOVE_DRAGON_CLAW", "MOVE_EARTHQUAKE", "MOVE_POISON_JAB", "MOVE_DRAGON_DANCE"]),
        ("SPECIES_SALAMENCE", 57, "ITEM_LIFE_ORB", ["MOVE_DRAGON_CLAW", "MOVE_FLY", "MOVE_EARTHQUAKE", "MOVE_FLAMETHROWER"]),
    ],
    "TRAINER_WALLACE": [
        ("SPECIES_TENTACRUEL", 56, "ITEM_BLACK_SLUDGE", ["MOVE_SURF", "MOVE_SLUDGE_BOMB", "MOVE_ICE_BEAM", "MOVE_TOXIC_SPIKES"]),
        ("SPECIES_LUDICOLO", 56, "ITEM_LEFTOVERS", ["MOVE_SURF", "MOVE_GIGA_DRAIN", "MOVE_ICE_BEAM", "MOVE_RAIN_DANCE"]),
        ("SPECIES_PRIMARINA", 57, "ITEM_EXPERT_BELT", ["MOVE_SURF", "MOVE_MOONBLAST", "MOVE_ICE_BEAM", "MOVE_PSYCHIC"]),
        ("SPECIES_GYARADOS", 57, "ITEM_LUM_BERRY", ["MOVE_WATERFALL", "MOVE_CRUNCH", "MOVE_EARTHQUAKE", "MOVE_DRAGON_DANCE"]),
        ("SPECIES_KINGDRA", 58, "ITEM_SCOPE_LENS", ["MOVE_SURF", "MOVE_DRAGON_PULSE", "MOVE_ICE_BEAM", "MOVE_FLASH_CANNON"]),
        ("SPECIES_MILOTIC", 59, "ITEM_LEFTOVERS", ["MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_RECOVER", "MOVE_TOXIC"]),
    ],
}

IMPORTANT_CLASS_WORDS = ("Leader", "Elite Four", "Champion", "Admin", "Aqua Leader", "Magma Leader", "Cooltrainer", "Ace Trainer")
IMPORTANT_LABEL_WORDS = ("ARCHIE", "MAXIE", "RIVAL", "WALLY", "STEVEN")
ROTATION_ITEMS = ["ITEM_SITRUS_BERRY", "ITEM_LUM_BERRY", "ITEM_EXPERT_BELT", "ITEM_LEFTOVERS"]


def format_mon(species, level, item, moves, iv=20):
    lines = [f"{species} @ {item}", f"Level: {level}", f"IVs: {iv} HP / {iv} Atk / {iv} Def / {iv} SpA / {iv} SpD / {iv} Spe"]
    lines += [f"- {move}" for move in moves]
    return "\n".join(lines)


def strengthen_meta(meta):
    lines = meta.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith("AI:"):
            lines[i] = "AI: Check Bad Move / Try To Faint / Check Viability"
            found = True
            break
    if not found:
        lines.append("AI: Check Bad Move / Try To Faint / Check Viability")
    return "\n".join(lines)


def add_held_items(party, level_hint=30):
    chunks = party.strip().split("\n\n") if party.strip() else []
    out = []
    changed = 0
    for idx, chunk in enumerate(chunks):
        lines = chunk.splitlines()
        if not lines:
            continue
        first = lines[0]
        if " @ " not in first and not first.startswith("/*"):
            item = "ITEM_ORAN_BERRY" if level_hint < 20 else "ITEM_SITRUS_BERRY" if level_hint < 35 else ROTATION_ITEMS[idx % len(ROTATION_ITEMS)]
            lines[0] = first + " @ " + item
            changed += 1
        out.append("\n".join(lines))
    return "\n\n".join(out), changed


def process_block(block):
    m = re.match(r"(=== (TRAINER_[A-Z0-9_]+) ===\n)(.*)", block, re.S)
    if not m:
        return block, 0, 0
    header, label, rest = m.groups()
    if "\n\n" not in rest:
        return block, 0, 0
    meta, party = rest.split("\n\n", 1)

    if label in BOSS_TEAMS:
        meta = strengthen_meta(meta)
        mons = BOSS_TEAMS[label]
        new_party = "\n\n".join(format_mon(*mon, iv=24 if mons[0][1] >= 50 else 18) for mon in mons)
        return header + meta.rstrip() + "\n\n" + new_party + "\n\n", 1, len(mons)

    class_match = re.search(r"^Class:\s*(.+)$", meta, re.M)
    trainer_class = class_match.group(1) if class_match else ""
    important = any(word.lower() in trainer_class.lower() for word in IMPORTANT_CLASS_WORDS) or any(word in label for word in IMPORTANT_LABEL_WORDS)
    if not important:
        return block, 0, 0

    levels = [int(x) for x in re.findall(r"^Level:\s*(\d+)$", party, re.M)]
    level_hint = max(levels) if levels else 30
    party, item_count = add_held_items(party, level_hint)
    if item_count:
        meta = strengthen_meta(meta)
    return header + meta.rstrip() + "\n\n" + party.rstrip() + "\n\n", 0, item_count


def main():
    text = TRAINERS.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    tuned = held = 0
    for part in parts:
        new_part, boss_count, item_count = process_block(part)
        out.append(new_part)
        tuned += boss_count
        held += item_count
    TRAINERS.write_text("".join(out))
    print(f"Hand-tuned {tuned} major boss teams and added {held} held items to other important trainers.")


if __name__ == "__main__":
    main()
