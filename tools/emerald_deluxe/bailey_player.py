#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "src/data/object_events/object_event_graphics_info.h"
s = p.read_text()
pat = re.compile(r"const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_BrendanNormal = \{.*?\n\};", re.S)
repl = '''const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_BrendanNormal = {
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_BRENDAN,
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_BRIDGE_REFLECTION,
    .size = 512,
    .width = 16,
    .height = 32,
    .paletteSlot = PALSLOT_PLAYER,
    .shadowSize = SHADOW_SIZE_M,
    .inanimate = FALSE,
    .compressed = FALSE,
    .tracks = TRACKS_FOOT,
    .oam = &gObjectEventBaseOam_16x32,
    .subspriteTables = sOamTables_16x32,
    .anims = sAnimTable_BrendanMayNormal,
    .images = sPicTable_BrendanNormal,
};'''
s, n = pat.subn(repl, s, count=1)
if n != 1:
    raise RuntimeError("Could not restore BrendanNormal graphics table")
p.write_text(s)
print("Bailey player graphics table enabled")
