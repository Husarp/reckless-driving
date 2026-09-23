"""Generate the Android launcher icons from the game's own cone artwork.

The APK shipped Capacitor's stock placeholder - a white square with a pale grid and a blue
cross - because `npx cap add android` writes those and nothing ever replaced them. The Windows
build has used the traffic-cone art since Batch 427; this makes Android match.

    .venv\\Scripts\\python.exe tools\\make_android_icons.py

Every size here is an INTEGER multiple of one of the assets/cone-N.png sources, scaled with
NEAREST. That is the whole point of the size table below: the cone is pixel art, and scaling
pixel art by a fraction can only blur or deform it - the same rule the in-game sprites follow
(CHANGELOG Batches 413, 461, 498, 502).

Android wants three sets:
  * ic_launcher.png            legacy square, the icon fills it on a solid background
  * ic_launcher_round.png      the same, circularly masked, for round-icon launchers
  * ic_launcher_foreground.png adaptive-icon foreground: transparent, and the art must stay
                               inside the safe zone (a 66/108 circle) because the launcher
                               masks and parallaxes the outer band however it likes
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
RES = ROOT / "mobile" / "android" / "app" / "src" / "main" / "res"

# The game's own --c-night, so the icon sits on the same black-blue the game does.
BG = (0x12, 0x16, 0x1F, 0xFF)

# density -> (legacy px, adaptive px, cone source px, legacy scale, adaptive scale)
# legacy:   cone covers ~2/3 of the tile.
# adaptive: cone must fit the 66/108 safe circle - that is 0.611 * the canvas.
DENSITIES = [
    #  name       legacy  adaptive  src  xL  src  xA
    ("mdpi",       48,     108,      32,  1,   64,  1),   # 32/48 = .67   64/108 = .59
    ("hdpi",       72,     162,      16,  3,   32,  3),   # 48/72 = .67   96/162 = .59
    ("xhdpi",      96,     216,      64,  1,  128,  1),   # 64/96 = .67  128/216 = .59
    ("xxhdpi",    144,     324,      32,  3,   64,  3),   # 96/144 = .67 192/324 = .59
    ("xxxhdpi",   192,     432,     128,  1,  128,  2),   # 128/192 = .67 256/432 = .59
]

SAFE_FRACTION = 66 / 108


def cone(src_px, scale):
    """The cone at src_px, blown up `scale` times with no interpolation."""
    im = Image.open(ASSETS / f"cone-{src_px}.png").convert("RGBA")
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return im


def centred(canvas_px, art, background=None):
    out = Image.new("RGBA", (canvas_px, canvas_px), background or (0, 0, 0, 0))
    out.alpha_composite(art, ((canvas_px - art.width) // 2, (canvas_px - art.height) // 2))
    return out


def circular(im):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, im.width - 1, im.height - 1), fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main():
    missing = [d for d, *_ in DENSITIES if not (RES / f"mipmap-{d}").is_dir()]
    if missing:
        sys.exit(f"no mipmap folder for: {', '.join(missing)} - is the android project generated?")

    written = 0
    for name, legacy_px, adaptive_px, l_src, l_scale, a_src, a_scale in DENSITIES:
        folder = RES / f"mipmap-{name}"

        legacy_art = cone(l_src, l_scale)
        assert legacy_art.width <= legacy_px, f"{name}: legacy art {legacy_art.width} > {legacy_px}"
        square = centred(legacy_px, legacy_art, BG)
        square.save(folder / "ic_launcher.png")
        circular(square).save(folder / "ic_launcher_round.png")

        fg_art = cone(a_src, a_scale)
        safe = adaptive_px * SAFE_FRACTION
        assert fg_art.width <= safe, f"{name}: foreground {fg_art.width} > safe zone {safe:.0f}"
        centred(adaptive_px, fg_art).save(folder / "ic_launcher_foreground.png")

        written += 3
        print(f"  {name:<8} legacy {legacy_px}px (cone {l_src}x{l_scale}={legacy_art.width})"
              f"   adaptive {adaptive_px}px (cone {a_src}x{a_scale}={fg_art.width}, safe {safe:.0f})")

    colour = RES / "values" / "ic_launcher_background.xml"
    colour.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        '    <color name="ic_launcher_background">#12161F</color>\n'
        "</resources>\n",
        encoding="utf-8",
    )
    print(f"  background colour -> #12161F (the game's --c-night)")
    print(f"{written} icons written")


if __name__ == "__main__":
    main()
