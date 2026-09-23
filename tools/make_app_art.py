"""Generate every platform's icon and launch art from the two source files in assets/.

    .venv\\Scripts\\python.exe tools\\make_app_art.py

Sources, both supplied by the user (Batch 547):
  * assets/gt-impact.ico                  the app icon, a full-bleed 256px tile with its own
                                          dark background, carrying 16/24/32/48/64/128/256 frames
  * assets/loading-impact-transparent.png the same artwork with NO background, 1920x1080

Two sources rather than one because the two jobs genuinely differ. A legacy launcher icon and the
Windows .ico are full tiles, so they want the tile art. An adaptive foreground and a splash are
art placed ON something else, so they want the transparent version - pasting the full tile would
put a dark square inside the adaptive icon's circular mask, which is exactly what it is not for.

This replaces make_android_icons.py, which built the same files from the traffic-cone artwork.

Everything is resized with NEAREST. The art is pixel art, and scaling pixel art by anything other
than a whole number can only blur or deform it (CHANGELOG Batches 413, 461, 498, 502). Where a
whole-number scale is available - every legacy icon below - the table picks the .ico frame that
gives one exactly. Where it is not (the splash, whose target sizes are fixed by Android and share
no common factor with the art), NEAREST at least keeps the edges hard instead of smearing them.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
RES = ROOT / "mobile" / "android" / "app" / "src" / "main" / "res"

ICON = ASSETS / "gt-impact.ico"
LOGO = ASSETS / "loading-impact-transparent.png"

# The game's own --c-night. The supplied splash uses exactly this, so the generated ones match it.
BG = (0x12, 0x16, 0x1F, 0xFF)
BG_HEX = "#12161F"

# density -> (legacy px, adaptive px, .ico frame, whole-number scale to reach legacy px)
DENSITIES = [
    #  name        legacy  adaptive  frame  scale
    ("mdpi",        48,     108,      48,    1),
    ("hdpi",        72,     162,      24,    3),
    ("xhdpi",       96,     216,      48,    2),
    ("xxhdpi",     144,     324,      48,    3),
    ("xxxhdpi",    192,     432,      64,    3),
]

# An adaptive icon's outer band is masked and parallaxed however the launcher likes; only the
# inner 66/108 circle is guaranteed to survive.
SAFE_FRACTION = 66 / 108

# Android's launch-screen drawables. The activity theme sets one as the window background
# (see AppTheme.NoActionBarLaunch), so each is a full-bleed canvas, not a bare logo.
SPLASHES = {
    "drawable": (480, 320),
    "drawable-land-mdpi": (480, 320),
    "drawable-land-hdpi": (800, 480),
    "drawable-land-xhdpi": (1280, 720),
    "drawable-land-xxhdpi": (1600, 960),
    "drawable-land-xxxhdpi": (1920, 1280),
    "drawable-port-mdpi": (320, 480),
    "drawable-port-hdpi": (480, 800),
    "drawable-port-xhdpi": (720, 1280),
    "drawable-port-xxhdpi": (960, 1600),
    "drawable-port-xxxhdpi": (1280, 1920),
}
# How much of the shorter edge the logo may occupy. Below 1 so the art never touches an edge and
# has room on a phone whose aspect ratio is nothing like the source's.
SPLASH_COVERAGE = 0.72


def ico_frame(px):
    """One frame out of the multi-size .ico, at its native resolution."""
    im = Image.open(ICON)
    im.size = (px, px)          # Pillow selects the matching frame from this
    im.load()
    return im.convert("RGBA")


def scaled(im, factor):
    if factor == 1:
        return im
    return im.resize((im.width * factor, im.height * factor), Image.NEAREST)


def logo_cropped():
    """The transparent artwork trimmed to the pixels that are actually opaque."""
    im = Image.open(LOGO).convert("RGBA")
    box = im.getchannel("A").getbbox()
    if not box:
        sys.exit(f"{LOGO.name} is fully transparent - nothing to place")
    return im.crop(box)


def centred(canvas, art, background=None):
    w, h = canvas
    out = Image.new("RGBA", (w, h), background or (0, 0, 0, 0))
    out.alpha_composite(art, ((w - art.width) // 2, (h - art.height) // 2))
    return out


def circular(im):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, im.width - 1, im.height - 1), fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def fit_within(art, max_w, max_h):
    """Largest NEAREST resize of `art` that fits the box, aspect preserved."""
    factor = min(max_w / art.width, max_h / art.height)
    w = max(1, int(art.width * factor))
    h = max(1, int(art.height * factor))
    return art.resize((w, h), Image.NEAREST)


def main():
    for src in (ICON, LOGO):
        if not src.is_file():
            sys.exit(f"missing source: {src}")
    missing = [d for d, *_ in DENSITIES if not (RES / f"mipmap-{d}").is_dir()]
    if missing:
        sys.exit(f"no mipmap folder for: {', '.join(missing)} - is the android project generated?")

    logo = logo_cropped()
    written = 0

    print("launcher icons")
    for name, legacy_px, adaptive_px, frame_px, scale in DENSITIES:
        folder = RES / f"mipmap-{name}"

        tile = scaled(ico_frame(frame_px), scale)
        assert tile.width == legacy_px, f"{name}: {frame_px}x{scale} = {tile.width}, wanted {legacy_px}"
        tile.save(folder / "ic_launcher.png")
        circular(tile).save(folder / "ic_launcher_round.png")

        safe = int(adaptive_px * SAFE_FRACTION)
        fg = fit_within(logo, safe, safe)
        centred((adaptive_px, adaptive_px), fg).save(folder / "ic_launcher_foreground.png")

        written += 3
        print(f"  {name:<9} legacy {legacy_px}px (ico {frame_px}x{scale})"
              f"   adaptive {adaptive_px}px (logo {fg.width}x{fg.height} in safe {safe})")

    print("launch screens")
    for folder_name, (w, h) in SPLASHES.items():
        folder = RES / folder_name
        if not folder.is_dir():
            print(f"  {folder_name:<22} skipped - folder not in this project")
            continue
        art = fit_within(logo, int(w * SPLASH_COVERAGE), int(h * SPLASH_COVERAGE))
        centred((w, h), art, BG).convert("RGB").save(folder / "splash.png")
        written += 1
        print(f"  {folder_name:<22} {w}x{h}  logo {art.width}x{art.height}")

    (RES / "values" / "ic_launcher_background.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<resources>\n"
        f'    <color name="ic_launcher_background">{BG_HEX}</color>\n'
        "</resources>\n",
        encoding="utf-8",
    )
    print(f"  adaptive background -> {BG_HEX} (the game's --c-night)")
    print(f"{written} files written")


if __name__ == "__main__":
    main()
