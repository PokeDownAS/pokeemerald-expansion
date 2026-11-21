"""Story encounters with short, themed teams and a deliberate opening for the player."""
import re
from pathlib import Path

TRAINERS = Path(__file__).resolve().parents[2] / "src/data/trainers.party"

# Each row is species, level, optional held item, then moves in party order.
TEAMS = {
    'IVAN': """
GOLDEEN 7 PECK WATER_SPORT TAIL_WHIP
BARBOACH 8 WATER_GUN MUD_SLAP""",
    'GINA_AND_MIA_1': """
LOTAD 8 ABSORB ASTONISH GROWL
PLUSLE 8 QUICK_ATTACK HELPING_HAND GROWL""",
    'ANTHONY': """
DODUO 15 PECK QUICK_ATTACK GROWL
FLAAFFY 16 THUNDER_SHOCK THUNDER_WAVE TACKLE""",
    'EDWARD': """
NATU 15 NIGHT_SHADE PECK REFLECT
SPOINK 16 PSYBEAM SPLASH PSYWAVE""",
    'DALE': """
TENTACOOL 14 ACID WATER_PULSE CONSTRICT
CARVANHA 15 BITE AQUA_JET FOCUS_ENERGY""",
    'LUNG': """
SPINARAK 19 TOXIC_THREAD BUG_BITE POISON_STING
GULPIN 20 VENOSHOCK YAWN POUND""",
    'COBY': """
TAILLOW 19 QUICK_ATTACK WING_ATTACK FOCUS_ENERGY
SKARMORY 20 METAL_CLAW PECK AGILITY""",
    'MADELINE_1': """
WINGULL 19 RAIN_DANCE WATER_GUN WING_ATTACK
LOMBRE 20 BUBBLE_BEAM ABSORB FAKE_OUT""",
    'BRENT': """
SURSKIT 26 BUBBLE_BEAM STRING_SHOT QUICK_ATTACK
HERACROSS 27 BRICK_BREAK AERIAL_ACE HORN_ATTACK""",
    'YASU': """
NINJASK 26 FURY_CUTTER AGILITY BATON_PASS
KECLEON 27 SHADOW_SNEAK FEINT_ATTACK SLASH""",
    'RACHEL': """
CASTFORM 27 RAIN_DANCE WEATHER_BALL HEADBUTT
PELIPPER 28 WATER_PULSE WING_ATTACK MIST""",
    'TORI_AND_TIA': """
MINUN 20 HELPING_HAND SPARK QUICK_ATTACK
PLUSLE 20 FAKE_TEARS SWIFT ELECTRO_BALL""",
    'ROXANNE_1': """
GEODUDE 13 ROCK_THROW DEFENSE_CURL TACKLE
ANORITH 14 FURY_CUTTER SCRATCH WATER_GUN
NOSEPASS 16 @ORAN_BERRY ROCK_TOMB TACKLE HARDEN""",
    'BRAWLY_1': """
MACHOP 17 KARATE_CHOP LEER FOCUS_ENERGY
MEDITITE 18 CONFUSION DETECT FORCE_PALM
MAKUHITA 20 @ORAN_BERRY BULK_UP ARM_THRUST KNOCK_OFF""",
    'WATTSON_1': """
VOLTORB 22 VOLT_SWITCH SONIC_BOOM CHARGE
MAGNETON 23 SHOCK_WAVE MAGNET_BOMB METAL_SOUND
MANECTRIC 25 @SITRUS_BERRY SPARK BITE QUICK_ATTACK HOWL""",
    'FLANNERY_1': """
SLUGMA 26 SUNNY_DAY INCINERATE ANCIENT_POWER
NUMEL 27 FLAME_BURST MAGNITUDE AMNESIA
TORKOAL 30 @SITRUS_BERRY OVERHEAT BODY_SLAM SMOG SUNNY_DAY""",
    'NORMAN_1': """
SPINDA 29 TEETER_DANCE DIZZY_PUNCH FEINT_ATTACK
VIGOROTH 30 ENCORE SLASH ROCK_SMASH
SLAKING 33 @SITRUS_BERRY FACADE FEINT_ATTACK YAWN""",
    'WINONA_1': """
PELIPPER 32 WATER_PULSE WING_ATTACK MIST
SKARMORY 33 STEEL_WING AERIAL_ACE SPIKES
ALTARIA 36 @SITRUS_BERRY DRAGON_DANCE DRAGON_BREATH AERIAL_ACE TAKE_DOWN""",
    'TATE_AND_LIZA_1': """
CLAYDOL 40 EARTHQUAKE PSYBEAM LIGHT_SCREEN
XATU 40 TAILWIND AIR_SLASH PSYCHIC
SOLROCK 41 ROCK_SLIDE ZEN_HEADBUTT SUNNY_DAY
LUNATONE 42 @SITRUS_BERRY PSYCHIC MOONBLAST CALM_MIND""",
    'JUAN_1': """
LUVDISC 41 RAIN_DANCE WATER_PULSE CHARM
WHISCASH 42 AQUA_TAIL MAGNITUDE AMNESIA
CRAWDAUNT 43 CRABHAMMER NIGHT_SLASH AQUA_JET
KINGDRA 45 @SITRUS_BERRY WATER_PULSE DRAGON_PULSE AGILITY""",
}

BIRDS = {
    'ROUTE_103': 'TAILLOW 4 PECK GROWL',
    'RUSTBORO': 'TAILLOW 13 WING_ATTACK QUICK_ATTACK FOCUS_ENERGY',
    'ROUTE_110': 'TAILLOW 19 WING_ATTACK QUICK_ATTACK FOCUS_ENERGY',
    'ROUTE_119': 'SWELLOW 29 WING_ATTACK QUICK_ATTACK U_TURN',
    'LILYCOVE': 'SWELLOW 33 AERIAL_ACE QUICK_ATTACK U_TURN ENDEAVOR',
}


def pokemon(row):
    name, level, *moves = row.split()
    item = ' @ ITEM_' + moves.pop(0)[1:] if moves[0].startswith('@') else ''
    assert 1 <= len(moves) <= 4
    return '\n'.join([f'SPECIES_{name}{item}', f'Level: {level}',
                      *(f'- MOVE_{move}' for move in moves)])


def main():
    text = TRAINERS.read_text()
    updated = set()

    def update(match):
        label, body = match.groups()
        rival = re.fullmatch(r'(?:MAY|BRENDAN)_(ROUTE_103|RUSTBORO|ROUTE_110|ROUTE_119|LILYCOVE)_(MUDKIP|TREECKO|TORCHIC)', label)
        if label not in TEAMS and not rival:
            return match[0]
        meta, *party = body.strip().split('\n\n')
        meta = re.sub(r'^Items:.*\n', '', meta, flags=re.M)
        if label in TEAMS:
            meta = re.sub(r"^AI:.*$", "AI: Check Bad Move / Try To Faint / Check Viability", meta, flags=re.M)
            party = [pokemon(row) for row in TEAMS[label].strip().splitlines()]
        else:
            stage = rival[1]
            # The story pass appends a signature Pokémon after the rival's starter.
            # Keep the starter selected by the story branch as the team's ace.
            starter = party[-2]
            supports = party[:-2]
            if stage in ('RUSTBORO','ROUTE_110','LILYCOVE'):
                supports = supports[1:]
            if stage == 'ROUTE_103':
                starter = re.sub(r'Level: \d+', 'Level: 5', starter)
            party = [pokemon(BIRDS[stage]), *supports, starter]
        updated.add(label)
        return f'=== TRAINER_{label} ===\n' + '\n\n'.join([meta,*party]) + '\n\n'

    result = re.sub(r'^=== TRAINER_(\w+) ===\n(.*?)(?=^=== |\Z)', update, text,
                    flags=re.M | re.S)
    assert set(TEAMS) <= updated and len(updated) == len(TEAMS) + 30
    TRAINERS.write_text(result)
    print(f'Updated {len(updated)} trainer party definitions')


if __name__ == '__main__':
    main()
