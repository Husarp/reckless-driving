"""Generate a car-sprite icon from the game's OWN renderer.

SUPERSEDED as the shipped icon (2026-09-20, Batch 427): the app and the installer now use the
traffic-cone artwork the user supplied in "cone ico files/". This tool therefore writes to
assets/car-icon.ico and NO LONGER touches assets/recklessdriving.ico - running it must not
silently clobber supplied artwork. Kept because generating an icon from the live sprite is
still useful if a car-based icon is ever wanted again.

Original note follows.

Generate an icon from the game's OWN car sprite.

The icon is not hand-drawn: it opens carCrash.html in a hidden window and calls the game's real
drawPixelCar() with the player's current paint, on a strip of road built from the same palette
the road uses. So if the car art ever changes, re-running this keeps the icon honest - which
matters here, because hand-approximated versions of this game's sprites have a track record of
being wrong in ways nobody spots for weeks (see CHANGELOG Batch 175, Batch 410).

    python tools\\make_icon.py
"""
import base64
import io
import sys
import time
from pathlib import Path

import webview
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import main as app  # noqa: E402

OUT_PNG = ROOT / "assets" / "icon64.png"
OUT_ICO = ROOT / "assets" / "car-icon.ico"
# Every size is an exact integer ratio of the 64px base, so nearest-neighbour scaling stays
# pixel-crisp in both directions. 48 is deliberately absent - it is not a clean ratio of 64.
ICO_SIZES = [16, 32, 64, 128, 256]

DRAW_JS = """
(() => {
  const c = document.createElement('canvas');
  c.width = 64; c.height = 64;
  const g = c.getContext('2d');
  g.imageSmoothingEnabled = false;
  g.fillStyle = '#12161f'; g.fillRect(0, 0, 64, 64);          // --c-night
  g.fillStyle = '#5a5f66'; g.fillRect(6, 0, 52, 64);          // asphalt
  g.fillStyle = '#cec9b8'; g.fillRect(8, 0, 1, 64); g.fillRect(55, 0, 1, 64);   // edge lines
  g.fillStyle = '#ded9c8';                                     // lane dashes, clear of the car
  for (let y = 2; y < 64; y += 16) { g.fillRect(14, y, 2, 9); g.fillRect(48, y, 2, 9); }
  g.save(); g.translate(18, 8); g.scale(2, 2);
  drawPixelCar(g, 0, 0, resolvePlayerColor(), false, 0);
  g.restore();
  return c.toDataURL('image/png');
})()
"""


def main() -> None:
    result = {}

    def work(window):
        for _ in range(150):
            try:
                if window.evaluate_js("typeof drawPixelCar === 'function'"):
                    break
            except Exception:
                pass
            time.sleep(0.1)
        result["png"] = window.evaluate_js(DRAW_JS)
        window.destroy()

    # game_url(), not game_html(): same cache reason as the app itself - otherwise this can draw
    # the icon from a previously cached build of the game.
    window = webview.create_window("icon", app.game_url(), hidden=True, **app.WINDOW)
    webview.start(work, window, private_mode=False, storage_path=str(app.storage_path()),
                  http_port=app.HTTP_PORT)

    data_url = result.get("png") or ""
    if not data_url.startswith("data:image/png;base64,"):
        sys.exit("The game did not return an icon - did drawPixelCar() load?")

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    png = base64.b64decode(data_url.split(",", 1)[1])
    OUT_PNG.write_bytes(png)

    base = Image.open(io.BytesIO(png)).convert("RGBA")
    if base.size != (64, 64):
        sys.exit(f"Expected a 64x64 render, got {base.size}")
    frames = [base.resize((s, s), Image.NEAREST) for s in ICO_SIZES]
    frames[-1].save(OUT_ICO, format="ICO", sizes=[(s, s) for s in ICO_SIZES],
                    append_images=frames[:-1])
    print(f"Wrote {OUT_ICO.name} ({OUT_ICO.stat().st_size} bytes) at sizes {ICO_SIZES}")


if __name__ == "__main__":
    main()
