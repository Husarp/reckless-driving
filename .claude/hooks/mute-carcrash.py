"""PreToolUse hook: never let a test run play sound at the user.

Standing instruction (2026-09-20): "remember to always when you test game set volume to 0 to
not interupt". Batch 430 made the game start at 30% sound / 50% music, so simply OPENING the
menu starts music playing out of the speakers while the user is doing something else.

A hook cannot itself run JavaScript inside the page, so this does the one thing a hook CAN do
reliably: it fires at the exact moment the game is being opened and hands back the snippet to
run, instead of relying on the instruction being remembered from a memory file.

Scoped deliberately: the browser tools are used for plenty of unrelated things (docs, other
sites), so this only speaks up when the target is actually this game - carCrash.html, the
car-crash launch.json entry, or the dev server's port.
"""
import json
import sys

GAME_MARKERS = ("carcrash", "car-crash", ":8420", "localhost:8420")

# The one-liner that was here first was NOT enough, and the user heard the game because of it.
# Setting config.soundVolume alone leaves music that is already playing untouched (its
# oscillators are live and never re-read the value), ignores config.musicVolume (its own
# category level since Batch 300), and is wiped by the next reload because the page re-reads
# the persisted keys on boot. All four lines are needed: stop the loop, zero both levels,
# persist them so reloads stay muted, and close the AudioContext so nothing queued can sound.
SNIPPET = (
    "stopMusic(); config.soundVolume = 0; config.musicVolume = 0; config.soundEnabled = false;\n"
    "    try { syncVolumeUI('sound', 0); syncVolumeUI('music', 0); } catch (e) {}\n"
    "    try { localStorage.setItem('soundVolume','0'); localStorage.setItem('musicVolume','0'); } catch (e) {}\n"
    "    if (audioCtx) { try { audioCtx.close(); } catch (e) {} audioCtx = null; }"
)

MESSAGE = (
    "Reckless Driving is being opened. Before clicking anything, launching a run or stepping "
    "loop(), run ALL of this via javascript_tool - not just the first line:\n"
    f"    {SNIPPET}\n"
    "The game defaults to 30% sound / 50% music since Batch 430, and merely opening the menu "
    "starts the music. config.soundVolume alone does NOT stop music already playing, and does "
    "not survive a reload."
)


def targets_the_game(tool_input) -> bool:
    return any(m in json.dumps(tool_input).lower() for m in GAME_MARKERS)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return                                  # nothing to say; never block the call
    if not targets_the_game(payload.get("tool_input", {})):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": MESSAGE,
    }}))


if __name__ == "__main__":
    main()
