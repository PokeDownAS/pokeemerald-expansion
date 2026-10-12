#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The expansion already supplies Gen 1-9 species, modern move categories,
# abilities, items, and mechanics. This script turns the base into Emerald Deluxe.

CLASS_ADDS = {
    "Bug": "SPECIES_LOKIX", "Bird": "SPECIES_KILOWATTREL",
    "Psychic": "SPECIES_ESPEON", "Hex": "SPECIES_MISMAGIUS",
    "Ninja": "SPECIES_GRENINJA", "Black Belt": "SPECIES_HAWLUCHA",
    "Battle Girl": "SPECIES_LUCARIO", "Swimmer": "SPECIES_FLOATZEL",
    "Fisherman": "SPECIES_BASCULEGION", "Hiker": "SPECIES_GARGANACL",
    "Aroma": "SPECIES_ROSERADE", "Pokefan": "SPECIES_SYLVEON",
    "Collector": "SPECIES_SCIZOR", "Gentleman": "SPECIES_HONCHKROW",
    "Lady": "SPECIES_GARDEVOIR", "Triathlete": "SPECIES_CYCLIZAR",
    "Camper": "SPECIES_LYCANROC", "Picnicker": "SPECIES_DEERLING",
    "Youngster": "SPECIES_STARAVIA", "School": "SPECIES_RAICHU",
    "Cooltrainer": "SPECIES_LUCARIO", "Expert": "SPECIES_MIENSHAO",
    "Team Aqua": "SPECIES_CRAWDAUNT", "Team Magma": "SPECIES_HOUNDOOM",
}

BOSS_ADDS = {
    "TRAINER_ROXANNE_1": "SPECIES_ROCKRUFF",
    "TRAINER_BRAWLY_1": "SPECIES_CROAGUNK",
    "TRAINER_WATTSON_1": "SPECIES_BELLIBOLT",
    "TRAINER_FLANNERY_1": "SPECIES_HOUNDOOM",
    "TRAINER_NORMAN_1": "SPECIES_BEWEAR",
    "TRAINER_WINONA_1": "SPECIES_GLISCOR",
    "TRAINER_TATE_AND_LIZA_1": "SPECIES_METAGROSS",
    "TRAINER_JUAN_1": "SPECIES_LAPRAS",
    "TRAINER_SIDNEY": "SPECIES_KINGAMBIT",
    "TRAINER_PHOEBE": "SPECIES_ANNIHILAPE",
    "TRAINER_GLACIA": "SPECIES_BAXCALIBUR",
    "TRAINER_DRAKE": "SPECIES_DRAGAPULT",
    "TRAINER_WALLACE": "SPECIES_PALAFIN",
}


def collect_families():
    ordinary, rare, seen = [], [], set()
    d = ROOT / "src/data/pokemon/species_info"
    for gen in range(1, 10):
        p = d / f"gen_{gen}_families.h"
        if not p.exists():
            continue
        s = p.read_text()
        starts = list(re.finditer(r"#if P_FAMILY_[A-Z0-9_]+", s))
        for i, m in enumerate(starts):
            end = starts[i+1].start() if i+1 < len(starts) else len(s)
            block = s[m.start():end]
            sm = re.search(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=", block)
            if not sm or sm.group(1) in seen:
                continue
            species = sm.group(1); seen.add(species)
            cm = re.search(r"\.catchRate\s*=\s*(\d+)", block)
            rate = int(cm.group(1)) if cm else 45
            (rare if rate <= 10 else ordinary).append(species)
    return ordinary, rare


def encounters():
    p = ROOT / "src/data/wild_encounters.json"
    data = json.loads(p.read_text())
    group = next(x for x in data["wild_encounter_groups"] if x.get("label") == "gWildMonHeaders")
    ordinary, rare = collect_families()
    slots, late = [], []
    encs = group["encounters"]; late_at = int(len(encs) * .68)
    for ei, enc in enumerate(encs):
        for field, idxs in (("land_mons",(8,9,10,11)),("water_mons",(3,4)),("rock_smash_mons",(3,4)),("fishing_mons",(7,8,9))):
            table = enc.get(field)
            if not table: continue
            mons = table.get("mons", [])
            for idx in idxs:
                if idx < len(mons):
                    slots.append((mons, idx))
                    if ei >= late_at: late.append((mons, idx))
    for i, sp in enumerate(ordinary):
        mons, idx = slots[i % len(slots)]; mons[idx]["species"] = sp
    for i in range(len(ordinary), len(slots)):
        mons, idx = slots[i]; mons[idx]["species"] = ordinary[i % len(ordinary)]
    for i, sp in enumerate(rare):
        if not late: break
        mons, idx = late[-1-(i % len(late))]
        mons[idx]["species"] = sp
        mons[idx]["min_level"] = max(45, mons[idx].get("min_level",45))
        mons[idx]["max_level"] = max(mons[idx]["min_level"], mons[idx].get("max_level",50))
    p.write_text(json.dumps(data, indent=2)+"\n")
    print("families distributed", len(ordinary), len(rare))


def evolutions():
    d = ROOT / "src/data/pokemon/species_info"
    for p in d.glob("*.h"):
        s = p.read_text()
        # Make trade evolutions solo-friendly.
        s = re.sub(r"EVOLUTION\(\{EVO_TRADE,\s*[^,{}]+,\s*(SPECIES_[A-Z0-9_]+)(?:,\s*[^{}]*)?\}\)",
                   lambda m: f"EVOLUTION({{EVO_LEVEL, 36, {m.group(1)}}})", s)
        def lower(m):
            n=int(m.group(1))
            if n>=50: n=max(42,n-8)
            elif n>=40: n-=4
            elif n>=31: n-=2
            return f"EVO_LEVEL, {n}"
        s = re.sub(r"EVO_LEVEL,\s*(\d+)", lower, s)
        p.write_text(s)


def trainer_add(meta, label):
    if label in BOSS_ADDS: return BOSS_ADDS[label]
    cm = re.search(r"^Class:\s*(.+)$", meta, re.M)
    cls = cm.group(1) if cm else ""
    for key, sp in CLASS_ADDS.items():
        if key.lower() in cls.lower(): return sp
    return "SPECIES_EEVEE"


def trainers():
    p = ROOT / "src/data/trainers.party"; s = p.read_text()
    parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", s, flags=re.M); out=[]
    for part in parts:
        lm=re.match(r"^=== (TRAINER_[A-Z0-9_]+) ===$", part, re.M)
        if not lm or "\n\n" not in part: out.append(part); continue
        label=lm.group(1)
        if label=="TRAINER_NONE": out.append(part); continue
        meta, party = part.split("\n\n",1)
        boss = label in BOSS_ADDS
        bump = 3 if boss else 2
        party = re.sub(r"^Level:\s*(\d+)$", lambda m:f"Level: {min(100,int(m.group(1))+bump)}", party, flags=re.M)
        floor = 22 if boss else 10
        def ivs(m):
            vals=re.findall(r"(\d+)\s+(HP|Atk|Def|SpA|SpD|Spe)",m.group(0))
            return "IVs: "+" / ".join(f"{max(floor,int(v))} {n}" for v,n in vals) if len(vals)==6 else m.group(0)
        party=re.sub(r"^IVs:.*$",ivs,party,flags=re.M)
        mons=[x for x in party.strip().split("\n\n") if x.strip()]
        levels=[int(x) for x in re.findall(r"^Level:\s*(\d+)",party,re.M)]
        if mons:
            lvl=round(sum(levels)/len(levels)) if levels else 25
            sp=trainer_add(meta,label)
            nm=f"{sp}\nLevel: {lvl}\nIVs: {max(12,floor)} HP / {max(12,floor)} Atk / {max(12,floor)} Def / {max(12,floor)} SpA / {max(12,floor)} SpD / {max(12,floor)} Spe"
            if len(mons)<6: mons.append(nm)
            else: mons[-1]=nm
            party="\n\n".join(mons)+"\n\n"
        out.append(meta+"\n\n"+party)
    p.write_text("".join(out))


def wallace():
    p=ROOT/"src/data/object_events/object_event_graphics_info.h"; s=p.read_text()
    pat=re.compile(r"const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_BrendanNormal = \{.*?\n\};",re.S)
    repl='''const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_BrendanNormal = {
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_NPC_4,
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,
    .size = 256,
    .width = 16,
    .height = 32,
    .paletteSlot = PALSLOT_PLAYER,
    .shadowSize = SHADOW_SIZE_M,
    .inanimate = FALSE,
    .compressed = FALSE,
    .tracks = TRACKS_FOOT,
    .oam = &gObjectEventBaseOam_16x32,
    .subspriteTables = sOamTables_16x32,
    .anims = sAnimTable_Standard,
    .images = sPicTable_Wallace,
};'''
    s,n=pat.subn(repl,s,count=1)
    if n!=1: raise RuntimeError("Wallace player patch failed")
    p.write_text(s)


def config():
    p=ROOT/"include/config/pokemon.h"; s=p.read_text()
    s=re.sub(r"#define P_CAN_FORGET_HIDDEN_MOVE\s+FALSE","#define P_CAN_FORGET_HIDDEN_MOVE         TRUE",s)
    p.write_text(s)


def main():
    config(); evolutions(); encounters(); trainers(); wallace()
    (ROOT/"EMERALD_DELUXE.md").write_text("Emerald Deluxe: Gen 1-9 expanded dex, modern physical/special categories, easier solo evolutions, modernized trainers, Wallace player, and difficulty above BW2 Challenge Mode.\n")

if __name__=="__main__": main()
