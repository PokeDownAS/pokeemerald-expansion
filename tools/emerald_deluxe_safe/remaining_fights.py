"""Tune the rest of Hoenn after the individually authored story fights."""
import json
import re
from pathlib import Path
from zlib import crc32

from signature_fights import TEAMS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src/data'
# A setter and a follow-up. Score both against the actual party's learnable moves.
PLANS = {
    'speed': ('STRING_SHOT ELECTROWEB ICY_WIND ROCK_TOMB THUNDER_WAVE BULLDOZE', 'ELECTRO_BALL HEADBUTT BITE ROCK_SLIDE STOMP AIR_SLASH'),
    'rain': ('RAIN_DANCE', 'WATER_PULSE BUBBLE_BEAM AQUA_TAIL WATERFALL WEATHER_BALL BRINE'),
    'sun': ('SUNNY_DAY', 'FLAME_WHEEL FIRE_FANG FLAME_BURST SOLAR_BEAM WEATHER_BALL FLAMETHROWER'),
    'poison': ('POISON_STING POISON_FANG TOXIC_SPIKES POISON_POWDER', 'VENOSHOCK HEX'),
    'status': ('WILL_O_WISP STUN_SPORE THUNDER_WAVE GLARE', 'HEX SMELLING_SALTS'),
    'defense': ('REFLECT LIGHT_SCREEN AURORA_VEIL', 'WORK_UP BULK_UP CALM_MIND GROWTH CHARGE_BEAM'),
    'pressure': ('LEER TAIL_WHIP SCREECH', 'QUICK_ATTACK MACH_PUNCH AQUA_JET FORCE_PALM SLASH WING_ATTACK'),
    'special': ('FAKE_TEARS METAL_SOUND ACID_SPRAY', 'CONFUSION PSYBEAM STRUGGLE_BUG DISARMING_VOICE WATER_PULSE'),
    'pivot': ('U_TURN VOLT_SWITCH FLIP_TURN PARTING_SHOT', 'FAKE_OUT QUICK_ATTACK AQUA_JET MACH_PUNCH'),
    'focus': ('FOCUS_ENERGY', 'KARATE_CHOP NIGHT_SLASH LEAF_BLADE AIR_CUTTER PSYCHO_CUT CROSS_POISON'),
    'doubles': ('HELPING_HAND TAILWIND LIGHT_SCREEN REFLECT', 'SWIFT RAZOR_LEAF ICY_WIND BUBBLE ROCK_SLIDE DISARMING_VOICE'),
}
# Alternatives for the repetitive extra Pokémon appended by earlier build stages.
FAMILIES = {
    'coast': 'WINGULL/PELIPPER CHINCHOU/LANTURN FINNEON/LUMINEON TENTACOOL/TENTACRUEL',
    'stream': 'GOLDEEN/SEAKING CORPHISH/CRAWDAUNT BARBOACH/WHISCASH BUIZEL/FLOATZEL',
    'rock': 'GEODUDE/GRAVELER DRILBUR/EXCADRILL ARON/LAIRON DWEBBLE/CRUSTLE',
    'sport': 'TYROGUE/HITMONTOP MAKUHITA/HARIYAMA MEDITITE/MEDICHAM DODUO/DODRIO',
    'forest': 'SEWADDLE/LEAVANNY JOLTIK/GALVANTULA SURSKIT/MASQUERAIN VENIPEDE/SCOLIPEDE',
    'field': 'HOPPIP/JUMPLUFF DEERLING/SAWSBUCK SKIDDO/GOGOAT ODDISH/GLOOM',
    'shadow': 'DUSKULL/DUSCLOPS SHUPPET/BANETTE MISDREAVUS/MISMAGIUS LITWICK/LAMPENT',
    'mind': 'NATU/XATU SPOINK/GRUMPIG ESPURR/MEOWSTIC_M RALTS/KIRLIA',
    'fire': 'NUMEL/CAMERUPT SLUGMA/MAGCARGO GROWLITHE/ARCANINE HOUNDOUR/HOUNDOOM',
    'agile': 'NINCADA/NINJASK CROAGUNK/TOXICROAK SKORUPI/DRAPION ZUBAT/GOLBAT',
    'sky': 'TAILLOW/SWELLOW SWABLU/ALTARIA STARLY/STARAVIA FLETCHLING/FLETCHINDER',
    'sound': 'WHISMUR/LOUDRED ELECTRIKE/MANECTRIC TOXEL/TOXTRICITY_AMPED VOLTORB/ELECTRODE',
    'domestic': 'SKITTY/DELCATTY LILLIPUP/HERDIER MEOWTH/PERSIAN MINCCINO/CINCCINO',
}
GROUPS = {
    'coast': 'Swimmer M|Swimmer F|Sailor|Sis And Bro|Tuber M|Tuber F|Parasol Lady',
    'stream': 'Fisherman|Team Aqua', 'rock': 'Hiker|Ruin Maniac',
    'sport': 'Battle Girl|Black Belt|Triathlete|Expert', 'forest': 'Bug Maniac|Bug Catcher',
    'field': 'Aroma Lady|Pkmn Ranger|Camper|Picnicker',
    'shadow': 'Hex Maniac', 'mind': 'Psychic|School Kid',
    'fire': 'Kindler|Team Magma', 'agile': 'Ninja Boy', 'sky': 'Bird Keeper',
    'sound': 'Guitarist|Interviewer', 'domestic': 'Lady|Gentleman|Youngster|Lass|Pokefan|Rich Boy|Beauty|Twins',
}
MAJORS = {'Leader','Rival','Elite Four','Champion','Aqua Admin','Magma Admin','Aqua Leader','Magma Leader'}
AVOID = set('DOUBLE_TEAM MINIMIZE FISSURE SHEER_COLD HORN_DRILL GUILLOTINE EXPLOSION SELF_DESTRUCT SWAGGER FLASH SAND_ATTACK'.split())
SPECIAL = {'SIDNEY':'focus','PHOEBE':'status','GLACIA':'speed','DRAKE':'pivot','WALLACE':'rain','STEVEN':'defense'}


REMATCH_PARTNERS = {'ROXANNE':'ARMALDO','BRAWLY':'HITMONTOP','WATTSON':'MANECTRIC',
                    'FLANNERY':'NINETALES','NORMAN':'ZANGOOSE','WINONA':'SWELLOW',
                    'TATE_AND_LIZA':'XATU','JUAN':'LUDICOLO'}
# Party order follows boss_balance.BOSS_TEAMS.
LEAGUE = {
    'SIDNEY': ['SNARL CRUNCH ROAR FIRE_FANG','FAKE_OUT LEAF_BLADE FEINT_ATTACK',
               'CRABHAMMER AQUA_JET KNOCK_OFF','BULLDOZE CRUNCH ROCK_SLIDE',
               'FOCUS_ENERGY NIGHT_SLASH PSYCHO_CUT','NASTY_PLOT DARK_PULSE FLAMETHROWER'],
    'PHOEBE': ['WILL_O_WISP SHADOW_PUNCH NIGHT_SHADE','SHADOW_CLAW KNOCK_OFF SHADOW_SNEAK',
               'HEX MAGICAL_LEAF POWER_GEM','PLAY_ROUGH SHADOW_SNEAK HONE_CLAWS',
               'SHADOW_PUNCH ICE_PUNCH DISABLE','HEX FLAME_BURST WILL_O_WISP'],
    'GLACIA': ['ICY_WIND SHADOW_BALL LIGHT_SCREEN','SURF ICE_BEAM BODY_SLAM',
               'QUIVER_DANCE BUG_BUZZ AURORA_BEAM','ICE_SHARD EARTHQUAKE ROCK_TOMB',
               'CRUNCH ICE_BEAM SPIKES','ICE_PUNCH NIGHT_SLASH QUICK_ATTACK'],
    'DRAKE': ['U_TURN DRAGON_CLAW EARTH_POWER','SLUDGE_BOMB DRAGON_PULSE WATER_PULSE',
              'AGILITY SURF DRAGON_BREATH','TAILWIND DRAGON_CLAW AERIAL_ACE',
              'DRAGON_CLAW BRICK_BREAK DRAGON_TAIL','FLAMETHROWER DRAGON_CLAW FLY'],
    'WALLACE': ['RAIN_DANCE WATER_PULSE ACID_SPRAY','GIGA_DRAIN SURF FAKE_OUT',
                'MOONBLAST SPARKLING_ARIA ENCORE','WATERFALL CRUNCH DRAGON_DANCE',
                'RAIN_DANCE DRAGON_PULSE SURF','SURF ICE_BEAM RECOVER'],
}


def key(name):
    return re.sub('[^A-Z0-9]', '', name.upper().removeprefix('SPECIES_'))


class Moves:
    def __init__(self):
        self.legal = {key(k): {m[5:] for m in v} for k,v in json.loads((DATA/'pokemon/all_learnables.json').read_text()).items()}
        self.info = {}
        for name, body in re.findall(r'\[MOVE_(\w+)\]\s*=\s*\{(.*?)\n    \},', (DATA/'moves_info.h').read_text(), re.S):
            power = re.search(r'\.power\s*=\s*(?:[^,?]+\?\s*)?(\d+)',body)
            typ = re.search(r'\.type\s*=\s*TYPE_(\w+)',body)
            category = re.search(r'\.category\s*=\s*DAMAGE_CATEGORY_(\w+)',body)
            if typ and category:
                self.info[name] = (int(power[1]) if power else 0,typ[1],category[1])
        self.levels = {}
        text = (DATA/'pokemon/level_up_learnsets/gen_9.h').read_text()
        for name,body in re.findall(r's(\w+)LevelUpLearnset\[\] = \{([^}]+)',text):
            self.levels[key(name)] = [(int(n),m) for n,m in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+), MOVE_(\w+)\)',body)]
        self.types = {}
        for path in (DATA/'pokemon/species_info').glob('gen_*_families.h'):
            blocks = re.split(r'\[SPECIES_(\w+)\]\s*=',path.read_text())
            for n,b in zip(blocks[1::2],blocks[2::2]):
                m = re.search(r'\.types\s*=\s*MON_TYPES\(([^)]+)',b)
                if m:
                    self.types[key(n)] = set(re.findall(r'TYPE_(\w+)',m[1]))

    def attacks(self, name, level, known):
        natural = [m for n,m in self.levels.get(name,[]) if n <= level]
        cap = 50 if level < 12 else 65 if level < 22 else 80 if level < 33 else 100
        options = set(known + natural) | self.legal.get(name,set())
        options -= AVOID | {'HIDDEN_POWER','TERA_BLAST','FACADE','ROUND','SNORE','DREAM_EATER','BELCH','LAST_RESORT','FAKE_OUT','FLING','SNORE','FUTURE_SIGHT','FINAL_GAMBIT','SYNCHRONOISE','STEEL_ROLLER','BURN_UP','POLTERGEIST','FOCUS_PUNCH','ENDEAVOR','COUNTER','MIRROR_COAT','BIDE','SUCKER_PUNCH','SPIT_UP','NATURAL_GIFT','UPPER_HAND'}
        viable = [m for m in options if m in self.info and 10 <= self.info[m][0] <= cap and self.info[m][2]!='STATUS']
        def score(m):
            p,t,_ = self.info[m]
            return (22*(t in self.types.get(name,set())) + 18*(m in natural) + 9*(m in known) + p/3, m)
        return sorted(viable,key=score,reverse=True)

    def choose(self,name,level,known,preferred,seed):
        legal = self.legal.get(name,set()) | set(known) | {m for n,m in self.levels.get(name,[]) if n<=level}
        attacks = self.attacks(name,level,known)
        options = [m for m in preferred.split() if m in legal and m in self.info and (level>=22 or self.info[m][0]<=65)]
        if name in ('WOBBUFFET','WYNAUT'):
            return ['COUNTER','MIRROR_COAT','SAFEGUARD']
        moves = attacks[:1]
        if options:
            moves.append(options[seed%len(options)])
        natural = [m for n,m in self.levels.get(name,[]) if n<=level]
        utility = [m for m in reversed(natural) if self.info.get(m,(0,'',''))[2]=='STATUS']
        for m in known + utility + attacks:
            redundant = any(self.info[m][1:] == self.info[other][1:] for other in moves) if m in self.info and self.info[m][2]!='STATUS' else False
            if m in self.info and m not in AVOID and m not in moves and not redundant and (m in attacks or self.info[m][2]=='STATUS'):
                moves.append(m)
            if len(set(moves))>= (3 if level<24 else 4):
                break
        return list(dict.fromkeys(moves)) or known


def run():
    dex = Moves()
    path = DATA/'trainers.party'
    groups = {c:k for k,classes in GROUPS.items() for c in classes.split('|')}
    updated = []
    def transform(match):
        label,body = match.groups()
        if label in TEAMS or re.fullmatch(r'(MAY|BRENDAN)_(ROUTE_103|RUSTBORO|ROUTE_110|ROUTE_119|LILYCOVE)_(MUDKIP|TREECKO|TORCHIC)',label):
            return match[0]
        meta,*party = body.strip().split('\n\n')
        if not party:
            return match[0]
        cls = re.search(r'^Class: (.*)',meta,re.M)[1]
        seed = crc32(re.sub(r'_\d+$','',label).encode())
        doubles = 'Double Battle: Yes' in meta
        species = [p.splitlines()[0].split(' @ ')[0] for p in party]
        levels = [int(re.search(r'Level: (\d+)',p)[1]) for p in party]
        # Keep native story partners, leaders' aces, and original rematch families.
        group = groups.get(cls)
        if group and len(party)>1 and species[-1].startswith('SPECIES_'):
            choices = FAMILIES[group].split()
            for offset in range(len(choices)):
                candidate = choices[(seed+offset)%len(choices)].split('/')[levels[-1]>=30]
                if key(candidate) not in {key(n) for n in species[:-1]}:
                    species[-1] = 'SPECIES_'+candidate
                    break
        if cls == 'Leader':
            # Earlier general-purpose upgrades append a Flygon to many rematches.
            gym = re.sub(r'_\d+$','',label)
            partner = REMATCH_PARTNERS.get(gym)
            if partner and key(species[-1])=='FLYGON' and key(partner) not in {key(n) for n in species[:-1]}:
                species[-1]='SPECIES_'+partner
        names = [key(s) for s in species]
        def synergy(plan):
            lead,finish = PLANS[plan]
            hits = [bool(dex.legal.get(n,set()) & set((lead if i==0 else finish).split())) for i,n in enumerate(names)]
            return 3*hits[0] + sum(hits[1:]) + (2 if doubles and plan=='doubles' else 0)
        plans = list(PLANS)
        if not doubles: plans.remove('doubles')
        plans = plans[seed%len(plans):]+plans[:seed%len(plans)]
        plan = SPECIAL.get(label) or max(plans,key=synergy)
        if cls in MAJORS:
            meta = re.sub(r'^Items:.*\n','',meta,flags=re.M)
        new = []
        for i,(p,name,species_name,level) in enumerate(zip(party,names,species,levels)):
            lines=p.splitlines()
            original=lines[0].split(' @ ')[0]
            same=key(original)==name
            known=[m.removeprefix('MOVE_').upper().replace(' ','_').replace('-','_') for m in re.findall(r'^- (.+)$',p,re.M)] if same else []
            moves=dex.choose(name,level,known,PLANS[plan][i!=0],seed+i)
            if label in LEAGUE:
                moves=LEAGUE[label][i].split()
            header=species_name
            if cls in MAJORS and i==len(party)-1 and level>=15:
                header+=' @ ITEM_'+('ORAN_BERRY' if level<22 else 'SITRUS_BERRY')
            other=[line for line in lines[1:] if not line.startswith('- ')]
            if not same:
                other=[line for line in other if not line.startswith('Ability:')]
            new.append('\n'.join([header,*other,*('- MOVE_'+m for m in moves)]))
        updated.append(label)
        return '=== TRAINER_'+label+' ===\n'+'\n\n'.join([meta,*new])+'\n\n'
    result=re.sub(r'^=== TRAINER_(\w+) ===\n(.*?)(?=^=== |\Z)',transform,path.read_text(),flags=re.M|re.S)
    path.write_text(result)
    print('Reworked remaining party definitions:',len(updated))
    facilities(dex)


def facilities(dex):
    # Fixed facilities get modern, species-appropriate attacks in place of
    # accuracy/evasion and instant-KO moves. Keep rental item and species clauses.
    for filename in ('battle_frontier/battle_frontier_mons.h','battle_frontier/battle_tent.h','battle_frontier/trainer_hill.h','../frontier_util.c'):
        path=DATA/filename
        def tune(match):
            prefix,name,inside=match.groups()
            moves=re.findall(r'MOVE_(\w+)',inside)
            attacks=dex.attacks(key(name),50,moves)
            if not attacks:
                return match[0]
            damaging=any(dex.info.get(m,(0,'',''))[0]>=20 for m in moves if m not in AVOID)
            for i,m in enumerate(moves):
                if m in AVOID or (not damaging and i==0):
                    replacement=next((a for a in attacks if a not in moves),None)
                    if replacement:
                        moves[i]=replacement
                        damaging=True
            return prefix+'{'+', '.join('MOVE_'+m for m in moves)+'}'
        txt=path.read_text()
        result=re.sub(r'(\.species\s*=\s*SPECIES_(\w+),[^;]*?\.moves\s*=\s*)\{([^{}]*?)\}',tune,txt)
        if filename.endswith('frontier_util.c'):
            # Each Silver / Gold Brain keeps its party and receives a distinct lead.
            leads = iter([
                'PSYCHIC DISABLE REFLECT FIRE_PUNCH', 'THUNDERBOLT REFLECT ROAR CALM_MIND',
                'MUDDY_WATER EARTHQUAKE ICE_PUNCH COUNTER', 'WATERFALL EARTHQUAKE YAWN MIRROR_COAT',
                'CROSS_POISON U_TURN CONFUSE_RAY FLY', 'FLARE_BLITZ EXTREME_SPEED ROAR PROTECT',
                'MEGAHORN ROCK_TOMB ENDURE REVERSAL', 'PAYBACK CHARM MOONLIGHT QUICK_ATTACK',
                'GLARE POISON_FANG CRUNCH GIGA_DRAIN', 'GLARE VENOSHOCK POISON_JAB CRUNCH',
                'ROCK_TOMB SUPERPOWER EARTHQUAKE CURSE', 'ICE_BEAM TAILWIND AERIAL_ACE REFLECT',
            ])
            pattern = r'(// (?:Silver|Gold) Symbol\.(?:(?!\.moves).)*?\.moves = )\{[^}]+\}'
            def lead(match):
                return match[1]+'{'+', '.join('MOVE_'+m for m in next(leads).split())+'}'
            result, count = re.subn(pattern,lead,result,flags=re.S)
            assert count==12
        path.write_text(result)


if __name__=='__main__':
    run()
