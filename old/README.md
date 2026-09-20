# Reckless Driving

A retro pixel-art top-down driving game, fully self-contained in a single HTML file.
Designed to run in any modern browser — on desktop and mobile.

## What it is

You control a car driving down a multi-lane road and must avoid oncoming traffic for as long as possible.
The longer you survive, the higher your score. Settings let you tune difficulty and earn a higher score multiplier.

## How to play

Open `carCrash.html` in any browser. No server, no install, no dependencies.

From the main menu: **START RUN** to play, **SETUP** for settings, **SCORES** for the local leaderboard.

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
| Road Lanes | 3–10 | 3 lanes: +0.5x, 4 lanes: +0.1x, 5+ lanes: -0.1x per lane above 4 |
| Tilt Steering | Off / On (mobile) | — |
| Steering Buttons | Off / On | On-screen per-lane click/drag zones below the road |
| Hold for Multiple Lanes | On / Off | Off = one lane per key press, no matter how long it's held |
| Sound | Volume slider | — |
| Night Mode | Off / On | +0.2x |
| Car Color | 10-swatch picker | — |

Speed always accelerates, semi trucks are always on, and Jump is the only ability — these are no longer configurable, but the multiplier still accounts for them.

### Jump ability

Hold to fly and become immune to traffic (and ambulances) while airborne; release to land early. Needs at least 25% energy to take off, then drains in real time for as long as it's held. Energy recharges automatically while idle.

## Project files

| File | Description |
|---|---|
| `carCrash.html` | The game (all HTML, CSS, JS in one file) |
| `Car Crash Game UI Design/` | Source UI/art mockup this design was implemented from (reference only, not part of the game) |
| `PLAN.md` | Development roadmap and feature backlog |
| `CHANGELOG.md` | Version history with dates and descriptions |
| `README.md` | This file |

## Planned features

See `PLAN.md` for the full roadmap. Highlights:
- Static road obstacles (crashed cars, debris)
- Road pickups (multiplier boosts, "golden honk", collectible letters)
- Car shop / unlockable player models
- Vehicle visual variety (more NPC body shapes/colors)
- Player crash animation

## Technical notes

- Rendering: HTML5 Canvas, internal resolution scales with lane count (`26px × lanes + 36`) × 260px, displayed via a JS-computed exact-fit frame that preserves the true aspect ratio at any viewport size
- Pixel art drawn procedurally — no image assets. Road/verge scenery is pre-rendered into offscreen buffers once per lane-count change and blitted each frame
- Fonts: Google Fonts 'Silkscreen' (headers/numbers) and 'Pixelify Sans' (body), loaded via `<link>`
- Local leaderboard (top 10) persists via `localStorage`, filterable by lane count
- Target: Chrome, Firefox, Safari (iOS), Chrome (Android). Further mobile-specific work (touch/tilt polish) is on hold — a from-scratch native Android app is planned separately; this HTML version is treated as a prototype
