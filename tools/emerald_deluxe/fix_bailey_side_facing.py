#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "graphics/object_events/pics/people/brendan"


def flip_frames(name, frame_width, indices):
    p = BASE / f"{name}.png"
    im = Image.open(p)
    out = im.copy()
    for idx in indices:
        frame = im.crop((idx * frame_width, 0, (idx + 1) * frame_width, 32))
        frame = frame.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        out.paste(frame, (idx * frame_width, 0))
    out.save(p)

# Emerald stores west-facing movement art and mirrors it for east-facing movement.
# Bailey's walking, bike and one surfing pose were authored facing east instead.
# The running sheet is already authored correctly, so it must NOT be flipped.
flip_frames("walking", 16, (2, 7, 8))
flip_frames("mach_bike", 32, (2, 7, 8))
flip_frames("acro_bike", 32, (2, 7, 8, 17, 18, 19, 20, 25, 26))
flip_frames("surfing", 32, (4,))

print("Fixed Bailey horizontal facing for walking, Mach Bike, Acro Bike, and Surfing; running already faces west correctly")
