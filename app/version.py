"""Single source of the app version.

Kept as a plain literal rather than parsed out of carCrash.html at runtime, because the
installer imports this too and it must not depend on the game file being present. Instead
scripts/build.ps1 checks this against the game's own GAME_VERSION and refuses to build on a
mismatch - so the two can't drift, which is the failure this project has hit repeatedly with
hand-copied numbers (see CHANGELOG Batch 405).
"""
VERSION = "3.1.1"
