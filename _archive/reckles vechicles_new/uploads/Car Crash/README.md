# Reckless Driving

A retro pixel-art top-down driving game, fully self-contained in a single HTML file.
Designed to run in any modern browser — on desktop and mobile.

## What it is

You control a car driving down a multi-lane road and must avoid oncoming traffic for as long as possible.
The longer you survive, the higher your score. Settings let you tune difficulty and earn a higher score multiplier.

## How to play

Open `carCrash.html` in any browser. No server, no install, no dependencies.

### Controls

| Action | Desktop | Mobile |
|---|---|---|
| Steer left/right | Arrow keys or A/D | Drag the slider |
| Steer (alternative) | Drag the blue slider | Tilt phone (when enabled) |
| Use ability | Spacebar or click "READY!" button | Tap the "READY!" button |

### Settings

| Setting | Options | Effect on multiplier |
|---|---|---|
| Game Mode | Accelerating / Constant | Accelerating: +0.3x |
| Road Lanes | 3 / 4 / 5 | 3 lanes: +0.5x, 4 lanes: +0.1x, 5 lanes: -0.1x |
| Semi Trucks | Enabled / Disabled | Enabled: +0.2x |
| Special Ability | None / Jump / Ram | None: +0.5x, Jump: -0.1x, Ram: -0.2x |

### Special Abilities

- **Jump** — your car jumps over traffic, immune to collisions for ~1 second
- **Ram Shield** — your car destroys any vehicle it touches for ~1.8 seconds, scoring bonus points per kill

Energy recharges automatically after each use.

## Project files

| File | Description |
|---|---|
| `carCrash.html` | The game (all HTML, CSS, JS in one file) |
| `PLAN.md` | Development roadmap and feature backlog |
| `CHANGELOG.md` | Version history with dates and descriptions |
| `README.md` | This file |

## Planned features

See `PLAN.md` for the full roadmap. Highlights:
- Mobile touch and tilt (gyroscope) steering
- Reckless driver AI, emergency vehicles
- Local score leaderboard
- Player car color customization
- Smoother road animation and car movement
- Removal of the CAPTCHA window frame

## Technical notes

- Rendering: HTML5 Canvas, 160x220 internal resolution (displayed at 2x via CSS)
- Pixel art drawn procedurally — no image assets
- All state is in-memory; localStorage will be used for score ranking when implemented
- Target: Chrome, Firefox, Safari (iOS), Chrome (Android)
