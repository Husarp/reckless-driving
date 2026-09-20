"""Reckless Driving - the Windows app.

Wraps carCrash.html in a native window using the Edge WebView2 runtime that is already part of
Windows 11, so there is no browser chrome, no localhost to start by hand and nothing extra to
install alongside it.

SAVES. The game keeps everything - scores, coins, cars, achievements - in localStorage. Three
things below are what make that survive a restart AND an app update, and none of them is the
library default:

  * private_mode=False. pywebview defaults to True, which both turns on WebView2's InPrivate
    mode (localStorage is never written to disk) and deletes the whole user-data folder when
    the window closes (webview/platforms/edgechromium.py, clear_user_data).
  * storage_path pinned to %LOCALAPPDATA%\\RecklessDriving - OUTSIDE the installed program
    folder, so an update replacing that folder cannot touch the save.
  * a FIXED http port. pywebview serves a local file from 127.0.0.1:<port>, and localStorage is
    keyed to that origin, so a port that changed per launch would silently lose every save.
    pywebview already defaults to a fixed 42001 for this reason; it is set explicitly here so a
    change to that default can't quietly break saves.

--selftest <file> starts the app hidden, checks the real page actually booted, and writes a
one-line report. The build runs it and refuses to package a build that fails.
"""
import argparse
import ctypes
import json
import os
import shutil
import socket
import sys
import tempfile
import time
from pathlib import Path

import webview

from version import VERSION

APP = "Reckless Driving"
# Own port, not pywebview's shared 42001 default - two pywebview apps running at once would
# otherwise fight over it, and for this app losing the port means losing the save origin.
HTTP_PORT = 42017
# The self-test runs on its own port and its own throwaway profile. It has to: a build must never
# collide with a copy of the game the player already has open, and must never touch the real save.
# Found the hard way - a build's self-test silently read the INSTALLED game through the running
# copy's server and reported the wrong version, which looked exactly like a stale cache.
SELFTEST_PORT = 42018
# Batch 432 - the minimum is derived from what the menu actually needs, not guessed. Its content
# measures ~529px tall at native scale, and the frame is aspect-locked to the canvas (160/260), so
# height is the binding constraint: a 700px window leaves a ~657px frame, which clears 529 with room
# to spare. Below roughly 580 the menu overflows its frame and clips - reproduced at 420x520, where
# the content needed 529px in a 477px frame and the footer ended up 132px outside it.
# The old (900, 640) floor was wider than necessary (at that height the frame is only ~380 wide, so
# the extra width was empty margin) while being slightly short on the axis that actually matters.
WINDOW = dict(width=1120, height=840, min_size=(480, 700))


def already_running() -> bool:
    """Is another copy of the game already serving on our port?"""
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", HTTP_PORT)) == 0


def focus_existing_window() -> None:
    """Bring the copy that is already open to the front, instead of opening a broken second one.

    A second instance cannot bind the port, and pywebview does not treat that as an error - the
    new window just loads the URL, which the FIRST instance answers. The result is a second
    window showing the other instance's build of the game. Single-instance is the honest
    behaviour, and it is what the player expects from the desktop shortcut anyway.
    """
    try:
        user32 = ctypes.windll.user32
        handle = user32.FindWindowW(None, APP)
        if handle:
            if user32.IsIconic(handle):
                user32.ShowWindow(handle, 9)   # SW_RESTORE
            user32.SetForegroundWindow(handle)
    except Exception:
        pass                                    # focusing is a nicety; never fail the launch over it


def resource_root() -> Path:
    """The folder holding carCrash.html: PyInstaller's temp dir when frozen, else the project."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))


def game_html() -> Path:
    path = resource_root() / "carCrash.html"
    if not path.exists():
        sys.exit(f"carCrash.html not found next to the app (looked in {resource_root()})")
    return path


def game_url() -> str:
    """The game's path with a ?v= query, and it has to be there.

    The profile we deliberately keep for saves also holds WebView2's HTTP cache, and after an
    update the URL of the game file is byte-for-byte the same as before - so the browser served
    the PREVIOUS version's carCrash.html out of that cache and the update appeared not to have
    happened. Reproduced exactly: with a kept profile the self-test read 2.215.0 out of a build
    that packaged 2.216.0; with the profile deleted the same build read 2.216.0.

    pywebview does set no-store on its asset route, but those headers never reach the browser:
    it sets them on `bottle.response` and then returns `bottle.static_file(...)`, which builds
    its own response object. With no Cache-Control arriving, the browser falls back to heuristic
    caching and doesn't revalidate.

    Keying the URL to the version sidesteps all of that - a new version is simply a new URL.
    Query strings are not part of an origin, so localStorage (the save) carries over untouched,
    which is the whole reason the profile is kept in the first place. pywebview resolves this via
    os.path.relpath + urljoin, and bottle strips the query before matching its static route, so
    the file still serves normally.
    """
    return f"{game_html()}?v={VERSION}"


def storage_path() -> Path:
    """Where WebView2 keeps the profile that holds localStorage. Never inside the program folder."""
    local = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    path = local / "RecklessDriving"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_selftest(window, report: Path) -> None:
    """Prove the packaged build really works, rather than just that it started."""
    problems = []
    try:
        version = None
        for _ in range(150):                      # up to ~15s for the page to boot
            try:
                version = window.evaluate_js("typeof GAME_VERSION === 'string' ? GAME_VERSION : null")
            except Exception:
                version = None
            if version:
                break
            time.sleep(0.1)

        if not version:
            problems.append("the game never finished loading (GAME_VERSION never appeared)")
        elif version != VERSION:
            # Report the URL too: when this fires it is almost always the browser serving a cached
            # copy of a previous build, and the loaded URL is what tells you so.
            loaded = window.evaluate_js("location.href")
            problems.append(f"game reports {version}, app is built as {VERSION} (loaded {loaded})")

        if version:
            # Fonts: proves the embedding survived packaging. If these were still being fetched
            # from Google they would simply fail offline, which is the whole reason they were
            # embedded - so check the real thing, not that a <style> block exists.
            #
            # A font has to be LOADED before it can be checked or measured, and nothing here loads
            # it for us. The menu renders no DotGothic16 text, and `font-display: swap` means layout
            # falls back until the face is active - so both a bare document.fonts.check() AND a
            # width measurement report it missing on a build where it is perfectly fine. Measured
            # both ways: before an explicit load, check()=false and the width equals the fallback
            # exactly (285.9px); after one, check()=true and the width is 260px. So: ask for the
            # load, then poll until the browser confirms it.
            families = ["Silkscreen", "VT323", "DotGothic16"]
            js_list = ",".join(f'"{f}"' for f in families)
            window.evaluate_js(
                f"[{js_list}].forEach(f => document.fonts.load('16px \"' + f + '\"')); 1"
            )
            missing = families
            for _ in range(50):                       # up to ~5s
                missing = json.loads(window.evaluate_js(
                    f"JSON.stringify([{js_list}].filter(f => !document.fonts.check('16px \"' + f + '\"')))"
                ) or "[]")
                if not missing:
                    break
                time.sleep(0.1)
            if missing:
                problems.append("fonts not available offline: " + ", ".join(missing))

            # localStorage: the single most important thing to get right, since it IS the save.
            probe = window.evaluate_js(
                "(() => { try { localStorage.setItem('__selftest','ok');"
                " const v = localStorage.getItem('__selftest');"
                " localStorage.removeItem('__selftest'); return v; }"
                " catch (e) { return 'ERR:' + e.name; } })()"
            )
            if probe != "ok":
                problems.append(f"localStorage is not writable ({probe}) - saves would not persist")
    except Exception as e:                        # report it rather than vanish
        problems.append(f"self-test crashed: {e}")

    report.write_text("OK" if not problems else "FAILED: " + "; ".join(problems), encoding="utf-8")
    window.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(prog=APP, add_help=True)
    parser.add_argument("--selftest", metavar="REPORT", help="run hidden, write a report, exit")
    args = parser.parse_args()

    if not args.selftest and already_running():
        focus_existing_window()
        return

    window = webview.create_window(
        APP, game_url(), hidden=bool(args.selftest), **WINDOW
    )
    if args.selftest:
        # Isolated on every axis: its own port, and a throwaway profile so a build can never read
        # or damage the player's real save.
        # Sweep profiles a previous build could not finish deleting (see the finally: below).
        # They are unlocked by now, so this keeps %TEMP% from collecting one per build.
        for old in Path(tempfile.gettempdir()).glob("recklessdriving-selftest-*"):
            shutil.rmtree(old, ignore_errors=True)
        tmp = tempfile.mkdtemp(prefix="recklessdriving-selftest-")
        try:
            webview.start(run_selftest, (window, Path(args.selftest)),
                          private_mode=False, storage_path=tmp, http_port=SELFTEST_PORT)
        finally:
            # NOT TemporaryDirectory(): its cleanup raises, and WebView2 keeps handles open inside
            # EBWebView\Default for a moment after the window is destroyed, so the delete loses the
            # race and the app dies with an unhandled-exception dialog - after the self-test has
            # already passed, which is the worst version of this: a green build and a crash box.
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        webview.start(private_mode=False, storage_path=str(storage_path()), http_port=HTTP_PORT)


if __name__ == "__main__":
    main()
