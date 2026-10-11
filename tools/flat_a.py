"""Batch 656 - flatten the pointed top of the letter A in the embedded 'Jersey 10' font, then
re-hint the font with ttfautohint so the new A is hinted like every other glyph.

Owner's ask: the crash title's A gets a square top like the R, with ONE pixel cut from BOTH top
corners (the R has one cut, top right). Everything else in the font stays as it is.

Jersey 10 is drawn on a 75-unit pixel grid (unitsPerEm 1400, cap height 750 = 10 pixels, A is
7 pixels wide). The old A's outer contour climbs a 4-step staircase from (0,525) to a 1-pixel
peak at (225..300, 750); its counter is a 3x2 rectangle with a 1-pixel notch up to 525.
The new A:
    outer   - straight sides up to 675, top row (675..750) from x 75 to 450, i.e. the two
              corner pixels cut; legs and crossbar untouched.
    counter - a plain 3x4 rectangle (150..375 x 300..600), so the top bar is 2 pixels thick,
              the same weight as the R's.
The accented A's (A-grave .. A-ogonek) carry the same two contours (A-ogonek's outer runs on into
the ogonek), so they get the same top; AE is a different letter and is left alone.

Hinting. The stock fonts are hinted by ttfautohint (name ID 5 'ttfautohint (v1.8.4...)'), and a
glyph's TrueType program addresses its points by index, so the old A's program cannot be kept on
the new outline. The font is re-hinted with ttfautohint's DEFAULT options, which reproduce the
stock hinting byte for byte (fpgm, prep, cvt and every glyph program; checked on the stock fonts
with --selftest). Only the hinting data is copied back (glyph programs, fpgm, prep, cvt, gasp,
maxp's hinting limits): outlines, metrics, cmap, layout tables and the name table stay as they
are. The latin-ext subset has no 'o' (ttfautohint's standard character) and no blue-zone letters,
so it is hinted with the latin subset's glyphs added to it for the run - the same full-font
context the stock hints were made in - and only its own glyphs' programs are kept.

Usage (Python with fonttools, brotli and ttfautohint-py):
    python tools/flat_a.py carCrash.html             # edits the file in place
    python tools/flat_a.py --selftest a.woff2 b.woff2 # stock fonts: re-hinting reproduces them
It is idempotent: a face whose A is already flat AND hinted is left alone (a flat A without a
program, as left by the first version of this script, is only re-hinted).
tools/embed_fonts.py calls it at the end, so a fresh font download gets the flat A again.
"""
import base64
import copy
import io
import re
import sys

from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

A_FAMILY = ["A", "Agrave", "Aacute", "Acircumflex", "Atilde", "Adieresis", "Aring",
            "Amacron", "Abreve", "Aogonek"]
OLD_TOP = [(0, 525), (75, 525), (75, 600), (150, 600), (150, 675), (225, 675), (225, 750),
           (300, 750), (300, 675), (375, 675), (375, 600), (450, 600), (450, 525), (525, 525)]
NEW_TOP = [(0, 675), (75, 675), (75, 750), (450, 750), (450, 675), (525, 675)]
OLD_COUNTER = [(150, 300), (375, 300), (375, 450), (300, 450), (300, 525), (225, 525),
               (225, 450), (150, 450)]
NEW_COUNTER = [(150, 300), (375, 300), (375, 600), (150, 600)]
MAXP_HINT_FIELDS = ["maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
                    "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions"]


def load(data):
    # Keep the font-wide header values (bbox, max extents, timestamp) exactly as shipped - the
    # Google subset carries the full family's values, and only the A's own bounds should change.
    return TTFont(io.BytesIO(data), recalcBBoxes=False, recalcTimestamp=False)


def contours(glyphset, name):
    pen = RecordingPen()
    glyphset[name].draw(pen)
    out, cur = [], []
    for op, args in pen.value:
        if op in ("moveTo", "lineTo"):
            cur.append(tuple(args[0]))
        elif op == "closePath":
            out.append(cur)
            cur = []
        else:                               # Jersey 10 is pure straight lines on a grid
            raise SystemExit(f"{name}: unexpected pen op {op}")
    return out


def rotations(seq):
    return [seq[i:] + seq[:i] for i in range(len(seq))]


def flatten(contour):
    """Return the contour with the A's top redrawn, or None if it is not an A contour."""
    if contour in rotations(OLD_COUNTER):
        return list(NEW_COUNTER)
    n = len(OLD_TOP)
    for i in range(len(contour)):
        rot = contour[i:] + contour[:i]
        if rot[:n] == OLD_TOP:
            return NEW_TOP + rot[n:]
    return None


def flatten_font(font):
    """Redraw the A family in place; returns the list of changed glyphs."""
    glyf, gs = font["glyf"], font.getGlyphSet()
    changed = []
    for name in A_FAMILY:
        if name not in glyf.keys():
            continue
        new, hits = [], 0
        for c in contours(gs, name):
            f = flatten(c)
            hits += f is not None
            new.append(f if f is not None else c)
        if not hits:
            continue
        pen = TTGlyphPen(gs)
        for c in new:
            pen.moveTo(c[0])
            for p in c[1:]:
                pen.lineTo(p)
            pen.closePath()
        g = pen.glyph()
        g.recalcBounds(glyf)
        glyf[name] = g                     # no program yet - hint() gives it one
        changed.append(f"{name}({hits})")
    return changed


def program(g):
    return g.program.getBytecode() if hasattr(g, "program") else b""


def ttf_bytes(font):
    out = io.BytesIO()
    flavor, font.flavor = font.flavor, None
    font.save(out)
    font.flavor = flavor
    return out.getvalue()


def dehinted(font):
    """A TTF copy of the font with every hint removed (ttfautohint refuses hinted input)."""
    f = load(ttf_bytes(font))
    for t in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX"):
        if t in f:
            del f[t]
    for name in f["glyf"].keys():
        g = f["glyf"][name]
        if g.numberOfContours != 0:
            g.program = ttProgram.Program()
            g.program.fromBytecode(b"")
    for r in f["name"].names:                # ttfautohint also refuses a font it already signed
        if r.nameID == 5 and "; ttfautohint" in r.toUnicode():
            r.string = r.toUnicode().split("; ttfautohint")[0]
    return f


def add_helper_glyphs(font, helper):
    """Give `font` every glyph and cmap entry of `helper` that it lacks (same family, other subset)."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    order = font.getGlyphOrder()
    have = set(order)
    extra = [n for n in helper.getGlyphOrder() if n not in have]
    for n in extra:
        glyf[n] = copy.deepcopy(helper["glyf"][n])
        hmtx[n] = helper["hmtx"][n]
    font.setGlyphOrder(order + extra)
    glyf.glyphOrder = order + extra
    mine = font.getBestCmap()
    for st in font["cmap"].tables:
        if st.isUnicode():
            for cp, n in helper.getBestCmap().items():
                if cp not in mine and (st.format != 4 or cp <= 0xFFFF):
                    st.cmap[cp] = n


def hint(font, helper=None):
    """Re-hint `font` in place with ttfautohint defaults; only hinting data is copied back."""
    import ttfautohint
    work = dehinted(font)
    if ord("o") not in work.getBestCmap():
        if helper is None:
            raise SystemExit("this face has no 'o' and no helper face to hint it with")
        add_helper_glyphs(work, dehinted(helper))
    hinted = load(ttfautohint.ttfautohint(in_buffer=ttf_bytes(work)))
    for name in font["glyf"].keys():
        g = font["glyf"][name]
        if g.numberOfContours != 0:
            g.program = ttProgram.Program()
            g.program.fromBytecode(program(hinted["glyf"][name]))
    for tag in ("fpgm", "prep", "cvt ", "gasp"):
        if tag in hinted:
            font[tag] = hinted[tag]
        elif tag in font:
            del font[tag]
    for k in MAXP_HINT_FIELDS:
        setattr(font["maxp"], k, getattr(hinted["maxp"], k))


def has_latin_o(data):
    return ord("o") in load(data).getBestCmap()


def patch_face(data, helper_data):
    """Return (new woff2 bytes or None if nothing to do, description)."""
    font = load(data)
    changed = flatten_font(font)
    if not changed:
        names = [n for n in A_FAMILY if n in font["glyf"].keys()]
        if all(program(font["glyf"][n]) for n in names):
            return None, "A already flat and hinted, left alone"
    helper = None
    if helper_data is not None:
        helper = load(helper_data)
        flatten_font(helper)               # the hinting context sees the new A too
    hint(font, helper)
    font.flavor = "woff2"
    out = io.BytesIO()
    font.save(out)
    what = ("redrew " + ", ".join(changed) + " and re-hinted") if changed else "re-hinted (A was flat, unhinted)"
    return out.getvalue(), what


FACE_RE = re.compile(r"(@font-face \{\s*font-family: 'Jersey 10';[^}]*?base64,)([A-Za-z0-9+/=]+)")


def patch_html(path):
    html = open(path, encoding="utf-8", newline="").read()
    faces = [base64.b64decode(m.group(2)) for m in FACE_RE.finditer(html)]
    if not faces:
        raise SystemExit("No embedded 'Jersey 10' @font-face found.")
    helper = next((d for d in faces if has_latin_o(d)), None)   # the latin subset
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        data = base64.b64decode(m.group(2))
        new, what = patch_face(data, None if has_latin_o(data) else helper)
        print(f"  Jersey 10 face {count}: {what}")
        return m.group(0) if new is None else m.group(1) + base64.b64encode(new).decode("ascii")

    html = FACE_RE.sub(repl, html)
    open(path, "w", encoding="utf-8", newline="").write(html)


def selftest(paths):
    """Re-hint the STOCK fonts: every hint must come out identical to Google's."""
    datas = [open(p, "rb").read() for p in paths]
    helper = next((d for d in datas if has_latin_o(d)), None)
    bad = 0
    for p, d in zip(paths, datas):
        orig, font = load(d), load(d)
        hint(font, None if has_latin_o(d) else load(helper))
        diff = [n for n in orig["glyf"].keys() if program(orig["glyf"][n]) != program(font["glyf"][n])]
        for tag in ("fpgm", "prep"):
            if orig[tag].program.getBytecode() != font[tag].program.getBytecode():
                diff.append(tag)
        if list(orig["cvt "].values) != list(font["cvt "].values):
            diff.append("cvt")
        diff += [k for k in MAXP_HINT_FIELDS if getattr(orig["maxp"], k) != getattr(font["maxp"], k)]
        print(f"  {p}: {len(orig.getGlyphOrder())} glyphs, {len(diff)} hinting differences {diff[:8]}")
        bad += len(diff)
    print("selftest", "PASS" if not bad else "FAIL")
    return not bad


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        sys.exit(0 if selftest(sys.argv[2:]) else 1)
    patch_html(sys.argv[1])
