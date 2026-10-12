#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "src/data/trainers.party"

BOSSES = {
    "TRAINER_ROXANNE_1", "TRAINER_BRAWLY_1", "TRAINER_WATTSON_1",
    "TRAINER_FLANNERY_1", "TRAINER_NORMAN_1", "TRAINER_WINONA_1",
    "TRAINER_TATE_AND_LIZA_1", "TRAINER_JUAN_1", "TRAINER_SIDNEY",
    "TRAINER_PHOEBE", "TRAINER_GLACIA", "TRAINER_DRAKE", "TRAINER_WALLACE",
}

# Fully evolved additions are stepped down when an ordinary trainer is too early
# for them. This preserves the class theme without handing Route 102 trainers
# endgame stats.
def stage(species, level):
    if species == "SPECIES_LOKIX" and level < 24: return "SPECIES_NYMBLE"
    if species == "SPECIES_KILOWATTREL" and level < 25: return "SPECIES_WATTREL"
    if species == "SPECIES_ESPEON" and level < 25: return "SPECIES_EEVEE"
    if species == "SPECIES_MISMAGIUS" and level < 30: return "SPECIES_MISDREAVUS"
    if species == "SPECIES_GRENINJA":
        return "SPECIES_FROAKIE" if level < 16 else ("SPECIES_FROGADIER" if level < 36 else species)
    if species == "SPECIES_HAWLUCHA" and level < 28: return "SPECIES_MACHOP"
    if species == "SPECIES_LUCARIO" and level < 28: return "SPECIES_RIOLU"
    if species == "SPECIES_FLOATZEL" and level < 26: return "SPECIES_BUIZEL"
    if species == "SPECIES_BASCULEGION" and level < 40: return "SPECIES_BASCULIN"
    if species == "SPECIES_GARGANACL":
        return "SPECIES_NACLI" if level < 24 else ("SPECIES_NACLSTACK" if level < 38 else species)
    if species == "SPECIES_ROSERADE":
        return "SPECIES_BUDEW" if level < 20 else ("SPECIES_ROSELIA" if level < 34 else species)
    if species == "SPECIES_SYLVEON" and level < 28: return "SPECIES_EEVEE"
    if species == "SPECIES_SCIZOR" and level < 32: return "SPECIES_SCYTHER"
    if species == "SPECIES_HONCHKROW" and level < 32: return "SPECIES_MURKROW"
    if species == "SPECIES_GARDEVOIR":
        return "SPECIES_RALTS" if level < 20 else ("SPECIES_KIRLIA" if level < 30 else species)
    if species == "SPECIES_CYCLIZAR" and level < 26: return "SPECIES_PAWMO"
    if species == "SPECIES_LYCANROC" and level < 25: return "SPECIES_ROCKRUFF"
    if species == "SPECIES_DEERLING" and level >= 34: return "SPECIES_SAWSBUCK"
    if species == "SPECIES_STARAVIA":
        return "SPECIES_STARLY" if level < 14 else ("SPECIES_STARAPTOR" if level >= 34 else species)
    if species == "SPECIES_RAICHU" and level < 28: return "SPECIES_PIKACHU"
    if species == "SPECIES_MIENSHAO" and level < 35: return "SPECIES_MIENFOO"
    if species == "SPECIES_CRAWDAUNT" and level < 30: return "SPECIES_CORPHISH"
    if species == "SPECIES_HOUNDOOM" and level < 30: return "SPECIES_HOUNDOUR"
    return species

text = PATH.read_text()
parts = re.split(r"(?=^=== TRAINER_[A-Z0-9_]+ ===$)", text, flags=re.M)
out = []
for part in parts:
    m = re.match(r"^=== (TRAINER_[A-Z0-9_]+) ===$", part, flags=re.M)
    if not m or m.group(1) in BOSSES:
        out.append(part)
        continue
    blocks = part.split("\n\n")
    fixed = []
    for block in blocks:
        sm = re.match(r"(SPECIES_[A-Z0-9_]+)\n", block)
        lm = re.search(r"^Level:\s*(\d+)\s*$", block, flags=re.M)
        if sm and lm:
            old = sm.group(1)
            new = stage(old, int(lm.group(1)))
            if new != old:
                block = new + block[len(old):]
        fixed.append(block)
    out.append("\n\n".join(fixed))
PATH.write_text("".join(out))
