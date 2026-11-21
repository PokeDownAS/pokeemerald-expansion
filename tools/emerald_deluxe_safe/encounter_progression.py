"""Build the playable Hoenn encounter tables from the enabled species families."""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from zlib import crc32

ROOT = Path(__file__).resolve().parents[2]
WILD = ROOT / "src/data/wild_encounters.json"
ROUTES = dict(enumerate([
    3, 4, 5, 7, 26, 12, 26, 27, 13, 14, 22, 19, 21, 22, 28, 9, 16,
    28, 29, 31, 32, 32, 33, 35, 36, 38, 38, 39, 40, 40, 41, 42, 42, 42,
], 101))
AREAS = [
    ('PETALBURG_WOODS', 7), ('RUSTURF', 9), ('GRANITE', 12), ('DEWFORD', 12),
    ('SLATEPORT', 14), ('PETALBURG_CITY', 7), ('MIRAGE_TOWER', 22),
    ('FIERY_PATH', 19), ('JAGGED', 23), ('NEW_MAUVILLE', 30), ('ABANDONED', 29),
    ('MT_PYRE', 32), ('LILYCOVE', 33), ('MOSSDEEP', 36), ('SHOAL', 36),
    ('MAGMA_HIDEOUT', 35), ('UNDERWATER', 38), ('SEAFLOOR', 40), ('ORIGIN', 42),
    ('PACIFIDLOG', 41), ('SOOTOPOLIS', 42), ('SKY_PILLAR', 44),
    ('EVER_GRANDE', 44), ('VICTORY_ROAD', 46), ('STEVENS_CAVE', 58),
    ('METEOR_FALLS_1F_1R', 22), ('METEOR_FALLS', 44), ('SAFARI_ZONE_NORTHEAST', 52),
    ('SAFARI_ZONE_SOUTHEAST', 52), ('SAFARI', 32), ('ARTISAN', 55),
    ('DESERT_UNDERPASS', 54), ('ALTERING', 57),
]
THEMES = [
    ('FIERY MAGMA JAGGED ROUTE112 ROUTE113', 'FIRE GROUND ROCK STEEL'),
    ('MIRAGE DESERT ROUTE111', 'GROUND ROCK BUG'),
    ('MT_PYRE', 'GHOST DARK PSYCHIC FAIRY'), ('SHOAL', 'ICE WATER ROCK'),
    ('NEW_MAUVILLE', 'ELECTRIC STEEL POISON'), ('SKY_PILLAR', 'DRAGON FLYING PSYCHIC'),
    ('PETALBURG_WOODS ROUTE119 ROUTE120', 'BUG GRASS FLYING'),
    ('METEOR GRANITE RUSTURF VICTORY', 'ROCK STEEL FIGHTING DRAGON GROUND'),
    ('SEAFLOOR ORIGIN', 'GROUND ROCK WATER DARK'), ('SAFARI', 'NORMAL GRASS FIGHTING FLYING'),
]
# These tables can disappear, require a rare island, or have no reliable floor encounters.
OPTIONAL = ('UNUSED', 'MIRAGE_TOWER', 'CAVE_OF_ORIGIN', 'ROUTE130', 'GRANITE_CAVE_STEVENS_ROOM')
ANCHORS = {
    'ROUTE103': 'WINGULL TAILLOW PATRAT', 'ROUTE104': 'PIDGEY BUNNELBY SEEDOT',
    'ROUTE110': 'ELECTRIKE PLUSLE MINUN', 'ROUTE111': 'SANDSHREW TRAPINCH CACNEA BALTOY',
    'ROUTE112': 'NUMEL MACHOP', 'ROUTE114': 'SWABLU ZANGOOSE SEVIPER',
    'ROUTE116': 'NINCADA SKITTY', 'ROUTE117': 'ROSELIA VOLBEAT ILLUMISE',
    'ROUTE119': 'TROPIUS KECLEON', 'ROUTE120': 'ABSOL LINOONE',
    'ROUTE121': 'GLOOM KECLEON', 'SKY_PILLAR_1F': 'ALTARIA CLAYDOL',
    'VICTORY_ROAD_1F': 'LAIRON HARIYAMA', 'SEAFLOOR_CAVERN_ROOM1': 'GOLBAT GRAVELER',
    'ROUTE101': 'ZIGZAGOON POOCHYENA STARLY SENTRET SHROOMISH MAREEP',
    'ROUTE102': 'LOTAD SURSKIT WOOPER MARILL BUDEW PSYDUCK RALTS',
    'PETALBURG_WOODS': 'WURMPLE SHROOMISH SLAKOTH', 'RUSTURF_TUNNEL': 'WHISMUR',
    'GRANITE_CAVE_1F': 'MAKUHITA ZUBAT', 'GRANITE_CAVE_B2F': 'ARON SABLEYE',
    'FIERY_PATH': 'NUMEL SLUGMA', 'ROUTE113': 'SPINDA SKARMORY',
    'NEW_MAUVILLE_INSIDE': 'MAGNEMITE VOLTORB', 'MT_PYRE_1F': 'SHUPPET DUSKULL',
    'SHOAL_CAVE_LOW_TIDE_ICE_ROOM': 'SNORUNT SPHEAL',
}
COASTAL = set('DRATINI DRAGONAIR DRAGONITE LUGIA LATIAS LATIOS SURSKIT MASQUERAIN STUNFISK PINCURCHIN DHELMISE CRESSELIA INKAY MALAMAR EISCUE DRAGALGE KILOWATTREL WATTREL CRAMORANT DRAGAPULT DRAKLOAK DREEPY BEARTIC CUBCHOO DRAGALGE TYNAMO EELEKTRIK EELEKTROSS'.split())


def species_catalog():
    # Expand shared form macros before reading Pokédex numbers (e.g. Flabébé and Arceus).
    headers = ['config/species_enabled.h'] + [
        f'data/pokemon/species_info/gen_{n}_families.h' for n in range(1, 10)]
    source = '#define TRUE 1\n' + '\n'.join(f'#include "{h}"' for h in headers)
    raw = subprocess.check_output(['cpp', '-P', '-Iinclude', '-Isrc', '-'], cwd=ROOT,
                                  input=source, text=True)
    blocks = re.split(r'\[(SPECIES_\w+)\]\s*=\s*\{', raw)
    species = {}
    for symbol, block in zip(blocks[1::2], blocks[2::2]):
        dex = re.search(r'\.natDexNum\s*=\s*NATIONAL_DEX_(\w+)', block)
        if not dex or dex[1] in species:
            continue
        name = dex[1]
        types = set(re.findall(r'TYPE_(\w+)', re.search(r'\.types\s*=\s*(?:MON_TYPES\(|\{)([^})]*)', block)[1]))
        stats = [int(re.findall(r'\d+', value.split('?')[-1].split(':')[0])[0])
                 for value in re.findall(r'\.base(?:HP|Attack|Defense|Speed|SpAttack|SpDefense)\s*=\s*([^,]+)', block)]
        special = bool(re.search(r'\.is(?:Mythical|SubLegendary|RestrictedLegendary|UltraBeast|Paradox)\s*=\s*1', block))
        bst = sum(stats)
        level = 53 if special else max(4, min(46, (bst - 260) // 6))
        species[name] = (symbol, types, level, special)
    expected = set(re.findall(r'^\s*NATIONAL_DEX_(\w+),', (ROOT/'include/constants/pokedex.h').read_text(), re.M)) - {'NONE'}
    assert set(species) == expected and len(expected) == 1025, expected - species.keys()
    return species


def location(area, field, index):
    route = re.fullmatch(r'ROUTE(\d+)', area)
    level = ROUTES[int(route[1])] if route else next(v for key, v in AREAS if key in area)
    if field == 'fishing_mons':
        level = max(level, 36 if index >= 5 else 26 if index >= 2 else 10)
    if field == 'water_mons':
        level = max(level, 26)
    if field == 'rock_smash_mons':
        level = max(level, 18)
    if any(x in area for x in ('B2F', 'ICE_ROOM', 'SUMMIT', '5F', '6F')):
        level += 2
    return level


def main():
    species = species_catalog()
    data = json.loads(WILD.read_text())
    group = next(g for g in data['wild_encounter_groups'] if g['label'] == 'gWildMonHeaders')
    slots = []
    assigned = {}
    counts = Counter()
    local = set()
    for entry in group['encounters']:
        label = entry['base_label']
        if 'FireRed' in label or 'LeafGreen' in label:
            continue
        area = entry['map'].removeprefix('MAP_')
        theme = next((set(types.split()) for keys, types in THEMES
                      if any(k in area for k in keys.split())), {'NORMAL','FLYING','GRASS','BUG','FAIRY'})
        for field in group['fields']:
            method = field['type']
            if method not in entry:
                continue
            for i, mon in enumerate(entry[method]['mons']):
                level = location(area, method, i)
                rate = field['encounter_rates'][i]
                safe = not any(k in area for k in OPTIONAL)
                # Underwater grass uses the surfing encounter table. Don't rely on
                # gated ship interiors or ocean fishing while submerged for coverage.
                if 'ABANDONED' in area or (area in {'SHOAL_CAVE_LOW_TIDE_ENTRANCE_ROOM','SHOAL_CAVE_LOW_TIDE_INNER_ROOM'} and method != 'land_mons') or ('UNDERWATER' in area and method != 'water_mons'):
                    safe = False
                slots.append((label, method, level, rate, theme, mon, safe))
                anchors = ANCHORS.get(area, '').split() if method == 'land_mons' else []
                if i < len(anchors):
                    assigned[len(slots)-1] = anchors[i]
                    counts[anchors[i]] += 1
                    local.add((label, method, anchors[i]))

    def score(name, j):
        _, types, target, special = species[name]
        label, method, level, rate, theme, _, _ = slots[j]
        aquatic = 'WATER' in types or name in COASTAL
        if method in ('fishing_mons','water_mons') and not aquatic:
            return -10000
        if special and (level < 43 or (level < 50 and rate > 5)):
            return -10000
        if level < 12 and target > 22:
            return -10000
        habitat = 0
        if method == 'land_mons':
            habitat = 12 if types & theme else 0
        elif method == 'rock_smash_mons':
            habitat = 18 if types & {'GROUND','ROCK','STEEL','BUG','FIGHTING'} else -55
        elif aquatic:
            habitat = 35
        rare = min(rate, 20) if special else 0
        noise = crc32(f'{name}/{j}'.encode()) % 500 / 100
        return habitat - abs(target-level)*1.5 - rare + noise

    available = {j for j,s in enumerate(slots) if s[-1] and j not in assigned}
    # Place constrained terrestrial species before the many fishable species.
    order = sorted(species, key=lambda n: (not species[n][3],
                   'WATER' in species[n][1] or n in COASTAL, -species[n][2], n))
    for name in order:
        if counts[name]:
            continue
        j = max(available, key=lambda k: score(name,k))
        assert score(name,j) > -10000, name
        assigned[j] = name
        counts[name] += 1
        local.add((*slots[j][:2],name))
        available.remove(j)
    for j,(label,method,level,rate,theme,mon,safe) in enumerate(slots):
        if j not in assigned:
            candidates = (n for n in species if (label,method,n) not in local)
            name = max(candidates, key=lambda n: score(n,j) - counts[n]*4)
            assigned[j] = name
            counts[name] += 1
            local.add((label,method,name))
        name = assigned[j]
        mon.update(species=species[name][0], min_level=level, max_level=level+(2 if level<20 else 4))
    assert {assigned[j] for j,s in enumerate(slots) if s[-1]} == set(species)
    WILD.write_text(json.dumps(data,indent=2)+'\n')
    print(f'{len(species)} National Dex species across {len(slots)} Hoenn encounter slots')


if __name__ == '__main__':
    main()
