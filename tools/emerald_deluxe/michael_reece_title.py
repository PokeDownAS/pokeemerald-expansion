#!/usr/bin/env python3
from pathlib import Path
import io
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

# Rename character names only inside C string literals so identifiers, file paths,
# and engine symbols such as TRAINER_PIC_MAY / OBJ_EVENT_GFX_WALLY stay intact.
def rename_strings(text):
    pat = re.compile(r'"(?:\\.|[^"\\])*"', re.S)
    def repl(m):
        s = m.group(0)
        s = re.sub(r"\bMAY\b", "MICHAEL", s)
        s = re.sub(r"\bMay\b", "Michael", s)
        s = re.sub(r"\bWALLY\b", "REECE", s)
        s = re.sub(r"\bWally\b", "Reece", s)
        return s
    return pat.sub(repl, text)

for folder in (ROOT / "src", ROOT / "data", ROOT / "include"):
    if folder.exists():
        for p in folder.rglob("*"):
            if p.suffix in {".c", ".h", ".inc", ".s"} and p.is_file():
                try:
                    t = p.read_text()
                except UnicodeDecodeError:
                    continue
                nt = rename_strings(t)
                if nt != t:
                    p.write_text(nt)

# Restore Michael's original face/hair detail from the pre-shirt-fix sprite while
# preserving the corrected shirt pixels below the face. The prior commit contains
# the intended facial shading and outline.
front_path = ROOT / "graphics/trainers/front_pics/may.png"
original_bytes = subprocess.check_output(
    ["git", "show", "6893594ca217b9f621b0d9bcb026e48ed34f2fd7:graphics/trainers/front_pics/may.png"],
    cwd=ROOT,
)
original_front = Image.open(io.BytesIO(original_bytes)).convert("RGBA")
current_front = Image.open(front_path).convert("RGBA")
face_box = (20, 0, 45, 25)
current_front.paste(original_front.crop(face_box), face_box[:2])
current_front.save(front_path)

# Put the supplied 240x160 indexed Emerald Deluxe artwork on BG0.  We retain
# Emerald's existing title state machine, input handling, music and fades; BG0
# simply sits in front of the stock animated background layers.
p = ROOT / "src/title_screen.c"
t = p.read_text()
marker = 'static const u32 sTitleScreenCloudsGfx[] = INCGFX_U32("graphics/title_screen/clouds.png", ".4bpp.smol");'
custom = marker + '\nstatic const u32 sEmeraldDeluxeTitleGfx[] = INCGFX_U32("graphics/title_screen/emerald_deluxe.png", ".8bpp.smol");\nstatic const u32 sEmeraldDeluxeTitleTilemap[] = INCGFX_U32("graphics/title_screen/emerald_deluxe.bin", ".smolTM");\nstatic const u16 sEmeraldDeluxeTitlePal[] = INCGFX_U16("graphics/title_screen/emerald_deluxe.png", ".gbapal");'
if "sEmeraldDeluxeTitleGfx" not in t:
    if marker not in t:
        raise SystemExit("title declaration marker not found")
    t = t.replace(marker, custom, 1)

load_marker = '        DecompressDataWithHeaderVram(gTitleScreenCloudsTilemap, (void *)(BG_SCREEN_ADDR(27)));'
load_custom = load_marker + '\n        // Emerald Deluxe custom full-screen title on BG0\n        DecompressDataWithHeaderVram(sEmeraldDeluxeTitleGfx, (void *)(BG_CHAR_ADDR(0)));\n        DecompressDataWithHeaderVram(sEmeraldDeluxeTitleTilemap, (void *)(BG_SCREEN_ADDR(24)));\n        LoadPalette(sEmeraldDeluxeTitlePal, BG_PLTT_ID(0), 16 * PLTT_SIZE_4BPP);'
if "Emerald Deluxe custom full-screen title on BG0" not in t:
    if load_marker not in t:
        raise SystemExit("title load marker not found")
    t = t.replace(load_marker, load_custom, 1)

old_bg0 = 'SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(3) | BGCNT_CHARBASE(2) | BGCNT_SCREENBASE(26) | BGCNT_16COLOR | BGCNT_TXT256x256);'
new_bg0 = 'SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(0) | BGCNT_CHARBASE(0) | BGCNT_SCREENBASE(24) | BGCNT_256COLOR | BGCNT_TXT256x256);'
if old_bg0 in t:
    t = t.replace(old_bg0, new_bg0, 1)
elif new_bg0 not in t:
    raise SystemExit("BG0 config marker not found")

# Preserve each existing mode/layer setup and only add BG0 where the stock
# title screen is active.
def enable_bg0(match):
    s = match.group(0)
    if "DISPCNT_BG0_ON" in s:
        return s
    return s[:-2] + '\n                                    | DISPCNT_BG0_ON);'

t = re.sub(r'SetGpuReg\(REG_OFFSET_DISPCNT,\s*DISPCNT_MODE_1.*?\);', enable_bg0, t, flags=re.S)

# The artwork already contains its own version banner and PRESS START text.
left = '        spriteId = CreateSprite(&sVersionBannerLeftSpriteTemplate, VERSION_BANNER_LEFT_X, VERSION_BANNER_Y, 0);\n        gSprites[spriteId].sAlphaBlendIdx = ARRAY_COUNT(gTitleScreenAlphaBlend);'
left_new = '        spriteId = CreateSprite(&sVersionBannerLeftSpriteTemplate, VERSION_BANNER_LEFT_X, VERSION_BANNER_Y, 0);\n        gSprites[spriteId].invisible = TRUE;\n        gSprites[spriteId].sAlphaBlendIdx = ARRAY_COUNT(gTitleScreenAlphaBlend);'
if left in t:
    t = t.replace(left, left_new, 1)
right = '        spriteId = CreateSprite(&sVersionBannerRightSpriteTemplate, VERSION_BANNER_RIGHT_X, VERSION_BANNER_Y, 0);'
right_new = right + '\n        gSprites[spriteId].invisible = TRUE;'
if right in t and right_new not in t:
    t = t.replace(right, right_new, 1)

t = t.replace('        CreatePressStartBanner(START_BANNER_X, 108);', '        // PRESS START is part of the custom Emerald Deluxe artwork.')
t = t.replace('        CreateCopyrightBanner(START_BANNER_X, 148);', '        // Stock copyright banner omitted on the custom title artwork.')

p.write_text(t)
print("Installed Michael/Reece names, restored Michael face detail, and wired the Emerald Deluxe title screen")
