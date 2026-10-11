# Sound lab

Renders the game's synthesized sounds to WAV files without playing the game, and measures them, so
sound changes can be heard and compared side by side.

- `render.js` - loads a game HTML file in headless Chrome and renders named sounds through an
  OfflineAudioContext into 44.1 kHz 16-bit WAVs, using the game's own audio code. Usage is at the
  top of the file.
- `analyze.py` - prints length, audible span, peak/RMS dBFS, spectral centroid and an 8-band
  spectrum per WAV, and writes a spectrogram PNG next to it. `--compare REF.wav X.wav` prints the
  differences against a reference.

## Setup (once per machine)

```
uv venv /tmp/sndvenv && VIRTUAL_ENV=/tmp/sndvenv uv pip install numpy matplotlib
```

`render.js` needs playwright-core (it falls back to `/home/coder/projects/handy-tool/node_modules/playwright-core`,
or set `PLAYWRIGHT_CORE`) and Chrome at `/opt/google/chrome/chrome` (or set `CHROME`).

## Workflow

1. Render: `node tools/soundlab/render.js carCrash.html notes/sounds/new` (all default sounds), or
   name some: `... notes/sounds/new crash@1 siren music@chase`. `--list` shows the recipe names.
2. Analyze: `/tmp/sndvenv/bin/python tools/soundlab/analyze.py notes/sounds/new/*.wav > notes/sounds/new/report.txt`
3. Listen: the owner plays the WAVs (and looks at the PNGs) and says what to change.
4. Reference sounds: the owner can drop a sound he likes into `notes/sounds/reference/` (as a WAV:
   analyze.py reads only WAV, and ffmpeg is not installed here). An agent then runs
   `analyze.py --compare notes/sounds/reference/ref.wav notes/sounds/new/crash-0.5.wav` and tunes the
   recipe toward it (length, brightness, which bands carry the energy).

The old sounds (before the 3.41.0 rework) are rendered in `notes/sounds/old/` for comparison.

## Notes

- Renders are repeatable: the same file, sound and `--seed` give the same WAV byte for byte.
- Each render runs 0.5 s of silence first and cuts it off, so the game's master limiter (3.41.0) has
  settled before the sound starts, as it has in the game. Older game files render the same as before.
  Since the limiter, new renders are 6 ms (264 samples) later than old ones: its look-ahead.
- `--mix full` (default) renders at every volume 1.0, so levels compare between sounds and between
  versions. `--mix game` uses the out-of-the-box Settings volumes (what a new player hears).
- Continuous sounds are driven the way the main loop drives them (siren distance every 1/60 s,
  music scheduler every 0.1 s), but this is a scripted pass, not real gameplay.
- The player engine: `engine@0.5` (speed ratio 0.5, stock car), `engine@0.5,roller` (another garage
  car), `engineramp` (ratio 0 -> 1 over 6 s). Renders of it are in `notes/sounds/new/`.
- Biome ambience: `bed@<biome>` (that biome's bed plus the first event, 2-5 s in), `bedx@forest,city`
  (a crossfade at 2.5 s), `bioev@<kind>` (one event alone: bird, water, horn, gust, wave, rumble).
  All stereo. Renders are in `notes/sounds/new/biomes/`.
- New sounds: add a recipe to `RECIPES` in `render.js`, or pass `--recipes my-recipes.js`.
