# Reckless Driving

A retro pixel-art top-down driving game, fully self-contained in a single HTML file.
Designed to run in any modern browser — on desktop and mobile.

## What it is

You control a car driving down a multi-lane road and must avoid oncoming traffic for as long as possible.
Score comes from PASSING cars — not from survival time itself — multiplied by a score multiplier you raise
with fewer lanes, higher difficulty, a bigger car, and above all speed. Settings let you tune difficulty.
In-game, the TUTORIAL button explains all of this with the real numbers.

## How to play

Two ways, both offline — the fonts are embedded in the file, so nothing is fetched from the network.

**As a Windows app.** Run `build\RecklessDrivingSetup.exe`. It installs for your account only
(`%LOCALAPPDATA%\Programs\RecklessDriving`), needs no administrator rights, and adds a Start menu and
desktop shortcut. Windows SmartScreen will warn the first time because the exe is unsigned — "More info"
→ "Run anyway". To update, run a newer `RecklessDrivingSetup.exe`: it spots the existing install and the
button says **Update**. Your scores, coins, cars and achievements live in `%LOCALAPPDATA%\RecklessDriving`,
outside the program folder, so an update never touches them. Uninstall from Settings → Apps (saves are
kept unless you tick the box).

**Or just open `carCrash.html`** in any browser. No server, no install, no dependencies.

From the main menu: **START RUN** to play, **SETUP** for settings, **SCORES** for the local leaderboard,
**TUTORIAL** for the in-game HOW TO PLAY screen (shown automatically on a first launch).

### Controls

| Action | Desktop | Mobile |
|---|---|---|
| Steer left/right | Arrow keys or A/D (snaps to the nearest lane) | Drag on the road, tilt phone, or on-screen lane buttons (all optional settings) |
| Move forward/back | Up/Down arrow keys | — |
| Jump (hold to fly) | Hold Spacebar | Hold the JUMP energy bar |
| Pause | P, Escape, or the pause icon (top-left) | Tap the pause icon |

### Settings (Setup screen)

| Setting | Options | Effect on multiplier |
|---|---|---|
| Road Lanes | 3–10 | Multiplicative: 3 lanes x1.30, 4 x1.15, 5 x1.10, down to 10 x1.00 |
| Tilt Steering | Off / On (mobile) | — |
| Steering Buttons | Off / On | On-screen per-lane click/drag zones below the road |
| Hold for Multiple Lanes | On / Off | Off = one lane per key press, no matter how long it's held |
| Sound | Volume slider | — |
| Car Color | 10-swatch picker | — |

Speed always accelerates and semi trucks are always on — no longer configurable. The ability you get is
decided by your CAR, not a setting: **Jump** (43 cars), **Shield Bump** ram (8 heavy cars), or the
**Tank**'s ranged shot. Difficulty multiplies score too (SAFE x1.00, RECKLESS x1.15, SUICIDAL x1.40),
and every km/h above 50 adds +1%.

### Jump ability

Hold to fly and become immune to traffic (and ambulances) while airborne; release to land early. Needs at
least 3 of the bar's 9 cells (~34%) to take off, then drains for as long as it's held (about 3 seconds from
full). Energy does **not** regenerate passively — it is earned back by passing cars (+1 cell, trucks +2,
a grounded ambulance +5) and by close calls (+4).

## Building the Windows app

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install pywebview pyinstaller pillow
.\scripts\build.ps1
```

Produces `build\RecklessDrivingSetup.exe` (~23 MB). The build refuses to run if `app\version.py`
disagrees with the game's own `GAME_VERSION`, or if `carCrash.html` still references Google Fonts, and it
runs the built exe hidden first to check the game boots, the fonts resolve offline and `localStorage`
is writable — a build that fails any of those is never packaged. `-NoSelfTest` skips that last step.

## Building the Android app

`carCrash.html` is wrapped for Android with [Capacitor](https://capacitorjs.com/). The game is still a
single file — `mobile/sync-web.js` copies it into `mobile/www/index.html` at build time, and that copy is
build output, gitignored, never edited by hand.

```powershell
cd mobile
npm install
npm run sync
cd android
.\gradlew.bat assembleDebug
```

Produces `mobile\android\app\build\outputs\apk\debug\app-debug.apk` (~4.9 MB). The copy step repeats the
Windows build's font guard: it refuses to run if `carCrash.html` still references Google Fonts.

Requires the Android SDK, a JDK 21 and Node. On the current build machine all three are installed but
**none are on `PATH`**, so Gradle needs them pointed at explicitly:

```powershell
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:ANDROID_HOME = "C:\Users\adam\AppData\Local\Android\Sdk"
```

`mobile\android\local.properties` holds the SDK path and is gitignored, being machine-specific — Gradle
regenerates it, or write `sdk.dir=<path>` by hand.

The APK is **debug-signed**, so it installs by sideloading (allow "install unknown apps" on the phone).
That is all a personal build needs. Publishing to the Play Store would require a release keystore, which
is deliberately not kept in this repo.

## Development (Coder workspace — note: the app build above runs on Windows, not in the workspace)

Development happens in a Coder workspace. Two servers run from `~/game/`:

| Port | What |
|---|---|
| 8080 | Live preview — open `/carCrash.html`, refresh after each edit |
| 8090 | Drag-and-drop upload page (chat attachments reject `.html`) |

Start them if they're not running:

```
cd ~/game && nohup python3 -m http.server 8080 > server.log 2>&1 &
cd ~/game && nohup python3 tools/upload_server.py > upload.log 2>&1 &
```

The project is a git repo — each working state is committed, so bad edits
can be rolled back.

## Project files

| File | Description |
|---|---|
| `carCrash.html` | The game (all HTML, CSS, JS in one file) |
| `app/` | The Windows app host — `main.py` (WebView2 window) and `version.py` |
| `installer/` | `game.spec` (PyInstaller) and `setup.py` (the install/update/uninstall window) |
| `scripts/build.ps1` | Builds `build\RecklessDrivingSetup.exe` |
| `mobile/` | Capacitor wrapper that packages the game as an Android APK |
| `tools/` | `embed_fonts.py` (inline the fonts), `make_icon.py` (icon from the game's own sprite) |
| `assets/` | `recklessdriving.ico` — the app icon |
| `backup/` | Manual safety copies of `carCrash.html` |
| `Car Crash Game UI Design/` | Source UI/art mockup this design was implemented from (reference only, not part of the game) |
| `PLAN.md` | Development roadmap and feature backlog |
| `docs/` | Design proposals and code-verified reference notes |
| `CHANGELOG.md` | Version history with dates and descriptions |
| `README.md` | This file |
| `AGENTS.md` | Standing rules for AI agents working on this project |
| `tools/upload_server.py` | Drag-and-drop file uploader (port 8090) |

## Planned features

See `PLAN.md` for the full roadmap. Highlights:
- Cosmetic trail "effects" (fire, smoke, stars) usable on any car
- Crosswalks and median/traffic-island obstacles
- Main menu redesign (per-tab icons, lanes/difficulty moved under START RUN)
- Music: per-biome track selection, more drum variety
- An online leaderboard, and an Android build

(The road obstacles, car shop, NPC visual variety and crash animation listed here previously are all
built — see `CHANGELOG.md`. Road pickups were tried and deliberately removed.)

## Technical notes

- Rendering: HTML5 Canvas, internal resolution scales with lane count (`26px × lanes + 36`) × 260px, displayed via a JS-computed exact-fit frame that preserves the true aspect ratio at any viewport size
- Pixel art drawn procedurally — no image assets. Road/verge scenery is pre-rendered into offscreen buffers once per lane-count change and blitted each frame
- Fonts: 'Silkscreen' (headers), 'VT323' (numbers) and 'DotGothic16' (body), embedded in the file as
  base64 `@font-face` (latin + latin-ext subsets, ~68 KB) rather than fetched from Google Fonts, so the
  game keeps its type offline. Regenerate with `python tools\embed_fonts.py`
- Local leaderboard (top 10) persists via `localStorage`, filterable by lane count
- Target: Chrome, Firefox, Safari (iOS), Chrome (Android). Further mobile-specific work (touch/tilt polish) is on hold — a from-scratch native Android app is planned separately; this HTML version is treated as a prototype
