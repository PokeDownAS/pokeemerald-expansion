#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "graphics/object_events/pics/people/brendan"

# Standard Brendan normal/run sheets store west-facing frames at 2, 7, 8;
# the engine mirrors those for east-facing movement. Bailey's imported art had
# those side frames oriented east, so horizontal movement appeared reversed.
for name in ("walking", "running"):
    p = BASE / f"{name}.png"
    im = Image.open(p)
    fw, fh = 16, 32
    out = im.copy()
    for idx in (2, 7, 8):
        frame = im.crop((idx * fw, 0, (idx + 1) * fw, fh)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        out.paste(frame, (idx * fw, 0))
    out.save(p)

print("Fixed Bailey west/east facing frames for walking and running")
