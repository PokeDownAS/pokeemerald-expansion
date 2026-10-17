#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "src/data/trainers.party"

# Emerald Deluxe battle philosophy:
# - readable themes and recognizable plans
# - useful status, pivoting, setup, weather, hazards and priority
# - no blanket competitive EV/IV perfection or giant level spikes
# - ordinary trainers get one "personality" Pokémon; bosses get a signature tactical piece

BOSS_SETS = {
    "TRAINER_ROXANNE_1": ("SPECIES_ROCKRUFF", "ITEM_ORAN_BERRY", ["MOVE_STEALTH_ROCK", "MOVE_ROCK_TOMB", "MOVE_BITE", "MOVE_HOWL"]),
    "TRAINER_BRAWLY_1": ("SPECIES_CROAGUNK", "ITEM_ORAN_BERRY", ["MOVE_FAKE_OUT", "MOVE_LOW_SWEEP", "MOVE_POISON_JAB", "MOVE_TAUNT"]),
    "TRAINER_WATTSON_1": ("SPECIES_BELLIBOLT", "ITEM_SITRUS_BERRY", ["MOVE_DISCHARGE", "MOVE_MUD_SHOT", "MOVE_THUNDER_WAVE", "MOVE_SLACK_OFF"]),
    "TRAINER_FLANNERY_1": ("SPECIES_HOUNDOOM", "ITEM_HEAT_ROCK", ["MOVE_SUNNY_DAY", "MOVE_FLAMETHROWER", "MOVE_SNARL", "MOVE_WILL_O_WISP"]),
    "TRAINER_NORMAN_1": ("SPECIES_BEWEAR", "ITEM_SITRUS_BERRY", ["MOVE_BULK_UP", "MOVE_FACADE", "MOVE_PAYBACK", "MOVE_PROTECT"]),
    "TRAINER_WINONA_1": ("SPECIES_GLISCOR", "ITEM_SITRUS_BERRY", ["MOVE_TAILWIND", "MOVE_AERIAL_ACE", "MOVE_BULLDOZE", "MOVE_U_TURN"]),
    "TRAINER_TATE_AND_LIZA_1": ("SPECIES_METAGROSS", "ITEM_SITRUS_BERRY", ["MOVE_ZEN_HEADBUTT", "MOVE_METEOR_MASH", "MOVE_ROCK_SLIDE", "MOVE_PROTECT"]),
    "TRAINER_JUAN_1": ("SPECIES_LAPRAS", "ITEM_DAMP_ROCK", ["MOVE_RAIN_DANCE", "MOVE_SURF", "MOVE_ICE_BEAM", "MOVE_SING"]),
    "TRAINER_SIDNEY": ("SPECIES_KINGAMBIT", "ITEM_BLACK_GLASSES", ["MOVE_KOWTOW_CLEAVE", "MOVE_IRON_HEAD", "MOVE_SUCKER_PUNCH", "MOVE_SWORDS_DANCE"]),
    "TRAINER_PHOEBE": ("SPECIES_ANNIHILAPE", "ITEM_SITRUS_BERRY", ["MOVE_RAGE_FIST", "MOVE_DRAIN_PUNCH", "MOVE_BULK_UP", "MOVE_TAUNT"]),
    "TRAINER_GLACIA": ("SPECIES_BAXCALIBUR", "ITEM_NEVER_MELT_ICE", ["MOVE_ICICLE_CRASH", "MOVE_DRAGON_CLAW", "MOVE_ICE_SHARD", "MOVE_SWORDS_DANCE"]),
    "TRAINER_DRAKE": ("SPECIES_DRAGAPULT", "ITEM_DRAGON_FANG", ["MOVE_DRAGON_DARTS", "MOVE_SHADOW_BALL", "MOVE_U_TURN", "MOVE_THUNDER_WAVE"]),
    "TRAINER_WALLACE": ("SPECIES_PALAFIN", "ITEM_MYSTIC_WATER", ["MOVE_FLIP_TURN", "MOVE_JET_PUNCH", "MOVE_ICE_PUNCH", "MOVE_BULK_UP"]),
}

# These are the extra class-identity Pokémon injected by build_mod.py (or their
# progression-safe pre-evolutions). Giving only this one member a designed set makes
# random trainers memorable without turning every route into a boss gauntlet.
PERSONALITY_SETS = {
    "SPECIES_NYMBLE": ("ITEM_ORAN_BERRY", ["MOVE_STRUGGLE_BUG", "MOVE_QUICK_ATTACK", "MOVE_LEER"]),
    "SPECIES_LOKIX": ("ITEM_BLACK_GLASSES", ["MOVE_LUNGE", "MOVE_SUCKER_PUNCH", "MOVE_U_TURN", "MOVE_TAUNT"]),
    "SPECIES_WATTREL": ("ITEM_ORAN_BERRY", ["MOVE_SPARK", "MOVE_GROWL", "MOVE_QUICK_ATTACK"]),
    "SPECIES_KILOWATTREL": ("ITEM_MAGNET", ["MOVE_VOLT_SWITCH", "MOVE_AIR_SLASH", "MOVE_THUNDER_WAVE", "MOVE_ROOST"]),
    "SPECIES_EEVEE": ("ITEM_ORAN_BERRY", ["MOVE_QUICK_ATTACK", "MOVE_BITE", "MOVE_SAND_ATTACK"]),
    "SPECIES_ESPEON": ("ITEM_TWISTED_SPOON", ["MOVE_PSYCHIC", "MOVE_CALM_MIND", "MOVE_MORNING_SUN", "MOVE_SWIFT"]),
    "SPECIES_MISDREAVUS": ("ITEM_ORAN_BERRY", ["MOVE_HEX", "MOVE_CONFUSE_RAY", "MOVE_WILL_O_WISP", "MOVE_SHADOW_SNEAK"]),
    "SPECIES_MISMAGIUS": ("ITEM_SPELL_TAG", ["MOVE_SHADOW_BALL", "MOVE_MYSTICAL_FIRE", "MOVE_WILL_O_WISP", "MOVE_HEX"]),
    "SPECIES_FROAKIE": ("ITEM_ORAN_BERRY", ["MOVE_WATER_PULSE", "MOVE_QUICK_ATTACK", "MOVE_LICK"]),
    "SPECIES_FROGADIER": ("ITEM_MYSTIC_WATER", ["MOVE_WATER_PULSE", "MOVE_ICY_WIND", "MOVE_U_TURN", "MOVE_SMOKESCREEN"]),
    "SPECIES_GRENINJA": ("ITEM_MYSTIC_WATER", ["MOVE_SURF", "MOVE_DARK_PULSE", "MOVE_ICE_BEAM", "MOVE_U_TURN"]),
    "SPECIES_MACHOP": ("ITEM_BLACK_BELT", ["MOVE_LOW_SWEEP", "MOVE_ROCK_TOMB", "MOVE_BULK_UP", "MOVE_KNOCK_OFF"]),
    "SPECIES_HAWLUCHA": ("ITEM_BLACK_BELT", ["MOVE_FLYING_PRESS", "MOVE_ROOST", "MOVE_SWORDS_DANCE", "MOVE_QUICK_ATTACK"]),
    "SPECIES_RIOLU": ("ITEM_ORAN_BERRY", ["MOVE_FORCE_PALM", "MOVE_QUICK_ATTACK", "MOVE_SCREECH", "MOVE_BITE"]),
    "SPECIES_LUCARIO": ("ITEM_BLACK_BELT", ["MOVE_AURA_SPHERE", "MOVE_BULLET_PUNCH", "MOVE_SWORDS_DANCE", "MOVE_DARK_PULSE"]),
    "SPECIES_BUIZEL": ("ITEM_ORAN_BERRY", ["MOVE_AQUA_JET", "MOVE_BITE", "MOVE_SWIFT", "MOVE_RAIN_DANCE"]),
    "SPECIES_FLOATZEL": ("ITEM_MYSTIC_WATER", ["MOVE_WATERFALL", "MOVE_AQUA_JET", "MOVE_ICE_PUNCH", "MOVE_CRUNCH"]),
    "SPECIES_BASCULIN": ("ITEM_MYSTIC_WATER", ["MOVE_AQUA_JET", "MOVE_CRUNCH", "MOVE_SCARY_FACE", "MOVE_TAKE_DOWN"]),
    "SPECIES_BASCULEGION": ("ITEM_MYSTIC_WATER", ["MOVE_WAVE_CRASH", "MOVE_LAST_RESPECTS", "MOVE_AQUA_JET", "MOVE_CRUNCH"]),
    "SPECIES_NACLI": ("ITEM_ORAN_BERRY", ["MOVE_ROCK_TOMB", "MOVE_MUD_SHOT", "MOVE_RECOVER", "MOVE_HEADBUTT"]),
    "SPECIES_NACLSTACK": ("ITEM_HARD_STONE", ["MOVE_SALT_CURE", "MOVE_ROCK_SLIDE", "MOVE_RECOVER", "MOVE_PROTECT"]),
    "SPECIES_GARGANACL": ("ITEM_LEFTOVERS", ["MOVE_SALT_CURE", "MOVE_BODY_PRESS", "MOVE_RECOVER", "MOVE_PROTECT"]),
    "SPECIES_BUDEW": ("ITEM_ORAN_BERRY", ["MOVE_ABSORB", "MOVE_STUN_SPORE", "MOVE_GROWTH"]),
    "SPECIES_ROSELIA": ("ITEM_MIRACLE_SEED", ["MOVE_GIGA_DRAIN", "MOVE_TOXIC_SPIKES", "MOVE_STUN_SPORE", "MOVE_LEECH_SEED"]),
    "SPECIES_ROSERADE": ("ITEM_MIRACLE_SEED", ["MOVE_GIGA_DRAIN", "MOVE_SLUDGE_BOMB", "MOVE_TOXIC_SPIKES", "MOVE_SLEEP_POWDER"]),
    "SPECIES_SCYTHER": ("ITEM_SHARP_BEAK", ["MOVE_AERIAL_ACE", "MOVE_U_TURN", "MOVE_SWORDS_DANCE", "MOVE_QUICK_ATTACK"]),
    "SPECIES_SCIZOR": ("ITEM_METAL_COAT", ["MOVE_BULLET_PUNCH", "MOVE_X_SCISSOR", "MOVE_SWORDS_DANCE", "MOVE_U_TURN"]),
    "SPECIES_MURKROW": ("ITEM_BLACK_GLASSES", ["MOVE_FEINT_ATTACK", "MOVE_HAZE", "MOVE_TAUNT", "MOVE_WING_ATTACK"]),
    "SPECIES_HONCHKROW": ("ITEM_BLACK_GLASSES", ["MOVE_NIGHT_SLASH", "MOVE_AERIAL_ACE", "MOVE_SUCKER_PUNCH", "MOVE_TAUNT"]),
    "SPECIES_RALTS": ("ITEM_ORAN_BERRY", ["MOVE_CONFUSION", "MOVE_DISARMING_VOICE", "MOVE_GROWL"]),
    "SPECIES_KIRLIA": ("ITEM_TWISTED_SPOON", ["MOVE_PSYBEAM", "MOVE_DRAINING_KISS", "MOVE_CALM_MIND", "MOVE_THUNDER_WAVE"]),
    "SPECIES_GARDEVOIR": ("ITEM_TWISTED_SPOON", ["MOVE_PSYCHIC", "MOVE_MOONBLAST", "MOVE_CALM_MIND", "MOVE_WISH"]),
    "SPECIES_PAWMO": ("ITEM_MAGNET", ["MOVE_SPARK", "MOVE_ARM_THRUST", "MOVE_NUZZLE", "MOVE_QUICK_ATTACK"]),
    "SPECIES_CYCLIZAR": ("ITEM_SILK_SCARF", ["MOVE_DRAGON_CLAW", "MOVE_U_TURN", "MOVE_QUICK_ATTACK", "MOVE_TAUNT"]),
    "SPECIES_ROCKRUFF": ("ITEM_HARD_STONE", ["MOVE_ROCK_TOMB", "MOVE_BITE", "MOVE_HOWL", "MOVE_SAND_ATTACK"]),
    "SPECIES_LYCANROC": ("ITEM_HARD_STONE", ["MOVE_ROCK_SLIDE", "MOVE_ACCELEROCK", "MOVE_CRUNCH", "MOVE_SWORDS_DANCE"]),
    "SPECIES_DEERLING": ("ITEM_MIRACLE_SEED", ["MOVE_SEED_BOMB", "MOVE_HEADBUTT", "MOVE_LEECH_SEED", "MOVE_SAND_ATTACK"]),
    "SPECIES_SAWSBUCK": ("ITEM_MIRACLE_SEED", ["MOVE_HORN_LEECH", "MOVE_BODY_SLAM", "MOVE_LEECH_SEED", "MOVE_SWORDS_DANCE"]),
    "SPECIES_STARLY": ("ITEM_ORAN_BERRY", ["MOVE_WING_ATTACK", "MOVE_QUICK_ATTACK", "MOVE_GROWL"]),
    "SPECIES_STARAVIA": ("ITEM_SHARP_BEAK", ["MOVE_AERIAL_ACE", "MOVE_QUICK_ATTACK", "MOVE_ENDEAVOR", "MOVE_DOUBLE_TEAM"]),
    "SPECIES_STARAPTOR": ("ITEM_SHARP_BEAK", ["MOVE_BRAVE_BIRD", "MOVE_CLOSE_COMBAT", "MOVE_U_TURN", "MOVE_QUICK_ATTACK"]),
    "SPECIES_PIKACHU": ("ITEM_ORAN_BERRY", ["MOVE_SPARK", "MOVE_NUZZLE", "MOVE_QUICK_ATTACK", "MOVE_DOUBLE_TEAM"]),
    "SPECIES_RAICHU": ("ITEM_MAGNET", ["MOVE_THUNDERBOLT", "MOVE_NUZZLE", "MOVE_VOLT_SWITCH", "MOVE_ENCORE"]),
    "SPECIES_MIENFOO": ("ITEM_BLACK_BELT", ["MOVE_FORCE_PALM", "MOVE_FAKE_OUT", "MOVE_U_TURN", "MOVE_DETECT"]),
    "SPECIES_MIENSHAO": ("ITEM_BLACK_BELT", ["MOVE_DRAIN_PUNCH", "MOVE_FAKE_OUT", "MOVE_U_TURN", "MOVE_KNOCK_OFF"]),
    "SPECIES_CORPHISH": ("ITEM_MYSTIC_WATER", ["MOVE_AQUA_JET", "MOVE_KNOCK_OFF", "MOVE_LEER", "MOVE_PROTECT"]),
    "SPECIES_CRAWDAUNT": ("ITEM_MYSTIC_WATER", ["MOVE_CRABHAMMER", "MOVE_KNOCK_OFF", "MOVE_AQUA_JET", "MOVE_SWORDS_DANCE"]),
    "SPECIES_HOUNDOUR": ("ITEM_CHARCOAL", ["MOVE_BITE", "MOVE_INCINERATE", "MOVE_ROAR", "MOVE_SMOG"]),
    "SPECIES_HOUNDOOM": ("ITEM_CHARCOAL", ["MOVE_FLAMETHROWER", "MOVE_DARK_PULSE", "MOVE_WILL_O_WISP", "MOVE_NASTY_PLOT"]),
}


def rewrite_mon(block: str, species: str, item: str, moves):
    if not re.match(rf"^{re.escape(species)}(?:\s|$)", block):
        return block, False
    lines = block.splitlines()
    lines[0] = f"{species} @ {item}"
    lines = [ln for ln in lines if not ln.startswith("- ")]
    lines.extend(f"- {mv}" for mv in moves)
    return "\n".join(lines), True


def style_party(part: str, label: str):
    if "\n\n" not in part:
        return part, False
    meta, party = part.split("\n\n", 1)
    blocks = party.strip().split("\n\n")
    changed = False

    # Boss signature takes priority.
    if label in BOSS_SETS:
        species, item, moves = BOSS_SETS[label]
        for i, block in enumerate(blocks):
            blocks[i], did = rewrite_mon(block, species, item, moves)
            if did:
                changed = True
                break
    else:
        # Exactly one personality member per ordinary trainer is enough to create a plan.
        for i, block in enumerate(blocks):
            sm = re.match(r"^(SPECIES_[A-Z0-9_]+)(?:\s|$)", block)
            if not sm or sm.group(1) not in PERSONALITY_SETS:
                continue
            item, moves = PERSONALITY_SETS[sm.group(1)]
            blocks[i], did = rewrite_mon(block, sm.group(1), item, moves)
            changed |= did
            break

    if not changed:
        return part, False
    return meta + "\n\n" + "\n\n".join(blocks) + "\n\n", True


def main():
    text = PATH.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
    out = []
    themed = 0
    boss_count = 0
    for part in parts:
        m = re.match(r"^=== (TRAINER_[A-Z0-9_]+) ===$", part, flags=re.M)
        if not m:
            out.append(part)
            continue
        label = m.group(1)
        new, changed = style_party(part, label)
        if changed:
            themed += 1
            boss_count += label in BOSS_SETS
        out.append(new)
    PATH.write_text("".join(out))
    print(f"Strategic trainer pass: {themed} trainers themed, including {boss_count} major bosses")


if __name__ == "__main__":
    main()
