# Reckless Driving

A retro pixel-art top-down driving game, fully self-contained in a single HTML file.
Designed to run in any modern browser — on desktop and mobile.

## What it is

You control a car driving down a multi-lane road and must avoid oncoming traffic for as long as possible.
Score comes from PASSING cars — not from survival time itself — multiplied by a score multiplier you raise
with fewer lanes, higher difficulty, a bigger car, and above all speed. Scattering an obstacle's cones and
being in the next lane when two cars wreck each other both pay on top. Settings let you tune difficulty.
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
| Steer left/right | Arrow keys or A/D (snaps to the nearest lane) | On-screen arrows or stick (Settings → **Touch Controls**) |
| Move forward/back | Up/Down arrow keys | The same arrows, or push the stick up/down — the stick does both axes at once |
| Use ability | Hold Spacebar | Hold the **USE** button |
| Pause | P, Escape, or the pause icon (top-left) | Tap the pause icon |

Dragging on the road and tilting the phone were both removed in v3.4.x: dragging put your hand over the
road you were reading and offered no way to accelerate or brake, and tilting was never accurate enough to
steer with.

### Settings (Setup screen)

| Setting | Options | What it does |
|---|---|---|
| Control Type | PC / Mobile | PC: keyboard only. Mobile: on-screen controls |
| Multi-Lane Hold | On / Off | Off = one lane per press or tap; On = hold to glide across several. On Mobile it lives on the Controls screen |
| Controls (Mobile) | EDIT → its own screen | Every touch option - arrows or joystick, size, height, style, layout, joystick position - with a live preview of your screen. Tap the preview to see it full size |
| Lane Change Speed (Mobile) | 1-5 | How fast the car crosses lanes while a direction or a diagonal is held. 3 is the original |
| Tap Road For Ability (Mobile) | On / Off | No ability button: touch the road - hold to keep jumping, tap to ram. Not with the floating joystick |
| Volumes | Master, plus music / siren / explosion / SFX | — |
| Skip Crash Animation | On / Off | Straight to the summary |
| Fullscreen | On / Off | Hides the phone's navigation bar while you play |
| Score Popups | On / Off | Floating +points when you pass or jump over a car |
| FPS Counter | On / Off | Bottom-right of the game screen |
| Abbreviate Money | On / Off | Shows 50K / 10.8M instead of the full number |
| Speed-Scaled Music | On / Off | Tempo rises as you speed up |
| Check For Updates | On / Off | See [Updating](#updating) |

Road lanes, difficulty and car colour are **not** here — lanes and difficulty are chosen on the main menu (the lane count is remembered)
(they drive the score multiplier: 3 lanes x1.30 down to 10 x1.00), and paint is in the Garage.

Speed always accelerates and semi trucks are always on — no longer configurable. The ability you get is
decided by your CAR, not a setting: **Jump** (43 cars), **Shield Bump** ram (8 heavy cars), or the
**Tank**'s ranged shot. Difficulty multiplies score too (SAFE x1.00, RECKLESS x1.15, SUICIDAL x1.40),
and every km/h above 50 adds +1%.

### Jump ability

Hold to fly and become immune to traffic (and ambulances) while airborne; release to land early. Needs at
least 3 of the bar's 9 cells (~34%) to take off, then drains for as long as it's held (about 3 seconds from
full). Energy does **not** regenerate passively — it is earned back by passing cars (+1 cell, trucks +2,
a grounded ambulance +5) and by close calls (+4).

## Updating

The game checks GitHub for a newer release on startup and shows a banner on the main menu when it
finds one. The check is a Settings toggle (**CHECK FOR UPDATES**, on by default) and there is a
**CHECK NOW** button beside it. A failed check is silent unless you asked for it - it is usually
just no internet.

| Where | What UPDATE does |
|---|---|
| Windows app | Downloads the setup exe and runs it; the app closes so the installer can replace it. Per-user, so no admin prompt. |
| Android | Downloads the APK and hands it to Android's installer. **Android always asks you to confirm** - a sideloaded app may never replace itself silently. |
| Browser | Opens the release page, since there is nothing to install. |

Dismissing the banner is remembered per version: "not now" survives a restart, but a newer release
still shows up.

The Android side needs `REQUEST_INSTALL_PACKAGES` and the system's "install unknown apps" permission
for the game; if it is not granted, the first UPDATE tap sends you to that settings screen.

**Updates only install over a build signed with the same key.** Since 3.25.0 the APK is signed with
the project's own release key (see *Android release key* below). Installs from before 3.25.0 were
debug-signed and cannot update to it in place: uninstall the old app first - which deletes the
progress saved on that phone - then install the new APK.

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

Run `npm install` in `mobile\` once, then build both the installer and the APK with one command:

```powershell
.\scripts\build.ps1 -Android
```

It ends by stating what it produced, e.g. `BUILT 3.5.1 - RecklessDrivingSetup.exe, RecklessDriving.apk`.
Both land in `build\`; the APK is also left at `mobile\android\app\build\outputs\apk\release\app-release.apk`.
Without `-Android` only the installer is built, and any APK left in `build\` by an earlier run is deleted
so it cannot be mistaken for part of the current build.

To build the APK on its own:

```powershell
cd mobile
npm run sync
cd android
.\gradlew.bat assembleRelease
```

The copy step repeats the Windows build's font guard: it refuses to run if `carCrash.html` still
references Google Fonts.

Requires the Android SDK, a JDK 21 and Node. On the current build machine all three are installed but
**none are on `PATH`**, so `build.ps1` sets these itself when the environment does not already define
them — an environment that does define them wins:

```powershell
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:ANDROID_HOME = "C:\Users\adam\AppData\Local\Android\Sdk"
```

`mobile\android\local.properties` holds the SDK path and is gitignored, being machine-specific — Gradle
regenerates it, or write `sdk.dir=<path>` by hand.

### Android release key

The APK is signed with the project's own release key, and it installs by sideloading (allow "install
unknown apps" on the phone). The key is **never** in this repository - the repository is public. It
lives in the build machine's user profile:

| File | What it is |
|---|---|
| `%USERPROFILE%\.keystores\recklessdriving-release.jks` | The keystore (RSA 4096, alias `recklessdriving`, valid until 2054) |
| `%USERPROFILE%\.keystores\recklessdriving-signing.properties` | Its path and password, read by `mobile\android\app\build.gradle` |

`build.ps1 -Android` stops with an error if the properties file is missing, rather than producing an
unsigned or debug-signed APK.

**Back both files up somewhere safe.** Android only installs an update over an app signed with the same
key, so if this key is lost, no installed copy can ever be updated again - every player would have to
uninstall, and lose their progress, a second time.

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
| `tools/` | `embed_fonts.py` (inline the fonts), `make_app_art.py` (Android icons and launch screen), `make_icon.py` (icon from the game's own sprite) |
| `assets/` | `gt-impact.ico` — the app icon; `loading-impact-transparent.png` — the launch-screen art |
| `PLAN.md` | Development roadmap and feature backlog |
| `CHANGELOG.md` | Version history with dates and descriptions |
| `README.md` | This file |

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
- Target: Chrome, Firefox, Safari (iOS), Chrome (Android). Mobile is no longer treated as a prototype:
  v3.4.0 added real on-screen controls and safe-area handling, and v3.5.0 ships this same HTML as an
  Android APK through Capacitor rather than the separate native app once planned

## Licence

**All rights reserved** — © 2026 Husarp. The code is public to read, and the releases are free to
download and play, but the game may not be copied, changed, shared, sold or built upon without
written permission. The embedded fonts (Silkscreen, VT323, DotGothic16, Jersey 10) keep their own licence, the
SIL Open Font License. Full terms in [LICENSE](LICENSE).
