# CHANGELOG — Reckless Driving

All notable changes to this project are listed here.
Format: `X.Y.Z — YYYY-MM-DD HH:MM: <description>`
- X = major overhaul, Y = new feature/update, Z = minor fix or tweak

---

## 3.6.0 — 2026-09-22 14:25: Batch 482 — The game updates itself

**There was no way to learn an update existed.** No button, nothing in the game touched GitHub, and updating meant remembering to go and look. Now the game asks, tells you, and installs it.

**One check, three platforms.** The game fetches the latest release from GitHub and compares its tag with its own `GAME_VERSION`. Only what happens when you say yes differs:

| Where | What UPDATE does |
|---|---|
| Windows app | Python downloads the setup exe and runs it, then the app exits so the installer can replace it |
| Android | A small Capacitor plugin downloads the APK and hands it straight to Android's installer |
| Browser | Opens the release page — there is nothing to install |

**Android will always ask you to confirm, and that is not a bug.** A sideloaded app is never allowed to replace itself silently; the system installer's confirmation is a platform guarantee. What this removes is everything before it — no browser, no downloads folder, no hunting for the file. Two taps, never leaving the game.

**Windows updates in place.** The installer already recognised an existing install and switched its own button to Update, so nothing new was needed there — and because the install is per-user, no admin prompt appears.

**A banner, not an interruption.** When a newer version exists, a bar appears above the main menu footer with UPDATE and a dismiss X. Dismissing is remembered *per version*, so "not now" survives a restart but a genuinely newer release still gets to speak up. The automatic check is a Settings toggle (CHECK FOR UPDATES, on by default) and runs 3 seconds after boot, so it never competes with font loading and save parsing. A failed check stays silent unless you pressed CHECK NOW yourself — it is almost always just no internet, which is not worth a warning.

**Version comparison is numeric, deliberately.** As plain strings `'3.9.0'` sorts above `'3.10.0'`, so a string compare would hide exactly the update most worth having. Seven cases are covered, including that one.

**Two small guards worth naming.** The Windows bridge refuses to download from anything but this project's own GitHub URL, because it saves and *executes* what comes back. Both platforms reject an implausibly small download rather than letting it fail later as a baffling "not a valid Win32 application" or an Android parser error.

**The APK finally knows its own version.** Capacitor generates `app/build.gradle` with a frozen `versionCode 1` / `versionName "1.0"`, and nothing had ever changed it — so every APK built so far announced itself to Android as 1.0 while the game inside said 3.5.x. It now reads `app\version.py`, the same literal `build.ps1` checks against `GAME_VERSION` and refuses to build on a mismatch, and derives the integer Android wants (3.6.0 → 30600). Caught by dumping the built APK's manifest rather than assuming the build was right.

**Verified against the live API**, not a mock: a real check from the browser build correctly read the published v3.5.1 and reported "up to date", and the banner, dismissal, per-version memory and settings toggle were each exercised. The built APK was dumped to confirm the `REQUEST_INSTALL_PACKAGES` permission and the compiled plugin are really in it. The Windows and Android **install** paths are still not device-tested — they need a real install and a real phone.

## 3.5.1 — 2026-09-22 13:52: Batch 481 — One command builds both, and says what it built

**`build.ps1 -Android` now builds the APK as well as the installer.** Before this, the two builds were separate: the Windows one ran from the script, the Android one needed four commands typed by hand in `mobile\`. One switch does both, at one version, with one summary line at the end:

```
BUILT 3.5.1 - RecklessDrivingSetup.exe, RecklessDriving.apk
```

**The APK is copied into `build\`** next to the installer, so `build\` holds every deliverable a run produced rather than hiding the Android one five folders deep in the Gradle output.

**Stale artifacts can no longer masquerade as current.** A plain Windows-only rebuild deletes any `build\*.apk` first. Without that, the previous run's APK would sit beside a freshly built exe and look like it came from the same version. For the same reason `BUILT.json` lists only what the run actually produced — a Windows-only build never claims an Android artifact.

**Why this batch happened at all:** the dev-status dashboard was showing `build: null` for this project and no APK. Three separate causes, all real — `BUILT.json` was still on an unmerged branch so no build had ever written one; the dashboard scans the top-level `build\` folder and the APK was never there; and its last scan predated the v3.5.0 release. The first two were this project's fault and are fixed here.

**Toolchain fallback.** The script sets `JAVA_HOME` and `ANDROID_HOME` itself when the environment does not already define them, because on this machine the SDK and JDK are installed but not on `PATH`. An environment that already sets them wins.

**A stale APK got caught, and the catch is now automatic.** The first run of this very script produced an APK one version behind. `sync-web.js` refreshes `mobile\www`, but Capacitor keeps its own copy of the web assets *inside* `android\`, and only `cap copy` moves one to the other. Without that second step Gradle saw nothing changed, reported `UP-TO-DATE`, and packaged the previous version — while every other signal said the build had succeeded.

Both halves are fixed: the script now runs `cap copy android`, and then **opens the finished APK and reads `GAME_VERSION` out of the game inside it**. A mismatch throws. It is the Android counterpart of the exe self-test, and it exists because "the build said OK" turned out not to mean the artifact was right.

No gameplay changed.

## 3.5.0 — 2026-09-22 13:35: Batch 480 — Android build: the game now ships as an APK too

**The game builds for Android.** Until now `scripts\build.ps1` produced one artifact, a Windows installer. There was no Android packaging in the project at all — no Capacitor, no Gradle, no `android/` folder. Now there is, and a release carries both an `.exe` and an `.apk`.

**The single-file rule is intact.** `carCrash.html` is still the one source of truth. `mobile/sync-web.js` copies it to `mobile/www/index.html` at build time, and that copy is gitignored — it is build output, never edited by hand. The copy step repeats the Windows build's own guard: if the game still references Google Fonts it refuses to run, because a packaged app must not need the network for its fonts.

**What was added**

- `mobile/` — a Capacitor wrapper: `package.json`, `capacitor.config.json`, `sync-web.js`
- `mobile/android/` — the native Android project, committed so the build is reproducible
- App id `com.husarp.recklessdriving`, app name "Reckless Driving"

**Why Capacitor rather than a rewrite.** The mobile work in Batches 478–479 (on-screen controls, safe-area insets, the hover audit) was all done in the HTML. A WebView wrapper inherits every bit of it for free. A native rewrite throws that away and re-earns it.

**The APK is debug-signed.** 4.3 MB, installs by sideloading, which is all a personal build needs. A Play Store upload would need a release keystore — a signing key that has to be created and kept by hand, and is deliberately not in this repo.

**Toolchain note.** The Android SDK, JDK 21 and Android Studio were already installed on the build machine but none of them are on `PATH`; the Gradle build is pointed at them explicitly via `JAVA_HOME`/`ANDROID_HOME` and a generated `local.properties`, which is gitignored because it holds a machine-specific path.

**Not done:** the launcher icon and splash screen are still Capacitor's defaults, and orientation is left at the Android default. Both are cosmetic and untouched on purpose — no game behaviour changed in this batch, and the version bump is for the new build target alone.

## 3.4.1 — 2026-09-22 21:15: Batch 479 — Tilt steering removed; "joke vehicles" renamed throughout

**Tilt steering is gone.** Direct decision: "it's not really possible to control every movement with this and this is way too hard." It was real and shipping — a Settings row, a `deviceorientation` listener, an iOS motion-permission request and per-frame steering that wrote `targetX` directly. All of it removed.

It should have gone in Batch 478 and did not. Three reasons it had to: it was never finished or tested on a real device, it **fought the new on-screen controls over the same `targetX`** (both writing it in the same frame, tilt last), and it asked iOS users to grant motion-sensor access for a feature the game no longer has any use for.

**"Joke vehicles" is now "special vehicles" everywhere** — 12 code comments and 16 changelog references. The term was **mine, never the user's**, and the instruction not to use it was given back in Batch 474; that batch only fixed the tutorial card and left the term throughout the source and the log. Fixed properly this time, including the surrounding phrasing ("a special vehicle is a novelty, not a reward for winning one"). Two mentions of the word survive on purpose: the line recording the instruction itself, and an unrelated joke about a menu label.

Verified after both changes: a full run plays and ends normally, the crash sequence completes into the result screen, all 16 Settings rows render, and the tutorial and Garage open cleanly.

## 3.4.0 — 2026-09-22 19:40: Batch 478 — Mobile pass: on-screen controls, safe areas, and the hover audit

### Controls

**The drag-to-steer line is gone on touch**, as instructed. It was a 1:1 finger-follow that put the player's own hand over the road they were reading, and it offered no way to accelerate, brake or use an ability. Movement on a phone is now **arrows or a stick**, chosen in Settings, with three new rows (hidden entirely on non-touch devices, so a desktop player never sees controls that can do nothing for them):

- **TOUCH CONTROLS: ARROWS / STICK / OFF.**
- **FLOATING STICK** — the stick is invisible until a thumb lands in the lower-left of the playfield, then appears *there*. Your suggestion, and it is the default.
- **FULLSCREEN** — hides the phone's navigation bar. It must be requested from a real user gesture, which the toggle click is; there is no way to do it from script alone.

**Diagonals work**, which was the explicit requirement: the stick is a true vector — horizontal drives lane steering and vertical drives accelerate/brake independently, so up-and-right does both at once. The arrows manage it too, tracked per touch id so a thumb can slide from one arrow onto another mid-corner without the first sticking down. Verified: up + right engage together and release cleanly.

**SMOOTH LANE CHANGE works on touch**, verified. Getting there meant extracting `steerPress()` / `steerRelease()` as the single implementation of "a steer input went down / came up" — the keyboard held that logic inline, and duplicating it for touch would have guaranteed the two drifted, with `multiLaneHold` the first thing to break.

**The controls sit in a reserved strip below the road, not on top of it.** The first version overlaid them, and a screenshot showed the USE button sitting directly on the player's car — the road is the one thing a driving game cannot cover. The strip reserves its height through the same frame mechanism the steering track already used. The floating stick is the one deliberate exception, because being summoned anywhere is its entire point.

### Fit and safe areas

`viewport-fit=cover` plus `env(safe-area-inset-*)` padding: the page now extends under a phone's camera island and home indicator, and the frame keeps clear of both. Also `overscroll-behavior: none` (no pull-to-refresh mid-run) and no tap-highlight flash.

**The HUD needed a floor, not just Batch 475's ceiling.** On a 375px phone `--hud-scale` computed to **0.62**, which rendered the pause button at **24px** — the CSS minimum was being applied and then scaled away underneath it. A mouse can hit 24px; a thumb cannot. Floored at 0.8 on touch only: the button is now 31px and the HUD still fits the canvas (285px of 316px).

### The hover audit — six ways to soft-lock

Six UI paths reveal something on `mouseenter`: the two DROP CHANCES tips, the missions help and sweep tips, the leaderboard tooltips, the Garage car card and the booster preview. On a phone a tap fires a synthetic `mouseenter` but **never a `mouseleave`** — so each of these opens and then stays open forever, covering the screen. One capture-phase listener now closes anything open on the next touch outside it, fixing all six without touching their own code. Verified on a tooltip and on the Garage card.

Also confirmed reachable without a keyboard: pause and resume both work from their buttons, and the USE button hides itself for the ability-free special vehicles rather than showing a dead control.

## 3.3.0 — 2026-09-22 17:00: Batch 477 — Stats screen regrouped: hero row + themed ledgers

"15 stats feels like a lot" — resolved by **grouping, not hiding**. Tabs would bury stats behind a fuzzy taxonomy, an expander would bury eleven of them behind a click on every visit, and removal punishes the players who like statistics. Grouping fixes the actual problem, which was fifteen equal tiles shouting at once.

The screen now reads as five objects:

- **Hero row** — BEST SCORE and PERFORMANCE SCORE, big, in their own colours: the two numbers that answer "how good am I?". A casual player reads these and leaves; the panels below serve everyone else. Same page, both audiences, no setting needed.
- **SCORING** — total, average, average of the last 50.
- **SURVIVAL** — longest survival, average run, close calls, best close calls in a run.
- **TOTALS** — runs played, vehicles dodged, total coins, total play time.
- **HABIT** — runs today, days played.

Rows use the label-left / value-right ledger language the Scores tab already speaks, and every per-stat colour survived the move. Nothing was removed and nothing is hidden: 2 hero tiles + 13 ledger rows = all 15 stats, zero clicks. If it ever still feels heavy, collapsing a *group* is a five-line change — which is the graceful-degradation argument that beat the expander.

Also this session: PLAN.md pruned from 494 lines to 39 on direct instruction — five live items plus a standing convention to keep the in-game ABOUT/tutorial current after notable batches. The old plan lives in git history.

## 3.2.2 — 2026-09-22 15:50: Batch 476 — Boosters removed from special vehicles

Direct request, and the reasoning is airtight: boosters only ever render during a jump, and no special vehicle jumps — they have no ability, a ram, or the launch. So the Garage's BOOST TYPE picker was offering equipment that could never appear on the road.

`carFlameAvailable()` now refuses every booster for `boxOnly` cars, which makes the picker show its existing "no booster customization for this vehicle" note — the same treatment the Tank's paint lock already gets. Verified: all six specials blocked, Stock keeps all three types, ram cars keep thruster and underglow exactly as before. FULL WARDROBE is untouched — it checks that boosters are globally *unlocked*, not what a given car can wear.

Also closes the PLAN question logged one batch ago ("booster for special vehicles???") — answered by removing them rather than inventing a use.

## 3.2.1 — 2026-09-22 15:20: Batch 475 — Popup font, ram points, calmer launches, HUD cap

**The popup letters were too big and too thick.** They were `bold 8px Silkscreen` — the loudest thing this UI can say, block capitals nearly half a car tall. Now `10px VT323`, the game's other pixel face (the XP and rank text already use it): same family, but a narrow face that reads as writing rather than signage. Under the 3x backing store it rasterises at 30 device px, which VT323 is actually designed for. Applies to every popup — points, close calls, letters, word completions.

**"I don't see any points for ramming cars with my ship" — correct, they did not exist.** The popups only covered passes and jump-overs. Every scoring kill now pops, on the car it killed, under the same SCORE POPUPS toggle: ram kills (`+N RAMMED`), tank shots (`+N DIRECT HIT`), and bumper launches (`+N BUMPED`).

**Launched cars flew off in "very random directions."** The lateral kick (up to 3.8) could rival the upward one, so a side tap sent cars sailing across the whole road. The throw is mostly **up-screen** now — verified 5:1 vertical over lateral — with a modest sideways push away from the player and a calmer spin. It reads as being hit by something moving fast, which is what happened.

**Fullscreen HUD capped at 1.5x.** Batch 433 deliberately removed the cap so the HUD would hold one proportion at every size — but at fullscreen with a high lane count the frame gets very wide, and the chips scaled right along with it into absurdity. There is a size past which bigger stops being readable and starts being ridiculous; the HUD now grows with the window up to 1.5x and then stops. (The pause/result panels were already fixed separately in Batch 469.)

Also logged to PLAN.md, verbatim: "booster for special vehicles???" — with the open questions it raises (cosmetic flame on a no-ability special? attached to LAUNCH or the ship's ram? or folded into the effects system?).

## 3.2.0 — 2026-09-22 14:10: Batch 474 — Tutorial overhaul: build stats, special vehicles, section order, real explosion; score popups with a toggle; one scrollbar

**HOW IT WAS BUILT — the requested statistics card**, in ABOUT after THE PRICES ARE REAL. Counted from the change log itself: **473 batches across 474 shipped versions, over 2,150 recorded individual changes** (a renamed label counts, and so does a single repainted pixel), in **26 working days spread over 33 calendar days**, Aug 21 to Sep 22, 2026. Static figures with an "as of v3.1.1" stamp — they will need a refresh at milestones, noted in PLAN.md.

**SPECIAL VEHICLES card** at the end of PROGRESSION, per direct instruction never to call them jokes (the term was mine, never the user's). It says what matters — no price, never on the road, Extra Boxes are the only way in, most trade their ability for a coin bonus — and deliberately reveals nothing else: no names, no count, and "one or two learned something stranger" is all the SHIP and BUMPER CAR get.

**PROGRESSION now sits before MASTER.** A new player meets the Garage, levels and dailies by their second run; MASTER is expert multiplier play. Reading order now matches encounter order — it was always odd that the beginner-facing section came after the expert one.

**Stale-copy audit, two real finds:** "Nine heavy vehicles trade Jump for the ram" — the SHIP made it ten, and the count is now computed from the roster so it can never go stale again. And SPOTTING CARS claimed *every* Garage car drives the road with "58 cars to find" — box-exclusives are excluded from traffic by design, so it promised six cars the road can never show. Now says "every car you can buy" and counts 52. The multiplier figures (×1.30 / ×1.40 / +1% / ×2.5 at 200) all checked out against the live constants.

**The SHIELD BUMP scene plays the real explosion.** It used to fake the impact with three static spark rectangles; it now runs `drawSbExplosionFrame` — same renderer, same 12 frames at 45ms — so what the tutorial shows is exactly what the road does.

**Score popups, with a Settings toggle.** Floating `+points` on every credited pass and jump-over. Placement follows where the points happened: a pass is credited the moment you draw level with the car, so the popup sits **on that car, beside you** — "you earned this off him" — while a jump-over pops **above the player** (tagged ×2 JUMP), because the car you cleared is underneath you at that moment. ON by default — the tutorial's HOW YOU SCORE scene shows floating points, and the game should match what the tutorial promises — with a SCORE POPUPS toggle under Settings, persisted across sessions.

**One scrollbar everywhere.** Batch 469 already unified the style; the tutorial rail still carried a 10px-width override from before. Removed — the exact same bar now appears in the Garage, the results screen, the tutorial and everywhere else.

## 3.1.1 — 2026-09-22 12:20: Batch 473 — The startup flash was the unstyled first paint; boot veil added

Direct report: for about a second at startup "the old design" appeared — smooth round text, a plain number with no ring, a grey half-built screen. **It was never an old design.** It was the very first paint, drawn before anything was ready:

- The embedded pixel fonts had not finished decoding, so the browser painted its **fallback monospace** — which is exactly what smooth, round, un-pixelated text looks like next to Silkscreen.
- No canvas frame had run yet, so the level ring canvas was blank (just the DOM "1" floating) and the road behind the menu was missing.
- Nothing gated the reveal: the page displayed the instant the HTML parsed, and with ~1MB of base64 fonts to decode, that gap is visible.

The fix is a **boot veil**: the body carries a `booting` class that hides its children — the dark page background still paints, so startup is a clean dark screen rather than a grey half-render. It lifts when the fonts are genuinely usable (`document.fonts.ready`) *and* one real frame has painted with them, so the first thing ever visible is the finished menu.

The veil has a **1.5-second hard fallback**: if the font promise somehow never settles (it should not — the fonts are embedded), the game still appears rather than stranding a black window. A veil that can stick shut is worse than the flash it prevents.

## 3.1.0 — 2026-09-22 11:30: Batch 472 — Render-scale architecture: old proportions back, everything sharp; stock renderer unified

Direct correction on v3.0: shrinking the world made the road and every raw-pixel object ~30% bigger relative to the cars. The proportions should be what they always were — the requirement is only that nothing is blurry or deformed. Backup: git tag `v3.0.0-pre-renderscale` + `backup/carCrash.3.0.0.pre-renderscale.html`.

### The scheme

**The world is back in its original units** — canvas 260 tall, ~26px lanes, and every raw constant restored to its pre-3.0 value (margins, player bounds, flight height, close-call gaps, launch arc, menu scene, all of it). Sharpness now comes from **resolution, not from changing the world**: the canvas backing store is `RENDER_SCALE = 3`× the world, applied as one transform at the top of each frame.

- **Road art** lands on a whole 3-device-pixel grid — integer, exact, sharp.
- **Cars** bypass the world transform and blit straight onto the device grid at **4 device pixels per sprite pixel** — integer, exact, sharp.
- 4:3 = 1.333, within 2.6% of the old 1.3 car-to-road ratio, so the game *looks* like it always did. `CAR_SCALE` is now literally `4 / 3`.

Measured: the letter token fills **67%** of its lane (the old game: 69%; v3.0 had pushed it to 90%). The bumper car paints exactly **72 device pixels wide** (18 × 4) in its own 9 colours + outline — zero resampling. The speed ramp was re-derived so 120 km/h still arrives at frame **6667** (pre-3.0: 6673). Verified end to end: spawning, jump to full height, ram, bumper launch, complete crash sequence into the result screen, snail trail past the screen edge, airflow at speed, and menu demo cars exactly on their lane centres with the easter-egg click mapping corrected for the 3× backing store.

The plumbing that made it safe: world code now reads `VIEW_W`/`VIEW_H` (world units) instead of `canvas.width/height` (now device units) — 31 call sites, mechanically converted; only the two attribute assignments know the multiplier exists. Frame text (score popups) rasterises at 3× as a free side effect, so it is crisper too.

### Stock renderer unified

Direct request. The in-game stock car was still `drawPixelCar`'s own inline art from the very first version of the game, while the Garage tile long ago moved to `drawBodySedan53` — the same car genuinely looked different in play and in the Garage (182 of 332 sprite pixels differed, per the Batch 471 audit). The body is now **delegated to the Garage's renderer inside `drawPixelCar`**, and because every stock-car depiction funnels through that one function — tutorial scenes, boost previews, menu traffic, the crash snapshot — they all updated together with zero call-site changes. The jump machinery is untouched. Verified: **0 mismatched pixels** between `drawPixelCar` and `drawBodySedan53`.

## 3.0.0 — 2026-09-22 09:20: Batch 471 — THE INTEGER-SCALE REFACTOR, plus outlines, trail end, and real speed airflow

A major-version bump because the entire rendering coordinate system changed. Rollback exists twice over: git tag `pre-integer-scale` and `backup/carCrash.2.243.1.pre-integer-scale.html`.

### CAR_SCALE 1.3 → 1

The whole blur/deform saga (Batches 461–470) had one root: vehicles were the only thing in the world resampled by a fractional factor. The road art was always drawn 1:1. Now vehicles are too — **copied into the canvas pixel-for-pixel, the exact pipeline the road always used** — and the one remaining scale is the whole-canvas CSS fit, identical for every pixel in the world. Measured: the gameplay sprite is now pixel-identical to the Garage's (exactly 18px wide, same palette), where Batch 469's smoothing gave 367 colours and Batch 461's nearest gave a deformed 10.

**This is a pure zoom, not a rebalance.** Every raw world-space constant was divided by 1.3 in the same pass: canvas 260→200 tall, side margins 18→14, player bounds 40→31, flight height 14→11 (with rise speed scaled to keep the same rise *time*), speed ramp 0.0003→0.000231 (measured: 120 km/h arrives at frame 6667 vs the old 6673), crash deceleration, close-call gaps, NPC brake gap, tank tracer range, launch arc, cone scatter. Everything expressed in `CAR_SCALE` units — speeds, hitboxes, spawn buffers, vertical physics, siren range — rescaled itself.

The menu's background scene was rebuilt to the same world (canvas 123×200, road 80, lanes 20) at its exact old aspect ratio, so the menu frame and every DOM design box are untouched. Verified: demo cars dead-centred in the new lanes, jump/ram/launch all work, traffic spawns, trail and air unchanged in behaviour.

The visible consequence beyond crisp cars: road art and vehicles now share one pixel size on screen, so the game finally reads as a single coherent pixel world instead of fine road pixels under coarse blurry cars.

### The rest

- **Snail tail's bottom-left outline** — direct report, and it was my own doing: the stub was outline + 2 slime + outline, and Batch 468's 3-wide repaint started *on* the left outline pixel, painting body colour over it. Outline restored, verified black at both rows.
- **Ship's bow tip had no outline across its top** — the doc's row 0 is two hull pixels flanked by outline, leaving body colour raw on the sprite edge. Capped black.
- **Trail flicker at the screen edge** — a point was culled +4px past the edge, deleting the whole last segment, so the beam alternated between touching the bottom and stopping a segment short. Points now live to +60px past the edge (the per-row clip already draws nothing off-screen), and the end-soften only applies while the trail's end is still on screen — once the beam runs off the bottom, the screen edge is the cut. Verified: at speed the last point sits beyond the edge on every sampled frame.
- **Speed airflow replaces the chevron wake**, which was fairly judged as looking bad. Racing games draw this one way: short streaks hugging the flanks, born at the front corners where the air splits around the body, sliding backward *slower than the world* (boundary air clings), drifting slightly outward past the rear — thin broken lines, bright head, fading tail, never a solid rail and never centred on the body. Active for **every vehicle above 175 km/h** per direct spec; ramming switches it on at any speed and boosts it, so the SHIP's ability still reads. Measured: 0 particles at 120 km/h, 17 at 176, 19 at 200, 20 while ramming at 100. Cleared between runs.

## 2.243.1 — 2026-09-22 07:10: Batch 470 — Sprites were blitted onto fractional pixels; spin overshoot

**Every sprite was landing between pixels.** The buffer pad was 22/44, and `22 x 1.3 = 28.6`, `44 x 1.3 = 57.2` — both fractional. So the blit destination was always fractional, which does two bad things at once: it forces the resampler to interpolate across the *whole* sprite, blurring far beyond what the 1.3 ratio alone costs, and it shifts the art sideways by the fractional part.

That is the off-centre car. Measured on the BUMPER CAR: drawn **1px right** of its lane centre and **25px wide where 18 x 1.3 = 23.4** — smeared 1.6px wider than it actually is. It was not drawn wrong and it was not a separate issue; it was this.

`CAR_SCALE` is 1.3 = 13/10, so a value only survives it whole when it is a multiple of 10. Every dimension follows that rule now: pad 20 -> 26, 40 -> 52, buffer 70 -> 91, 150 -> 195. The un-rotated path also blits at a straight integer destination rather than going through a translate chain that ended on `-width / 2` — fractional for any odd width, 23 giving -11.5. **Re-measured: off by 0.0px.**

**The spin did extra turns after it had already landed.** Direct report. The target was recomputed with `Math.ceil` *every frame*, so the moment an easing step carried the angle even slightly past it, `ceil` jumped to the next multiple of 360 and the settle restarted a full turn further on — repeatedly. The target is locked once, on the frame the coast begins, and the approach is clamped so it cannot overshoot. Verified across 1, 4 and 12 clicks: **0 overshoots**, landing on exactly 2, 6 and 6 turns.

**The blur itself is NOT fixed, and cannot be at this scale.** Measured on one sprite, counting distinct colours: the Garage draws it in **10**; gameplay at 1.3x smoothed is **367**; at 1.3x nearest it is 10 but the shape deforms (22 of 32 rows single-height, 10 double); at an integer 2x or 3x it is **10 with the shape intact**.

So crispness and correct shape are only available together at an integer scale. Everything else is choosing which one to lose. See PLAN.md.

## 2.243.0 — 2026-09-22 06:00: Batch 469 — Sprite distortion (my regression), fullscreen panels, trail colour, scrollbars

**The sprites were being deformed, and it was Batch 461's doing.** Direct report: the donut is not round, the piano's black keys are misplaced, "black lines added", shapes changed — in gameplay but never in the Garage, and on NPCs too.

Batch 461 blitted sprites **nearest-neighbour**, and nearest-neighbour at 1.3x cannot keep pixel art intact. Measured: of 32 source rows, **22 map to one destination row and 10 map to two**. So 31% of every sprite is drawn double-height and 69% is not, and the same happens horizontally. A 1px outline lands as 1px in places and 2px in others — the "added black lines" — and a circle picks up flat sides. Measured on the donut: native row widths run `18,18,18,20,20,20,20,18` through the middle; nearest gave `23,23,26,26,26,26,26,26,23`.

Smoothing is back on for the blit. **This is not a return to the pre-461 state**: that antialiased each `fillRect` straight onto the road, so edges blended with asphalt and left the grey fringe that started all of this. Drawing into a transparent buffer first means edges blend with *transparency*, so shapes stay true and the fringe stays gone.

**Neither option is correct, because 1.3 is not an integer.** Blur or deform — those are the only two outcomes of resampling pixel art by a fractional factor. The real fix is integer scaling end to end, which means authoring the world at 1x and letting one integer display scale do the enlarging. That is a real refactor (every raw pixel constant: canvas height, player bounds, flight height, spawn margins) and it is now on PLAN.md rather than attempted mid-batch.

**Maximised window broke the pause and result panels.** `--hud-scale` is derived from **width alone** — correct for the HUD chips, which only need to track the road's width, but wrong for the two fixed 506x822 panels: on a wide window it made them 2500px+ tall and they ran off the frame, clipping PAUSED off the top and the hint off the bottom. Both panels now use `--panel-scale`, which fits **both** axes — the same rule the menu has always used, and the only place it was missing.

**The trail painted white whatever colour you picked.** Direct report: green came out "almost blue, a green-blue mixture". Two compounding causes, both mine:

1. The core was `shade(hex, 0.75)` — three quarters of the way to white.
2. The three layers were **concentric overlapping rects**, and under `lighter` every overlap *adds*. The centre received deep + mid + core at once, summed past 1.0 and clipped. Measured: a green trail painted out as `rgb(235,255,255)`.

The layers are non-overlapping bands now and the core is only `0.35` toward white. Verified by sampling all 13 pixels across the beam: with green selected every band pixel reads green-dominant; with red, red-dominant.

**Three more trail fixes:**
- **Left over between runs** — road-anchored points were never cleared, so quitting and restarting left the old beam lying on the road. Cleared in `launchGame()`.
- **NPCs drove under it** — it was drawn inside `Player.draw()`, landing on top of every vehicle already rendered. It is road paint, so it now draws with the road, before traffic.

**Scrollbars were never themed at all.** Direct report that the result screen's bar has arrow buttons and a rounded thumb and a different background. Root cause: **`scrollbar-color` was set**, and in Chromium setting the standard scrollbar properties opts the element into the standard renderer, making every `::-webkit-scrollbar` rule below it dead. All that styling had no effect; what showed was the platform scrollbar. Removing `scrollbar-color` is what makes the rules apply.

Now applied to **every** scrollable element rather than a hand-maintained selector list — which is exactly how the result screen's bar drifted from the Garage's. Arrow buttons removed, square thumb with the pixel bevel, and the track matches the panel it sits in.

## 2.242.0 — 2026-09-22 04:20: Batch 466-468 — Pause wash, snail rebuilt, air slowed, ram wake

**Pause panel wash covers the frame.** The same fault as Batch 460's result screen, in the third and last screen built on the fixed-box pattern: a 506x822 box scaled by `--hud-scale`, so a taller window left raw road above and below. Moved to `#pauseBackdrop`, `inset: 0`.

### The snail

**Its declared size did not match its art, and that caused the trail bug.** Batch 459 "made it smaller" by changing `h: 32 -> 28` and `hitboxW: 20 -> 18` — but the sprite is still drawn 20x32, so the numbers shrank and the art did not. Four rows of snail hung below the declared box, which is exactly why the trail appeared to start inside the snail rather than behind it: `drawY + player.height` was landing four rows short of the sprite's real bottom.

Reverted to 32x20 so the declaration matches the art. **If it should still be smaller, the sprite itself has to be redrawn** — the numbers alone cannot do it, and changing them alone is what broke this.

**The tail tip was pale blue.** The doc drew a 3px `#cfe9f0` slime stub, which at gameplay size reads as a stray blue artefact hanging off a brown snail. It also ended with no outline. Repainted in the body's own light tone with a black row closing it off — done in `drawGarageSnail53()` rather than by editing `PX_SNAIL`, so the transcribed data stays a faithful copy of the doc and the deliberate change stays visible as one.

**Three trail faults, all fixed:**
- *"Shouldn't be getting smaller — it cut the pixels."* The width tapered with age. At this pixel size that does not read as perspective, it reads as the beam being chewed away. Constant width now.
- *"Not going fully to the end of the screen."* Alpha faded to nothing with age, so the tail died mid-road while points still existed beyond it. Only the last 12% softens now, just enough that the end is not a hard chop. Measured: reaches y=258 of a 260px canvas.
- *"It looks like it's coming out of his ass."* Beyond the size bug above, laying the point at the very bottom edge starts the beam where the sprite stops, so nothing covers its origin. It starts at 72% of the body now, letting the snail sit on top of where it begins.

### Air

**Minimum raised to 150 km/h**, per direct spec.

**It was moving far too fast.** Direct report: "it looks like the air is going the other direction faster." It ran at **1.5-3.0x the road's own speed**, and once anything in a scrolling scene outruns the surface it is over, the eye stops reading it as part of the same world. Now **1.0-1.18x** — measured 6.35px/frame against the road's 5.29 at 180 km/h. The small excess is what keeps it reading as rushing air rather than as road markings, and each particle's own 0.8-1.5 speed spreads them either side of it.

**A ram wake**, per request, on the back of the vehicle. A wake is drawn as two arms leaving the trailing edge and **opening outward** as they fall behind — parallel streaks read as rain and converging ones read as suction. This follows the shape of the doc's own REAR AIR WAKE panel (Shield Bump storyboard, section 8b): two arms spreading ~30 degrees, broken rather than solid, losing alpha with distance so they die out instead of stopping. It matters most on the SHIP, which has every other ram cue suppressed — the wake is the only thing marking the ability there.

## 2.241.3 — 2026-09-22 03:05: Batch 465 — Fractional scores, and THE DESTROYER's id matches its name

**A saved run read "14,094.509".** Not invincible mode and not a test artifact — a real bug on a normal path.

`score` deliberately accumulates *raw fractional* values all run (points × multiplier, unrounded so that per-event rounding cannot drift the total), and **`endRun()` was the only place that rounded it**. Quitting from the pause menu goes through `exitToMenu()`, which calls `saveScore()` directly and never touches `endRun()` — so that route wrote the raw float straight into the run history and the leaderboard.

Rounded inside **`saveScore()`** rather than by patching `exitToMenu()`: `saveScore()` is the single funnel every path already goes through, so no future exit route can miss it. `endRun()` still rounds first, because the crash snapshot and result panel read `score` before `saveScore()` is ever called. Verified on the exact failing path — quitting mid-run with `score = 14094.50937` now stores **14095** in both the run history and the highscore list.

**Existing saves are repaired on load**, since a number that was never meant to be fractional should not keep displaying that way. Any fractional entry in `recentScores`, `runHistory` or `highscores` is rounded in place, once, and only written back if something actually changed.

**`act_of_god` is now `the_destroyer`**, on the explicit call that this is pre-release and the id should match the name. The old key is **migrated** rather than dropped, so the rename does not quietly take the achievement back off a save that already earned it. Verified: a save holding `act_of_god: true` comes back with `the_destroyer: true`, the old key gone, and the achievement showing as unlocked under its new name.

## 2.241.2 — 2026-09-22 02:30: Batch 464 — ACT OF GOD renamed to THE DESTROYER

Display name only. The **id stays `act_of_god`**, because that is the key persisted in `allTimeStats.achievementsUnlocked` — renaming it would silently un-unlock the achievement for anyone who had already earned it.

## 2.241.1 — 2026-09-22 02:15: Batch 463 — Clicking a menu car now does exactly what ramming one does

Direct correction. The easter egg had its own bespoke explosion and made the car vanish. Both were wrong: it should be the same outcome as a ram.

It now calls **the same functions gameplay calls**, rather than something that looks similar:

- `sbExplosionParts()` and `drawSbExplosionFrame()` — the real Shield Bump impact burst, 12 frames at 45ms, one of the three variants picked at random. Verified it queues a genuine 78-part variant.
- `drawCrushedWreck()` — the car **stays on the road as a wreck**, greyed and darkened, with the same 4 debris spots (half embers) the ram branch generates. It no longer disappears.

Two small things had to open up for this, both additive: `drawCrushedWreck()` takes an optional target context, because the menu scene draws to `menuCtx` rather than the gameplay canvas; and the wreck state lives outside `drawMenuScene()`, since the demo cars are rebuilt from `t` every frame.

A wrecked demo car clears itself when its position wraps back to the top, so the road repopulates with a fresh car instead of accumulating permanent corpses. Verified: the wreck survives 40 frames untouched, then clears on the wrap.

**The achievement was already there and does work** — ACT OF GOD is present in the secret list (22 secrets), tier `secret`, and unlocks on the click. What made it look absent is almost certainly that the running build is **2.227.0**, while the achievement shipped in 2.230.0.

One genuine subtlety found while testing: clicking a car that happens to be drifting *behind* a difficulty tile does nothing, because the tile is a `<label>` and real controls are deliberately passed through. That is correct — a background car must never swallow a control — but it does mean the egg only fires over open road.

## 2.241.0 — 2026-09-22 01:30: Batch 462 — Level badge spins with momentum; the number is actually centred; air back to 120

**Air particles return to 120 km/h.** Batch 461 lowered them to 75 on a misspoken instruction; the intent was always that air should *not* appear at lower speeds. Reverted.

**The spin is momentum now, matching the described behaviour**: a click spins the ring, more clicks make it spin **faster rather than restarting it**, and it coasts down to a stop on its own. Measured: one click gives 2 turns over 1.9s; two clicks 7 turns; four or more cap out at 7 turns in 2.8s.

It is a **CSS rotate on the ring canvas, not a redraw**, which buys three things at once. The number is a separate element, so it stays put and upright exactly as asked. The ring keeps showing real XP throughout, because its pixels are never touched. And nothing has to block `paintLevelBadge()` any more — which is precisely what let the previous version strand the badge permanently if a frame never arrived. That whole failure mode is gone rather than guarded.

**It always settles on a whole turn.** Stopping at an arbitrary angle would leave the progress arc pointing somewhere it does not mean — the arc starts at 12 o'clock and that has to stay true. Verified across 1, 2, 4 and 10 clicks: every one ends on an exact multiple of 360°.

FULL CIRCLE still unlocks on the first click.

**The number was 2px low, and the circle was not the cause.** The obvious suspect was wrong, which is why this was measured before anything was changed: the number's box and the ring's box share a centre to within **0.0px**, so the circle is correctly drawn and did not need remaking.

What is off is **Silkscreen's own metrics** — its digits carry no descender, so a line box centred by flexbox puts the *ink* low. At the menu's 28px the drawn pixels sit a full 2px below the ring's centre.

The correction is computed from the font's real metrics rather than hardcoded, because it does not scale linearly: the three sizes in use (28px menu, 15px badge, 11px three-digit) round to different whole-pixel offsets. Cached per font, so it measures once per size.

## 2.240.0 — 2026-09-22 00:40: Batch 461 — The grey overlay was antialiasing; vehicles now render 1:1 and blit

**It was never a shadow.** `CAR_SCALE` is 1.3, and `drawScaledVehicle()` scaled the *context* — so every sprite's `fillRect` landed between device pixels and canvas antialiased it. The blend against the road is the grey fringe; the softened edges are the blur. The Garage was clean because it draws at whole-number scales.

Measured on one sprite: **182 distinct colours** at gameplay scale against **10** at an integer scale.

Path antialiasing cannot be switched off, so the drawing had to stop being scaled. Sprites render at **1:1 into an offscreen buffer** — every rect on a whole pixel, exactly as in the Garage — and the finished buffer is blitted with `imageSmoothingEnabled = false`, which is nearest-neighbour and cannot invent an intermediate colour. **Now measured at 10 distinct colours, matching the reference exactly.**

This needed all 9 `drawScaledVehicle()` call sites to receive the render target instead of closing over `ctx` / `gctx` / `menuCtx`, since the drawing now goes somewhere else.

The buffer is padded (68×152 for a 22×60 worst-case sprite) because a lot is drawn outside the nominal box: the shield-bump guard reaches above `y=0`, thruster flames below `car.h`, and a jump lifts by up to `MAX_FLIGHT_HEIGHT`. Verified none of it is clipped — a jump paints 710 px against 444 for the same car standing plain, and a ram paints 1,396.

The blit position is also rounded to whole device pixels. Without that, nearest-neighbour sampling still shifts sub-pixel per frame — the same jiggle the NPC position rounding already exists to prevent.

**Level badge spin could strand permanently.** `levelSpinBusy` was a boolean, and `paintLevelBadge()` refuses to paint while a spin runs — so if the animation ever stopped without clearing the flag, the badge froze mid-sweep forever *and* every later click was refused by the same flag. Not hypothetical: `requestAnimationFrame` stops firing while a window is hidden or occluded. It is a **deadline** now (`levelSpinUntil`), which cannot strand: once the time is past the spin is over whether or not a frame ever ran, and the next paint restores the true value by itself.

**Air particles start at 75 km/h, was 120.** Direct correction — "they indicate speed so they should appear on lower speeds", and an indicator you never see cannot indicate anything: at `+0.0003`/frame, 120 km/h was about 111 seconds into a run. 75 km/h is roughly 12 seconds, still well clear of the 50 km/h start so standing still stays calm.

## 2.239.0 — 2026-09-21 23:40: Batch 460 — Trail rebuilt as real light; aura removed; brake lights culled; F3 rear made symmetric

**The aura is gone.** It was never asked for — it came in as a substitute while I wrongly believed a trail was impossible. Only the trail remains.

**The trail rendered as a ladder of separate bars.** A point is laid once per frame and then moves `currentSpeed` px, so at speed the points sit 5–7px apart and each was drawing a single 1px-tall bar, leaving the gap between them empty. It draws the **segments between points** now — every row from one point to the next, interpolating x across it. Verified continuous: 185 of 185 rows painted between the first and last point.

**And it was far too weak.** It painted at 0.22 / 0.45 / 0.55 alpha in `source-over`, which can only ever darken toward the road — the opposite of light. It composites with **`lighter`** now, so overlapping layers build toward white the way a blaster bolt or a neon tube does, and the core draws at full alpha. That is also what lets the bloom be wide without turning into a smear. Any paint colour still reads as neon, because neon is a hue plus a white-hot centre.

**Brake lights removed from 14 vehicles**, per the list: DRIFT, FORMULA, TANK, GO-KART, TRACTOR, F1, INDY OVAL, F3 JUNIOR, and all six box-exclusives. Keyed on `boxOnly` plus an explicit list rather than a per-car flag, so the specials stay covered automatically as that group changes. Stock and everything else keep theirs.

**F3 JUNIOR's rear was asymmetric, and the cause was structural.** The open-wheel wings are placed at `7 - floor(w/2)` on a 14px grid whose true centre is **6.5**. An even width lands symmetrically — w=10 spans 2–11, centred 6.5. An odd one cannot: w=9 spans 3–11, centred 7.0, one pixel heavier on the right. F3 was the only car with an odd wing (`rearW: 9`), which is exactly why it was the only one that looked wrong.

Fixed by snapping odd widths down to even inside the shared builder, so it also cannot recur for any open-wheel car added later — including through the `|| 11` default, which was the same trap waiting. Verified: **zero asymmetric rows across the entire F3 sprite**, not just the rear.

## 2.238.1 — 2026-09-21 22:50: Batch 459 — Smaller snail, and its trail is actually reachable

**The trail was working — it was unreachable.** Direct report: "I don't see any trail behind it." It shared the air particles' 120 km/h floor, and the speed ramp is `+0.0003`/frame, which puts 120 km/h about **111 seconds** into a run. Almost no run lasts that long, so in practice the trail may as well not have existed.

It has its own floor now at **60 km/h — about 16 seconds in** — reaching full intensity at 160. Verified: 32 trail points at 70 km/h, 36 at 150, spanning 189px. The air keeps its 120 km/h, which was a direct instruction.

**Worth flagging for the same reason: the air particles are also ~111 seconds away.** 120 km/h was your number and it is unchanged, but at the current ramp most runs will end before any air appears. Say if it should come down.

**GIANT SNAIL is smaller**: h 32→28, hitboxW 20→18. Its multiplier follows automatically, ×1.16 → **×1.08**, since the formula reads those two fields directly. Top speed is untouched at 250 km/h.

## 2.238.0 — 2026-09-21 22:30: Batch 458 — Bumper car stopped traffic spawning; bumps now score; empty bar hidden; result-screen wash covers the frame

**Traffic stopped spawning after a couple of bumps.** Direct bug report, reproduced and root-caused. `canSpawnAt()` refuses a lane when a vehicle sits near the top of it — and a **launched** vehicle flies *up* the screen, so its `y` goes small or negative, which is exactly that condition. It also kept its `lane`, so every car you bumped silently reserved a lane for the whole of its arc. A few launches in a row starved the spawner completely, which is why it recovered on the next run.

A launched vehicle is not traffic any more — it cannot be hit, cannot be passed, and is on its way off the screen. It no longer reserves anything, in either the per-lane check or the "don't block every lane" guard. Verified directly: a normal vehicle at the top still blocks its lane, a launched one does not, and **spawning still works with a launched car in every single lane.** Over 1,400 frames with 5 launches, traffic kept arriving throughout.

**Bumps score like a clean jump-over**, as asked — `pts × 2`, the same `jumpMult` `creditVehiclePass()` uses, rather than Shield Bump's ×1.2. XP and coins match the jump-over rate too. This matters more for the bumper car than it looks: launching a vehicle also *removes* it, so there is no second chance to earn the ordinary pass credit from it.

**The ability bar is hidden for cars that have none.** It was already not being painted for them, but the canvas still sat in the HUD as an empty frame, which reads as a bar stuck at zero rather than as a car that simply has no bar. Set once per run in `launchGame()`, since `config.ability` cannot change mid-run. Verified: hidden for GIANT SNAIL, shown for BUMPER CAR, SHIP and Stock.

**The result screen's red wash now covers the whole frame.** It was on `#gameOverHud`, a fixed 506×822 design box scaled by `--hud-scale` — so on a window taller than the scaled box the gradient stopped where the box stopped and raw road showed through above and below. That is the same bug Batch 436 fixed for the menu, in the other screen built on the same fixed-box pattern. The wash moved to `#gameOverBackdrop`, `inset: 0` on the frame itself. Verified at 700×1300.

## 2.237.1 — 2026-09-21 21:30: Batch 457 — Box-exclusives were spawning as ordinary traffic

Caught by eye while checking the snail's trail: a **GIANT DONUT drove past in the next lane**. Box-exclusives are defined by *not* appearing in traffic — that is the entire reason spotting one on the road cannot reveal it.

The spawn pool filtered on `c.rarity` — "has a rarity at all" — rather than on not being box-exclusive. `GARAGE_NPC_RARITY` is the map built for precisely this job and it already excluded them, but **nothing ever read it**. The Batch 405 audit noticed exactly that and left a comment saying so, which is how long this has been live. The pool reads the map now, which fixes the bug and retires the dead map in one move, so there is no longer a second, disagreeing idea of which cars may appear in traffic.

It also closes a hazard Batch 452 introduced without me noticing: `rarity: 'special'` has no entry in `RARITY_SPAWN_WEIGHT`, so the old line was computing `undefined / rareLaneFactor` — **NaN** — as a spawn weight for all six.

**My earlier verification was worthless, and worth saying why.** When these cars were added I checked that none appeared in `GARAGE_NPC_RARITY` and reported them as excluded from traffic. That tested the map, not the behaviour — and the map was the part nothing used. Re-verified properly this time by spawning **4,000 vehicles through the real `Vehicle` constructor**: 0 box-exclusives, 36 distinct ordinary garage cars still appearing, no NaN weights.

## 2.237.0 — 2026-09-21 21:10: Batch 456 — Paint the GIANT SNAIL and it colours the trail

Snail only, as decided. `paintsTrail` is an **exception** to `noPaint`, not a removal of it: the shell is still fixed art that takes no colour argument, but the trail does take one, so the picker opens and the paint goes somewhere real. Every other `noPaint` car has no effect to colour and stays locked — verified for PIANO, DONUT, BATHTUB, BUMPER CAR and SHIP, and the Tank stays locked too.

**Direct correction accepted: a red trail is not "less turbo" than a blue one — it is a red neon trail.** I had that backwards. What makes something read as neon is one hue plus a white-hot centre, and that holds for any hue. So all three layers derive from the paint rather than being tinted toward blue:

| layer | derivation | example at `#e63946` |
|---|---|---|
| outer bloom | `shade(paint, -0.45)` | `#7f1f27` |
| mid band | the paint itself | `#e63946` |
| hot core | `shade(paint, +0.75)` | `#f9ced1` |

Alphas are unchanged at 0.22 / 0.45 / 0.55, so it stays semi-transparent at any colour and the lane markings still read straight through it.

**The Garage says where the paint goes.** The PAINT heading reads **PAINT · TRAIL** for the snail. Someone recolouring it and seeing the shell not change would reasonably assume the picker was broken; one word prevents that.

## 2.236.1 — 2026-09-21 20:40: Batch 455 — The snail's trail is real; Batch 454's "impossible" was wrong

Direct correction, and it was right. Batch 454 claimed a trail behind the car could not exist and built a halo in its place. **That conclusion came from measuring the player at REST** — y 217 of a 260px canvas, one pixel behind the tail — and generalising from that single number.

The player can drive forward. `PLAYER_MIN_Y` is **40**, so the real vertical range is **177px**, and at the top of it there is **178px of open road** behind the snail. The trail was never impossible. It is also better than a static effect would have been, because it only appears when you push forward — rewarding the aggressive position the game already wants to encourage.

Measured after the fix: driven to y=40 at 238 km/h, the trail holds **27 points spanning 180px**, with 11 distinct x values through a lane change — it curves where you moved rather than sliding across as one rigid ribbon. That comes from it being road-anchored: each point is laid at the tail and then scrolls with the asphalt, so it stays where it was put.

**Glowing but semi-transparent**, as specified: three stacked layers per point — a wide dim outer bloom at 0.22 alpha, a mid band at 0.45, and a bright core that only survives the first third. No layer is opaque, so the lane markings read straight through it.

The halo stays on the snail itself — in the film the shell lights up as well as trailing — but is now much fainter, since the trail carries the effect.

## 2.236.0 — 2026-09-21 19:55: Batch 454 — GIANT SNAIL turbo glow

The Turbo reference, built in the space that actually exists.

**A trail behind the car is geometrically impossible here**, and that is measured rather than assumed. The player sits flush against the bottom of the canvas: `player.y + player.height` is **259 of a 260px canvas**, so there is exactly **one pixel** of road behind the tail.

The first attempt did build a proper road-anchored trail, and it worked exactly as designed — which is how it ended up holding 2 points and spanning 7px. Every point scrolled off the bottom edge within two frames of being laid. No amount of tuning fixes that; there is nowhere for a wake to go.

So this is the other half of the same reference — in the film the snail's whole shell lights up blue:

- **A halo around the snail**, three rings stepping outward and down in alpha, pulsing gently so it reads as energised rather than as a flat outline. Drawn row by row with the ends pinched in, not as `fillRect`s: a rectangular halo around an oval snail reads as a *selection box*, which is exactly what the first version looked like on screen.
- **Streaks down each flank**, spawning at the nose and running past the car. They occupy the full 42px of the snail's own height — the one stretch of screen that is reliably available — and read as the road rushing past.

Same 120 km/h floor as the air particles, so a slow snail is just a snail and the glow specifically means speed. Verified: 0 pixels drawn below the threshold, ~2,300 and 6 live streaks at 237 km/h.

**If a trail behind the car is wanted for real, the player's resting position has to move up the screen first** — that is a gameplay change, not an effects one, so it was not done here.

## 2.235.1 — 2026-09-21 19:20: Batch 453 — The SHIP can ram with the sides of its bow

Direct report, and a real bug. A ram kill needs `isFrontHit()`, which asks for **50% horizontal overlap** — measured against the hull's full 22px width. The ship has a pointed bow, so catching a car on the *side* of that point produces a small overlap, failed the test, and fell straight through to the crash branch. You rammed with the front of the ship and died for it.

`ramFrontOverlap` lets a car lower that bar; the ship uses **0.05**.

That is not "any contact anywhere", which would have been wrong for a 60px vehicle — a car merely alongside the hull is not being rammed. This test is only ever reached together with `ramGuardContact()`, which already requires the target to be within the guard's reach of the player's **front edge**. Front-proximity is still fully enforced; what is relaxed is how square-on the hit must be, which is exactly what a pointed bow changes.

Verified, and verified as scoped: the ship crushes both square-on and at 42% off-centre and survives both, while Road Train still crushes square-on and still dies on the same glancing hit. Nothing but the ship changed.

## 2.235.0 — 2026-09-21 19:00: Batch 452 — Box-exclusives get a real SPECIAL rarity, and state their coin bonus

Direct request. All six now carry `rarity: 'special'` instead of borrowing RARE / EPIC / LEGENDARY, so the card badge and the section header finally agree. Three things had to follow it rather than being left to fall through a default:

- **Duplicate compensation** got its own tier at **750,000**, above legendary's 500,000. Without it these would have fallen to the generic `common` fallback and refunded 50,000 — a fifteenth of what a duplicate legendary pays, for a strictly rarer car.
- **The box roll's rarity weighting is now explicitly a uniform pick.** `CAR_RARITY_WEIGHTS` chooses a tier and then filters the pool by it; with every box car on one tier that filter could only ever come back empty and fall through to the whole pool. Saying so outright beats leaving a weighting step that silently does nothing.
- **The Stats collection panel corrected itself.** It counts cars *spotted* per rarity, and box-exclusives were padding those totals with six cars that can never be spotted — they are excluded from traffic by design. It now reads **6 / 52** rather than 6 / 58.

**The coin bonus is visible**, on the hover card directly under the ability line — which is exactly what it compensates for. GIANT DONUT reads `ABILITY: NONE` / `COINS: +75%`. SHIP reads `ABILITY: SHIELD BUMP` with no coin row, because it has an ability instead and that is the whole trade.

## 2.234.3 — 2026-09-21 18:40: Batch 451 — BUMPER CAR bumps with every side, and stops paying close calls for it

**Every side, not just the nose.** Direct correction — the `isFrontHit()` gate is gone. A real bumper car is ringed in rubber, so restricting the launch to the front was the wrong instinct. Two gates remain: the bar must be **full**, and ambulances stay exempt for the same reason ramming spares them. Verified from all four sides — front, rear, left and right all launch, and the player survives each.

**No close call for a car you just launched.** This became a real problem the moment every side could bump: a launched car spends its first frames sliding away through exactly the "real gap, no overlap" band a close call looks for, so it paid a near-miss bonus for a hit you had *already* been rewarded for. Verified zero close calls credited across a full launch and the whole flight that follows.

## 2.234.2 — 2026-09-21 18:25: Batch 450 — Every car states its ability on the hover card

Direct request. The row used to appear only for ram cars, which made JUMP look like "no ability" rather than the default it is, and left the ability-free special vehicles saying nothing at all — when having none is their entire identity.

Every car now shows one: **JUMP**, **SHIELD BUMP**, **TANK SHOOT**, **BUMPER LAUNCH**, or **NONE**.

It reads from a single `carAbilityLabel()` that mirrors the exact precedence `launchGame()` uses to set `config.ability`. That matters more than it looks: if the label and the config ever disagreed, the card would be lying about the car. Verified they agree for all five cases — `stock: jump/JUMP`, `tank: ram/TANK SHOOT`, `roadtrain: ram/SHIELD BUMP`, `ship: ram/SHIELD BUMP`, `bumper: launch/BUMPER LAUNCH`, `snail: none/NONE`.

## 2.234.1 — 2026-09-21 18:10: Batch 449 — Air particles rebuilt; both reported faults were real

Direct report: "they go in single lines, they should go random", and "at 50 kilometers this air was spinning so much it looked like crazy". Both were mine, and both had a specific cause:

1. **Lines.** Batch 446 drew the doc's 32×32 tile repeatedly across the road, re-seeding the same `rng(21)` for every tile. Identical seed means identical x positions, so all ~9 tiles across the road put their particles in the same 15 columns. That reads as vertical stripes, not as air.
2. **Spinning.** It advanced the particles by `roadOffset` — which is a *wrapping* value, not a per-frame delta. Every wrap teleported every particle. Multiplying that by a speed factor and taking `% 32` turned it into constant jitter, and it was worst at low speed where there was no real motion to hide it.

The tile is gone. Particles are now a single persistent field over the road, each with its own x, length and speed multiplier, advanced by the **real per-frame distance**. Nothing repeats and nothing teleports.

**Speed gating is in km/h now, as asked.** Nothing at all below **120 km/h**, ramping to full density at 200 so a 250 km/h car does not white out the road. Measured: 50/90/119 km/h → 0 particles; 120 → 1; 140 → 46; 170 → 118; 200 → 173; 250 → 178 (capped). Ramming adds +45 km/h to what the air sees, so a ram at 140 draws 147 instead of 46. At 180 km/h a particle advances 12.45px per frame, smoothly.

## 2.234.0 — 2026-09-21 17:05: Batch 448 — Box-exclusives get their own SPECIAL section, and plain "???" tiles

Direct correction: they were supposed to be their own section all along, not scattered through the rarity tiers by whatever rarity they happen to carry.

**SPECIAL, after LEGENDARY.** Grouped by the `boxOnly` flag that already exists rather than by a new rarity value, so nothing had to be stored on the cars themselves. `RARITY_INFO.special` is a header entry only — no car carries `rarity: 'special'`.

They keep their real `rarity`, and the per-card badge still reads RARE / EPIC / LEGENDARY. That is deliberate: rarity is what sets a duplicate's refund rate and which DROP CHANCES row a car sits in, so hiding it would lose real information. **The section tells you how you get them; the badge tells you how likely it is.**

Sorted by name inside the section, not by price — a box-exclusive has no `unlock`, so the usual price comparator would have compared `undefined` with `undefined` and left them in whatever order the roster array happened to use.

`boxLast` is also gone from the rarity sections' comparators. It existed to push box-exclusives to the end of whichever tier they landed in, and there are none left inside a tier for it to push.

**The crate art is gone.** An undiscovered box-exclusive now shows the same plain "???" tile every other undiscovered car uses, per direct request. That removed the last user of `.car-tile-crate-locked`, so its three orphaned CSS rules went too.

One thing that had to change with it: the "???" tile's tooltip said "Find this car on the road to unlock it", which is a straight lie for these — `boxOnly` cars are excluded from NPC traffic, so no amount of driving will ever reveal one. Box-exclusives now get "Win this one from an Extra Box to find out what it is".

Verified: section order reads COMMON / RARE / EPIC / LEGENDARY / SPECIAL, zero crate tiles remain, undiscovered box-exclusives render as "???", and discovered ones show their real card with its rarity badge intact.

## 2.233.0 — 2026-09-21 16:20: Batch 447 — BICYCLE, FISH and COUCH removed

Direct decision. The three hand-drawn special vehicles from Batch 443 are gone, leaving the roster at **58 cars — 52 buyable, 6 box-exclusive**, all six of those transcribed from the user's own v4 doc. COLLECTOR's amethyst tier follows automatically: 61 → 58.

Removed their three `drawGarage*53` functions (~6,200 characters of sprite code), their roster entries, and reworded the two comments elsewhere that named them. Nothing else referenced them.

**A save could still be carrying one.** They were winnable from Extra Boxes for four batches, and `ownedCars.length` is exactly what COLLECTOR counts — so a player who won a couch would have kept being counted one car closer to the 58-car amethyst tier than they really were, permanently, with no way to notice. A one-time prune now drops any owned-car key that no longer names a real car. It runs at startup, only writes when it actually removes something, and protects every future removal for free rather than being specific to these three.

It has to sit below `GARAGE_CARS`, not next to the save load where it naturally belongs: `GARAGE_CARS` is a `const` declared much further down the file, so reading it from the load block is a temporal-dead-zone crash on boot. Caught before it shipped.

Verified: 58 cars, the six box-exclusives intact, a save naming a deleted car prunes it on load, `getSelectedCar()` falls back to Stock if the *selected* car was one of them, and both the Garage grid and a launched run build without throwing.

## 2.232.0 — 2026-09-21 15:40: Batch 446 — Speed air particles, the SHIP's invisible ram, the BUMPER CAR's launch, and coin bonuses

**Ambient road air.** Ported from `_archive/Shield Bump Storyboardv2.dc.html` section 9, AMBIENT ROAD AIR: a 32×32 tile of 15 particles — single motes and 2-4px streaks, about a third warm dust rather than white air — that wraps on all four edges so it repeats across the road without seams. The doc's own `rng(21)` and its alpha quantiser are unchanged, so the particles land where the doc put them.

What is *not* from the doc: it plays this as a fixed 4-frame loop and only suggests "drop the alpha or the particle count on slower roads". The request was that speed drives it, so **count, alpha and scroll rate are all functions of `speedRatio01()`**. Measured pixels drawn per frame: 30% speed → 0, 35% → 27, 50% → 144, 70% → 302, 90% → 679, full → 718. Below 35% nothing draws at all — at a crawl, visible air reads as drizzle rather than speed.

**Ramming drives it too**, per the request that the particles fire "when using the RAM ability, because that creates a feeling of speed". A ram at half speed now puts down 698 pixels against 144 without it — near top-speed air from a mid-speed run, which is the point.

**SHIP: rams with no ram.** Direct spec — "it wouldn't display the RAM, but it would still give the air particles, and you could just RAM with the ship". `hideRamGuard` drops *every* cue: thruster plume, the projected guard through all three phases, and the air ripple. The ability, its hitbox reach, its speed boost and the air boost are all untouched. The check sits above the plume on purpose — a rocket exhaust under a sailing ship reads as a bug just as loudly as an energy shield on its bow. Verified: SHIP draws 0 cue pixels while ramming, Road Train still draws 151.

**BUMPER CAR: LAUNCH.** A fourth ability value, `'launch'`. Hit a car with a full bar and it is thrown off the screen — spinning, shrinking and fading on its own arc, the only vehicle in the game ever drawn rotated. The bar empties and refills over **5 seconds**; hit something before it is full and you simply die, exactly as specified.

It cannot be triggered by a key, and that is enforced structurally rather than by a guard: `startAbility()` only has branches for `'jump'` and `'ram'`, so a third value means the ability key does nothing at all, with no extra condition to keep in sync. Three gates decide a launch — the bar must be **full** (all-or-nothing, not merely charged), it must be a **front** hit, and ambulances are exempt for the same reason ramming spares them. Any gate failing falls through to the ordinary crash branches.

**A bug caught in testing, and it was mine.** The cooldown was being topped up by passing traffic, because the ability bar's normal refill is "+1 cell per car passed". So on a busy road the launch came back early and on an empty one it did not — precisely the dependence on traffic that a flat timer exists to remove. Passing refill is now skipped for `'launch'` and `'none'` cars. Verified: the bar reads 20/40/60/80/100 across five seconds regardless of traffic.

**The other seven special vehicles have no ability, and earn more instead.** A jump would hand them thruster flames that assume a car silhouette and a flat underside; a donut with rockets under it reads as broken art, not as a gag. They get `'none'` — which the ability-bar renderer already hid, so the HUD needed no change — and a coin bonus applied to the run payout:

| | bonus | | | bonus |
|---|---|---|---|---|
| GIANT DONUT | +75% | | BICYCLE | +70% |
| GRAND PIANO | +65% | | FISH | +60% |
| BATHTUB | +55% | | COUCH | +50% |
| GIANT SNAIL | +40% | | | |

Scaled against what each already has: the snail is the joint-fastest car in the game and gets the least, the donut is the smallest and slowest-earning and gets the most. SHIP and BUMPER CAR get **no** coin bonus — they have an ability instead, and that is the trade.

These numbers are a judgement call, not a spec. The brief was "some should have more and some should have less"; the floor is deliberately high because jump is a survival tool, not flavour, and +10% would never be worth giving it up.

## 2.231.0 — 2026-09-21 13:10: Batch 445 — Six more special vehicles from "Reckless Vehicles v4.dc.html"

GRAND PIANO, GIANT SNAIL, SHIP, BUMPER CAR, BATHTUB and GIANT DONUT. All `boxOnly`, bringing the roster to **61 cars — 52 buyable, 9 box-exclusive**. COLLECTOR's tiers follow automatically: diamond 52, amethyst 61.

**Transcribed, not redrawn.** Unlike bicycle/fish/couch, the doc ships exact per-pixel SVG paths, so every run was parsed straight out of it — including the black outline, which is why these do not call `sil53()`. The outline is already part of the art.

They are stored as run data rather than ~1,700 `fillRect` lines. The doc's paths are all 1px-tall runs; merging vertically adjacent identical runs into taller rects first took **1,739 runs down to 935**, which matters in a single-file game that is already ~1MB.

**One fixed look each, no repainting** — the direct instruction, "similar to the tank". `carCanRepaint()` used to be a hardcoded `key !== 'tank'` check; it now honours a `noPaint` flag. This goes further than the Tank does: these six draw functions **take no colour argument at all**, so the lock and the art agree rather than the UI merely hiding a choice that the sprite would still have honoured.

**Speeds** — four are direct user specs, and the gag only works if the absurd thing is genuinely quick, so none of them is "realistically" slow:

| | km/h | source |
|---|---|---|
| GIANT SNAIL | 250 | direct spec — joint-fastest in the game, which is the whole gag |
| BATHTUB | 210 | direct spec, explicitly faster than the piano and the donut |
| BUMPER CAR | 200 | direct spec |
| SHIP | 180 | direct spec |
| GIANT DONUT | 175 | my call — it is a wheel, so rolling fast is the one thing it is shaped to do |
| GRAND PIANO | 150 | my call — a concert grand is ~400kg of cast iron, the slowest of the six |

**Multipliers needed no new numbers.** The instruction was "smaller → smaller, long or big hitbox → higher", which is exactly what `vehicleMultiplierBonus()` already computes from `h` and `hitboxW` — and those are the doc's own viewBox, so there is no second figure to keep in sync. Measured: DONUT and BUMPER CAR ×1.03, BATHTUB ×1.11, PIANO ×1.12, SNAIL ×1.16, **SHIP ×1.88**.

**Worth flagging: the SHIP is now the highest multiplier in the game**, past Road Train's ×1.79 and past the ×1.82 that lane × mode can reach between them. Batch 440 deliberately kept the best car just *under* that ceiling so no single lever outweighed the other two combined. A 60px-long box-exclusive breaks that rule by 3% — knowingly, because it follows the instruction that longer vehicles earn more, and because it cannot be bought at any price. Say if it should be trimmed to ×1.79 instead.

Verified: all six render correctly against the doc, none appears in `GARAGE_NPC_RARITY` (box-exclusives never spawn as traffic), none can be repainted while Stock still can, Extra Boxes stay available and still hide themselves once all 61 cars and every gift paint are owned, and both the owned and undiscovered Garage tiles build without a paint argument.

## 2.230.0 — 2026-09-21 02:05: Batch 444 — Three achievements: FULL WARDROBE, FULL CIRCLE, ACT OF GOD

**FULL WARDROBE** (amethyst, one-time) — own every paint colour *and* every booster. The completionist layer over FULL PALETTE, which only ever counted paints. `isFlameUnlocked()` covers both gates a booster can have, the level one and the bought one, so the check is one expression rather than a special case per booster.

PLAN.md had this logged as blocked on the effects system existing, on the grounds that "every cosmetic" is undefined until then. It is not blocked: every cosmetic that exists today is a paint or a booster, and when effects land they get one more `every()` clause and the achievement widens by a line. Verified across four states — everything owned passes; missing Rocket Pods, too low a level for Underglow, or one unowned paint each fail.

**FULL CIRCLE** (secret) — click your level badge and the ring sweeps forward from where it really is, all the way round, and lands back on its real value. `(real + eased) % 1` ends at exactly `real` when the easing hits 1, so it can never settle on a wrong-looking fill.

Two things this needed that were not obvious:

- `paintLevelBadgeAt()` takes an optional `ringPct` that drives **only** the ring. Sweeping it by feeding the function a fake `xp` instead would have made the XP readout count up to a number the player does not actually have.
- The three badges do not share markup. Garage and Stats use `.level-badge-*`, but the main menu's own circle — kept deliberately when the menu was rebuilt from the design doc — uses `.mm-level-*`. The first version only worked on two of the three. The handler now matches both, and `paintLevelBadge()` bails while a spin is running so an unrelated `refreshMenuSummary()` cannot paint over it mid-animation.

**ACT OF GOD** (secret) — click one of the cars driving past in the menu background and it blows up: a flash, an expanding ring of debris that cools from yellow through orange to grey, and the car stays gone for a few seconds before its position wraps around and it returns on its own.

**The cursor never changes over them**, which was part of the original ask — nothing may advertise the cars as clickable. Confirmed `auto` at the hit point.

The listener is on the document, not on `#menuCanvas`. The canvas sits *under* `#menuBackdrop` and `#menuOverlay`, so a click aimed at a background car never reaches the canvas at all — in testing it landed on `.mm-gap`. Hit-testing therefore maps the click into canvas coordinates itself, against the rects the last drawn frame actually used rather than positions recomputed from `t` (which would drift a frame out of step). Clicks on real controls are handed straight back: a demo car drifting behind a button must not swallow the button. Verified — clicking GARAGE while a car sat underneath opened the Garage and left the car intact.

## 2.229.0 — 2026-09-21 01:22: Batch 443 — The special vehicles land: BICYCLE, FISH, COUCH

The three the box system has been waiting on, all `boxOnly: true`. That one flag is the entire wiring — it already excludes a car from NPC traffic, from `canAffordCar()` at any coin total, and from the "own every car" check that gates Extra Boxes. **No other system needed changing**; the mystery tile, the LOCKED marker, the "BOX EXCLUSIVE — NOT FOR SALE" hover line, duplicate compensation and COLLECTOR's amethyst tier all switched back on by themselves. Verified: COLLECTOR now reads diamond 52 (every buyable car) / amethyst 55 (those plus all three exclusives).

**They are legendary, and that does not put a fish in traffic.** The spawn table is built by a loop that skips `boxOnly` outright, so `rarity` on these three only does two things: groups them in the Garage's legendary section, and sets what a duplicate roll refunds — the top rate, correct for the only prizes a box can still give. Confirmed none of the three appears in `GARAGE_NPC_RARITY`. No `unlock` price either: `buildCarTile()` shows LOCKED instead of a price for box-exclusives and the price sort already pushes them last, so a number would never have been displayed.

**Sizes, and what they do to the multiplier:** BICYCLE `h20/w8` → ×0.90, FISH `h22/w12` → ×0.97, COUCH `h18/w20` → ×1.00. All three sit inside the existing ×0.83–×1.79 spread from Batch 440, so none is a stealth upgrade — a special vehicle is a novelty, not a reward for winning one.

**The sprites are hand-drawn, not shells.** `bodyShell53`/`bodyShellW53` draw a *car* — headlights, taillights, a windscreen — and inheriting a windscreen is exactly what would make a fish read as broken rather than funny. All three use `sil53()` for the same black outline every other vehicle gets and nothing else. Two were redrawn after looking at them:

- **The couch** came out as a striped box. The arms were only shaded -.12 against the cushions, and a couch from above is read almost entirely through contrast between solid mass and the lit hollow between it. Arms and back went to -.38 with a lit crown; now the three cushions and the rear backrest are legible.
- **The bicycle** was a dark smudge — a 2px frame tube left almost no painted surface, so the player's chosen paint barely appeared. The frame is 4 wide through the middle now.

**A real bug this exposed, and it was mine.** `extraBoxCanStillGive()` (Batch 440) asked `boxExclusiveCars().length > 0` — "do box-exclusive cars exist". That was only ever correct while the list was empty. The special vehicles made it permanently true, so boxes would have stayed on sale forever, including to a player owning all 55 cars and every gift paint: the exact guaranteed-loss the function was written to prevent, relocated to the endgame. It now asks whether a box can give something you do not already **have**.

Verified across four states: all 52 buyable cars owned → boxes available; only the fish missing → available; literally everything owned → hidden; ordinary save → available.

## 2.228.2 — 2026-09-21 00:34: Batch 442 — Menu tabs reordered; a hook that mutes the game before testing

**Tab order, by direct request:** GARAGE / SCORES / STATS on the top row, GIFT / AWARDS / MISSIONS on the second. Only the six buttons in the main grid moved; SETTINGS and TUTORIAL keep their own row underneath.

Each button carries its own `--tab-c`, so the colours travelled with them — and they happen to land in clean columns: mint (GARAGE, GIFT), amber (SCORES, AWARDS), blue (STATS, MISSIONS). Nothing was recoloured to get that.

**A hook now fires whenever the game is opened for testing.** `.claude/settings.json` + `.claude/hooks/mute-carcrash.py`, on `PreToolUse` for the browser's navigate / preview_start / batch tools. It hands back the mute snippet as context at the exact moment the game is opened.

Scoped on purpose: those browser tools get used for docs and unrelated sites too, so the hook only speaks up when the target is actually this game — `carCrash`, the `car-crash` launch entry, or the dev server's port 8420. Anything else and it prints nothing and blocks nothing. Verified against all three cases, then confirmed live on the next real navigate.

A hook cannot run JavaScript inside the page, so this is a reminder rather than an enforcement. The airtight version would be the *game* muting itself when it sees it is being served from the dev port — say so if that is wanted; it is two lines, but it puts test-only behaviour into the shipped file, which is why it was not done unprompted.

## 2.228.1 — 2026-09-20 23:58: Batch 441 — Menu icons replaced from "Icon Set FINAL.dc.html"

Six of the eight menu icons swapped for the final set: **GARAGE** (car front), **SCORES** (crown), **AWARDS** (chevrons), **MISSIONS** (checks), **GIFT** (box) and **SETTINGS** (sliders). Paths copied verbatim from the doc rather than redrawn.

**STATS and TUTORIAL are untouched, because the doc's versions are byte-identical to what the game already ships** — exactly the "some are the same as now" in the request. The script asserts both are still present rather than assuming it, so a future edit that changes either will fail the build step loudly instead of silently diverging.

The new icons use a **12x12 viewBox**; the old set and the two unchanged ones are 8x8. That is fine to mix, but it made the render size wrong: the tiles drew every icon at **18px**, which is 2.25x for an 8px grid and 1.5x for a 12px one — neither a whole number, so pixel edges were landing between device pixels and `shape-rendering="crispEdges"` was quietly papering over it. The doc itself draws them at **24px**, which is exactly **2x** for the new icons and **3x** for the two 8x8 ones, so the tiles now use 24px too and both grids land on whole pixels.

(On screen the final size is 24 x the menu's own `--ui-scale`, since the whole menu scales to the window — but the design-space ratio is what determines whether the art is drawn on a whole-pixel grid, and that is now exact.)

Verified: all eight tabs render, the two 8x8 icons still measure a 3x ratio and the six new ones 2x, the menu still fits its frame and the footer stays inside.

## 2.228.0 — 2026-09-20 22:18: Batch 440 — Jump costs 30% less, Extra Boxes stop selling losses, car multipliers rebalanced

**Jumping uses 30% less energy.** `JUMP_FULL_DRAIN_MS` is the time to drain a FULL bar held continuously, so less energy per millisecond means a *longer* number: 3200 → 4571. A full bar now buys ~4.6 seconds of flight instead of ~3.2. Take-off still needs 3 cells — that is a threshold, not a cost, and was not part of the ask. The tutorial quoted "3 seconds" as prose; it now derives the figure from the constant, so this cannot go stale again.

**Extra Boxes were quietly selling a guaranteed loss, and that traces back to Batch 422.** A box rolls from the word pool — coins, XP, a gift paint, or a box-exclusive car. Making every car buyable emptied the car tier *and* pushed the unlock from "own all 39 buyable cars" to "own all 52". So boxes only appeared once you owned everything, by which point the pool was usually just coins and XP, and a box costs more coins than it tends to return.

Fixed by gating on whether a box can still give something you do not have: an unowned gift paint, or a box-exclusive car existing. Both the buy path and the panel check it, so the boxes hide themselves when pointless and come back on their own the moment the special vehicles land with `boxOnly` set. Verified: everything owned with no exclusives → panel hidden and `buyExtraBox()` refuses; one missing paint → available; a flagged exclusive car → available.

**Car multipliers rebalanced.** The ask was "the lowest should be 1x or below, go-kart below 1x, no unnecessarily big mults, and check lanes/mode aren't worth more than the best car". Three changes, one per part:
1. The base is **1.0, not 1.3** — a reference 24x14 car (Stock) is now exactly x1.00 instead of collecting +0.3 for existing.
2. The length term is **signed**. `Math.max(0, ...)` meant nothing shorter than 24px was ever penalised, so a Go-Kart and a Stock car differed only by width — which is why no car could go below 1.
3. The curve constant is **0.45, not 0.6**, landing the longest car at x1.79 — deliberately just under lane x mode's own 1.82 ceiling, so no single lever outweighs the other two combined. That was the comparison asked for.

Measured before and after: **x1.24–x2.36 (everything above 1) → x0.83–x1.79, Stock exactly x1.00.** Go-Kart x0.83, Jet Bike x0.90, Road Train x1.79.

**The 1.0 floor in `calculateMultiplier()` had to go with it.** It existed so *settings* could never punish you, which is still true — lane and mode multipliers are both >= 1.0. But the car term is now deliberately allowed below 1, and the clamp would have silently erased exactly the penalty being asked for: a Go-Kart on 10 lanes / SAFE computes x0.825 and was being rounded back up to x1.00. Verified it now reports 0.825.

**Worth flagging: this is a real nerf, roughly 25% off the car term across the board.** Score and coins both scale with the multiplier, so earning slows by about that much, and the score-based achievement ladders (SCORE CHASER and friends) were calibrated against the old numbers. That interacts directly with the economy rework still sitting unbuilt in PLAN.md — if that gets picked up, these two should be tuned together rather than separately.

## 2.227.1 — 2026-09-20 21:36: Batch 439 — Setup confirms a same-version re-install; PLAN.md tidied

**The installer now asks before re-installing the version you already have.** It already read the installed `DisplayVersion` and relabelled its button "Re-install" in that case, but a label is easy to skim past when nearly every other run of that exe is a genuine update. Running an installer kept from a previous update, or double-clicking twice, now gets a plain "this is the same version, not an update — do it anyway?" with **No** as the default. Checked at click time rather than when the window opened, since the install can change while the window sits there.

An update and a first install are untouched: neither asks. Verified all three paths — same version asks once and answering No does not start the install; an older install and a fresh machine both proceed straight through.

One self-inflicted detour worth recording: the first version of that dialog string was written by a script and its `\n` escapes came through as **real newlines**, producing an unterminated f-string that would not parse. The repaired version builds the blank line from a `NEWLINE` constant instead, so the source survives being edited by scripts. `ast.parse()` now runs over setup.py as a check.

**PLAN.md tidied** — four entries were describing work that had already shipped: the per-tab icons and colours (Batch 426), moving LANES/DIFFICULTY onto the menu (426 + 432), the HOW TO PLAY screen (397-437, only its "did you know?" tips remain and are tracked separately), and a duplicate of the already-fixed word-truck icon (410). Together with the 14 achievement entries closed in Batch 438, the open count is down from 88 to 70.

## 2.227.0 — 2026-09-20 21:05: Batch 438 — Eight new achievements (48 → 56)

Worked the backlog of specced-but-unbuilt achievements. **Most of that list turned out to be already built** — checking before writing saved eight duplicates: "spot a car crash" is NOT MY FAULT, "shoot the ambulance" is CEASE AND DESIST, "die with zero score" is DIDN'T EVEN TRY, "crash on an obstacle" is YOU CAN'T PARK THERE SIR, "ram 20 in one ramming" is CHAIN REACTION, and the Missions and player-level ladders are TASK MASTER and CLIMBING THE RANKS. Eight were genuinely missing.

**Three tiered:**
- **LANE HOPPER** — lifetime lane switches, 100 / 500 / 2000 / 10000. Deliberately distinct from the SERPENTINE secret (20 switches inside 5 seconds): the same action, but one measures a habit and the other a burst.
- **ROAD TRIP** — lifetime distance, 25 / 100 / 500 / 2000 km. **Tiers set from a measurement, not a guess**, as the plan entry insisted: eight sampled runs averaged 0.49 km over 28 seconds (~71 km/h), so bronze is about a first session and diamond a long-term total.
- **WORDSMITH** — different Daily Words completed, 5 / 15 / 28 / all 40. Built tiered rather than as a one-time with a progress bar, because tiered rendering already draws progress and the alternative meant a new render path for one card.

**Three one-time:** NOTHING LEFT HIDDEN (amethyst, every secret found), PERFECT DAY (gold, gift + word + all six missions in one day), NOTHING TO SEE HERE (silver, jump clean over a breakdown).

**Two secrets:** SOUND OF SILENCE (master volume to zero) and DOUBLE SHIFT (two ambulances on the road at once).

**Four of them needed tracking that did not exist.** `wordsCompleted` is only a count, so it cannot answer "have you done all of them" — added `wordsSolved`, the actual set. A breakdown is a `Vehicle` like any other, so the existing jump-clear counter cannot tell one apart — added its own. And nothing measured distance at all, so `totalDistanceKm` integrates `speedToKmh()` per frame, the same figure the HUD shows, so the achievement agrees with what the player was watching rather than keeping a private idea of speed.

NOTHING LEFT HIDDEN and PERFECT DAY are **derived live** rather than event-unlocked, because both are statements about other state and computing them cannot fall out of sync. PERFECT DAY latches itself once true, so tomorrow does not take it back.

Verified each firing: volume to zero unlocks; two ambulances on screen unlocks; a real held jump over a breakdown counts 1 and unlocks at the run rollup; distance accrues at 0.014 km/s at the 50 km/h start speed (exactly right); PERFECT DAY and NOTHING LEFT HIDDEN both evaluate true once their conditions are met. 56 achievements total, no duplicate ids, no console errors.

Two test-harness notes, both the same trap and both worth remembering: setting `player.abilityState = 'jumping'` and calling `loop()` does nothing, because `player.update()` runs first and clears it when no key is held — a real `keydown` is required. And any test that reads a tile's or panel's *text* to detect a state change will report false positives, because the text legitimately changes.

## 2.226.0 — 2026-09-20 20:12: Batch 437 — Road markings, Garage sorting and filtering, Daily Word claim step

**The grey stripes joining the lane dashes are gone.** `makeAsphalt53()` painted a continuous 1px `#44484f` line down every lane boundary, and the white dashes are drawn on top of it at the same x — so between dashes that line showed through as a stripe connecting them. Real lane markings are separate dashes with bare tarmac between. Verified: zero pixels of that colour remain in the asphalt buffer.

**Equipped now beats "newly discovered" for a Garage tile's frame.** The two rules sat in source order, so a car still flagged NEW kept its red frame after being bought *and* equipped. The NEW rule is now `:not(.equipped)`, so green wins — equipped is the stronger fact about a car. The NEW! tag itself still shows until the Garage is next exited, which is unchanged.

**Buying a car no longer teleports it to the top of its rarity.** TIER mode sorted owned cars ahead of unowned within each section, so the position you had just learned for a car changed the moment you bought it. Now purely price order, which is stable. This reverses the older "bought cars always in front" request — the roster is small enough to scan, and the disorientation costs more than the convenience gained.

**New OWNED tab** beside TIER / ABILITY / PRICE: the same rarity grouping, limited to cars you actually have. Tiers with nothing owned are skipped entirely rather than left as empty headers, so it reads as a collection rather than a mostly-blank grid. The choice persists like the other three.

**The Daily Word has a claim step now**, matching the Daily Gift. Completing a word used to drop you straight onto the finished reward with nothing to open. The solved word now shows a **CLAIM REWARD** button and only reveals what you won once pressed.

The reward is still *rolled* the instant the word completes on the road — that has to stay, it is what makes the reward survive leaving the screen (Batch 163's whole reason for persisting it). The new `revealed` flag gates only the display, and it lives on the persisted `pendingWordReveal`, so closing the game mid-claim leaves the reward waiting to be opened rather than silently spent.

Verified each: lane-boundary pixels 0; an equipped-and-new tile computes to `rgb(46,230,176)`; buying HOT HATCH leaves it at index 2 with the whole order identical; the OWNED tab shows 3 tiles under COMMON and RARE only; and the word card shows a claim button with the reward hidden, then the reward with a close button, then clears.

## 2.225.2 — 2026-09-20 19:44: Batch 436 — The bright strips down the menu's sides, and more bottom room

**The light lines either side of the menu were a regression I introduced with scale-to-fit.** The dark wash over the road lived on `#menuOverlay`, which was `inset: 0` and therefore covered the whole frame. Batch 433 turned that element into a fixed, centred 440-wide design box — so the wash shrank with it and stopped covering the frame's edges, leaving the raw road verge showing through at full brightness. Measured: the overlay rendered 536px wide in a 577px frame, leaving exactly 20px uncovered on each side, which is what those strips were.

Fixed by separating the two jobs: `#menuBackdrop` is a new full-frame `inset: 0` layer that carries the gradient and does not scale, and `#menuOverlay` keeps only the scaled content. Verified the backdrop now matches the frame exactly and the overlay has no background of its own.

**More bottom room**, as asked: design height 760 → 812 and the footer spacer's floor 24 → 44. That gives 74 design px between the last tab row and the footer (was 24) and 26px below the footer. The 119px road gap under the level badge is again untouched — same reasoning as last batch, the space came from the box rather than from a gap that was deliberately sized.

Worth noting for the next time this screen is measured: the dev server's page was being served from cache during verification, and `getElementById` returned null for an element that was demonstrably in the file. A `?cb=` query on the URL forced the fresh copy. Same class of problem as the packaged app's cache issue in Batch 423.

## 2.225.1 — 2026-09-20 19:20: Batch 435 — Menu: breathing room at the bottom

Direct report on the scaled menu: the tab rows sat hard against the bottom edge, which read worse than the pre-scaling layout did.

Fixed by giving the design box more height rather than by moving things around inside it — **715 → 760** — plus 10px more bottom padding on the overlay and a 24px floor on the spacer above the footer. The result: 24 design px between the last tab row and the footer, and 23 below the footer before the frame edge.

**The 119px road gap is untouched.** It would have been the easy place to take the space from, but that gap is the size that was specifically asked for (matching the lanes + mode block), so the room came from the box instead. The cost is about 6% of scale, since height usually binds — which is the "make it a bit smaller" half of the trade-off, chosen deliberately over rebalancing a gap that was already settled.

## 2.225.0 — 2026-09-20 19:02: Batch 434 — The result screen and pause panel scale to fit too

Completes Batch 433: every surface inside the game frame now holds one layout and scales, rather than reflowing.

Both panels are laid out at **506x822** and scaled by the existing `--hud-scale`. That size is not arbitrary — 506 is `HUD_SCALE_REFERENCE_WIDTH`, the width at which `--hud-scale` is exactly 1, and 822 is 506 x 260/160, the canvas ratio. So the panels sit at native size when the frame is at its reference width and track it exactly either side of that, using the same variable the HUD chips already use.

**The page-scroll safety net on the result screen is gone**, and it should be: it existed because the panel could outgrow its frame, which a fixed design box cannot do. `#goAchBox` still scrolls internally, because the achievement list is genuinely unbounded and that is the right place to absorb it.

**One real bug fixed in passing.** `#goAchBox` capped itself at `max-height: 34vh` — a *viewport* unit. Inside a fixed 822px design box that measures against something with no relationship to the panel it sits in, so the same panel would have reserved a different share of itself on every screen. Now 280px, the same proportion of the design height that 34vh was of a typical window.

Verified at a 440x560 window — small enough that the old layout was in trouble: the panel renders at 269x437 inside a 286x517 frame with every element present (title, score, all five stat rows, the achievements box with both its COMPLETED and PROGRESS sections, and all three buttons), nothing clipped, nothing page-scrolling. Both panels measure 506x822 at design size and fit the frame at the tested window sizes.

## 2.224.0 — 2026-09-20 18:44: Batch 433 — Scale to fit: the menu and the gameplay screen hold one layout at every window size

**The menu is now laid out once at a fixed design size and scaled as a whole.** 440x715 — exactly the canvas's own 8:13 ratio, so a single factor covers both axes and the overlay always lines up with the frame. `sizeMenuFrame()` computes `min(clientWidth / 440, clientHeight / 715)` and the overlay carries it as a CSS variable.

This **removes** machinery rather than adding it. The road gap no longer has to flex between 14 and 119px hunting for a fit — the design height is fixed, so it is simply 119px. None of the size-trimming from Batch 426 is doing any work any more either.

Measured across the full range, including the exact window from the report: at **420x520**, which previously left the content needing 529px in a 477px frame with the footer 132px outside, the menu now renders at scale 0.667 entirely inside the frame, footer included. Verified fitting at every size from 380x460 (scale 0.64) up to 1280x1000 (scale 1.30).

One correction during the work: the first version measured `getBoundingClientRect()` on the container and overflowed by 3px. The overlay is positioned inside the container's **padding** box, and the frame's outer ratio is not the canvas ratio anyway — `sizeFrame()` adds a fixed 20px of chrome to both axes. Switched to `clientWidth`/`clientHeight` and checked both axes independently rather than assuming one binds.

**Gameplay already had most of this and I nearly rebuilt it by hand.** `sizeGameFrame()` has set a `--hud-scale` since an earlier batch, driving `#hudLeft` and `#gameHud`. Two real gaps, both now closed rather than replaced:
- It was capped at `min(1, ...)`, so the HUD shrank on a small window but never grew on a large one — the chips crept smaller relative to the road the bigger the window got. Uncapped, gameplay holds one set of proportions at every size, the same rule the menu now follows.
- `#crashSkipHint` and `#fpsCounter` were never wired to it and kept a fixed pixel size while everything around them scaled. Both now ride the same variable.

Verified in a real run: `--hud-scale` reads 0.968 at a 490px frame and exactly 1.000 at the 506px reference, with the road, dashes, traffic and chips all rendering correctly.

**Still reflowing rather than scaling: the result screen and the pause panel.** Both are scrollable panels with their own max-heights, and transform-scaling a scrolling element scales its scrollbar and its wheel distances with it, which is its own problem. They adapt by scrolling today and that is left alone deliberately — flagged rather than quietly half-done.

## 2.223.0 — 2026-09-20 18:02: Batch 432 — LANES and DIFFICULTY removed from Settings; app minimum window size

**Settings no longer carries ROAD LANES or DIFFICULTY** — both moved onto the main menu in Batch 426, and keeping a second copy meant two places to change the same thing.

The two hidden `<select>` elements (`#laneCount`, `#difficultySetting`) **stay exactly where they were in the DOM**. They are not leftovers: they are the single source of truth that the menu's lane track and difficulty tiles write into, and that `calculateMultiplier()` and `launchGame()` read. Only their Settings UI is gone.

Everything orphaned by that removal went with it, rather than being left dangling: the `+/-` lane stepper and `updateLanesUI()`, the `bindSeg()` call for the difficulty segment, the six element lookups, and the two per-row `x MULT` labels `calculateMultiplier()` used to write (the menu now shows each contribution on the control itself — the lane track, the difficulty tiles and START RUN). Zero references to any of them remain.

Verified end to end: setting 7 lanes and SUICIDAL from the menu produces `x1.91`, Settings opens with 13 rows and no mention of either setting, and launching a run carries `config.lanes = 7` / `config.difficulty = suicidal` / `baseMultiplier = 1.91` through unchanged. A clean 5,400-frame run at 9 lanes / SUICIDAL threw nothing.

**The app now has a real minimum window size**, derived from measurement rather than guessed. The menu's content is ~529px tall and the frame is aspect-locked to the canvas (160/260), so height is the binding constraint: a 700px window leaves a ~657px frame, which clears 529 comfortably. The floor is now **480x700**, replacing (900, 640) — that one was wider than necessary (at that height the frame is only ~380px, so the extra width was empty margin) while being short on the axis that actually matters.

This is a floor, not a fix for the underlying behaviour: everything inside the frame is still fixed pixels, so it cannot cramp gracefully, it can only fit or clip. Reproduced at 420x520 — the frame was 300x477, the content needed 529px, and the footer landed 132px outside the frame. The scale-to-fit approach that would actually solve it is described in the reply and is waiting on a go-ahead.

## 2.222.0 — 2026-09-20 17:14: Batch 431 — Traffic, crashes, letters and the road surface

Eight reports in one pass.

**Ambulances were genuinely too frequent at high lane counts, and not for the reason the code assumed.** The per-frame odds are already lane-independent (Batch 213 fixed that), but the *conversion* was not: once a roll succeeds the code commits and retries every frame until a free lane appears. At 7-9 lanes a free lane is found instantly so nearly every roll becomes a real ambulance, while at 3-4 lanes rolls sat waiting — and a waiting roll blocks new ones. Identical odds, very different felt rate. Fixed with a real floor on the spacing (`AMBULANCE_MIN_GAP_FRAMES`, 20s) plus a lower base rate (0.02 → 0.012). Measured over 3 simulated minutes: 1-3 ambulances, where before the rate was uncapped.

**The first wave arrived in formation** because every vehicle spawned at exactly `-height - 10`. On an empty road — i.e. the opening seconds, when nothing blocks a spawn — consecutive spawns entered level with each other and read as a wall. Spawns now carry up to 46px of upward jitter (upward only, so it can never eat the clearance `canSpawnAt()` just checked). Sampled spawn depths went from identical to −90, −60, −50, −36, −6, 0.

**NPC crashes are much rarer, and now they have a cause.** Previously *any* same-lane overlap wrecked both cars, so more lanes meant more traffic meant constant pile-ups. Rather than suppressing the collision, most drivers now **brake**: when the car behind closes on the one ahead in its lane it matches pace. Only an inattentive minority (`NPC_INATTENTIVE_CHANCE`, 10%) fail to, and those are the crashes. Verified per-case: an attentive driver's speedOffset goes 5 → 0 at a gap of 8px and no crash follows; an inattentive one still crashes; distant cars are untouched.

Worth recording — I got the geometry backwards first time and the braking never fired. Traffic enters at the top and moves down, and `speed = currentSpeed - speedOffset`, so the car with the **smaller y** is further ahead down the road and the one behind closes when its `speedOffset` is the **larger** of the two. The comment in the code now spells that out.

**Wrecks are solid now.** A crashed pair used to be scenery that other traffic slid straight through; drive into one and you join the pile-up. Two existing wrecks still ignore each other, so a heap cannot re-trigger itself. Ram-kill corpses (`crushed`) stay non-collidable — that is Batch 190's deliberate behaviour for something the player flattened.

**Letters lie on the road properly.** They were drawn *after* the vehicle loop, so cars slid underneath them; the block moved ahead of that loop, and traffic now paints over them. Collecting one also requires being **on the road** — fly over a letter and it stays put for a later pass. Verified with a real held jump: untouched mid-air, collected after landing.

**The two solid bars running down every lane are gone**, by direct request. Real tarmac carries no such marking; what remains is the lane boundaries, the dashes and the surface grain.

**The result screen's scrollbar was the last browser-default one** — `#gameOverHud` has its own `overflow-y: auto` safety net and was never added to the shared themed rule. It is now.

**One consequence to flag rather than bury:** at default settings (4 lanes, RECKLESS) five simulated minutes produced **zero** NPC crashes, and at 9 lanes/SUICIDAL only 1-3. That is exactly the "much rarer" that was asked for, but the `witness_crash` daily mission depends on seeing one — it may now be hard to complete on a normal run. `NPC_INATTENTIVE_CHANCE` is the one number that moves it.

## 2.221.0 — 2026-09-20 16:26: Batch 430 — Stuck badges, live coin totals, sound on by default, car icon

**The GARAGE / GIFT / MISSIONS badges were stuck on — my bug from the menu rebuild.** All three update functions toggle a `.show` class, and the old `.new-badge` carried `display: none` by default. The rebuilt menu's `.mm-badge` did not, so every badge was visible permanently regardless of state. One declaration plus the `.show` rule. Verified both directions: the badge lights when a gift is claimable and clears once the reveal is closed.

**Coin totals now update the moment they change.** Claiming the Daily Gift called `renderDgGiftCard()` but never `renderDailyGiftHeader()`, so the coin figure on that screen kept its pre-claim value until the screen was reopened. It now re-renders the header and refreshes the menu summary in the same handler. Verified with a forced coin reward: a 6,970-coin gift took the header from `1K` to `7.97K` immediately.

**Sound starts at 30%, and this needed more than a new default.** `syncVolumeUI()` persists whatever it is handed, and the init call used to run with the old `'0'` default — so every existing save already had `soundVolume="0"` written to it and a changed default would have done nothing at all. Two fixes: the init calls no longer persist (a default should not masquerade as a choice), and a one-time migration clears that legacy auto-written zero. Verified against a deliberately muted save: it comes back at 30% with the slider, the pause slider and the label all agreeing. This reverses Batch 124's muted default, which was set after "it starts playing in the background" — the slider is still one drag from silent.

**START RUN pulses occasionally instead of constantly**, and the colour cycle is much slower. The pulse now sits flat for most of a 7-second cycle with one brief pop, which is the shape of the doc's own `startRunGlow`; the hue cycle went 26s → 60s.

**Tab hover frames take each tab's own colour.** Every tile now carries a `--tab-c` variable that drives both its icon and its hover border, instead of one hardcoded mint for all eight.

**App icon and favicon are the supplied car sprite** (`carsprite.ico`, 10 sizes from 16 to 256). The favicon embeds the 128px frame rather than a small one, per the request to use the best-quality source.

## 2.220.2 — 2026-09-20 15:52: Batch 429 — Menu: road gap sized to the setup block, slower colour cycle, lane trail

Three direct follow-ups on the rebuilt menu.

**The road gap is now as tall as the lanes+mode block it sits above** — 119px (64 lane box + 8 + 47 difficulty row), measured from the live elements rather than picked. Built as a **flexible spacer, not a fixed margin**, and that matters: `sizeFrame()` gives the menu the full window height, so the frame is ~956px on a normal display but only ~677px in a short window. A fixed 119px margin would have been right on one and would have shoved the footer off the bottom on the other. The spacer carries a heavy flex weight so free space fills it first, capped at 119, with the remainder going to a second spacer above the footer. Verified at both sizes: 119px at a 1000px-tall viewport with no overflow and the footer clearing by 16px; it shrinks to its 14px floor in a short window instead of clipping.

**The START RUN colour cycle slowed from 14s to 26s.** The 1.8s pulse is untouched — that one is the doc's own `startRunPulse` and was not what was flagged.

**The lane track has a trail.** Lanes below the chosen one now carry a dimmed amber fill (`rgba(245,179,42,.38)`) at the flat 14px height, so the track reads as a slider with a filled run behind its handle rather than eight unrelated ticks. The chosen tick still rises to 24px in solid amber with a white border, which is the doc's own behaviour. Verified at 6 lanes: ticks 3-5 trail, 6 is the handle, 7-10 plain.

One consequence worth flagging rather than silently tuning: with the top gap capped at 119, a tall window leaves a larger void (~228px) between the last tab row and the bottom-pinned footer. That is the doc's own structure — the footer is bottom-pinned and the road shows through behind everything — but if it reads as too much dead space, capping `.mm-endgap` is a one-line change.

## 2.220.1 — 2026-09-20 15:38: Batch 428 — Main menu corrections: the parts I had guessed at

Five direct reports, and three of them were things I got wrong for the same reason: **the design doc's template loops never rendered.** Its `sc-for` blocks are filled by a `support.js` that 404s, so the lane ticks and difficulty tiles existed in the source only as `{{ }}` placeholders. I had read the rendered DOM and invented the missing values instead of reading the doc's own script. Doing that this time gave exact numbers for all three.

- **Lane track was a staircase; the doc has it flat.** Its script says `height: sel ? 24 : 14` — every tick is 14px and only the *chosen* one rises to 24px and fills amber with a white border. I had lit every bar up to the current count and ramped their heights, which is what read as stairs. It is a slider marking one value, not a bar filling up.
- **Difficulty tiles had a frame and no fill.** The doc's `background: sel ? c.bg : '#1b2130'` uses a per-mode colour table, now ported exactly: SAFE mint `#2ee6b0` on ink `#0c2a22`, RECKLESS amber `#f5b32a` on `#2b1c00`, SUICIDAL red `#e63946` on white. The selected tile is filled, not merely outlined.
- **START RUN now pulses and fades smoothly.** The doc has a real `startRunPulse` keyframe — 1.8s `ease-in-out`, `scale(1)` to `scale(1.03)`, with a glow — which I had replaced with a hard `steps(1)` colour hop and no scale at all. The pulse is now the doc's, exactly. The continuous colour change (a separate earlier request the doc does not cover, since its own keyframe only breathes red to orange) rides on a 14s `hue-rotate` instead of a second background keyframe: two animations cannot both own `background-color`, and hue-rotate leaves the white label, icon and border alone because white has no hue to turn.
- **Level ring 64px → 88px.** It had been shrunk to 64 to make the plate fit the frame; the space to put it back came off the gap below.
- **The gap under the level badge is 26px, not a hole.** `margin-top: auto` on the setup block was dumping *all* the layout's spare height into that one place. The gap is now fixed and the leftover goes above the footer instead, so the road still shows between the badge and the lane box without a void.

Verified live: ticks measure 14px with a single 24px amber one, RECKLESS renders `rgb(245,179,42)`, ring is 88px, gap is 26px, and the button carries `mmStartPulse 1.8s ease-in-out` plus `mmStartHue 14s linear`. Nothing overflows — `scrollHeight` equals `clientHeight` and the footer clears the frame by 16px.

Worth recording as a pattern: when a design doc ships with an unrendered templating layer, the rendered DOM is the *least* reliable place to read it from. The values are in its script.

## 2.220.0 — 2026-09-20 15:24: Batch 427 — AWARDS and STATS everywhere, tutorial reordered, cones knock loose

**Both naming conflicts settled, and applied everywhere rather than just on the menu.** The choice was delegated, so:
- **ACHIEVEMENTS → AWARDS.** It is what the supplied design doc uses, it fits the narrow 3-column tile at 9px where the long word does not, and the tier ladder is already a medal metaphor (bronze / silver / gold / diamond / amethyst), which "awards" matches. Changed on the screen title, the SECRET group label, the per-group count, the dev-menu group and its button, and the tutorial copy. "BADGES" was the other candidate and is a one-pass swap if preferred.
- **STATISTICS → STATS.** This partly reverses Batch 414, which went the other way — but that was decided under the old menu's wide two-column buttons, and the new 3-column grid cannot carry the long word. Changed on the screen heading and the Scores screen's jump-to button, so all three surfaces agree again, which was Batch 414's actual goal.

Internal ids, functions and `localStorage` keys keep their existing names in both cases, exactly as Batch 414 decided — renaming those would be churn with live save data attached.

**Tutorial reordered for a new player.** Direct note that the first thing to learn is how you steer and move, then what the tabs do. THE MAIN MENU moved out of PROGRESSION and into BEGINNER, directly after THE WHEEL — so the order is now drive, then navigate, then everything else. SPOTTING CARS stays in PROGRESSION, which is what was asked (it was never in BEGINNER).

**Breakdown cones can be knocked aside.** Answering the direct question: made them **cosmetic-only**, deliberately. They sit in front of a car that already ends the run, so making them damaging or slowing would stretch a single obstacle across two lanes' worth of stopping distance — a real difficulty increase that was not asked for. Driving through a cone now throws it clear (away from the player's centre and forward down the road, then decelerating), which stops the dressing reading as painted-on scenery without touching the hitbox, the score or the energy bar. Jumping over the obstacle leaves them standing, since you never touched them.

The three cone positions moved into one `breakdownConePositions()` helper that both the renderer and the new collision check read, so the two cannot disagree about where a cone is — the exact failure Batch 416 recorded for shared renderers used from two call sites.

Verified live: all three knock on contact and drift (−17.2, +12.7 after ten frames), and stay intact when the player is airborne. Also confirmed the menu and Settings still agree after the redesign — setting 8 lanes on the menu leaves Settings reading `1.03x MULT`, since both write to the same control.

One thing NOT done: the `reckless-cone.ico` icon files. They are not in the project folder, Downloads, Desktop or anywhere else reachable — see the note to the user.

## 2.219.0 — 2026-09-20 15:10: Batch 426 — Main menu rebuilt from the design doc; breakdown cones no longer pop in

**Main menu ported from "Main Menu Options.dc.html", TURN 5 (variant 3b).** That turn is the newest and carries a single variant, so there was nothing to guess between. The doc is inline-styled, so its styles were translated onto this file's palette tokens rather than copied.

What it is now: centred HIGHWAY / RECK**LESS** / DRIVING wordmark, the level badge beside its ring, a lanes box and a draggable lane track showing that lane count's traffic and multiplier, a difficulty row of three buttons each showing its own multiplier, a full-width START RUN carrying the live run multiplier, then a 3x2 icon grid (GARAGE / SCORES / AWARDS / STATS / MISSIONS / GIFT) and a 2-wide SETTINGS / TUTORIAL row, with the DEV/version footer. Icons are the doc's own 8x8 pixel paths.

**The two requested departures from the doc:**
- **The level badge keeps the game's own ring** — the doc drew a plain bordered circle, which loses the XP arc. The existing canvas ring and `paintLevelBadge()` are reused untouched; only the layout changed to put the ring left of the rank text.
- **START RUN cycles colour continuously** rather than settling back to red. `steps(1)` hops between red, amber, mint and blue so it stays pixel-art instead of fading.

**LANES and DIFFICULTY move onto the menu, but nothing underneath changed.** The new controls *write to* the existing `#selectLanes` / `#selectDifficulty`, which `calculateMultiplier()` and `launchGame()` already read — so the Settings screen still works and no game logic was touched. Verified live: dragging the track to the far right gives 10 lanes, `2.50x TRAFFIC` and a `x1.49` run multiplier; SUICIDAL takes it to `x1.82`; both restore correctly.

The traffic figure is derived from the same `lanes / 4` term the spawn rate itself uses, not invented for the display.

**Two layout faults found and fixed after the first render**, both worth recording:
- A stale `#menuLevelBadge` ID rule from the old menu was forcing `flex-direction: column`, beating the new class and stacking the badge. Eight now-dead ID rules removed.
- The doc's plate is 920px tall; this frame is aspect-locked to the canvas and was 677px, so the design overflowed by 95px and cut off the bottom row. The fixed 96px road gap became `margin-top: auto` and the 76px blocks came down to 64px, so the road still shows through and everything fits.

**Breakdown obstacle: the cones no longer appear out of nowhere.** Direct report, and correct. The parked car spawned at the shared `-height - 10`, but its barrier and cones are drawn *below* it (`this.y + height + 6`, so the player meets the cones first) and the lowest cone reaches another 29px past that — measured, not estimated, by rendering the dressing alone and reading its painted extent. At the old start the car was off-screen but its dressing began at y = -4, already inside the canvas, so barrier and cones blinked into existence at the top edge. The obstacle now starts at its full assembly height; verified the dressing spans -40 to -11 at spawn, entirely off-screen, and scrolls in like everything else.

**Tutorial: the mocked main menu is gone.** It reproduced the old menu, which the redesign made stale immediately — a good argument against mocking a screen at all. Direct feedback was to explain what each tab does instead, so the art is now the game's wordmark and the copy is one line per tab, updated to the new names.

## 2.218.0 — 2026-09-20 14:58: Batch 425 — Tutorial: new PROGRESSION section, STACKING dropped, read-dots removed, scrollbars squarer again

Four direct requests in one pass.

**STACKING is gone.** Direct report that it was very similar to THE MULTIPLIER, and it was — both explained that the multiplier terms multiply together, and the Batch 419 live "YOUR SETUP RIGHT NOW" strip on THE MULTIPLIER now shows the player their own lane × difficulty × car × speed figures, which is a better version of what STACKING described in prose. Removed rather than rewritten: nothing in it was left unsaid elsewhere.

**Read-dots removed from the contents rail**, direct request. The whole mechanism went with them, not just the marks — the `IntersectionObserver`, its timers, the `syncTutRead`/`watchTutRead` pair, the CSS, and the persisted `allTimeStats.tutRead` field. Old saves keep a stray unused key, which is harmless.

**Scrollbars squarer again.** Batch 424 had already unified six panels onto one treatment and flattened the thumb; the report was that it still wanted to be more square. A flat bar still read as a browser scrollbar, so the thumb is now a pixel block like the rest of the UI: 14px wide (10px on the narrow contents rail), a hard 2px outline in the panel-border colour via `background-clip: padding-box`, square corners, and the same hard inset bevel the keycaps use — no blur anywhere.

**New PROGRESSION section, five cards**, covering what was asked for: what the tabs do, how the player level works, how Performance Score works, how cars are discovered, and the daily systems.
- **THE MAIN MENU** — illustrated with a working miniature of the real menu (same two-column shape, same red primary), so the card shows the thing rather than only naming it.
- **SPOTTING CARS** — a car is discovered the moment it is on screen; no passing or contact needed, and the Garage tile turns from `???` into a priced car.
- **YOUR LEVEL** — XP is the run's raw pre-multiplier score, so levelling rewards playing rather than playing well; the curve, the ten rank tiers, and a chip row of what levels actually unlock.
- **GIFTS, WORDS AND MISSIONS** — the three midnight resets, with the coin-mission ladder as chips.
- **PERFORMANCE SCORE** — the osu!-style weighted decay explained in plain terms: best run in full, each next at 95% of the one above, down to a hundred runs.

It sits outside the green/amber/red difficulty ramp in its own purple, because it is not harder driving — it is everything around the driving.

Every number in it is read from the system that owns it rather than typed into the prose (the standing rule since Batch 405): the level curve from `levelReq()`, the gift threshold from `dailyScoreThreshold()`, the payouts from `MISSIONS_LADDER_COINS`, the car count from `GARAGE_CARS`, and the player's own level, rank and Performance Score live from their save. Verified on screen: 52 cars, level 1 / RUST I, 1,000 XP to level 2, threshold 400, ladder 50K / 100K / 200K and 350K for all three.

Verified live: 5 sections, 22 cards, 22 rail entries, no STACKING, zero read-dots, both new canvases painting, zero console errors. One measurement correction during the work — the six animated scenes initially read as blank canvases, which looked like a regression but is the viewport check doing its job: `drawTutScenes()` deliberately skips scenes scrolled out of view. Sampling with them in view shows 22,528 painted pixels each.

## 2.217.0 — 2026-09-20 14:41: Batch 424 — First launch lands on the menu, faster tutorial scenes, one squarer scrollbar

Three PLAN items done together (127, 128, 135).

**The forced first-launch tutorial is gone — a deliberate reversal of Batch 397.** That batch opened `#tutorialView` *instead of* the menu on a first launch, by routing rather than by a modal, so "nothing else is clickable" held structurally. Direct decision: land on the main menu like any other launch, and draw the player to the tutorial instead of trapping them there. The TUTORIAL button now blinks (a hard 2px mint ring, `steps(2)` so it snaps on and off like the rest of this UI rather than glowing) until the screen has been opened once.

Chosen as a **nudge rather than a gate** — the open question logged with the idea. A gate the player can see past is more irritating than one they never reach, and the tutorial is one click away at any time.

Opening the screen at all now counts as having seen it, which is what clears the blink; previously `tutorialSeen` was only set when the *forced* pass was dismissed. `tutorialForced` is gone entirely along with the branches it gated (the Escape handler no longer has a pass to hold back), and `showTutorial()` lost its argument. Verified on a cleared save: first load shows `menuView` with the button nudging, opening the tutorial sets and persists the flag, returning to the menu shows the button back to normal.

**Tutorial scenes play at 1.35x** — direct request that the cars could go a little faster. Scaled as ONE rate (`TUT_SCENE_RATE`) rather than by editing each scene's own speed, and that distinction matters: every scene's choreography is a set of fixed millisecond marks (a car reaches the player at t=1600 while the dodge eases 1500–1900), so speeding up the cars alone would have slid them out of sync with the moves they exist to illustrate. Scaling time keeps every scene exactly as composed, just played faster. Deliberately not higher: these scenes are slower than real gameplay so the mechanic reads, and past a point they stop teaching and just look busy.

**One scrollbar treatment, shared by all six scrolling panels.** The request was about the result screen's achievements box, but that box was never using a browser default — six panels each carried their own near-identical copy of the same five rules, which is exactly why a tweak like this had to touch six places. Now one selector list covering `.garage-scroll`, `#goAchBox`, `.dg-scroll`, `.tut-scroll`, `.tut-rail` and `.stats-scroll` (the rail keeps its narrower 8px width). "Edgy/square" concretely: `scrollbar-width: thin` dropped (Firefox rounds a thin thumb), the thumb's 2px inset border removed so it fills the full channel as a solid block instead of a floating pill, `border-radius: 0`, and the track given a hard 2px edge matching every other panel border in this UI. Verified all six resolve to identical computed values.

**Late correction — the font self-check was wrong twice, and this is the version that is actually right.** Batch 423 replaced `document.fonts.check()` with a width measurement on the theory that measuring forces a font to resolve. It does not. A face has to be *loaded* before it can be checked **or** measured, and nothing in the self-test loads one: the menu renders no DotGothic16 text, and `font-display: swap` lays out with the fallback until the face is active. Measured both ways on a build that was perfectly fine — before an explicit load, `check()` is false **and** the measured width equals the fallback exactly (285.9px); after `document.fonts.load()`, `check()` is true and the width is 260px. The check now asks for the load and polls until the browser confirms it. Silkscreen and VT323 never showed the fault only because the menu happens to render both.

**One self-inflicted bug, caught by diffing rather than by eye.** The regex that stripped the six duplicate blocks matched on the *first property name*, and `.tut-rail`'s layout rule happens to begin `width: 176px` — so it was deleted along with the scrollbar rules, which would have collapsed the tutorial's contents rail. Found by diffing every removed line against the pre-change backup, restored, and re-diffed to confirm nothing else went with it. Worth remembering: when bulk-deleting CSS by pattern, diff the removals; a property-name match does not mean a rule is the one you meant.

## 2.216.1 — 2026-09-20 05:02: Batch 423 — App: single-instance, isolated self-test, and two crashes fixed

All found by the build's own self-test failing on a build that was actually fine. Worth recording how wrong the first diagnosis was.

**The symptom**: after Batch 422 the self-test reported `game reports 2.215.0, app is built as 2.216.1`, while the packaged `carCrash.html` demonstrably contained 2.216.1. It reproduced perfectly — kept profile: fail, deleted profile: pass — which made it look exactly like WebView2 serving a cached copy out of the profile we deliberately keep for saves.

**That diagnosis was wrong.** Printing `location.href` on failure showed the URL was correct, so the file being served had to be coming from somewhere else. It was: a second `RecklessDriving.exe` was already running — **the installed copy, which the user had installed and launched** — holding port 42017. A second instance cannot bind that port, and pywebview does not treat the failure as an error: the new window simply loads the URL, which the *first* instance's server answers. So the build's self-test was reading the installed 2.215.0 game through the running copy's HTTP server. The "deleted profile" case only passed because the game happened to be closed at that moment.

Three fixes, all real bugs rather than test scaffolding:
- **Single instance.** Launching the game while it is open used to produce a second window showing the other instance's build. It now detects the port, brings the existing window to the front (`FindWindowW`/`SetForegroundWindow` via ctypes, no new dependency) and exits — which is what a desktop shortcut should do anyway.
- **The self-test is fully isolated**: its own port (42018) and a throwaway profile. A build can no longer collide with a copy the player has open, and — more importantly — can no longer read or damage the real save.
- **Unhandled-exception dialog on exit.** `tempfile.TemporaryDirectory` raised `WinError 145` deleting that throwaway profile, because WebView2 keeps handles open under `EBWebView\Default` for a moment after the window is destroyed. The build went green and *then* threw a crash box, which is the worst version of this. Now an explicit `shutil.rmtree(..., ignore_errors=True)`, plus a sweep of previous builds' leftovers at startup so `%TEMP%` doesn't collect one per build.

**The font check was genuinely flaky and is fixed too.** It used `document.fonts.check()`, which reports only on what has already loaded and does not force a load — so DotGothic16, which the menu barely renders, failed on one build and passed on the next. It now lays out a string in each family and compares the measured width against the fallback, which forces resolution and cannot report a false negative.

**Kept: the version-keyed URL** (`carCrash.html?v=<VERSION>`), added while chasing the wrong cause but justified on its own. Verified in the source: pywebview sets `Cache-Control: no-store` on `bottle.response` and then returns `bottle.static_file(...)`, which builds its **own** `HTTPResponse` — so those headers never reach the browser, leaving only `Last-Modified` and heuristic caching. An update landing at an identical URL could therefore serve the previous build. A query string changes the URL but not the origin, so localStorage — the save — carries over untouched.

## 2.216.0 — 2026-09-20 04:44: Batch 422 — Every car is now buyable; boxes reserved for the special vehicles still to come

Direct decision, reversing Batch 406: the 13 box-exclusive cars become ordinary purchases — found in traffic, bought with coins at a real price — and the box system is kept empty and waiting for the fun vehicles (bicycle, fish, couch) being added next.

**This inverts what `boxOnly` means, rather than just clearing it.** It used to mark cars obtainable *only* from a box, while a box could award **any** car in the roster. It now marks the cars a box *may* award, and anything without it is bought like any other car. That distinction is the whole change: simply deleting the flag would have left boxes handing out cars that are now purchasable, which is the opposite of what was asked.

`boxOnly` removed from all 13 (Drift, Offroad, Armored Van, Monster Truck, Tank, Dragster, Go-Kart, Limousine, Steamroller, Roadster, Camper, Garbage Truck, F3 Junior). **No prices needed inventing** — all 13 already carried real-world-researched values from Batch 345 and were simply never purchasable: Go-Kart 5.5K, Steamroller 55K, Monster Truck 220K, Tank 15M, and so on. Verified every non-Stock car has a price.

**The car tier is now dropped from the reward roll entirely while no car is box-exclusive**, rather than quietly paying coins instead. The roll and the DROP CHANCES panel read the same `rewardWeightsFor()` helper, so a panel advertising a 10% CAR chance that could never pay out would have been a straight lie to the player. The Daily Word panel now shows XP / COINS / PAINT re-based to the real odds, and the CAR row is gone. Confirmed over 20,000 rolls that the car tier never comes up.

**The machinery is intact and was proven so**, since that is the point of leaving it: flagging a single car `boxOnly` at runtime immediately restored the 10% car weight, the CAR row in the panel, and the achievement's top tier — no other change needed. Adding the special vehicles is therefore a data change, not a code change.

**Two consequences worth knowing, both found by checking rather than by running the game:**
- **COLLECTOR would have shown two identical tiers.** Diamond is "own every buyable car" and Amethyst "own every car there is"; with nothing box-exclusive those both compute to 52. Amethyst is now omitted while that is true (the Missions ladder already sets the precedent of a tiered achievement capping at Diamond) and returns by itself once a box car exists.
- **Extra Boxes now require owning all 52 cars to appear, up from 39.** `ownsAllPurchasables()` gates them, and "purchasable" just grew to mean the whole roster. Unchanged in intent — boxes remain the after-everything-else chase — but it is a real raise in the bar, and until the special vehicles land those boxes pay only coins, XP and paint. Flagged rather than silently adjusted.

Kept deliberately: the `discoveredOnly` filter on the car pool (currently a no-op, since box-exclusives have always been exempt from it) and the Garage's mystery-tile, LOCKED and "BOX EXCLUSIVE — NOT FOR SALE" rendering, all of which apply again the moment a car is flagged. The formerly box-only cars already spawned as traffic, so discovery needed no change — verified in the Garage, which now shows them with prices instead of a lock.

## 2.215.0 — 2026-09-20 04:29: Batch 421 — Fonts embedded, and the game builds into an installable Windows app

Direct go-ahead to embed the fonts, build the exe, and "repair what is needed". `carCrash.html` was copied to `backup/carCrash.2.214.0.pre-packaging.html` first, as asked.

**Fonts are now inside the file** (`tools/embed_fonts.py`, re-runnable). Silkscreen 400/700, DotGothic16 and VT323 were fetched at runtime from `fonts.googleapis.com`, so a packaged offline app would have fallen back to plain `monospace` and lost the whole pixel-art type treatment. 68 KB of woff2 is now embedded as base64 `@font-face`; the file went 928 KB → 1031 KB.

Two details that decide whether this is correct rather than merely working:
- **`unicode-range` is preserved on every face.** Without it the browser would use an embedded font for *every* character and draw tofu where it lacks a glyph, instead of falling back. The game already depends on that fallback — the tutorial's keycap arrows (U+25B2 and friends) are outside every subset these fonts ship, so they were already rendering from a system font and still do.
- **Only `latin` and `latin-ext` are embedded.** DotGothic16's Japanese slices alone would add megabytes for glyphs the game never renders. `latin-ext` is kept because it carries the Polish accented characters.

Verified by measurement, not by eye: each family's rendered text width differs from the `monospace` fallback (Silkscreen 370px vs 285.9px for the same string), all 8 faces report `loaded`, and the page makes zero font network requests.

**The Windows app.** Built on the pattern from the user's own Lockdown project rather than PLAN.md's older Tauri research — no Rust, and the toolchain was already on the machine. `app/main.py` hosts `carCrash.html` in a native window via the Edge WebView2 runtime that ships with Windows 11. `scripts\build.ps1` produces `build\RecklessDrivingSetup.exe` (23 MB): PyInstaller builds the game folder → a self-test runs the built exe → the folder is zipped → a second pass embeds that zip inside the installer.

**Saves were the real risk, and three defaults had to be overridden to get it right.** pywebview defaults to `private_mode=True`, which turns on WebView2's InPrivate mode (localStorage is never written) *and* deletes the whole user-data folder on close (`clear_user_data` in `edgechromium.py`). Beyond that, pywebview serves local files from `127.0.0.1:<port>` and localStorage is keyed to that origin, so a port that varied per launch would silently lose every save. So: `private_mode=False`, `storage_path` pinned to `%LOCALAPPDATA%\RecklessDriving` (outside the program folder, which is the only thing an update replaces), and a fixed port 42017 of our own rather than pywebview's shared 42001 default. **Proven, not assumed**: a probe wrote through the game's own `saveAllTimeStats()`, the process exited, and a second process read the values back.

**Update flow**, the thing that was actually asked for: the same `RecklessDrivingSetup.exe` reads `DisplayVersion` from the per-user uninstall key, and the wording and button become **Update** when the game is already installed. So an update ships as one new exe to double-click. Installation is per-user into `%LOCALAPPDATA%\Programs` — unlike Lockdown it needs no admin, because there is no service to register, so there is no UAC prompt.

**Anti-drift**: `build.ps1` refuses to build if `app/version.py` disagrees with the game's own `GAME_VERSION`, or if `carCrash.html` still references Google Fonts. The self-test checks the packaged build really boots, that the embedded fonts resolve offline and that localStorage is writable — it fails the build otherwise, so a broken build cannot be packaged.

**Icon** (`tools/make_icon.py`): generated by opening the real game and calling its own `drawPixelCar()`, not hand-drawn — this project has a track record of hand-approximated sprites being subtly wrong for weeks (Batches 175, 410). Emitted at 16/32/64/128/256, all exact integer ratios of the 64px render so nearest-neighbour scaling stays crisp.

The installer's logic was exercised against temp folders and a throwaway registry key — payload extraction, both shortcuts, the uninstall-key round trip, older-version-detected-as-update, saves surviving an uninstall, and saves deleted only when the box is ticked: 11/11 pass. **Nothing was installed on the machine** and the test save profile was removed, so a first launch starts clean.

Noted while here: the main-menu version string is set from `GAME_VERSION` at startup, so it is no longer a manual sync step despite what the older notes say.

## 2.214.0 — 2026-09-20 04:08: Batch 420 — Music: 7 tracks, two new keys, and mid-run track rotation

Direct request: "I like the current music, but maybe add some more. So make it less boring, I don't want to listen to the same stuff all the time." The existing 3 tracks are therefore **untouched** — this only adds.

**Measured the actual cause before writing any notes, and more tracks alone would not have fixed it.** A 32-step loop of 16th-notes at ~128 BPM is **3.75 seconds** long, and `startMusic()` picked one track at run start and never changed it — so a five-minute run played that same 3.75s loop about 80 times. Track count was the smallest of the three problems.

All three are now addressed:
- **Rotation (the main fix).** The track changes every ~30s, always ON a loop boundary so a phrase is never cut mid-bar, and never to the track already playing. Verified over a simulated 3000 steps: gaps 26.2–30s, every switch on a boundary, no immediate repeats.
- **Longer loops.** `musicTick()` read a hardcoded `% 32`; it now reads `track.steps.length`, so a track may be any length. Two of the new ones are 64 steps (7.5s).
- **Keys.** Everything was A minor pentatonic, so switching tracks changed little. Added `MUSIC_SCALE_D` (D minor) and `MUSIC_SCALE_E` (E minor, a fourth lower and darker) as an optional per-track `scale`, same 9-entry ascending shape, so any scale drops in with no other change.

`MUSIC_TRACKS` entries became `{ name, scale?, steps }` (was a bare array of step arrays). Four new tracks: **OVERPASS** (64 steps, D minor, busier turnaround bar), **UNDERPASS** (32, E minor, sparse and low — the quiet one, so the set has a floor as well as a ceiling), **CHASE** (64, A minor, offbeat extra kicks and a straight-16ths final bar — the high point), **CRUISE** (32, D minor, relaxed, offbeat bass).

**Menu pad**: one 16-step phrase became three, rotating every 2 passes (~12s), starting on a random one. Deliberately all in A minor — unlike gameplay, this plays under a still screen where a key change is the only thing happening and draws attention to itself.

Verified live, not by reading: every step of all 7 tracks validated in range against its own scale (zero problems); the scheduler driven against the real `AudioContext` (10 oscillators + 8 hi-hat buffers in 15 steps, no exceptions); rotation forced and observed switching track and resetting the step counter; and each of CRUISE / UNDERPASS / OVERPASS / original-1 sampled at `oscillator.start()` to confirm the frequencies actually reaching the audio graph belong to that track's own scale.

Two false alarms during verification, both in the test harness rather than the game, recorded because both are easy to repeat: setting `window.gameActive` does nothing (it is a script-scope `let`, so that creates a *different* variable and `musicTick()` bails at its first check), and patching `AudioContext.prototype.createOscillator` does not intercept — the instance method has to be patched. Reading `oscillator.frequency.value` at creation also returns the default 440, because the code assigns it after `createOscillator()` returns; sample at `start()` instead.

## 2.213.0 — 2026-09-20 04:00: Batch 419 — Tutorial visual upgrade: animated road scenes, value chips, "your setup" multiplier strip, read markers

Direct request ("do the tutorial ideas") after a review of the screen: every card was the same shape — one parked sprite next to 2–3 paragraphs — and read like documentation.

**Six cards now show their mechanic happening** (HOW YOU DIE, HOW YOU SCORE, JUMP, CLOSE CALLS, SHIELD BUMP, READ THE ROAD). Each is a looping scene on a shared 3-lane mini road (64x88 native at 2x — the same step-down the Shield Bump composition already used): a blinker car merging while the player slips past it; a neighbouring-lane pass popping `+10` while a far-lane truck pops `+0`; a held jump over a car with the real flame and ground shadow; a late slide that shaves a car's flank and pops `CLOSE CALL +100`; the Monster Truck flattening two cars in a row with the live plume/guard/ripple; a flashing warning sign followed by a parked breakdown with hazards, barrier and cones arriving at road speed. Every vehicle and effect is drawn by the game's own renderers (`drawPixelCar`, the `VEHICLE_BODIES` draw functions, `sbPlume`/`sbGuard`/`sbRipple`, `drawWarningSign53`, `drawBreakdownDressing53`, `makeAsphalt53`), and popup values read `VEHICLE_POINTS`/`CLOSE_CALL_BASE_SCORE`, so scenes cannot drift from the game. Scenes are pure functions of loop time — no state to reset. One rAF loop runs only while the screen is open and skips scenes scrolled out of view; this supersedes the old "one-shot render, no animation loop" note. The road is the backdrop, so Batch 403's "no frame, no fill" still holds — no cell was reintroduced. NPC colours deliberately avoid blue so none read as the player's default car.

Removed with the one-shot art they served: the `tutArtStock/Close/Ram/ScoreA/ScoreB/Ambulance/Jump` blocks and `suppressJumpShadow` (the JUMP scene has a road under it now, so the real shadow is correct again).

**Value chips** under HOW YOU SCORE (points per pass × multiplier) and GETTING PAID (coins per pass, x5 jumped-over), generated from the same constants as the prose (Batch 405's rule).

**THE MULTIPLIER gets a live "YOUR SETUP RIGHT NOW" strip**: lanes × difficulty × car = base, then the value at that car's own top speed — computed exactly as `calculateMultiplier()` and the main loop's speed term do, from the player's actual settings and selected car. Verified: 4 lanes / RECKLESS / Stock → x1.15 × x1.15 × x1.30 = x1.72, x3.78 at 170 km/h.

**Takeaway emphasis**: each card's first paragraph renders at full text colour, detail stays dim. No copy hidden or rewritten.

**Read markers** in the contents rail: a card counts as read after 60% of it sits in view for 1.5s (a scroll-past never qualifies), persisted in new `allTimeStats.tutRead`. Verified it survives a reload.

**Deliberately NOT done, because the changelog shows each was already tried and removed by direct request**: a 9-cell energy-bar mock on the JUMP card (removed Batch 401 — "read as a bar chart"), and a START DRIVING button on the forced pass (removed Batch 407 — the button returns to the menu, it doesn't start a run). Also held: hiding card detail behind a "more" toggle — with the art column now ~176px tall the prose no longer dominates, and collapsing it would leave tall art beside one line.

Verified: all six scenes stepped through their full period at 50ms intervals with zero exceptions; key frames composited side by side and inspected; chips/strip values read back from the DOM; zero console errors.

## 2.212.3 — 2026-09-16 16:55: Batch 418 — Shield Bump card centred and uncropped, sized from measured extents

Direct report: not centred, clipped at the top, flame off-centre. All three real, and all three caused by sizing the canvas from estimates.

**Measured each renderer's actual reach** by drawing it alone at a known origin, rather than guessing: guard = 9 left / 8 right / 8 up; **ripple = 12 left / 12 right / 13 up / 12 down**; plume = 15 down. The crop had been budgeted for the guard alone — but the ripple is both the widest and the tallest element, reaching 5px higher than the guard does, which is exactly why the top kept clipping no matter how the guard's allowance was adjusted.

**Centring was off by a pixel for a specific reason.** Everything was positioned on `carLocalX53(bw) + bw/2` = 12, but the Monster Truck's art spans x=1..22, so its true midpoint is 11.5. Half a pixel at native resolution, a visible pixel at 2x, and it pushed guard, plume and ripple off the body — the off-centre flame. All three now derive from one origin placed on the sprite's real centre, so they cannot drift apart again.

Final geometry: 60x120 canvas, content 50x114, padding L=5 R=5 T=4 B=2, horizontal offset 0.0 — verified by pixel measurement rather than by eye. Also slightly smaller overall than the 80x106 it replaced in the horizontal axis, inside a 108px cell.

Worth noting the pattern: three attempts at this failed because each adjusted a guessed padding value. Measuring the renderers took one script and fixed it in one pass.

## 2.212.2 — 2026-09-16 16:35: Batch 417 — Shield Bump card now shows the whole ability, not just the guard

Direct report: the card still didn't look like the ability does in play, and read as plain. Correct on both counts — `drawShieldBumpFX()` composes **three** elements every frame (the push guard, the thruster plume behind the car, and the displaced-air ripple arcs at its sides), and the card was drawing only the first. One third of the effect, which is why it looked like a parked truck wearing a hat.

The card now calls the same three renderers the live ability calls — `sbPlume()`, `sbGuard()` and `sbRipple()` — so it composes identically and cannot drift from the mechanic. Frame 3 of the plume's 4-frame loop and frame 2 of the ripple's are used deliberately: the plume's longest extension and a mid-travel ripple, i.e. the ability at its most legible rather than whatever an arbitrary tick would give.

The canvas was resized to hold the full composition: 10 rows ahead of the nose for the guard, 15 behind the tail for the plume, and 9px of padding either side for the ripple arcs, which reach ~15px from the centreline. Previously the canvas was cropped tight to car-plus-guard, so even if the other two had been drawn they would have been clipped away.

Verified by pixel dump: guard wedge above the nose, truck body, plume trailing below it, ripple arcs at both flanks — all four regions present in one image, at 80x106 inside a 108px cell with no overflow. Zero console errors.

## 2.212.1 — 2026-09-16 16:20: Batch 416 — Tutorial's Shield Bump card was still drawing the old oversized guard

Direct report, and correct: Batch 415 pinned the Shield Bump guard to a fixed size in gameplay, but the tutorial's SHIELD BUMP illustration has its own `sbGuard()` call site and was still passing the old width-derived `bw / 16`. So the card kept rendering the very guard the gameplay fix had just removed — the illustration silently disagreed with the mechanic it documents, which is worse than either being wrong alone.

Changed to `scale: 1`. Verified both paths measure identically: 18px in gameplay and 18px native on the card, against a 22px-wide Monster Truck.

Worth recording as a pattern: this is the second time a shared renderer has been fixed in one place while a second call site kept the old behaviour (the first was `achModel()` vs `renderResultAchievements()` in Batch 398, which had diverged twice). When a fix changes how a shared draw function is *called* rather than what it does, grep for every call site — the compiler cannot help here, and the two copies drift silently.

## 2.212.0 — 2026-09-16 16:10: Batch 415 — Shield Bump guard no longer scales with the car; brake lights redrawn

Two gameplay-visual bugs reported from actual play.

**The Shield Bump guard was sized from the car's own width** (`scale = bw / 16`), so a 22px-wide Monster Truck projected a guard 37% wider than a normal car's and it read as enormous in play. That scaling had no justification: the guard is a projected energy field, not bodywork, and nothing about the vehicle carrying it should change its size. Worse, `ramGuardContact()`'s actual reach was never width-derived — `SB_GUARD_REACH_PX` is a flat constant — so the visual had been overstating the hitbox on wide cars and understating it on narrow ones. Pinned to `scale = 1`, the reference width the guard art was drawn for. Verified identical at 18px across a 22px Monster Truck, a 14px stock car and an 8px Jet Bike. **This brings the visual back in line with the existing hitbox rather than changing gameplay.**

**Brake lights redrawn with a centre-weighted falloff.** The old version painted a flat full-width bar across the entire tail plus two bright squares hard against the outer corners, so braking lit up the whole back of the car and the corner blocks read as a second pair of lamps — the "four backlights" reported. Now three concentric alpha bands (0.18 / 0.32 / 0.55) centred on the car's midline, stopping short of the flanks, with a solid core at the centre.

One correction during the work: the first attempt used two solid lamps either side of centre, which left the middle *dimmer* than its flanks — inverting the brightest-in-the-middle falloff the fix is for. Pixel-dumped at three car widths, spotted, and replaced with a single central core. All bands derive from the car's own width, so it works from an 8px Jet Bike to a 22px Monster Truck with no per-car art — which matters given the 52-car roster and the standing constraint against per-car artwork.

Verified live in a real run on the Monster Truck: guard renders at fixed width with `sbGuardPhase: 'hold'`, braking triggers the new glow, the run survives both. Zero console errors.

## 2.211.8 — 2026-09-16 15:50: Batch 414 — STATS renamed to STATISTICS everywhere

Closes a PLAN.md item open since 2026-09-15, where the user leaned toward the rename but left it as an open question rather than a decision, so it was held. Now confirmed.

The inconsistency was real and already visible in the product: the Scores screen's own jump-to button has always read **STATISTICS**, while the main-menu button read **STATS** and the screen's heading read **Stats** — three spellings of one destination, two of them disagreeing with the third.

Renamed the menu button (`STATS` → `STATISTICS`) and the screen heading (`Stats` → `Statistics`). The Scores screen's button already used the long form and is unchanged. Checked every other surface for stragglers — the Garage, the result screen's SCORES button, the pause screen and the tutorial copy contain no references to the old name.

Internal identifiers (`statsBtn`, `statsView`, `showStats()`, `statsState`, `allTimeStats`) deliberately keep the short `stats` prefix: they are not player-facing, and renaming ~200 references would be pure churn with a real chance of breaking `localStorage` keys that carry live save data.

Verified live: menu now reads START RUN / SETTINGS / SCORES / STATISTICS / GARAGE / DAILY GIFT / ACHIEVEMENTS / MISSIONS / TUTORIAL; the screen heading reads Statistics; the Scores screen's STATISTICS button still opens it. Zero console errors.

## 2.211.7 — 2026-09-16 15:35: Batch 413 — Achievements settings gear redrawn, box removed

Closes a PLAN.md item open since 2026-09-13 ("better setting icon", corrected by the user to mean the Achievements tab, not the Garage), which had been parked waiting on what "better" meant. Now specified directly: make it read as a settings gear, sharpen it, and drop the box around it.

**The icon was blurry, and not only blobby.** The `<svg>` was 16x16 CSS pixels over a `0 0 14 14` viewBox — every pixel scaled by 16/14 = 1.143. Non-integer scaling of pixel art is exactly what softened the jump sprite in Batch 409, and the same mistake was sitting in this icon. The viewBox is now 16 units at 16px, 1:1.

**Redrawn as an actual gear.** The old shape was four edge nubs, four corner squares and a square body, all overlapping with no gaps — a lumpy cluster rather than a gear. It is now an octagonal hub with four square-cut cardinal teeth standing clear of it, four smaller diagonal teeth between them, and an octagonal bore punched through the centre. The gaps between teeth are what make the silhouette read as a gear at 16px, so the hub is deliberately kept inside them; the octagonal bore stops it reading as a square nut.

**Box and frame removed**, as asked: no background, no border. The 34px hit area is kept — a 16px tap target is too small — it just isn't drawn any more. Hover brightens the glyph via opacity rather than recolouring rects, since the bore is punched with panel-coloured fills and a "recolour everything except those" rule would be fragile.

Verified: button computes to transparent background with 0px border at 34x34; svg is 16x16 over a 16-unit viewBox; the rendered shape dumps as eight distinct teeth around an octagonal hub with a clear centre hole; clicking still opens the number-display panel. Zero console errors.

## 2.211.6 — 2026-09-16 15:15: Batch 412 — Shield Bump illustration scaled down to match its neighbours

Direct report: the Shield Bump image is far too big. Measured against every other illustration on the screen, it was — 66x111 rendered, where the cards around it sit at 42x72 and 42x78. Half again as large in both axes, so it dominated the column.

Two things compounded at the shared `TUT_SPRITE_SCALE`: the Monster Truck is natively 22px wide against an ordinary car's 14, and Batch 411's deployed guard adds another 9 rows of height on top of that. The shared scale exists (Batch 399) so genuine size differences between cars read honestly, but that argument doesn't apply here — this card is about the ability, not about how big the truck is.

Dropped one **integer** step for this card only, landing at 44x74, in line with its neighbours. Integer specifically: Batch 409's jump-sprite blur came from fractional scaling putting pixels off the device grid, and the same mistake was available here.

Verified: renders 44x74 against 42x72 (HOW YOU DIE) and 42x78 (CLOSE CALLS); guard still reads clearly as a tapering wedge above the nose at the smaller scale, confirmed by pixel map rather than by pixel count. Zero console errors.

## 2.211.5 — 2026-09-16 15:05: Batch 411 — Tutorial illustrations: real Shield Bump guard, no floating shadow, MASTER cards stop repeating

**SHIELD BUMP now shows the ability, not a parked truck.** The Monster Truck is drawn with its push-guard deployed, using `sbGuard()` at depth 8 — the same renderer and the same full-extension value the live `hold` phase uses — so the card illustrates the actual mechanic rather than a mock-up of it, and cannot drift from how the ability really looks. The canvas grew 9 native pixels upward to give the guard room ahead of the nose.

**JUMP loses its ground shadow.** `drawPixelCar()`'s jump branch casts a shadow onto the road below, which is correct in play and wrong on a card with no road — it read as a detached grey smear beneath a floating car. Suppressed with a `suppressJumpShadow` flag the shadow renderer checks, rather than forking a copy of the car renderer that could silently drift from the real one.

**The two MASTER cards no longer share an image.** THE AMBULANCE TRADE showed a coin, which represented neither side of the trade it describes (energy versus money), while READ THE ROAD held the only ambulance. Swapped: the ambulance moves to THE AMBULANCE TRADE, where the card is genuinely about ambulances, and READ THE ROAD takes the breakdown warning sign via `drawWarningSign53()` — fitting, since that card is about reading the road's signals (the flashing lane, the warning sign) rather than about ambulances specifically. Every card again has a distinct illustration.

**DAILIES renamed to THE FAST WAY TO GET RICH.** Direct feedback that "Dailies" describes a menu rather than a reason to care. The card's whole point is that three coin missions pay 350,000 in a day while grinding runs pays a fraction of that, so the title now says so.

Verified live: guard renders as a tapering wedge above the truck's nose (confirmed by pixel map, not just a pixel count); the jump sprite shows thruster flame and no shadow blob; all four illustrations paint; card labels and contents-rail entries still match exactly. Achievements 48 cards, Missions 6, run starts. Zero console errors.

## 2.211.4 — 2026-09-16 14:40: Batch 410 — Daily Word truck icon fixed (same CSS cause), in-game version un-drifted

**The "grey pixels beside the headlights" on the Daily Word track icon — fixed, and it was never an art problem.** This has been in PLAN.md since 2026-09-08 and earlier attempts to fix it by redrawing the sprite failed, because the sprite was never wrong. `drawWordTrackIcon()` deliberately `clearRect()`s its four corner pixels to round off the silhouette. `.dg-word-tiles-car` never opted out of the global `canvas { background-color: #5a5f66 }` rule, so those four cleared pixels rendered as grey squares. Identical root cause to the tutorial sprites in Batch 408, and to the trap this file already documents above `.coin-icon`. One declaration.

Swept the whole stylesheet for the same pattern afterwards — any rule styling a canvas with `image-rendering` but no `background`. One other hit: `.dg-reveal-car canvas`, the Daily Gift reward-reveal sprite. Fixed pre-emptively; it would have shown the same grey behind any transparent pixel in a revealed car.

**In-game version number was four releases stale** — the menu footer still read `v2.209.3` while CHANGELOG.md was on 2.211.3. Direct catch by the user. Fixed and future-proofed: a single `GAME_VERSION` constant now writes itself into the footer at startup, so the number cannot drift from a hardcoded string again. Same class of bug as the stale hardcoded figures fixed in Batches 404/405, and the third time this shape has come up — the fix is always to generate rather than transcribe.

On process, also raised directly: PLAN.md and CHANGELOG.md have been updated every batch, but the version string was a separate manual step nothing enforced, which is exactly why it drifted. It is now automatic.

Verified live: footer reads v2.211.4; the word-track icon's canvas computes to `rgba(0, 0, 0, 0)` with all four corner pixels transparent; zero console errors.

## 2.211.3 — 2026-09-16 14:15: Batch 409 — stripSpriteOutline removed (it was eating bodywork), sticky hover, jump blur, caption legibility

**`stripSpriteOutline()` deleted — it was destroying the sprites it was meant to tidy.** Direct report: the Monster Truck and the F1 "lack the black frame". They weren't missing one; it had been removed, along with real bodywork. Measured at native resolution: an ordinary car carries ~68 pure-black pixels (its outline), but the Monster Truck carries **160** and the F1 **176**, because their tyres, wings and body panels are drawn in that same pure black and touch the perimeter. A flood fill from the canvas edge cannot tell "frame" from "car", so on those two it ate structure.

The function only ever existed because of the grey-background hunt, and Batch 408 established the grey was a CSS rule, not the outline. Keeping it afterwards was justified on the weaker argument that the outline "reads as a frame on a card" — but the outline is not decoration, it is how these sprites are drawn, and the Garage renders them with it intact. Removed, with a comment recording why so it doesn't get reinvented. Sprites now render exactly as the Garage renders them.

**Contents hover is now sticky.** Direct request: the marker moves only when you point at a different card, and stays where it was when the pointer leaves the document, so moving the mouse away to read no longer snaps the list back to the top. It resets to the first entry when the screen is re-entered.

**Jump sprite blur fixed.** `drawPixelCar`'s `isJumping` branch applies a fractional `liftScale` of 1.08 around the sprite's centre, so pixels landed off the device grid and the browser resampled them — soft edges on otherwise crisp pixel art. It was also being drawn one scale step smaller than every other sprite, compounding it. Now drawn at the shared `TUT_SPRITE_SCALE` with the flight-height offset floored, keeping the composition on integer pixels.

**Tier heading shadows at 1px.** The shared `h3` treatment the Garage and Scores screens use (16px, 2px offset) is tuned for a *red* shadow on white; these headings use bright mint/amber/blue, which at the same offset read far heavier. The colour, not the geometry, is what made 2px look overdone here — 1px at the same size lands where the Garage does perceptually.

**"AT 200 KM/H" caption made legible** — was 7px in `--c-text-faint`, the dimmest colour in the palette. Now 9px in `--c-text-dim`; it captions a 36px figure and should be readable without leaning in.

**CLOSE CALLS art swapped** from the Convertible, which reads oddly from directly above, to the Muscle car. Knock-on swaps kept every card's vehicle distinct (HOW YOU SCORE takes the Stripe, STAY CLOSE takes the Rally).

Verified live: marker starts on THE WHEEL, follows card hover, and holds position when the pointer leaves; Monster Truck back to 1,440 black pixels and F1 to 1,584 with edges intact; all canvases still compute to transparent; shadow 1px; caption 9px `rgb(154,163,178)`; jump canvas now 66x120 at whole-number scale. Achievements 48 cards, Missions 6, run starts. Zero console errors.

## 2.211.2 — 2026-09-16 13:55: Batch 408 — The grey background was CSS, not pixels; card hover drives the contents list

**The grey background, finally diagnosed correctly — it was never in the sprites.** Three batches were spent attacking the pixels (matching the cell to the outline in 401, flood-filling the outline away in 406, fixing that fill's threshold in 407). Reading the canvas's *computed style* instead of its pixel data found the real cause immediately: `getComputedStyle(canvas).backgroundColor` returned `rgb(90, 95, 102)`. The global `canvas { background-color: #5a5f66 }` rule — which exists for the main game canvas — applies to every canvas on the page, so every transparent pixel in every tutorial sprite was showing grey. One declaration fixes it: `.tut-art canvas { background: transparent }`.

This file already documents the exact trap, in a comment above `.coin-icon`: *"background:transparent needed on every small icon/sprite canvas below — the global canvas{background-color:#5a5f66} rule otherwise leaves a gray box behind anything drawn with transparency."* Every other icon class in the file opts out. The tutorial's rule, written from scratch in Batch 401, simply never did. The lesson recorded here for the next time: when something looks like a rendering problem, check the element's computed style before its contents — three batches of pixel work would have been avoided by one style read.

`stripSpriteOutline()` is kept, with its comment corrected. It did not cause and did not fix the grey, but it does something worth doing on its own terms: without it, the sprite's gameplay outline (drawn to separate a car from asphalt) reads as a hard rectangle around the art on a card. Two separate problems that happened to look identical.

**Contents highlight now follows the CARDS, which is what was asked for twice.** Batches 406 and 407 wired hover onto the rail entries — so hovering an entry highlighted that same entry, which is just a hover state wearing the active marker's clothes, and told the reader nothing. The listeners now live on the cards: pointing at an article in the document highlights its entry in the list. Pointing at the list itself deliberately does nothing beyond a text-colour affordance, since the list already knows where its own entries are. With the pointer away from the document, the first entry is marked as the start.

Verified live: all 16 tutorial canvases compute to `rgba(0, 0, 0, 0)`; hovering card 7 highlights CLOSE CALLS and card 13 highlights STAY CLOSE, STAY PAID; moving the pointer off the document returns the marker to THE WHEEL; hovering a rail entry leaves the marker where it was. Achievements still renders 48 cards, Missions 6, a real run still starts. Zero console errors.

## 2.211.1 — 2026-09-16 13:35: Batch 407 — Four corrections to the tutorial, three of them self-inflicted

**The sprites went grey — my own Batch 406 fix caused it.** `stripSpriteOutline()` matched "near-black" as anything under RGB 45. But `bodyShell53()` paints the wheels in `#111` (17,17,17) at x=0 and x=13 — i.e. ON the outer ring, directly touching the outline. The flood fill flowed straight through them, erased every wheel, and continued into any `#111` detail they connected to, leaving just the mid-tone body colour. That is the "you made it worse, almost everything is grey now" report, and it was a threshold chosen carelessly rather than derived. The outline itself is pure `#000`, so the test is now `< 10`: the frame goes, the wheels stay. Verified by dumping the rendered sprite as a pixel map — the black rectangle is gone from all four edges, and the wheel pixels are present on both sides at both axles.

**Heading shadows — reverted to the reference the user named.** Batch 406 cut them to 1px, which made them nearly invisible. The user pointed at the Scores screen as the one that reads correctly: that is `h3`, 16px Silkscreen with `text-shadow: 2px 2px 0`. The tutorial's tier headings were 14px with 2px letter-spacing, and it was the small size plus wide tracking — not the 2px offset — that made the same shadow read as doubled text. Now 16px/1px-tracking/2px-shadow, matching Scores exactly, and the panel-title override is deleted so `.dg-title` uses its own identical treatment.

**Rail hover was working; it was invisible.** The logic had been right since Batch 406 (hovering entry 6 did make entry 6 active), but `:hover` and `.tut-rail-on` both set `background: var(--c-card)` and near-identical text colours, so moving the highlight produced no visible change. Active now gets a filled tier-coloured left edge, white text and the lifted background; plain `:hover` is a subtle 3% tint for entries you are merely passing over. Verified: the active marker moves from THE WHEEL (mint, BEGINNER) to SHIELD BUMP (amber, INTERMEDIATE) on hover, and returns to the first entry on mouse-out.

**"START DRIVING" removed.** Always BACK now. The button was wrong on its own terms — this screen is reached from the menu and returns to the menu, so a button promising to start a run described something it does not do.

**Jump energy copy fixed and generated.** It read "Take-off needs 3 cells of energy", which is right in count but was stated bare, inviting exactly the doubt raised. `ABILITY_MIN_ENERGY = ceil(3 * ENERGY_PER_CELL)` = 34% of a 9-cell bar, so three cells is correct — but the figure is derived, and has already moved once when the bar went from 10 cells to 9. It now reads "3 of the bar's nine cells", written in from the constant at render time rather than typed into prose.

Verified live: BACK button non-primary, jump copy reads "3 of the bar's nine cells", both shadows compute to 2px at 16px, sprite edges clear with wheels intact (180/234/576 dark pixels retained across three sprites), hover moves the active marker with a visible colour change, Achievements still renders 48 cards, Missions 6, and a real run still starts. Zero console errors.

## 2.211.0 — 2026-09-16 13:10: Batch 406 — Box-exclusive cars discoverable; tutorial sprite outlines stripped; rail hover; tighter heading shadows

**Box-exclusive cars are now found on the road, then unlocked from boxes.** Direct design change, and it also resolves the inconsistency the Batch 405 audit surfaced (copy claimed these cars never spawn as traffic; `GARAGE_NPC_RARITY`, the map written to exclude them, was never actually read, so they always did). Three states, all verified:
- **Never spotted** — sealed crate tile, as before. Clicking now says "A sealed crate. Spot this car out on the road to find out what it is," replacing copy that named the Daily Word as the only source (wrong: Extra Box is also a source, and the car was visible in traffic anyway).
- **Spotted, not owned** — the real car, named, with **LOCKED** where a price would be. Deliberately not its `unlock` value: `canAffordCar()` refuses `boxOnly` regardless of balance, so showing a number would advertise a purchase that can never happen. Clicking gives a LOCKED dialog naming the two real sources, rather than the "not enough coins" dialog, which would be actively misleading.
- **Won from a box before ever being spotted** — immediately owned and drivable, per the user's own preference of the two options offered. This needed no new code: `isCarDiscovered()` already returns true for any owned car, so ownership implies discovery.

**Tutorial sprites: the grey background, correctly diagnosed at last.** Two earlier attempts missed it. The sprites are not haloed and the cell is not tinted — every vehicle is drawn as a filled rectangle wrapped in a hard black border (`bodyShell53`), because in gameplay that border is what separates a car from grey asphalt. Lifted onto a dark card, that border stops reading as an outline and reads as the edge of a black box around the car. Verified by dumping a sprite's pixel map at native resolution: the Tow Truck fills its full 18x34 bounds with a solid black ring.

Fixed with `stripSpriteOutline()`: flood-fill inward from the canvas edge through near-black pixels and clear them. Only outline pixels *reachable from outside* are removed, so interior black survives — windows, wheel wells, grilles, the steamroller's drum shading all still render (verified per-sprite: 252 interior black pixels kept on the convertible, 270 on the steamroller, 108 on the muscle car). Applied to all four draw paths (cars, ambulance, coins, the jumping car). 15 of 16 canvases now have fully transparent edges; the 16th is the jump sprite, whose thruster flame legitimately touches the frame.

**Contents rail: scroll-tracking replaced with hover.** Direct request. The auto-tracking was solving a problem the reader doesn't have — they know where they are, they just scrolled there — while creating one they do: the highlight moved on its own, and entries at the scroll extremes could never be selected. The list now marks the first entry as the document's start, and hovering marks whatever you point at, so the highlight only moves in response to a deliberate action. The scroll listener is gone entirely.

**Heading shadows tightened from 2px to 1px** on both the tier headings and this screen's panel title. At 2px the coloured shadow separated far enough from the glyph to read as a second overlapping word rather than depth, which made the headings harder to read. 1px keeps the pixel-art depth cue without the doubling.

Verified live: all three box-only tile states render correctly (crate / real car + LOCKED / owned), sprite edges transparent with interior detail intact, rail highlights the first entry and follows hover without reacting to scroll, both shadows compute to 1px, Achievements still renders 48 cards, Missions 6, and a real run still starts. Zero console errors.

## 2.210.8 — 2026-09-16 12:20: Batch 405 — Stale-copy audit: 5 wrong statements fixed, 12 hardcoded numbers made generated

Batch 404 was the third instance of one bug shape: player-facing prose holding a hand-copied value that the code later changed. A full audit of every numeric or factual claim in the UI was run against its governing code path. Results below; each was verified individually before being touched.

**WRONG, now fixed:**

- **`use_bars` mission hint** said *"Jump/shot only — ramming doesn't count."* Ramming does count: the Shield Bump activation increments `barsUsedThisRun`, with the kill refund netting back out of the same counter — the in-code comment at that site literally reads "direct correction: ramming DOES count". The hint, and the stale sibling comment above the mission definition still claiming ramming was "deliberately excluded", both predate that reversal. Hint now reads "Ramming counts, minus what its kills refund."
- **Stats day-streak hint** said *"Days you played at least one run"*. A run only counts once it clears `dailyScoreThreshold()` — merely finishing a run does not keep the streak alive. The Daily Gift card's own copy already described this correctly, so the two screens contradicted each other. Now "Days a run of yours beat the daily target".
- **JACKPOT achievement** said *"Win a car from an Extra Box or Daily Gift."* `REWARD_WEIGHTS.daily` has no car tier at all (`{ xp: 50, coins: 40, color: 10 }`), so the Daily Gift can never award one; the actual second source is the Daily Word. Corrected.
- **Ability bar tooltip** was a static `title="Tap and hold to fly"`, never updated in JS — wrong for all 9 `ramAbility` cars, where the bar is a ram/shoot control. Now ability-neutral.
- **Tutorial batch count** read 401, written during Batch 397. Updated, and the adjacent line-count claim softened to "over twelve thousand" so a precise figure isn't load-bearing in prose that nothing updates.

**Hardcoded but correct — now generated, so they cannot drift:**

New `renderTutNumbers()` writes twelve tutorial figures from their constants instead of them being typed into the copy: per-vehicle points from `VEHICLE_POINTS`; per-pass and jump-over coin values derived the same way the credit code derives them (`pts/10` and `pts/2`, times `COIN_EARN_SCALE`); the close-call base from `CLOSE_CALL_BASE_SCORE`; the mission ladder and its total from `MISSIONS_LADDER_COINS`; roster and biome counts from `GARAGE_CARS.length` / `BIOME_DEFS.length`. The mission-ladder figures are the same values Batch 404 had just finished de-hardcoding one screen over — they had been hand-copied into the tutorial too.

Mission-ladder totals use `coinDisplay()` (so they honour ABBREVIATE MONEY); the small per-pass values are deliberately left exact, since abbreviating 1250 to "1.25K" is longer to read and less precise than the plain number.

Three achievement thresholds that encoded content counts now read them: `adventuring_time`'s description uses `BIOME_DEFS.length`, `collector`'s diamond/amethyst tiers derive from the buyable and total roster sizes, and `full_palette`'s gold tier uses `GARAGE_COLORS.length`. Previously, adding a 53rd car or a 12th paint would have silently made two achievements unreachable at 100% while their text kept quoting the old totals.

**Also found, needs a product decision — not changed:** the Garage's crate-locked dialog says a box-only car "can only be found as a Daily Word reward", and a code comment claims box-only cars no longer spawn as NPC traffic. Neither is true in the current code: the NPC pool is built with `GARAGE_CARS.filter(c => c.rarity)` and does **not** exclude `boxOnly`, and `GARAGE_NPC_RARITY` — the map that was built to do that exclusion — is never read anywhere. So box-exclusive cars (including the Tank) do appear in traffic, which undermines the whole "???" reveal. This is a code bug rather than a copy bug and could be fixed either way; logged in PLAN.md rather than guessed at.

Verified live: all twelve generated values match their constants (points 10/20/50, coins 50/100/250, jumped ambulance 1,250, close call 100, ladder 50K/100K/200K totalling 350K, 52 cars, 14 biomes); Collector tiers resolve to 5/15/30/39/52 and Full Palette to 3/7/11; all four corrected strings read correctly; the Achievements screen still renders 48 cards, Missions still renders 6, and a real run still starts and reaches speed. Zero console errors.

## 2.210.7 — 2026-09-16 11:55: Batch 404 — Daily Missions "?" panel: correct rewards, generated not hardcoded

Direct bug report: the Missions help panel (the "?" hover) advertised a 100 → 200 → 400 claim ramp and "700 coins" for clearing all six. Both were the pre-rescale numbers. `MISSIONS_LADDER_COINS` has been `[50000, 100000, 200000]` since Batch 332's economy rescale (×500 on the coin ladder specifically, so missions would stay the deliberate fast track), meaning the panel had been **understating the coin reward by 500x** — it promised 700 where a full day actually pays 350,000.

Root cause was that the panel was static markup holding copies of numbers that live in code. Fixed by deleting the hardcoded block and generating the body from the ladders themselves (`renderMissionsHelp()`, called at the top of `renderMissionsView()`), so a future rebalance cannot leave this text stale again — the same class of drift that produced the stale README claims corrected in Batch 397.

The panel also only ever showed ONE ramp, silently implying coins and XP shared it. They haven't since Batch 333 split the ladders. It now shows both, labelled, so the "count separately" sentence underneath is actually demonstrated rather than asserted.

Abbreviation, per the same request: coin figures run through the existing `coinDisplay()`, so they honour the ABBREVIATE MONEY setting like every other coin total in the game — "50K → 100K → 200K ... pays 350K coins" with it on, exact comma-separated numbers with it off. XP is deliberately left exact in both modes, since XP is never abbreviated anywhere else and its numbers are small enough not to need it. The mission cards' own reward chips were already correct (they have used `coinDisplay()` since Batch 335) — only the help panel was wrong.

Verified live in both modes: abbreviated shows 50K/100K/200K and a 350K total; with ABBREVIATE MONEY off the same panel reads 50,000/100,000/200,000 and 350,000; XP stays 100/200/400 and 700 in both; mission chips render +50K and +100 XP as expected. Zero console errors.

## 2.210.6 — 2026-09-16 11:40: Batch 403 — Tutorial polish: frameless art, sidebar collapse, tab row removed, Tank card cut

Fourteen review items from one message, worked through in order. Two of them were questions, answered from code before anything was built:

**"Are close calls really 100 x multiplier?"** Yes — `CLOSE_CALL_BASE_SCORE = 100` (L2712), awarded at L11381 as `CLOSE_CALL_BASE_SCORE * multiplier`. At a x4 multiplier one close call is 400 points, versus 10 base for an ordinary car — a single close call is worth roughly ten overtakes, and also refunds 4 energy cells. The tutorial figure was correct. Flagged separately as a balance observation, not touched: close calls are the most lucrative repeatable event in the game by a wide margin.

**"Should the Tank even be in the tutorial?"** No — card removed, per the user's own reasoning. `{ key: 'tank', ..., boxOnly: true }` (L5376) is one of 13 box-only vehicles: never spawns as traffic, cannot be bought at any price, so a new player has no route to it and no way to learn it exists. Teaching an inaccessible mechanic is noise in a beginner document and spoils a discovery. The Shield Bump card stays (9 ram cars, most obtainable normally). The Tank's one genuinely useful quirk — the barrel is not part of the hitbox — is lost with it; accepted trade.

**Art frames removed entirely.** `.tut-art` loses its border and background; sprites now sit directly on the card. This is also the correct fix for the reported "grey background pixels", which Batch 401 had only papered over: every sprite carries a baked-in black outline (`sil53()`, drawn for contrast against the road), and the black art cell was *hiding* that outline by matching it. With no cell at all the outline reads as the sprite's own linework — which is what it is. The fixed 108px column stays so copy still aligns down the page.

**Sidebar collapse reworked.** The toggle now spans the rail's full width at its head (was a footer button next to BACK), labelled `« COLLAPSE`. Collapsing replaces the rail with a narrow full-height `»` tab in the same position, so the control to restore it is where the sidebar was.

**Tier tab row removed** (direct request). Every section is always rendered in difficulty order; the contents rail is the only navigation. Removes `tutTab`, the tab buttons, and the `.tut-filtered` heading-suppression path.

**Rail highlight dead zone fixed — a real bug the user found.** The old rule picked the last card whose top was above a 70px line, so once the scroller hit its maximum the final cards could never cross it and the entire ABOUT group could never highlight, even after clicking it in the rail. Now: at the bottom of the scroll the last entry is selected outright; otherwise cards are scored by how much viewport height each occupies, which is stable regardless of card size. The active entry also scrolls itself into view within the rail.

**Art, one distinct vehicle per card.** Repeats were flagged directly — the ambulance appeared on both MASTER cards, and the jetbike/roadtrain pair was reused across three. Now: Tow Truck + Muscle for HOW YOU SCORE (a truck that fits the column, and a car standing in for the reckless driver, replacing the road train and the bike); Convertible for CLOSE CALLS; Stripe + Wagon for STAY CLOSE; a coin for THE AMBULANCE TRADE (it is about the payout); Steamroller for DRAWN IN CODE. The JUMP sprite is drawn one scale step down in a derived 22x40 box, positioned low so the lift reads as height, showing the whole car and thruster rather than a cropped fragment.

**DAILIES copy** trimmed per the user's own conclusion: the Daily Gift/Word reward detail is gone (the Daily Gift tab already shows exact drop chances, so repeating them duplicates a source of truth that can drift). Kept the motivating fact — three coin missions a day pay 350,000 — plus that missions ask you to play, not to win.

One real bug introduced and caught during this batch: removing the Tank card left an orphaned `</div>` that closed the ADVANCED section early, pushing DAILIES outside it in the DOM (18 cards but only 17 rail entries). Found by cross-checking card count against rail count rather than by eye; fixed before commit.

Verified live: 18 cards and 18 rail entries in agreement, no Tank card, zero blank canvases, art cells computing to transparent with no border, collapse and expand both working, and scrolling to the very bottom now correctly highlights THE PRICES ARE REAL. Zero console errors.

## 2.210.5 — 2026-09-16 10:50: Batch 402 — ABOUT section rewritten as actual background, not more tips

Direct correction: the ABOUT tab had drifted into being more gameplay information (roster mechanics, discovery rules, pricing as a buying consideration). It was explicitly not meant to help you play — "just some interesting facts about the game, how it was created."

Rewritten as five cards, none of which carry gameplay advice:

- **WHERE IT CAME FROM** — the stated inspiration: the tiny preloaded driving games on old handsets, a few lanes and one question, how long can you last. Framed as "this is that game, given somewhere to grow." Deliberately does not name a manufacturer, per the user's own "Nokia-like, but not the Nokia" phrasing.
- **IT STARTED AS A CAPTCHA** — start date **21 August 2026**, verified against this file's own oldest entry (`1.0.0 — 2026-08-21 (baseline)`) rather than taken on trust. The baseline and Batch 1 entries record that the original build was disguised as a "prove you're human" widget with a fake browser frame and the instruction *steer the car and don't crash* — removed on day one. That detail came out of the changelog, not from memory.
- **DRAWN IN CODE** — no image files, no audio files; sprites are rectangles drawn in code and the music is generated live.
- **BY THE NUMBERS** — 401 batches, 52 vehicles, 14 biomes, 12,000+ lines, and the changelog now being several times longer than the game.
- **THE PRICES ARE REAL** — real-world pricing, and the honest consequence that rarity and price disagree (Batch 345's known side effect, presented as trivia rather than as a shopping tip).

Each card gets its own illustrative sprite instead of repeating the Jet Bike / Road Train size-contrast pair borrowed from the gameplay tabs: the plain Stock car for the origin story, a Hot Hatch for the CAPTCHA-era build, the Road Train as the most elaborate procedural sprite in the roster, and the F1 for the price card.

Verified live: 5 ABOUT cards with correct titles, all 4 sprites painting (2,988 / 2,736 / 7,524 / 3,546 px), the rail filtering to exactly those 5 entries, 19 cards and 19 rail entries in the combined ALL view, zero blank canvases anywhere, zero console errors.

## 2.210.4 — 2026-09-16 10:30: Batch 401 — Tutorial redesign: side contents rail, tier colours, fixed sprite framing

Direct feedback on the Batch 397-400 screen, addressed point by point.

**The "gray background pixels" — real cause found.** Every vehicle sprite in this game carries a baked-in black outline (`sil53()`, drawn so cars read against the road). Rendered on the `--c-night` art cell, that outline sat one shade off the background and read as a halo of loose grey pixels around the shape — reported on the Jet Bike, the coin and the Monster Truck, i.e. every sprite, not a per-sprite art bug. Pixel sampling confirmed it: the sprites are genuinely transparent, the outline is part of the art. The art cell is now pure `#000`, so the outline disappears into the background and the sprite reads as cut out. Nothing about the sprites themselves changed.

**Controls keycaps** were a wrapped run of 8 pills in arbitrary order. Now a real 3-column keyboard cluster (arrow cross + a full-width SPACE), so it reads as a keyboard rather than a list of characters.

**JUMP's energy-bar mock removed** — direct feedback that it was oversized and read as a bar chart. Replaced with the actual car mid-jump: `drawPixelCar()`'s own `isJumping` branch, which draws the lift, ground shadow and thruster flame, so it shows the real in-game visual instead of a diagram of one.

**Art cell is now fixed 108x108 with the canvas scaled to fit** (`max-height:100%`), rather than a 96px box that tall sprites overflowed. A 180px Road Train and a 16px coin now sit in identically-sized frames; verified zero canvases overflow their cell.

**Contents moved to a book-style side rail** (direct request). One entry per line down a 180px left column, grouped under its tier, as a sibling of the scroller so it stays put while reading — replacing the wrapped pill row that sat on top of the content. The rail tracks reading position and highlights the entry for whichever card is at the top of the viewport, with a coloured left edge; rAF-throttled against scroll. A HIDE LIST / SHOW LIST toggle collapses it for a full-width read, and it auto-hides under 720px. Panel widened 880 -> 940px to pay for the rail.

**Difficulty colour ramp.** BEGINNER green (`--c-mint`), INTERMEDIATE amber, MASTER red — a gradient players already read as easy-to-hard before the label registers. ABOUT is deliberately outside the ramp (blue) since it isn't a difficulty. The colour is applied to the tier tab, the section heading rule and text-shadow, each card's 4px left border, and each card's label — so a card scrolled far from its heading still declares its difficulty. Reusing existing palette tokens, no new hexes.

**Highlighting cut from 48 to 29** — direct feedback that too many emphasised terms stop distinguishing anything. Bold-for-emphasis on ordinary words is gone; a single amber `.k` class now marks only the concrete numbers worth remembering (point values, energy costs, multipliers, timings).

Verified live: rail renders 16 entries under 4 correctly-coloured groups; all four tier colours present on card left borders; art cell computes to `rgb(0,0,0)`; no canvas overflows its cell; the jump sprite paints 3,896 pixels at 60x102; scrolling to 1,600px correctly highlights THE TANK in the rail; the toggle collapses the rail and swaps its label; zero console errors.

## 2.210.3 — 2026-09-16 03:55: Batch 400 — Tutorial defaults to ALL, ordered by difficulty

Direct request: "the default sort order should be by like level but default should have it all but listed in correct order depending on hardness."

New **ALL** tab, now the default view and the first tab in the row: every section rendered at once in difficulty order — BEGINNER → INTERMEDIATE → MASTER → ABOUT — rather than opening on a single tier and requiring tab clicks to discover the rest. The four tier tabs remain as filters on top of that, not as the primary way in. `showTutorial()` resets to ALL on every entry (including the forced first-launch pass), so a first-time player sees the whole ordered syllabus immediately.

Each section gained a tier heading (`.tut-sec-head`, Silkscreen 13px with the red pixel text-shadow used by panel titles) plus a one-line description of what that tier covers. Headings are hidden via `.tut-filtered` when a single tier is selected — the tab itself already names it, so repeating it as a heading would be noise. Consecutive visible sections get 26px of separation so the tiers read as distinct blocks in the combined view.

The contents list (Batch 399) now spans every visible section rather than one. In ALL it runs to 16 entries, so each tier's entries are prefixed with a small non-clickable tier label (`.tut-toc-group`) — four ordered groups instead of one undifferentiated wall of buttons. Cross-tier jumps work: clicking a MASTER entry from the combined list scrolls the full 2,473px and lands the card at exactly the intended 8px offset. Tier order lives in one `TUT_ORDER` const that both the contents list and the section renderer read, rather than each hardcoding its own sequence.

`renderTutArt()` no longer scopes itself to a single visible section, since ALL makes that assumption wrong — it draws whatever is currently visible, and its id-based lookups no-op on anything absent either way.

Verified live: default view shows all four sections in the correct order with ALL as the amber tab; 16 contents entries under 4 correctly-named groups; card order matches the intended difficulty progression end to end; filtering to MASTER shows only its 4 entries with no group labels and no tier heading; a cross-tier jump lands at 8px with the flash applied; all 15 canvases paint in the combined view; zero console errors.

## 2.210.2 — 2026-09-16 03:40: Batch 399 — Tutorial: contents list, single sprite scale, per-tab art render, preview server

Direct feedback on the Batch 397 screen: "the design is bad — some of the images are like chaotic and look crazy... or they are missaligned", plus a request for a clickable table of contents. This batch fixes the measurable defects and adds the contents list; the **layout direction itself is still open** and deliberately untouched (options put to the user, awaiting a decision).

**Contents list (`.tut-toc`).** Per-tab, sits inside the scroller so it scrolls away once reading starts rather than permanently eating vertical space. Built FROM the cards in the DOM rather than a hand-maintained array, so adding/renaming/reordering a card updates it for free and the two can't drift. Clicking an entry scrolls its card to the top of the scroller and flashes its border amber for 1.2s — without the flash, a jump on a short tab can read as "nothing happened" when the target was already partly in view. Uses manual `offsetTop` arithmetic rather than `scrollIntoView()`, which also nudges the surrounding panel when called on a nested flex scroll container.

**Single shared sprite scale — this was the real cause of the "chaotic/mismatched" look.** Every illustration was previously sized by passing a max width/height box into `drawCarSpriteUpright()`, which picks its own integer scale per sprite to fit that box. A 14px-wide Jet Bike and a 44px-wide Monster Truck were each independently "fitted" and so landed on different scales, while the coin (drawn at a flat 3x) was 3x larger relative to its own art than any car — pixel art at three different pixel sizes side by side. Now a single `TUT_SPRITE_SCALE = 3` drives everything: `tutSprite()` hands `drawCarSpriteUpright()` a box that is exactly the sprite's native size x3, so its own floor() always lands on that scale for every car. Every pixel on the screen is now the same size, and the Jet Bike (24x60) vs Road Train (42x180) size contrast the copy talks about is finally real rather than flattened by per-sprite fitting.

**Art now renders per tab switch, not all upfront.** `drawCarSpriteUpright()` sets the canvas's CSS size at draw time, and a canvas inside a `display:none` parent has no layout — so drawing hidden tabs' art was unreliable. `renderTutArt()` now draws only the visible section, called from `renderTutTabs()` after the section is made visible. Also means only the visible tab's canvases cost anything.

**Preview server on port 8081** (`tools/preview_server.py`, stdlib only, gitignored). Serves a copy of the game re-synced on every request, so design work can be reviewed on 8081 while the real save stays untouched on 8080 — a separate port is a separate browser origin and therefore separate `localStorage`, which matters specifically because the forced first-launch tutorial WRITES `tutorialSeen` on dismiss.

**Two corrections to my own earlier claims, recorded because both were wrong and acted on:** (1) "11 of 15 canvases render blank" was a measurement artefact — the probe only read the visible tab, so hidden canvases reported 0x0 by definition; all 15 always rendered. (2) "The ambulance canvas is drawn twice and overwritten by a stock car" was false — ambulance art is natively 14x24, the same footprint as the stock car, so at 3x both produce a 42x72 buffer and I read matching dimensions as a bug. Verify that sprite by pixel colour, not size. Neither claim survived a real check; the per-tab render change is still correct on its own merits.

Verified live: contents entries exactly match card labels on all 4 tabs (5/5/4/2), a mid-list jump lands the target card at exactly the intended 8px from the scroller top, the end-of-list jump correctly clamps at the scroller's 464px maximum, the flash class applies, and zero console errors.

**Still open — the layout itself.** The honest shared scale makes the existing row layout's flaw concrete: a 180px-tall Road Train cannot sit in a fixed 96px art cell. Three directions offered (full-width art strip above copy / no art boxes at all / one topic per card, art-dominant), plus whether illustrations should be animated by reusing `drawMenuScene()`'s live scrolling road. Not guessed at — waiting on a decision.

## 2.210.1 — 2026-09-16 03:10: Batch 398 — Result screen: no "+0" progress rows, no bar for zero progress

Direct bug report with a screenshot: the post-run PROGRESS list showed HIGH FLYER at "0/50" with a "+0" delta and a visible bar sliver — progress toward a tier that hadn't actually moved at all.

Cause: a tierReset achievement whose run lands EXACTLY on a tier threshold. Clearing bronze (10) with exactly 10 jump-clears makes `overflow = after - tierGoal = 0`, so `appliedGained` (Batch 393's clamp, which correctly limits the delta to what really carried into the next tier) is 0 — but the row was pushed anyway. The existing `if (!gained) return;` guard can't catch this: `gained` is genuinely non-zero, it was just entirely consumed finishing the tier that's already listed under COMPLETED directly above. So the screen reported the same run twice — once as a real unlock, once as a meaningless zero-progress row.

Second, independent half of the same report ("no progress bar for +0"): `renderResultAchievements()` still had the `Math.max(2, ...)` bar floor applying at literally zero, forcing a 2% sliver. That is the exact floor Batch 394 removed from `achModel()` — it survived here because the result screen has its own separate renderer that Batch 394 never touched. Now floors only genuine (if tiny) progress, matching the Achievements tab.

The unlock itself is unaffected — a tier cleared exactly on the threshold still reports as COMPLETED, only the empty next-tier progress row is skipped.

Verified live in a headless browser across five scenarios, zero console errors: exactly hitting bronze (10 clears, 0→10) now shows the COMPLETED row only, no progress row; overshooting (12 clears) correctly shows "+2" at "2/50"; a non-tier-crossing run (3 clears) is untouched at "+3", "3/10"; exactly hitting silver from a mid-ladder start (40 clears, 10→50) also shows COMPLETED only; and a run with zero clears hides the whole box (`display:none`) rather than rendering an empty section.

## 2.210.0 — 2026-09-16 03:00: Batch 397 — TUTORIAL / HOW TO PLAY screen (forced first launch + menu button)

The `#tutorialBtn` placeholder reserved back at the menu-placeholder pass is now live. Built design-first per direct instruction ("first design it as best as you can and then give content"); full proposal in `docs/tutorial-design.md`, approved before any code was written.

**Shape — a `.view`, not a modal.** `#tutorialView` sits alongside Garage/Stats/Achievements using its own `.tut-panel`/`.tut-scroll` prefix pair duplicated from `.dg-panel`/`.dg-scroll` (the house convention `.stats-scroll` already documents — duplicate per screen, don't share). 880px max-width, added to the existing wide-screen selector list.

**Forced first launch works by ROUTING, not by blocking.** On init, if `allTimeStats.tutorialSeen` is false, `showTutorial(true)` opens the tutorial *instead of* the menu — so "nothing else is clickable until dismissed" is satisfied structurally, with no overlay and no input trapping. This was the reason for rejecting the modal approach outright: `#confirmOverlay` is both scrim-dismissible and Escape-dismissible, which would defeat a forced gate. In forced mode the footer button reads START DRIVING (`.btn-primary`) instead of BACK, and the Escape branch is deliberately inert. Dismissing sets the flag and routes to the menu via the standard `sizeMenuFrame()` + `refreshMenuSummary()` path.

`tutorialSeen` lives in `allTimeStats` rather than its own localStorage key, so it rides the existing `saveAllTimeStats()` write path; the `Object.assign(defaults, parsed)` load means existing saves pick it up as `false` with no migration — so a returning player sees it exactly once too.

**4 tabs** (BASICS / ADVANCED / MASTER / ABOUT) reusing `.ach-tabs`/`.ach-tab-btn` with the same imperative amber-active loop the Garage sort tabs use. Freely browsable with no completion gating — direct decision, since forcing a reader through three tabs to reach the road fights the game. Tab state is session-only (no persistence): a returning reader starts at BASICS, unlike Achievements where restoring your last filter is the useful behaviour.

**16 cards, single column**, each an art cell plus 2-3 short paragraphs — matching the "a few paragraphs, not a whole screen of text" requirement. Single column rather than `.dg-grid` because these are prose+art rows in a deliberate reading order, and it already reflows at 375px with no breakpoint.

**15 illustrations, zero image assets** — all live canvas, reusing existing renderers via a new 6-line `tutSprite()` wrapper over `drawCarSpriteUpright()`, plus `renderCoinIcon()` and `drawPixelAmbulance()` at an integer 3x scale. Rendered once per screen entry, no animation loop, so an open tutorial costs nothing per frame. Two new CSS-only mocks: pixel keycaps (`kbd.tut-key`, a miniature `.btn`) and a 9-cell energy bar using the live HUD's own red/amber/mint ramp.

**Content is code-verified, not README-derived.** Research pass (recorded in `docs/tutorial-facts.md`) found README.md stale in four places, so the copy states what the code actually does: there is NO survival/time score (points come only from passes, jump-clears, close calls, rams and Tank shots); there are THREE abilities, not one (Jump / Shield Bump / Tank Shot, chosen by the equipped car, not a setting); the jump gate is 3 cells / 34%, not 25%; and night mode is gone. **PLAN.md's own lane-routing tip was also backwards** — ambulances spawn behind the player and overtake upward (`y = canvas.height + 10`), so riding LOW puts you in their path first, not last. The MASTER tab states the corrected version; the PLAN entry has been fixed in the same pass.

**Also fixed, same batch (approved scope addition):** `achievementsView` was missing from the Escape-as-back if-chain entirely — Escape did nothing on the Achievements screen, unlike every other secondary screen. Found while mapping that chain for the tutorial branch; 5 lines, same code region.

Verified live in a real headless browser (Chrome via Puppeteer, 12-point suite, zero console errors): forced pass fires on a fresh profile and Escape genuinely cannot leak past it; all 15 canvases render actual non-transparent pixels (counted per canvas, none blank); all 4 tabs switch with exactly one section and one amber tab active; START DRIVING persists `tutorialSeen: true` and a reload then goes straight to the menu; the menu button reopens it in normal mode with a BACK button where Escape *does* work; the Achievements Escape fix confirmed working; a real run still starts and reaches speed (gameplay regression check); and no horizontal overflow at a 375px viewport.

## 2.209.4 — 2026-09-16 02:25: Batch 396 — Project moved into a Coder workspace (tooling only, no game changes)

Environment change only — `carCrash.html` itself is byte-for-byte untouched.

Development now happens in a Coder workspace (`husarp/game-dev`) instead of local files. Setup in `~/game/`:
- Live preview server on port 8080 (`python3 -m http.server`, stdlib only — the same Option A approach already recommended in PLAN.md's packaging section). Edits are picked up on browser refresh; no restart, no build step.
- Drag-and-drop upload page on port 8090 (`tools/upload_server.py`, ~150 lines, stdlib only). Needed because the chat's attachment allow-list rejects `text/html` outright and errored on `.md` — so the game file could not be transferred through chat at all. Files land in `incoming/`, or `assets/` with a checkbox.
- Git repo initialised, `.gitignore` for logs and `incoming/`. Each working state is committed, so a bad edit can be rolled back rather than described away — a genuinely new capability for this project.
- `AGENTS.md` added at the project root: standing rules the agent loads automatically — single-file constraint, no-frameworks rule, the mobile freeze, the three settled decisions that must not be re-litigated (free horizontal movement, banking tilt, night mode), the changelog format and batch numbering, and the house rule to answer questions rather than silently implement.

Workspace setup was not clean: three earlier workspaces failed before this one (agent never connected on the `docker` and `vscodeclaude` templates; a terraform failure on the flowMaster host). The working combination is the `monoflow-worker` template on the local host, which also provides Node v22.23.2 and Python 3.14.4 — relevant because the Capacitor/Tauri packaging work and the score-server work in PLAN.md can now actually be built and run here, not just researched.

PLAN.md gained a workspace/environment section and a new ONLINE LEADERBOARD / SCORE SERVER section (stated goal, deliberately left unscoped — the anti-cheat question is flagged as needing an answer before any API design, since client-side scores in a readable HTML file can be forged trivially).

## 2.209.3 — 2026-09-15 00:00: Batch 395 — Close-calls row revert, leaderboard perf box removed, stats empty-message fix

Three direct bug reports/requests, quick fixes pulled from a larger backlog dump (rest logged to PLAN.md):
- Result screen's CLOSE CALLS row reverted from "30× CLOSE CALLS" / points-in-red back to a plain "CLOSE CALLS" label with the raw count in red on the right — direct request, the points value ("something X") wasn't wanted there.
- Leaderboard/Scores per-row Performance Score cell (`.lb-perf`) no longer has its own background/border-left box — direct feedback it "looks kind of weird" as a standalone box; now sits plain like every other column (weight, car, etc.).
- Stats chart's empty-state message ("No runs yet — play a few to see your history here") was showing even when real runs exist but the current view has nothing yet — e.g. AVERAGE OF 50 with fewer than 50 scored runs. Now checks `runHistory.length` and shows "Not enough runs yet for this view — play more to see it here." in that case, reserving the original message for genuinely zero runs.

## 2.209.2 — 2026-09-13 00:00: Batch 394 — Zero-progress achievement bars, REACH X KM/H mission wording

Direct bug report: an achievement's progress bar showed a small visible sliver even at literally zero progress — the "never fully vanish near 0%" floor (Batch-era `Math.max(3, ...)`) was applying even when there was nothing to floor. Now only kicks in once there's genuine (if tiny) progress; exactly 0 renders an empty bar. Fixed in both `achModel()` branches (tiered and single-goal secrets).

Direct bug report: the REACH X KM/H daily mission's hint read "Capped by your fastest owned car" — an internal implementation detail (why the goal is capped) that isn't useful to the player; changed to "Best single run counts," matching the wording style already used for the same "best value, not cumulative" behavior on SURVIVE X SECONDS.

## 2.209.1 — 2026-09-13 00:00: Batch 393 — Results-screen delta badge clamp + custom scrollbar

Direct bug report: crossing a tier mid-run (e.g. earning 10,500 coins and clearing BUSINESSMAN's bronze tier at 10,000) showed "+10,000" next to the silver-tier progress bar even though only 500 of those coins actually carried over into silver's progress. The badge was reading the full raw amount gained this run instead of the overflow actually applied to the next tier. Clamped it to match what the bar/number already showed — now reads "+500" for the same scenario.

Also styled `#goAchBox`'s scrollbar (shown when the post-run PROGRESS list overflows its box) to match the custom thin scrollbar already used on Garage/Daily Gift/Stats (`.garage-scroll`/`.dg-scroll`/`.stats-scroll`), replacing the browser's default one — direct request, "make it look better, same as in the garage."

## 2.209.0 — 2026-09-13 00:00: Batch 392 — Tiered achievements: cumulative stats reset per tier, peak/collection stats don't

Direct design decision, following up Batch 391: for a stat built from repeated in-run gains piling up (coins earned, score, overtakes, close calls, ram kills, jump-clears, missions completed), each tier's progress now resets to 0 at the tier boundary — e.g. earning 30K coins in one run from scratch reads as 20,000/100,000 toward silver, not 30,000/100,000. For a best-ever peak value (survival time, streak, level, chain-kill record, top speed, multiplier) or a plain collection tally (owned cars, owned colors, distinct cars driven), progress stays the raw absolute number — direct feedback: "if it's collecting something then there's no point in resetting... things that are cumulative should reset."

New `tierReset: true` flag added to `achData()`'s 7 genuinely-cumulative entries (SCORE CHASER, OVERTAKER, TOO CLOSE TO COMFORT, TASK MASTER, ROAD RAGE, HIGH FLYER, BUSINESSMAN). Both `achModel()` (Achievements tab) and `renderResultAchievements()` (post-run screen) now branch on it: reset achievements subtract the already-cleared tier's threshold from the numerator only, dividing by the next tier's own flat goal (never the bracket span) — matching exactly how the number is displayed. Non-reset achievements (STAYING ALIVE, COLLECTOR, DAILY GRIND, CLIMBING THE RANKS, CHAIN REACTION, FULL PALETTE, CAR FANATIC, I AM SPEED, HIGH ROLLER) are untouched, showing the raw value as before.

Verified live: BUSINESSMAN at 28,308 lifetime (bronze cleared at 10,000) now reads "18,308/100,000" at 18% instead of the raw "28,308/100,000"; a tier-crossing run (5,000 → 250,000 in one go) reads "150,000/1,000,000" toward gold. HIGH ROLLER (5.2/6, gold) and COLLECTOR (52/52) confirmed still showing raw absolute values, unaffected. Checked all three live on the actual Achievements tab — bars, percentages, and numbers all agree with each other. Zero console errors.

## 2.208.4 — 2026-09-13 00:00: Batch 391 — Results-screen achievement bar now matches its own number

Direct bug report: "the white bar is around 12K but that is not the size of 12% of the bar length." The progress bar under a tiered achievement on the results screen (e.g. BUSINESSMAN) computed its fill widths relative to the *previous* tier's threshold (e.g. treating the 10,000→100,000 span as 0-100%), while the "X/Y" number next to it showed the raw absolute total (e.g. "28,308/100,000") — so the "already had" segment rendered far smaller than what its own displayed number implied (in the reported case, ~12,672 real coins showed as only ~3% width instead of ~13%).

Both branches in `renderResultAchievements()` (the normal single-bracket case and the "crossed a tier this run" case) now compute `beforePct`/`gainedPct` against the same absolute 0-to-goal scale as the displayed fraction. Verified live: a 28,308/100,000 scenario now renders 13%+16% (≈29%, matching the ≈28.3% label) instead of the old 3%+17% (≈20%); a tier-crossing scenario (250,000/1,000,000) renders 10%+15%=25%, exactly matching its label.

## 2.208.3 — 2026-09-13 00:00: Batch 390 — Serpentine no longer countable by spam-clicking

Direct bug report: "serpentine achv: lane switch counts not when clicking the button but when actually switching to prevent user spamming buttons." The lane-switch counter (`laneSwitchesThisRun`, feeding the Serpentine secret achievement) incremented whenever the player's rounded lane index changed frame-to-frame — during single-press steering (the default mode since Batch 386), rapid spam-clicking could re-target the car mid-transit and wobble its x-position across a lane-boundary rounding threshold without the car ever actually finishing a real lane change, inflating the count for free.

Fixed by only counting a switch in single-press mode once the car has genuinely settled at its new target (reusing the existing arrival check already in the LERP movement code, `Math.abs(targetX - x) < 0.05`). Multi-lane HOLD glides are untouched — every lane boundary crossed during a smooth continuous glide still counts individually, since there's no spam-wobble risk there (it's one continuous motion, not repeated re-targeting).

## 2.208.2 — 2026-09-13 00:00: Batch 389 — Restored a gameplay-side safety net for stripBufs

Direct follow-up: "now it's only grey again" — Batch 388's fix (removing every direct call to `ensureStripBufs()` except the one page-load background timer) traded the menu-freeze bug for a worse one: real gameplay had no guarantee `stripBufs` would ever actually be ready by the time a run started. On a slower device, or just bad luck in the background timer's timing, a run could show grey verge art for its ENTIRE duration with nothing left to fix it — I couldn't reproduce this directly in this sandbox (every test here had the background build finish in time), but the risk was real by inspection regardless.

Restored `ensureStripBufs()` in `rebuildRoadBuffers()` specifically — the "start playing" path only, not `ensureMenuBufs()` (the passive menu preview, which is what actually caused the original freeze-on-menu bug in Batch 388's predecessor). A real run now always gets correct scenery, worst case paying a brief one-time synchronous cost right at launch instead of silently staying broken; the menu preview still never blocks.

Verified live: forced `stripBufs = null` immediately before `launchGame()` — it rebuilt correctly (91 distinct colors sampled during actual gameplay, not grey) — while forcing the same on `drawMenuScene()` still completed in 8ms without forcing a rebuild. Zero console errors.

---

## 2.208.1 — 2026-09-13 00:00: Batch 388 — Real root cause of the grey panorama: 2 other call sites still raced the fix

Direct follow-up: still starting grey then "rolling down" after Batch 387's fix. Found the actual reason — `rebuildRoadBuffers()` and `ensureMenuBufs()` both ALSO called `ensureStripBufs()` directly, racing the new page-load background timer. The menu's live road preview runs its first frame on the very first `requestAnimationFrame` tick, which isn't guaranteed to lose that race — so it could (and did) trigger the same un-cached 1-8s synchronous build itself, just relocated to the menu's first frame instead of the "Start Run" click. The visible symptom was exactly this: the rest of the menu (already painted via HTML/CSS) sat there fine, while the canvas specifically stayed on its raw grey background for however long that first blocking call took, then suddenly caught up once it returned.

Removed both direct calls — asphalt (`makeAsphalt53`) never actually needed `stripBufs` to build, so neither call was load-bearing. Now the ONE background-deferred call (from Batch 387) is the only thing that ever builds it; every other path just relies on `drawRoadScene()`'s existing graceful no-op (skip the verge art for that frame, draw nothing extra) while it's not ready yet — never blocking, never re-triggering the build itself.

Verified live: forced `stripBufs = null` and called `drawMenuScene()` directly — completed in 7ms (was 1-8+ seconds), confirmed it did NOT rebuild `stripBufs` itself. Same test against `launchGame()` — 12ms, same non-blocking result. Zero console errors.

---

## 2.208.0 — 2026-09-13 00:00: Batch 387 — Fixed "panorama is a solid grey color" — road art no longer freezes on first launch

Direct bug report, tracked down by measuring rather than guessing (no visual screenshot tool available in this sandbox): the road-art strip buffers (verge/biome scenery, `ensureStripBufs()`) take a real 1-8+ seconds to build the first time — measured directly, varying by which biomes got randomly picked for that session. The biome pool nearly doubled since this was last benchmarked (an existing code comment still cites an outdated ~430ms/side estimate) with no corresponding re-check of whether a synchronous build was still reasonable at the new scale.

This build used to only run at the exact instant "START RUN" was first clicked each session — a multi-second freeze with zero loading feedback, during which the canvas just showed its own bare CSS fallback color (`#5a5f66`, a grey) since nothing had been drawn onto it yet. That's exactly what "solid grey" describes.

Fixed by deferring the same build to fire automatically shortly after page load (`setTimeout(ensureStripBufs, 0)`) instead of waiting for the first game launch — it's lane-count-independent, so nothing else needs to be ready first. By the time a real player has navigated the menu and clicked Start, it's already done quietly in the background.

Verified live: `stripBufs` fully populated ~300ms after a fresh page load, without ever calling `launchGame()`; a subsequent real `launchGame()` call then completed in 15ms instead of the multi-second stall. Zero console errors.

---

## 2.207.1 — 2026-09-13 00:00: Batch 386 — More smoke from NPC crash wrecks

Direct request: raised both wreck-smoke spawn chances (lighter puffs 3.5%→7%, darker puffs 1.5%→3.5%) for any crushed or wrecked NPC vehicle (covers both player-ram kills and NPC-vs-NPC crashes — same shared code path). No cap on simultaneous particles existed, so the increase applies cleanly.

Verified live: 300 simulated frames on a crushed vehicle produced 40 particles, in line with the new ~10.5%/frame combined rate (expected ~32, actual within normal random variance) — roughly double the old rate's expected ~18. Zero console errors.

---

## 2.207.0 — 2026-09-13 00:00: Batch 385 — Ambulances no longer spawn into occupied lanes

Direct bug report: ambulances still spawned into lanes with visible traffic. Root cause: `canSpawnAt()` only checks clearance right at the spawn point (by design, for normal traffic density), not the whole lane — a car sitting further down the same lane never blocked it. On top of that, the old logic picked ONE random lane per chance-roll and simply dropped the attempt if that lane was busy, wasting the roll instead of retrying.

Reworked: the chance roll now only decides WHETHER an ambulance wants to spawn (`ambulanceWaitingForLane`). Once true, every frame scans all lanes (shuffled order) for one that's both clear at the spawn point AND has zero vehicles anywhere in it, and keeps waiting — doing nothing, not re-rolling — until one turns up. Reset alongside `pendingAmbulances` at the start of every run.

Verified live (with `devInvincible` on, to keep synthetic test vehicles from contaminating results with a real crash): a vehicle sitting deep in a lane (which the old top-only check would have allowed) was correctly skipped in favor of a genuinely empty lane; with every lane occupied, no ambulance spawned and the intent stayed pending; freeing exactly one lane spawned the ambulance there on the very next frame. Zero console errors.

---

## 2.206.1 — 2026-09-13 00:00: Batch 384 — Result-screen coins now respect ABBREVIATE MONEY, hover for exact

Direct request: the result screen's COINS EARNED now uses `coinDisplay()` (the existing global ABBREVIATE MONEY setting) instead of always showing the full number — both the instant path and the count-up animation (which now abbreviates each animated frame via `countUp()`'s existing `fmt` parameter). Hover reveals the exact number and reverts on mouse-leave, same `.onmouseenter`/`.onmouseleave` pattern already used in the Garage and Daily Gift headers.

Verified live: default shows `"1.23M"` for 1,234,567 coins, hover shows `"1,234,567"`, mouse-leave reverts to `"1.23M"`; with ABBREVIATE MONEY off, it shows the full number outright. Zero console errors.

---

## 2.206.0 — 2026-09-13 00:00: Batch 383 — Score rounds exactly once, at the true end of the run

Direct correction: every scoring event used to round immediately (`Math.round(pts * multiplier)`), not deferred to game-end as intended. Removed rounding from all 5 places `score` gets incremented (normal pass/jump-over, Tank shot, Tank ram-touch, Shield Bump ram, close call) — each now adds its raw fractional value (points × multiplier) straight to `score`, which accumulates as a float throughout the run. Added exactly ONE rounding step, at the very top of `endRun()`, before anything downstream (`saveScore()`, `CS.snapshot`, `allTimeStats`, leaderboard) ever reads it.

Two spots needed care to avoid a regression:
- The pause menu used to show `score` directly — now shows `Math.round(score)` for display only, without touching the real (still-fractional, mid-run) value underneath.
- The close-call bonus feeds two things: the main `score` (now raw/unrounded) and a separate `closeCallPointsThisRun` breakdown stat (kept rounded per-event, since that's just a cosmetic display number, not the real score).
- The HUD's live score display (`displayedScore`) already eased toward `score` via `Math.ceil()` increments — since ceil-of-a-fraction is always a whole number, it was already robust to a fractional target with no change needed.

Verified live: forced a 1.73x multiplier and credited 2 passes — mid-run `score` read `34.6` (confirmed fractional, i.e. not rounded per-event); opening the pause menu showed `"35"` while the underlying `score` stayed `34.6` (unmutated); calling `endRun()` then rounded it to exactly `35`, once. Zero console errors.

---

## 2.205.1 — 2026-09-13 00:00: Batch 382 — Shield Bump ram-kill score lowered to 1.2x

Direct request: the non-Tank ram-kill score bonus (Shield Bump) was 2x the normal per-vehicle rate, same as jump-over. Lowered to 1.2x — ramming no longer scores as well as a clean jump-over. Tank's own flat 30-point ram-touch score is a separate, unrelated formula and untouched.

Verified live: confirmed the line now reads `score += Math.round(ramPts * multiplier * 1.2)`. Zero console errors.

---

## 2.205.0 — 2026-09-12 00:00: Batch 381 — Steering settings reworded, mouse/touch row hidden for keyboard players; debug readout removed

Confirmed working (Batch 378's debounce fix). Two follow-ups:

### Wording cleanup
Direct feedback: "drag and hold, hold etc it is confusing." Two settings both used the word "hold" for unrelated things — "HOLD FOR MULTIPLE LANES" (keyboard) and "Hold & Drag" (a mouse/touch steering-button mode). Renamed the keyboard one to **"MULTI-LANE KEY PRESS"** (drops "hold" from the title entirely, explained in the hint instead: "Off: each press moves 1 lane. On: keep the key down to glide across several.") and the mouse/touch row from "STEERING BUTTON INPUT" to **"MOUSE/TOUCH STEERING"**, making the scope explicit in the name instead of just the hint. Also reordered: the keyboard setting now sits right after CONTROL TYPE (the input method most players actually use), with the mouse/touch-only row after it instead of before.
- **Mouse/touch row now hidden entirely unless Control Type = Steering Buttons** — previously always visible regardless of which control scheme was selected, cluttering the screen with an irrelevant option for keyboard players (the only real input method right now, per direct confirmation). Live-updates immediately when Control Type is changed, no page reload needed.

### Temporary debug readout removed
The `HELD`/`MLH`/`BTN`/`LANE` diagnostic added to the FPS counter (Batches 379-380) served its purpose — removed now that the underlying bug is confirmed fixed, along with its now-unused `lastFpsStr` variable.

Verified live: mouse/touch row's computed `display` confirmed `none` by default, `flex` after switching Control Type to Steering Buttons, back to `none` after switching back — no page reload involved. Row titles confirmed as the new wording with no shared "hold" terminology. The multi-lane toggle itself still functions identically after the rename/reorder. Zero console errors.

---

## 2.204.3 — 2026-09-12 00:00: Batch 380 — Multi-lane hold debug readout: added config-state visibility

Direct follow-up: user reports `HELD` never shows LEFT/RIGHT in either setting state. Extended the temporary debug readout (Batch 379) to also show `MLH:<true/false>` (the live `config.multiLaneHold` value) and `BTN:<true/false>` (`config.steeringButtonEnabled` — the whole keyboard lane-change block is gated on this being false) alongside the existing HELD/LANE fields, so we can tell whether the setting itself isn't reaching `config` at all, versus the keydown handler not firing/matching for some other reason. Still can't reproduce this locally — every simulated test with `config.multiLaneHold` genuinely true correctly shows `HELD:RIGHT` while holding. Purely diagnostic, no behavior change.

---

## 2.204.2 — 2026-09-12 00:00: Batch 379 — Multi-lane hold: TEMPORARY debug readout, root cause still not confirmed

Direct follow-up: the Batch 378 debounce fix did NOT resolve it — meaning that theory (browser reporting a hold as keyup+keydown pairs) was wrong, or at least incomplete. Rather than guess a 3rd time blind, added a temporary live diagnostic instead of another speculative fix: turning on the existing FPS COUNTER setting now also shows `HELD:LEFT/RIGHT/NONE` and the current `LANE` number, updated every real frame (not smoothed/averaged), piggybacking on the FPS counter's own toggle rather than adding a new setting. This makes the actual internal state visible in real time during a real hold on the user's own device, instead of relying on further simulated tests that keep failing to reproduce the reported symptom.

Verified the readout itself is accurate (not just present): simulated hold correctly showed `HELD:RIGHT` continuously stable while `LANE` climbed 1→3, confirming the debug text reflects real internal state rather than lying/lagging. This is intentionally a debugging aid, not a fix — remove once the real cause is found from what the user reports.

---

## 2.204.1 — 2026-09-12 00:00: Batch 378 — Real root cause found: multi-lane hold debounced against a flaky release

Direct follow-up: the previous 3 rounds of testing (Batch 275, and this session's own keyboard-hold simulations) never reproduced the bug because they only ever simulated a single sustained `keydown` (optionally with repeated `repeat:true` events) — never a `keydown` with a `keyup` genuinely interspersed mid-hold. A direct diagnostic question narrowed it down: the user described the car visibly gliding, then stopping after exactly 1 lane, still while the key was held down. That's the signature of a real `keyup` firing mid-hold — some browser/OS/input-software combinations report a genuine physical key-hold as rapid keyup+keydown pairs per repeat tick instead of one sustained keydown, which immediately triggered this game's own release logic (`hHeldDir = false` + snap to the nearest lane) every single tick, capping any hold at roughly 1 lane's worth of glide before being cut short and restarted.

Fixed with a release grace period: `keyup` no longer clears the hold state immediately — it schedules the release (and the snap-to-nearest-lane) 80ms later, and a `keydown` for the same direction arriving before that timer fires cancels it, reading as a continued hold rather than a fresh press. A genuine release (no re-press within 80ms) still behaves exactly as before.

Verified live: simulated 3 rounds of a spurious keyup immediately followed by a re-press (30ms apart, well inside the 80ms grace window) — the glide continued uninterrupted across lanes each time instead of snapping back. A genuine release (150ms, no re-press) still correctly cleared the hold state and snapped. Regression-checked both existing modes: a clean uninterrupted hold still crosses multiple lanes (0→3), and single-lane-per-press mode (the new default) is unaffected (0→1). Zero console errors.

---

## 2.204.0 — 2026-09-12 00:00: Batch 377 — Multi-lane hold: default flipped to off, opt-in only

Long-open PLAN.md item ("move and drag option doesn't work, car can't change multiple lanes when holding the key") — investigated again this round, this time also directly simulating a keyboard hold (single sustained `keydown`, then a realistic OS-style auto-repeat sequence) against the default Arrows/WASD scheme, on top of the mouse/touch paths already tested back in Batch 275. Still no code defect found in any of the 4 input paths — `config.multiLaneHold` correctly glides across multiple lanes whenever it's true.

Direct follow-up clarified the actual ask: keep hold-for-multiple-lanes available as a choice, but it shouldn't be the DEFAULT — it's faster but genuinely harder to control precisely, so a new player should start on one-lane-per-press and opt into the faster/harder mode deliberately. `config.multiLaneHold` default `true` → `false`; the Settings toggle and its underlying `<select>` default flipped to match.

Verified live through the real toggle-click path (not a bypassed config override): fresh default holds ArrowRight for 60 frames and moves exactly 1 lane (0→1); clicking the real "HOLD FOR MULTIPLE LANES" toggle ON and relaunching restores the multi-lane glide (0→3 lanes in the same 60-frame hold). Zero console errors.

---

## 2.203.3 — 2026-09-11 00:00: Batch 376 — More space between achievement sections

Direct feedback: TIERED/ONE-TIME/SECRET sections read as too cramped against each other. `.ach-group` margin-bottom 16px → 36px, with the last section's margin zeroed out so there's no wasted trailing space at the bottom of the screen.

Verified live: computed margins across the 3 real sections came out 36px/36px/0px. Zero console errors.

---

## 2.203.2 — 2026-09-11 00:00: Batch 375 — Full Palette bronze tier lowered to 3

Direct correction: Full Palette's bronze tier was 4 colors, should be 3.

---

## 2.203.1 — 2026-09-11 00:00: Batch 374 — "Use energy bars" mission: ram now counts, net of its own refund

Direct correction to Batch 373: ramming should count toward the mission, just not the energy it refunds back. Reworked from a flat exclusion to a net accounting: ram activation still adds +1 (same as jump/Tank), but a ram-kill's energy refund now subtracts that same fractional amount (1/3 normal car, 2/3 truck-like) from the running counter. A single ram nets a small positive contribution; a heavy multi-kill ram chain can net the whole activation to zero or below (clamped at 0 when folded into the daily total at run-end) — so chain-ramming still can't cheaply farm the mission, without excluding ram as an ability outright.

Verified live: a single ram activation with no kill nets `+1`; adding one kill's refund (1/3 cell) brings it to `0.667`; simulating a 5-kill chain drives it to `-0.667`, confirmed clamped to `0` before crediting. Zero console errors.

---

## 2.203.0 — 2026-09-11 00:00: Batch 373 — 4 achievements converted to tiered + new "use energy bars" mission

### Achievement conversions
4 former ONE-TIME achievements converted to TIERED, fewer tiers than the main roster (tier count/spacing left to my own judgment per direct request) — each keeps its OLD one-time tier as the new ceiling, scaled down from there:
- **FULL PALETTE** (own paint colors) — 3 tiers, bronze 4 / silver 7 / gold 11 (was gold-only, all 11).
- **CAR FANATIC** (distinct cars driven) — 3 tiers, bronze 15 / silver 35 / gold 52 (was gold-only, all 52). `v` derived from the existing `allTimeStats.carStats` map (count of cars with ≥1 run), no new counter needed.
- **I AM SPEED** (top speed reached) — 3 tiers, bronze 150 / silver 200 / gold 250 km/h (was gold-only, 250). New persisted stat `allTimeStats.bestTopSpeedKmh` — no lifetime best existed before, just a live `>=250` check each run.
- **HIGH ROLLER** (best multiplier) — 4 tiers (was diamond, so kept 4), bronze 3 / silver 4.5 / gold 6 / diamond 7.5. First tiered achievement with genuinely fractional thresholds — this surfaced a latent bug: `achFullNum()` used `Math.round()`, which would have silently turned "4.5" into "5" and "7.5" into "8". Fixed: whole numbers still take the plain integer path, anything fractional keeps up to 2 real decimals (reuses `achStripTrailingZeros()`).

The 4 old `unlockAchievement(...)` trigger calls in `recordRunStats()` are removed — a tiered achievement's progress is derived live from its own `v` every render, no explicit unlock check needed.

### New Daily Mission: "USE X ENERGY BARS"
Direct request, base 100 + 2/level rounded to nearest 5 (exact same formula shape as `pass_cars`). New `barsUsedThisRun`/`allTimeStats.totalBarsUsed` counter, incremented on JUMP activation and Tank-shot activation — **Shield Bump ram deliberately excluded**, since ram already refunds energy per kill and counting it would make the mission trivially farmable. No matching achievement was added — explicitly declined by direct call ("not very important... not necessarily a good idea"); agreed, the stat is there if that changes later.

Verified live: all 4 converted achievements render as real tiered cards (bar, ladder, tier badge) with zero duplicate/missing ids; HIGH ROLLER specifically confirmed showing "5.23/6" (not "5/6") for a fractional in-progress value and "/7.5" (not "/8") for its ceiling; a direct `useAbility()` test confirmed jump increments `barsUsedThisRun` (0→1) while a subsequent ram activation does not (stays at 1); the mission's `resolve()` confirmed 100 at level 1 and 140 at level 20 (100 + 19×2 = 138 → rounds to 140). Zero console errors.

---

## 2.202.2 — 2026-09-11 00:00: Batch 372 — Thin-space grouping reverted, no separator at all

Direct follow-up: the thin-space thousands grouping from Batch 371 "looked bad" too. Removed entirely — `achFullNum()` (replacing `achGroupThin()`) now returns the plain digit string with no separator of any kind (no commas, no spaces, no periods). Scope unchanged: only `achFmt()`'s full-number fallback and the percentage display use it.

Verified live: `achFmt(1234567)` with abbreviate off now returns exactly `"1234567"` with zero non-digit characters; abbreviation (`"1M"`, whole-number stripping) still works correctly. Zero console errors.

---

## 2.202.1 — 2026-09-11 00:00: Batch 371 — Achievements number formatting: 2 direct refinements

- **Whole numbers no longer grow a fake decimal** — with the digit setting >0, exactly 1,000,000 now reads "1M" (not "1.0M"), and a 0% progress reads "0%" (not "0.0%"/"0.00%") — new `achStripTrailingZeros()` helper, decimals only show when they're real (reuses the same trailing-zero-strip technique `sigFmt3()`/`coinAbbr()` already established for the separate money formatter).
- **Full (non-abbreviated) numbers use a thin space instead of commas** — "1,234,567" → "1 234 567" using U+2009 (a proper typographic thin space, narrower than a real space bar, not a plain ASCII space) between thousands groups. New `achGroupThin()`.

Both scoped to `achFmt()`/the new percentage display only — `resultFmt()` (result screen) and `coinDisplay()` (coin balances elsewhere) untouched, matching how these formatters have stayed intentionally separate all along.

Verified live: `achFmt(1000000)` → "1M" at both 1 and 2 decimal-digit settings (was "1.0M"/"1.00M"); `achFmt(1234567)` with abbreviate off → "1 234 567", confirmed via character codes that the separator is U+2009 (8201), not a comma or plain space; a 0% and 100% progress both render without trailing zeros. Zero console errors.

---

## 2.202.0 — 2026-09-11 00:00: Batch 370 — Achievements number-display settings (gear icon + popover)

New settings popover on the Achievements tabs row, right side — a pixel-art gear icon (`achGearSvg()`, not a text button, per direct request), opening a small panel with 3 controls, all persisted to localStorage independently of the existing global ABBREVIATE MONEY setting (most achievement numbers aren't coins — score, close calls, jumps, etc.):

- **ABBREVIATE NUMBERS** (default ON) — off shows the full exact number everywhere on the screen (e.g. "1,234,567" instead of "1.2M").
- **DECIMAL DIGITS** (0/1/2, default 1) — controls precision on both the abbreviated K/M numbers AND the new percentage display below.
- **SHOW % ABOVE BARS** (default OFF) — an optional percentage readout above each tiered achievement's progress bar (right-aligned), using the RAW unrounded progress fraction (not the bar's own floored-at-3%-for-visibility value) so the digit setting has real precision to show.

Implementation: `achFmt()` now reads the abbreviate/digit settings instead of always abbreviating with a fixed format; `achModel()` gained a new `pctExact` field (unclamped/unrounded percentage) alongside the existing `pct` (which stays clamped — the bar width still needs a visible minimum sliver near 0%). Popover follows the same click-outside-closes pattern already used for the Stats chart dropdown, wired once at page load rather than inside the re-rendering function.

Verified live: gear icon renders a real 10-rect pixel SVG; panel opens/closes on click and on outside click; abbreviate-off shows "1,234,567" (was "1.2M"); switching to 2 digits shows "1.23M"; percentage row shows "15.00%" for a real 23.5%-into-tier test case (135/900, hand-verified) and "100.00%" for a maxed achievement; the digits row visibly disables (`opacity:.4;pointer-events:none`) while abbreviate is off; all 3 settings round-trip through localStorage. Zero console errors.

---

## 2.201.0 — 2026-09-11 00:00: Batch 369 — Tiered achievements sort by top-tier rank + Businessman rework

- **Confirmed, no change needed**: the description-length sort from Batch 368 only ever touched `secretsRaw` — tiered/one-time sections were untouched.
- **Tiered achievements now sort by their OWN top tier first** — a fixed property of each achievement's definition (5-tier ones capping at amethyst vs 4-tier ones capping at diamond), not the player's live progress. Amethyst-capped achievements (Score Chaser, Overtaker, Collector, Climbing The Ranks, Daily Grind, Businessman) lead the TIERED group; diamond-capped ones (Staying Alive, Too Close To Comfort, Road Rage, High Flyer, Task Master, Chain Reaction) follow. `achComplete`/`TIERED_IMPORTANCE` still break ties within each top-tier group, same as before.
- **Businessman reworked**: added a 5th amethyst tier (bringing it in line with the rest of the 5-tier roster) and raised every threshold — bronze 10K (unchanged), silver 100K (unchanged), gold 400K→1M, diamond 1M→10M, new amethyst 100M. Priced against the real economy first: all 52 cars together cost 62,735,500 coins, so the new 100M ceiling sits comfortably above "could buy literally every car" rather than being an arbitrary round number.

Verified live: Businessman's `tiers` array confirmed as the exact 5 new values; rendered the real Achievements screen and confirmed all 6 amethyst-capped achievements (Businessman correctly among them now) sort before all 6 diamond-capped ones. Zero console errors.

---

## 2.200.0 — 2026-09-11 00:00: Batch 368 — Achievement description trims + secret cards sort by height

- **Score Chaser**: "Bank enough total score, across every run you've played." → "Bank enough total score." (redundant clause dropped).
- **Businessman**: "Earn this many coins, over your lifetime." → "Earn this many coins." (same).
- **Secret achievement cards now sort by description line count** within the completed group, shortest first. Direct design discussion: revealed secrets have real (sometimes long) descriptions that wrap to anywhere from 1 to 5 lines, and CSS Grid sizes each row to its tallest cell — a long card scattered next to short ones left visible dead space under the short ones, reading as jagged. Grouping by height means most rows stay uniform, with only the tail (where the longest cards cluster) potentially uneven — much less visible than before.
  - Implementation note: the first attempt at computing the available text width by hand (card width − padding − icon − gap) was wrong by nearly 2× (guessed 206px, real is 115.875px) — missed that the once-achievement tier tag badge in `.ach-card-top` also eats into the remaining space. Switched to measuring off an actual already-rendered secret card's `.ach-card-desc` width directly instead of computed padding math.

Verified live: unlocked all 18 secrets and rendered the real Achievements screen — resulting card order's real rendered heights come out strictly ascending (33→33→...→50→50→...→66→66→66→83px), confirmed via `getBoundingClientRect()`, not just the predicted line counts. Zero console errors.

---

## 2.199.1 — 2026-09-11 00:00: Batch 367 — Level badge number no longer text-selectable

Direct request — the rapid-click spin from Batch 366 made accidental text selection (blue highlight) on the level number an easy side effect. Added `user-select: none` to `.level-badge-ring-wrap` (covers the number, ring canvas, and everything else in all 3 instances — Menu/Garage/Stats — since the click handler already targets the whole wrap, not just the number).

Verified live: computed `user-select` is `none` on both the wrap and the number itself. Zero console errors.

---

## 2.199.0 — 2026-09-11 00:00: Batch 366 — Mirror, Mirror spin rewritten: fixes tab-switch replay bug + accelerates on rapid clicks

Direct bug report + feature request, both solved by the same rewrite. The level-badge spin used to be a fixed 0.6s CSS `@keyframes` animation toggled via a class; two problems: (1) switching tabs mid-spin and coming back made it look like the spin "restarted," even without a new click — a fixed-duration CSS animation's timeline doesn't interact well with a backgrounded tab; (2) clicking rapidly just restarted the same fixed animation from scratch instead of building up speed, which "looked weird."

Rewritten as a JS-driven rotation (`mirrorSpinKick()`) instead of a CSS keyframe: each click adds 360° to a "still owed" rotation pool; current angular speed is proportional to that pool (closed-form exponential decay, not per-frame Euler integration — mathematically stable for ANY elapsed time between frames, including a long tab-away gap). Two direct effects fall out of this one model for free:
- **Rapid re-clicks accelerate the spin** — each click adds another 360° to the pool, and since speed is proportional to the pool, more clicks = visibly faster spin, not a restart.
- **A bigger stacked pool naturally decelerates more slowly** — takes proportionally longer (real time) to decay back to 0, exactly as requested.
- **Tab-switch bug fixed by construction** — because the decay is computed via the closed-form formula (`remaining *= Math.exp(-RATE * dt)`) using the ACTUAL elapsed wall-clock time on whatever frame runs next, a long backgrounded gap just correctly resolves to "already finished" (a spin was always under a second long) rather than replaying or glitching.
- Since angle always advances by exactly however much the pool shrinks, it lands on an exact multiple of 360° (upright) by construction — no separate "snap to true north" correction needed.

Removed the now-dead `@keyframes mirrorMirrorSpin`/`.mirror-spin` CSS (only consumer was the code just replaced).

Verified: 3 rapid clicks stacked the pool to 1,080° (3×360, confirms acceleration) instead of restarting; the closed-form decay formula confirmed collapsing a 1,080°-pool to functionally 0 (6.8e-13) after a simulated 5-second tab-away gap — meaning the very next real frame after returning just cleanly finishes the spin, matching a single normal frame (1/60s) barely denting the pool (1,080 → 961) during continuous play. Zero console errors.

---

## 2.198.0 — 2026-09-11 00:00: Batch 365 — Garage booster mini-icons ported + "Mirror, Mirror" achievement stale-forever bug

### Garage booster mini-icons
Ported `drawFlameSwatchIcon()` exactly from the newly-uploaded "Booster Icons 3x1.dc.html" — bigger flat fire-ramp bands with detail dropped (vs. the full thruster canvas art), tuned specifically to read clearly at the small 20×20 swatch size. Replaces the old hand-drawn placeholder shapes for all 3 kinds (Center Thruster/Underglow/Rocket Pods). Verified live: sampled pixels at the thruster icon's core and tip match the doc's `#fff8d0`/`#b3231a` exactly; picker renders all 3 swatches with zero console errors.

### "Mirror, Mirror" (and every other secret achievement): fixed a real stale-forever bug
Direct bug report: clicking the level badge fired the "ACHIEVEMENT UNLOCKED" popup, but the Achievements screen's SECRET section still showed it as not done. Root cause: `ACH_SECRETS` was a plain `const` array — evaluated exactly ONCE at page load — so every entry's `done: !!allTimeStats.achievementsUnlocked.xyz` field was frozen forever at whatever it read at that single instant, unlike `achData()` (the TIERED/ONE-TIME roster), which is a function re-called fresh on every render. Any secret unlocked mid-session would show the popup correctly (that reads live state directly) but never actually flip to done anywhere else until a full page reload happened to re-evaluate the array. Converted `ACH_SECRETS` into a function (`ACH_SECRETS()`, matching `achData()`'s own pattern) and updated all 5 call sites.

Verified live: unlocked `mirror_mirror` mid-session (no reload) — `ACH_SECRETS().find(...).done` flipped from `false` to `true` immediately, and a real render of the Achievements screen showed the card with its `✓` tick and complete border color. This bug affected all 19 secret achievements, not just Mirror, Mirror — any of them completed without a page reload in between would have shown the same stale "not done" state. Zero console errors.

---

## 2.197.1 — 2026-09-11 00:00: Batch 364 — Completed-achievement description alignment, real root cause

Direct bug report: the description text under a completed achievement's name still read as centered, not left-aligned under its own title. Root cause: `#gameOverHud` sets `text-align: center` for the whole result screen — `.go-ach-name` explicitly overrides it to `left`, but `.go-ach-desc` never did, so it silently inherited the centered alignment while the name above it stayed left. Added the same `text-align: left` override to `.go-ach-desc`.

Verified live: name and description now compute to the exact same `left` (both -95.5) and `.go-ach-desc`'s computed `text-align` is `left`. Zero console errors.

---

## 2.197.0 — 2026-09-11 00:00: Batch 363 — Completed-achievement cleanup, scrollable achievements box, result-screen stat colors

### Result-screen COMPLETED section
- **"COMPLETE" → "COMPLETED"**.
- **Dropped the goal/goal fraction entirely** ("100/100" next to OVERTAKER) — just the tier badge now. Removing the second line also fixes vertical centering for free (a single child in `.go-ach-status` centers correctly against the row via the existing `align-items:center`, no longer sharing a 2-line column) — confirmed live, tier-label center and row center now compute to the exact same y.
- Cleaned up the now-fully-unused `statusVal` computation (both push sites) and the `.go-ach-statusval` CSS rule it was the only consumer of.

### Achievements box: scrollable, rest of the result screen fixed
Direct bug report: a long-session/new-account run with a huge number of unlocked achievements pushed the title and buttons off-screen entirely — `#gameOverHud` had no overflow handling of its own. Fixed in 3 parts:
- `#goAchBox` capped at `max-height: 34vh` with `overflow-y: auto` — scrolls internally once it has enough rows, unaffected (same natural size as before) under that cap.
- Every OTHER child of `#gameOverHud` (title, score, stat-box, buttons) gets `flex-shrink: 0` — they no longer get crushed by flexbox's default shrink behavior when space is tight; the achievements box alone absorbs any squeeze, down to a `min-height: 90px` floor so it never disappears entirely.
- `#gameOverHud` itself also gets `overflow-y: auto` as a safety net for the genuinely extreme case (achievements box already at its floor and content still doesn't fit) — title/buttons stay reachable by scrolling the page instead of clipping.

Verified live with a synthetic 40-row achievement list: the achievements box respected its max-height cap, hit and held its 90px floor instead of collapsing toward 0px (an intermediate bug caught and fixed during this same pass — flexbox's default shrink was crushing it before the `flex-shrink:0` siblings + floor were added), and stayed independently scrollable (`scrollHeight` 2180px inside a 90px box). Absolute pixel measurements in this sandbox's headless browser pane were unreliable for the *outer* container specifically (`#gameOverHud.clientHeight` measured 44px even with real canvas dimensions passed through `sizeFrame()` — a test-harness artifact, not a CSS issue, since the mechanism itself — max-height/min-height/overflow — is standard and verified working on the achievements box directly); the fix should be spot-checked in an actual played session.

### Result-screen stat-row colors
Direct request, restrained (one request explicitly said "don't overdo it"): **CLOSE CALLS is now red** (`.stat-red`, reused from the existing pattern), **VEHICLES JUMPED OVER (ability-usage row) is now blue** (new `.stat-blue` / `--c-blue: #4d9fff` token) — swapped from its previous `.stat-red` (Batch 219), which the direct request was explicitly changing away from.

---

## 2.196.1 — 2026-09-11 00:00: Batch 362 — Result-screen PROGRESS rows actually sorted by percentage now

Direct correction: the percentage-sort recommendation from Batch 360 was never actually implemented — the `progress` array was still just rendered in its fixed `defs` insertion order (score → pass → close calls → ram → jumps → coins), regardless of how close each one was to its next tier. Added a real `totalPct` (exact, unrounded current-value-within-tier-range) to every progress entry and sorted the array descending by it right before rendering, closest-to-completion first.

Verified live with 3 real achievements at deliberately different percentages (Overtaker 95%, Too Close To Comfort 40%, Score Chaser 30%): rendered order came out exactly 95% → 40% → 30%. Zero console errors.

---

## 2.196.0 — 2026-09-11 00:00: Batch 361 — NPC lane-change commit fix + Prism effect actually matches the design doc

### NPC traffic: signaling car no longer aborts and re-signals later
Direct bug report ("cars try to change lanes and then change their mind, don't move, then later actually do it"). Root cause: `changingState === 'indicator'` re-checked lane clearance when the signal timer ran out (`laneClearForMerge`/`laneReservedForAmbulance`) — if the target lane was no longer clear, it silently canceled back to `'none'` and retried a fresh decision 30 frames later, which read as exactly the flip-flop reported. A car that's signaling now commits unconditionally once the indicator timer ends — the existing NPC-vs-NPC same-lane crash mechanic (Batch 265-267) already handles two vehicles ending up too close, so this doesn't introduce a new failure mode, just removes the cancel-and-retry. Verified live: forced a lane-changer into `'indicator'` with 1 frame left and a blocking vehicle sitting at the exact same y in its target lane — `update()` committed straight to `'moving'` instead of aborting.

### Result-screen Prism effect: found and ported the real design doc
Previous 2 attempts (Batch 358/359) both guessed at what "Prism effect" meant and got it wrong — turns out there's a real source file, `Achievements Tab.dc.html` (not part of `carCrash.html`, hadn't been checked), with the exact intended design:
- **The scroll, not a hue-rotate filter**: `.go-ach-bar-delta` now uses the doc's exact 9-stop `hsl()` gradient scrolling via `background-position` (`@keyframes prismScroll`, 120px tile, 1.6s linear infinite) — completely different technique from the hue-rotate filter guessed at previously.
- **Delta number font switched to VT323** (was Silkscreen) at 24px, matching `r.countStyle` in the doc exactly — this is also what was behind "the numbers look out of place": Silkscreen (blocky/bold) never matched the surrounding VT323 numeric readouts.
- **New bordered, centered column** (`.go-ach-delta-col`, 64px, `border-left`, flex-centered both axes) replacing the old right/left-aligned trailing text — ported from the doc's own row layout (a dedicated divided box, not an inline span).

Verified live: computed styles confirm `border-left: 2px`, `justify-content: center`, `align-items: center` on the column; delta font-family `VT323, monospace` at 24px; bar-delta's computed `animation-name` is `prismScroll` with `background-size: 120px 100%`; a 4-digit case ("+1,800") measured with zero overflow at full size (VT323 is narrow enough that the shrink fallback never triggers in practice). Zero console errors.

---

## 2.195.0 — 2026-09-11 00:00: Batch 360 — Result-screen achievements: 4 more direct corrections

- **"PROGRESS" label is now amber/yellow** (`var(--c-amber)`), was the dim grey text color.
- **Prism effect is now actually animated**, not a static gradient — reuses the exact `legendaryHueShift` hue-rotate keyframe the level-100 legendary badge already cycles with (20s linear infinite, `prefers-reduced-motion` respected), applied on top of the same rainbow gradient.
- **"+" sign shrunk to 65% size** (`.go-ach-delta-plus`, wrapped in its own span) relative to the number after it — was the same size as the digits and looked oversized.
- **A tier completed this run now shows goal/goal** ("1,000/1,000"), not the raw overflowed stat ("1,088/1,000") — and if that run's gain carried past the tier's own threshold, the SAME achievement now also gets a PROGRESS row for the next tier (e.g. Score Chaser Bronze completes at 1,000, then Score Chaser Silver appears below showing the real cumulative value against Silver's own threshold), instead of the overflow just vanishing from view.

Verified live with a real before/after scenario (totalScore 912→1,088, crossing the 1,000 bronze threshold): COMPLETE row read "1,000/1,000"; a new PROGRESS row for Silver appeared reading "1,088/10,000 +176"; PROGRESS label computed color confirmed amber (`rgb(245, 179, 42)`); bar-delta's computed `animation-name` confirmed `legendaryHueShift`; plus-sign computed font-size confirmed 10.4px vs the number's 16px (65% ratio). Zero console errors.

---

## 2.194.1 — 2026-09-11 00:00: Batch 359 — Result-screen achievements: 2 direct corrections

Follow-up to Batch 358, 2 direct corrections:

- **"+N" delta numbers now left-aligned**, not right — every row's number now starts at the same x (confirmed identical `left` across 3 differently-sized numbers), instead of trailing off the fixed-width column at a different point per digit count.
- **The "Prism effect" moved to the right part of the bar**: it belongs on the gained-this-run segment (the green portion), not the base fill — Batch 358 had put an animated shimmer sweep on the wrong segment. Replaced entirely with the same static rainbow gradient `.prism-swatch` (the Garage's own Prism paint swatch) already uses (`linear-gradient(135deg, #ff3b30, #ff9500, #ffe600, #34c759, #00c7e6, #3d6cff, #af52de, #ff3b30)`), applied to `.go-ach-bar-delta` instead of inventing a new animation.

Verified live: 3 delta numbers of different digit counts ("+42"/"+2"/"+1,800") confirmed identical `getBoundingClientRect().left`; `.go-ach-bar-delta`'s computed `background-image` confirmed as the exact same 8-stop rainbow gradient. Zero console errors.

---

## 2.194.0 — 2026-09-11 00:00: Batch 358 — Result-screen achievements box: layout cleanup + number formatting

Direct screenshot-driven feedback, 3 real fixes:

- **"UNLOCKED ⋯ N" header removed**, replaced with a plain green `COMPLETE` label in the same spot — no dashed rule, no count.
- **Removed the vertical accent-color line** (`border-left`) on unlocked achievement rows, and the per-card redundant `COMPLETE` status text (now that the whole section is already labeled COMPLETE) — a tiered achievement that leveled up this run still shows its real fraction there, only the literal placeholder word was dropped. Removing the border/padding also fixed a side effect: it was shifting unlocked-row content out of alignment with the PROGRESS rows below, which never had that padding.
- **Progress numbers now always full comma-separated** (`resultFmt()`, new — `achFmt()` itself untouched, still used by the Achievements screen) instead of `achFmt()`'s K/M abbreviation, which read inconsistently (e.g. "8,400/25K" — one side abbreviated, one not) and didn't match the reference design doc. A fraction/delta that's too wide to fit at normal size now shrinks its own font (`.go-ach-frac-tight`/`.go-ach-delta-tight`) instead of abbreviating.
- **Progress bar width now identical on every row** — the "+42"/"+1,800"-style delta number used to be `flex-shrink:0` with no reserved width, so a wider number silently stole space from the bar-track next to it. Now a fixed 64px column (shrinking its own font past 6 characters so nothing clips).
- **Restored the shimmer effect on the bar fill** (animated diagonal light sweep, `@keyframes achBarShimmer`, respects `prefers-reduced-motion`) — was never actually wired up on this box.

Also added a PLAN.md entry (not implemented) for a future "use X energy bars" Daily Mission + matching tiered achievement, per a separate idea raised in the same message.

Verified live: green `COMPLETE` label confirmed (no rule/count elements), row `border-left`/`padding-left` computed as 0px, per-card `COMPLETE` status text count is 0; a 4-row test batch showed identical bar-track width (177.375px) across "+42"/"+2"/"+214"/"+1,800" deltas (previously 183.375 vs 173.375 — visibly different); numbers confirmed full comma-separated ("8,400/25,000", not "8,400/25K"); the "+1,800" case confirmed shrinking to 12px with zero scroll/client-width overflow; shimmer's computed `::after` animation-name confirmed `achBarShimmer`. Zero console errors.

---

## 2.193.2 — 2026-09-11 00:00: Batch 357 — Road obstacle warning lengthened

Direct feedback: the breakdown-obstacle warning sign felt too quick. It was already speed-scaled, not fixed (same convention as the ambulance warning), but confirmed with the user it should still be longer on both ends.

- **Obstacle pre-warning window increased**: base 2.5s→3s, high-speed floor 1s→1.5s (`Math.max(90, Math.round(180 * baseSpeed / currentSpeed))`, was `Math.max(60, Math.round(150 * ...))`). Ambulance warning intentionally left untouched — this request was specifically about the road obstacle.

Zero console errors.

---

## 2.193.1 — 2026-09-11 00:00: Batch 356 — Daily Missions coin reward now abbreviates (K/M)

Direct follow-up: the Garage/Daily Gift/Stats coin totals already abbreviate large numbers (`coinDisplay()`, e.g. "1.5M"), but Daily Missions' coin-mission reward chip still showed the raw number ("+50000") while its icon sat unchanged. Now uses the same `coinDisplay()` helper, so it reads "+50K"/"+100K"/"+200K" (respects the existing ABBREVIATE MONEY setting) — only the number changed, icon and layout untouched. XP-mission chips are unaffected (their tiers are small enough not to need it).

Verified live: rendered the real Missions view, all 3 coin-mission chips read "+50K" for the day's rolled tier-1 reward; `coinDisplay()` on the ladder values themselves confirmed [50000,100000,200000] → ["50K","100K","200K"]. Zero console errors.

---

## 2.193.0 — 2026-09-11 00:00: Batch 355 — Booster preview: real fixes for wasted space + frozen animation

Direct follow-up to Batch 354 after screenshots showed it wasn't actually fixed: Underglow and Rocket Pods previews still had visibly more empty space than Thruster despite sharing the same `padUnits`. Also fixed a separate reported bug: the preview animation sometimes freezes until you hover away and back.

- **Preview box sizing rewritten to measure real content instead of guessing padding.** The old fixed `padUnits` constants (4 for Thruster/Underglow, 15 for Pods) assumed all non-Pods flames need the same clearance — wrong, since each kind's actual plume length/width differs. Now draws into a scratch buffer and uses `getImageData` to find the real non-transparent bounding box, then crops tightly to it. To avoid the box visibly resizing every animation frame (flame length varies frame-to-frame), the box is measured ONCE as the union across all 4 animation frames × 3 flicker variants per kind+car, then cached and reused for every redraw — stable size, tight fit, no per-kind guessing.
- **Fixed intermittent frozen preview animation.** Root cause: clicking a swatch to equip a booster calls `renderFlamePicker()`, which rebuilds every swatch's DOM via `innerHTML=''` — including the one still being hovered. The browser never fires `mouseleave` on an element removed from the DOM instead of actually left, so `stopFlamePreview()` was never called and its `setInterval` leaked, running forever and fighting later preview sessions over the same shared canvas. Fixed by calling `stopFlamePreview()` unconditionally at the top of `renderFlamePicker()`.

Verified live: preview canvas dimensions now differ correctly per kind on 'hatch' (Thruster 228×108, Underglow 252×126, Pods 248×240) and stay IDENTICAL across all 4 animation frames per kind (no resize jitter); confirmed generalizes on 'stock' (different, correctly-sized dimensions per kind). Interval-leak fix verified via simulated equip-while-hovering on a clean reload: `{afterRender:null, afterHover:1, afterRerender:null}` — leak closed. Zero console errors. Note: this sandbox's browser pane still can't be screenshotted, so sizing was verified via measured pixel dimensions rather than a visual diff.

---

## 2.192.0 — 2026-09-11 00:00: Batch 354 — Booster preview polish (3 small fixes)

- **Rocket Pods' cost dialog centered** — `#confirmCostRow` was left-aligned (missing `justify-content: center`).
- **Booster hover preview now matches Garage tile orientation** (nose-to-the-right) instead of the gameplay-upright direction — reuses the exact same `rotate(Math.PI/2)` + `translate(footprint, 0)` convention `drawCarTileSprite()`/`drawSideways()` already use for the car grid, so it's now visually consistent with every other car sprite shown in the Garage.
- **Preview box now sized per-booster, not a shared worst-case** — Rocket Pods' side pods genuinely need ~15 units of clearance each side, but Underglow/Center Thruster stay within the car's own body width; all 3 used to share Pods' wide padding, wasting space and making the car look small for the other two. Underglow/Thruster previews are now visibly tighter and the car renders bigger within them (since padding shrank, the auto-scale-to-fit factor grows).

Verified live: cost row's computed `justify-content` confirmed `center`; preview canvas dimensions confirmed per-kind (Thruster/Underglow both 228×156, Rocket Pods 228×288 — same nose-tail length, correctly wider only for Pods); a direct comparison against `drawCarTileSprite()`'s own known-correct output confirmed both are wider-than-tall (nose-tail-along-X), matching orientation. Zero console errors. Note: this sandbox's browser pane can't be screenshotted, so the rotation was verified by exactly replicating the already-shipped, already-correct Garage-tile transform rather than a pixel-level visual diff.

---

## 2.191.0 — 2026-09-11 00:00: Batch 353 — Comment cleanup pass

- **Direct request**: the file's comment volume ("almost half the code is comments") condensed drastically. Every multi-line comment block (CSS `/* */`, JS `//` paragraphs, HTML `<!-- -->`) collapsed to a single line — "Batch N — direct request:" prefixes stripped, kept down to the essential first sentence. Applied via a script (not manual edits, given the scale — 15,175 lines) that only ever touches lines that are ENTIRELY a comment, never a line of real code, so nothing structural could be affected by construction. Single-line comments and inline trailing comments (already terse) were left alone.
- **File shrunk from 15,175 → 11,546 lines** (~24% fewer lines), **1,051,456 → 812,837 bytes** (~23% smaller). 601 JS comment blocks, 99 CSS blocks, 34 HTML blocks condensed.

Verified live: zero console errors on load; re-exercised every major system after the pass — achievements (48 cards), Garage (52 car tiles), paint picker (12 swatches), booster picker (3 swatches), Missions view, and a live `launchGame()` + several real frame ticks — all render/run cleanly with no errors. Full history of every past decision these comments used to narrate remains intact in this CHANGELOG regardless.

---

## 2.190.0 — 2026-09-11 00:00: Batch 352 — Booster hover/click UX follow-up

- **Reverted Batch 350's hover-preview status line** — direct follow-up ("take that back"): the booster hover popup is sprite-only again, just the car with the booster applied, no text.
- **Locked-booster status text now lives entirely in the click dialog** instead:
  - Underglow (level-gated) — unchanged, already worked exactly as wanted ("you even have it now").
  - Rocket Pods (coin-gated) — rebuilt into ONE dialog regardless of affordability: title, a real coin-sprite cost row (new `showConfirm({costAmount})`, reuses the same pixel coin icon used elsewhere, not plain text), and the "doesn't fit a few vehicles" note below. The old separate "NOT ENOUGH COINS / you need X more" wording is gone — direct call, the player can already see their own balance. BUY still actually purchases when affordable; the unaffordable case is purely informational (OK-only, no action), reusing the same no-`onConfirm` pattern the gift-only paint dialog already used.

Verified live: hover popup contains only a canvas, no label element exists in the DOM at all; the unaffordable-Rocket-Pods dialog confirmed showing "ROCKET PODS" / a real coin-icon row reading "1,000,000 COINS" / the vehicle-fit note / OK-only with no cancel; the affordable case confirmed "BUY ROCKET PODS?" / BUY+CANCEL; Underglow's level-gate dialog confirmed unchanged; a real end-to-end purchase (click → BUY) confirmed coins deducted, ownership granted, and the booster equipped. Zero console errors.

---

## 2.189.0 — 2026-09-11 00:00: Batch 351 — Multi-Millionaire rename + dev "complete all achievements"

- **Renamed** MILLIONAIRE → MULTI-MILLIONAIRE (display name only, `id` unchanged so existing unlocks aren't affected).
- **New dev-menu button: COMPLETE ALL ACHIEVEMENTS** — maxes out every TIERED achievement's backing stat past its top threshold and unlocks every ONE-TIME/SECRET id directly, same spirit as the existing "OWN ALL CARS & COLORS"/"COMPLETE ALL MISSIONS" tools. A testing/preview shortcut, not a gameplay change.

Verified live: achievement name confirmed "MULTI-MILLIONAIRE"; clicking the new button and re-rendering the achievements screen confirmed all 48 cards (tiered/one-time/secret alike) show fully complete. Zero console errors.

---

## 2.188.0 — 2026-09-11 00:00: Batch 349/350 — Monster/Hover re-tier, tooltip cleanup, real sprite bug fixed

- **Direct re-tier**: Monster Truck epic→legendary, Hover Coupe legendary→epic (swapped).
- **Direct request**: removed every native `title`-attribute tooltip from paint swatches (the color is already visible, no text needed) and booster swatches (the hover preview popup is the only feedback now).
- **Booster hover preview enlarged** ("much bigger... normal size the whole sprite") — max render size roughly doubled (130×190 → 260×380). A status line now shows at the BOTTOM of that same popup when there's something to say (a locked booster's level/coin requirement) instead of a separate tooltip; stays hidden for already-unlocked ones since the sprite speaks for itself.
- **Real bug fixed, direct report ("Monster Truck has doubled headlights, one shifted down")**: `drawGarageMonsterTruck53()` calls the shared `bodyShellW53()` helper, which draws its OWN default headlight pair unless told not to — and this function already draws its own custom headlight bar 2 lines later, so the shell's copy was silently doubling underneath it the whole time, at every size this car is ever drawn. Fixed with `noLights: true`; the shell's taillights (which were the vehicle's ONLY taillights) were re-added explicitly at the same position so nothing was lost in the process.

Verified live: rarity swap confirmed; every color/booster swatch confirmed with an empty `title`; the preview popup confirmed at ~240×190 (up from the old ~130-wide cap) with the status label showing real text for a locked booster and staying hidden for an unlocked one; a direct pixel check on `drawGarageMonsterTruck53()`'s own canvas output confirmed the duplicate headlight pixel is gone, the real headlight bar is intact, and the taillights are preserved. Zero console errors.

---

## 2.187.0 — 2026-09-11 00:00: Batch 348 — Rarity re-tiers + ability-sort Stock fix

- **Direct re-tier, "cool factor" not price**: Garbage Truck common→epic, Camper rare→common, Limousine epic→rare (a 3-way swap chain — garbage↔camper, then limo↔garbage). Go-Kart rare→epic, Time Attack epic→rare (swapped with each other). Time Attack was my own call among the 3 offered (Time Attack/Super SUV/GT3) — GT3 and Super SUV kept their epic slot as the more visually distinctive picks; flag it if Time Attack wasn't the one meant to move.
- **Direct bug report on the Batch 346 ability sort**: Stock now sits inside the JUMP section (it has no `ramAbility`, so it belongs there) instead of floating separately above the sections — TIER and PRICE modes keep Stock separate/ungrouped as before, this only changed for ABILITY mode specifically.

Verified live: all 5 rarity changes confirmed (`garbage`→epic, `camper`→common, `limo`→rare, `kart`→epic, `attack`→rare); ABILITY mode confirmed 52 tiles total with zero standalone tiles before the first section header (Stock now inside JUMP). Zero console errors.

---

## 2.186.0 — 2026-09-11 00:00: Batch 347 — Result-screen achievements panel, exact reference redesign

- **Full rebuild of the result-screen "achievements this run" panel** to match an exact reference screenshot supplied by the user — new CSS (section headers with a dashed rule + count for UNLOCKED, plain label for PROGRESS, bigger 34px icon boxes, colored left-accent bar on unlocked rows, tier label + status value stacked on the right, a solid mint progress-bar "gained" segment instead of the old rainbow-animated one, and a big colored "+N" delta number on progress rows) replacing Batch 302's original compact version entirely.
- **Expanded which achievements can appear here**: was hardcoded to just Score Chaser/Overtaker (the only 2 with a reconstructable per-run delta at the time); now also Too Close To Comfort/Road Rage/High Flyer/Businessman, all of which gained real per-run counters in later batches. Missions/streak/collector/level/Chain Reaction stay excluded — still no honest "this run" delta exists for them.
- **Any ONE-TIME/SECRET achievement unlocked live during the run now shows in UNLOCKED too** — new `newlyUnlockedThisRun`, populated directly inside `unlockAchievement()` itself, so nothing has to be special-cased per achievement.

Verified live: a simulated run (a secret unlock + Score Chaser progress) rendered the exact expected structure — UNLOCKED section with dashed rule/count/pink-accent row/"SECRET"+"COMPLETE" status, PROGRESS section with fraction/bar/delta-segment/colored "+N". Zero console errors. Note: this environment's browser pane can't be screenshotted for a pixel-level comparison against the reference image — verified structurally (DOM/CSS) instead.

---

## 2.185.0 — 2026-09-11 00:00: Batch 346 — Garage sort picker (TIER/ABILITY/PRICE)

- **New sort control** on the Garage screen, reusing the Achievements screen's own tab-button styling. Persisted via `localStorage`, defaults to TIER (today's existing layout).
  - **TIER** (default) — the existing rarity-grouped layout, now with owned cars sorted before not-yet-owned ones within each rarity section (direct request).
  - **ABILITY** — 2 sections, RAM ABILITY and JUMP, splitting every car by whether it has `ramAbility`.
  - **PRICE** — one flat list (no sections) by price ascending.
  - All 3 modes keep Stock first/ungrouped and keep box-exclusive cars sorted after every priced car within whichever section they land in (an existing Batch 192 convention, now applied consistently across all 3 modes rather than just the one layout that used to exist).

Verified live: all 3 modes render the full 52 tiles with the right section headers (COMMON/RARE/EPIC/LEGENDARY for TIER, RAM ABILITY/JUMP for ABILITY, none for PRICE); box-exclusive cars confirmed to never appear before a non-boxed one; a simulated single-owned-common-car state confirmed that car sorts first within its TIER section. Zero console errors.

---

## 2.184.0 — 2026-09-11 00:00: Batch 345 — Real-world car prices

- **All 51 car prices replaced with real-world-researched estimates** (average of the researched market range, not the extreme), fully replacing the old ×50-scaled arbitrary numbers (`CAR_PRICE_SCALE` removed entirely — these are now final absolute values). Researched via live web search against real new-vehicle pricing: hot hatch ~$36K, muscle car ~$52K, supercar ~$275K, hypercar ~$2.8M, go-kart ~$5.5K, tow truck ~$140K, school bus ~$115K, garbage truck ~$325K, fire engine ~$1.2M, monster truck (custom build) ~$220K, road roller ~$55K, GT3 race car ~$500K, IndyCar ~$1.8M, NASCAR stock car ~$300K, F1 car ~$18.5M, military tank ~$15M, and so on for every entry.
- **Confirmed and flagged as expected**: real-world price does NOT respect the game's rarity tiers — a "common" Garbage Truck (~$325K) now costs more than several "epic" cars, a "rare" Fire Engine (~$1.2M) costs more than most "legendary" ones, and "legendary" Steamroller (~$55K) costs less than several "common" cars. This is real-world accurate (rarity here means "how special," not "market price") and was flagged to the user before implementing — they plan to re-tier some cars afterward to match, as a deliberate separate follow-up, not a bug.
- Sci-fi/exotic entries with no real market (Prototype, Land Speeder, Hover Coupe, Jet Bike, Neon Wedge) and racing classes without a public sale price (Formula, F3, LMH, GT3, Indy, Stock Car, Superbike) are judgment-call estimates anchored to their closest real category, not literal lookups — noted directly in the code.

Verified live: all 52 `GARAGE_CARS` entries intact (count unaffected), spot-checked prices match the researched numbers exactly (Hot Hatch $36K, Garbage Truck $325K, Fire Engine $1.2M, F1 $18.5M, Tank $15M, Coachbuilt $3.5M), Garage screen renders all 52 tiles with zero console errors.

---

## 2.183.0 — 2026-09-11 00:00: Batch 344 — Déjà Vu tightened to model-level

- **Direct correction**: Déjà Vu was tracking the broad `vehicleType` bucket (e.g. any 2 'truck' crashes counted as "the same thing"), too easy. Now tracks the actual specific model — the Garage car key if it's one, otherwise the generic body silhouette (sedan/hatch/box/etc.), falling back to type only for vehicles with no model identity (ambulance). New `lastCrashModel`, set in `endRun()` from the real `otherVehicle` instance.

Verified live: crashing into two different truck bodies (box, then semi) correctly resets the streak instead of counting as a match; 3 crashes into the same model in a row (semi/semi/semi) unlocks it, 2 does not. Zero console errors.

---

## 2.182.0 — 2026-09-11 00:00: Batch 343 — 3 new secrets

- **Déjà Vu** — crash into the same vehicle type 3 runs in a row. New `allTimeStats.lastDeathType`/`sameDeathTypeStreak`, checked in `recordRunStats()`.
- **Lucky Start** — spot a legendary car among the first 10 vehicles spawned in a run. New per-run `spawnedVehicleCount`, checked inside the `Vehicle` constructor itself (catches every spawn path — traffic, ambulances, obstacles — uniformly).
- **Exact Change** — level up landing on exactly 0 XP into the new level. Confirmed genuinely achievable first (not just theoretical): every XP source is a whole number and `levelReq()` is always an integer, so the running total can land exactly on a level boundary depending on the sequence of gains. Hooked directly into `gainXP()`'s existing level-up loop.

48 total achievement cards now (was 45).

Verified live: a real 3-in-a-row same-type death sequence confirmed Déjà Vu doesn't fire at 2 but does at 3; the Lucky Start spawn-counting logic confirmed count reaches exactly 10 on the 10th vehicle; Exact Change confirmed both ways — landing exactly on a level boundary unlocks it, overshooting by even 1 XP does not. Zero console errors.

---

## 2.181.0 — 2026-09-11 00:00: Batch 342 — Paint prices flattened + reordered

- **Direct correction**: paint colors were still too cheap even after the ×50 rescale. Every buyable color (Red/Cyan/Gold) now costs the same flat 500,000 — no per-color variation.
- **Picker order changed**: free → buyable → gift/box-exclusive (was an arbitrary mix), so the row reads left-to-right as starter, then purchasable, then box-only.

Verified live: all 3 buyable colors confirmed at 500,000; picker swatch order confirmed free/buy/gift/Prism. Zero console errors.

---

## 2.180.0 — 2026-09-11 00:00: Batch 341 — Tier swaps + MILLIONAIRE

- **Direct tier reassignments**: Jackpot bronze→silver, Clear The Way silver→bronze, Not My Fault silver→bronze.
- **New ONE-TIME achievement: MILLIONAIRE** (Amethyst) — have 10,000,000 coins at once (current balance, not lifetime-earned — that's the separate TIERED "Businessman"). A restraint/hoarding challenge, distinct from Businessman's reward-for-steady-play angle. Fills the ONE-TIME roster's previously-empty AMETHYST slot. New `checkMillionaire()` helper called at every real coin-earning site (run payout, reward rolls, duplicate compensation, mission claims) — not the dev-menu "Add Coins" tool, consistent with how Businessman's lifetime-earned tracking already excludes it.
- 45 total achievement cards now (was 44).

Verified live: all 3 tier swaps confirmed via `achData()`; a simulated balance of 9,999,999 correctly does NOT unlock Millionaire, exactly 10,000,000 does; the card renders with the right tier/description. Zero console errors.

---

## 2.179.0 — 2026-09-11 00:00: Batch 340 — Secrets get their own tier, not bronze-amethyst

- **Direct request**: secret achievements no longer carry a bronze/silver/gold/diamond rank (the old per-secret assignments were flavor-only and were muddying the header's tier-count row, which counted them alongside real tiered/one-time achievements). All 15 secrets now share one dedicated **SECRET** tier instead.
- New SECRET tier listed **first**, before BRONZE, in the achievements header's tier-count row (`ACH_ORDER` — user's own call after thinking it through).
- **New pink color** (`#ec4899`) for the SECRET tier — was reusing the same purple as AMETHYST, which read too similar at a glance. Consolidated the card-accent color into `ACH_TIER.secret` as the one source of truth (was a separate hardcoded `ACH_PURPLE` constant); the SECRET ACHIEVEMENTS section's divider rule updated to match.

Verified live: header tier-count row now reads "SECRET 9 BRONZE 2 SILVER 5..." with SECRET first; its color confirmed `rgb(236,72,153)` (`#ec4899`), distinct from amethyst's `#b06ef5`; a secret card's own `achModel()` output confirmed the same pink accent and `tierLabel: 'SECRET'`; all 44 cards still render. Zero console errors.

---

## 2.178.0 — 2026-09-11 00:00: Batch 339 — Coin abbreviation always rounds down

- **Direct correction**: `coinAbbr()` now always rounds DOWN, never to nearest — showing "2.00M" for 1,999,999 coins would make a player think they can afford something they actually can't. New `truncTo()` floors instead of `.toFixed()`'s round-to-nearest.

Verified live: 1,999,999→"1.99M" (was rounding to "2M"), 9,999→"9.99K" (was rounding to "10K"); every previously-confirmed example (1,021,000→"1.02M", 50,000→"50K", 5,300→"5.3K") still holds. Zero console errors.

---

## 2.177.0 — 2026-09-11 00:00: Batch 338 — Mirror, Mirror bug fixes

- **Real bug fixed, direct report ("spins every time I open the menu/garage")**: the `mirror-spin` CSS class was added on click but never removed once the animation finished, so it stayed on the element forever. Browsers restart a CSS animation whenever its element goes from `display:none` back to visible — exactly what happens every time a screen is left and revisited — so the leftover class replayed the spin on every single visit, not just on an actual click. Now stripped via an `animationend` listener right after it plays.
- **"No achievement" — the unlock itself was actually firing correctly** (double-checked directly); the real problem was that nothing ever told the player they'd earned it. Every other achievement gets shown on the result screen after a run, but this one unlocks from the main menu/Garage, which has no such moment. Added a one-time "ACHIEVEMENT UNLOCKED" confirmation the instant it's genuinely earned for the first time — guarded so it never shows again on later clicks.
- The fancier "ring spins full circle, progress boundary stays fixed" animation idea was NOT built this batch — it needs a new frame-loop-driven canvas animation layered on top of the existing level-up fill-animation system, real added complexity and real risk of the two interfering. Flagged back to the user rather than attempted under time pressure, per their own "skip it if it's a little challenging" allowance.

Verified live: a real dispatched click confirms `mirror_mirror` unlocks and the confirmation dialog shows on the true first click; a direct `animationend` dispatch confirms the class is stripped afterward (closing the display-toggle-restart bug); a second click after already-unlocked still spins but does not re-show the dialog. Zero console errors.

---

## 2.176.0 — 2026-09-11 00:00: Batch 337 — Coin abbreviation, always 3 significant digits

- **Direct follow-up**: `coinAbbr()` now always shows 3 significant digits instead of a fixed 1 decimal — 1,021,000 now reads "1.02M" (was "1.0M", silently dropping real precision). Trailing zeros still strip (50,000 stays "50K", not "50.0K") since those carry no extra information.

Verified live against a full spread: 1,021,000→"1.02M", 50,000→"50K", 5,300→"5.3K", 10,836,220→"10.8M", 999→"999" (unabbreviated, below the 1,000 floor), 123,456→"123K", 1,500,000→"1.5M". Zero console errors.

---

## 2.175.0 — 2026-09-11 00:00: Batch 336 — Booster picker order + Rocket Pods description

- **Booster picker order now follows unlock progression**: Center Thruster (free default) → Underglow (level 10) → Rocket Pods (coin purchase), was the old arbitrary underglow/pods/thruster order.
- **Rocket Pods tooltip now notes vehicle fit**: "Doesn't fit a few vehicles — including most ramming-ability cars." — worded to read as an exception, not a broad limitation.

Verified live: `FLAME_TYPES` order confirmed thruster→underglow→pods; Rocket Pods swatch tooltip confirmed includes the new description line. Zero console errors.

---

## 2.174.0 — 2026-09-11 00:00: Batch 335 — Abbreviation corrections

- **Stats "TOTAL COINS" reverted to the plain exact number** — direct correction, abbreviation was never wanted there.
- **Hover no longer opens a title tooltip** — the displayed text itself now swaps in place: hover the Garage or Daily Gift coin total and it changes instantly to the exact number, move the cursor away and it changes back. (`.onmouseenter`/`.onmouseleave` assignment, not `addEventListener`, so re-rendering the screen doesn't stack duplicate listeners on the same persistent element.)
- **New Settings toggle: ABBREVIATE MONEY** (default ON). Off means every coin number always shows in full, everywhere, no exceptions.
- **Car prices now abbreviate too** — new dedicated `coinAbbr()`/`coinDisplay()` (separate from `achFmt()`, which stays achievement-only), applied to the compact price badge on each Garage car tile. Two real differences from achFmt()'s abbreviation: starts at 1,000 not 10,000 (so a 5,300-coin car reads "5.3K", not the full number), and keeps 1 decimal on the K tier too (matches the "5.3K" example exactly, not rounded down to "5K").
- **Left exact on purpose, everywhere, regardless of the setting**: the "LOCKED — X COINS" hover-card description text and every buy-confirm dialog ("This costs X coins", "You need X more coins") — these are the moments you're deciding whether you can afford something, so the precise number stays visible there no matter what.

Verified live: `coinAbbr(5300)` → "5.3K", `coinAbbr(50000)` → "50K", `coinAbbr(10836220)` → "10.8M" (all match the exact examples given); a real hover-swap test on the Garage total showed "10.8M" → "10,836,220" → back to "10.8M"; the Settings toggle flips the same element between full and abbreviated live; the Hot Hatch tile badge shows "3K" for its 3,000-coin price; Stats now shows the plain number with no hover behavior; the locked-car description and buy dialogs confirmed still using `.toLocaleString()` directly, untouched. Zero console errors.

---

## 2.173.0 — 2026-09-11 00:00: Batch 334 — Extra Box paint bug, paint prices, booster overhaul

- **Real bug fixed, direct report**: `ownsAllPurchasables()` (gates whether Extra Boxes still appear) required every buyable PAINT owned too, not just cars — "paints are included for some reason." Now cars-only, and documented to stay that way even if boost types ever get locked again.
- **Paint prices scaled ×50** — missed in the Batch 332 economy rescale. Red 80→4,000, Cyan 180→9,000, Gold 250→12,500.
- **Booster system overhaul, direct spec**:
  - **Center Thruster** is now the shared free default for BOTH Jump and Ram abilities (neither one specifically defaulted to it before) — the module's default `flameType` flipped from `'underglow'` to `'thruster'`.
  - **Underglow** is no longer free from the start — unlocks at player level 10 (`FLAME_UNLOCK_LEVEL`), same pattern as the existing Prism paint (level 100).
  - **Rocket Pods** is no longer free either — now a real coin purchase, 1,000,000 coins (`FLAME_BUY_COST`), tracked in new `allTimeStats.ownedFlames`. Full buy/confirm flow in the booster picker, mirroring the paint picker's existing locked-swatch pattern exactly (lock icon, price/level tooltip, "not enough coins" dialog).
  - `effectiveFlameType()` now falls back past any type that's car-incompatible OR not yet unlocked, not just car-incompatible.
  - 10 cars given explicit `disabledFlames` overrides per the user's own per-car list: Land Speeder/Dragster/Jet Bike/Go-Kart/Tractor/F3 Junior/Superbike restricted to Center-Thruster-only, F1/Indy Oval/Formula restricted off Rocket Pods only. The other 8 cars named (School Bus, Fire Engine, Road Train, Garbage Truck, Limousine, Monster Truck, Tank, Steamroller) already got the exact same Rocket-Pods-off behavior for free from the existing `ramAbility` default — no code change needed for those, confirmed by cross-checking each one.

Verified live: `ownsAllPurchasables()` returns true with every car owned but zero paints owned; paint costs confirmed ×50; a fresh level-1/no-purchases state confirmed Underglow and Rocket Pods both locked while Center Thruster stays free; the picker correctly falls back a stale-equipped locked Underglow to Thruster; Tractor's picker shows ONLY Center Thruster; a real `buyFlame('pods')` call deducted exactly 1,000,000 coins and marked it owned; zero console errors throughout.

---

## 2.172.0 — 2026-09-11 00:00: Batch 333 — Mission XP fix + coin abbreviation

- **Real bug fixed, direct report**: Batch 332's Missions coin-ladder ×500 rescale was applied to a SINGLE `MISSIONS_LADDER` shared by both coin AND xp-category missions, so XP mission rewards got silently scaled too — never intended, only coins should have changed. Split into `MISSIONS_LADDER_COINS` ([50,000/100,000/200,000], unchanged from Batch 332) and `MISSIONS_LADDER_XP` ([100/200/400], reverted to its original un-rescaled numbers), each mission card/claim now picks the right one off its own `category`.
- **Large coin totals now abbreviate** (`achFmt()`, already used by Achievements — 50,000 → "50K", 10,836,220 → "10.8M") at the 3 places you see your own coin balance: Garage header, Daily Gift header, and the Stats "TOTAL COINS" tile. Hovering any of them shows the exact full number via the browser's native tooltip (`title` attribute) — abbreviated by default, exact on demand.
- Intentionally left alone: individual item PRICE tags (Garage car costs, "this costs X coins" dialogs) — those are catalog values you compare against your balance, not "your money," and weren't part of what was asked; the result screen's animated "COINS EARNED" count-up was also left as-is since abbreviating a live climbing number mid-animation would read worse, not better.

Verified live: `MISSIONS_LADDER_XP` confirmed still `[100,200,400]` while `MISSIONS_LADDER_COINS` stays scaled, checked against a real xp-category and coin-category mission definition; `achFmt(50000)` → "50K" and `achFmt(10836220)` → "10.8M" (matches the user's own example exactly); all 3 balance displays confirmed showing the abbreviated text with the exact comma-formatted number in their `title` attribute. Zero console errors.

---

## 2.171.0 — 2026-09-11 00:00: Batch 332 — Economy rescale + Businessman

- **Car prices ×50** (`CAR_PRICE_SCALE`, applied as a runtime multiply over `GARAGE_CARS` rather than hand-editing 51 numbers) — cheapest car 60→3,000, priciest 20,000→1,000,000.
- **Coin earn-rate ×50**, without touching score/XP: `VEHICLE_POINTS` is shared with the score/XP formulas, so a new `COIN_EARN_SCALE` constant multiplies only the 2 actual `coinsThisRun +=` sites (grounded-pass and jump-over-pass credit) instead of the shared table. Daily Gift/Word coin-tier formula (`REWARD_COINS_BASE_LOWER`/`REWARD_COINS_PER_LEVEL`) and Extra Box duplicate-compensation (`CAR_DUPLICATE_BASE`, plus the flat color-duplicate payout) all scaled ×50 too — pacing is unchanged, only the numbers are bigger.
- **Daily Missions coin ladder ×500** (not ×50), per the settled direction: `MISSIONS_LADDER` [100,200,400] → [50,000,100,000,200,000] — missions are day-limited so making them disproportionately generous is what makes them the deliberate fast track, while normal grinding stays the slower fallback.
- **New `allTimeStats.totalCoinsEarnedLifetime`** — tracks total ever earned, never decreases on spend (unlike `totalCoins`, the spendable balance). Wired into every real coin-earning site (run payout, Daily Gift/Word rewards, Extra Box/color duplicate compensation, Mission claims) — deliberately NOT the dev-menu "Add Coins" tool, which stays a pure testing shortcut.
- **Businessman** — final achievement of the whole roster, TIERED on the new lifetime-earned stat: Bronze 10,000 / Silver 100,000 / Gold 400,000 / Diamond 1,000,000. **44/44 achievements now real — the full system is complete.**
- Number-display abbreviation (K/M for big coin values) intentionally NOT done this batch — `toLocaleString()` commas already keep 7-figure coin numbers readable; flagged as optional follow-up polish, not a real gap.

Verified live: `GARAGE_CARS` prices confirmed exactly ×50 (Hot Hatch 60→3,000, Steamroller 20,000→1,000,000, Stock stays 0); `coinsThisRun` credit confirmed exactly ×50 (grounded 1→50, jumped 5→250) while a parallel `creditVehiclePass()` call confirmed SCORE stayed untouched; a real `rollReward('daily')` call confirmed `totalCoinsEarnedLifetime` tracks alongside `totalCoins` and the Businessman card reads the live total correctly; all 44 achievement cards render across the 3 sections with zero console errors.

---

## 2.170.0 — 2026-09-11 00:00: Batch 331 — Achievements phase 4 (Road Rage/High Flyer/Chain Reaction)

- **3 new TIERED achievements**, each needing a genuinely new lifetime counter:
  - **Road Rage** — lifetime ram kills (`allTimeStats.totalRamKills`), counting both Shield Bump on-touch kills and Tank's ranged shot kills. Bronze 50 / Silver 200 / Gold 500 / Diamond 2,000.
  - **High Flyer** — lifetime vehicles cleared by jumping over them (`allTimeStats.totalJumpClears`, folding the existing per-run `jumpedOverCount` the same way Overtaker already folds `dodgedCount`). Bronze 10 / Silver 50 / Gold 150 / Diamond 500.
  - **Chain Reaction** — most kills landed within ONE continuous ramming activation (`allTimeStats.bestRamChainKills`, new `player.ramChainKills` reset at ram-activation start, only Shield Bump's sustained window feeds it — Tank's instant ranged shot isn't a "chain"). Bronze 5 / Silver 10 / Gold 15 / Diamond 20.
- **Businessman intentionally NOT added** — still waits on the economy-rescale go-ahead (car prices/earn-rate rework), per PLAN.md.
- 43 tiered+one-time+secret cards total now (was 40). `TIERED_IMPORTANCE` updated to place the 3 new ones alongside the other core-action achievements.

Verified live: all 43 cards render with zero console errors; folded a simulated 3-kill ramming activation plus 4 jump-clears through a real `recordRunStats()` call and confirmed all 3 new lifetime stats (`totalRamKills`, `bestRamChainKills`, `totalJumpClears`) landed with the exact expected values.

---

## 2.169.0 — 2026-09-11 00:00: Batch 330 — Letter alert draw-order fix

- **Real bug fixed, direct report ("cars can cover letter alert")**: the Daily Word pre-warning icon (the bobbing present icon that flashes before a letter spawns) used to draw BEFORE the vehicle loop each frame, so a passing car painted right over it. The draw call now happens after every vehicle is drawn, on top of traffic — the timer/spawn logic that decides when the icon disappears and the real letter spawns is untouched, only the visual moved.
- Confirmed (direct question, not a bug): picking up an individual Daily Word letter does NOT grant XP and never has — `collectWordLetter()` only rolls a reward (which can include XP, same as Daily Gift/Extra Box) once the WHOLE word is completed, never per-letter.

Verified live: forced a vehicle to fully overlap the warning icon's exact position, ran a real frame, and sampled the canvas pixel at the icon's center — reads the icon's own gold color (`#ffd700`), confirming it now paints on top of the car instead of underneath it. Zero console errors.

---

## 2.168.0 — 2026-09-10 00:00: Batch 329 — Achievements sorting/filtering removed, fixed ordering

- **Direct correction: the TYPE/PROGRESS/TIER sort picker and the ALL/TIERED/ONE-TIME/SECRET category filter (both just added in Batch 328) are gone** — "not really useful." Replaced with fixed, non-configurable ordering: all 3 sections (TIERED/ONE-TIME/SECRET) always shown, always in-progress-before-complete within each section.
  - TIERED: incomplete ones first, ordered by a hand-picked importance ranking (Score Chaser → Climbing The Ranks → Overtaker → Too Close To Comfort → Collector → Task Master → Daily Grind → Staying Alive), completed ones pushed to the end in the same order.
  - ONE-TIME / SECRET: incomplete ones first sorted bronze→amethyst, completed ones pushed to the end, same tier order.
- Shortened Round The Clock and Lucky Streak descriptions to fit on one line.
- Cleaned up the now-orphaned sort-button CSS (`.ach-sorts`/`.ach-sort-label`/`.ach-sort-btn`) that Batch 329's own markup removal left dead.

Verified live: all 40 cards still render across the 3 fixed sections with zero console errors; tiered/one-time ordering independently checked against the exact sort logic (confirmed a genuinely-complete "Climbing The Ranks" card correctly sorted to the end, and one-time cards showing clean bronze→diamond-then-completed grouping); IN PROGRESS/COMPLETED/ALL tabs still sum correctly (18+22=40).

---

## 2.167.0 — 2026-09-10 00:00: Batch 327/328 — Pull Up! Pull Up! fixed, achievements polish

- **"Pull Up! Pull Up!" now implemented for real** — direct correction: jump immunity only lasts while `abilityState === 'jumping'`, which ends the instant landing completes, so a mistimed jump (released too early / ran out of energy) landing right back into a car still there is a completely normal, already-possible crash. New `player.lastJumpLandTs`, checked in both crash branches for a landing within the last 500ms. The full SECRET roster is now 15/15.
- **Real bug found and fixed**: the achievements header's total count excluded all SECRET achievements entirely (`achData()` only, never `ACH_SECRETS`) — was showing 54/54 instead of the real 69. Now correctly tallies both.
- Trimmed 3 tiered descriptions (Overtaker/Too Close To Comfort/Task Master) that redundantly spelled out "over your lifetime" — every tiered achievement is cumulative by default, per direct feedback. Collector's description cut down to just the first sentence.
- New category filter row (ALL/TIERED/ONE-TIME/SECRET) next to the existing ALL/IN PROGRESS/COMPLETED tabs, independent and combinable with both, persisted the same way (`localStorage`).

Verified live: all 40 cards (8 tiered + 17 one-time + 15 secret) render with zero console errors; header now reads 69 total; category filter buttons individually confirmed (secret=15, tiered=8, all=40 cards); Pull Up! Pull Up! confirmed via a real `player` object showing `lastJumpLandTs` initialized and the unlock condition firing correctly.

---

## 2.166.0 — 2026-09-10 00:00: Batch 326 — Real achievements roster, phase 3 (secrets)

- **14 of the 15 planned SECRET achievements wired up**, each hooked at the genuine gameplay moment: **No School Today** / **Eye Catching** / **You Can't Park There, Sir** (crash into the school bus / a legendary car / an obstacle — main collision loop), **Cease and Desist** (Tank-shot kill on an ambulance), **Too Close, Too Caring** / **Back To Back** (close call with an ambulance / two close calls within 3s — close-call credit block, new `lastCloseCallTs`), **Didn't Even Try** / **Over Before It Started** (0-score run / crash within 5s — `recordRunStats()`), **Word Sacrifice** (crash within 0.5s of collecting a Daily Word letter — new `lastLetterPickupTs`, session-scoped not per-run), **Just In Time** (complete the Daily Word within the last minute before reset — `collectWordLetter()`'s completion branch), **Dripped Out** (legendary car + non-default paint + non-default booster together — `launchGame()`), **Serpentine** (20 lane switches within a 5s sliding window — new `laneSwitchTimestamps`, `Player.update()`), **Addicted?** (1 real hour in one sitting — new `SESSION_START_TS`, checked in `loop()`), **Mirror, Mirror** (click any of the 3 level-badge rings to spin them — genuinely new UI interaction, not just a data hook; click-to-spin wired on all 3 instances via the shared `.level-badge-ring-wrap` class).
- **"Pull Up! Pull Up!" (land on top of a car and crash into it) intentionally NOT implemented.** The jump ability makes the player fully immune to collision for the entire airborne duration, including ambulances, and there's no "landed on top of a vehicle" collision case anywhere in the game — faking it would mean lying about what actually happened, so it's skipped rather than misimplemented. Flag for later if the jump/landing mechanics ever change.
- `ACH_SECRETS` replaced with the real 14-item roster (was 3 old placeholders).

Verified live: all 39 achievement cards render (8 tiered + 17 one-time + 14 secret) with zero console errors; every new check confirmed via direct logic exercise — `recordRunStats()` (Didn't Even Try, Over Before It Started, Word Sacrifice), `collectWordLetter()` (Just In Time), `launchGame()` (Dripped Out), Serpentine/Addicted? window math, and a real click on the menu level badge for Mirror, Mirror (confirmed both the unlock and the spin CSS class firing).

---

## 2.165.0 — 2026-09-10 00:00: Batch 325 — Real achievements roster, phase 2b (remaining one-time)

- Last 6 ONE-TIME achievements wired up, each with its own small new tracking piece: **Jackpot** (win a car from any reward roll — `rollReward()`'s own car-win branch), **Bad Samaritan** (ram an ambulance — the existing Shield Bump ram-kill branch already handles ambulances, just needed the hook), **Spotter** (3 distinct legendary cars in one run — new per-run `Set`, reuses the same "first visible on screen" guard the Daily Missions rare-car spot already uses), **Lucky Streak** (3 Extra Box paint rewards in a row — new `extraBoxColorStreak` counter), **Round The Clock** (every one of the 24 local hours, ever — new `hoursPlayed` array, checked at run start alongside Early Bird/Night Owl), **What A Monster** (first-ever Monster Truck spot — the existing lifetime car-discovery gate already means exactly this).
- **The full ONE-TIME roster (17) is now real.** Remaining phases: the ~16 SECRET achievements (phase 3), then the TIERED ones needing new lifetime counters — Road Rage/High Flyer/Chain Reaction/Businessman (phase 4).

Verified live: all 28 cards render; Spotter/Lucky Streak/Round The Clock/What A Monster confirmed via direct logic checks; Jackpot confirmed via an actual `rollReward('word', false)` call that genuinely won a car (also incidentally confirmed Daily Gift's own reward pool has no car tier — only Daily Word/Extra Box do, matching existing project history); zero console errors.

---

## 2.164.0 — 2026-09-10 00:00: Batch 324 — Real achievements roster, phase 2 (one-time)

- **New persistence layer**: `allTimeStats.achievementsUnlocked` (`{id: true}`) + `unlockAchievement(id)` helper — the real, permanent "was this ever unlocked" flag every ONE-TIME/SECRET achievement needs (unlike TIERED ones, whose progress IS the live stat itself, a one-time trigger like "crashed within 5s" isn't a lasting state to re-check later, so it has to be recorded the instant it happens and never re-derived).
- **11 real one-time achievements wired up**, the "ready now" bucket — each reuses a per-run var or `allTimeStats` field that already existed for other reasons, same reuse pattern the Batch 320 missions already used: **Clear The Way** (ambulance jump-clear), **Full Palette** (all 11 colors), **Car Fanatic** (all 52 cars driven), **I Am Speed** (250 km/h), **Adventuring Time** (all 14 biomes in one run), **Truly A Reckless Driver** (10 close calls in one run), **Not My Fault** (witness an NPC crash), **High Roller** (7.5x multiplier), **Early Bird** / **Night Owl** (run start hour), **Two Of A Kind** (2 ambulances on screen at once).
- Still placeholder: **Jackpot, Bad Samaritan, Spotter, Lucky Streak, Round The Clock, What A Monster** (need real new tracking of their own — phase 2b), and the whole SECRET set (phase 3).

Verified live: all 22 cards render (8 tiered + 11 real one-time + 3 still-placeholder secret); simulated a run hitting 6 of the 11 triggers at once (Clear The Way, I Am Speed, Adventuring Time, Truly A Reckless Driver, Not My Fault, High Roller) and confirmed every one persisted correctly to `achievementsUnlocked` and showed complete (checkmark) in the UI on the next render; zero console errors.

---

## 2.163.0 — 2026-09-10 00:00: Batch 323 — Real achievements roster, phase 1 (tiered)

- First phase of rolling out the FINAL achievements roster (worked out across a long multi-message design pass — see PLAN.md/the "Achievement Roster" Artifact), replacing the Batch 302 placeholder set. This phase: the 8 TIERED achievements that read 100% pre-existing `allTimeStats` fields, zero new tracking needed — **Score Chaser** (total score), **Overtaker** (cars passed), **Staying Alive** (longest run, minutes), **Collector** (cars owned, Diamond=all buyable/39, Amethyst=all 52 incl. box-exclusives), **Too Close To Comfort** (close calls), **Daily Grind** (login streak), **Climbing The Ranks** (player level), **Task Master** (Daily Missions completed).
- Still placeholder, coming in later phases: the 2 ONE-TIME cards (real roster is Clear The Way/Jackpot/etc.), the whole SECRET set, and the TIERED achievements needing new tracking first (Road Rage/High Flyer/Chain Reaction/Businessman — ram-kills-lifetime, jump-clears-lifetime, per-ram-activation kills, and coins-earned-lifetime don't exist as tracked stats yet).

Verified live: all 8 render with correct names, real live `allTimeStats` values (confirmed against this test profile's actual accumulated stats, not stale/hardcoded numbers), correct tier count (Staying Alive's 4-tier ladder, no Amethyst, renders its pips/ladder correctly without assuming a 5th tier); zero console errors.

---

## 2.162.2 — 2026-09-10 00:00: Batch 322 — Overtake mission scaling raised

- Overtake X Cars: scaling raised 0.5→2 cars/level (still rounded to nearest 5). Level 1 stays 100, level 100 now reaches 300 (was 150).

Verified live: level 1 and level 100 goals confirmed at 100/300; zero console errors.

---

## 2.162.1 — 2026-09-10 00:00: Batch 321 — 4 new missions rebalanced

- Overtake X Cars: base 50→100 (kept the same +0.5/level scaling).
- Ram X Cars: base 8→30 (kept the same +level/5 scaling) — ramming is easy, direct feedback.
- Witness A Car Crash: flat 1, level-scaling removed entirely.
- Pass Through X Different Biomes: base 3→5, level-scaling removed entirely.

Verified live: all 4 `resolve()` outputs confirmed at their new flat/base values; zero console errors.

---

## 2.162.0 — 2026-09-10 00:00: Batch 320 — Daily Missions: 4 new missions, reach_multiplier removed

- **Removed `REACH A Xx MULTIPLIER`** — direct call: too swingy in practice, either trivially cheesed with the right car/lane/difficulty combo or unreasonably hard otherwise, with a flat unscaled 3.0x goal that never adjusted for player level either.
- **4 new missions added**, checked against the real pool first (most of the original ask — meet ambulances, reach multiplier, total score, jump over cars — already existed): `OVERTAKE X CARS`, `RAM X CARS`, `WITNESS A CAR CRASH` (NPC-vs-NPC), `PASS THROUGH X DIFFERENT BIOMES`. Overtake/Ram reuse the exact same per-run counters (`dodgedCount`/`ramsUsed`) already tracked for other reasons — no new state needed there. Witness-crash and biome-tracking are genuinely new: a crash counter incremented at the same spot NPC-vs-NPC wrecks already get flagged, and a per-run `Set` of biome keys sampled once/frame during active gameplay.
- Numbers scaled to land in the same difficulty range as the existing pool, not harder: Overtake 50+0.5/level, Ram 8+level/5 (matches Jump Over Cars' own shape), Witness 1+level/25 (matches the similarly-rare Jump-Ambulance mission), Biomes 3+level/25.

Verified live: `reach_multiplier` confirmed gone from `MISSION_DEFS`, all 4 new ones present and correctly resolving/rendering when rolled; ran a full `launchGame()`→`endRun()` cycle with the new counters set and confirmed only the missions actually rolled that day picked up progress (the no-op guard for un-rolled missions working as intended); zero console errors.

---

## 2.161.2 — 2026-09-10 00:00: Batch 319 — Music defaults to 50%, "Other SFX" renamed

- MUSIC VOLUME now defaults to 50% (was 100%), direct request. Real fix required two changes — the `config.musicVolume` object default AND `initSimpleVolumeSlider()`'s own separate hardcoded default argument, which was silently overriding the former at init time regardless of what the config default said (same dual-default pattern the other two sliders already have).
- "OTHER SFX VOLUME" renamed to "SFX VOLUME" — the "Other" read oddly on its own.

Verified live: fresh profile (no localStorage) confirmed landing on `config.musicVolume === 0.5`; label confirmed renamed.

---

## 2.161.1 — 2026-09-10 00:00: Batch 318 — Achievement card text-selection fix

- Direct bug report: clicking a card to expand sometimes selected its text instead (the standard browser double-click-reads-as-selection behavior on clickable text). Added `user-select:none`, the same fix already used elsewhere in this file for the identical issue on other clickable rows (`.stg-toggle`, `.stz-opt`, etc.) — applies wherever this renders (desktop browser, any future app wrapper), not just this page; it isn't a mobile-only concern.

Verified live: computed `user-select` on the card confirmed `none`.

---

## 2.161.0 — 2026-09-10 00:00: Batch 317 — Achievements ladder rebuilt again: reflow instead of overlap

- Direct request, after the overlap approach kept causing real bugs across several batches (border/height desync, then the open ladder physically stealing clicks from the card below it, per Batch 316) that a `pointer-events:none` patch still didn't fully resolve: switched the whole mechanism from "ladder overlaps the grid, doesn't reflow" to "card genuinely grows taller, grid reflows around it" — the user's own proposed fix.
- The tier ladder is now a normal child INSIDE `.ach-card` (not a separate absolutely-positioned sibling anymore) — there's only ONE border on the whole box now, expanding it for real grows the card's real height, and the CSS Grid it sits in naturally pushes later rows down to make room, the same way any normal reflowing content would. Nothing overlaps anything anymore, so the click-stealing bug is gone by construction, not patched around.
- This also deleted a good chunk of the earlier complexity: no more z-index juggling, no more separate ladder-border color to keep in sync with the card's, no more border-bottom-style hide/show timing trick — `achOpenCard()`/`achCloseCard()` are now ~10 lines total instead of ~35.
- Collapsed cards' own resting height is unchanged: the ladder's spacing lives inside its own clipped box (`.ach-ladder-row`'s padding), not the card's outer flex `gap` (which would've added permanent dead space at the bottom of every tiered card, open or not).

Verified live: opening a card confirmed growing its real box height with the ladder measured correctly (not a guess); the card actually below it in the same column confirmed pushed down by exactly the grid's own 12px gap, zero overlap; closing correctly reverts everything; opening several cards in sequence correctly closes each previous one, only ever one open at a time.

---

## 2.160.1 — 2026-09-10 00:00: Batch 316 — Open ladder was stealing clicks from the card below it

- Direct bug report with a screenshot showing multiple achievements stuck open at once, unable to close. Root cause, confirmed via `elementFromPoint()`: an open ladder is genuinely 72px tall against only a 12px grid row-gap, so it physically overlaps the card in the same column, next row — and being raised (`z-index:5`), it silently absorbed clicks meant for that other card. A click meant to open a different achievement was actually re-toggling whichever one was already open, which is how several ended up stuck open with no click able to reach them anymore.
- Fixed with `pointer-events:none` on the ladder — clicks now pass straight through to whatever's actually underneath. The card itself remains the only (and already-primary) way to open/close it, so nothing about the interaction model changes, just the accidental click-stealing.

Verified live: `elementFromPoint()` over the overlapped region now correctly resolves to the card underneath, not the ladder; opening one achievement and then a different one now correctly closes the first and opens the second.

---

## 2.160.0 — 2026-09-10 00:00: Batch 315 — Achievements expand/collapse rebuilt, no more rebuild-on-toggle

- Direct bug report: expand got stuck for a split second, collapse got stuck for much longer (~0.5s). Real root cause: every single toggle click was rebuilding ALL 9 cards' HTML from scratch (`renderAchievementsView()`, plus a double-`requestAnimationFrame` choreography to fake a "from" state on the freshly recreated nodes) — genuine, measurable DOM-rebuild cost on every click, not a CSS timing issue, and worse for collapse since it also had a scrollHeight remeasurement in the mix.
- Rebuilt the whole open/close mechanism: the tier ladder is now always present in the DOM (rendered once, collapsed, whenever the screen is built/tab or sort changes) instead of being conditionally created/destroyed per click. Toggling a card is now a direct, targeted style mutation on just that one card+ladder (new `achToggleCard()`/`achOpenCard()`/`achCloseCard()`) — no rebuild, no rAF hackery, no remeasuring. A real persistent element's own CSS transition just plays normally on a plain property change, the way transitions are meant to work.
- Along the way: switched from the `border-bottom` shorthand (which was quietly overwriting the bottom edge's color too) to `border-bottom-style` specifically, so restoring it after the collapse animation correctly falls back to whatever color the box currently has instead of the stylesheet's static default.

Verified live end-to-end: open sets real measured height + bright border + hidden bottom edge + raised z-index, all synchronously on click; close reverses all of it and restores the bottom border after the .32s slide finishes; opening a second card correctly closes whichever one was already open first; zero errors from this session's actual page execution (one stale error message left over in the console tool from an earlier broken edit in this same session, confirmed NOT reproducible against the current file via direct functional testing).

---

## 2.159.12 — 2026-09-10 00:00: Batch 314 — Collapse "stuck then snaps" fixed

- Direct bug report: the ladder appeared to pause for a moment mid-collapse, then suddenly snap shut. Root cause: `.ach-ladder-open`'s `max-height:140px` was a rough guess, nearly double the actual content height (~72px) — most of the .32s transition ran through height values still bigger than the real content, so nothing visibly moved until height finally dropped below ~72px near the very end of the animation window.
- Fixed at the source instead of re-guessing a better constant: `renderAchievementsView()` now measures the ladder's real `scrollHeight` and animates to/from that exact pixel value via inline style. First attempt at the measurement came back wrong (~24px, just the padding) because the measured element was itself a flex container being clamped to 0 — a flex container's cross-size can compress along with its own clamp. Fixed by moving the actual tier-column row into a new inner `.ach-ladder-row` div; the outer `.ach-ladder` (the one being measured/clamped) is now a plain wrapper that reports its child's true natural height regardless of its own clamp.

Verified live: `scrollHeight` confirmed correctly reporting 72px (24px padding + 48px row) both while class-collapsed and while naturally open; closing's synchronous pre-flip measurement confirmed setting the same accurate 72px as its starting point; zero console errors.

---

## 2.159.11 — 2026-09-10 00:00: Batch 313 — Collapse bottom-border gap, take 2

- Real root cause, found via a screenshot showing the collapsed card fully grey while mid-collapse (not the resting state — this was DURING the animation): the ladder's opacity fade (.32s) was faster than its border-color fade (1s), so it went fully invisible — taking its bottom border with it — well before the color transition finished, leaving the box colored on top/sides but with nothing on the bottom for that gap.
- Fix (smaller/safer than Batch 311's revert-ed full-duration-sync): dropped the opacity fade entirely — `overflow:hidden` + `max-height` alone now drive the reveal/hide. The border no longer disappears early; it stays visible and correctly mid-color the whole time, even squeezed down to a hairline at the end. Keeps the snappier .32s slide feel, only touches the one property that was actually causing the gap.
- Considered but not built (yet): merging card+ladder into one single continuously-bordered box (the user's own suggested alternative — "box expands downward, frame gets colored" — which would eliminate this whole class of bug by construction, since there'd only be one border to animate). Held off since it needs the ladder to stop being a separately-overlapping absolutely-positioned element, which risks reintroducing grid-reflow behavior that was explicitly rejected earlier (Batch 308) — worth revisiting if this smaller fix doesn't hold up.

Verified live: `.ach-ladder`'s transition-property confirmed down to just `max-height, border-color`; zero console errors.

---

## 2.159.10 — 2026-09-10 00:00: Batch 312 — Reverted Batch 311

- Direct request: reverted Batch 311's change (max-height/opacity synced to border-color's 1s). Back to max-height/opacity at .32s, border-color at 1s.

Verified live: transition durations confirmed back to 0.32s/0.32s/1s; zero console errors.

---

## 2.159.9 — 2026-09-10 00:00: Batch 311 — Collapse frame gap fixed

- Direct bug report: on collapse, the ladder (which carries the box's own bottom border) shrank away on a faster .32s timer than the border-color fade's 1s — so for part of the collapse, the top/sides were still visibly mid-color-fade while the bottom border had already vanished entirely. All 3 properties (max-height, opacity, border-color) now share the same 1s duration, so the frame stays complete on every side until the box is actually gone.

Verified live: all 3 transition durations confirmed at 1s; zero console errors.

---

## 2.159.8 — 2026-09-10 00:00: Batch 310 — Whole-box complete brightness, full open/close animation

- **Correction: brighter-on-complete moved from the icon to the whole card box.** Icon border reverted to a plain flat accent on complete (as before Batch 309); the card's own border now uses the tier's brighter tint instead of the old dim complete-tint hex.
- **Expand frame now covers the ladder too**: previously only the card itself flipped to the bright color on expand, leaving the tier-ladder half with a plain neutral border — both now light up together as one unit.
- **Full open AND close animation**: the tier ladder now slides open (height+opacity) when expanding and slides shut in reverse when collapsing, with the border easing color both ways (grey→tier-color opening, tier-color→grey closing) instead of snapping. New `achClosing` state keeps a collapsing card's ladder rendered for one extra render pass (in its "was open" look) so there's something to actually animate FROM, cleaned up via timeout once the animation window has passed.

Verified: icon/card border colors confirmed correct in both directions; the open→closing→cleanup state machine confirmed correct at every step (`achOpen`/`achClosing` values, initial border/class before the animation flip, DOM cleanup after the timeout). As with Batch 309, the actual animation playback isn't independently visually confirmable in this session's test browser (rAF/CSS transitions pause while the pane is backgrounded) — please confirm it looks right in a normal focused tab.

---

## 2.159.7 — 2026-09-10 00:00: Batch 309 — Complete-icon brightness, expand-frame transition

- **Icon border brighter on completion**: uses each tier's own lighter tint (already used for the pip/ladder outlines) instead of the flat base tier color, direct request. Flipped `NO SCHOOL TODAY` to `done: true` (placeholder data) so there's a real complete example to compare against — this is a demo flag, not a real unlock.
- **Expand frame is back, but animated**: the card+icon border again lights up to the tier's bright color on expand (same brightness as the original, pre-308 version) — but now eases in over 1 second instead of snapping instantly, direct request. Technique: the card/icon start every re-render at their resting (grey/dim) color, then a double-`requestAnimationFrame` callback flips them to the bright color one frame later — `transition: border-color 1s ease` on `.ach-card`/`.ach-icon-box` then animates that flip. A plain instant style change in the render string wouldn't animate at all, since every click fully replaces these DOM nodes.

Not independently visually verified end-to-end in this session's test browser — its rAF/animation pipeline is paused while the pane is backgrounded (the same known limitation already documented for this game's canvas `loop()`), so the transition can't actually be watched play out here. Verified everything short of that: confirmed via direct checks that the correct card and correct bright color are identified after each expand, and that `.ach-card`/`.ach-icon-box` carry the `transition: border-color 1s` declaration. Please confirm the actual animation looks right in a normal (focused) browser tab.

---

## 2.159.6 — 2026-09-10 00:00: Batch 308 — Expanded-card frame removed

- Direct bug report: expanding a card showed a bright accent "frame" around the card and its icon, which then visually blended into the card it overlapped below. Tried making the ladder push the grid down instead of overlapping (no more overlap = nothing to blend with) — direct follow-up: expanding should overlap, not move other achievements. Reverted the layout, fixed the actual complaint instead: the card/icon no longer light up with a bright accent border on expand (only genuine completion still colors them) — quiet neutral border only, and the ladder's top border is dropped so it and the card above read as one continuous outer-bordered shape with no seam line between them.

Verified live: ladder confirmed back to overlapping (`position:absolute`), card/icon border confirmed neutral (not accent) on expand, no border between card content and the tier ladder; zero console errors.

---

## 2.159.5 — 2026-09-10 00:00: Batch 307 — "SECRET MISSIONS" renamed to "SECRET ACHIEVEMENTS"

- Renamed the group label and its "N MISSIONS" meta count to "SECRET ACHIEVEMENTS"/"N ACHIEVEMENTS", direct request — avoids overloading "missions," which already names the separate Daily Missions feature.

Verified live: group label and meta text confirmed updated; zero console errors.

---

## 2.159.4 — 2026-09-10 00:00: Batch 306 — Ladder checkmark removed

- Removed the "✓" appended to a cleared tier's goal number in the expanded tier ladder, direct request.

Verified live: ladder goal text confirmed plain numbers, no checkmark; zero console errors.

---

## 2.159.3 — 2026-09-10 00:00: Batch 305 — Achievements section-divider lines brightened

- The TIERED/ONE-TIME/SECRET MISSIONS group-divider rules (ported from the source doc near-black) barely showed against the panel background — brightened to a clearly visible mid-tone of each group's own accent color.

Verified live: all 3 rule colors confirmed rendering at the new brighter values; zero console errors.

---

## 2.159.2 — 2026-09-10 00:00: Batch 304 — Achievements header box removed, ladder text centered

- Removed the header's own dark background/border (read as a nested second panel) — replaced with a plain dashed bottom rule, same divider style `.dg-sticky-header` already uses elsewhere.
- Centered the expanded tier ladder's number and tier-name text within each column (was left-aligned).

Verified live: header background/border confirmed empty, ladder goal/name text-align confirmed center; zero console errors.

---

## 2.159.1 — 2026-09-10 00:00: Batch 303 — Achievements screen fixes

- **Doubled title fixed**: the screen's static shell title and the count-header renderAchievementsView() builds (which already has its own "ACHIEVEMENTS" + live count) were both rendering — removed the redundant static one, the header IS the title now, matching the source doc.
- **Header/tabs/sort now fixed in place**: moved out of the scrolling region into `.dg-panel`'s non-scrolling flex area (same shape as Garage's `.garage-panel`/`.garage-scroll`) — only the card grid scrolls now, direct request.
- **Scrollbar overlap fixed**: `#achievementsView .dg-scroll` gets the same `padding-right: 10px` Batch 233 already gave `.garage-scroll` for the identical complaint — the last grid column no longer sits under the scrollbar thumb.
- **Unit labels added** under each tiered card's X/Y number (SCORE, OVERTAKES, CARS, MINUTES) per direct request, hidden while a card is secret-veiled so it can't hint at the hidden objective.

Verified live: single title confirmed, header/controls confirmed outside `.dg-scroll`, scrollbar padding confirmed 10px, unit text confirmed rendering per card; zero console errors.

---

## 2.159.0 — 2026-09-10 00:00: Batch 302 — Achievements screen + result-screen summary

- **New ACHIEVEMENTS screen**, ported from the user's own "Achievements Tab.dc.html". The `#missionsBtn` placeholder (reserved since Batch 122, labeled ACHIEVEMENTS since Batch 180) is now live. Full engine: ALL/IN PROGRESS/COMPLETED tabs, TYPE/PROGRESS/TIER sort, tiered achievements with pip trackers and a click-to-expand tier ladder, one-time achievements, and secret achievements that stay veiled ("???"/"Unknown objective") until unlocked. Header shows total rungs cleared, a segmented progress bar by tier, and per-tier counts.
- **Placeholder roster, by direct instruction**: shipped with 9 representative achievements (4 tiered, 2 one-time, 3 secret) in `achData()`/`ACH_SECRETS` — not the final list or thresholds, which get reviewed and triaged together next (see PLAN.md's ACHIEVEMENTS SYSTEM entry for the full untriaged idea list). Of the 9, 3 (TOTAL SCORE, PASS X CARS, SURVIVE X MINUTES) already read real lifetime numbers straight off `allTimeStats` (free realism, no new tracking needed); the rest have no dedicated tracking yet and show static placeholder progress.
- **Result-screen achievements summary**: a new `#goAchBox` panel on the crash result screen reports what this run actually did for the 2 real-tracked SUM-style achievements (TOTAL SCORE, PASS X CARS) — reconstructs each one's pre-run value from the post-run lifetime total minus this run's own contribution, then genuinely detects whether this run crossed a new tier threshold (shows "UNLOCKED — GOLD!" etc.) or just made progress toward the next one (shows a delta-highlighted progress bar, prism-animated gain segment). Compact variant of the source doc's wide desktop card, sized for the game's narrow `#gameOverHud` column; its own `.stat-box` sibling so it doesn't disturb the existing `.stat-row:nth-of-type()` entrance-animation delays.

Verified live: all 9 placeholder cards render correctly (tiered pip/bar math, one-time tier tags, secret veiling — confirmed `CHICKEN CROSSED` reveals while the other 2 secrets stay `???`); tab filter/sort/ladder-expand all confirmed interactive via direct DOM checks; result-screen panel verified through the REAL `endRun()` → `recordRunStats()` → `showResultScreen()` path (not just a mock) — confirmed correct tier-cross detection and progress-bar math at several before/after value combinations; zero console errors throughout.

---

## 2.158.0 — 2026-09-10 00:00: Batch 301 — Player sprite blur while steering, traffic anti-clustering

- **Real bug fixed: player's own car sprite blurred the instant it started steering, crisp again once it settled.** Same root family as the garage-preview blur (Batch 295), but never applied to live gameplay: `drawScaledVehicle()` deliberately translates by the raw, unrounded x/y position, a Batch 42 tradeoff kept specifically to avoid NPC traffic stutter at sustained near-zero relative speed (see Batch 248). The player's x only ever moves via the lane-change glide though — a transient ease that's either fully stationary or moving well above the stutter-risk threshold — so it never needed that exemption; Batch 248 just never checked the X axis when it carved out NPCs above a speed threshold. Now rounds the player's draw position (physics stays float, only the draw call snaps) at all 3 of Player.draw()'s `drawScaledVehicle` calls (body, jump-lift, brake lights). Verified live: sampled canvas pixel alpha around the player mid-glide (x=129.36, genuinely fractional) — 0% partial-alpha edge pixels, confirming true crispness, not just "looks fine."
- **Traffic spawn anti-clustering**, direct report with a screenshot showing cars piled into a run of adjacent lanes while the rest of the road sat empty. Root cause: each spawn independently rolled a uniform-random lane with zero memory of the last pick — genuine RNG, but real randomness clusters and reads as broken. Fixed the same way the letter-pickup spawn already solved this (Batch 167, `letterLastLane`): new `lastTrafficLane` excludes the immediately-previous spawn's lane from the candidate pool, still a uniform-random pick otherwise, so it can never repeat the same lane twice in a row.

Verified live: zero console errors across a full launch→steer→300-frame idle cycle; traffic confirmed spawning without repeating the last-used lane.

---

## 2.157.1 — 2026-09-10 00:00: Dead-code cleanup pass

- Removed `.color-swatch.paint-locked` CSS rule and its 6-line explanatory comment — dead since Batch 289 changed Tank's paint-lock UX from dimming swatches to hiding the whole PAINT section (`carCanRepaint()`).
- Removed orphaned `.showroom-model` / `.showroom-tag` CSS rules — unused since Batch 73, predates this session entirely, zero HTML references.
- Updated `TANK_FIXED_COLOR`'s trailing comment, which still referenced the old "paint-locked swatches" behavior — now points at the current `carCanRepaint()` mechanism.
- Swept for `console.log`/`debugger`/`TODO`/`FIXME`/commented-out code and cross-checked every function/constant removed or replaced earlier this session (`snapCanvasToDevicePixel`, `carHasJumpAbility`, old `MUSIC_BPM`, `musicPattern`, `windSound.filter`, jump-wing sprites, `.dg-boxes-hint`) — all confirmed fully clean, no stale references left anywhere.

Verified live: page loads with zero console errors after removals; grepped confirmations that all removed identifiers have zero remaining references.

---

## 2.157.0 — 2026-09-10 00:00: Batch 300 — Master Volume + Music slider, exact ram-energy spec, level-badge animation never resets

- **Settings restructure**: SOUND renamed to MASTER VOLUME and given real teeth — now an overall ceiling multiplied against every category (Music/SFX/Explosion/Ambulance), not just an on/off gate. New MUSIC VOLUME slider added (was silently tied 1:1 to the master before). Every category in the expandable panel now has its own distinct color: Music mint, Ambulance red (unchanged), Explosion orange, SFX purple.
- **Ram energy — exact spec**: base duration (no kills) is now precisely 9 seconds on a full bar (`SHIELD_BUMP_MS_PER_CELL` 500→1000ms), and the per-kill refund is exactly 1/3 cell for a normal car — so 3 kills refunds exactly one full bar, per direct request ("would be nice if it would be round, like 3 cars for one bar"). Truck refund kept at double (2/3 cell). Net: sustaining indefinitely now needs a kill roughly every ~333ms — the "every 500ms" ballpark floated alongside the 3-cars-per-bar spec doesn't land exactly on 9 whole cells at once, so the more concrete round-number ask won out.
- **Real bug fixed: the level-up badge animation reset its acceleration at every level crossed.** Direct report: "don't reset the speed every level... starts slow and then starts spinning faster and faster... even when it comes to a new level it doesn't slow down." Root cause: a multi-level-up ran each level as its own independent `t²` ease-in curve, restarting from zero speed at every boundary. Fixed by driving one continuous eased timeline across the WHOLE animation and mapping its cumulative progress to whichever level segment it currently falls in for display — the ring still visibly rolls over level by level, but the underlying acceleration never restarts.

Verified live: master volume confirmed multiplying correctly into all 4 categories with 4 distinct slider colors; `SHIELD_BUMP_MS_PER_CELL`/refund fraction confirmed giving exactly 9s base duration and exactly 3-kills-per-bar; level-badge animation's implied speed sampled just before/after a level-boundary crossing — continuous within ~2%, no reset; full menu→gameplay→ram→menu cycle with sound enabled, zero console errors.

## 2.156.0 — 2026-09-10 00:00: Batch 299 — Ram-energy fix, wind sound (brown noise), louder explosion, expandable SFX volume settings

- **Real bug fixed: ramming could sustain forever.** Math check confirmed it: at the old 800ms/cell drain rate, a normal ram-kill's 1-cell energy refund covered exactly 800ms of continued drain — so killing traffic faster than once every 800ms (easy in dense lanes) was net-positive energy, an uncapped chain. Fixed per direct request, both halves together: `SHIELD_BUMP_MS_PER_CELL` 800→500ms (back to the original Batch 245 spec, "each bar 0.5s"), and the ram-kill refund halved (1→0.5 cell normal, 2→1 cell truck). Break-even now requires killing something within 250ms, a much tighter margin.
- **Wind sound rebuilt again** — researched real wind-synthesis technique (a "leaky integrator" brown-noise generator, the standard approach: white noise is harsh/hissy at the source regardless of filtering afterward, since every frequency is equally present, whereas real air-rush has a natural low-frequency-weighted rolloff). Same highpass/lowpass/LFO shaping as Batch 298 now runs on brown noise instead of white.
- **Explosion/crash sound: louder and more explosive** — added a sharp bright "crack" transient at the very onset (real explosions have a hard attack before the rumble), and the sub-bass thud layer is now soft-clipped through a WaveShaper for real weight instead of a plain sine thump. Peak volume raised.
- **New expandable "MORE SOUND SETTINGS" panel** under the master SOUND slider in Settings — Ambulance/Siren Volume (previously always-visible) moved in here, alongside two new independent sliders: Explosion Volume and (general) SFX Volume. All three follow the master SOUND on/off gate but aren't multiplied against its percentage, same independent-category pattern the Siren slider already used.
- **Tank shooting sound**: re-confirmed via the real Space-key path (not just calling the function) that it fires correctly — code is right; if still silent, it's very likely this session's known stale-cache issue rather than a real bug.

Verified live: ram-kill refund math checked directly; expand/collapse panel toggles and persists correctly; both new sliders update `config`/localStorage and are confirmed independent of the master SOUND value; wind sound's brown-noise buffer and crash sound's new crack/distortion layers confirmed callable with no errors; full menu→gameplay→crash cycle with sound enabled, zero console errors.

## 2.155.0 — 2026-09-10 00:00: Batch 298 — Speed-scaled music toggle, wind sound rework, click sounds

- **New Settings toggle: SPEED-SCALED MUSIC** (default on) — the BPM-scales-with-speed from Batch 297 is now a real on/off, not forced.
- **Ramming wind sound rebuilt** — direct report: "very bad." Root cause: a single narrow bandpass filter (Q 0.7 at 650Hz) reads as a resonant nasal whine, not a rush of air. Rebuilt as a genuinely broad "shhh": highpass (cuts rumble) feeding a lowpass (cuts harsh hiss) leaves a wide open mid band instead of one resonant peak, with a slow LFO gently drifting the lowpass cutoff for a soft gusting motion instead of a static drone. Lower peak volume too.
- **Tank shooting sound — re-verified, not actually missing.** Traced the report through the real keyboard-triggered path (not just calling the sound function directly): confirmed `playSound('tankshot')` genuinely fires on a real Space-key activation, correctly wired since Batch 297. If it's still not audible, it's very likely this project's known stale-cache gotcha (a hard refresh has fixed several "doesn't work" reports this session that turned out to already be fixed) — flagging in case it persists after a hard refresh, since the code path itself checks out.
- **New: quiet click sound for buttons** — one delegated listener on `.btn` (the single class shared by every button in the game, ~60 uses — BACK/START RUN/BUY/CLAIM/menu nav/etc.) instead of threading a sound call into every individual handler, so new buttons get it for free too. Two quiet pitch variants, picked at random per click.

Verified live: BPM toggle confirmed switching between scaled (142 at top speed) and fixed (128) output; wind sound's new filter graph confirmed structurally in place; Tank shot sound confirmed firing through the real Space-key path (not just a direct function call); click sound confirmed firing on a real `.btn` click event; 3 full menu→gameplay→menu cycles plus a mass click of every `.btn` on screen, zero console errors throughout.

## 2.154.0 — 2026-09-10 00:00: Batch 297 — Jump energy, music overhaul, realistic siren, ramming wind + Tank shot sounds

- **Jump costs ~22% less energy** — `JUMP_FULL_DRAIN_MS` 2500→3200 (direct request: "20-25% less").
- **Music overhaul, focused on "less annoying"**: root cause was the old pattern being only 16 steps (~1.8s at 130 BPM) — looping that fast forever for a whole run is what actually made it grating, more than the raw tones did. Doubled every pattern to 32 steps with real harmonic movement across two distinct halves; added 3 tracks picked randomly per run for cross-run variety; softened instruments (triangle instead of sawtooth/square, a gentle attack ramp, a lowpass on the bass); BPM now scales gently with speed (122→142); and added a genuinely separate, sparse, slow chill track for Menu/Garage/Stats/Setup, which had no music at all before this. Direct decision: kept this procedural (Web Audio synthesis, same as every other sound in the game) rather than downloading real third-party tracks — that raises real file-size and licensing questions worth a separate conversation, not something to do unprompted.
- **Ambulance siren remade — "more realistic and less annoying"**: was a single raw sawtooth oscillator (reads as harsh/synth-buzzy); now two sine oscillators a few Hz apart (the beating gives body without buzz) through a gentle lowpass, and the wail rate slowed from ~0.87s/cycle to ~2.2s/cycle, closer to how a real siren actually sweeps.
- **New: wind/speed rush sound while Shield Bump ramming is active** (not Tank — its shot is instant, not sustained), continuous filtered noise gated per-frame on `abilityState === 'ramming'` rather than hooked into the 5 different places ramming can end (a per-frame check can't miss one the way threading it into all 5 exit paths could).
- **New: dedicated Tank cannon-fire sound**, separate from the generic 'ram' impact thud (which only ever played on an actual hit) — fires on every activation, hit or miss, same as a real cannon.

Verified live: menu chill music starts on Menu and every non-gameplay screen, stops the instant gameplay starts, confirmed via 3 full menu→gameplay→menu cycles with no leaked timers or errors; gameplay music track index randomized and BPM confirmed scaling 122→142 with speed; wind sound starts/stops correctly across a ramming toggle; Tank shot sound and reworked siren both confirmed callable with no errors; jump energy reduction confirmed at 21.9%, inside the requested 20-25% range.

## 2.153.0 — 2026-09-09 00:00: Batch 296 — 0-score runs excluded from every score average/chart

Direct request: a run that ends with 0 points (died before scoring anything) was dragging down every average-score stat just by inflating the run COUNT (it never affected the sum — 0 adds nothing). Fixed everywhere scores get averaged/charted:
- New `allTimeStats.scoringRunsPlayed` (runs with score > 0), used as the lifetime AVERAGE tile's denominator instead of `runsPlayed`.
- The "last 50" average tile now filters `recentScores` to `> 0` before averaging.
- The Stats chart's shared data source (`statsSeries()`) now excludes 0-score runs from every SCORE-driven mode (ALL RUNS, LAST N, AVERAGE OF N, BY PERIOD, PERFORMANCE SCORE) — added empty-state guards to each so an all-zero history shows "0" cleanly instead of `NaN`/crashing. HOURS PLAYED deliberately keeps counting every run including 0-score ones — it tracks WHEN you played, not what you scored, so a 0-score run is still a real data point there.
- Logged a new achievement idea to PLAN.md per the same message: dying with exactly 0 score (distinct from the existing "die within 5 seconds" time-based idea) — working title "Didn't Even Try."

Verified live with synthetic mixed zero/non-zero run history across all 6 chart modes plus both average tiles — every score-based mode's average/points correctly exclude the zeros while HOUR mode correctly still counts them; also verified an all-zero history renders "0" everywhere with no errors instead of crashing.

## 2.152.0 — 2026-09-09 00:00: Batch 295 — Garage sprite blur, the actual real fix

Direct follow-up, fourth attempt: Batch 293's integer-nearest-neighbor upscale still wasn't enough — still visibly blurry. Real remaining cause, found by inspecting the offscreen buffer's own alpha channel directly: the buffer was drawn through `drawScaledVehicle`'s `ctx.scale(CAR_SCALE, CAR_SCALE)`, and CAR_SCALE (1.3) is non-integer — every `fillRect` in a car's own draw function landed on a fractional buffer pixel under that transform, which the canvas rasterizer anti-aliases at every edge regardless of `imageSmoothingEnabled` (that setting only affects `drawImage`/pattern sampling, not native shape rasterization). Batch 293's integer upscale was then faithfully magnifying that already-soft buffer instead of fixing anything. Fixed for real by skipping CAR_SCALE inside `drawCarSpriteUpright()`/`drawFlamePreview()` entirely: per an existing Batch 42 note, `drawPixelCar()`/`car.draw()` only ever emit native-resolution `fillRect` calls — CAR_SCALE is purely an ambient transform `drawScaledVehicle` applies externally — so calling them directly with no scale transform at all makes every `fillRect` land on an exact integer buffer pixel. The one integer upscale from that genuinely crisp native buffer is now the only scaling anywhere in the pipeline.

Verified live by reading the buffer's own pixel alpha values directly (not just "no console errors"): across 5 different cars, every single pixel in the final canvas is either fully opaque (255) or fully transparent (0) — zero partially-transparent/anti-aliased pixels, which is the actual proof of crispness a visual screenshot can't give me in this sandbox. Full regression across all 52 cars × both preview functions × all 3 booster types — zero errors. A hitboxW car's rendered body bounding box confirmed exactly edge-to-edge with no unexpected shift from removing the CAR_SCALE transform.

## 2.151.0 — 2026-09-09 00:00: Batch 294 — Prism grey-body bug (real root cause) + BOXES OPENED relocated

- **Real bug found: Prism paint left most of a car's body grey, only one accent line actually cycling.** Reported on 11 specific cars (Steamroller, Dragster, Formula, Land Speeder, Jet Bike, Superbike, Monster Truck, Indy Oval, F3 Junior, Go-Kart, Tractor). Root cause: `shade(hex, amt)` — used throughout every car's own draw function for panel highlights/shadows — assumes a `#rrggbb` hex string and does `parseInt(hex.slice(1), 16)`. Prism's color was an `hsl(...)` string; parsing that hits a non-hex character immediately and returns `NaN`, which JS's bitwise ops silently coerce to `0`, so every `shade(prismColor, amt)` call became a flat grey (amt>0) or black (amt<0) instead of erroring. Every car actually had this same bug — the 11 reported ones just lean on `shade()` for more of their body than most others, which use the raw color directly for more of their fill and only `shade()` for small accents, masking it. Fixed at the source: `currentPrismColor()` now returns a real hex string (new `hslToHex()`), so every existing `shade()` call already works correctly — no need to touch dozens of individual car draw functions.
- **BOXES OPENED relocated** from the DAILY WORD card's own stat row into the EXTRA BOXES description, replacing the "AFTER THIS: `<next price>`" line, per direct request ("less confusing... under the description of the boxes"). Also dropped the "price rises 150 coins per box" hint text entirely, per direct request ("users will figure it out") — redundant with the price already shown on the buy button.

Verified live: `hslToHex()` checked against 4 known reference colors (pure red/green/blue/white) — exact matches; sampled colored-vs-grey pixel counts before/after the fix across 7 of the 11 reported cars — every one shows a real increase in colored pixels, confirming genuine repaired shading, not just a plausible-sounding theory; Extra Boxes card HTML confirmed showing the relocated stat with the correct combined count, old price label and hint text both confirmed gone.

## 2.150.0 — 2026-09-09 00:00: Batch 293 — Garage sprite blur, actually fixed (removed the scale mismatch entirely)

Direct follow-up, third attempt: Batches 289/290's rounding and device-pixel-snap fixes still weren't enough per a screenshot. The user's own diagnosis was right: the sprite gets drawn small then handed to the BROWSER to scale up via CSS width/height (relying on `image-rendering: pixelated` to keep it crisp) — a real mismatch between the canvas's pixel buffer and its CSS display size that this rendering pipeline doesn't keep reliably crisp. Fixed by removing the mismatch entirely instead of trying to out-guess the compositor: `drawCarSpriteUpright()` and `drawFlamePreview()` now draw into a small offscreen buffer (unchanged, already-correct positioning logic), then bake an INTEGER nearest-neighbor upscale directly into the canvas's own pixel buffer via `drawImage` + `imageSmoothingEnabled=false` — a raster operation, not a compositor hint, so it can't be silently ignored — and set the CSS size to exactly match that buffer so the browser has no scaling left to do at all. Also enlarged both preview windows per direct request: the Garage hover-card sprite column (56px→90px, card 250px→290px) and the booster hover popup (80×118→130×190 max).

Verified live: canvas pixel-buffer size and CSS display size are byte-identical strings for both the hover-card sprite and the booster popup (zero scale mismatch left for the browser to interpolate), `imageSmoothingEnabled` confirmed false, all 4 callers of the shared sprite function checked with no console errors.

## 2.149.0 — 2026-09-09 00:00: Batch 291/292 — Prism live-cycle fix + Daily Word BOXES OPENED stat

- **Real bug found: Prism paint stopped visibly cycling in the Garage.** Every car-grid tile paints with the same equipped color (`resolvePlayerColor()`), not each car's own fixed color, so ALL of them need to re-render while Prism's hue rotates — not just one preview. The existing fix (Batch 161) only redrew the Showroom's single top preview canvas, which Batch 289 removed entirely, so this had silently stopped updating anything visible at all. `refreshPrismCarTiles()` now redraws every grid tile's canvas in place (throttled to 200ms, well under the 12s hue cycle) instead of rebuilding the whole grid.
- **New stat**: DAILY WORD card gets a third tile, BOXES OPENED — lifetime Extra Boxes bought + Daily Words completed (each completion is itself a reward box). Needed a new `extraBoxesOpenedLifetime` field since the existing `extraBoxesOpenedToday` resets daily (it drives Extra Box pricing, not a lifetime count).

Verified live: sampled a car tile's canvas color before/after a simulated time jump — genuinely different, confirming the tile repaints; BOXES OPENED tile renders the correct sum; `buyExtraBox()` confirmed incrementing the new lifetime field (5→6) alongside the existing daily one.

## 2.148.0 — 2026-09-09 00:00: Batch 290 — Hover-info blur (actually fixed) + jump/brake-light bug

Two unrelated direct reports:
- **Hover-info blur, actually fixed this time.** Batch 289's CSS-integer rounding wasn't the real (or at least the whole) cause. Measured live and found `window.devicePixelRatio` is 1.25 in this environment — a real OS/display scale setting, not a sandbox artifact — so a card position that rounds to a perfectly clean CSS integer can still land a descendant canvas at a fractional DEVICE pixel once padding/border/flex-centering stack up (confirmed: a card at a clean `left: 310px` still put the inner canvas at CSS x=316.8, i.e. device x=396.0 only by coincidence — other cases don't land so cleanly). `image-rendering: pixelated` can't fix a position that's off by a fraction of a real screen pixel, only the scaling itself. New `snapCanvasToDevicePixel()` measures a canvas's actual on-screen rect after layout and nudges it with a sub-pixel `translate()` just far enough to land exactly on a device-pixel boundary — applied to both the Garage hover-info card's sprite and the booster hover popup (same underlying bug class).
- **Real bug found: brake lights stayed at ground level (on the shadow) while jumping.** The brake-light overlay pass drew at the car's raw `this.y` unconditionally; the car itself lifts during a jump via an inner `ctx.translate(0, -flightHeight)` applied AFTER the outer draw call's own CAR_SCALE transform. A first-pass fix subtracted `flightHeight` from the OUTER y argument instead — wrong coordinate space (pre-scale), which would have under-lifted the lights by a factor of CAR_SCALE. Fixed properly by applying the exact same inner-translate technique the car body itself uses, so the two are guaranteed to move together.

Verified live: `devicePixelRatio * rect.left/top` is now an exact integer (0.00 fractional remainder) for both canvases, confirmed on the same car/position that measured fractional before the fix; jump+brake combination run across stock, a wide car, and a narrow car with no console errors.

## 2.147.0 — 2026-09-09 00:00: Batch 289 — Booster overhaul, hover-preview bug fixes, ambulance lane-clear fix, hover-card blur fix

Five direct reports/requests in one batch:
- **Boosters unlocked for everyone**: removed all cost/level gating from `FLAME_TYPES` entirely ("unlock all thruster for all cars"). Availability is now purely per-car via a new `carFlameAvailable(car, key)` — `ramAbility` cars default to Rocket Pods disabled, everything else defaults to fully open; a car can override with its own `disabledFlames` list as those get specified one by one.
- **Real bug found: Rocket Pods invisible in the hover preview.** Traced through `drawFlameFxScaled`'s transform: Rocket Pods draws its two side pods ~14 native units either side of the car's own center column — genuinely wider than Underglow/Center Thruster, which both stay within the body. The preview canvas had zero horizontal margin, so pods were clipped clean off both edges. First attempt at a fix undersized the margin (used an 8x multiplier instead of the actual ~15x reach) and still clipped about half the pod — second attempt verified correct via direct pixel-column scanning (pods now span comfortably inside the canvas on both a wide car and the narrowest one, Jet Bike).
- **Top car preview removed** from the Garage showroom per direct request — paint already previews live on the Car Model grid tiles. Boosters get a new floating `#boostHoverPreview` popup instead, shown only while hovering a swatch, positioned next to it (equipped car + hovered thruster, same rendering as before).
- **Real bug fixed: ambulance (and the new breakdown obstacle) deleted already-visible NPC cars from their lane.** Both used to unconditionally clear every vehicle in the target lane the instant one was queued — including cars already on screen mid-pass, which just vanished. Now only vehicles still fully off-screen (never actually seen yet) get cleared; anything visible finishes its pass.
- **Real bug fixed: blurred car sprites in the Garage hover info card.** `getBoundingClientRect()`-derived position was fractional; browsers anti-alias sub-pixel-positioned content regardless of `image-rendering: pixelated` on the canvas inside it. Rounded to whole pixels.

Verified live: Tank/Monster Truck show Underglow+Center Thruster only (no Pods); a normal jump car shows all 3; Pods hover-preview pixel-column-scanned on both a normal-width and the narrowest car — fully inside canvas bounds, not touching either edge; showroom-stage confirmed removed from DOM, popup hidden by default and shown/positioned/hidden correctly on hover; lane-clear fix verified directly (visible car kept, off-screen one cleared); hover-card position confirmed integer; full game loop run across 6 different car types (including ram-ability and narrow ones) with zero console errors.

## 2.146.0 — 2026-09-08 00:00: Batch 288 — Static breakdown obstacle + warning sign

Ported from "Road Decals + Obstacles.dc.html", scoped to only the "breakdown" kind per direct feedback (rockfall/cow/deer dropped — "this just looks pretty weird"):
- New `Vehicle` type `'obstacle'`: a real, permanently parked NPC car — reuses the exact same random body/`GARAGE_CARS` pool and realistic color palette as normal traffic, per direct request ("just place a random car... no new car art needed"). `speedOffset: 0` makes it scroll at exactly `currentSpeed` — genuinely stationary relative to the world, not slow traffic — and it never changes lanes.
- Barrier + 3 tapering cones (`drawBreakdownDressing53`) drawn spanning the lane, positioned so the player reaches them before the parked car itself (matches the source doc's own layering). 4-corner hazard flashers on the car.
- 17x15 warning sign (`drawWarningSign53`) shown ahead of time in the target lane during a pre-warning countdown — reuses the exact same queue/countdown/flash-cadence pattern as the existing ambulance pre-warning (`pendingObstacles`, mirrors `pendingAmbulances`).
- Rides the same spawn pipeline as traffic (`canSpawnAt`/lane-clearance guarantee via new `laneReservedForObstacle()`). Global (every biome), independent low-probability roll — exact frequency wasn't specified by the source doc ("a difficulty-curve question"), so this is a first-pass judgment call, easy to retune.
- Ends the run on contact exactly like traffic (no new collision code needed — just participates in the existing generic check) and can be jumped clean over like anything else.

Verified live: obstacle spawns with a real random body/garageCar and realistic color; direct rect-overlap check confirms `checkCollision` treats it exactly like any other vehicle; pre-warning countdown correctly hands off to a real spawn; dressing art (barrier/cones/hazards) draws without error across every lane index at 3/4/5/10-lane configs; no console errors.

## 2.145.0 — 2026-09-08 00:00: Batch 287 follow-up — Review agent found a real manhole placement bug

Cross-checked Batch 287 with a second agent. Found one real bug: `generateManholes()`'s jitter range (±780px) was wider than its edge margin (300px), so roughly a third of suburb/city segments could place a manhole up to ~480px into the wrong biome next door — the "every manhole lands in a suburb/city segment" claim only held for that one session's random draw, not as a guarantee. Fixed by clamping the final position into the segment instead of just widening the margin (robust regardless of future spacing tuning). Also tightened the oil-mark vertical margin in `makeAsphalt53`, which the same agent flagged as having no real headroom for the largest variant/size combination even though it hadn't actually clipped yet.

Verified live: regenerated biome layout + manholes 200 times (1299 manholes total) — zero landed outside a suburb/city segment.

## 2.144.0 — 2026-09-08 00:00: Batch 287 — Road-surface decals (oil, scuffed dash, manholes)

Ported from the uploaded "Road Decals + Obstacles.dc.html" design doc, scoped down to exactly what was asked (not the doc's full set — no patches/potholes/drains/skid marks yet):
- **Oil marks** (`drawOil53`): translucent soft blobs, 3 fixed sizes (7/12/16px), 3 shape variants (drip/pool/smear). 2 per 576px asphalt cycle, baked into the existing `makeAsphalt53` buffer alongside the pre-existing crude patch rectangles.
- **Scuffed dash**: the existing lane-divider dash system (`drawRoadScene`'s per-frame dash loop) already had a "wear" roll (1% fully missing, 4% faded) — added a genuinely "scuffed" texture on top (chipped paint — individual rows of the dash randomly don't render, ~4.6% chance) and cut the fully-missing rate to 0.4% per direct feedback ("too many gaps").
- **Manholes** (`drawManhole53`): 3 variants, suburb/city biomes only, rare (~1 per 2600px within a matching segment). Unlike oil/dash these need biome awareness, so they're placed the same way as BRIDGES/CROSSINGS — a `MANHOLES` list computed once from the generated biome layout, drawn live in `drawRoadScene`.

Verified live: `MANHOLES` array (10 entries this session) checked against `BIOMES` — every single one lands in a city/suburb segment; oil pixel sampled measurably darker than plain asphalt; `drawRoadScene`/`drawManholes` run standalone across many offsets with no console errors.

## 2.143.0 — 2026-09-08 00:00: Batch 286 — Bug fix found by review agent: buy+auto-equip skipped PAINT/BOOST refresh

Cross-checked Batch 284/285 with a second agent before moving on. It found one real bug: buying a car from the Garage and auto-equipping it updated the preview/grid but never called `renderColorPicker()`/`renderFlamePicker()` — so buying Tank while a jump car was selected left the real paint/booster swatches showing instead of the "no customization" note (and vice versa) until leaving and re-entering the Garage. Fixed by adding both calls to the buy-confirm callback. Also fixed a stale comment nearby that still described boosters as stock-only.

## 2.142.0 — 2026-09-08 00:00: Batch 285 — Booster preview bug fix + narrow-car restriction dropped

- **Real bug found and fixed**: the booster hover-preview canvas was sized exactly to the car's own bounding box, so the flame plume (which extends below the car's rear edge) rendered almost entirely off-canvas — hovering a booster looked like nothing happened, and switching looked broken even though the underlying equip logic worked. Fixed by padding the preview canvas below the car (`FLAME_TAIL_PAD`).
- Removed the always-on flame from the Garage Showroom's default (non-hover) preview — per direct follow-up, this was also what made cars look different there than their normal sprite. Booster art now only shows on hover, same as before Batch 284.
- Dropped the narrow-car (hitboxW<12) forced-single-booster restriction from Batch 284 — every jump-ability car now gets the full 3-way picker, freely switchable, per direct feedback that side boosters scale down fine on most cars.
- PAINT/BOOST TYPE now show an explanatory note ("No paint/booster customization for this vehicle") instead of just disappearing, for cars that can't use them (Tank/ram-ability cars).

Verified live: hover-preview now shows real flame pixel deltas (9→37 orange px on Jet Bike), reverts cleanly on mouse-leave, base preview no longer shows flame; Tank shows both placeholder notes; no console errors.

## 2.141.0 — 2026-09-08 00:00: Batch 284 — Boosters generalized to every jump car + hide unusable paint/boosters

- Booster flames (underglow/pods/thruster) are no longer stock-only: generalized to any car via a uniform-scale wrapper (`drawFlameFxScaled`) around the existing stock flame art, driven by each car's real width/length — reused live in the Garage preview, the BOOST TYPE hover preview, and real gameplay jumps.
- Cars too narrow for side boosters (hitboxW<12: Jet Bike, Land Speeder, Go-Kart) are forced onto Center Thruster only — shown as a single non-clickable "forced" swatch (free, not the paid unlock), since it's their only physically-fitting option. Wider cars keep the full 3-way picker unchanged.
- PAINT and BOOST TYPE sections are now fully hidden (not just greyed out) for cars that can't use them at all — Tank (no repaint, no jump ability) hides both; any non-jump (ram-ability) car hides BOOST TYPE.
- Garage Showroom preview now shows the equipped/forced booster rendered on whichever car is actually selected, not just Stock.
- Removed `activeFlameTypeOverride` (dead after the hover-preview rewrite) and the Tank-specific `paintLocked` grey-out branch (superseded by the hide-the-section logic above).

Verified live: jetbike shows PAINT + only the forced Center Thruster swatch; Tank hides both sections entirely; Hyper (wide) still shows all 3 boosters; garage preview renders real flame pixels on jetbike; forced a jump frame for both a wide car (Hyper) and a narrow one (Jet Bike) with no console errors.

## 2.140.0 — 2026-09-08 00:00: Batch 283 — Realistic NPC colors + two-tone trucks

- Truck/reckless/motorbike/normal NPC color pools swapped from a mix that included pink/lavender/mint/purple to real-world car colors (black, white, grey/silver, navy, red).
- Trucks now roll a separate `trailerColor` (white/grey/black only) independent of the cab color, for bodies with a real trailer (box/semi/tanker) — cab keeps its own color, trailer doesn't have to match.

Verified live: 20 sampled truck spawns confirmed cab/trailer colors roll independently from the correct palettes; pixel-sampled a rendered box-truck's trailer area to confirm the passed trailer color is actually used; confirmed non-truck bodies and calls without a trailer color still render fine (fallback default).

---

## 2.139.0 — 2026-09-08 00:00: Batches 281-282 — Real bug: biomes invisible in gameplay; ram-kills now score 2x

**Batch 281 — biomes rendering blank on the sides, root-caused and fixed.** Direct bug report: "biomes don't appear on the sides, it's just blank grey." Root cause: `makeStrip()` baked the ENTIRE biome cycle into one canvas element sized `BIOME_CYCLE` px tall — harmless at the old 28,800px cycle, but Batch 278 (2x longer segments) + Batch 279 (8→12 segments, 6 new biomes) pushed a real generated cycle up to ~89,000px, past this environment's own measured max canvas height (~65,484px via binary search — and known to run far lower on some real mobile browsers this game targets). Setting `canvas.height` past that limit doesn't throw or clamp visibly — the property still reads back whatever you set it to, but every draw call into it silently becomes a no-op. Confirmed directly: the built strip buffer's own pixels were alpha-0 everywhere, with zero exceptions thrown anywhere in the pipeline — a genuinely silent failure mode.

Fixed by paginating: `makeStrip()` now returns an array of small page buffers (4000px each, safely under any real browser's limit) covering the full cycle between them, instead of one giant canvas. Every per-biome drawing routine is unchanged — each page just applies `translate(0, -pageY0)` so the same absolute-coordinate drawing calls land correctly, and a cheap segment-vs-page overlap check (added to all 3 passes: ground, shoulder, props) skips a segment's real work when it doesn't touch the current page, so total work stays proportional to cycle length, not `pages × cycle length`. `drawRoadScene()`'s verge-draw loop updated to iterate and cull pages instead of one `drawImage` call.

Verified live: confirmed the exact failure mode first (a real canvas set to the current BIOME_CYCLE height silently drops all draws); after the fix, sampled the actual rendered game canvas — real ground colors now appear at the verge (previously solid black/transparent) — across 21 pages per side at the current ~82,560px cycle, with no errors, including after scrolling deep past multiple page boundaries (no seams/gaps).

**Batch 282 — ram-kills (Shield Bump, non-Tank) now also score, at 2x.** Direct request: "running [ramming] a vehicle with the ramming ability gives you two times the points." Batch 222 had removed scoring from non-Tank ram-kills entirely (energy-only payoff, since the ability itself costs energy to activate) — now scores too, at 2x the same per-vehicle rate a normal pass credits (`creditVehiclePass()`'s own points formula), matching the same "2x for a skilled kill" pattern jump-over and Tank's own shot already use. Added on top of the existing energy refund, not instead of it. Verified live: forced a real ram-kill (confirmed via `v.crushed`) and matched the exact expected score (`Math.round(points × multiplier × 2)`) precisely.

---

## 2.138.0 — 2026-09-08 00:00: Batch 280 — Hours-played Stats chart

New chart mode: "HOURS PLAYED", a bucket-by-hour-of-day (0-23) view of when the player actually plays, with a RUNS/% display toggle (same reasoning as the original request's "option to see in % or hours/minutes" — simplified to RUNS-count vs. % of total runs, since the game only tracks a start TIMESTAMP per run, not per-hour duration, so "how many runs started in this hour" is what's actually derivable without adding a new stat). Reuses the existing chart's line/area/tooltip machinery entirely — no new HTML, `kinds`/`paramSets` are already fully dynamic — rather than building a separate bar-chart renderer.

Two small adaptations needed since hour-of-day buckets aren't a real timeline like every other chart mode: `statsTicksFor()` gained a `mode === 'HOUR'` branch that reads tick labels straight from each point's own key ("00:00" etc.) instead of computing them from a `.date` span; the hover tooltip's date row is now hidden for these points (`noDate: true`) since an aggregate across every day ever played has no single real date to show.

Verified live: seeded `runHistory` with a known distribution (3 runs @ 14:00, 1 @ 09:00, 6 @ 22:00) and confirmed `statsSeries()` returns the exact right counts per hour, correctly identifies 22:00 as the busiest hour, and the % toggle computes the right percentages (60/10/30); confirmed the real UI renders the new "HOURS PLAYED" option and RUNS/% buttons, hour-formatted tick labels, and a hover tooltip with the correct key/value and no date row.

---

## 2.137.0 — 2026-09-08 00:00: Batch 279 — 6 new biomes + river/side-road crossing variation, from "Panorama Biomes v2.dc.html"

Ported from the uploaded design doc, adapted into this file's own `makeStrip()` idiom (per-biome ground-pass special cases + a prop-scatter table) rather than the doc's own generic `terrain()`/`fbm()` system — that's a different rendering pipeline built for the doc's much wider 140px reference plate; the existing biomes ported earlier (mountain/river/coast) already used this same simpler, hand-adapted approach, so these follow the same precedent instead of introducing a second art system.

**6 new biomes**, each with its own `GROUND` palette, a ground-pass treatment, and (where the doc called for it) new prop sprites:
- **Desert** — open hardpan, sun-cracked ground streaks, one meandering dry-wash channel per side, cactus/rock/scrub scatter (new `sprCactus53`).
- **Canyon** — shares Mountain's rock-wall ground-pass shape (now `seg.k === 'mountain' || seg.k === 'canyon'`) with its own warm palette and no snow accent, cactus/rock scatter.
- **Industrial** — a sparse dotted chain-link fence line eaten into the shoulder, storage tanks and smokestacks in plan view (new `sprTank53`/`sprStack53`), deliberately sparse otherwise per the doc's own note.
- **Quarry** — 4-step terraced bench bands stepping toward the shoulder, rubble scatter.
- **Marsh** — layered-noise standing-water pools, reed clumps (new `sprReed53`), boardwalk-plank shoulder (added to the existing "hard shoulder" set).
- **Orchard** — shares Farm's furrow-line ground-pass (now `seg.k === 'farm' || seg.k === 'orchard'`), trees placed on a fixed cadence instead of random scatter — direct doc note: "regularity is what reads as planted from above."

**Rarity** — my own call, per direct instruction ("how do you think it should be best"): Desert/Canyon/Quarry/Marsh join Mountain/River/Coast's "more rare" tier (weight 1) — all visually striking biomes that should feel like a real event. Industrial joins Suburb/City's "a little rare" tier (weight 2). Orchard sits one tier below plain Farm (weight 2) as a variant, not a duplicate of an existing common biome. `BIOME_SEGMENT_COUNT` raised 8→12 to keep decent representation now that the pool is 14 biomes instead of 8.

**Crossing variation** ("the river and like side road variation"): `drawCrossing()` now takes an `opt` (`amp`/`skew`/`phase`, ported from the doc's `crossHalf()`), and each `CROSSINGS` entry rolls a random variant at load — square/angled-either-way/strong-meander for the river crossing, square/two skew directions/curved for the side-road (underpass) crossing — instead of the one fixed meander shape every crossing used before.

Verified live: forced sequences containing every new biome key rendered through `makeStrip()` with no exceptions (worst-case timing ~460ms per side — still a one-time page-load cost, consistent with Batch 278's existing "build once" reasoning); ran 200 real game frames through a forced all-new-biomes sequence with no errors; pixel-sampled the built strip buffer at a Desert offset (sandy tan, not black/broken) and a Marsh offset (olive-green, not black/broken); confirmed `CROSSINGS` entries carry distinct randomly-rolled `opt` objects.

---

## 2.136.0 — 2026-09-08 00:00: Batch 278 — Biomes: 2x longer, randomized order, real rarity tiers

Direct follow-up to the earlier "make biomes last longer / any rarity ideas?" ask, now with concrete numbers:

1. **2x longer**: every biome's base segment length is unchanged in the data (`BIOME_DEFS`), just multiplied by a new `BIOME_LEN_MULT = 2` when the cycle is built.
2. **Random order, not a fixed cycle**: the old hardcoded `BIOMES` list (always meadow→forest→coast→farm→mountain→suburb→river→city→loop) is gone. `generateBiomes()` now draws 8 biomes via weighted random pick (repeats allowed — matches the user's own example, "forest meadow meadow forest mountain forest meadow meadow river"), then appends a short loop-out segment matching whatever the sequence's own first pick was, closing the cycle invisibly same as before.
3. **Real rarity, via pick WEIGHT not segment length**: direct correction — "rare" means less likely to be picked, not a shorter stretch when it does show up. Meadow/Forest/Farm stay the common baseline (weight 3), Suburb/City are "a little rare" (weight 2), Mountain/River/Coast are "more/pretty rare" (weight 1) — roughly the "two times more often, or even more common" scale the user gave as an example.
4. **Regenerated once per page load, not per run**: `makeStrip()` bakes the whole cycle into an actual pixel buffer — measured at ~430ms EACH for the L/R verge strips at the OLD length, so redoing this on every "START RUN" click would be a real, visible freeze at the new 2x length. Kept the existing "build once, lazily, shared by menu + every run" caching this file already used, just filled with a freshly randomized order at that one build instead of a hardcoded list — every page load/reload gets a different order, individual runs within one session share it.
5. **Bridges/river-crossing repositioned dynamically**: the 2 named bridges (forest, city) and the river crossing used to sit at hand-picked Y positions that happened to land inside the matching biome under the old fixed cycle — with random order, a fixed Y can't be trusted to land on the right ground anymore. `findBiomeMidpoint()` now locates the first real segment of the matching biome in whatever sequence just got generated and places the set-piece at its midpoint (falls back to the old fixed value on the rare chance an 8-pick random draw doesn't include that biome at all).

Not implemented yet, deliberately: the user floated possibly waiting for a few new biome ideas before doing this pass — decided to proceed now rather than wait, since `BIOME_DEFS` is a plain list any new biome just gets appended to later, no rework needed.

Verified live: `BIOMES` after a fresh load shows correctly doubled `n` values and a loop-out matching its own first entry; a 20,000-draw statistical sample of `pickWeightedBiome()` landed within ~1 percentage point of every tier's expected share (common ~18-19% vs. 18.75% expected, semi-rare ~12-13% vs 12.5%, rare ~6-6.4% vs 6.25%); a full run launched and played 30 frames with no errors; confirmed the fallback path fires correctly when a given random draw happens to omit a biome entirely (a real draw with 0 'city'/'river' picks correctly fell back to the old fixed Y for both).

---

## 2.135.0 — 2026-09-08 00:00: Batch 277 — Jet Bike Garage-tile sizing, finally fixed (3rd attempt)

The long-open "Jet Bike looks too big/blocky next to Superbike" item, genuinely tried twice before and reverted both times — this attempt used a different technique specifically to route around what killed the first two: pixel-measurement-driven verification (`getImageData`) instead of needing a real screenshot, which this sandbox's Browser pane can't reliably composite.

Root cause confirmed by measurement: Jet Bike's tile-only render (`drawCarTileSprite()`) fills its own cropped bounding box with genuinely **zero** margin on every side (both fill ratios measured exactly 1.0), while Superbike — the named "looks right" comparison — has real margin on 3 of 4 sides (96% width fill, 57% height fill). A real hitboxW change wasn't warranted just to fix how snugly a Garage tile crops around the sprite (that would touch collision/spawn-clearance), so the fix lives entirely in the tile-rendering path: `drawCarTileSprite()` gained two new optional per-car fields, `tilePadLen`/`tilePadWidth`, defaulting to 0 (byte-identical output) for every car except Jet Bike, which now gets `tilePadLen: 1, tilePadWidth: 3` — padding added only to the cropped tile canvas, GARAGE_CARS' real `hitboxW`/`h` untouched.

Verified via pixel measurement: Jet Bike's height fill ratio now measures exactly 0.571, matching Superbike's own 0.571 exactly; width fill ratio 0.909 vs Superbike's 0.958 (same ballpark). Confirmed symmetric margins (1px each side lengthwise, 3px each side widthwise) and confirmed several other cars (Stock, Tank) measure byte-identical to their pre-change values, ruling out any regression from the new optional fields.

---

## 2.134.0 — 2026-09-08 00:00: Batch 275 — Leaderboard BACK button pinned; steering multi-lane drag investigated (no bug found)

1. **Leaderboard BACK button stays visible now**: same fix Batch 92 already gave the Garage screen — `#leaderboardView`'s `.settings-panel` gained the `.garage-panel` class (flex column, `overflow:hidden`) and `#leaderboardList` is now wrapped in a `.garage-scroll` sub-container, so only the run list itself scrolls; header/filters/BACK all stay fixed in place. `showLeaderboard()`'s scroll-reset updated to target `.garage-scroll` instead of the whole panel. Verified structurally (this sandbox's Browser pane can't composite real pixels for a geometric screenshot check, per its known `document.hidden` limitation) — confirmed the panel is `display:flex; overflow:hidden`, the scroll container has `overflow-y:auto; flex:1 1 auto`, the list is nested inside it, and BACK's row is a DOM sibling positioned AFTER the scroll container, exactly matching the Garage screen's proven-working structure.
2. **Steering "can't change multiple lanes while holding/dragging" — investigated, could not reproduce**: tested all 3 input paths via simulated events — Hold & Drag (mousedown + mousemove across the track), Move to Steer/hover (mousemove alone), and touch (touchstart + touchmove) — all three correctly update `player.targetX` on every step of a continuous drag across multiple lane zones, and `player.x` genuinely glides all the way across (tested lane 0 → lane 4 in one gesture, arrived correctly). No code defect found in this environment's testing. Left open in PLAN.md pending a more specific repro from the user (exact input method, possibly touch-device-specific behavior this sandbox can't fully emulate).

---

## 2.133.0 — 2026-09-08 00:00: Batch 274 — Two more Tank bugs: double-kill on close targets, and your own ram-kills still paying out on pass

Two direct follow-up reports after Batch 273:

1. **"Shoot a close vehicle, the shot goes over it, kill two at once"**: root cause in `findTankShotTarget()` — a vehicle close enough to already be touching the barrel is deliberately excluded from RANGED targeting (that's melee's job), but the old code just `continue`d past it to keep searching for a farther valid target. So one activation could destroy the close vehicle via melee touch AND a second, more distant one via the ranged shot. Now returns `null` the instant any same-lane vehicle is that close — the ranged shot simply doesn't fire on a target that activation, so at most one vehicle (whichever the melee touch actually connects with, if any) dies per shot.
2. **Corpses still refilling energy — narrowed down to your OWN ram-kills specifically**: direct clarification distinguishing the two corpse types — `.wrecked` (an NPC that crashed into ANOTHER NPC, not dark/blackened, Batch 265-267) SHOULD still give the normal pass credit (score/coins/energy) when you drive past it, same as any other traffic you dodge; but `.crushed` (your own ram-kill, dark/blackened) was ALSO still getting that same pass credit on top of the reward it already paid out at the moment of the kill — a double-dip. Both `creditVehiclePass()` call sites now skip `.crushed` vehicles specifically, `.wrecked` ones untouched.

Verified live: forcing a close same-lane vehicle to exist makes `findTankShotTarget()` return `null` even with a valid farther target also present, while a scene with only the farther vehicle still targets it correctly. For the pass-credit fix — driving past a `.wrecked` corpse still grants the normal +1 cell (11.11 energy, confirmed via a wrapped `creditVehiclePass()` call counter), while driving past a `.crushed` one (the player's own kill) now grants nothing.

---

## 2.132.0 — 2026-09-08 00:00: Batch 273 — Ram cell duration bumped, Tank fire-rate lockout, two more ram-payoff bugs closed

1. **Ram bar duration**: `SHIELD_BUMP_MS_PER_CELL` 500ms → 800ms, direct spec ("make the ram 1 energy bar 800ms"). `RAM_DRAIN_PER_FRAME` and `RAM_MIN_ACTIVE_MS` (Batch 269) both derive from this constant, so both scaled automatically — a full 9-cell bar now lasts 7.2s instead of 4.5s.
2. **Tank real firing lockout**: direct follow-up to Batch 272's animation — Tank now genuinely can't fire again until the full reload cycle (drain + the 1.5s recharge tween) is done, not just once the 200ms shot window ends. The existing `abilityState !== 'idle'` guard already blocked re-firing during the drain phase; a new `if (this.tankReloadPhase !== 'idle') return;` check closes the recharge-phase gap.
3. **Wrecked corpses could still be "destroyed" by a ranged shot**: `findTankShotTarget()` only excluded `.crushed` vehicles, not `.wrecked` ones (Batch 265-267's NPC-vs-NPC crash mechanic) — Batch 272 fixed this for the melee/touch ram-payoff branch but missed the separate ranged-shot targeting function, so a shot could still pick an already-wrecked corpse as its target and pay out score/XP for "destroying" it. Now excludes both flags, matching the melee branch.
4. **Reported lag while shooting Tank repeatedly, investigated**: profiled `drawSbExplosionFrame` directly (a single explosion's full 12-frame draw costs ~7ms total, ~0.6ms/frame — cheap in isolation) and confirmed via instrumented `loop()` calls that cost scales with how many explosions are concurrently alive. Each explosion lives 540ms (12 frames @ 45ms); before this batch, Tank could refire every ~200ms while spamming, so 2-3 explosions could overlap and stack their draw cost every frame, plus the object churn from `sbExplosionParts()` (up to ~98 short-lived objects per shot) adding real GC pressure under rapid fire. Couldn't fully reproduce this sandbox's own multi-second frame spikes reliably (some observed spikes look like sandbox/tool artifacts, not the game itself) — but #2's firing lockout structurally caps Tank to one shot per ~1.7s cycle, which makes concurrent-explosion overlap impossible by construction. Flagged to the user as the most likely fix rather than a guaranteed one; worth confirming after real play.

---

## 2.131.0 — 2026-09-08 00:00: Batch 272 — Tank's real drain-then-recharge ability bar animation, and a wrecked-car energy-refund bug fix

Two direct reports:

1. **Tank reload animation, actually built this time**: direct follow-up — Batch 200 had rejected an earlier generic drain animation as "jarring", and the bar was just showing real energy directly (looked instant/snapped). New spec, a real scripted two-phase tween purely on the DISPLAY (real energy/gating untouched): on firing, the bar drains fast to 0 over the shot's own real duration (`TANK_SHOT_WINDOW_MS`, 200ms); once the shot window ends, it recharges from 0 up to whatever energy the player actually has, always over a FIXED `TANK_RELOAD_ANIM_MS` (1.5s) regardless of how much that real amount is — a half-full recharge isn't slower than a near-full one. New `Player` fields: `tankReloadPhase` ('idle'/'drain'/'recharge'), `tankReloadMs`, `tankReloadFromEnergy`.
2. **Wrecked cars no longer give a ram-kill payoff**: direct bug report — ramming/shooting an already-`.wrecked` vehicle (Batch 265-267's NPC-vs-NPC crash mechanic — a real, solid, collidable obstacle by design, not a fresh target) still counted as a kill and refilled energy/scored. The ram-payoff branch's condition now excludes `v.wrecked`; hitting one falls through to the normal crash branch instead, same as hitting any other real obstacle.

Also logged 2 new achievement ideas to PLAN.md ("spot a car crash", "shoot the ambulance") and split the open "Tank reload system" PLAN item — the animation is now done, but whether Tank should also be LOCKED OUT of firing again during that window (the original complaint's "basically unkillable" half) is still an open, unconfirmed question.

Verified live via direct `player.useAbility()`/`player.update()` stepping: firing drops real energy instantly (100→66.67) while `tankReloadPhase` flips 'drain'→'recharge' exactly when the 200ms shot window closes; at the ~750ms mark (half of 1.5s) the computed display value sits at ~33.3, half of the real 66.67 energy, confirming the fixed-1.5s recharge rate; phase returns to 'idle' once the full window elapses. For the wrecked-car fix: forced a `.wrecked` vehicle to overlap the player mid-ram and stepped `loop()` — the run ended (`gameActive` false, a normal crash) with `ramsUsed` still 0 and `energy` unchanged, confirming no payoff was granted.

---

## 2.130.1 — 2026-09-08 00:00: Batch 271 — Ram's upfront fee now animates instead of instant-snapping

Direct follow-up to Batch 269's 1-bar upfront activation fee: it vanished from the ability bar instantly on activation, which read as a confusing glitch rather than a real cost. The real energy deduction/gating is untouched (nothing here can afford to lag — the forced minimum window and future gate checks all still need the true value the instant it changes) — this only smooths what the BAR shows: for the first `RAM_FEE_ANIM_MS` (100ms — "a tenth of a second... but still visible"), the displayed fill tweens from its pre-fee value down to the real (already-deducted) energy, then falls back to tracking real energy directly for the rest of the ramming duration.

Verified live via direct `player.useAbility()`/`player.update()` stepping: real energy drops instantly (100→88.89) on activation as before, but the manually-computed display value at the 50ms mark sits at ~93.9 — genuinely mid-tween between the pre-fee and real value, not snapped to either endpoint — and the tween completes by 100ms as expected.

---

## 2.130.0 — 2026-09-08 00:00: Batch 270 — Tank barrel fix + Tank locked to one fixed color

Two direct requests from the uploaded "Tank Barrel Fix.dc.html" design doc and a follow-up:

1. **Barrel/turret joint fix**: `drawGarageTankArt53` replaced wholesale with the doc's own "A · LONG GUN" design (`drawFix(dy=4, tTop=13, tipY=1, tint=false)` — the plain grey-mantlet variant, NOT its A2 sibling which paints the mantlet in the car's color). The doc's diagnosed root cause: the old barrel drew AFTER the turret and had to stop short to avoid painting over it, so the joint always read as a cut, and the hull front never pulled back — no part of the barrel cleared the hull at all. Fixed by flipping the draw order (barrel first, turret over it, a grey mantlet last bridging the seam) and pulling the hull front back 4px, giving the barrel 9px of free air (6px actually clear of the hull).
2. **Tank locked to one fixed color**: direct follow-up — Tank can no longer be repainted at all. `drawGarageTank53` now force-overrides whatever color its caller passes with a new `TANK_FIXED_COLOR` (`#4f6b3a`, the doc's own "olive" reference), so it renders the same regardless of the player's actually-equipped paint. The Garage color picker (`renderColorPicker()`) greys out every swatch (including Prism) — same dimmed look as a disabled menu button (`.btn-disabled`'s opacity:.4), a new `.paint-locked` class — while Tank is selected; clicking one still works but shows an informational popup ("This vehicle cannot be painted") via the existing `showConfirm()` pattern instead of equipping.

Verified live: `drawGarageTank53` called with `'#ff0000'` renders in olive tones, not red, confirming the override actually takes; the color picker shows all 12 swatches `.paint-locked` + correct tooltip while Tank is selected, and clicking one opens the real confirm modal with the right title/text; pixel-sampled the rendered sprite — the barrel column is fully opaque and unbroken from muzzle to hull (no gap), and the free-air rows beside it (above the pulled-back hull front) are genuinely transparent.

---

## 2.129.0 — 2026-09-08 00:00: Batch 269 — Ram (Shield Bump) can't be spammed for cheap kills anymore

Direct bug report: "press space twice, destroy a car, only costs one bar, a little too good." Three changes together close that:
1. **1-bar upfront fee**: activating Ram now needs 2 bars (was 1) — one is spent immediately as a flat activation fee, the other is budget for #2 below.
2. **Forced minimum active window (500ms)**: once activated, Ram can't actually end — by manual cancel OR by hitting 0 energy — until 500ms of real time have passed. A cancel pressed early is queued (`ramCancelQueued`) and applied the instant the window closes, instead of being ignored or firing immediately. Combined with #1, a same-frame tap-and-cancel now always costs a real minimum of 2 bars, never 1.
3. **No partial bar left behind**: whenever Ram actually ends (window elapsed + cancelled/empty), energy floors down to the nearest whole-cell boundary — same technique Jump's own Batch 115 fix already uses. Ending mid-bar always consumes that whole bar, never leaves a fractional sliver.

The ready-glow threshold (`readyThreshold` in the ability-bar draw code) raised 1→2 cells to match, so the bar's own "ready" glow can't disagree with what `useAbility()` actually requires. Ram-kill's live energy refund (unchanged) still applies on top of all this — a skilled, connecting ram still outlasts an idle one, it just can no longer be farmed for a near-free kill via instant cancel.

Verified live via direct `player.useAbility()`/`player.update()` stepping (bypassing this sandbox's stalled real-`requestAnimationFrame`): activating with exactly 2 cells succeeds and deducts the upfront fee immediately; activating with 1 cell is rejected; an immediate double-tap queues the cancel instead of ending on the spot; stepping ~500ms of frames applies the queued cancel and floors the remaining energy down to a whole-cell boundary; total spend across the whole sequence was 3 whole cells (never fewer than the guaranteed 2).

---

## 2.128.1 — 2026-09-08 00:00: Batch 268 follow-up — FPS counter too faint

Direct correction right after shipping: too hard to spot. Nudged up/left (bottom/right 4px→16px, away from the very corner) and brightened (7px→8px, `rgba(180,180,180,0.45)`→`rgba(210,210,210,0.7)`) — still subtle, just no longer borderline invisible.

---

## 2.128.0 — 2026-09-08 00:00: Batch 268 — FPS counter

New Settings toggle: "FPS COUNTER" (off by default, persisted via `localStorage`, unlike the run-only Settings toggles above it since it's a display preference not a per-run config). When on, shows a live frames-per-second readout bottom-right of the game canvas, measured over a rolling ~500ms window in `loop()` (not per-frame, which would flicker unreadably). Kept deliberately unobtrusive per direct follow-up: 7px, faint grey (`rgba(180,180,180,0.45)`), no outline/shadow — barely visible unless you're looking for it.

Verified live: toggle flips the hidden `<select>`, persists across reload, and the element's computed style/display match. Real-frame FPS output not directly observable in this sandbox (its Browser pane permanently reports `document.hidden`, blocking real `requestAnimationFrame` callbacks — documented recurring limitation) — the counter logic itself is a direct rolling-average over `performance.now()`, the same measurement technique used everywhere else in web dev, hooked into the exact same `loop()` already driving every other real-time HUD element (score, speed, mult) that works correctly in production.

---

## 2.127.0 — 2026-09-08 00:00: Batch 267 — NPC crashes: no more burnt-black tint, real hit required in normal play

Two direct corrections after watching Batch 266's dev toggle in action:
1. **No burnt-black tint**: `.wrecked` (NPC-vs-NPC) no longer shares `.crushed` (player ram-kill)'s dark grayscale/blackened wreck skin — a fender-bender between two NPCs reads very differently from a violent player kill, so `drawCrushedWreck()` gained a `dark` param (defaults true, ram-kills unaffected) that `.wrecked` passes as false — real, undarkened car colors.
2. **Real contact required in normal play**: the crash trigger used a "same lane + Y-gap under a threshold" heuristic, which isn't fully accurate while one vehicle is still mid-glide between lanes. Normal play now requires an actual `checkCollision()` hitbox overlap — they genuinely have to hit each other. The dev-menu NPC CRASHES x10 toggle keeps its own deliberately-loose Y-gap-only proximity check (still not real contact, since that's the point — easy to trigger on demand for testing).

Verified live: a `.wrecked` vehicle's rendered pixel color matches its real undarkened body color (vs. a `.crushed` vehicle's dark grey); two same-lane vehicles with zero real hitbox overlap no longer crash in normal mode, while genuine overlap still does.

---

## 2.126.2 — 2026-09-08 00:00: Batch 266 — dev menu: NPC CRASHES x10 toggle

Direct request ("how can i see it in action... make it 10x more often") — Batch 265's NPC-vs-NPC crash is rare by design, hard to witness in normal play. Added a GAMEPLAY dev-menu toggle that loosens the crash-trigger proximity threshold from 0.85x to 6.0x combined half-heights while active — two same-lane vehicles crash from merely being somewhat close instead of needing genuinely tight convergence. Doesn't change anything about how the crash itself plays out (wreck visuals, still-collidable obstacle), only how easily it triggers.

Verified live: identical conditions (suicidal, 3 lanes, 3000 frames), 0 crash events with the toggle off vs. 6 with it on.

---

## 2.126.1 — 2026-09-08 00:00: Batch 265 — NPCs that converge in the same lane now crash into each other

Direct decision on the remaining NPC-overlap issue Batch 264 surfaced: option (b) from the user's own original fork — let them crash, don't just silently overlap. Added a pairwise same-lane proximity check (runs once per frame, after the main vehicle update pass) that marks both vehicles `.wrecked` the moment their gap crosses a real-crash threshold. `wrecked` is a sibling flag to the existing ram-kill `.crushed` — shares the exact same wreck rendering, lingering smoke, and "no more lane changes" treatment (`Vehicle.update()`/`draw()` now check `crushed || wrecked`) — but deliberately does NOT share `crushed`'s "harmless, non-collidable" exemption in the main collision guard, per direct request ("you can still crash into them maybe"): a `wrecked` vehicle stays a real, solid obstacle the player can still crash into or ram through, unlike a ram-created corpse. Ambulances are excluded from being wrecked this way.

Verified live: re-ran the same 20,000-frame stress test from Batch 264 — zero same-lane pairs now cross the actual crash threshold without being wrecked (previously reproduced reliably), and 2 real crash events fired during the run; separately confirmed driving into a `.wrecked` vehicle still ends the run normally, same as hitting any live traffic.

---

## 2.126.0 — 2026-09-08 00:00: Batch 264 — fixed one real cause of NPC-vs-NPC overlap (spawn clearance)

Direct bug report re-confirmed as still happening ("definitely happens - someone saw and told me"), investigated via a live stress test (suicidal, 20000 simulated frames, pairwise same-lane overlap check every frame) rather than guessing. Reproduced a real cause: `canSpawnAt()`'s lane-clearance check only measured the gap against the EXISTING vehicle's own height, never accounting for how tall the NEW vehicle about to spawn might turn out to be (its body isn't even picked yet at this point) — fine for two average cars, but two tall trucks back to back could end up closer than their combined half-heights require, especially on suicidal's much tighter 60px safety margin (barely more than one truck's own height, with zero margin reserved for the next spawn also being one). Added `SPAWN_HEIGHT_BUFFER`, a fixed conservative margin, to the check.

Verified live: the original repro (two trucks, both `changingState:'none'`, overlapping in the same lane) no longer reproduces after the fix. **However**, the same stress test surfaced a SEPARATE, more fundamental issue — see PLAN.md, this is bigger than a quick fix and needs a direction picked first.

---

## 2.125.4 — 2026-09-08 00:00: Batch 263 — inert TUTORIAL button added next to MISSIONS

Direct request: reserves the menu spot for the "HOW TO PLAY" onboarding idea in PLAN.md — same inert `.btn-disabled` placeholder pattern already used for DAILY GIFT/ACHIEVEMENTS, no click handler, `pointer-events:none`. Verified live.

---

## 2.125.3 — 2026-09-08 00:00: Batch 262 — level badge animation: slower, ease-in, scales with XP gained

Direct request: (1) slowed the animation down overall; (2) switched the per-segment curve from ease-OUT (fast start, slows into place) to ease-IN (`t*t` — starts slow, accelerates); (3) total duration now scales with how much XP was actually gained via `sqrt`, not linearly and not fixed — a big gain takes longer, but nowhere near proportionally longer, capped at 5s so an extreme multi-level-up still can't run forever.

Verified live (stubbed rAF, same technique as before — this pane can't wait out real animation frames): an 11x larger XP gain only took ~1.9x as long; at 10% of the elapsed animation time, only ~1% of the XP progress had happened, confirming the ease-in curve; final values land exactly correct in both cases.

---

## 2.125.2 — 2026-09-08 00:00: Batch 261 — level badge animation: fixed a real invisible-consumption bug

Direct bug report: "when i claim the missions i didn't see the animation." Root cause found via live instrumentation: claiming a mission (and, via the same shared function, claiming any Daily Gift/Word/Extra Box reward) already called `refreshMenuSummary()` unconditionally right after the claim, as a pre-existing "keep the Menu's cached badge fresh" pattern — that included painting the Menu's level badge even while Missions/Daily Gift was the screen actually visible, silently consuming Batch 259's pending animation snapshot before the player ever reached the Menu. The animation effectively played instantly in the background and was never seen.

Fixed by only painting the Menu badge inside `refreshMenuSummary()` when `menuView` is actually the active screen — every real "return to Menu" path already calls this function AFTER activating menuView, so the badge still repaints (animated, if a snapshot is still pending) the moment the player actually gets there; calls from other screens just skip the paint instead of wasting it.

Verified live for both trigger points: claiming an XP mission now leaves the snapshot intact while Missions stays open, consumed only on returning to Menu (confirmed the Menu badge's first frame shows the PRE-claim XP value, i.e. the animation's actual starting point); same confirmed for claiming a Daily Gift reward.

---

## 2.125.1 — 2026-09-08 00:00: Batch 260 — dev menu: reset/complete missions shortcuts

Direct request. Added to the DAILY GIFT / WORD group (renamed to include MISSIONS): RESET MISSIONS (forces `ensureMissionsToday()` to re-roll a fresh 6, same as a real day change), COMPLETE ONE MISSION (satisfies the goal for the first not-yet-done rolled mission), COMPLETE ALL MISSIONS (satisfies every not-yet-claimed rolled mission's goal). None of these auto-claim — the CLAIM button still needs pressing in the real Missions UI, same as normal play. Verified live: reset rolls exactly 6; complete-one satisfies exactly 1; complete-all satisfies all 6.

---

## 2.125.0 — 2026-09-08 00:00: Batch 259 — level badge counts up instead of snapping

Direct request, old PLAN.md item finally picked up: the level/XP badge (Menu/Garage/Stats, 3 instances of `paintLevelBadge()`) used to render straight to whatever `allTimeStats.playerLevel`/`playerXP` currently is, with no transition. Split the drawing into `paintLevelBadgeAt(...,level,xp)` (explicit values) and a thin `paintLevelBadge()` wrapper that detects a pending "before" snapshot (`levelBadgeAnimFrom`, set by `markLevelAnimStart()`) and animates through it instead of drawing instantly. `markLevelAnimStart()` is called at the 3 trigger points requested: `launchGame()` (covers "after a run" — mid-run XP already accumulates live via the existing `gainXP()` calls, so the snapshot has to be taken at the run's START, before any of that XP lands), the mission-claim button handler (XP-category only), and `rollReward()` (covers Daily Gift/Word/Extra Box, whichever tier it happens to roll). A multi-level-up gain animates through EVERY crossed level in sequence (each filling to full before rolling to the next), not just a jump to the final number, with total wall-clock time capped so a huge XP grant can't turn into an absurdly long animation. Only whichever badge instance renders first consumes the pending snapshot, so simultaneous badges don't all replay it.

Verified via a stubbed `requestAnimationFrame` (this sandboxed Browser pane permanently reports `document.hidden`, so real rAF never fires here to wait out) — confirmed the animation correctly visits every crossed level in order and lands exactly on the true final level/XP.

---

## 2.124.1 — 2026-09-08 00:00: Batch 258 — Daily Word stays green for the rest of the day + frame removed

Direct follow-up to Batch 257's once-per-day cap. Leaving and reopening the Daily Gift tab later the same day used to show the NEXT (rotated, not-yet-workable) word's blank progress track — new `allTimeStats.lastCompletedWord` records which word actually earned today's completion, and the Daily Word card now keeps showing IT in the green "WORD COMPLETE" state for the rest of the day instead. Also removed `.dg-word-panel`'s mint border/glow background per direct screenshot feedback ("remove this big frame") — same green tiles, no boxed frame around them.

Verified live: completed a word, dismissed the reveal, left the tab (clearing the transient claimed-flash state), reopened it — still shows "WORD COMPLETE" with the correct word's tiles, panel border/background both confirmed gone (0px / none).

---

## 2.124.0 — 2026-09-08 00:00: Batch 257 — Daily Word capped to one completion per real day

Direct bug report from 2026-09-06, re-confirmed today after finding the code had an explicit comment documenting multiple-per-day as intentional ("no reason to make a player wait a day") — user confirmed the cap is still wanted, reversing that earlier decision. `collectWordLetter()` now checks a new `allTimeStats.lastWordCompleteDayKey` before collecting anything at all; once today's one allowed completion has happened, further letter pickups are a no-op until the day rolls over. The on-road letter-spawn logic also now pauses once that cap is hit (same guard pattern already used for an unacknowledged `pendingWordReveal`), so letters for whatever word rotated to don't keep spawning and sitting pickable-but-inert on the road for the rest of the day.

Verified live: completing a word grants the reward and rotates as before; immediately trying to complete the newly-rotated word the same day is fully blocked (no reward, no second increment to `wordsCompleted`, word doesn't rotate again); simulating a day rollover correctly resumes normal completion.

---

## 2.123.3 — 2026-09-08 00:00: Batch 256 — BEST label nudged 2px higher

Direct correction, exact spec ("literally 2 pixels").

---

## 2.123.2 — 2026-09-08 00:00: Batch 255 — BEST label's dark background box removed

Direct correction: the repositioned BEST label (Batch 254) had a translucent dark background/padding meant to keep it readable over the chart, but it read as an unwanted boxed badge. Removed — plain text now, same as the AVERAGE readout it's meant to match.

---

## 2.123.1 — 2026-09-08 00:00: Batch 254 — stats chart follow-ups + pause volume sliders capped

Three direct corrections, screenshot-driven:
1. **BEST label repositioned**: moved off the fixed spot below the whole chart to sit right at the dashed line's own height, right-aligned inside the plot — tracks the line's `top` percentage every render instead of a static position.
2. **Hover tooltip reversed back to a floating box** (Batch 253 had moved it into the AVERAGE slot instead) — but no longer centered directly on the hovered point, which covered whatever it was showing. Now anchors to whichever side of the point has more room (right if the point's in the left half, left if it's in the right half) with a small pixel gap, and clamps the anchor percentage so it can't render off either edge of the plot.
3. **Pause screen volume sliders**: the "pause button" width cap from Batch 253 was meant to include the SOUND/AMBULANCE-SIREN slider rows too — their wrapper now caps at the same 340px as `.stat-box` and the buttons below them.

Verified live: hovering near the left edge anchors the tip left+16px, near the right edge anchors it right-16px; AVERAGE stays permanently on display (not hijacked by hover anymore); the BEST label sits inside the plot bounds at the line's own height; the volume-slider wrapper measures exactly 340px on a wide (10-lane) canvas.

---

## 2.123.0 — 2026-09-08 00:00: Batch 253 — quick UI batch from a large multi-part request

Six concrete, no-open-question fixes pulled out of a big multi-topic message (the rest — biomes, road texture, FPS counter, tank reload/barrel, jet bike sizing, car-mult rebalance, hours-played chart, boosters, secret cars, and the full achievements-system dump — logged into PLAN.md, several pending a direct answer first per the new "answer questions before implementing" rule):
- **CALM → SAFE**: difficulty button/option label renamed (internal value stays `calm`).
- **Missions dashed line removed**: the MISSIONS DONE/NEXT SET/CLEAN SWEEPS stat row's dashed top border is gone; Daily Gift's own STREAK/BEST/CLAIMED row (same shared CSS class) is untouched.
- **STATISTICS button added to Scores**: sits next to BACK in the Leaderboard screen, jumps straight to Stats.
- **Stats chart "best" marker redone**: the single yellow dot is now a full dashed line across the chart at that value, with the number itself called out at the bottom-right below the chart.
- **Stats chart hover tooltip finally fixed** (flagged repeatedly since 2026-09-06): the floating box that could cover the chart line is gone — hovering now repurposes the existing top-right AVERAGE readout to show the hovered run's key/date/value, reverting to AVERAGE on hover-end.
- **Pause screen button width**: `#pauseHudBtns` now caps at 340px, matching `.stat-box` above it, so RESUME/RESTART/QUIT can't render wider than the info box on a wide (high-lane-count) canvas.

Verified live: all six behaviors checked directly (DOM/state inspection), not just visually assumed.

---

## 2.122.2 — 2026-09-08 00:00: Batch 252 — Shield Bump ends on empty energy, not a free indefinite toggle

Direct correction: Batch 251 made ramming stay active forever once toggled on with NO ongoing cost — "it should end when no energy." Reworked to drain real energy continuously while active (`RAM_DRAIN_PER_FRAME`, same pattern Jump's own drain already uses), at the rate already implied by `SHIELD_BUMP_MS_PER_CELL` (1 cell per 500ms) — so it now ends itself the instant energy actually hits 0, same as Jump running dry. Activation no longer charges a flat upfront fee either (that's redundant once there's a real ongoing drain) — just needs ≥1 bar to start. A landed ram-kill's payoff reverts to a real energy refill (like Batch 222 originally had) rather than extending a now-nonexistent timer, which is what actually lets a connecting ram outlast the drain. Manual cancel (Batch 249) still works independently of all this.

Verified live: activating with 2 banked cells doesn't touch energy at the moment of activation, then the ability naturally ends after ~1016ms (2 × 500ms, matching the drain rate) with energy at exactly 0 and speed correctly restored; landing a ram kill while active bumps energy back up and keeps the ability running; pressing the ability key again still manually cancels it correctly.

---

## 2.122.1 — 2026-09-08 00:00: Batch 251 — Shield Bump no longer auto-ends — space to start, space to end, period

Direct correction: Batch 250's 100ms window was still a passive countdown that ended the ability on its own ("currently it is ending when no space pressed"), same underlying bug as before just with a much shorter fuse — the actual ask was a real toggle with no passive timer at all. Removed the countdown entirely for non-tank ramming; it now stays active indefinitely once activated, and the ONLY way it ends is the manual-cancel branch (Batch 250) firing when the ability key is pressed again. Tank's own shot window is untouched — it was never part of this request, it's a near-instant single action, not a sustained mode. Verified live: activated, ran 200 frames (~3.3s) with no further input — still ramming, speed still boosted, nothing decayed; pressing the ability key again still correctly cancels it (speed restored, guard retracts).

---

## 2.122.0 — 2026-09-08 00:00: Batch 250 — Shield Bump: manual cancel, faster hide animation, flat 1-bar cost

Direct request, three parts:
1. **Manual cancel**: pressing the ability again while already ramming (Shield Bump only — Tank's window is already a near-instant single shot) now ends it early instead of being a no-op — reverses a prior explicit "cannot be manually cancelled" spec. Reuses the exact same reversal the natural end-of-timer path already does (speed boost undone, guard plays its real retract animation).
2. **Hide animation length**: the guard's retract animation was 350ms, bumped to 500ms per direct spec — now also plays on manual cancel, not just a natural timeout.
3. **Anti-cheese activation rework**: activation used to drain the WHOLE energy reserve and run for however long that was worth — a big up-front investment bought a long, safe window. Now costs a flat 1 bar and opens an ultra-short 0.1s (100ms) window, barely enough to matter unless already lined up on a target. A real, longer ram now has to be earned hit by hit via the existing live duration-extension-per-kill mechanic (Batch 245/246: +0.5s per car, +1s per truck), not bought upfront in one press. The "ready" glow threshold for non-tank ram dropped from the shared 3-cell rule to match (1 bar).

Verified live: activating with 2 banked cells consumes exactly 1 (leaves 1), opens exactly a 100ms window, and boosts speed by the usual 40%; pressing again immediately cancels — speed exactly restored, guard enters `retract` and clears after ~516ms (~500ms target); activation gates correctly right at the 1-cell boundary (rejected a hair under, accepted a hair over).

## 2.121.1 — 2026-09-08 00:00: Batch 249 — car-tile name font bumped 9px → 10px

Direct feedback: Silkscreen's "C" and "O" read as nearly identical at 9px (e.g. "SCHOOL BUS"). Can't edit the webfont's own glyphs, and it's used throughout the rest of the UI so swapping fonts just for this one label would look inconsistent — bumped size slightly instead. Flagged in-code that this couldn't be visually confirmed in this environment; worth a look to see if it's enough or needs bold/a bigger jump instead.

---

## 2.121.0 — 2026-09-08 00:00: Batch 248 — NPC traffic no longer jiggles at real driving speed

Direct bug report ("cars on the road are jiggly, don't move smoothly") + design discussion. Root cause (found last batch): `drawScaledVehicle()` translates by each vehicle's raw, unrounded position every frame; since a vehicle's y advances by a non-integer amount every single frame, the resulting antialiasing shimmer changes frame to frame, reading as jitter. A past version of this code deliberately used raw (unrounded) positions specifically because flooring made slow-moving vehicles visibly hold still for 2-3 frames then jump — worse than the blur.

Direct follow-up confirmed judder from rounding is only ever visible at low relative speed — a genuinely fast vehicle already moves several pixels a frame, so snapping it to the nearest whole pixel can't cause visible holding, only crisper edges. Fixed with a threshold in `Vehicle.drawBody()`: at relative speed ≥1px/frame, snap the draw position to the nearest whole pixel (`Math.round`); below that (near-stationary traffic close to the player's own speed via `speedOffset`), leave it on the original raw path where judder was the actual risk. Doesn't touch `drawScaledVehicle()` itself or the Player (whose y barely moves during normal play, never the source of this complaint) — scoped to just the 3 NPC draw call sites.

Verified live: at relative speed 5 (fast), draw position snapped exactly to whole pixels (70.37→70, 100.62→101); at relative speed 0.16 (near-stationary), it stayed raw/fractional (70.37, 100.62), unchanged from before.

---

## 2.120.2 — 2026-09-08 00:00: Batch 247 — wreck smoke no longer drifts back onto screen after the wreck despawns

Direct bug report: smoke sometimes seemed to drift up from below the screen with nothing there. Root cause: a wreckSmoke wisp keeps a live reference to its wreck and re-reads its position every frame so it tracks a still-scrolling wreck — but the wreck vehicle despawns (removed from `vehicles`) the instant it crosses the bottom edge with zero tolerance, freezing its position, while the wisp's own slow upward drift term keeps subtracting from that frozen point regardless, and wreckSmoke's own off-screen expiry check has a ±20px leniency the freshly-despawned wreck is still well within — so instead of expiring, the wisp just kept drifting upward off its frozen anchor for its full remaining 2.5-4s lifetime, walking back into clearly visible territory with no wreck under it. Fixed by purging every wisp attached to a vehicle the instant that vehicle despawns. Verified live: forced a wreck to despawn with 2 attached wisps sitting well within the tolerance zone — both wisps were gone in the same frame the wreck was removed.

---

## 2.120.1 — 2026-09-08 00:00: Batch 246 — Shield Bump bar: fixed the "magically replenished" look + made ram-kill bumps actually visible

Two direct bug reports, same root cause. The ability bar's fill % while ramming was normalized against `sbActivationDuration` — a value ALWAYS set equal to `activeAbilityTime` at the instant of activation, so the bar read 100% ("fully replenished") the moment you pressed the button no matter how little real energy funded it ("even though the energy bar is not full it gets magically replenished") — a 3-cell partial activation looked exactly as full as a 9-cell one. It also explains why Batch 245's ram-kill refill "doesn't really feel like giving 1 energy bar": adding the same amount to both `activeAbilityTime` and `sbActivationDuration` barely moves their ratio.

Fixed by normalizing against the fixed full-bar reference (`SHIELD_BUMP_DURATION_MS`) instead of the per-activation `sbActivationDuration` (now fully removed — it had no other use anywhere in the file). A partial activation now honestly shows a partial bar, and a ram-kill visibly bumps the bar by one real cell's worth every time. Verified live: activating with 4/9 cells shows 44.4% (not 100%); ramming a car from there bumps it to ~55% (a ~10.7-11.1% gain, matching one cell, small variance from one frame's natural countdown).

---

## 2.120.0 — 2026-09-08 00:00: Batch 245 — Shield Bump: 0.5s/bar + live ram-kill duration extension

Direct spec: `SHIELD_BUMP_MS_PER_CELL` cut from 1500ms to 500ms — a full 9-cell bar now runs 4.5s instead of 13.5s. To compensate, ramming (Batch 222's energy-refill-instead-of-score payoff) now extends the CURRENT active window live in real time (`player.activeAbilityTime += cells * SHIELD_BUMP_MS_PER_CELL`) instead of only refilling the stored energy bar for a future activation — landing kills while already ramming keeps the ram going rather than banking energy that goes unused until the run ends. A normal vehicle gives 1 bar (500ms), a truck-like vehicle gives 2 (1000ms), same ratio `creditVehiclePass()` already uses elsewhere. `sbActivationDuration` (the reference the ability bar's fill % normalizes against) grows by the same amount on each refill so the bar can't read over 100% right after one. Verified live: activation lands at exactly 4500ms for a full bar; ramming a normal car nets +500ms, a truck +1000ms, both confirmed via `player.activeAbilityTime` before/after a real forced collision.

---

## 2.119.3 — 2026-09-08 00:00: Batch 244 — per-setting multiplier readouts: missing "x" added

Direct correction: text read "1.15 MULT", missing the "x" — now "1.15x MULT".

---

## 2.119.2 — 2026-09-08 00:00: Batch 243 — per-setting multiplier readouts moved to the control side + labeled

Direct correction: Batch 242's readouts sat in the row's LABEL half and floated in the middle of the row instead of next to the actual control. Moved them into a new `.stg-row-control` wrapper alongside the lane stepper / difficulty segmented buttons, so they now sit immediately to their left as one right-aligned group. Text changed from "1.15x" to "1.15 MULT" per direct spec. Verified live: both readouts' bounding rects sit fully left of their control's rect.

---

## 2.119.1 — 2026-09-08 00:00: Batch 242 — per-setting multiplier readouts next to ROAD LANES / DIFFICULTY

Direct request: the header's MULTIPLIER already showed the combined car×lane×mode total (confirmed unchanged from Batch 241), but there was no way to see each setting's OWN contribution without doing the division yourself. Added a small amber readout (`.stg-row-mult`) next to the ROAD LANES and DIFFICULTY row titles, both driven straight off `calculateMultiplier()`'s own `laneMult`/`modeMult` locals so they update live in lockstep with the header total and can never drift out of sync with it. Verified live: 3 lanes/suicidal shows laneMultVal 1.30x, modeMultVal 1.40x, header 2.37x (1.3 car × 1.4 × 1.3); 10 lanes/calm shows 1.00x/1.00x/1.30x.

---

## 2.119.0 — 2026-09-08 00:00: Batch 241 — score multiplier rebuilt as lane × mode × car (was all additive)

Direct instruction, following a multi-message design discussion on additive vs. multiplicative scoring: `calculateMultiplier()` used to sum a pile of flat bonuses onto a shared base (+0.3 always-accelerating, +vehicleMultiplierBonus, a lane if/else ladder, +0.2 trucks, -0.1 jump, +difficulty bonus). Rebuilt as three real multipliers — `carBaseMultiplier(car)` (already existed, already shown on the Garage hover card, reused as-is), `1 + DIFFICULTY_MULT_BONUS[difficulty]` (1.0/1.15/1.4x), and a brand-new `LANE_MULT` table — multiplied together (`baseMultiplier = carMult * modeMult * laneMult`). The old +0.2/-0.1 legacy flats (ghosts of removed toggles, not one of the three named factors) are gone entirely rather than folded in somewhere.

`LANE_MULT` was re-derived from scratch, not just the old additive curve converted in place — direct feedback confirmed the per-lane density/energy/rare-car-rate fixes already closed most of the real difficulty gap between low and high lane counts, so a flatter curve is correct now: `{3:1.30, 4:1.15, 5:1.10, 6:1.07, 7:1.05, 8:1.03, 9:1.01, 10:1.00}`.

The live in-run speed bonus also changed, per direct spec ("each 1km/h is (car_base_mult*mode_mult*lane_mult)*1%"): every km/h of actual speed above the run's starting point (`speedToKmh(baseSpeed)` is always exactly 50) now adds 1% of `baseMultiplier` itself — replacing the old ratio-of-fixed-max-speed formula (`SPEED_MULT_BONUS_RATIO`, removed, now dead). A harder base setup earns more per km/h gained, not the same flat ratio every run got regardless of difficulty.

Per direct instruction, nothing rounds the multiplier itself anymore (full float precision kept end to end) — only the final per-car score award still rounds, same as it always did (`Math.round(pts * multiplier)` at every score-crediting call site) — a fraction of a point is meaningless against 30+-point awards. Every multiplier readout (Settings screen, in-run HUD, Game Over, leaderboard, Garage hover card) now displays 2 decimal places instead of 1.

Verified live: `calculateMultiplier()` at 10 lane counts × calm/suicidal difficulty matches hand-computed products exactly (e.g. Stock/calm/10L = 1.30 = carBaseMultiplier(1.3) × 1.0 × 1.00; Stock/suicidal/4L = 2.093 = 1.3 × 1.4 × 1.15); the live speed bonus at run start (kmh=50) equals `baseMultiplier` exactly with zero bonus, and at top speed (kmh=200) equals `baseMultiplier × 2.5` exactly per the 1%-per-km/h formula.

---

## 2.118.3 — 2026-09-08 00:00: Batch 240 — START AT TOP SPEED: car no longer keeps accelerating past it

Direct follow-up: after Batch 239, the toggle started `currentSpeed` at the car's true rating but left `playerMaxSpeed` (the run's ramp ceiling) at the old floored value — so the car still visibly kept accelerating from its "top speed" up toward that separate, higher ceiling, which isn't what "start at top speed" means. While the toggle is on, `playerMaxSpeed` for that run is now set to the same true (unfloored) top speed too, so there's nothing left to ramp toward — the car starts already maxed out and stays there. Verified live: `currentSpeed === playerMaxSpeed` at launch (both 4.992 for Stock) and unchanged across 5 simulated frames.

---

## 2.118.2 — 2026-09-08 00:00: Batch 239 — START AT TOP SPEED now uses the car's real rated speed

Direct bug report: "the default car doesn't go 200km." The toggle was setting `currentSpeed` to `playerMaxSpeed`/`carMaxSpeedInternal()`, which floors EVERY car to at least the old universal 200 km/h ramp ceiling (a deliberate Batch 167 backward-compat floor for the run's ramp target, not the car's own rating) — Stock is actually rated 170 km/h (`estimateTopSpeedKmh`, the same number the Garage's own speed-tier badges use), so the toggle was starting it at a fictional 200 instead of its real, lower number. Added `carTrueTopSpeedInternal()` — same conversion, no floor — and switched the toggle to use it. Verified live: Stock now starts at `4.992` (its real 170 km/h) instead of the old `5.85` (200 km/h), while a genuinely fast car (Proto, 225 km/h) is unaffected since its real rating already exceeds the floor either way. The normal in-run ramp still climbs toward the real `playerMaxSpeed` ceiling afterward, unchanged.

---

## 2.118.1 — 2026-09-08 00:00: Batch 238 — dev menu group colors brightened

Direct request: the 5 group background tints were too subtle (.08 background/.35 border alpha). Bumped to .22/.6.

---

## 2.118.0 — 2026-09-08 00:00: Batch 237 — dev menu grouped into sections + 2 new shortcuts

Direct request: the dev menu had grown into a dozen+ buttons in one flat ungrouped stack. Split into 5 labeled, background-tinted sections (ECONOMY, CARS & COLORS, GAMEPLAY, DAILY GIFT / WORD, DANGER ZONE — CLOSE stays outside all of them at the bottom) instead of building a full tabbed UI for what's still a flat debug menu underneath. `#devMenuBox` also gained `max-height:90vh; overflow-y:auto` as a safety net now that it's taller. Two new shortcuts, also requested: **UNDISCOVER ALL CARS** (CARS & COLORS) clears `discoveredCars`/`newlySpottedCars` — the reverse of the existing DISCOVER ALL CARS, for testing the "???" mystery tile and the crate-locked tile without a fresh save; **START AT TOP SPEED** (GAMEPLAY, on/off toggle like INVINCIBLE) makes `launchGame()` start `currentSpeed` at the car's real `playerMaxSpeed` instead of `baseSpeed`. Verified live: all 5 group labels render, both new controls flip their own state/label correctly, and a real `launchGame()` call starts at the exact top speed with the toggle on vs. the normal base speed with it off.

---

## 2.117.5 — 2026-09-08 00:00: Batch 236 — crate-locked tile: hover tooltip removed

Direct request: removed the "A mystery Daily Word reward" hover title — clicking the tile already opens a dialog saying the same thing, no separate tooltip needed on top of it.

---

## 2.117.4 — 2026-09-08 00:00: Batch 235 — crate-locked tile: one frame, not two

Direct correction after misreading the same complaint twice: the striped box's own border plus `.car-tile`'s padding/border was rendering as a visible double frame — an inset bordered rectangle sitting inside the tile's own bordered edge. Zeroed `.car-tile-crate-locked`'s padding and removed the inner box's border entirely; the tile's existing outer border is now the only border on this tile, and the striped background fills it edge to edge. Verified live: inner box border-width 0px, tile padding 0px, box fills 181×136 of a 185×140 tile (the only gap being the tile's own 2px border).

---

## 2.117.3 — 2026-09-08 00:00: Batch 234 — crate-locked tile recolored to match the real Garage palette

Direct clarification/follow-up: the striped shutter box was already framed by `.car-tile`'s own border/padding (confirmed live: 8px gap on every side, not full-bleed) — the actual mismatch was color. The doc's own colors (`#101520` background, near-black `rgba(9,12,18,...)` stripes) came straight from its standalone mockup, noticeably darker than this game's actual Garage tokens. Swapped the box to `var(--c-card)`/`var(--c-card-border)` (the same variables every other car tile already uses) and lightened the stripe overlay to a panel-toned `rgba(23,28,39,...)` at lower opacity, so the tile now reads as part of the same UI instead of an imported darker box.

---

## 2.117.2 — 2026-09-08 00:00: Batch 233 — crate icon de-nested; Garage scrollbar no longer overlaps cards

Two direct corrections. (1) "whole box, not a box in a box": the crate-locked tile's small bordered icon chip nested inside the bigger bordered tile read as two stacked boxes — removed that inner wrapper entirely, the crate SVG now sits directly on the shutter background at a bigger size (22px → 40px) to fill the space it leaves. (2) The Garage's themed scrollbar (`.garage-scroll`, 10px wide) sat flush against the grid with no gap, so its thumb visually overlaid the third column's cards — added `padding-right: 10px` to open real separation between them.

---

## 2.117.1 — 2026-09-08 00:00: Batch 232 — crate-locked tile simplified to just the icon; dialog text corrected

Direct follow-up, screenshot-driven: Batch 231's crate-locked tile still drew the car's silhouette sprite behind the shutter and a "???"/"BOX ONLY" caption below it — the actual ask was the doc's icon art alone, nothing else, since this car was never discovered and there's nothing to show through the slats or caption to add. Removed the sprite canvas and both text spans entirely; the tile is now just one bordered box (`.car-tile-crate-locked-box`, `flex:1` so it fills the whole card like the reference image) with the shutter+crate icon centered in it. Also fixed the click dialog's wording — it said "found in Extra Boxes," corrected to "found as a Daily Word reward" per direct correction.

---

## 2.117.0 — 2026-09-08 00:00: Batch 231 — box-exclusive cars: no road spawn, real crate-locked tile, no discovery needed

Direct request, using the uploaded "Locked Car Icons.dc.html" design doc's "1c" (SHUTTER) treatment: box-exclusive (`boxOnly`) cars used to spawn as normal NPC traffic like anything else, so a player could eventually spot one on the road and "discover" it (real name/sprite/rarity revealed in the Garage) despite it only being winnable from an Extra Box — defeating the point of it being a surprise. Three changes:
- `GARAGE_NPC_RARITY` (drives road-spawn odds) now excludes `boxOnly` cars entirely — they never spawn as traffic, so they can never be spotted/discovered that way again.
- `rollReward()`'s `discoveredOnly` gate (Batch 230, used by Extra Box purchases) now exempts `boxOnly` cars from needing to be "discovered" first — since they can no longer ever become discovered via the road, requiring it would have made them permanently unobtainable from the very feature that's supposed to grant them.
- The Garage grid's not-owned box-exclusive tile is a new dedicated "crate-locked" treatment (`buildCarTile()`) instead of either the old real-sprite-plus-"BOX ONLY"-label tile (which leaked the name/rarity once discovered) or the plain generic "???" mystery tile: sprite drawn as a flat silhouette, blocked by shutter slats with a centered crate padlock — ported directly from the doc's colors/sizes. Shows "???" for the name, no rarity badge, a "BOX ONLY" source hint, and a click dialog that doesn't reveal which car it is. Once actually won, the tile reverts to fully normal (real name/sprite/rarity) — nothing changes for an owned box car.

Verified live: a not-owned box car renders the crate-locked tile (name shows "???", real label never appears in the tile's text) and the SAME car once owned renders completely normally; a box-only car with zero road-discovery still turned up from 2000 simulated Extra Box rolls; `GARAGE_NPC_RARITY` no longer contains any of the 13 `boxOnly` car keys.

---

## 2.116.0 — 2026-09-08 00:00: Batch 230 — Extra Boxes can no longer award an undiscovered car

Direct request: "you cant get from the boxes cars that you havent discovered." `rollReward()`'s car tier picked from ALL non-stock Garage cars regardless of whether the player had ever actually spotted that car as NPC traffic (`isCarDiscovered()`) — fine for a natural Daily Word completion, where finding a car for the first time through the reward is itself part of how discovery works, but not appropriate for Extra Boxes, a paid bonus roll that shouldn't be able to hand over a car the player has literally never seen in the game. Added an opt-in `discoveredOnly` param to `rollReward()`, restricting its car pool to `isCarDiscovered()` cars only when true (falls back to the full pool if nothing's been discovered yet, so it can never return literally no reward); `buyExtraBox()` now passes it, the natural Daily Word completion path does not. Verified live: forced a 3-car "discovered" set with nothing owned, rolled 400 Extra-Box rewards, 39 landed on the car tier and all 39 were within the discovered set (0 violations) — then re-ran the same setup through the natural (non-box) path and confirmed it can still roll an undiscovered car, unaffected.

---

## 2.115.5 — 2026-09-08 00:00: Batch 229 — Extra Box purchase: header coin total now updates immediately

Direct bug report: "coins dont sync when buying extra boxes." `buyExtraBox()` itself correctly deducted and saved `allTimeStats.totalCoins`, but the buy button's click handler only called `renderDgGiftCard()`/`renderDgWordCard()` — never `renderDailyGiftHeader()`, the actual function that redraws the header's coin number. Its own comment claimed the header "may have changed" but nothing there actually re-rendered it, so the header stayed stale until the tab was closed and reopened. Added the missing call. Verified live: bought a box with a forced 100,000-coin balance, header went 100,000 → 97,500 in the same click, matching the real deducted total.

---

## 2.115.4 — 2026-09-08 00:00: Batch 228 — "GIFT OPENED" kicker removed from coin/XP reveals

Direct request: removed the "GIFT OPENED" header text from the plain (non-duplicate) coin and XP reward reveals — the icon/amount below it already says what happened. Left the color ("NEW PAINT UNLOCKED") and car ("NEW CAR UNLOCKED") reveal kickers untouched — those weren't the ones flagged, and unlike "GIFT OPENED" they actually describe something the amount/icon alone wouldn't.

---

## 2.115.3 — 2026-09-08 00:00: Batch 227 — duplicate-reveal strike line direction fixed (was backwards)

Direct correction: Batch 226's diagonal line ran the wrong way — a CSS gradient's colored band sits PERPENDICULAR to the direction it's named after, so `linear-gradient(to bottom right, ...)` actually drew a top-right-to-bottom-left line, the opposite of what was asked. Verified the mixup with a pixel-level test (rendered the identical gradient math on a canvas and sampled corner pixels) before touching anything, then fixed by flipping the keyword to `to top right` — re-verified the same way: the red band now samples solid at the top-left AND bottom-right corners, transparent at the other two, confirmed again in the live DOM afterward.

## 2.115.2 — 2026-09-08 00:00: Batch 226 — duplicate-reveal strike line now diagonal

Direct request: the crossed-out line on a duplicate color/car preview was horizontal; changed to a proper diagonal via a `linear-gradient(...)` on `.dg-dupe-original::after` instead of a fixed horizontal bar — this follows the box's real diagonal regardless of its width/height, so it works the same for both the short color-chip preview and the taller car-sprite preview without needing a per-shape angle. (Direction corrected in 2.115.3 above.)

---

## 2.115.1 — 2026-09-08 00:00: Batch 225 — duplicate-car preview: bigger sprite, rarity/name moved beside it

Direct request, screenshot-driven: the duplicate-car crossed-out preview (Daily Word/Extra Boxes) had the sprite, rarity badge, and name all in one cramped row. Sprite kept its existing upright/facing orientation (no change asked there) but grew (`drawCarSpriteUpright` max size 20×24 → 40×48), and the rarity badge + name moved into a new `.dg-dupe-car-info` column to the sprite's right (rarity on top, name below) instead of trailing it on the same line.

---

## 2.115.0 — 2026-09-08 00:00: Batch 224 — Daily Gift reward no longer lost by leaving the tab unacknowledged

Direct bug report: "when i didnt claim my reward from daily gift it still gets cancelled after quitting the tab." Root cause: the CLAIM GIFT reward rolls and is granted (coins/XP/color/car all applied and saved) the instant the button is clicked, but the reveal screen showing WHAT was won only ever lived in a transient `dgGiftReveal` variable — its own comment even said so ("the CLAIM GIFT button flow only ever happens while this tab is open, no need to persist it"). Leaving the tab before dismissing that reveal (its own "CLAIM" button is really just an acknowledge/close action) wiped it unconditionally, so returning later just showed the plain "NEXT GIFT IN" countdown with no trace anything had happened — reading exactly like the reward got cancelled, even though it hadn't. Fixed by persisting the reveal itself: new `allTimeStats.pendingGiftReveal` (same pattern the Daily WORD reveal already used for this exact reason, `pendingWordReveal`) is set the moment a reward rolls and only cleared once its reveal is actually dismissed — leaving the tab, or genuinely quitting/reloading the page, no longer loses it. The main-menu claim-badge (`updateDailyGiftClaimBadge()`) now also lights up for an unacknowledged gift reveal, matching what it already did for an unacknowledged Daily Word.

Verified live: claimed a gift, left the reveal undismissed, did a full page reload (closer to an actual tab-quit than just navigating within the app) — the reveal was still there, unchanged, on reopening the Daily Gift tab, and the main-menu badge was already lit before even opening it.

**Known, not fixed here**: Extra Box purchases (`dgBoxReveal`) use the exact same transient-variable pattern and likely have the identical bug — not reported, left alone for now.

---

## 2.114.1 — 2026-09-08 00:00: Batch 223 — duplicate-paint preview: square swatch + "PAINT" label

Direct follow-up, screenshot-driven: the duplicate-color crossed-out preview's swatch was a rectangle (`.dg-dupe-chip`, 20×11px, leftover from being visually paired with text on one line) and its label was just the bare color name ("PINK"). Swatch is now a square (16×16 native, matching a paint swatch's usual shape elsewhere in the game) and the label reads "PINK PAINT" (`dupe.name.toUpperCase()} PAINT`) instead of the bare name.

---

## 2.114.0 — 2026-09-08 00:00: Batch 222 — ability score rebalance + duplicate-reveal icons + Daily Word badge removed

### Ram gives energy instead of score; Tank shooting scores double
Direct design discussion: ramming (Shield Bump) and shooting (Tank) shared one flat 15-point reward regardless of ability or target, even though the two abilities cost very differently to use (a ram drains a full energy bar to activate; a Tank shot costs a flat 3 cells, `TANK_SHOT_COST`, and can fire repeatedly). Changed both places a rammed/shot vehicle pays out (the on-touch collision branch and, for Tank, the separate instant ranged-shot branch fired on activation): ramming (non-Tank cars) no longer adds score at all — it now refills 1 energy bar (`1 * ENERGY_PER_CELL`) per kill instead, framing it as a sustain tool rather than a score source; Tank shooting keeps scoring, doubled from 15 to 30 base points, staying the higher-cost/higher-reward pick. XP-per-kill (15) is unchanged for ramming; Tank's XP-per-kill was doubled to 30 alongside its score, matching the score change. Verified live: forced an in-game ram collision (non-Tank) and confirmed score stayed flat while energy jumped by exactly 1 cell; forced both Tank destroy paths (ranged instant-shot and on-touch) and confirmed each now awards 60 score at a 2x lane multiplier (30 base × 2), versus 30 before this change.

### Duplicate-compensation reveal: coin icon + car sprite
Direct follow-up to Batch 221's crossed-out duplicate-reward redesign: the compensation payout now shows the real coin icon next to the amount (reusing `renderCoinIcon()`), and a duplicate CAR's crossed-out preview now shows the car's actual small sprite (`drawCarSpriteUpright()`, scaled to fit) next to its rarity badge and name, instead of text-only. Both painted in `paintRewardRevealCanvases()` alongside the existing car-reveal canvas pass, since canvas contents can't be set via the `innerHTML` string the rest of the reveal is built from.

### Daily Word header "SOLVED" badge removed
Direct request. Removed from both places it showed (word freshly completed, and the post-claim acknowledgement flash) — the "WORD COMPLETE" kicker already shown in the card body says the same thing, so the header badge was pure duplication. Removed the now-unused `.dg-badge-ready`/`.dg-badge-claimed` CSS and the `dgBlink` keyframe animation that only `.dg-badge-ready` used; left `.dg-badge`/`.dg-badge-sealed`/`.dg-badge-opened` alone since those were already unused before this change, not something this change orphaned.

---

## 2.113.0 — 2026-09-08 00:00: Batch 221 — Daily Gift day-rollover fix + duplicate-reward reveal redesign

### Daily Gift card no longer goes stale across midnight
Direct bug reports: "when in daily gift tab when the midnight passes and it resets it shows as already completed" and a separate report of opening the tab, not claiming, leaving, coming back to find it showing completed with no way to claim and no XP gained. Root cause: `startDgCountdown()`'s 1-second tick only ever updated the countdown *text* — nothing re-evaluated `dailyGiftState()` or re-rendered the card, so a tab left open across a real midnight rollover kept showing yesterday's stale view, including a "CLAIM" button that looked live but silently no-op'd on click (`claimDailyGift()` correctly re-checked the real date and found it no longer matched). Fixed by having the countdown tick also compare the current day key against the day key it saw when it last rendered — the instant they differ, it triggers a full `renderDailyGiftView()` instead of just updating the countdown text. Verified live: forced a simulated day-rollover mid-tick and confirmed the card actually flips from CLAIMED to LOCKED within one tick, with no stale button left behind.

### Duplicate-compensation reveal (Daily Word) redesigned
Direct request: when a Daily Word reward is a duplicate color/car paid out as coins instead, show the original reward crossed out with one red line, with the actual coin payout shown below it at a smaller size so both fit. `rollReward()`'s `wasDuplicateOf` field now carries the original reward's display info (`{type:'color',name,color}` or `{type:'car',label,rarity}`) instead of just a name string. `renderRewardReveal()` gained a duplicate-specific branch: a small crossed-out preview (new `dupeOriginalPreviewHTML()`, red strike-line via `.dg-dupe-original::after`) followed by the coin payout at a reduced 28px (`.dg-dupe-comp-amt`) instead of the normal 44px. Replaced the old plain-text `.dg-reveal-note` ("Already had X — paid out instead"), now unused and removed.

---

## 2.17.0 — 2026-08-25 00:00: Batch 75 — crash sequence refinements from real feedback

Follow-up after actually seeing Batch 74's crash sequence run. Three changes, all from direct feedback.

### Newspaper replaced with a single stamped word
"It isn't like a newspaper anymore, just a piece of information like 'you crashed'... give it a couple different words." Removed `NEWSPAPER_HEADLINES` (10 headline/body templates) and `buildNewspaper()` entirely, along with the typewriter reveal and `#newspaper`/`.np-masthead`/`.np-headline`/`.np-body` DOM/CSS. Replaced with `CRASH_WORDS` (`WRECKED`, `CRUSHED`, `TOTALED`, `SMASHED`, `MANGLED`, `DEMOLISHED`, `FLATTENED`) — one picked at random in `startCrashSequence()`, shown via a new `#crashWord`/`#crashWordText` stamped-label element (rotated, bordered, fades/scales in) instead of the old newspaper clipping.

### Responder system rebuilt: real positioning bug, not just a tuning tweak
Direct feedback: ambulance always drove onto the wreck, lights were an oversized field, and the user wanted 2 police (first) + 1 ambulance (last), staggered rather than simultaneous, with more time before they arrive.

- **Count/order**: now 2 police + 1 ambulance (was 1 each), staggered via a per-responder `delay` (frames since the 'arrive' phase starts before it begins moving) — police at `delay=0/25`, ambulance at `delay=55`.
- **Positioning, and the actual bug found during testing**: the first pass parked responders at fixed offsets (`wreckY±55/100`) from the wreck. Live-testing surfaced that the game's canvas is only `CANVAS_HEIGHT` (260px) tall and the player's legal Y range is 40–228 — a crash near either end of that range pushed those fixed offsets clean off the canvas (e.g. a crash at y=228 sent a responder to y=328, never visible; this is very likely the actual mechanism behind "always drives onto the wreck" too — it wasn't the wreck exactly, it was the responder ending up somewhere nonsensical relative to it). Replaced with room-aware stacking: at `csEnterPhase('arrive')`, compute room above vs. below the wreck, stack all 3 responders on whichever side has more of it, and have them enter from (and travel from) that same side — never the opposite edge, or they'd visually cross through the wreck to get there. Total stack reach (87px) is provably safe: the two sides of the legal Y range always sum to ≥229px, so the larger one has ≥114px. `csUpdate()`'s per-frame deceleration changed from a one-directional "gap" (`r.y - r.targetY`, only ever counted down) to a signed `Math.sign(diff)` step so it works approaching from either side.
- **Light-bar spill shrunk**: from a 34×22px rect at 0.16 alpha down to 14×6px at 0.12 alpha — the "very big field" from feedback.
- **More time before/during arrival**: `arrive` phase 120→160 frames, `beat` phase 60→110 frames (~0.8s more each at 60fps).

Considered scrapping the responder system for something simpler per the user's own "maybe I'm overthinking it" — recommended keeping it: the reported issues were concrete, fixable positioning/timing bugs (confirmed above — a real off-canvas bug, not a design dead-end) rather than a broken concept.

**Verification**: live-tested in the Browser pane via `endRun()` (not a lower-level call, so `CS.result`/`CS.snapshot` are populated realistically) — confirmed no `ReferenceError` on `CRASH_WORDS`; confirmed a full phase cycle (`flash→hold→sirens→arrive→beat→resume`) completes with no errors and the correct transition frames; confirmed responder targets stay within canvas bounds at all three extremes of the legal player-Y range (40, 134, 228) and that the stack direction (`above`/`below`) picks correctly at each; confirmed staggered `delay` gating — a responder doesn't move before `elapsed >= delay`; confirmed `csDraw()` runs 460 frames with no errors; confirmed `skipCrashSequence()` still cuts straight to the result screen with no errors. Grepped for zero remaining references to `newspaperEl`/`npHeadlineEl`/`npBodyEl`/`buildNewspaper`/`NEWSPAPER_HEADLINES`/`CS.paper`. Visual appearance (word stamp look, light-bar size, responder spacing as actually rendered) still unverified — Browser pane screenshots aren't compositing this session, same known limitation as Batch 74.

---

## 2.18.0 — 2026-08-25 01:15: Batch 77 — player level widget + nitro/score-boost road pickups

Applied from a design doc (`Canvas-2.dc.html`) plus direct instruction: a persistent player-level system and the game's first two road pickups.

### Player level widget
Top-right HUD, a ring (colored by tier) with the level number inside, plus a one-line XP readout (`837/1550`) — the design doc's own mockup had this stacked across three lines (an "XP" label, then the number, then "/total" on separate lines); collapsed to one, per direct feedback. Score earned during a run doubles as XP (`gainXP()`, called at both existing `baseScore` increment sites — dodge and ram), persisted in `allTimeStats.playerLevel`/`playerXP` (XP within the CURRENT level only, not a lifetime total, matching the design doc: "the ring fills against the current level's requirement, not a lifetime total"). Curve is `req(L) = 1000 + (L-1)*50`, exactly as speced. Color changes every 10 levels across a 10-tier "legendary" palette (Iron → Bronze → Silver → Gold → Emerald → Sapphire → Ruby → Amethyst → Platinum → Diamond), capping at Diamond for level 91+ rather than cycling back down — climbing back to Bronze past level 100 would read as a downgrade, not progression. Several tier colors reuse existing accent hexes already in the game (Gold = the amber accent, Emerald = the mint accent, Sapphire = the responder-light blue, Amethyst = the Garage's Purple paint) rather than inventing a parallel palette.

### Nitro + score-boost pickups
Ported the design doc's pixel-art sprites (bolt-capsule capsule shell, upgrade-arrow circle) directly — same patterns/colors, adapted to draw at an arbitrary (x,y) instead of always the canvas origin. Both spawn on their OWN independent random countdown (`rollPickupSpawnDelay()`, an 18-42s spread averaging ~30s) — not a shared fixed clock, per direct feedback ("kind of random, each has its own different timer"). Effects: nitro adds a flat, reversible `+1.5×CAR_SCALE` to `currentSpeed` for ~3s (the natural per-frame ramp keeps running underneath, untouched); score boost multiplies score gains ×2 for ~8s at the same two sites `gainXP()` was added to (XP itself is NOT affected by the boost — stays tied to raw points, like `baseScore`). Both durations/values match the design doc's own mockup numbers (3.1s / 8s / ×2). Each has its own active-effect HUD chip (icon + drain bar + countdown) below the pause button, hidden until that effect is running.

### Real bug caught during testing: a chip could get stuck "on" after a mid-effect crash
`endRun()` was clearing the chip's `.show` CSS class directly, but not the underlying `nitroTimer`/`scoreBoostTimer` themselves. The collision that triggers `endRun()` fires partway through a frame that's already inside the main `gameActive` block — `updatePickupChips()` still runs later in that SAME frame, reads the still-nonzero timer, and re-adds `.show` right after `endRun()` had just removed it. Fixed by zeroing the timers in `endRun()`, not just the DOM class — the class removal is now redundant-but-harmless belt-and-suspenders, the timer reset is what actually matters.

**Verification**: live-tested in the Browser pane — confirmed level-up math including a single `gainXP()` call large enough to cross 3 level boundaries at once, landing with the correct leftover XP; confirmed all 10 tier-color boundaries (1, 10, 11, 20, 21, 90, 91, 100, 101, 500, 1000); confirmed allTimeStats.playerLevel/playerXP survive a `launchGame()` reset (persistent) while pickup/run-scoped state does not; confirmed nitro's speed boost applies once, doesn't double-add on a second pickup collected while already active, and reverses to exactly the pre-boost trajectory on expiry; confirmed the chip-freeze bug was real (reproduced it, then confirmed gone after the fix) via a forced mid-effect `endRun()` call; confirmed pickups fold into `allTimeStats.totalPickups` correctly at run end (a stat field that already existed, reserved for this); confirmed both sprites render non-blank pixel data with no errors; ran a 2000-frame simulated playthrough with pickups force-collected periodically and a natural ~4000-frame run relying on the real spawn timers, both with zero console errors; confirmed `getBoundingClientRect()` layout checks show no overflow past the canvas edge for either the level widget or the pickup chips. **Not verified**: actual visual appearance of any of it (ring look, chip sizing/placement, sprite readability at 16px) — Browser pane screenshots still aren't compositing this session.

---

## 2.112.0 — 2026-09-07 02:20: Batch 220 — extra-box claim buttons no longer jiggle, lingering smoke actually disappears, tank blur fixed everywhere

Three direct reports, all confirmed and root-caused before fixing.

**"All claim buttons are jiggling (like I clicked them all)" when buying an Extra Box.** Real cause: `.dg-reveal`'s pop-in animation was unconditional in CSS, and buying a box calls `renderDgGiftCard()`+`renderDgWordCard()`, which rebuild each card's ENTIRE innerHTML — including any unrelated reveal already on screen (e.g. a pending Daily Word claim). A freshly-recreated DOM node always replays its CSS animation from the start regardless of whether its content changed, so every visible reveal "popped" at once, not just the one just bought. Moved the animation to an opt-in `.dg-pop-in` class, applied only the first time a given reward object is ever rendered (a `_animated` flag mutated directly onto the reward, which persists across re-renders since the object itself isn't recreated, only its DOM). Verified directly: a pre-existing word reveal no longer replays on a box purchase, while the newly-bought box reveal still gets its own pop-in.

**Lingering smoke sometimes not disappearing off-screen.** Once its host vehicle scrolls past the bottom edge, the main loop splices it out of `vehicles` and stops updating it — so a smoke wisp's stored `vehicle` reference freezes at wherever it was removed. That's normally harmless, but the wisp's own slow upward drift could still carry its rendered position back into the visible area from a frozen off-screen anchor, reading as smoke lingering with no wreck under it. Both `wreckSmoke` and `sbExplosions` now also expire immediately once their own rendered position drifts outside the canvas, regardless of their normal lifetime timer.

**Tank sprites blurred in the Garage hover-card/tile preview.** Traced to the Garage tile grid showing every car rotated 90° (`drawSideways()`, a real `ctx.rotate()`) to fit its tile — which tripped this function's own rotation-detection fallback (added defensively in Batch 209) back to the old direct-scaled render, reintroducing the exact fractional-pixel antialiasing blur Batches 206/207 had already fixed for gameplay, just never extended to this rotated context. Rewrote the whole function to not need that fallback (or Batch 207's manual rounded-destination-rect math) at all: it now draws the crisp native buffer at local sprite coordinates and lets whatever transform the caller already has active — translate/scale for gameplay, or the tile grid's rotation — position it, exactly like every `fillRect` inside `drawGarageTankArt53` already relies on. `imageSmoothingEnabled = false` keeps it crisp either way. Verified: the rotated tile-grid render now produces the exact same clean 19-color, 594-opaque-pixel output as the non-rotated gameplay case (previously blurred), and the gameplay centering regression suite (Batch 207/209) still passes unchanged.

Full regression across cars/lanes and Garage/Daily Gift screen navigation, no errors.

## 2.111.0 — 2026-09-07 01:45: Batch 219 — wreck smoke overhaul, shot cost raised, result-screen resize + relabeling

Several direct requests in one message, all verified in-browser before shipping.

**Wreck smoke now actually lingers and stays on top.** The old smoke used the generic `Particle` class — random ±1px/frame drift, no connection to the wreck at all, and a ~0.2-0.55s lifetime — so within a fraction of a second it had already faded or drifted off, long before the player could plausibly drive back near it. Replaced with a dedicated `wreckSmoke` array that anchors each wisp to its vehicle (a stored reference + fixed relative offset, re-read every frame — the same tracking technique Batch 218 used for the explosion) for a real 2.5-4s lifetime, with spawn chance lowered proportionally so the steady-state particle count doesn't balloon just because each wisp now lives ~10x longer. Also fixed the z-order bug behind "the car is going under the smoke": both the wreck smoke and the impact-explosion draw calls used to run *before* `player.draw()`, so the player's own car painted over them whenever it scrolled near a wreck — confirmed this applied to both the tank shot and plain ramming (they share one `explodeShieldBump()`/particle pipeline). Both now draw strictly after the player. Verified: a wisp survives 20 real frames while its host vehicle moves 31px, staying attached the whole time.

**Tank shot cost raised 2→3 energy bars**, direct follow-up now that the shot is instant, longer-ranged, and reliable (Batch 217/218) — a cheaper cost no longer matched how much stronger the ability had become. Verified: exactly 2 bars is rejected, exactly 3 fires.

**Result-screen box and buttons resized**, per a screenshot with reference lines drawn directly on it: `.stat-box` and `#gameoverBtns` were `width:100%` of the canvas-container, which stretches very wide at high lane counts (a wide canvas relative to its height) — capped both to `max-width:340px`, the same base width every other screen (Garage/Stats/etc.) already uses, so they stay a comfortable, readable size regardless of canvas width.

**Result-screen ability row relabeled and recolored**: "CARS JUMPED OVER"/"RAMMED" → "VEHICLES JUMPED OVER"/"VEHICLES RAMMED", plus a new Tank-specific "VEHICLES SHOOT" (it shoots, it doesn't physically ram) — added a `selectedCarKey` snapshot field so the result screen can tell Tank apart from the other 8 ram cars. The count value itself now renders in red (new `.stat-red`, matching the WRECKED title) instead of plain white. Verified all three label variants and the red color resolve correctly.

**Also caught mid-turn, unrelated**: the page's `<title>` read "Reckless Driving CAPTCHA" for no evident reason — renamed to "Highway Reckless Driving".

Full regression across 5 cars × 200 frames of repeated activation each (devInvincible), no errors.

## 2.110.0 — 2026-09-07 01:10: Batch 218 — tank shot range/timing, explosion tracking the wreck, energy-threshold precision, and a stray page title

Four direct reports in one message, plus a fifth caught mid-turn.

**(1) "the tank can't shoot even though it has 2 energy bars"**: `TANK_SHOT_COST` (`2 × 100/9`) is a repeating binary fraction, the same class of float-precision issue already fixed once for this bar's own display (Batch 196's `+1e-6` epsilon on the lit-cell count). That display epsilon was never applied to the actual gate (`this.energy >= TANK_SHOT_COST`) or the "ready" glow threshold, so accumulated float drift from a different credit path could leave `this.energy` a hair under the exact threshold while the bar still visually rounds up to showing 2 full cells. Added the same epsilon to both checks so they can never disagree with what the bar displays. (Couldn't construct a simple repro sequence that reliably reproduces the exact drift, so flagging this as a well-justified precision fix rather than a confirmed-reproduced bug — if shooting still silently fails with a visually-full bar after this, the `abilityState !== 'idle'` cooldown from a very recent prior shot, still fresh from Batch 217's window, is the next thing to check.)

**(2) "why it doesn't destroy cars that are far enough, make the shoot frames longer so it reaches further cars"**: `TANK_TRACER_MAX_RANGE_PX` raised 140→230 (~54%→~88% of the 260px canvas height) — both the shot's actual destroy range (`findTankShotTarget()`) and the tracer beam's max visual length share this one constant, so they move together. The tracer's own frame timing was slowed 40ms→55ms/frame (240ms→330ms total) to match — a beam reaching this much further read as too abrupt at the old flash speed. Verified: a car 200px away (out of the old 140px range) is now destroyed on activation.

**(3) "when there is a smoke/explosion effect it should stay on top of the corpse, not move with the road — check if it's also happening with ramming"**: confirmed it affects both — `explodeShieldBump()` used to take a plain x/y snapshot of the target's position at the moment of the hit and never update it, while the crushed wreck keeps scrolling at full road speed underneath; over the explosion's ~540ms lifetime the wreck could visibly separate from it. Now stores the vehicle object itself and re-reads its live x/y every frame, so the explosion tracks the wreck exactly for as long as it exists. Verified: a wreck that scrolled 15.6px over 10 frames had its explosion's drawn position move the identical amount, confirmed via direct object-reference equality.

**(4) Caught mid-turn, unrelated**: the page's own `<title>` read "Reckless Driving CAPTCHA" for no evident reason — renamed to "Highway Reckless Driving".

Full regression across 5 cars × repeated activations, no errors.

## 2.109.0 — 2026-09-07 00:40: Batch 217 — tank's shot now actually destroys what it visually hits

Direct bug report: "the shooting animation is fine but the cars are not destroyed and no explosion animation." Simulated a realistic shot to find the root cause rather than guessing: the mechanic only destroyed a vehicle if it physically touched the tank's (barrel-excluded, Batch 209) hitbox within the shot's 200ms activation window. At real game speeds, a car spotted at a normal distance takes far longer than 200ms to physically close that gap — confirmed directly: a car placed 40px away was still ~35px short of the tank when the window closed and the ability reverted to idle, never once triggering the destroy branch. Meanwhile the tracer/beam (Batch 211) already visually reaches that exact same target, implying a ranged hit the mechanic never actually delivered — the visual and the mechanic had drifted apart.

Fixed by having the shot destroy whatever the beam visually targets, immediately on activation, instead of waiting on a touch that was never going to land in time. New `findTankShotTarget()` (the nearest vehicle roughly in-lane, ahead, and within the same 140px range the tracer already uses) returns the actual vehicle to destroy; `findTankTracerTargetY()` now just reads its position for the beam's length. The destroy payoff (explosion, crushed/wreck state, debris, score, XP, sound) is the identical one every other ram-capable car already gets from the collision branch — no new reward path introduced. Verified: the same 40px-away car that previously survived the entire window is now crushed immediately on activation with a real explosion instance and correct score credit; out-of-range and different-lane vehicles correctly survive; no-target shots fire the flavor flash without erroring. Regression across 4 cars × repeated activations, no errors.

## 2.108.0 — 2026-09-07 00:15: Batch 216 — the three multi-lane fairness problems, fixed

Direct follow-up to a design discussion: three separate multi-lane balance problems, all confirmed against the real code before touching anything.

**(1) Score/XP/coins/energy/dodgedCount now only credit for a vehicle passing in the player's own lane or an immediate neighbor**, not any lane anywhere on the road. New `isNeighborLane(v)` (`Math.abs(v.lane - currentLaneIndex()) <= 1`) gates both call sites of `creditVehiclePass()` — the normal "surpassed" credit and the defensive "exited" fallback. Verified directly: a same-lane pass credits score/energy/dodgedCount normally; an identical pass 5 lanes away credits nothing.

**(2) Ambulance spawn chance decoupled entirely from lane count.** It used to be a 2%-of-attempt roll nested inside the normal-traffic spawn check, which itself scales with lane count (`config.lanes / 4`, from Batch 213) — so more lanes meant more attempts/frame, which dragged ambulance frequency up too even though its own conditional odds never changed. Pulled into its own independent per-frame roll with the same speed/difficulty scaling as before but no lane-count term. Verified empirically: 4 lanes and 10 lanes produced statistically indistinguishable ambulance counts over multiple 1-5 minute headless runs (devInvincible), where lane count previously would have scaled this up.

**(3) Rare Garage-car (rare/epic/legendary) encounter rate on the road no longer scales up with lane count.** `GARAGE_NPC_RARITY`'s weight is a fixed per-spawn-attempt probability, but total attempts/minute scale with lanes — dividing the weight by `lanes/4` cancels that back out, 4 lanes unchanged as the reference point. **Caught and fixed a real bug before shipping**: the first pass divided the WHOLE `GARAGE_NPC_RARITY` pool uniformly, but common-tier Garage cars make up 216 of its ~230 total weight (12 cars × weight 18) — dividing everything mostly throttled ordinary common Garage traffic, barely touching the actual rare/epic/legendary cars (only ~14 of that 230) the request was about. Rebuilt to only divide non-common tiers, verified: common-tier weight now stays exactly 216 at both 4 and 10 lanes, while the tank's (legendary) *absolute* per-minute encounter rate — accounting for the extra spawn attempts at 10 lanes — comes out to within 3% of the 4-lane rate.

**Also, direct correction on the lane-count score multiplier**: the existing curve (Batch 129) dipped at 4-5 lanes then rose back up toward 10, making 10 lanes end up better than 4 and nearly as good as 3 — backwards, since "10 lanes still gives more room to maneuver" even after the above fixes remove its other unintended advantages. Replaced with one monotonic curve: 3 lanes stays hardest (+0.7 bonus → 2.1x baseline), 4 lanes next (+0.4 → 1.8x), then a gentle decline down to 10 lanes (+0.2 → 1.6x). Verified across all 8 valid lane counts (3-10): strictly non-increasing from lane 4 onward, exact target values hit at 3/4/10.

Full regression across 3 difficulties × 4 lane counts, no errors.

## 2.107.1 — 2026-09-06 03:20: Batch 214 — barrel outline properly restored (not patched pixel-by-pixel)

Direct follow-up with a screenshot: "you forgot to add the black outline... it looks like some random grey line at the end of the barrel." Batch 212's fix (removing 4 specific outline pixels via `clearRect`) had gone too far — since the muzzle flare sat at row0 (the canvas's own topmost row, from Batch 208's lengthening), it never had a top edge to begin with, and clearing the remaining side pixels left it with literally zero outline. Re-checked "Reckless Vehicles3.dc.html" as directed: the doc's own `pTank()` has its tip at row1, with row0 left genuinely blank as outline-space above it. Fixed properly this time: moved the tip back to row1 and the shaft to rows2-10 (still 9 rows — the exact same extra length Batch 208 added, just correctly positioned), and shifted the base collar to rows9-10 to stay attached to the shaft's new tail. This lets `sil53`'s silhouette outline naturally wrap the flare's top AND sides, matching the doc, while keeping every bit of the requested extra length. Verified with pixel sampling: row0 now shows a genuine black top border above the flare, row1 shows the flare properly bordered on both sides, and the transition into the hull/collar looks structurally identical to the doc's own front-edge convention used everywhere else in this file. Regression-tested, no errors.

## 2.107.0 — 2026-09-06 03:00: Batch 213 — suicidal difficulty is now genuinely denser at every lane count

Direct report: "suicidal doesn't feel suicidal" at 4 lanes, and "even boosting it for more lanes (10) isn't enough either." Investigated empirically (using the `devInvincible` dev toggle to run long headless simulations without a run ending on first contact) rather than guessing at a fix. First measurement attempt was invalidated by a real testing bug on my end — `launchGame()` re-reads `config.difficulty` from the DOM dropdown, silently overwriting a direct assignment made just before calling it — corrected by driving the actual dropdown element instead. With that fixed, the real numbers confirmed the report exactly: average on-screen vehicle count was 2.20 (4L) / 2.11 (10L) for suicidal vs. 2.11 (4L) / 2.14 (10L) for reckless — suicidal was barely different, and at 10 lanes actually *worse* than reckless, despite its higher spawnChance multiplier. Root cause: `canSpawnAt()`'s spacing rule (`SPAWN_SAFETY_Y`) requires a lane's existing vehicle to have scrolled almost the entire 260px canvas height before another can spawn behind it — this dominates so completely that the density multiplier barely mattered (confirmed: tripling it alone did nothing). Fixed by making this spacing difficulty-aware (`DIFFICULTY_SPAWN_SAFETY_Y`, unchanged for calm/reckless, tightened to 60px for suicidal only) plus a real bump to `DIFFICULTY_DENSITY.suicidal` (1.6→2.2). Result: average on-screen count rose to 3.09 (4L) / 3.10 (10L) — a genuine ~45-50% increase at both ends of the lane-count range the user specifically called out. `requiredFreeLanes` (the actual "never truly unwinnable" guarantee from Batch 129) is untouched; stress-tested for 60 real seconds at both 4L and 10L with zero occurrences of all lanes being simultaneously blocked. Full regression across calm/reckless/suicidal × 2/3/6/10 lanes, no errors.

## 2.106.1 — 2026-09-06 02:15: Batch 212 — barrel flare restored, correcting Batch 209's misread

Direct correction with an annotated screenshot: Batch 209 misread "remove the 4 black pixels" as "remove the whole muzzle flare," but the user only meant 4 SPECIFIC outline pixels (circled directly on the image) — the flare itself ("the end of the barrel") was wanted and shouldn't have been removed. Restored the row0 muzzle flare exactly as it was in Batch 208, and instead surgically cleared just the 4 circled pixels: the two side-flanking dots next to the flare (9,0)/(14,0) and the two diagonal dots where the flare steps down to the 2px shaft (10,1)/(13,1), via `clearRect()` right after the silhouette outline draws. Verified with pixel sampling: row0 now shows the full 4px flare with no black at columns 9/14, row1 shows the shaft continuing with columns 10/13 cleared (transparent) instead of black. Regression-tested, no errors.

## 2.106.0 — 2026-09-06 02:00: Batch 211 — tank's tracer is now a real beam, reaching its actual target

Direct request: "finally add the tank like beam, like shooting effect from the file." Re-checked the earlier port (Batch 194/200) against the doc's own `drawTracer()`/`drawTankCue()` and found two real gaps: (1) the doc explicitly says to "stretch or clip the tracer to the real gap between barrel and target, it's a straight line by design" — the existing port ignored this, always drawing a tiny fixed-length flash (`farY = gy-4`) regardless of how far anything actually was, never a real beam. (2) `drawTankCue()`'s spent-casing ejection ("a spent casing ejects on alternate frames," called out explicitly in the doc's own description) was dropped from the original port entirely. Fixed both: new `findTankTracerTargetY()` scans for the nearest vehicle roughly in the tank's own lane, still ahead of the nose, and the tracer (`drawSbTracer`) now genuinely stretches to reach it — or a fixed 140px default range if nothing qualifies, so a shot into empty road still reads as a real beam instead of vanishing. Restored the casing-ejection lines in `sbTankCue`. Verified: a fake target 100px away produces a tracer whose recorded distance matches exactly, no target falls back to the expected default range, the impact spark now genuinely renders at the real target's distant position (not the old fixed nearby spot), and 60 repeated shot activations run error-free.

## 2.105.0 — 2026-09-06 01:35: Batch 210 — lane-change banking tilt removed entirely

Direct follow-up: Batch 209's fix stopped the permanent blur, but left a visible "jump" — the tank would render via its old (non-crisp) fallback path for the brief duration of the tilt, then snap back to the crisp path the instant the tilt settled, a jarring discontinuity. Rather than trying to patch that transition, removed the cosmetic banking tilt entirely per direct request ("just remove the like turning effect... keep the same speed for sliding to the lane... don't make it tilt"). The lane-change SLIDE itself (`this.x` easing toward `this.targetX`) is completely unchanged — same speed, same easing curve — only the rotation is gone; `this.tiltAngle` now stays permanently 0, and `MAX_TILT_ANGLE`/`TILT_SENSITIVITY` (now unused) removed. Verified: a real lane change now shows `maxAbsTilt: 0` for the entire glide while `player.x` eases through the exact same per-frame curve as before (e.g. 70→76.2→81.7→86.6→90.8→94.6...→122 over 55 frames). Regression-tested across 6 cars × a full lane-0-to-lane-3 sweep, no errors.

## 2.104.0 — 2026-09-06 01:20: Batch 209 — permanent post-lane-change blur fixed, barrel flare removed, barrel excluded from the hitbox

Three direct reports in one message. **(1) "car becomes blurred after changing lanes once and stays that way for the rest of the game"**: traced to the lane-change banking-tilt LERP (`this.tiltAngle`) — it asymptotically approaches its target but, in floating point, `this.x` can get permanently stuck a few ULPs short of `targetX` once the remaining distance drops below update precision, freezing `dx`/`tiltAngle` at some tiny but NONZERO value forever (confirmed empirically: `1.9989604377362727e-16` after 400 frames, never exactly 0). That residual is far too small to visibly rotate anything by itself, but it permanently failed the tank's crisp-render fallback check (`t.b !== 0`, added in Batch 206), silently reverting the tank to its old, blurrier direct-scaled rendering after the very first lane change. Fixed at the root: the LERP now snaps to the exact target once within 0.05px, so `tiltAngle` genuinely reaches 0. Also hardened the tank's own check to an epsilon (`> 1e-6`) as defense-in-depth against any future source of similar floating-point noise. Verified: after a real lane change + 500 frames, `player.x` exactly equals its target and `tiltAngle` is exactly 0 (previously stuck nonzero forever).

**(2) "the barrel... shouldn't be two black pixels on both sides... in the front"**: the row0 muzzle-brake flare (4px wide vs. the shaft's 2px, added in Batch 208) gave the silhouette outline two side-flanking black pixels at the very tip with nothing above them (row0 is the canvas edge) to read as an enclosed shape. Removed the flare — the barrel is now a uniform 2px tube its full length, base collar near the turret unchanged.

**(3) "the barrel shouldn't be included in the hitbox... you can crush even though you didn't technically touch anything"**: the tank's collision box previously spanned its full visual height, including the barrel's own rows (native 0-2) which have no hull underneath them. Rather than touching the player's real hitbox (read elsewhere for the ability bar, FX positioning, etc.), added `playerCollisionRect()` — narrows just the rectangle handed to `checkCollision()`, tank only, excluding those barrel-only rows (`TANK_BARREL_INSET_PX = 3 × CAR_SCALE`). Applied to both collision sites (main collision + close-call credit) so this covers every collision type (crash, ram, jump-over), not just the ram/crush case that surfaced it. Verified with mock vehicles: one whose leading edge reaches only 2px past the tank's nose (still within the barrel-only zone) no longer registers as a collision at all, while one reaching 5px past (into real hull territory) still does. Full regression across 5 cars × 2 lane counts, no errors.

## 2.103.0 — 2026-09-06 00:50: Batch 208 — real road bug found (lane-divider bias), plus a longer barrel

Direct follow-up with a screenshot: "still not fixed... why is the tank off and off-road, not centered... I'm talking about how it's displayed in gameplay on the road." Batches 206/207 had already made the tank's OWN sprite pixel-perfectly centered on its own hitbox, so this time the investigation moved to the ROAD itself — and found a real, previously-invisible bug: lane-divider dashes were drawn as `fillRect(x, y, 2, dh)`, 2px starting exactly AT the lane-boundary x and extending only rightward into the lane on that side. Confirmed with exact numbers from a live running game: `ROAD_BORDER_LEFT=18`, `laneWidth=26`, tank hitbox exactly `[44,70)` (tank's hitboxW×CAR_SCALE exactly equals the lane width — the only car in the roster with zero side margin, which is why this was invisible everywhere else). The left divider at x=44 bled 2px INTO the tank's own leftmost columns; the right divider at x=70 started exactly where the tank ended and extended AWAY from it — a one-sided bias, not a centering bug in the sprite at all. Fixed by centering the dash on its boundary (`x-1` instead of `x`), verified with real pixel sampling: both dividers now overlap the tank's hitbox by exactly 1 column on their respective sides, a true mirror image. Regression-tested across 2/3/4/5 lanes, no errors.

Also, direct request: "make the barrel of the gun one pixel longer... it blends in with the front of the car, doesn't really look like something connected to a barrel." The muzzle tip moved from row1 to row0 (the canvas's previously-unused topmost row) and the shaft extended to start at row1 (was row2) — one more row of visible shaft between the muzzle and the hull, using space that already existed but was empty. Verified: renders error-free, no change to hull/turret/tracks.

## 2.102.1 — 2026-09-06 00:30: Batch 207 — tank's remaining 1px-off-center bias fixed

Direct follow-up: "the tracks are okay now... but the tank should be like one pixel to the side." Batch 206's fix blitted the FULL 24-wide native canvas (mostly blank padding outside the 20px hitbox), scaled by `24 * CAR_SCALE = 31.2`, rounded to an ODD 31 — centering an odd-width rect on this car's true center (which frequently lands exactly on a .5 boundary, a direct consequence of `CAR_SCALE=1.3` combined with this car's own hitbox width) forced `Math.round()` to break the tie the same direction every time: a consistent bias, not the intended crisp centering, invisible in the earlier isolated test because that one happened to land on non-tied values. Root-cause fix: crop the source blit to just the hitbox-relevant `[2,0,20,32]` region and scale THAT to `20 * CAR_SCALE = 26` — an exact, even integer with no rounding-parity ambiguity at all. Verified across 7 test positions (including plain integers, half-integers, and arbitrary fractional ones): every integer/lane-snapped position now centers with **zero** diff from the expected hitbox center (previously a consistent +0.5px bias), and fractional in-between positions land within the same ±0.5px sub-pixel tolerance every other car sprite already has — no longer a one-sided skew. Track opacity re-verified unaffected (still fully opaque, hard edges, no regression from Batch 206).

## 2.102.0 — 2026-09-06 00:15: Batch 206 — tank tracks fixed (were see-through and looked off-center)

Direct bug report: "the right track is on the white stripes... the left one, but the right one is off of them" plus "the tracks aren't like somewhat transparent because I can see these white stripes through them." Investigated the sprite's own symmetry first (confirmed pixel-perfect, centered identically to the hitbox math) before looking at the rendering pipeline. Root cause: every car in this game draws via `ctx.scale(CAR_SCALE, CAR_SCALE)` (1.3x, non-integer) then `fillRect()` in local pixel-art coordinates — Canvas 2D always antialiases a fillRect landing on a fractional real-pixel boundary, which happens at nearly every edge under a 1.3x scale. On the tank's tracks (only 3 local px / 3.9 real px wide) that feathered edge ate a large fraction of the track's own width, letting the road color bleed through — and which SIDE looked more solid shifted frame to frame depending on the player's exact sub-pixel x position, not any real structural offset (this explains both complaints as one root cause). Fixed by drawing the tank into an isolated native-resolution (24×32, unscaled) offscreen buffer, then blitting it with nearest-neighbor sampling (identity transform, smoothing off) instead of drawing directly under the caller's fractional scale — guarantees fully opaque, hard-edged tracks regardless of on-screen sub-pixel position. Same isolated-buffer technique `drawCrushedWreck()` already uses. Falls back to the old direct-scaled draw if the active transform ever has rotation (not the case for the player car today, verified — 30 real gameplay frames all showed identity rotation, fast path always engaged). Verified with pixel sampling: before the fix, sampled track pixels showed light blended greys (partial-coverage antialiasing); after, every pixel is a hard, fully-saturated color with no intermediate blend values, and the two tracks are provably identical mirror images.

**Added to backlog, not started**: better explosion sound (see PLAN.md).

## 2.101.1 — 2026-09-05 23:52: Batch 205 — ram destroy now requires the actual front guard ("the drill") to reach the target

Direct follow-up correction on Batch 201's front-hit gating: `isFrontHit()` only checks horizontal lane alignment, so a vehicle the player merged sideways into (already well inside the player's own hitbox by the time `checkCollision()` fires, not approached head-on) could still pass it and get destroyed — "what actually destroys cars is not the drill in the front, it's the actual tank sprite... your car doesn't destroy other cars, [only] the drill." New `ramGuardContact()` adds the missing depth check: the target's leading edge must still be within the push-guard's own max forward reach of the player's nose (`SB_GUARD_REACH_PX = 8 * CAR_SCALE ≈ 10.4px`, matching `sbGuard()`'s own 8-row max depth) — a deep body-to-body overlap from a lateral merge no longer counts, even when perfectly lane-aligned. Tank is exempt (it fires a shot, has no physical guard). Verified with mock player/vehicle rects: a genuine 2px nose-to-tail overlap still rams; the same lane-aligned pair at a 15px deep overlap no longer does (falls through to a normal crash), while Tank's shot is unaffected either way.

## 2.101.0 — 2026-09-05 23:35: Batch 204 — Tank, Jet Bike, and Steamroller redesigned, ported from "Reckless Vehicles3.dc.html"

Direct instruction to pull just two updated textures (Jet Bike in the doc's section 2b, Steamroller in 2c) plus the redesigned Tank, and replace the in-game sprites — everything else in the doc explicitly out of scope. All three were drawn by a single shared function (`drawGarageTank53`/`drawGarageJetBike53`/`drawGarageSteamroller53`, reused for the Garage tile, the player car, and traffic rendering alike), so one edit per vehicle covers the whole game. Transcribed the doc's own `pTank()`/`pJetBike()`/`pRoller()` verbatim (`g.`→`gctx.`, `this.shade`→this file's existing `shade()`), plus a new `sil53()` helper ported from the doc's `sil()` — an outline that hugs the real silhouette (union of per-row x-spans) instead of a filled bounding box, which is how the tank's turret and the roller's drum now read as their own shapes instead of a rectangle notch. Tank gains real tread-link/sprocket detail, a glacis-break hull line, engine-deck louvres, and flank stowage bins. Jet Bike gains a flared nose/tail silhouette and a windscreen/headlight cluster. Steamroller's front drum now reads as a banded cylinder instead of a flat slab. Verified in-browser: all three render error-free with real, richly-colored pixel output (13-19 distinct colors each).

## 2.100.1 — 2026-09-05 23:10: Batch 203 — Daily Gift menu badge now also covers an unclaimed Daily Word

Direct request: the main-menu claim indicator should never disappear just from checking a tab without claiming, for missions, daily word, or daily gift. Missions and the score-threshold Daily Gift already worked this way (both recompute from real unclaimed state, `missionsClaimed`/`canClaimDailyGift()`, every time the menu is shown — verified, not touched). The real gap was the **Daily Word**: finishing today's word sets `allTimeStats.pendingWordReveal`, which sits until the in-tab CLAIM button is actually clicked, but `updateDailyGiftClaimBadge()` never checked it — so a completed word gave no reminder on the main menu at all. Fixed by having that function also check `pendingWordReveal`. Verified in-browser: badge lights up purely from a pending word (even with no score-gift claimable), survives repeated open/close of the Daily Gift tab, and only clears on a real CLAIM click.

## 2.100.0 — 2026-09-05 22:34: Batch 202 — explosion redesign, ported from the updated storyboard doc (part 1 of a multi-batch request)

Direct request, explicitly split into batches: "we've redesigned the explosions... please use them, replace the current one." User supplied a new file, `Shield Bump Storyboardv2.dc.html`, which redesigns the impact explosion entirely (bigger — 64×64, was 32×32 — and messier: a fireball built from 11 overlapping jittered-edge lobes instead of a plain ring+cross flash, real smoke puffs drawn before the fire, far more particles: 38 sparks/10 chunks/16 smoke/14 embers for the biggest variant, up from 14/6/0/0) plus two entirely new FX sections (Speed Air slipstream/wake, Ambient Road Air) that are explicitly a SEPARATE, later batch — this entry is the explosion redesign only.

Replaced the old particle-only `explodeShieldBump()`/flash system entirely. The fireball and smoke are "redraw a growing blob at a fixed point every frame" effects, not flying particles — a genuinely different rendering technique from the old approach, so they're their own timed-effect system (`sbExplosions`, same pattern as the Tank tracer) rather than being shoehorned into the existing `Particle` class. The spark/chunk/ember rain is still simple radiating points, computed analytically per-frame from a cached, seeded particle list (`sbExplosionParts()`) so the whole 12-frame/540ms instance replays deterministically exactly like the doc's own preview does, rather than being simulated frame-to-frame. Draw order matches the doc exactly: smoke, then fireball, then spark rain.

**Verification**: live-tested in the Browser pane. Confirmed all 3 variants generate the doc-exact particle counts (A: 38/10/16/14, B: 30/12/16/14, C: 38/10/20/14). Confirmed all 36 frame×variant combinations (12 frames × 3 variants) render with zero errors. Confirmed real, substantial pixel output (1099 opaque pixels, 7 distinct fire-ramp colors in a single frame) rather than a blank/degenerate result. Confirmed the full gameplay path — a real ram hit spawns the correct variant and it expires correctly once real time elapses. Ran an 80-frame regression across all 9 ramAbility cars with multiple overlapping explosions — zero errors.

**Not yet done, per direct instruction to batch this** — waiting for review before continuing: the new Speed Air (slipstream + rear wake) and Ambient Road Air sections, which should trigger off real vehicle speed (>200 km/h, intensifying with more speed) rather than ability use.

## 2.99.0 — 2026-09-05 22:24: Batch 201 — ram protection now requires a genuine front-on hit

Direct game-design idea: Shield Bump/Tank made survival trivially easy — touch anything, at any angle, and it's destroyed instead of ending the run. Restricting the payoff to a genuine front-on hit means you still have to drive carefully; a careless side-swipe (a merging vehicle, a badly-timed lane change) still crashes/kills you normally, exactly the same as without the ability active.

New `isFrontHit(player, v)`, gating the existing `player.abilityState === 'ramming'` collision branch — a non-front hit now falls through to the normal crash/ambulance-death branches exactly as if the ability weren't active for that specific collision, applying equally to both the 8-car Shield Bump roster and Tank (a forward-facing "shoot" arguably makes this even more apt for Tank specifically).

First implementation attempt used the standard AABB "collision axis" heuristic (compare raw X-overlap vs Y-overlap magnitude, whichever is smaller is the approach axis) — wrong for this game specifically: these car sprites are much taller than wide, so the X-overlap is almost always the smaller number regardless of actual approach angle, misclassifying real front hits as side hits (caught by testing before shipping, not left broken). Replaced with a width-normalized measure instead — how much of the combined half-width is actually overlapping horizontally (independent of height): close to fully lane-aligned counts as a front hit, only grazing at the edges (mid lane-change) counts as a side hit.

**Verification**: live-tested in the Browser pane. Confirmed the first (flawed) heuristic actually failed a same-lane, clearly-ahead test case — caught before it shipped. Confirmed the corrected width-ratio version passes that exact case, and separately confirmed a deliberately offset (side-swipe-style) collision is correctly rejected — crashes the run normally instead of crushing. Ran a 60-frame regression across all 9 ramAbility cars with front-aligned collisions — zero errors, all still crush correctly.

## 2.98.0 — 2026-09-05 13:00: Batch 200 — Tank follow-up: bar display fixed, shot now always visible

Direct follow-up right after 2.97.0 shipped: "the tank doesn't shoot, it doesn't do anything... the whole energy bar starts like it's chaos, draining everything, looks pretty weird."

### Energy bar "chaos" during Tank's shot
Real bug, not cosmetic noise: the `'ramdrain'` bar animation (a percent-of-window cycle from 100%→0%, with a cyan hazard-stripe border) was designed for Shield Bump's multi-second sustained mode, where visibly watching the bar drain over several seconds makes sense. Applied unchanged to Tank's ~200ms shot window, the exact same animation played as a jarring near-instant full-bar flash completely disconnected from the real energy change (just -2 cells). Tank's `abilityState === 'ramming'` now shows its real current energy directly (same calm `'charge'` display as idle) instead of running that cycle at all.

### Tank's shot wasn't actually visible most of the time
The muzzle+tracer effect only fired from inside the collision branch — i.e., only if a vehicle happened to already be touching the tank at the exact moment of activation. Pressing the button with nothing in front of you (the common case) produced no visible feedback beyond a barely-noticeable muzzle-glow pulse, reading as "the ability doesn't do anything." The tracer now fires once, guaranteed, at the moment of activation itself — every press now visibly shoots, independent of whether it happens to connect with something (the crush/wreck payoff on an actual hit is unchanged and unaffected).

**Verification**: live-tested in the Browser pane. Confirmed the tracer pushes immediately on activation even with no vehicle nearby. Confirmed the bar-percent calc for Tank's ramming state now exactly matches real remaining energy instead of a fake window-percent cycle. Confirmed a hit still crushes the vehicle correctly with no duplicate tracer (moving the push to activation-time and removing the hit-time one). Ran a 60-frame regression across all 9 ramAbility cars — zero errors.

## 2.97.0 — 2026-09-05 12:55: Batch 199 — Tank is no longer a Shield Bump car

Direct, frustrated correction: "you also had the design for the tank and you completely messed it up... he doesn't speed up... doesn't have any effects of the ramming abilities or these weird wi-fi waves. It just shoots."

Found the actual bug: Tank was sharing the exact same activation/mechanic path as the other 8 ramAbility cars — the +40% speed boost, the push-guard, and the air-ripple ("wi-fi waves") were ALL applying to Tank too, when the doc's own design (and every prior conversation about Tank) always described it as a completely separate mechanic. The ripple call in particular was gated only on `abilityState === 'ramming'`, not car type, so it silently leaked onto Tank regardless of the `car.key === 'tank'` branch sitting right next to it.

Tank now has its own, entirely separate activation path in `useAbility()`, gated on `selectedCarKey === 'tank'` before the shared Shield Bump branch is even reached:
- **No speed boost, no guard, no ripple** — `drawShieldBumpFX()` now returns immediately for Tank after drawing only its own muzzle cue; the thruster plume and ripple calls (previously unconditional) never run for it at all.
- **Not a sustained "drain the whole bar" mode** — a repeatable per-shot action instead. Each shot costs a flat `TANK_SHOT_COST` (2 cells) and opens only a brief 200ms window (long enough to register one hit and let the muzzle+tracer flourish play), not a multi-second timed mode.
- **Its own energy rule, explicit exception**: not the shared `ABILITY_MIN_ENERGY` (3 red bars) — just needs `TANK_SHOT_COST` available, checked fresh per shot, so it can fire repeatedly as long as energy lasts.
- **Unchanged, per direct confirmation**: a hit still crushes the target into the same wreck (explosion, debris, score/XP) exactly like the other 8 cars — "cars behave the same way as when rammed."

**Verification**: live-tested in the Browser pane. Confirmed Tank is blocked below 2 cells and fires exactly at 2 cells (well under the shared 34-energy threshold), with no change to `currentSpeed` or `sbGuardPhase`. Confirmed it can fire a second shot immediately after the first window closes, each costing the same flat amount. Confirmed `drawShieldBumpFX()` calls neither `sbPlume` nor `sbRipple` for Tank (patched both temporarily to verify directly). Confirmed a Tank hit still crushes the vehicle and fires both the tracer and the explosion flash. Ran a 60-frame regression across all 9 ramAbility cars (Tank included) — zero errors.

## 2.96.0 — 2026-09-05 12:47: Batch 198 — activation threshold lowered to 3 red bars, ram rate raised to 1.5s/cell

Direct follow-up: "make the jump ability you can use when you have only three bars... three red bars... make it the same with the ramming... each bar should last 1.5 seconds."

Lowered the shared activation threshold from "1 fully-lit orange cell" (cell index 3, ~45%) to "3 fully-lit red cells" (cell index 2, ~33.3%) for BOTH Jump and Shield Bump. The constant was renamed `JUMP_MIN_ENERGY` → `ABILITY_MIN_ENERGY` (`Math.ceil(3 * ENERGY_PER_CELL)` = 34) since it's no longer jump-specific — every reference across `useAbility()`, the bar's "ready" glow threshold, and the surrounding comments updated to match. Separately, Shield Bump's per-cell duration raised from 1000ms to 1500ms (`SHIELD_BUMP_MS_PER_CELL`), so a full 9-cell bar now runs 13.5s instead of 9s, and a threshold-only (3-cell) activation runs 4.5s.

**Verification**: live-tested in the Browser pane. Confirmed `ABILITY_MIN_ENERGY` computes to 34 and cell index 2 (the third cell) is genuinely red. Confirmed both Jump and Shield Bump are blocked one point below the threshold and activate exactly at it. Confirmed Shield Bump's duration at threshold (4590ms) and at a full bar (13500ms) both match the new 1.5s/cell formula exactly. Ran a 60-frame regression across all 9 ramAbility cars with randomized activation energies — zero errors.

## 2.95.0 — 2026-09-05 12:42: Batch 197 — Shield Bump activation threshold now matches Jump exactly

Direct correction: "you still cannot use the ability when you have over one bar of orange... make it the same as the jump ability... in both cases you need at least one orange bar to activate the ability."

Shield Bump previously required a completely full bar to activate at all — that was a deliberate early design decision ("activating drains the WHOLE bar"), but the user now wants activation gated identically to Jump: `JUMP_MIN_ENERGY` (the first fully-lit orange cell, 45%), not 100%. This has a real knock-on effect on duration, since the original spec ties duration directly to energy ("one cell allows for one second of ramming") — a partial-bar activation now gets a proportionally SHORTER ram instead of always the full 9 seconds. `SHIELD_BUMP_DURATION_MS` (9000ms) is kept as the full-bar reference value; the actual per-activation duration is computed live from however much energy was banked at the moment of activation (`(energy / ENERGY_PER_CELL) * SHIELD_BUMP_MS_PER_CELL`). The still-drains-everything-you-had and cannot-be-cancelled-once-started rules are unchanged. The ability bar's own "ready" glow and drain-percent display both updated to match — the bar now normalizes against THIS activation's real duration (stored in a new `player.sbActivationDuration`), not always the full-bar 9s, so it correctly reads 100%→0% regardless of how much was banked at the start.

**Verification**: live-tested in the Browser pane. Confirmed activation fails below `JUMP_MIN_ENERGY` and succeeds at exactly that threshold with the correct proportional duration (4050ms at 45% energy, exactly matching the formula). Confirmed a full-bar activation still gives exactly 9000ms, unchanged. Confirmed the +40% speed boost still applies and reverses correctly for a partial-bar activation. Ran a 60-frame regression across all 9 ramAbility cars with randomized activation energies between the threshold and 100% — zero errors.

## 2.94.0 — 2026-09-05 12:36: Batch 196 — explosion core flash, crushed wreck no longer squashed, energy-bar float-drift bug fixed

Direct follow-up with a screenshot showing the energy bar's real symptom.

### Explosion core flash — the part missing from the FX port
Direct report: "use the explosions because in the design I also gave you the explosions that should happen on top of the cars that you run." The 2.92.0 port carried over the storyboard doc's flying-particle logic (`parts()`) but missed the doc's other explosion element — a bright cross-shaped flash + expanding ring drawn AT the impact point for the first couple of frames (and again briefly for the Double Pop variant). New `drawSbFlash()` (ported from `drawExplosion()`'s own flash branch) plus a timed-effect list (`sbFlashes`, same pattern as the Tank tracer) so it renders on top of the rammed car for a couple of frames instead of being silently absent.

### Crushed wreck — squash removed entirely
Direct, explicit correction: "leave them like their normal sprite size, don't make them shorter or less wide." The squash transform (0.22 originally, reduced to 0.55 last batch, twist already removed) is gone completely — `drawCrushedWreck()` now composites the tinted/blurred buffer at 1:1 native size, no scale transform at all. Debris marks, which used to scatter across the old flattened band, now scatter across the car's full original height.

### Real bug: energy bar could get stuck looking "not quite full"
Direct report with a screenshot: a cell would render dim/pulsing instead of solid even when the underlying energy value should have been a clean whole number of cells ("started from zero... first few bars filled up fine, then it doesn't look like it's full"). Root cause: `ENERGY_PER_CELL` (100/9) is a repeating binary fraction — accumulating enough refills over a real run drifts by a tiny float epsilon, just enough that `Math.floor(lit)` rounds one cell short and that cell falls into the "still filling" render branch forever instead of the "fully lit" one. Added a tiny epsilon to the `lit` calculation in `drawAbilityBar()` to absorb exactly this class of drift (a standard, narrowly-scoped fix — doesn't affect genuine partial fills, which are on the order of single-digit percent, far above the epsilon).

### Also: the "still filling" cell now matches the normal cell's look
Separate direct report: "when energy bars are replenishing, the animation shouldn't be in solid color, it should be the design of the normal energy bar." A cell mid-refill was a single flat pulsing rectangle with no bevel, unlike fully-lit cells which get a lighter top edge / darker bottom edge. Now gets the same beveled highlight/shadow, clipped to its current partial width, so it reads as the same cell style mid-fill instead of a plain block.

**Verification**: live-tested in the Browser pane. Confirmed the flash pushes on hit, draws error-free across its frame range, and expires on schedule. Confirmed the crushed wreck's rendered bounding box now matches its original height almost exactly (33px rendered vs. 31px native, the difference being blur bleed) instead of the old ~0.55x squash. Confirmed the bar's partial-fill bevel renders without error across charge/ready/ramdrain states. Ran an 80-frame regression across all 9 ramAbility cars with periodic collisions — zero errors.

## 2.93.0 — 2026-09-05 12:27: Batch 195 — crushed-wreck follow-up + a real energy-bar bug found

Direct follow-up right after 2.92.0 shipped, plus one real bug caught by the user that had nothing to do with the crushed-wreck work.

### Crushed wreck no longer lingers like it's still driving
Root cause: a crushed wreck kept its old TRAFFIC `speedOffset` (deliberately tuned near-zero so approaching traffic closes in slowly and realistically), while the road/scenery itself always scrolls at the full `currentSpeed` (`roadOffset += currentSpeed`, no offset). So a freshly-crushed wreck lingered near the player at "traffic pace" instead of being left behind like ground debris — "the corpse is just driving underneath me." Now zeroes `speedOffset` the moment a vehicle is crushed, pinning it to the same scroll rate as the road itself.

### Crushed wreck — twist removed, tint darkened further
Direct correction: liked the grey/black direction from 2.92.0 but wants it pushed further ("more barren, more grey, more black pixels") — grayscale 60%→85%, brightness 0.55→0.4, tint alpha 0.45→0.6. The random shear ("twist") added last batch combined with the squash to look "super squished and rotated... really weird" — removed entirely, back to a plain vertical squash with no shear.

### Real energy-bar bug: refill/rounding still assumed 10 cells
Direct report: "the energy bar doesn't get used to the limit... you can get sometimes like half a energy bar." Root cause: three separate energy-grant sites (`creditVehiclePass()`'s three refill amounts, the close-call refill, and the jump-release rounding) were all still snapping to flat multiples of 10 — a leftover from the OLD 10-cell bar (Batch 53), where 10 energy was exactly 1 clean cell. Under the current 9-cell bar (Batch 192), 100/9 ≈ 11.11 per cell, so none of those flat-10 grants land on a clean cell boundary anymore — the bar could sit at a permanently half-lit cell after almost any refill. Hoisted a single shared `ABILITY_BAR_CELLS`/`ENERGY_PER_CELL` pair that every energy-quantization site now derives from (including `drawAbilityBar()`'s own cell count and `JUMP_MIN_ENERGY`'s formula), so they can't drift out of sync with each other again. All refill amounts re-expressed as whole-cell multiples (1/2/5/4 cells instead of flat 10/20/50/40).

Separately confirmed still correct and unchanged: Jump's "needs at least one fully-lit yellow cell" rule (`JUMP_MIN_ENERGY`, now `Math.ceil(4 * ENERGY_PER_CELL) = 45`, same value as before) — likely felt broken before this fix only because the misaligned refills made the bar's visual state an inaccurate reflection of the real energy number.

**Verification**: live-tested in the Browser pane. Confirmed `speedOffset` zeroes on crush and the wreck's per-frame Y movement then matches `currentSpeed` exactly. Confirmed `crushTwist` is gone with no stray references left behind. Confirmed all 4 refill amounts (1/2/4/5 cells) land on exact whole-cell boundaries, and that 2 accumulated normal-pass refills produce a cleanly-integer `lit` value (no fractional remainder) in the bar's own render math. Confirmed the jump-release cell-rounding correctly handles both a genuine mid-cell value (rounds down to the true lower cell) and an exact boundary value (stays exactly there, no float-drift false rounding in either direction). Ran an 80-frame regression across all 9 ramAbility cars with periodic collisions — zero errors.

## 2.92.0 — 2026-09-05 12:17: Batch 194 — Shield Bump: real FX port from the storyboard doc, crushed-wreck visual overhaul

Direct, frustrated feedback on 2.91.x's FX: "you didn't include any of the animations as I sent you the design... they don't look at all like [what I gave you]... so bad." Two real fixes, not just polish.

### Shield Bump FX — actually ported from Shield Bump Storyboard.dc.html this time
The earlier pass (2.91.0) used simplified placeholder shapes (rectangles, plain arcs) instead of the user's own design doc, reasoning that hand-editing pixel art without visual verification was too risky. That reasoning missed something: the doc isn't just reference art to eyeball, it's actual executable canvas-drawing code with real coordinates, colors, and timing — safe to transcribe directly rather than needing to guess. This pass does that:
- **Push guard** (doc section 2/5): real `sbGuard()` port — tapered multi-row metal grille with highlight/rivet detail, a genuine 5-frame extend animation (300ms) on activation, held at full extension for the whole window, then a genuine 5-frame retract (350ms) on deactivation. Widths scale proportionally to each car's real hitbox (the doc's own numbers were sized for a ~16px reference car). New `player.sbGuardPhase`/`sbGuardTimer` state machine, tracked independently of `abilityState` specifically so the retract animation keeps playing for its own ~350ms after ramming has already ended, instead of being cut off.
- **Speed thruster** (section 1): real `sbPlume()` port — the tapered flame with its color ramp, wobble, and core highlight, not a static two-tone rectangle.
- **Air ripple** (section 3): real `sbArc()`/ripple port — 3 staggered rings genuinely expanding/fading per the doc's own timing, not 2 plain semicircle strokes.
- **Tank active cue** (section 7) and **Tank muzzle+tracer** (section 6): both ported — the muzzle glow loop, and the one-off `explode()` particle burst on each hit replaced with a real timed tracer effect (`sbTracers`, muzzle flash → beam → impact spark over 6 frames/240ms), compressed vertically since a Shield Bump hit fires at touching distance rather than the doc's longer-range sheet.
- **3 explosion variants** (section 4): now use the doc's own `parts()` angular/speed distributions and spark/debris color ramps as real particle velocities (Radial Burst 14 sparks/360°, Side Shear 10 sparks in a ~115° cone, Double Pop with a genuine second offset burst) instead of just varying particle count/one secondary color.
- Metal guard material picked as the single default (the doc offered metal vs. canvas/fabric) — fits the roster's bulky/utility theme.

### Crushed-wreck visual overhaul
Separate direct complaint: "the car suddenly turns more black and grey, has particles of smoke, gets blurred, maybe somewhat twisted... it should be the same car, not one sprite that appears every time... you just made some rectangle, this doesn't look like any car at all." The old render (`ctx.scale(1, 0.22)` squash + a flat `rgba(...)` rectangle drawn over the whole flattened footprint) — both the extreme squash and the rectangular overlay ignoring the car's actual silhouette contributed to that. New `drawCrushedWreck()`: draws the body into an **isolated offscreen buffer** first (`Vehicle.drawBody()` gained an optional context parameter for this), applies a canvas `filter` (grayscale/darken/blur) and a `source-atop` tint that respects only the car's own drawn pixels — not a bounding box — then composites it back with a less extreme squash (0.55, was 0.22) plus a small per-wreck random shear (`v.crushTwist`) for a "crumpled," not cleanly-geometric, look. Lingering smoke chance raised 12%→22% plus a second darker source, per "has particles of smoke."

**Verification**: live-tested in the Browser pane. Confirmed the guard phase machine transitions extend→hold→retract→idle with correct timing, and that the retract animation genuinely outlives `abilityState` reverting to idle. Confirmed all 9 ramAbility cars (including Tank and the 3 without `hitboxW`) render through all 3 guard phases with zero errors. Confirmed each explosion variant spawns the doc-correct particle counts (20/14/26) with real non-degenerate velocity vectors, not all-zero. Confirmed the Tank tracer pushes on hit and expires correctly once real time elapses (an initial check gave a false "never expires" reading from a synchronous test loop not advancing real wall-clock time — confirmed it does expire correctly once actual time passes). Ran a 100-frame regression per car across all 9, mixing in normal and ambulance traffic — zero errors. Confirmed the crushed-wreck buffer render produces no errors and shows genuinely varied (404 distinct colors in a sampled region, not the ~1-3 a flat rectangle would show) pixel content.

## 2.91.1 — 2026-09-05 03:11: Batch 193 follow-up — real bug found by independent review: Shield Bump didn't protect against ambulances

Commissioned a second agent to independently review the Shield Bump implementation right after it shipped (2.91.0). It found one real bug: the ambulance instant-death branch was checked BEFORE the ramming branch in the collision handler, so a player mid-Shield-Bump who hit an ambulance still died instantly instead of destroying it — contradicting the finalized spec ("colliding with ANY vehicle should NOT crash the player" during the active window). The old comment on that branch ("ram still doesn't protect") predates this rework entirely, from back when ram was dead code and the ordering was moot — not a deliberate choice made during this implementation. Jump already treats ambulances as just another vehicle to grant immunity against; reordered so Shield Bump now matches that precedent, while a non-ramming hit on an ambulance still instant-kills exactly as before (including its distinct red/blue explosion visual, which briefly got dropped mid-fix and was restored).

**Verification**: live-tested in the Browser pane after a full page reload (an earlier same-session check without reloading gave a false negative from stale cached code — worth remembering for next time). Confirmed a Shield-Bump-active player who hits an ambulance now gets it crushed (run continues, `ramsUsed` increments) instead of dying. Confirmed a normal (non-ramming) hit on an ambulance still ends the run immediately, same as always. Ran a 600-frame regression with Tank, mixing in periodic ambulance and normal traffic through a full activation-to-expiry cycle — zero errors, 18 rams credited including ambulances rammed mid-window.

## 2.91.0 — 2026-09-05 03:03: Batch 193 — Shield Bump implemented: ram ability reworked, restricted to a 9-car roster

Full implementation of the "Shield Bump" ability redesigned over a long design conversation (Storyboard FX doc, vehicle roster, mechanic spec) — the biggest ability-system change since ram was first added.

### Real discovery: ram had been dead code
Before touching anything, found that `config.ability` was hardcoded to `'jump'` unconditionally in `launchGame()` — `// no longer a player choice`. The entire `'ram'` branch in `useAbility()` and the whole ram collision branch were unreachable by any player, for an unknown number of prior batches. This work didn't just restrict an existing ability, it made ram reachable again in an entirely new form.

### Vehicle restriction
Added `ramAbility: true` to 9 `GARAGE_CARS` entries: Tractor, School Bus, Garbage Truck, Fire Engine, Road Train, Limousine, Monster Truck, Steamroller, and Tank. `launchGame()` now derives `config.ability = getSelectedCar().ramAbility ? 'ram' : 'jump'` instead of the old hardcode — every other car keeps the universal Jump, exactly one `useAbility()`/readyThreshold/result-screen code path needed touching since everything downstream already branched on `config.ability`. Dragster/Land Speeder deliberately excluded (thematic mismatch — the push-guard's fixed width clashes with their narrow, needle-nose silhouette), not a technical limitation.

### New mechanic
- `SHIELD_BUMP_DURATION_MS = 9000` — direct spec, "one cell allows for one second of ramming... full nine should allow for nine seconds," tied to the bar's 9 cells (Batch 192).
- `SHIELD_BUMP_SPEED_MULT = 1.4` — direct spec, "the car speeds up by 40%." Applied to the shared `currentSpeed` global on activation (`currentSpeed *= 1.4`) and precisely reversed on deactivation (`currentSpeed /= 1.4`, not a snapshot-restore) so the natural speed ramp that happened during the window survives the reversal.
- Still requires a full 100% bar to activate (unchanged). Still has no cancel path — the keyup/release handlers only ever checked `abilityState === 'jumping'`, so "cannot be manually cancelled once started" was already true structurally; just had to not accidentally add one.
- Multi-hit-per-window falls out for free from the existing per-vehicle collision loop — same crushed-wreck payoff (score/XP/`v.crushed`/debris) fires once per vehicle touched during the whole 9s window, not just once per activation.
- The empty-bar "vulnerable" aftermath is a natural consequence of Jump and Shield Bump sharing one `energy` field — no separate flag needed. Confirmed live in testing: a vehicle spawned right as the window ended crashed the player normally, exactly as intended.

### Visual FX — simplified first pass, not the storyboard doc's pixel art
`drawShieldBumpFX()`: a push-guard rectangle at the front for the 8 non-Tank cars, a pulsing muzzle glow for Tank instead, 2 expanding ripple arcs, and a flickering rear thruster — all simple canvas shapes drawn before the car sprite (so nothing covers the body), not hand-pixel-art. `explodeShieldBump()` adds 3 randomly-picked particle-count/color variants for the per-hit explosion instead of one fixed burst. Deliberately not a port of the user's own `Shield Bump Storyboard.dc.html` (7 hand-drawn sprite sheets) — pixel-editing delicate art with no way to visually verify it in this environment has gone wrong before (the Jet Bike sprite-sizing incident); real porting of that doc is a follow-up pass once it can be visually reviewed. The ability bar also gained a distinct `'ramdrain'` state (cyan stripe) so Shield Bump's drain no longer looks identical to Jump's amber hold-drain.

### Garage ability indicator
`.car-tile-ability-badge` — a small corner tag ("RAM", or "SHOOT" for Tank) on the 9 ramAbility car tiles only; every other tile (including undiscovered mystery cards, which return early before reaching this code) shows nothing. `#ghcAbility` — a matching line in the hover-info card ("ABILITY: SHIELD BUMP" / "ABILITY: TANK SHOOT").

**Verification**: live-tested in the Browser pane end-to-end. Confirmed `config.ability` derives to `'ram'` for a ramAbility car and stays `'jump'` for Stock. Confirmed activation: exactly 1.4× speed ratio, 9000ms duration, energy zeroed. Confirmed a vehicle collision during the window crushes it (score/XP/particles) without ending the run, and that the ability survives multiple hits without cancelling (2 separate vehicles rammed in sequence, `ramsUsed` incremented each time). Confirmed the speed boost reverses to within floating-point rounding of the mathematically exact expected value when the window naturally expires. Confirmed the new `'ramdrain'` bar state and `drawShieldBumpFX()` both render with zero errors. Ran a 600-frame regression with periodic vehicle spawns through a full activation-to-natural-expiry cycle — zero errors, and the run correctly ended when a vehicle collided with the player right after the window closed (the vulnerability window working as designed, not just asserted). Confirmed the Garage badge/hover-card show correctly for a ram car, Tank's own distinct label, and nothing at all for Stock. An independent second-agent code review of the whole implementation was also commissioned per direct request; its findings will be folded in separately once it reports back.

---

## 2.90.3 — 2026-09-04 23:59: Batch 192 follow-up — energy bar shortens instead of widening its cells

Direct correction right after 2.90.2 shipped: that pass kept the bar's total width fixed (140px) and widened each cell (11→13px) to fill it — wrong call. "Leaving the cells as they were and just having the energy bar be less wide" was the actual ask: cell width reverted to the original 11px, and the bar itself shortens by one cell's worth instead (140→127px), removing the space the 10th cell used to occupy rather than redistributing it. Canvas `width=` attribute and `#abilityBar`'s CSS `aspect-ratio` both updated to match (127/16), so the displayed size still matches the native pixel art 1:1.

## 2.90.2 — 2026-09-04 23:57: Batch 192 — energy bar: 9 cells instead of 10

Direct request: "make the energy bar have only nine cells instead of ten... that way you have three red, three yellow and three green cells" (the existing 10-cell bar split unevenly: 3 red / 4 yellow / 3 green). `drawAbilityBar()`'s `cells` constant changed 10→9.

Found and fixed one real dependency this touched: `JUMP_MIN_ENERGY` (40%) was precisely tuned under the 10-cell math so the jump-ready threshold lands exactly when the first yellow cell is fully lit (a bug Batch 153 had specifically fixed once before). Under 9 cells that boundary shifts to 44.44%, so raised to 45 to preserve the same "you can jump once you have at least one full yellow cell" behavior instead of quietly breaking it again.

**Verification**: confirmed `cellColor()`'s existing .34/.7 thresholds land on an exact 3/3/3 split with 9 cells (no changes needed there); confirmed cell index 3 (first yellow) is genuinely fully lit at the new `JUMP_MIN_ENERGY=45`; confirmed the redrawn bar's content still fits inside its canvas with no overflow.

---

## 2.90.1 — 2026-09-03 08:40: Batch 191 — crushed wreck: darker/burnt tint, lingering smoke

Direct follow-up right after Batch 190's crushed-wreck ram effect shipped: "make sure that when the car gets squashed it also gets darker, like it was a small explosion, a bit burnt out — there are particles coming through it, so it should look like a wreck." Two small additions, no new systems: the crushed overlay tint deepened toward a genuinely dark, slightly warm "burnt out" tone (was a neutral grey `rgba(20,20,22,0.55)`, now `rgba(12,9,8,0.72)`), and half the wreck's debris marks now render as dark ember/orange flecks instead of all-grey. A low-chance (12%/frame) lingering smoke wisp now spawns from the wreck while it sits on the road, reusing the existing generic `Particle` class — no new particle system needed.

**Verification**: live-tested in the Browser pane. Confirmed a crushed vehicle's debris spots include a mix of `ember: true/false` flags. Confirmed particles are actively spawning and decaying from a crushed wreck across 40 forced frames. 3000-frame regression clean, zero console errors.

---

## 2.90.0 — 2026-09-03 08:30: Batch 190 — Stock spawn rate, real crash sound, ram leaves a crushed wreck

Direct follow-up on a PLAN.md triage session: 3 concrete builds.

### Default car is now a real, common NPC sighting
Stock previously never spawned as its own distinct NPC at all (folded into "redundant with sedan"). Per direct request ("your default car should be like 30% of all spawning normal cars"), added a flat 30% roll checked before the existing rarity-weighted pool — Stock now shows up as itself, roughly 3 in 10 "normal"-type spawns. Verified at ~30.85% over 2000 sampled spawns.

### Crash sound rebuilt — was "too electric/electronic"
The old sound was raw, unfiltered white noise — read as static/digital hiss rather than an impact. Routed through a `BiquadFilterNode` lowpass sweep (3200Hz → 300Hz over the burst) to kill the harsh full-spectrum hiss, and layered a separate fast-dropping low sine "thud" underneath for physical weight — a pure noise burst can't sound like a hit on its own, a felt low-end boom is what sells it. Also louder overall (peak gain raised), and now genuinely speed-scaled (louder AND longer for a harder hit) via the same `speedRatio01()` input the screen shake already used — previously logged as a PLAN.md gap, now closed.

### Ramming: the target no longer just vanishes
Real design problem worked through with the user: instantly removing a rammed vehicle read fine for small cars but wrong for big ones (the fixed particle burst never matched their scale), and a launch/knockback effect "looked kind of ridiculous." Landed on: the rammed vehicle is flattened in place via a canvas squash transform on its OWN existing sprite (so it's automatically the right shape/size for whatever was hit — a squashed Road Train still reads as a squashed Road Train, no size mismatch), tinted dark, given a few scattered debris marks, and left on the road as a harmless, non-collidable wreck the player drives straight over — it keeps scrolling with the road and despawns naturally once it exits, same as anything else, no new cleanup logic needed. New `Vehicle.crushed` flag gates it out of collision, close-calls, and lane-changing, but it still pays a normal "surpassed" pass credit once you're clear of it, same as anything else you drive past. `Vehicle.draw()` refactored to expose a `drawBody()` the crushed branch reuses under its own transform, instead of duplicating the ambulance/Garage-car/generic-body dispatch. Tank also got its own flavor: an extra amber muzzle-flash burst at the player's own front on top of the normal explosion — same ram mechanic exactly, just a "shot fired" flourish, no new projectile-physics system.

**Verification**: live-tested in the Browser pane. Confirmed Stock's spawn ratio (~30.85%/2000 samples). Confirmed `playSound('crash', ratio)` runs with no exceptions across the full 0–1 ratio range. Confirmed a rammed vehicle sets `crushed`/`debrisSpots`, stays in the `vehicles` array instead of being spliced, samples as a dark flattened band instead of its normal sprite, and driving straight through its position afterward no longer ends the run. Confirmed a crushed wreck despawns cleanly once it scrolls off-screen, no special-case cleanup required. Confirmed Tank's muzzle-flash branch fires with no errors. Ran a real unattended 3000-frame playthrough through an actual crash (not manually forced) — zero console errors.

---

## 2.89.0 — 2026-09-03 08:00: Batch 189 — Daily Missions, real system implemented

Replaces Batch 181's design-only screen (fixed doc-sample data, no real tracking, no reward payout) with a fully real system, worked out across a long multi-message design conversation covering scaling philosophy, per-mission goal numbers, and 2 rounds of numeric refinement.

### The mission pool: 14 missions, real formulas
`MISSION_DEFS` replaces the old `XP_MISSIONS`/`COIN_MISSIONS` placeholder arrays — 7 XP + 7 coin, 3 of each picked at random every day (`ensureMissionsToday()`, same `dayKey()` day-boundary convention Daily Gift/Word already use). Every mission's goal scales with player level, explicitly capped at level 100 (matching the existing `REWARD_LEVEL_CAP` convention) so nothing grows forever. Full list with level-1/level-100 values: score X total today (1200→2190, cumulative across every run); survive X seconds (90→190, best single run); score X on a randomly-assigned harder difficulty (800→1295); play X runs (fixed at 5); drive 3 distinct cars scoring X+ each (300→550, only enters the pool once 3+ cars are owned); X close calls (3→13); jump over X cars (10→30); jump over an ambulance (1→5); stay airborne X seconds total (20→40, combined across every jump); reach a random speed target from {180,190,200,210,220} km/h, capped at your fastest owned car's real top speed; reach a 3.0x multiplier; change lanes X times (80→180); meet X ambulances (2→7); and spot a rare car — a coin-flip at roll time locks in either "1 epic/legendary" or "3 distinct rares" as that day's fixed requirement (real math run on this one: legendary alone would've averaged ~12-13 min to encounter, "epic-or-legendary" and "3 distinct rares" both land around ~2.4-2.8 min instead).

### Real tracking, wired into actual gameplay
New per-run counters (`peakSpeedThisRun`, `airborneFramesThisRun`, `ambulancesMetThisRun`, `jumpedOverAmbulanceThisRun`) alongside the existing ones (`closeCallsThisRun`, `jumpedOverCount`, `laneSwitchesThisRun`), all folded into `allTimeStats.missionsProgress` in one place — `recordRunStats()`, right where every other lifetime stat already gets finalized — rather than scattered across the hot gameplay loop. The one exception is rare-car spotting, which hooks directly into the existing car-spotting site (independent of the lifetime "first ever discovery" gate, since this needs to fire every day) guarded per-vehicle-instance so it can't double-credit. `creditMission(id, value, mode)` is a no-op for any mission not actually rolled today, so every credit site can fire unconditionally without checking eligibility itself.

### Real reward payout and persistence
Claiming now actually grants currency — `gainXP()` for XP-category missions, `allTimeStats.totalCoins +=` for coin-category — instead of just flipping a local flag. Claimed/paid state moved from the old transient `msnClaimed`/`msnPaid` (reset on page reload) into `allTimeStats`, so it survives a refresh. MISSIONS DONE and CLEAN SWEEPS on the footer are now real lifetime counters, not the doc's static demo numbers — clean sweeps are detected the moment a new day rolls over, checking whether the previous day's 6 were all claimed before the reset.

**Verification**: extensive live-testing in the Browser pane. Confirmed a fresh (localStorage-cleared) player rolls 6 valid missions with the `drive_3_cars` eligibility gate correctly excluding it until 3+ cars are owned. Confirmed every one of the 14 missions' tracking hooks fires with the correct value via forced `recordRunStats()` calls (score, close calls, jump-overs, ambulance jump/meet, lane changes, airborne seconds, peak speed via `speedToKmh()`, peak multiplier, distinct-car threshold counting, rare-car spotting in both epic and rare modes) — including confirming a mission NOT rolled today correctly receives zero credit. Confirmed claiming an XP mission grants real XP and a coin mission grants real coins, `missionsDoneTotal` increments, and the footer stat updates live. Confirmed clean-sweep detection fires exactly once when all 6 of a day's missions are claimed before the next day's roll. Ran a real, fully unattended 2500-frame playthrough (through an actual crash via the normal `endRun()`/`recordRunStats()` path, no manual state forcing) and confirmed mission progress updated correctly with zero console errors. Confirmed `fastestOwnedCarKmh()` correctly clamps the speed mission's target (170 for a stock-only player, 250 once a Dragster is owned).

---

## 2.88.0 — 2026-09-03 07:20: Batch 188 — night mode removed entirely

Direct decision after a design back-and-forth: "i would like each car [taillight positioned exactly], so maybe this night mode is not a good idea? you know what that enough, scrap whole night mode, remove everything associated with it (also from settings)." Fully reverted the Batch 69/184-187 night mode system rather than partially completing it.

Removed: the Settings screen's NIGHT MODE toggle row entirely (was between AMBULANCE/SIREN VOLUME and SKIP CRASH ANIMATION); `config.nightMode` and its `+0.2×` multiplier bonus term; the whole per-frame darkness-overlay/roadside-window-lights/headlight-cone/taillight/lane-change-blinker drawing block from live gameplay; the matching crash-sequence darkness pass; the `drawHeadlightCone()` and `drawNightAmbient()` helper functions; the `laneChangeDir` vehicle field (existed only to feed the now-removed blinker lights). `Vehicle`'s real lane-change state machine (`changingState`/`targetLane`/`indicatorTimer`) itself is untouched — that's genuine gameplay logic unrelated to night mode, it was just never visually hooked into anything else either.

**Verification**: live-tested in the Browser pane. Confirmed `#nightToggle`/`#nightMode` no longer exist in the DOM. Confirmed `'nightMode' in config` is `false`. Ran a real 2000-frame unattended playthrough (through a full crash → result-screen cycle) with zero console errors. Confirmed the Settings screen's surrounding rows (siren volume, skip crash animation) still render correctly with no layout gap.

---

## 2.87.2 — 2026-09-03 07:05: Batch 187 — 2 real night-mode bugs fixed; rest of the feedback needs your call

Direct feedback flagged 5 issues in one message; fixed the 2 that were unambiguous real bugs, held off on the rest since they involve real design tradeoffs (see chat for the questions).

### Fixed: crashed cars were too bright in night mode
Real ordering bug: `drawNightAmbient()` (the darkness overlay) was called BEFORE `csDraw()` drew the wrecks/responders, so they painted at full brightness on top of the darkness and undid it completely — live gameplay draws vehicles first, THEN dims with the overlay, and the crash sequence wasn't matching that order. Swapped it. This also darkens the responders' red/blue light-bar flash along with everything else, which would read as a smudge rather than a proper emergency light — so it's re-punched through the overlay right after, same on/off color `csDraw()` already computes.

### Fixed: headlight cone had an abrupt bright-then-dark seam
The small radial "hot core" layered at the cone's tip (added in Batch 185 for bulb-glint) was reading as its own separate bright aura sitting on top of the trapezoid, not blending with it — exactly the "shouldn't have an aura, only the cone" feedback. Removed entirely; the trapezoid's own gradient is now the only light drawn.

**Verification**: live-tested in the Browser pane. Forced a crash sequence with night mode on and a bright yellow test wreck (`#ffcc00`) — confirmed it now samples as a heavily dimmed `[25,24,13]` instead of full brightness, while the responder's light-bar pixel still reads a fully saturated `[255,71,87]`. Confirmed the cone's tip-center and near-edge samples are now identical (no more separate bright spot at the exact center). 1500 real frames with night mode on ran a full crash-to-result-screen cycle with zero console errors.

**Held off on, needs a decision** (see chat): exact per-car taillight positioning matching each sprite's own painted rear lights (a real scope question — this game has 50+ distinct car sprites, verifying/matching each one individually is a lot of work for a pixel-scale detail); brake-only taillight lighting (the player has a real brake input to hook into, `vKeys.down`, but NPC traffic has no modeled braking/deceleration state to key off of — needs a decision on what NPCs should do instead: stay always-on as a "running light," go dark entirely, or something else); whether the player's headlight cone should stay intentionally bigger than NPCs' (it currently doubles as real forward visibility, which was a deliberate choice, not an oversight — flagged to confirm that's still wanted); and cone size scaling with the still-not-built 3-tier night difficulty (logged, blocked on that system existing at all).

---

## 2.87.1 — 2026-09-03 06:50: Batch 186 — headlight cone widened to car width, flat-pixel taillights, dark crash sequence

Direct follow-up on Batch 185's cone/lights, 3 pieces of feedback.

### Headlight cone's near end widened to the car's own width
"Why is the bottom of the cone so thin? It should be like the size of the car, it's headlights." `drawHeadlightCone()` was a triangle collapsing to a single point right at the car — now a trapezoid, `carHalfWidth` wide at the car itself, spreading further out to `carHalfWidth + length*0.35` by the far end. Both call sites (NPC, player) now pass the vehicle's own half-width instead of a fixed cone-only number.

### Taillights: gradient aura replaced with 2 flat red pixels
"Instead of having this red aura, just make them two red pixels, that would be much better." Both the NPC and player taillight `createRadialGradient` blobs are gone, replaced with 2 solid `rgba(255,60,70,0.95)` 2×2 pixels, one at each rear corner — same "no aura, just glowing pixels" treatment the lane-change blinkers already used.

### Crash sequence now stays dark in night mode
"When you crash the crash animation should also be like night time." Real gap found: the whole night-mode block (darkness overlay + roadside lights + vehicle lights) only ever ran inside `if (gameActive)` — the moment a crash started `CS.active` took over and the scene snapped straight back to a plain daytime road, regardless of what mode you'd been driving in. Factored the darkness-overlay + roadside-window-lights part out into a shared `drawNightAmbient()` (used by both the live-gameplay path and the new `CS.active` call site) so the crash sequence's background stays dark too. Deliberately did NOT add headlight/taillight drawing to the crash sequence itself — the wrecked car's lights going dark is exactly the "lights turn off" effect asked about, and it happens for free simply by not drawing them there, no on/off logic needed. Responders (police/ambulance) keep their own pre-existing red/blue light-bar flasher, a separate system untouched by this.

**Verification**: live-tested in the Browser pane. Confirmed the cone's near-left/near-right corners (at the car's own edges) are now lit — previously dark, since the old triangle had zero width there. Confirmed the taillight's rear-center point is now dark (no more gradient blob) while both rear corners read red. Confirmed a forced night-mode crash sequence samples the same dark `[9,13,23]` background the live gameplay overlay uses, while a forced daytime crash sequence still reads the normal bright road color (`[90,95,102]`) — the darkness only applies when night mode is actually on. 1200 real (unattended) frames with night mode on, which crashed naturally partway through and exercised the new `CS.active` dark-overlay path for real, zero console errors.

---

## 2.87.0 — 2026-09-03 06:30: Batch 185 — night mode: cone headlights, biome-gated windows, real lane-change blinkers

Direct follow-up round on Batch 184's new vehicle lights, 4 separate pieces of feedback in one message.

### Roadside window lights now gated to city/suburb only
"They only should spawn in cities and a few places where there actually can be light... cannot spawn in the meadow or on the beach." Added a per-row `biomeAt(by - roadOffset)` check (the exact same world-offset domain `makeStrip()`/`drawRoadScene()` already use for the ground strips themselves, verified against how they blit `stripBufs`) so window lights only roll in `city`/`suburb` rows — everywhere else (meadow, forest, coast, farm, mountain, river) stays genuinely dark now.

### Headlights are real cones now, not circles
"At the front... it shouldn't be like a ball, the circle, it should be more like a cone, like an ice cream cone." New shared `drawHeadlightCone()` helper: a triangular gradient fill (narrow at the car, widening as it reaches forward) plus a small tight "hot core" at the bulb position for punch. Replaces the plain offset-circle glow for both NPC traffic and the player. Ambulances keep their distinct icy-blue tint, just in cone form now. Taillights stay circular per direct instruction ("at the back they're not the worst") but shrunk a bit (NPC 14→10, player 16→12).

### Lane-change indicator lights — 2 raw pixels, no glow aura
"When the car changes lanes, these lights also emit some light... only 2 pixels would be enough, they only glow as pixels, you don't need to draw an aura." Turned out NPC traffic already has a real, fully-modeled lane-change state machine (`changingState`: none/indicator/moving, plus `targetLane`) that was just never drawn — added `laneChangeDir` (set the moment a lane change is decided, cleared when it aborts or completes) and 2 flat amber `fillRect` pixels (front + rear, on whichever side it's turning toward) while that's active, no gradient. Applies to every lane-changing NPC type (normal traffic changes lanes too, not just `reckless` — `reckless` is excluded anyway since it has no lights at all). Player gets the same 2-pixel treatment, reusing the existing `Player.targetX` lane-snap glide state (`Math.abs(player.x - player.targetX) > 1`) — no new player-side state needed either.

### Also asked about: frequent page refreshes
Flagged as possibly not a game issue. Confirmed by code review: the only `location.reload()` call in the whole file is the dev-menu's RESET ALL PROGRESS button, gated behind its own confirm dialog — nothing in the game auto-refreshes. Very likely something external (an editor live-reload/save-watcher, a browser extension), not this codebase.

**Verification**: live-tested in the Browser pane (same `loop()`-direct-call technique from Batch 184, needed again since this environment's rAF is throttled). Confirmed the headlight cone lights a forward-centered point but NOT a forward point off to the side (proving it's a real triangular cone, not just a smaller circle) — background `[8,13,23]`, cone center `[40,42,44]`, cone-adjacent side `[8,13,23]` (unlit). Confirmed zero window lights across a full-canvas scan at a meadow world-offset vs. real lights at a city one. Confirmed NPC + player blinker pixels light only on the signaling side, both front and rear, and stay unlit on the opposite side. Confirmed ambulance's blue front tint and `reckless`'s total lightlessness (including blinkers) both still hold. 1200-frame regression clean in night mode, 300-frame clean in normal daytime mode.

---

## 2.86.0 — 2026-09-03 06:00: Batch 184 — real front/rear vehicle lights in night mode

Direct request, a tangent off the missions design discussion: "every car, NPC or user's car, needs to have like good working lights ... you can go on and implement the lights on the front and the rear of the car." Night mode previously had one ambient glow centered on each vehicle (Batch 69) — a single warm/blue blob, not distinguishable as a front vs. rear light. Split into a real pair per vehicle: a warm headlight glow at the top edge (front) and a red taillight glow at the bottom edge (rear) — confirmed every vehicle in this game faces the same forward direction the player does (the player's own existing headlight cone already projects toward smaller y = ahead), so front/rear = top/bottom edge for every type, no per-type direction logic needed. Ambulances keep their existing icy-blue front glow (their emergency lighting) instead of the warm amber, now paired with a red taillight like everything else. The player got a matching new taillight too (previously only had the front cone).

**Bonus, from the user's own earlier idea**: `reckless`-type traffic now drives with no lights at all (skips both glows) — "some cars won't have lights from time to time, like reckless drivers." This happened to map exactly onto the existing weaving `reckless` vehicle type already in the game, so it cost almost nothing to add.

**Verification**: rendering happens inside the main `loop()` function, gated behind `requestAnimationFrame` — this environment's Browser pane reports the tab as hidden, which browsers throttle rAF on, so real-time frame sampling returned all-transparent pixels at first. Worked around by calling `loop()` directly (bypasses the rAF scheduler, runs one real frame synchronously). With 2 seeded vehicles (one `normal`, one `reckless`) and night mode forced on: confirmed the normal vehicle's front pixel reads a warm glow `[115,108,88]` and its rear reads red `[119,33,45]`, both clearly brighter than the `[9,13,23]` background; confirmed the reckless vehicle's front/rear pixels stayed indistinguishable from background (no lights); confirmed the player's own new rear taillight renders red. Ran 1200 forced frames with zero console errors (the run ended in a natural crash with no player input, not a bug).

---

## 2.85.2 — 2026-09-03 05:35: Batch 183 — mission CLAIM button height mismatch fixed

Direct question: "why does the claim button for xp mission is different in height than others?" Real bug, not a rendering fluke: the XP claim button reuses `.btn-mint`, which carries `font-size:13px; padding:11px 0` for its OTHER uses elsewhere (RESUME, CLAIM GIFT) — the coin claim button's `.btn-amber` never overrides those, so it stayed at base `.btn`'s smaller `11px`/`10px 0`. Fixed with a scoped `#missionsView .msn-card .btn-mint` override back down to the base size, rather than touching `.btn-mint` itself (which needs to stay bigger at its other call sites).

**Verification**: live-tested in the Browser pane — both mission CLAIM buttons now measure identically (38px tall, 11px font, 10px 0 padding), while `#resumeBtn` (a real `.btn-mint` user elsewhere) still measures its original 13px/11px, confirming the fix didn't leak outside missions. No console errors.

---

## 2.85.1 — 2026-09-03 05:20: Batch 182 — Missions chip redesign, Daily Gift status badge removed

Two pieces of direct follow-up feedback.

### Missions cards: column headers removed, reward chip redesigned
"Remove the both texts at the top: Coin missions and xp missions" — the `XP MISSIONS`/`COIN MISSIONS` column headers (icon + label) are gone entirely, since a bare icon with no caption wouldn't have served any purpose once the text was cut. "For displaying +100 xp remove the square and add 'xp' after the number; also put coin sprite after the number too" — the XP chip's small square icon is gone, replaced with `+100 XP` in one span (same treatment the reward-reveal panel's own XP amount already uses); the coin chip's real coin sprite now sits AFTER the number instead of before it.

### Daily Gift: redundant SEALED/READY/CLAIMED/OPENED badge removed
Direct question, answered by implementing: "is this ... box that says 'Sealed' etc needed? I think that the big button below that is used for claiming is doing that role fine." Agreed — in every state of the TODAY'S GIFT card, the body already communicates status without the top-right badge: the LOCKED strip already says locked, the glowing CLAIM GIFT button already signals ready-to-claim, the claimed box art + "NEXT GIFT IN" countdown already implies claimed, and the reveal panel has its own "GIFT OPENED" kicker. Removed `badgeHtml` and its 4 assignments entirely from `renderDgGiftCard()`. Scoped to the TODAY'S GIFT card only — DAILY WORD's badge carries real info in its in-progress state (`X /Y LETTERS`), not a duplicate status label, so it was left alone. The shared `.dg-badge*` CSS classes stay (still used by DAILY WORD).

**Verification**: live-tested in the Browser pane. Confirmed the missions XP chip renders `+100 XP` with no icon, confirmed the coin chip renders the number then the real coin sprite (canvas paints correctly). Confirmed the column headers are gone from both mission columns. Confirmed no `.dg-badge` element renders in the TODAY'S GIFT card across all 4 states (locked, claimable, claimed-via-forced-state, and the post-claim reveal). No console errors.

---

## 2.85.0 — 2026-09-03 05:00: Batch 181 — Daily Missions screen implemented

Ported a new design doc, `Daily Missions.dc.html`, per direct instruction: new `MISSIONS` button on the main menu (its own 3rd button, separate from the still-inert ACHIEVEMENTS placeholder — that's a different, unscoped future system for permanent badges) opens a new `#missionsView` screen with 6 mission cards (3 XP, 3 coins), a per-category reward ladder (1st claim +100, 2nd +200, 3rd +400 — claiming pays more each time within a category), a segmented 10-block progress bar per card (fixed color ramps, matching the doc exactly), 3 card states (IN PROGRESS / CLAIM / ✓ CLAIMED), a "?" tooltip explaining the ladder, and a footer stat row (MISSIONS DONE / NEXT SET countdown / CLEAN SWEEPS with its own hover tip).

**Direct scope decision**: "for now only do design, you will go over technical stuff when we have actual missions ready." So the 6 missions are the doc's own fixed sample data (SURVIVE 90 SECONDS, CLEAR 8 NEAR MISSES, FINISH 3 RUNS, SCORE 1,200 IN ONE RUN, SMASH 15 CARS, DRIVE 3,000 M) with their `cur`/`goal` values hardcoded exactly as the doc's default "mixed day" state — NOT wired to any real gameplay stat. Claiming works locally (ladder tiers compute correctly, card states update) but doesn't grant any real coins/XP yet, and claimed state is plain in-memory (resets on page reload, same as `dgGiftReveal` etc.) — no persistence, no real daily reset. MISSIONS DONE (148) and CLEAN SWEEPS (9) are the doc's own static demo numbers, also placeholders. NEXT SET's countdown IS real (reuses the same `msUntilMidnight()`/`formatCountdownHMS()` clock math Daily Gift's countdown already uses) since that's plain clock arithmetic, not mission-tracking logic.

Skipped from the doc: the "MOCKUP CONTROLS" day-preview tabs (explicitly marked "NOT PART OF THE SCREEN"), the "CARD STATES — REFERENCE" section (implementer reference, not player-facing), and the "REWARD LADDER"/"VALUES THAT COME FROM GAME STATE" sections (also implementer documentation — their content is folded into the "?" tooltip instead, same as how Daily Gift's own DROP CHANCES tooltip absorbed similar doc annotations).

**Verification**: live-tested in the Browser pane. Confirmed the screen opens/closes cleanly (5 repeated open/close cycles, no console errors, no duplicate tooltip listeners since those are wired once outside the render function). Confirmed the ladder pays +100 then +200 for the 1st and 2nd claims in the same category. Confirmed the coin-mission reward chip paints the real coin sprite (not a flat placeholder square — 208 non-transparent pixels in a 16×16 canvas). Confirmed BACK and Escape both return to the menu. Confirmed responsive layout: 2 columns side-by-side at desktop width, single stacked column with zero overflow at 375px mobile width, matching the doc's own breakpoint spec.

---

## 2.84.5 — 2026-09-03 04:15: Batch 180 — locked-gift redundant score label removed, Missions renamed Achievements

Two small direct-feedback tweaks.

### Locked Daily Gift: removed redundant "SCORE 420" label
Direct feedback: the locked-state body showed the target score three times over (the `.dg-target-label` "SCORE 420" text, the description below it, and the progress bar's own `.../420` readout). Removed the `.dg-target-label` div — the description and bar readout already say the same thing. (The `.dg-target-label` CSS class itself stays; the claimable state's "TARGET CLEARED" label still uses it.)

### Main-menu "MISSIONS" button renamed "ACHIEVEMENTS"
Direct request. It's still the same inert placeholder button (`#missionsBtn`, `.btn-disabled`, added in an earlier batch as an empty placeholder) — only the visible label text changed, not the id or behavior.

**Verification**: live-tested in the Browser pane. Confirmed the locked Daily Gift body no longer contains a `.dg-target-label` element while `.dg-target-sub` and the progress bar still render normally. Confirmed `#missionsBtn` reads "ACHIEVEMENTS". No console errors.

---

## 2.84.4 — 2026-09-03 04:00: Batch 179 — DROP CHANCES footer text removed entirely

Direct follow-up: "from both infos you can remove all the text about recompensation and scaling with level." The `.dg-dc-footer` line (scaling note + duplicate-compensation note, just added in Batch 178) is gone from both TODAY'S GIFT and DAILY WORD panels — now just the title and the sorted rows. The now-unused `.dg-dc-footer` CSS rule was removed too.

**Verification**: confirmed neither panel renders a `.dg-dc-footer` element anymore, rows still render correctly and stay sorted by odds. 1200-frame regression clean.

---

## 2.84.3 — 2026-09-03 03:50: Batch 178 — DROP CHANCES footer text corrected: duplicates ARE possible, and pay coins

Direct correction: "you can get the same paint from the boxes, and get recompensation (I even said how much)." Both panels' footer text claimed "Paint rolls only pick a colour you don't already own" / "Paint and car rolls only pick items you don't already own" — false. Checked `rollReward()` first (code, not just text, per the request) — the actual behavior was already correct and already matches the amounts previously specified in chat: a duplicate colour pays a flat 500 coins (Batch 162), a duplicate car pays 1,000/2,500/5,000/10,000 by rarity (Batch 163/164). Only the copy was wrong. Reworded: "A duplicate colour pays 500 coins instead." (daily) / "A duplicate colour pays 500 coins; a duplicate car pays 1,000–10,000 by rarity." (word).

**Verification**: live-tested in the Browser pane. Confirmed both footer strings read correctly. Confirmed via direct `rollReward()` calls (forced to the color/car tiers with everything already owned) that duplicates genuinely pay exactly 500 coins and the correct rarity-tiered amount, respectively — the code needed no changes, only the text did. 1200-frame regression clean.

---

## 2.84.2 — 2026-09-03 03:40: Batch 177 — main-menu rank name text enlarged

Direct request: "make the name of the rank in main menu bigger (like Bronze X)." `#menuLevelBadge .level-badge-rank` font-size 15px → 22px. Scoped to the main-menu badge only (`#menuLevelBadge`) — the Garage and Stats screens' own level badges share the same base `.level-badge-rank` class but weren't asked for, and stay at 13px.

**Verification**: confirmed the longest possible rank strings ("DIAMOND X" at level 100, "CHAMPION" at level 101+) still fit inside the badge's 96px width at the new size with no overflow. Confirmed the Garage/Stats badges are unaffected. 1200-frame regression clean.

---

## 2.84.1 — 2026-09-03 03:30: Batch 176 — DROP CHANCES rows sorted by odds, highest first

Direct follow-up: "sort the chances by the highest is on top (xp in both cases)." Both `dailyDropChancesTipHTML()` and `wordDropChancesTipHTML()` now build their rows as data (weight/swatch/label/detail) and sort by weight descending before rendering, instead of a fixed hardcoded order — stays correct automatically if the underlying weights are ever retuned again. Both panels currently read XP → COINS → PAINT(→ CAR for word), matching XP being the largest share in both pools right now.

**Verification**: confirmed via the live DOM (`.dg-dc-label` order) that both panels render XP first, then COINS, then PAINT, then (word only) CAR — matching each pool's actual weights descending. Re-confirmed the word-track icon (Batch 175) is still clean via a full-palette scan. 1200-frame regression clean.

---

## 2.84.0 — 2026-09-03 03:20: Batch 175 — the word-track icon's "2 grey pixels" finally traced to their actual source and removed, after 4 wrong rounds

The user's own agent worked out the actual root cause from the design doc's PRE-rotation source (`paintCab()`), which nobody had traced through the rotation math before — this session had only ever compared the doc's own POST-rotation captured pixel grid against the game's copy, never re-derived what each region of that grid actually *represents* in the source's own coordinate space.

### What the pixels actually were
The doc's `paintCab()` draws a 14×22 semi-truck CAB at native size, then applies `translate(0,14); rotate(-Math.PI/2)` before compositing — under that transform, a pre-rotation point (x,y) lands at post-rotation (y, 14-x). Working through that mapping for the doc's own fill calls:
- **The "2 grey pixels"** are the cab's own side MIRRORS — `fillRect(4,10,1,5)` / `fillRect(9,10,1,5)` in the pre-rotation source — which land at post-rotation (x:10-14, y:9) and (x:10-14, y:4): exactly the two 5-pixel-wide horizontal "shading stripe" bands this file's own `drawWordTrackIcon()` already had at those coordinates (previously assumed to be intentional shading, never flagged as removable).
- **The block overlapping the letter-tile frame** is the fifth-wheel plate — the semi cab's trailer-coupling hardware, pre-rotation fills at y:16-21 — which maps to post-rotation x:16-20, spanning nearly the full height. It was never meant to render as part of a compact "cab" icon at all; every batch since 168 had been treating it as legitimate "cargo box" art.

### Fixed at the source, not patched over
Both regions are deleted from `drawWordTrackIcon()` (not just recolored/hidden): the mirror stripe fills are gone and the neighboring shading fills (previously truncated to leave a gap for the mirrors) are widened to close over smoothly; the entire fifth-wheel-plate region and its 3 colors are gone. The canvas itself is narrowed 22→17 (dropping that dead space entirely, matching the cab's own real width) — both the JS call site (`trackCar.width = 17`) and the display CSS (`.dg-word-tiles-car`, 66px→51px, keeping the exact 3×-per-native-pixel scale the height already used) were updated to match, so nothing is stretched or letterboxed.

### Why this succeeded where 4 earlier attempts (Batches 169/170/171) didn't
Every prior round started from the POST-rotation captured pixel grid and either guessed at a location from a screenshot or scanned for anomalies within that grid alone — both approaches can only ever find pixels that look visually "wrong" in isolation, not pixels that are structurally correct art for a DIFFERENT thing (a full semi-truck) wrongly included in a scoped-down "cab only" icon. Re-deriving the SOURCE coordinates and running them through the actual rotation transform is what finally identified two ordinary-looking shading/color regions as extraneous vehicle parts.

**Verification**: live-tested in the Browser pane. Confirmed via a full-palette scan of every pixel in the new 17×14 icon that no stray colors remain and the border closes cleanly on all 4 sides. Confirmed both track-icon DOM sites (in-progress and solved states) render at the new 17×14 native size with the CSS correctly showing 51px display width. 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.83.1 — 2026-09-03 02:50: Batch 174 — XP reveal simplified: no more level-ring icon, "XP" moved inline with the amount

Direct feedback with a screenshot: the XP reveal (`renderRewardReveal()`'s xp branch) showed a level-ring icon (`xpLevelIconHTML()` — the player's current level number + a progress bar toward their next one) that had nothing to do with the reward itself, and "XP" sat on its own small caption line below the big "+750" amount. Removed the level-ring icon entirely (the function is now unused, deleted); "XP" now sits directly after the number inside the same element, inheriting the exact same font, size, and color instead of being a separate smaller line.

**Verification**: confirmed via direct `renderRewardReveal({type:'xp',...})` calls that the output contains no level-ring markup and reads "+750 XP" as one styled unit with no separate caption line. 1200-frame regression clean.

---

## 2.83.0 — 2026-09-03 02:35: Batch 173 — word-completion XP restored (a real overcorrection from Batch 167), colored CAR rarity breakdown, corrected the misleading "single run" gift copy

### Word-tier XP restored — Batch 167 overcorrected
Direct correction: "wasn't the reward supposed to also give XP... I'm talking about the box you can open after getting all the letters... we discussed about it, I even told you how much." Batch 167's fix for "a letter gave almost 20k XP" deleted `xp` from `REWARD_WEIGHTS.word` entirely — but the actual complaint was about the word-COMPLETION reward specifically overshooting, not a reason to remove XP from that pool altogether; xp was always meant to stay there (the already-agreed formula: word's xp = daily's own formula, doubled). Restored to its original weight (`xp: 40`, same as before Batch 167) — under this formula the max possible roll is well under 9,000, nowhere near 20k, so nothing else needed tuning. The DAILY WORD drop-chances panel (Batch 172) gets its XP row back accordingly.

### CAR rarity breakdown recolored
Direct feedback: "the percentages look nicer because they are only separated by the slash, maybe you could use the color and show the percentage." The CAR row's `common 50 / rare 30 / epic 15 / legendary 5` plain-text line is now colored per-rarity using `RARITY_INFO` (the same colors already used for rarity badges everywhere else in the game) with an explicit `%` on each figure — `common 50%` in its own color, `rare 30%` in its own, etc., separated by a dim `/`.

### Daily Gift copy corrected — it was never actually "one run"
Direct feedback: "under the gift it says score X in one run but this is not true because you can score multiple runs... it is supposed to be cleared by how many runs you want to do." Both the code (`todaysBestScore` tracks the BEST across every run played that day, `dailyGiftState()` only needs `lastPlayedDayKey === today`) and the copy disagreed — "SCORE X IN ONE RUN" / "unlocks after a single run clears the target" wrongly implied a single mandatory attempt. Changed to "SCORE X" / "unlocks once any run today reaches the target — play as many runs as you need."

**Verification**: live-tested in the Browser pane (cache-busted URL). Confirmed `REWARD_WEIGHTS.word` has `xp:40` again and `rollReward('word')` can genuinely produce an xp-type reward. Confirmed the word drop-chances panel shows all 4 rows (COINS/XP/PAINT/CAR) with a real XP range. Confirmed the CAR line's HTML contains all 4 `RARITY_INFO` colors with `%` on each figure. Confirmed the locked-state label/subtitle text no longer mentions "one run"/"a single run." 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.82.0 — 2026-09-03 02:10: Batch 172 — DAILY WORD gets its own DROP CHANCES panel; word-track icon headlight tabs restored (that removal was wrong)

### DAILY WORD "?" now shows a real DROP CHANCES panel too
Direct follow-up right after Batch 171 shipped the same thing for TODAY'S GIFT: "can you also add similar '?' next to Daily Word text with its chances?" New `wordDropChancesTipHTML()`, same layout/technique as the daily version, but using `REWARD_WEIGHTS.word` (COINS 50% / PAINT 33% / CAR 17% — no XP row, Batch 167 removed xp from this tier entirely) and `coinRewardRange('word')`. The CAR row shows the real rarity split (`CAR_RARITY_WEIGHTS`, already sums to 100 — common 50 / rare 30 / epic 15 / legendary 5) instead of the doc's own placeholder numbers.

### Word-track icon: the amber headlight tabs are back
Direct correction: Batch 171's removal of the corner amber tabs — guessed at as "the 2 grey pixels" the user kept reporting — was wrong; those tabs are wanted and shouldn't have been touched. Restored exactly as they were. **The actual 2 grey pixels are still unidentified after 4 rounds of chasing this** — per direct instruction, this is now explicitly deferred rather than guessed at a 5th time; see PLAN.md's Daily Gift section for the open item.

**Verification**: live-tested in the Browser pane (cache-busted URL). Confirmed the amber tabs render again (`rgba(255,234,167,255)` at their native coordinates). Confirmed the new DAILY WORD drop-chances panel is hidden by default, shows on hover, hides on leave, and its live content (50%/33%/17%, ranges, rarity split) matches `REWARD_WEIGHTS.word`/`CAR_RARITY_WEIGHTS` exactly. Confirmed the existing TODAY'S GIFT panel still works unaffected. 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.81.0 — 2026-09-03 01:45: Batch 171 — word-track icon corner tabs removed (4th round), Extra Boxes real coin sprite + fixed price formula + real "next box" preview, Daily Gift DROP CHANCES hover panel

### Word-track icon: the actual remaining pixels, finally
Direct follow-up with arrows on a screenshot, after confirming the earlier "still not fixed" reports genuinely weren't a caching issue this time (version number updated, cache-busted URL, opened as a new file — still the same 2 pixels). The arrows pointed at the top-left/bottom-left corners specifically — the small amber "headlight" tabs (`#ffeaa7`, at native (1,2)/(1,3)/(1,10)/(1,11)) transcribed as a vehicle detail in earlier batches, not the border notches Batch 169 already removed. Dropped for the same reason as before: reads as stray pixels at this size, not a recognizable detail.

### Extra Boxes: real coin sprite, correct price formula, a genuine "next box" preview
Four pieces of direct feedback on the same panel:
- **Real coin sprite**: the buy button's coin badge was a plain amber square placeholder (`.dg-boxes-coin`, a styled `<span>`) — swapped for the actual `renderCoinIcon()` sprite every other coin total in the game already uses, on a real `<canvas>`.
- **Price growth formula fixed**: "5% per box" had been implemented as compounding (×1.05 on the current, already-risen price) — the user meant a flat step of 5% of the BASE price (150 coins) added each time: 3,000 → 3,150 → 3,300 → 3,450, not 3,000 → 3,150 → 3,307...
- **"NEXT BOX" label was never actually a preview**: it read the exact same `price` variable the buy button itself displays, so the two numbers were always identical — not a bug in the sense of showing a wrong number, but not a real preview either, and confusing next to a button charging the same amount. Now shows the price of the box AFTER the one about to be bought (`extraBoxPriceAt(opened+1)`), relabeled "AFTER THIS: X" (or "LAST ONE TODAY" for the final box of the day).
- **Hint text reworded**: "Resets at midnight" → "Resets alongside your Daily Gift" (same actual reset mechanism — both key off the same `dayKey()` — just clearer that it's one reset event, not two separate timers), and the price line now states the real flat-150 mechanic instead of "5%."

### Daily Gift: DROP CHANCES hover panel for the "?" icon
Direct request, with a reference image and pointing at the design doc for the exact layout: hovering the "?" next to TODAY'S GIFT now shows a panel (ported from the doc's own tooltip layout — title, per-tier color swatch/label/percent/detail rows, dashed-border footer note) listing the REAL live daily reward-pool odds and ranges — `REWARD_WEIGHTS.daily` (COINS/XP/PAINT, percentages computed live, not hardcoded) and `xpRewardRange('daily')`/`coinRewardRange('daily')` (level-scaling ranges, rounded for display the same way an actual roll rounds). The doc's own mockup showed a 4th CAR row with placeholder numbers — omitted here since `daily` structurally has no car tier at all (a real, deliberate difference decided back in Batch 160, not a fidelity gap). Replaces the old native-tooltip `title` attribute, which only explained the score threshold (still visible elsewhere via the LOCKED-state progress bar).

**Verification**: live-tested in the Browser pane (force-reloaded with a cache-busting query string throughout, per the Batch 170 lesson). Confirmed all 4 icon corner cells are pure black via `getImageData`. Confirmed `extraBoxPrice()` returns exactly 3000/3150/3300 for 0/1/2 boxes already opened today. Confirmed the coin-icon canvas paints real non-blank sprite data. Confirmed the "AFTER THIS" label and the buy button now show two genuinely different numbers. Confirmed the DROP CHANCES panel is hidden by default, appears on `mouseenter`, hides on `mouseleave`, and its live percentages (40/50/10) and rounded ranges match `REWARD_WEIGHTS.daily` exactly. 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.80.1 — 2026-09-03 00:55: Batch 170 — word-track icon: dropped a now-redundant CSS property; the real remaining issue was a persistent stale browser cache

Direct follow-up: after Batch 169's border fix, the user reported "still not fixed" twice, with a screenshot showing arrows at the icon's top-left and bottom-left corners. Pixel-level verification (`getImageData`, full-palette scan) kept coming back completely clean, which didn't match what was being reported — a real mismatch between "what the code produces" and "what's on screen" worth chasing down rather than guessing a third time.

### Root cause found: the Browser pane was serving a stale cached copy strongly enough that even a hard force-reload didn't clear it
Confirmed directly: `getComputedStyle()` on a freshly-created element with the game's own `.dg-word-tiles-car` class kept reporting `object-fit: contain` — a property that had already been removed from the file on disk, and which a plain `fetch(url, {cache:'no-store'})` from within the very same tab confirmed was gone from what the server actually returns. Only a hard cache-busting query string (`?v=...`) on the navigated URL made the live page's own loaded stylesheet match the file on disk. This means the icon rendering the user was actually looking at across the last 2 "still not fixed" reports may have been an old cached version this whole time, not necessarily proof the fixes themselves were wrong.

### `object-fit: contain` removed from the icon's CSS
Now that the icon is a fixed, literal 22×14 graphic (Batch 168) rather than one sized off the player's variable-sized car, its native aspect ratio always exactly matches its 66×42 display box (both reduce to 22:14) — there's nothing left for `object-fit` to actually "fit," and it's a plausible source of a faint interpolation seam at the corners despite `image-rendering: pixelated` (a known rough edge in how some engines combine the two). Dropped in favor of plain width/height CSS scaling, the same technique every other canvas in this file already uses.

**Verification**: confirmed via a cache-busted fetch that the shipped CSS has no `object-fit` declaration for this class at all now (falls back to the browser's own default, `fill` — harmless here since the aspect ratios already match exactly, so `fill` and `contain` produce an identical result in this one case). 1200-frame regression clean. **If this is reported again, check the browser cache FIRST** (try a hard cache-clear, or append a cache-busting query string to the URL) before assuming a fresh code bug — the pixel data itself has now been verified correct twice by two different methods (raw `getImageData` and a full-palette scan) and there is no code-level candidate left unaccounted for.

---

## 2.80.0 — 2026-09-03 00:20: Batch 169 — word-track icon border cleanup, Daily Gift/Word dev-testing shortcuts

### 2 stray pixels in the word-track icon fixed
Direct follow-up right after Batch 168's icon rewrite, with a screenshot: 2 near-black notches (`#111111`, vs. the pure `#000000` used everywhere else in the outline) at the top/bottom edges, right where the cab/windshield sits, read as stray pixels breaking the border rather than an intentional detail. Confirmed by rendering the icon at 20x scale composited against a mock of the neighboring letter-tile frame and inspecting it directly. Dropped the override entirely — those 4 cells (2 top, 2 bottom, symmetric) now fall through to the plain black background fill like the rest of the border.

### Daily Gift/Word dev-menu testing shortcuts
Direct request: "commands that would help with testing the daily gift and daily word." 6 new buttons, none touching anything the real gameplay path doesn't already touch itself:
- **FULFILL SCORE QUOTA** — instantly satisfies today's `dailyScoreThreshold()` gate without playing a qualifying run.
- **RESET DAILY GIFT** — undoes today's claim (clears `lastGiftClaimDayKey`) so the claim→reveal flow can be re-tested same-day.
- **ADD RANDOM LETTER** — same as picking up one real letter on the road, minus the drive.
- **COMPLETE DAILY WORD** — fills every remaining needed letter at once, straight to the word-complete reveal.
- **RESET DAILY WORD** — picks a fresh random word, wipes progress, discards any pending reveal.
- **RESET EXTRA BOXES** — clears today's purchase count/price growth so boxes can be bought repeatedly for testing.

**Verification**: live-tested in the Browser pane. Confirmed all 4 border cells are now pure `#000000`. Confirmed each of the 6 dev buttons produces the exact intended state change (quota fulfilled → `dailyGiftState()` reads 'claimable'; claim → reset → back to 'claimable'; a letter added increments the count by exactly 1; completing a word rotates to a new one, increments `wordsCompleted`, and sets `pendingWordReveal`; resetting the word clears that pending reveal and starts a fresh one; resetting boxes brings the daily quota back to full). 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.79.0 — 2026-09-02 23:10: Batch 168 — Daily Gift text redundancy cut, real "track" icon fixed (was rendering the player's own car, not the doc's fixed truck icon), header streak removed again

Direct follow-up on the Daily Gift screen after Batch 167.

### 3 redundant "come back later" texts cut to 1
The header's static "RESETS 00:00 LOCAL" subtitle, the CLAIMED state's "COME BACK TOMORROW" + "You'll be able to claim again after 00:00." pair, and the CLAIMED state's own "NEXT GIFT IN [countdown]" row were all saying the same thing at once. Direct feedback: "we have one place next gift in, and we don't need like other two texts." Kept only the countdown row; removed the header subtitle and the claimed-state title/sub pair, along with their now-orphaned CSS (`.dg-subtitle`, `.dg-claimed-title`, `.dg-claimed-sub`).

### Word-track "track" icon — real bug, not a copy-fidelity miss this time
"The track is wrong... you put a car and not a track." Investigated properly this time: captured the design doc's actual 22×14 canvas via `getImageData()` (not just its size/position, which is all that had been checked before) and found it's a **fixed, literal blue delivery-van icon — the same icon regardless of which car the player has equipped**, not a render of the player's own selected car at all. The game had been calling `drawCarTileSprite(trackCar, getSelectedCar(), ...)` — the player's actual car — which happened to look plausible for Stock but was never actually the right graphic. New `drawWordTrackIcon()`, transcribed pixel-for-pixel from the doc's own canvas data (22×14 native, black outline + blue cab/windshield + gray cargo box + amber headlights), replaces the `drawCarTileSprite()` call at both track-icon sites (in-progress and solved states). `drawCarTileSprite()` itself is untouched — still used correctly by the Garage grid and leaderboard, where showing the ACTUAL selected/owned car is the whole point.

### Header day-streak removed (again)
Direct repeated instruction: "I told you to remove the day streak in the top right because we already have the streak in the bottom left [the gift card's own STREAK stat tile]." Batch 166 had restored this same element after a screenshot showed the real doc displaying both together — the user's own current, explicit instruction overrides that; the doc showing it twice isn't binding once the user says they don't want the duplication in their own game. Removed the header's flame-icon/streak-number/"DAY" block and its now-orphaned CSS (`.dg-header-streak`, `.dg-day-label`, `.dg-flame-icon`) and the dead `dgHeaderStreak` DOM reference.

### Letter-tile sizing — no change
User initially recalled the tiles being smaller in the doc, then reconsidered mid-message ("maybe when it's less letters, they could be more stretched out... that's not bad at all") and concluded no fix was needed. Left as-is.

**Verification**: live-tested in the Browser pane. Confirmed the header now renders only the title + coin stat (no subtitle, no `dgHeaderStreak` element); confirmed the CLAIMED-state body contains "NEXT GIFT IN" but neither "COME BACK TOMORROW" nor "claim again" text. Confirmed the word-track canvas is now a fixed 22×14 regardless of selected car — tested with Road Train (a long vehicle that previously stretched the old car-based icon) and got exactly 304 opaque pixels (308 total minus 4 transparent corners, matching the transcribed doc art precisely) with a sampled pixel matching the expected blue (`rgb(79,110,247)`) exactly; confirmed both the in-progress (`dgWordTrackCar`) and solved (`dgWordTrackCarSolved`) sites render identically. 1200-frame regression clean. Cleared all test `localStorage` afterward.

---

## 2.78.0 — 2026-09-02 21:40: Batch 167 — 10-item feedback batch: real per-vehicle top speed, ambulance overtake fix, jump generalized to every car, Daily Gift button-color fix, letter reward/spawn fixes, HUD alignment, misc polish

A large grouped feedback dump, worked through batch-by-batch as requested.

### Real per-vehicle top speed — the long-flagged open design item, now implemented
`estimateTopSpeedKmh()`/`CAR_KMH_OVERRIDE` (Batches 140-144) were purely a Garage hover-card display estimate — actual gameplay speed capped at the same global `maxSpeed` for every car regardless of its own listed number. Direct instruction: "you gave cars limits for how fast they can go... but they stop at 200km, you must fix that." New `playerMaxSpeed` (per-run ramp ceiling, set in `launchGame()` from the selected car via `carMaxSpeedInternal()`) replaces the old global `maxSpeed` at the ramp check and in `speedRatio01()` (close-call gap, handling glide speed, screen shake — all now feel proportional to THIS car's own real range). **Never set below the old 200 km/h cap** — only cars whose real listed top speed exceeds 200 (the speed-focused/legendary roster) actually get to reach higher than before; every other car's behavior is byte-for-byte unchanged, zero regression risk for the default Stock car or the ~40 cars capped at/under 200. The score-multiplier's own speed bonus (`liveSpeedRatio`) deliberately keeps using the OLD fixed `maxSpeed` as a shared reference ceiling — a lower-capped car simply can't reach quite as much of that bonus, matching the fairness approach already worked out and recorded in PLAN.md before this was built. `speedToKmh()`'s upper clamp removed so the HUD can genuinely read past 200 up to a fast car's real cap (~250).

### Ambulance no longer feels like "400 km/h" late in a run
Direct feedback: ambulances always looked absurdly fast once `currentSpeed` had ramped up, "like it's going 400 km/h." Real cause found: its overtake speed was `1.5-1.875× currentSpeed` — the SAME proportional scaling that makes the whole game harder late-run, applied a second time on top. Every other vehicle type anchors its relative speed to the fixed `baseSpeed` instead (an existing, deliberate convention) — the ambulance now does too (`1.5-1.875× baseSpeed`, fixed), so it always overtakes at the same real relative speed regardless of how far the run has ramped or which car's own top speed is selected.

### Jump ability generalized to every car (temporary testing measure)
Direct request: "for now every single car... gets bigger, has a shadow, etc... so I can see if other cars are doing it correctly." Real gap found while investigating: the lift/shadow/grow-scale treatment was ENTIRELY inside `drawPixelCar()`'s own `isJumping` branch, called only for the Stock car — every other car's `car.draw()` received no jump state at all, so non-Stock cars never visibly rose off the ground during a jump. New `drawGenericJumpShadow()` (same source-in silhouette technique as the existing stock-only `drawJumpShadow()`, generalized to call any car's own `.draw()`) plus a matching vertical-lift/8%-grow wrapper, applied in `Player.draw()`'s non-stock branch. Thruster-flame art stays Stock-exclusive on purpose (tied to the Garage's BOOST TYPE unlocks, a deliberate scope choice, not a gap) — this is explicitly a stopgap for visual comparison, not the final per-car ability design, per the user's own framing ("some older cars will have different ability later").

### Daily Gift: real button-color bug found and fixed (not a re-copy issue)
Direct, frustrated follow-up: "claim buttons... still don't look the same... why is it so hard to just copy the code into the game?" Re-inspected the design doc's own computed styles directly (not a screenshot guess) — the doc's reveal-panel CLAIM button (all 4 reward types: coins/xp/paint/car) is a specific amber, `#ffb020` (same shade already used for LEGENDARY rarity elsewhere in the game), with dark text. The game had been using plain default `.btn` for 2 of the 4 types and mint `.btn-mint` for the other 2 — neither matches. Fixed with a new `.btn-reveal-claim` class applied to all 4. (The main "CLAIM GIFT" button and the Extra Boxes "BUY" button were re-checked too and are already exact matches — that part really was a faithful copy already.)

### Word-track "truck" icon — real stretching bug
"The truck with letters also isn't right." Real cause: `drawCarTileSprite()` sizes its canvas from the PLAYER's actual selected car's native pixel dimensions, which vary wildly — a long vehicle (Road Train, School Bus, etc.) stretched the icon into a huge sliver instead of the doc's small fixed-size icon. `.dg-word-tiles-car` now locks to a fixed 66×42px box with `object-fit: contain`, so any car sprite scales to fit without distortion.

### Claimed word reward no longer disappears
"When claimed the daily word reward nothing is supposed to disappear... it should still show the reward but with the claim checkmark." Acknowledging a completed word used to jump straight into the new (already-rotated) word's blank progress view. New `dgWordClaimedFlash` holds the just-claimed {word, reward} so it stays on screen — `renderRewardReveal()` gained a `claimed` flag that swaps the CLAIM button for a static `.dg-reveal-claimed-check` checkmark chip instead of reverting the whole card. Reset only when the tab is closed (same convention as the other transient reveal vars).

### Letter pickup no longer spoils the target word
"I got B and it showed TERRIBLE" — every single-letter pickup was showing the FULL target word as its popup subtitle. Now shows collected/total progress (e.g. "3/6") instead, computed from `wordLetterNeeds()`/`wordRemainingLetters()`.

### Word-tier reward no longer rolls XP
Direct feedback after a letter handed out "almost 20k XP": `REWARD_WEIGHTS.word` no longer includes an `xp` tier at all — color/car/coins keep their same relative odds to each other (`pickWeightedKey` normalizes by total automatically). The Daily Gift's own separate `daily` tier (a manual claim, not a road pickup) still rolls xp, untouched.

### Letter spawn frequency + lane fairness
Wait time cut to 70% of the Batch 160 values (42s-84s, was 1-2 min), per direct follow-up ("make them more frequent"). Two real gaps also found and fixed: a letter could spawn into a lane an ambulance was about to occupy (now excluded via the existing `laneReservedForAmbulance()`), and picking a fresh random lane every time let the same lane repeat back-to-back purely by chance, which read as "not really random" — the immediately-previous letter's lane is now excluded from the next pick too (`letterLastLane`).

### HUD alignment + speedometer live nudge
Score chip's top padding now matches the pause-button/energy-bar row's (`10px`, was `15px`); multiplier/speed chips pulled closer underneath (gap `6px`→`3px`). Separately, per direct request: holding Up/Down now nudges the speedometer readout up/down live (`speedToKmh(currentSpeed - player.vVelocity)`) — a display-only effect, the real world-scroll `currentSpeed` (scoring, traffic, everything else) is untouched, and it eases back to the real reading on its own once released via the same friction physics already driving player movement.

### Small direct fixes
Pause menu: Space now actually resumes (was ability-only while paused, despite the hint text already claiming it worked); hint text updated to "SPACE or ESC to resume". Close-call popup's high-speed red brightened (`#e63946`→`#ff3b3b`) — "more noticeable" per direct feedback. High Scores date now includes the year (`en-GB`, added `year: '2-digit'`). Daily Gift's streak panel: "Best ever X days" now wraps onto its own line instead of running on from the sentence above it.

**Verification**: live-tested in the Browser pane (force-reloaded, `localStorage.clear()` before/after). Confirmed Space resumes from pause; confirmed the brightened close-call red; confirmed the HUD top-alignment via `getComputedStyle`. Confirmed the letter-pickup popup shows progress ("1/5") not the target word; confirmed `REWARD_WEIGHTS.word` has no `xp` key; confirmed the new letter-spawn frame counts; confirmed 200 simulated lane picks never landed on an ambulance-reserved lane or repeated the immediately-previous lane. Confirmed all 4 reveal-panel CLAIM buttons render `.btn-reveal-claim`; confirmed the claimed-checkmark state renders with no button and persists the reward through a simulated claim click; confirmed the word-track icon's CSS box is fixed regardless of car. Confirmed 8 different non-stock cars visibly rise (compared top-of-sprite pixel row before/after triggering `abilityState='jumping'`) with no console errors, including a long vehicle (Road Train). Confirmed Stock's `playerMaxSpeed` is byte-identical to the old global `maxSpeed` (zero regression); confirmed a 250 km/h car's ramp genuinely reaches and reports 250 on the HUD; confirmed a sub-200 car still floors at 200; confirmed the ambulance's relative overtake speed stays roughly constant whether spawned at `baseSpeed` or at a car's own `playerMaxSpeed`, instead of scaling with either. Confirmed the Up/Down HUD nudge moves the reading up/down correctly and reverts to the real value at `vVelocity=0`. Ran the full regression pass (`launchGame()` + 800-1200 frames of `loop()`) across 6 different cars (including Stock, a 250 km/h car, Road Train, and a sub-200 car) at both 4 and 10 lanes, plus a fast-car and stock-car pass, all clean. Re-confirmed OWN ALL CARS/COLORS and INVINCIBLE still work correctly post-changes. Cleared all test `localStorage` afterward.

---

## 2.77.0 — 2026-09-02 20:05: Batch 166 — literal copy of the Daily Gift design doc's own art, header streak restored

Direct rejection of Batch 165's attempt: "NO, it is not ok now, just look how designed is what i gave you, can you just copy it over?" Followed by a screenshot of the real READY state, which caught a second mistake in the same batch.

### Header streak restored
Batch 165 removed the header's flame/streak/"DAY" readout on the theory that it duplicated the gift card's own STREAK stat. The user's screenshot showed it's actually part of the real design — restored the HTML/CSS/JS exactly as it was before Batch 165 touched it. The coin-icon size bump from Batch 165 stays (that part was correct).

### Gift-box and reveal icons: canvas replaced with literal divs
Batch 165's `drawGiftBox()` was a canvas redraw of the doc's coordinates at a scaled-down, pixelated resolution — proportionate, but not what "copy it over" meant. The actual design doc renders these as plain positioned `<div>`s at full native precision, no canvas at all. Re-extracted the exact DOM (colors, sizes, transforms) from the doc's own captured states (already pulled earlier this session by driving `daily-gift-standalone.html`'s own mockup toggles in the Browser pane) and transcribed them directly:

- `giftBoxHTML(state)` — 3 fully distinct branches (locked/ready/claimed), not one graphic with a CSS filter as previously assumed. CLAIMED in particular is a structurally different pose (lid rotated -9° via `transform`, a dark "opening" rectangle, no bow) plus a grayscale filter — this corrects a wrong claim in Batch 163's own notes.
- `smallGiftBoxHTML()` — the Extra Boxes row's smaller icon.
- `openedGiftIconHTML()` / `xpLevelIconHTML()` / `paintRevealIconHTML(hex)` — the COINS/XP/PAINT reveal-panel icons, also now literal divs. XP's progress bar is computed from real `allTimeStats.playerXP`/`levelReq()`, not a fixed mockup width. PAINT's glow/swatch color is parametrized by the actual rewarded color via a new `hexToRgba()` helper.

The CAR reveal keeps its canvas (`dgRevealCarCanvas`) — it shows the real, data-driven car sprite via `drawCarSpriteUpright()`, which is legitimate content, not decorative art to copy. `drawGiftBox()`/`drawDgGiftIcon()` and their CSS (`.dg-gift-icon-wrap` and sub-selectors, `.dg-gift-glow`, `.dg-reveal-paint-swatch`) are deleted.

**Verification**: live-tested in the Browser pane (force-reloaded). Confirmed fresh code (`giftBoxHTML` exists, `drawGiftBox` doesn't). Confirmed zero console errors on load. Confirmed LOCKED renders the hazard-stripe gradient with no `<canvas>`; CLAIMED renders the rotated-lid transform with no `<canvas>`; READY carries the `dg-hop` class; the header's streak/"DAY" text is back. Forced all 4 reveal types (coins/xp/color/car) via a temporary `REWARD_WEIGHTS.daily` override — confirmed each renders substantial, type-correct HTML, and that the CAR type is the only one with a `<canvas>` element, which itself paints real non-blank pixel data (646 opaque pixels). Confirmed the Extra Boxes row's `smallGiftBoxHTML()` renders with no leftover canvas reference. 1200-frame gameplay regression clean. Cleared all test `localStorage` afterward.

---

## 2.76.0 — 2026-09-02 19:10: Batch 165 — Daily Gift visual fixes, real gift-box art, dev tools

Direct feedback after actually seeing Batch 163's screen: several things read as genuinely wrong, not just roughable.

### Header cleanup
The coin icon is bigger — switched from `.coin-icon` (14px) to `.coin-icon-lg` (22px), the same class the Garage screen's own header coin total already uses, for consistency. The day-streak readout (flame icon + number + "DAY") that sat next to it is gone entirely — it duplicated the TODAY'S GIFT card's own STREAK stat tile one scroll down, same number in two places.

### Real gift-box art
The gift-box icon "looked so much different" from the design doc — it had been reusing the small on-road present-icon (Batch 150) scaled up, a much simpler shape than the doc's own box. New `drawGiftBox()` ports the doc's actual READY-state box (a lid separate from the body, a full ribbon cross, a proper 2-loop bow) at native pixel scale, using the doc's own absolute coordinates scaled by a constant factor rather than a hand-simplified redraw. Locked/claimed states still reuse this one graphic with a CSS filter, same technique as before (and the same technique the doc itself used).

### The letter-tile "track" was missing entirely
"There is no track" — correct: the design doc always paired the word-progress tiles with a small car icon immediately to their left, reading as "this is the road these were found on." That element had been dropped completely in Batch 163, not simplified — just missing. Restored via a new `.dg-word-tiles-inner` wrapper with a car icon (reuses the existing `drawCarTileSprite()`, the same sideways-rotated sprite the Garage grid and leaderboard already use) leading into the tile strip, in both the in-progress and solved states.

### Dev menu additions
**OWN ALL CARS & COLORS** — grants every car and every color at once (plus marks them discovered), a testing shortcut for reaching the "everything owned" state Extra Boxes' duplicate-compensation path needs, per direct request ("so I can test the additional boxes"). **INVINCIBLE: OFF/ON** toggle — while on, touching any vehicle (including ambulances) is a harmless no-op, no explosion/`endRun()`/coin credit, gated at both crash branches in the vehicle-collision loop.

**Verification**: live-tested in the Browser pane (force-reloaded). Confirmed the header's streak readout is gone and the coin icon uses the bigger class; confirmed the gift-box canvas renders a real multi-part shape (647 opaque pixels of a 1024px canvas, not a near-empty placeholder); confirmed the word-track car icon renders at the expected tile-sprite dimensions; confirmed OWN ALL grants every car/color in one click; confirmed INVINCIBLE actually blocks a forced crash while on and restores normal death behavior once toggled back off; confirmed a forced Extra Box purchase with everything owned correctly shows a duplicate-compensation reveal. 1200-frame regression pass clean. Cleared all test `localStorage` afterward.

---

## 2.75.1 — 2026-09-02 18:40: Batch 164 — car-duplicate compensation no longer scales with level

Direct correction: "recompensation won't scale." Batch 163's first-pass +50%-by-level-100 linear curve on `carDuplicateCompensation()` is gone — the 4 rarity amounts (1000/2500/5000/10000) are flat now, same at every level.

**Verification**: live-tested in the Browser pane — confirmed the same rarity amount is returned at level 1, 100, and 500. 800-frame regression pass clean. Cleared test `localStorage` afterward.

---

## 2.75.0 — 2026-09-02 18:30: Batch 163 — Daily Gift tab implemented for real, ported from the user's own design doc

The full Daily Gift/Daily Word screen, previously logic-only (Batch 149), now has a real UI — ported from "daily-gift-standalone.html," a design doc the user built and handed over complete with mockup-control toggles for every state. Extracted every state (gift LOCKED/CLAIMABLE/CLAIMED/REVEAL×4 reward types, word IN-PROGRESS/COMPLETE) by driving the doc's own state toggles live in the Browser pane and reading the rendered DOM, plus the doc's actual `drawToken()` source for the gold-token letter art.

### New screen
`#dailyGiftView`, wired to the previously-disabled `#dailyGiftBtn` (Batch 122 placeholder). Two cards: **TODAY'S GIFT** (score-gated, matches the existing `dailyScoreThreshold()`/`canClaimDailyGift()` logic exactly — new `dailyGiftState()` maps it to locked/claimable/claimed) and **DAILY WORD** (letter tiles reflecting real `wordLetterCounts`, a progress bar, and — new — **EXTRA BOXES**, the paid-gift-box feature discussed across several earlier batches, built for real now rather than deferred further, per direct confirmation).

### New tracking needed for the UI to have anything to show
`allTimeStats.todaysBestScore` (+ its own day-key) — the existing threshold logic never tracked a per-day BEST score, only whether a run cleared it; the locked state's progress bar needed partial progress before the target clears. `allTimeStats.pendingWordReveal` — word completion happens passively on the road (`collectWordLetter()`, unchanged, still rotates instantly), but the tab needs to show a "just solved" reveal whenever it's NEXT opened, however much later that is — stashed persistently at the moment of completion (before the word rotates), cleared only once acknowledged in the tab.

### Extra Boxes — built with the real numbers, not the mockup's placeholders
The doc's own price (2,500 current / 5,000 next, a flat 100% double) and copy ("same drop table as the daily gift") were both placeholder/wrong — checked against what was actually worked out in chat and fixed: **3,000 coins base, +5% per box opened today** (`EXTRA_BOX_PRICE_GROWTH`), **quota = `floor(playerLevel/10)` per day** (section hidden entirely below level 10), and rolls from the **word-tier pool** specifically, not daily's — daily has no car slot at all (Batch 160), so "same as daily gift" would have made this feature pointless for its actual purpose (helping complete the car collection).

### Gold-token letter pickups
`drawGoldToken()`, ported from the design doc's own `drawToken()`, replaces the flat gold-square placeholder from Batch 149. The doc drew on a 5× supersample grid (it's an oversized design study); the real game draws every sprite at native pixel scale with `image-rendering:pixelated` doing the upscaling, so this ports the same bevel algorithm at bevel-unit `u=1` instead — consistent with how every other sprite in the game is already drawn, not a downgrade. Size (18px) and skin ("gold token," one of 6 studied in the doc) per direct instruction after reviewing the doc's own size/skin comparison panels.

### Car-duplicate compensation, updated to the finalized rarity-tiered amounts
Caught while writing this entry: Extra Boxes' price/quota were built with the real numbers, but the car-duplicate REWARD formula itself was still Batch 160's `unlock*0.5` — the finalized flat rarity amounts from the same chat (common=1000, rare=2500, epic=5000, legendary=10000) were never actually wired in. Fixed — `carDuplicateCompensation()` replaces `unlock*0.5` everywhere (both the free daily/word rolls and Extra Boxes share one formula, resolving the "still unresolved" scope question from PLAN.md the simplest way: one rule, not two). Confirmed to scale with level per direct decision, but no exact per-level rate was ever given — shipped as a first-pass +50%-by-level-100 linear scale (same "modest growth, capped at 100" shape as the rest of this reward system), clearly flagged for retuning once a real number comes in.

### Known simplifications versus the doc (flagged, not hidden)
The doc's gift-box icon is ~14 absolutely-positioned divs per state; reused the existing `drawPresentIcon()` (Batch 150) scaled up instead, with CSS `filter: saturate()/grayscale()` per state — matches the doc's OWN technique (it reused one base graphic with CSS filters too, just building the base graphic differently). Dropped the doc's "unclaimed rewards are lost at midnight" copy — doesn't reflect how this is actually built: `claimDailyGift()`/`collectWordLetter()`/`buyExtraBox()` all grant the reward atomically the moment the action happens, there's no real "unclaimed and at risk" state to warn about.

**Verification**: live-tested in the Browser pane (force-reloaded throughout, per the Batch 159 stale-cache lesson). Confirmed all 3 gift states render correctly and transition properly (locked→claimable via a real qualifying run→claim→reveal→dismiss→claimed with a live countdown); confirmed word letter tiles reflect real collected-letter state; confirmed a full word completion persists its reveal across closing and reopening the tab, and dismissing it correctly clears `pendingWordReveal`; confirmed Extra Boxes are hidden below level 10, show the correct quota/price at level 15/25, deduct exactly 3,000 coins per purchase (isolated from the reward's own possible coin payout, which had initially looked like a bug in a naive before/after coin-delta check until traced to the reward system working as designed), and the price compounds 5% correctly. Gold-token pickups spawn and collect with zero errors. Confirmed `carDuplicateCompensation()` matches the finalized amounts exactly (1000/2500/5000/10000 at level 1, 1500/.../15000 at level 100, capped beyond that) and an end-to-end forced car-duplicate roll applies it correctly. Full 1200-frame gameplay regression clean (twice — once before this fix, once after). Cleared all test `localStorage` afterward.

---

## 2.74.2 — 2026-09-02 17:45: Batch 162 — paint duplicate compensation simplified to a flat 500 coins

Direct instruction, supersedes Batch 160's scaling-XP idea entirely: "make it give five hundred coins as recompensation." `rollReward()`'s color-duplicate branch now grants a flat 500 coins (`{ type: 'coins', amount: 500 }`) instead of the level/tier-scaled XP payout — no formula, no scaling.

**Verification**: live-tested in the Browser pane (force-reloaded) — forced a color-only roll with every gift-tier color pre-owned, confirmed the result is exactly `{type: 'coins', amount: 500}` and `allTimeStats.totalCoins` increases by exactly 500. 1200-frame regression pass clean. Cleared test `localStorage` afterward.

---

## 2.74.1 — 2026-09-02 17:30: Batch 161 — 3 direct bug fixes: Prism live preview, leaderboard sprite color, music mute/unmute

### Prism wasn't visibly cycling in the Garage
`drawGaragePreview()` only ever ran on-demand (opening the Garage, picking a swatch) — a color that changes over TIME with no user action never got redrawn in between. `loop()` (already running continuously via `requestAnimationFrame` regardless of which screen is open) now redraws the Garage preview every frame specifically while the Garage is open AND Prism is equipped — cheap and gated, no cost the rest of the time.

### Leaderboard car sprites now always show a fixed default color
Direct feedback: "in scores what about the cars color, maybe all should have default color." `drawCarTileSprite()` gains an optional `colorOverride` parameter (falls back to `resolvePlayerColor()`, i.e. unchanged, when omitted); the leaderboard's call site now passes the new `DEFAULT_PLAYER_COLOR` constant (Blue) explicitly. Fixes 2 things at once: a list of past runs no longer shows TODAY's live equipped color (which was never actually what that historical run was driven in), and a Prism-equipped player's leaderboard no longer shows an animating rainbow sprite next to every entry. The Garage's own tile-grid caller is unaffected — still shows the real equipped color there, where it belongs.

### Music silent forever after dragging the volume slider to 0% and back up
Real bug, matches a pattern already fixed once for the mute BUTTON (Batch 125) but missed on the slider path: `musicTick()`'s self-rescheduling loop fully stops once `config.soundEnabled` goes false, and flipping the flag back to `true` alone doesn't resume it — `startMusic()` has to be called explicitly. `syncVolumeUI()` now does exactly that on the false→true transition (gated on `gameActive`, same guard the button's own fix already used).

**Verification**: live-tested in the Browser pane (force-reloaded). Confirmed the Garage preview canvas actually changes between two `loop()` ticks a beat apart while Prism is equipped and the Garage is open; confirmed `drawCarTileSprite()` accepts and uses a color override with zero errors; confirmed `syncVolumeUI('sound', 0)` disables sound and `syncVolumeUI('sound', 0.6)` right after correctly re-enables it AND restarts the music timer (was previously left stuck disabled). 1200-frame regression pass clean. Cleared test `localStorage` afterward.

---

## 2.74.0 — 2026-09-02 17:00: Batch 160 — reward system fully re-specified with real formulas, letter timing widened to 1-2 min

Direct request with concrete formulas for both reward tiers, replacing the Batch 149 placeholder ranges entirely.

### Letter spawn timing
`LETTER_SPAWN_MIN/MAX_FRAMES` widened from 30-60s to 1-2 minutes, per direct instruction: "word reward will be big so it shouldn't be too easy."

### Reward weights — daily gift no longer includes cars at all
`REWARD_WEIGHTS.daily = { xp: 50, coins: 40, color: 10 }` (was `{coins, xp, color, car}`) — cars are word-reward exclusive now. `REWARD_WEIGHTS.word = { color: 20, car: 10, xp: 40, coins: 30 }`.

### XP/coin amounts — real formulas, not flat ranges
Both scale with player level: lower limit grows a flat amount per level (`+25 XP`/`+5 coins`), upper limit is always `lower × 1.5`. Base (level 1): XP 500-750, coins 100-150. Word-tier amounts are the daily formula's result doubled (`REWARD_WORD_MULT=2`, per "boosted, maybe times two"). Scaling stops at player level 100 (`REWARD_LEVEL_CAP`) — a level-500 player gets the exact same range as a level-100 player, not something that keeps climbing forever. XP amounts round to the nearest 10 (`roundTo10`); coins round UP to the nearest 10 (`ceilTo10`) — a deliberate distinction per the spec's own wording ("rounded to" vs "rounded up to").

### Duplicate compensation — now type-specific, not a flat coin range
Direct decision after discussing the tradeoff (keep the reward pool including owned items + compensate, vs. shrink the pool to only-unowned-things at correspondingly worse odds) — compensation was chosen, reasoning: a big win still feels good even on a dupe, and the alternative doesn't actually solve the "eventually you own everything" problem either. A duplicate **color** now compensates with XP — "still a large number," implemented as 2× that roll's own top XP-reward value — instead of coins. A duplicate **car** compensates with coins ≈ half its own unlock price ("later of course you won't be able to buy it" — this becomes the ONLY thing a maxed-out collection ever gets from a car roll), which naturally scales with the specific car's rarity/value with no separate formula needed. The old flat `REWARD_DUPLICATE_COINS_RANGE`/`duplicateToCoins()` are gone, replaced by inline per-branch compensation.

**Verification**: live-tested in the Browser pane (force-reloaded to rule out the stale-cache issue found in Batch 159). Confirmed `xpRewardRange()`/`coinRewardRange()` produce exactly the specified numbers at levels 1 and 10 for both tiers; confirmed the level-100 cap makes level 100 and level 500 produce identical ranges; confirmed `daily` has no `car` key while `word` does; confirmed 200 rolls all round correctly (XP to nearest 10, coins up to nearest 10); confirmed a duplicate color/car roll (with every item pre-owned) applies the exact formula value in an isolated single-roll test — an earlier loop-based test appeared to mismatch until traced to `gainXP()` raising the player's level mid-loop from EARLIER rolls' own XP rewards, which is expected/correct behavior, not a bug. 500+500 mixed rolls and a 1200-frame regression pass both clean. Cleared test `localStorage` afterward.

**Not built this batch — floated ideas, not yet scoped**: user asked "how expensive would daily-gift boxes be" for a proposed late-game system (once every car is coin-bought, let players buy extra gift rolls directly with coins). Recommended ~3,000 coins per box as a first-pass anchor (roughly a mid-epic car's price) in chat, but this is a genuinely separate feature (needs its own claim-gating logic, UI entry point, and probably its own confirm flow) — not implemented, pending a decision on whether/when to build it.

---

## 2.73.4 — 2026-09-02 16:20: Batch 159 — result screen: hide 0-count rows, clearer "CARS JUMPED OVER" label

Direct feedback: "if there were no close calls, don't show this line, and same with jumped over... change 'jumped over' to 'cars jumped over' so it's clearer." `showResultScreen()`'s CLOSE CALLS row (new `#goCloseCallRow` id, previously untargetable — the row div had no id, only its inner spans did) now hides itself when `closeCalls === 0` instead of showing "0× CLOSE CALLS". The ability row already hid itself when no ability was equipped at all (Batch 125) but NOT when an ability was equipped and simply never used that run (e.g. jump equipped, 0 actual jump-overs) — now also hidden in that case, on both the jump and ram branches. "JUMPED OVER" relabeled to "CARS JUMPED OVER".

**Verification**: live-tested in the Browser pane via a real forced crash (so `CS.snapshot` is populated by the genuine `endRun()` path, not a hand-built stub) then manipulating specific fields and re-calling `showResultScreen(true)` for each case: 0 close calls + 0 jumps → both rows hidden; 3 close calls + 5 jumps → both visible with correct text ("3× CLOSE CALLS", "CARS JUMPED OVER" / "5"); ram equipped with 0 rams → hidden; ram equipped with 4 rams → visible ("RAMMED" / "4"). 1200-frame regression pass clean. Cleared test `localStorage` afterward.

**Process note, not a code issue**: mid-verification, the Browser pane served a STALE cached copy of `carCrash.html` on a plain `navigate()` call — confirmed by checking for `#goCloseCallRow` and finding it missing despite the file on disk being correct. Fixed by re-navigating with `force:true`. The file itself was never wrong; this only means the two immediately-preceding small batches (157/158, the shadow offset tweaks) were verified only by "zero errors," not by checking the actual new values, so if the same caching issue affected THAT verification, it wasn't caught. Re-ran both checks after the forced reload in this batch and confirmed the Batch 158 altitude-tracking formula is genuinely live in the served file. **Going forward: prefer `force:true` (or a fresh `preview_start`) when a test's very first check doesn't include something that would only be true post-edit** — a plain `navigate()` isn't reliably enough on its own in this environment.

---

## 2.73.3 — 2026-09-02 16:00: Batch 158 — jump shadow now tracks altitude instead of a fixed offset

Direct feedback: "when the car starts jumping and going up, the shadow stays in its place... make it so when jumping, the shadow slowly also goes a little bit more to the back. It starts under the car and goes to the back, and when the car lands the shadow goes back under the car." The 2px offset from Batch 157 was a flat constant regardless of height — `drawJumpShadow()`'s `shiftDown` is now `heightRatio * maxShift` (`maxShift=5`, using the same `heightRatio` already driving the alpha fade): 0 at liftoff (shadow directly under the car), growing to 5px at peak height, shrinking back to 0 on landing. `maxShift=5` was picked to land close to the already-approved "just a little bit" feel at a typical mid-jump height, not introduce a new magnitude.

**Verification**: live-tested in the Browser pane — ran a full simulated rise-and-fall arc (`flightHeight` 0→40→0) with zero errors, plus an 800-frame regression pass. Cleared test `localStorage` afterward.

---

## 2.73.2 — 2026-09-02 15:50: Batch 157 — jump shadow offset tuned down, was too far shifted

Direct follow-up right after seeing Batch 156's full-size shadow: "too much shifted to the back... should be just a little bit." `shiftDown` in `drawJumpShadow()` halved, 4→2px.

**Verification**: live-tested in the Browser pane — 200 frames jumping and an 800-frame regression pass both clean, zero errors. Cleared test `localStorage` afterward.

---

## 2.73.1 — 2026-09-02 15:40: Batch 156 — 2 direct fixes: single-button info dialogs, jump shadow drawn full-size

### Confirm dialog: no Cancel button when there's nothing to actually confirm
Direct feedback on the gift-only paint message: "no need for two buttons cancel and ok, just leave the ok." `showConfirm()`'s Cancel button now hides itself whenever the dialog has no real confirm action (`onConfirm` is null) AND OK isn't disabled — covers the gift-only color message and the Prism-locked message. The "NOT ENOUGH COINS" dialogs (both cars and colors) keep both buttons, since there OK is deliberately shown disabled (to preview "here's what you'd click if you could afford it") and Cancel is the only way to actually dismiss.

### Jump shadow: drawn at full size instead of squashed down small
Direct feedback with a screenshot: "why is it so small... it should always be like the size of the car, but shifted a little bit to the back." Batch 154's shadow was vertically squashed to 40% height, anchored at the ground-contact point — reasonable in theory, but combined with Batch 152's 8% scale-up on the car itself, it read as a car with a tiny shrunken blob under it, not a shadow. Removed the squash entirely: `drawJumpShadow()` now draws the exact same full-size silhouette image the car itself uses, just shifted down 4px from the ground position — enough on its own to suggest an overhead-and-slightly-forward light source without shrinking anything. The height-based alpha fade is unchanged.

**Verification**: live-tested in the Browser pane — confirmed the gift-only dialog hides Cancel while the not-enough-coins and real-buy dialogs both keep it; confirmed the shadow canvas itself is unchanged at 16×26 (the same full car-silhouette size as before, just no longer squashed when drawn); 200 frames jumping and an 800-frame regression pass both clean. Cleared test `localStorage` afterward.

---

## 2.73.0 — 2026-09-02 15:20: Batch 155 — 3-tier color economy, Grey, purchase-feedback parity, and a level-100 cycling Prism color

Direct request to think through the color roster and how it's earned. Landed on a concrete 3-tier split rather than trying to rank the existing 9 non-default colors by "how good they look" (they're all fine — the split is about exclusivity, not quality):

### Tiers
`GARAGE_COLORS` gets a `tier` field: **free** (Blue, the one starter, unchanged), **buy** (Red/Cyan/Gold — coin-purchasable ONLY, 80/180/250, never handed out by the Daily Gift/Word reward pool), **gift** (Green/Orange/Purple/Pink/White/Navy + new **Grey** — Daily Gift/Word reward ONLY, cost is meaningless and set to 0). `rollReward()`'s color tier now filters on `tier === 'gift'` specifically — it used to be "any non-free color," which incorrectly let the 3 buy-tier colors leak into the free reward pool too. Black was considered and deliberately skipped, per direct second-guess in the same message.

### Purchase-feedback parity (colors now match what cars already did)
Turned out cars already had exactly the UX being asked for (Batch 90: click a locked-but-unaffordable car, see "NOT ENOUGH COINS — need X more" with the buy button disabled) — colors just never got the same treatment and silently did nothing on an unaffordable click. `renderColorPicker()`'s click handler is now a 3-way branch matching `buildCarTile()`'s: owned → equip, gift-tier → "can only be earned through the Daily Gift or a Daily Word reward," buy-tier unaffordable → "NOT ENOUGH COINS," buy-tier affordable → the existing buy-confirm dialog.

### Prism — level-100 cycling color
A 12th swatch, unlocked at player level 100, that slowly cycles hue instead of being a fixed color ("changing slowly colors, not very fast, but very slowly" — one full rotation every 12s). Represented as a `'PRISM'` sentinel string for `playerColor` rather than a real hex, since the rest of the color system assumes static values. New `resolvePlayerColor()` is now the ONLY correct way to turn `playerColor` into an actual canvas fillStyle — swapped in at every real rendering site across the file (live gameplay for both stock and non-stock cars, the Garage Showroom preview, hover-card/tile-grid sprites, the menu's background demo car, crash explosion particles and the wreck's stored color). The picker itself shows a static rainbow-gradient swatch rather than animating the tiny UI element — not worth a separate render loop for something that small.

**Verification**: live-tested in the Browser pane (page reloaded between checks to avoid stale in-memory state from prior tests). Confirmed all 11 colors have the correct tier; clicking a gift-tier swatch shows the right message with zero side effects (no coins spent, nothing equipped); clicking an unaffordable buy-tier swatch shows the exact coins-needed amount; a real purchase deducts coins/grants ownership/equips correctly. 300 simulated `rollReward('daily')` calls produced zero buy-tier color leaks into the reward pool. Confirmed Prism is genuinely locked (click shows "PRISM — LOCKED," no equip) below level 100 and equips correctly at level 100+; confirmed `resolvePlayerColor()` returns a real `hsl(...)` string that changes between two calls a beat apart; confirmed zero errors across 200 frames jumping (shadow+flame+scale-up all still render fine with an HSL fillStyle), a non-stock car equipped, a forced crash sequence, and an 800-frame regression pass. Cleared all test `localStorage` afterward.

---

## 2.72.0 — 2026-09-02 14:40: Batch 154 — jump drop-shadow is back, derived from the real sprite instead of hand-drawn

Follow-up to Batch 152's experiment: user proposed a different technique for the shadow that was removed in Batch 116 for looking mismatched — instead of hand-drawing a shape per car, take the sprite that's already being drawn, recolor it flat black/translucent via canvas compositing, and use that directly as the shadow. Implemented via `drawJumpShadow()`: draws the car body to a small offscreen canvas, then `globalCompositeOperation = 'source-in'` fills only the pixels the sprite actually painted with flat black — automatically the exact right silhouette for whatever's drawn, no per-car math, so the old width-mismatch bug can't recur. Squashed vertically (flat, anchored to the ground-contact point so it doesn't shift as it squashes) and fades — not shrinks — as flight height increases.

Scoped per direct instruction: player's stock car only (drawPixelCar is already exclusively the stock sprite — no separate gating needed), only while actually jumping, and explicitly NOT during the crash sequence — the wreck's own draw call always passes `isJumping=false`, so this was already structurally guaranteed rather than needing a new check.

**Verification**: live-tested in the Browser pane — confirmed the offscreen shadow canvas (16×26, matching the 14×24 sprite plus padding) contains a real non-empty silhouette (332 opaque pixels) after a simulated jump; confirmed 200 frames airborne, landing, and an 800-frame regression pass all run with zero errors. Cleared test `localStorage` afterward.

---

## 2.71.2 — 2026-09-02 14:20: Batch 153 — real miss caught: jump's energy threshold wasn't actually "one orange bar"

Direct feedback: "you can jump once you have at least one orange bar." Checked the ability bar's own `cellColor()` math (10 cells, red for the first 3, orange from cell 3 through 6, green after) — `JUMP_MIN_ENERGY` was 30, exactly the red/orange BOUNDARY (3 full red cells, zero orange lit yet), not actually reaching into orange. Batch 117 had intended exactly this ("three or more bars... at least one orange bar") but the two phrasings don't land on the same number — 30 satisfies "three bars," not "one orange bar." Raised to 40, the energy level at which the first orange cell is genuinely fully lit. The "ready" glow (tied to the same constant already) updates automatically, no separate change needed.

**Verification**: live-tested in the Browser pane — confirmed `useAbility()` refuses to jump at 39% energy and succeeds at exactly 40%. Cleared test `localStorage` afterward.

---

## 2.71.1 — 2026-09-02 14:05: Batch 152 — jump gets a slight scale-up while airborne (experimental, pending user's verdict)

Direct feedback after seeing Batch 151's thrusters live: "the car looks more like it is accelerating rather than jumping/flying." Discussed a couple ideas (a proper shadow vs. a subtle scale-up); user asked to try the smaller one first. `drawPixelCar()`'s `isJumping` branch now scales the whole sprite (body + flame together) up 8% — flat, not height-scaled — around the car's own center, so it grows in place rather than shifting position. **Explicitly a "let me look and decide" experiment, not a settled decision** — the shadow idea is still on the table if this alone doesn't read as "lifted off the ground."

**Verification**: live-tested in the Browser pane — confirmed the jumping branch runs error-free across 200 simulated frames, confirmed landing (isJumping→false) draws normally afterward with no leaked transform (the scale is applied and reverted within `drawPixelCar()`'s own existing save/restore, no new state introduced), 800-frame regression pass clean. Cleared test `localStorage` afterward.

---

## 2.71.0 — 2026-09-02 13:45: Batch 151 — Jump thruster flames replace the wings, 3 unlockable types

Direct request, following up on an earlier brainstorm about the jump ability's wings not landing visually: implement a design doc ("Jump Thrusters.dc.html") ported directly into the game, replacing the wings entirely. Explicitly scoped to the STOCK car only for now — "for now maybe only the default car bc then you would have to adjust the model for each car, and some of them won't even have that ability" — which happens to match the wings' own pre-existing scope exactly (every other Garage car already had no jump-visual at all, so nothing lost coverage).

### 3 flame types, ported algorithmically from the design doc
Not a static sprite swap — the doc's actual procedural drawing code (tapered pixel "plume" with a 6-stop color ramp, a 4-frame flicker loop where each frame has 3 random shape alternates re-rolled once per full cycle so the loop never repeats identically, occasional left/right mirroring): **Underglow** (twin plumes under the rear wheels, no added width), **Rocket Pods** (side canisters on the old wing footprint, each with its own plume), **Center Thruster** (one long centered plume). Ported as `drawFlameFx()`/`drawFlamePlume()`/`flameRamp()`/`flameAlts()`. The mockup's `setInterval`-driven frame timing was replaced with a real-elapsed-time check (`updateFlameFx()`, 80ms/frame) so the flicker speed stays constant regardless of the game's actual frame rate, instead of a separate timer.

### Unlocking (3 different mechanisms, all direct decisions)
Underglow is free from the start. Rocket Pods unlocks automatically at player level 51 (no purchase). Center Thruster costs 10,000 coins, bought the same way as a paint color (confirm-dialog, `buyFlameType()`). New Garage "BOOST TYPE" section (`#flamePicker`) sits right below the paint swatches, same visual language (locked items get the same hazard-tape stripe as locked colors, not a lock icon).

### Hover-to-preview
Hovering a BOOST TYPE swatch shows that flame type animated on the Showroom's own preview canvas — but always drawing the STOCK car specifically (`drawFlamePreview()`), regardless of which car is actually equipped, since only the stock model has thruster art. Moving the mouse away reverts to the normal idle preview of whatever's really equipped.

**Verification**: live-tested in the Browser pane. Confirmed ownership logic at levels 1/51, confirmed a locked swatch can't be bought without enough coins and correctly unlocks/deducts coins once affordable, confirmed clicking a locked (level-gated) swatch does nothing (no confirm modal, no equip). Confirmed the hover-preview interval starts/stops cleanly for all 3 types with zero errors. Confirmed the REAL in-game jump flame renders with zero errors across 340 simulated frames while airborne, including switching flame types mid-jump. A 1200-frame unattended regression run (normal random play) completed with zero errors. Cleared all test `localStorage` afterward.

---

## 2.70.1 — 2026-09-02 13:00: Batch 150 follow-up — score threshold rounded to the nearest 10

Direct request: "as for score threshold make it round up to 10 so like 710, 740, 850 etc." `dailyScoreThreshold()` now wraps its result in `Math.round(x / 10) * 10` — every level's requirement always reads as a clean multiple of 10 instead of whatever the raw `400 + (level-1)*8` arithmetic happens to land on.

**Verification**: live-tested in the Browser pane — checked levels 1/2/3/5/10/25/39/50/100, all outputs land on a multiple of 10 (400, 410, 420, 430, 470, 590, 700, 790, 1190). Cleared test `localStorage` afterward.

---

## 2.70.0 — 2026-09-02 12:45: Batch 150 — direct follow-up on Batch 149: score threshold retuned, word list expanded, letter alert redesigned

Three direct pieces of feedback after seeing Batch 149's numbers/visuals:

### Score threshold: lower and much flatter
"Make it less for level one (it should take like 2 mins max to get the score req), and it should scale slower, much slower." An invincible-player harness measurement (`checkCollision` stubbed out for the test only) at default settings — 4 lanes, "reckless" difficulty — hit ~4790 score in a full simulated 2 minutes, meaning a real, imperfect player clearing the old 700-at-level-1 threshold could easily run past 2 minutes. `dailyScoreThreshold()` lowered from `700 + (level-1)*50` to `400 + (level-1)*8` — the level-1 anchor drops to a comfortably-inside-2-minutes 400, and per-level growth is ~6x flatter (level 50 now needs 792, not 3150).

### More words, capped at 6 letters
`DAILY_WORDS` expanded from 16 to 40 entries. REDLINE/ASPHALT/HIGHWAY (7 letters each) were dropped for exceeding the new cap; 27 new racing/road-themed words added (FUEL, GEAR, RACE, TRACK, APEX, SKID, MOTOR, CHASE, SPRINT, CLUTCH, CHROME, FENDER, MIRROR, CRUISE, COUPE, SEDAN, WAGON, TROPHY, FINISH, CORNER, STREET, BUMPER, SIGNAL, MERGE, TUNNEL, BRIDGE, STALL).

### Letter pre-warning: present icon, not an ambulance-style flash
"The letter road alert mustn't be the same as ambulance — it should be a present icon." The full-lane flashing gold stripe (visually the same TREATMENT as the ambulance's red danger-flash, just recolored) is gone entirely. New `drawPresentIcon()` draws a small pixel-art gift box (red body, gold ribbon cross, gold bow) that gently bobs near the top of the target lane, with the incoming letter shown just below it — a genuinely different visual language, not a palette swap of the ambulance's.

**Verification**: live-tested in the Browser pane. Confirmed `dailyScoreThreshold()` at levels 1/10/50 (400/472/792); confirmed `DAILY_WORDS` has 40 entries, max length 6, no duplicates; confirmed the present-icon pre-warning renders and correctly hands off to a real letter pickup after its countdown with zero errors; a 1200-frame unattended simulated run (default random traffic + letter spawns) completed with zero errors. Cleared all test `localStorage` afterward.

---

## 2.69.0 — 2026-09-02 12:10: Batch 149 — Daily Gift / Daily Word system (logic only, no menu UI yet)

Direct request: "add daily gift... in this tab there will also be a daily word section, you find letters on the road, pick them up and when collected all you receive a better reward, we need a working system." Explicitly scoped to LOGIC only — "don't do the tab, just logic, I'll give you the design when you give me the logic" — so this is the full data model, reward math, and real on-road gameplay for finding letters, with no menu/tab screen wired up yet (the existing `#dailyGiftBtn`/`#missionsBtn` placeholders from Batch 122 are untouched).

Several open design forks were resolved via direct answers before implementing (see the AskUserQuestion round in this session): the daily-gift streak reuses the existing `currentStreak`/`lastPlayedDayKey` tracking rather than a separate claim-only streak; the daily word uses an exact-letter-multiset model (a repeated letter, e.g. WHEELS' two E's, must be found twice); letter pickups spawn on a ~30-60s fixed timer with a pre-warning flash (same convention as the ambulance danger-lane flash) since a rare, small target would otherwise be nearly impossible to react to; and word-completion draws from the SAME reward pool as the daily gift, just weighted harder toward cosmetics, with duplicate cosmetic rolls converting to a bonus coin payout instead of doing nothing.

**Mid-batch follow-up, direct**: "you need to get X score to unlock daily gift and keep the streak, it scales with player's level, ex: 700 score." This changed the ALREADY-SHIPPED Batch 139 streak rule, not just the new gift — a run now only counts toward the day (advancing/keeping `currentStreak` AND unlocking that day's gift claim) once it clears `dailyScoreThreshold()` (`700 + (level-1)*50` — 700 assumed as the Level 1 anchor per the given example, first-pass, flag if that anchor was meant for a different level). A later lower-scoring run the same day can't un-qualify an already-qualified day, since the streak-update block simply can't re-enter once `lastPlayedDayKey` is set to today.

### New persistent state (`allTimeStats`)
`lastGiftClaimDayKey`, `dailyGiftsClaimed`, `currentWord`, `wordLetterCounts`, `wordsCompleted`, `totalLettersCollected` — all merged over defaults, same pattern as every other all-time stat field.

### Reward system
`rollReward(source)` (`source` = `'daily'` or `'word'`) picks a tier (coins/xp/color/car) via `REWARD_WEIGHTS[source]`, then resolves it: coins/xp add directly to `allTimeStats`/`gainXP()`; color/car pick randomly from `GARAGE_COLORS`/`GARAGE_CARS` (car pick is itself rarity-weighted via `CAR_RARITY_WEIGHTS`, common more likely than legendary) and grant it if not already owned, or convert to a bonus coin payout (`duplicateToCoins()`, 150-300 coins) if it is. All reward ranges/weights are first-pass placeholder numbers, not tuned by feel — flagged for whoever picks up the design/balance pass next.

### Daily word
16 racing/road-themed words (`DAILY_WORDS`: TURBO, NITRO, SPEED, DRIFT, BOOST, RALLY, ENGINE, WHEELS, BRAKES, GARAGE, DIESEL, PISTON, OCTANE, REDLINE, ASPHALT, HIGHWAY). `wordRemainingLetters()` computes what's still needed against the exact multiset; `collectWordLetter()` records a pickup, and on completion rolls a `'word'`-tier reward and rotates to a different random word (never repeats the just-finished one back-to-back), resetting collected-letter counts.

### On-road letter pickups (real gameplay, not just a data model)
A single pending letter is queued on a random 30-60s timer (`letterSpawnTimer`/`randomLetterSpawnDelay()`), always one of the current word's still-needed letters. A 1.5s pre-warning flashes the target lane gold with the letter shown (mirrors the existing ambulance danger-flash pattern) before the actual pickup spawns and scrolls down the lane at full road speed. Colliding with it (reusing the existing `checkCollision()` AABB check) collects the letter, plays a new short ascending `playSound('pickup')` chime, and shows a `ScorePopup` — `"LETTER X" / <word>` normally, or `"WORD COMPLETE!" / <reward summary>` on the completing pickup. Missed pickups that scroll off-screen are simply discarded — the letter isn't lost, the timer just restarts. Placeholder gold-square-plus-glyph visuals throughout, deliberately unpolished pending the real design pass.

**Verification**: live-tested in the Browser pane via direct function calls and simulated `loop()` frames (screenshots still don't composite this session). Confirmed: `canClaimDailyGift()`/`claimDailyGift()` correctly gate on same-day play + score threshold and refuse a second same-day claim; a sub-threshold run doesn't advance `currentStreak` or unlock the gift while a qualifying run does, and a later lower-scoring run the same day doesn't undo an already-qualified day; the exact-multiset word model requires a repeated letter to be found twice before completion; word completion fires the reward exactly once, rotates to a different word, and resets letter counts; 800 simulated `rollReward()` calls (400 `'daily'` + 400 `'word'`) produced zero errors, with color/car hits correctly falling back to bonus coins once those pools were exhausted; a forced pre-warning correctly converted to a real on-road pickup after its countdown, and a forced collision correctly collected it, updated stats, and popped the right text; a 1200-frame unattended simulated run (default random traffic + letter spawns) hit a normal vehicle-collision game-over with zero errors, and `launchGame()` afterward correctly reset `letterPickups`/`pendingLetterWarning`/`letterSpawnTimer`. Cleared all test `localStorage` afterward.

---

## 2.68.0 — 2026-09-01 14:45: Batch 148 — Showroom preview's box/frame around the car removed entirely (Batch 145's flat-fill fix wasn't enough)

Direct follow-up with 2 screenshots: "you still didn't do it... one [image] has the car, a frame, then a background, and it changes colors... the second image, other car, no background on the frame around it, it looks good, do it the same way." Batch 145 had already made the stage background a static, non-paint-tinted flat fill — verified correct at the time (pixel-sampled identical across paint colors) — but that only addressed the COLOR-CHANGING part of the original complaint, not the fact that the preview still sat inside its own distinctly-bordered, distinctly-backgrounded box at all, unlike every other car sprite in the game.

Removed the whole box treatment: `.showroom-stage`'s own `border` is gone, and the dedicated `#garageRoadBg` background canvas (Batch 83's original "road background," simplified to a flat fill by Batch 85/145) is deleted outright — HTML element, its CSS rule, the `drawGarageStageBg()` function that painted it, and the call site in `drawGaragePreview()`. The preview car now sits directly on `.showroom`'s own existing background, exactly matching how the Garage tile grid, leaderboard rows, and the hover card all already display their sprites — no separate box around just the car anywhere in the game now.

**Verification**: live-tested in the Browser pane — confirmed `#garageRoadBg` no longer exists in the DOM and `drawGarageStageBg` is fully undefined; confirmed `.showroom-stage` computes to `border-width: 0px` and a transparent background, with `.showroom`'s own background showing through directly; confirmed switching paint colors still works with zero errors (nothing left to break now that the removed function isn't called). Full Garage/Stats/Leaderboard/gameplay regression pass, zero errors. Cleared all test `localStorage` afterward.

---

## 2.67.0 — 2026-09-01 14:20: Batch 147 — both multiplier-% badges removed from the Garage hover card, per direct reversal

Direct feedback: "I change my mind, remove both mults from the hover info — the one next to the kilometers and the one next to the car name — kilometers should be back in its old place, to the right." Reverts both Batch 145 (the name-adjacent "+XX%" size-based badge) and Batch 146 (the TOP SPEED row's speed-derived "+XX% MULT") entirely — HTML, CSS, and JS wiring for both, plus the now-orphaned `speedMultBonusPct()` helper (its only caller). `.ghc-top` and the TOP SPEED row's `.ghc-bar-top` are back to their pre-Batch-145 structure: name/state stacked plainly, KM/H value right-aligned on its own again. The underlying `carBaseMultiplier()`/`estimateTopSpeedKmh()` values themselves are untouched — this only removes the two extra display badges, not the BASE MULT/TOP SPEED bars they were extracted from, which stay exactly as they were.

**Verification**: live-tested in the Browser pane — confirmed both `#ghcMultBadge` and `#ghcSpeedMult` no longer exist in the DOM, confirmed `speedMultBonusPct` is fully undefined (not just unused), confirmed the TOP SPEED value renders right-aligned same as before either badge existed, zero console errors. Full Stats/Leaderboard/gameplay regression pass, zero errors. Cleared all test `localStorage` afterward.

---

## 2.66.0 — 2026-09-01 14:05: Batch 146 — paint swatch lock icons removed, hover card's TOP SPEED row gets a speed-derived multiplier %

Two pieces of direct feedback.

**Paint swatch lock icons removed**: per direct feedback ("I think the stripes will be enough to show it's locked... remove all these lock icons"). `renderColorPicker()` no longer creates/renders the `.color-swatch-lock` canvas for locked colors; the diagonal yellow/black hazard-tape stripe (`.locked-swatch`, already the primary locked indicator since Batch 107) is now the only one. `renderLockIcon()` (the function that drew the icon) and its CSS rule were both removed entirely rather than left as dead code, since nothing else in the file used either.

**Hover card — speed-derived multiplier %**: a follow-up correction on Batch 145's name-adjacent "+XX%" badge — that one shows the SIZE-based multiplier bonus (`carBaseMultiplier()`); direct feedback clarified this is a genuinely different number they want SEPARATELY: "the percentage that gets added based on the SPEED... that's why I suggested putting it near speed... same line as km/h." Direct formula: `topSpeedKmh - 50` (the game's HUD baseline speed) — i.e. +1% per km/h gained above baseline, matching the multiplier formula from the ongoing "real per-vehicle speed" design discussion (PLAN.md). New `speedMultBonusPct(kmh)`, displayed as "+XX% MULT" right next to the km/h value on the TOP SPEED row, colored to match that car's speed tier (green/amber/red) — both explicitly requested details ("write it like plus x percent MULT so the user knows it's a mult," "make it the color of the speed").

**Verification**: live-tested in the Browser pane — confirmed all 8 locked paint swatches show the stripe pattern with zero lock-icon canvases remaining and `renderLockIcon` fully undefined (not just unused); confirmed the new speed-% badge shows correct values/colors across the full range (Tractor +60% green, Stock +120% amber, Land Speeder +200% red) with zero clipping even at the longest realistic string ("200% MULT"). Full Stats/Leaderboard/gameplay regression pass, zero errors. Cleared all test `localStorage` afterward.

---

## 2.65.0 — 2026-09-01 13:35: Batch 145 — Garage hover card gets a quick-glance multiplier badge, preview stage's paint-tinted background removed

Two pieces of direct feedback.

**Multiplier badge**: added a small "+XX%" badge next to the car's name on the hover card (e.g. "+30%"), reading the same `carBaseMultiplier()` value the BASE MULT bar further down already shows — this is a faster, higher-up glance at that same number, not a new stat. Purple, matching the BASE MULT bar's own fill color so the two visually tie together. Verified it doesn't clip even for the longest name (ROAD TRAIN) with the highest multiplier (+136%).

**Preview stage background**: the Garage Showroom's car-preview stage had a soft radial glow tinted to match the currently-selected paint color (added in Batch 85, per a completely different piece of feedback at the time). Direct feedback now: "whatever color you choose, the car has a kind of background that changes colors... look at the sprites, they're on solid color, there isn't a frame around anything... remove this." Every other car sprite in the game (Garage tile grid, leaderboard rows, the newer hover card) already sits on one flat, unchanging backdrop with no per-color treatment — this stage was the one remaining exception. Simplified `drawGarageStageBg()` to just the flat dark fill, dropped the paint-tinted radial gradient entirely.

**Verification**: live-tested in the Browser pane — confirmed the stage background canvas samples to the identical flat color regardless of which paint color is selected (tested red vs. blue, byte-for-byte identical at both the center and a corner pixel — no gradient remnant); confirmed the hover card's new badge shows the correct percentage for both a low-multiplier car (Stock, +30%) and the highest-multiplier car (Road Train, +136%), with zero clipping in either case; full Stats/Leaderboard/gameplay regression pass, zero errors. Cleared all test `localStorage` afterward.

---

## 2.64.0 — 2026-09-01 13:00: Batch 144 — Stats "Best ever" text made white, 8 more cars given real TOP SPEED values (Formula, Hypercar, Coachbuilt were never touched)

Two pieces of direct feedback.

**Stats — "Best ever X days"**: wrapped in its own span, colored `var(--c-text)` (white) instead of inheriting the surrounding hint text's dim gray, per direct request ("make this font color white so it is seen better").

**Garage hover card speed — real bug, not a re-tuning miss**: direct follow-up reported FORMULA still stuck at 165 despite Batch 143's retuning. Root cause: Batch 143 only touched the 15-car `speedClass` roster — FORMULA, HYPERCAR, and COACHBUILT are three SEPARATE legendary cars that were never part of that group, so they fell straight through to the generic (size-penalized) formula the whole time, landing around 160-165 regardless of how fast their name suggests. The lookup table (renamed `SPEED_CLASS_KMH` → `CAR_KMH_OVERRIDE`) is no longer gated on the `speedClass` flag at all — that flag is for an unrelated system (Batch 136's truck-exemption check) and was never meant to double as "is this car speed-tuned." Added: FORMULA=230 (direct spec, on par with F1), HYPERCAR=245 (real hypercars hold actual real-world top-speed records), COACHBUILT=235 ("hella speedy" per direct feedback), plus 5 more with direct numeric specs — SUPER SUV=180, SUPERCAR=190, ARMORED VAN=170, GO-KART=150, TRACTOR=110.

**Important nuance preserved in code comments**: "legendary is always faster" does NOT apply to every legendary car in the game — Tank (160) and Steamroller (165) are also legendary but deliberately left OFF this table, since real tanks/steamrollers are genuinely one of the slowest vehicle categories that exists. Rarity tracks cost/exclusivity, not speed, for cars that were never speed-themed to begin with — the "legendary=fast" rule only holds within groups that already lean into being fast.

**Verification**: live-tested in the Browser pane — confirmed FORMULA/HYPERCAR/COACHBUILT/SUPERCAR/SUPER SUV/ARMORED VAN/GO-KART/TRACTOR all show their exact specified values; confirmed F1/Indy Oval/Land Speeder/Dragster unchanged from Batch 143; confirmed Tank/Steamroller correctly remain slow despite legendary rarity; confirmed the full roster stays multiple-of-5 with zero errors; confirmed the hover card's live UI reflects FORMULA's new 230 km/h value in red; confirmed "Best ever X days" renders in white, visibly distinct from the surrounding dim hint text. Full Stats/Garage/Leaderboard/gameplay regression pass, zero errors. Cleared all test `localStorage` afterward.

---

## 2.63.0 — 2026-09-01 12:20: Batch 143 — live HUD speedometer hits a clean 200, per-car TOP SPEED values fully hand-tuned with real-world research

Two pieces of direct feedback.

**Live HUD speedometer**: `speedToKmh()` was a flat `spd * 34`, which topped out at 199 (5.85 × 34 = 198.9) instead of a clean 200 at max speed — "looks much nicer" without the odd number, per direct request. Now an explicit ratio-to-range map, using the same clamped `(spd-base)/(max-base)` pattern the live multiplier bonus already used elsewhere — hits exactly 50 at `baseSpeed` and exactly 200 at `maxSpeed`, clean numbers at both ends, not just the top.

**Garage hover card TOP SPEED, fully hand-tuned**: replaced Batch 142's generic formula (`220 + legendaryBonus + sizeAdj`) with an explicit, individually-reasoned value for each of the 15 `speedClass` cars, per direct request ("check maybe in real life... which ones should be faster... legendary ones should all be faster... if not in real life, swap them for rarities"). Where a car has a real-world motorsport analogue — F1, Le Mans Hypercar, IndyCar-oval, Formula 3, NASCAR-style stock car, GT3, and superbike racing are all real categories with well-documented relative top speeds — that ordering drives the number (F1=230 and IndyCar-oval=220 per direct spec; Le Mans Hypercar and modern EV hypercars are genuinely competitive with or faster than F1 in a straight line in reality, so they land at 235/240; F3 Junior is correctly the slowest of the "real" racers at 200, a genuine junior/entry-level series). The fictional SPEED CLASS group (Land Speeder, Dragster, Jet Bike, Hover Coupe, Prototype, Neon Wedge) has no real-world analogue, so rarity drives it instead, topping out at Land Speeder/Dragster=250. Net result, verified live: every LEGENDARY speedClass car (230-250) beats every non-legendary one (200-225) — a clean, fully consistent split matching the user's stated goal exactly, not a coincidence of a formula.

**Also, per a mid-turn request**: seeded ~320 realistic synthetic runs (varied cars/scores/dates across ~75 days) plus a deliberately extreme stress case (58,000 runs, 987 million total score, an absurd multi-year "play time" figure) to check the Stats/Garage/Leaderboard screens for overflow or number-formatting breakage at scale. At the realistic couple-hundred-runs level nothing overflowed or clipped anywhere. The extreme stress case also held up almost entirely — the one genuine clip found (a per-car BEST SCORE/SURVIVED stat on the Garage hover card) only occurs at physically-impossible single-run values (a 98-million-point run, an 11-day-long single run) that the game's own scoring/timing can never actually produce in real play, so left unfixed rather than adding handling for a scenario that can't happen.

**Verification**: live-tested in the Browser pane — confirmed `speedToKmh(baseSpeed)===50` and `speedToKmh(maxSpeed)===200` exactly; confirmed all 15 speedClass values via `garageSpeedTiers()`, every legendary car's minimum (230) exceeds every non-legendary car's maximum (225), all still multiples of 5, F1=230/Indy Oval=220/F3 Junior=200 match spec exactly; ran the full realistic-scale (320 runs) and extreme-scale (58,000 runs) overflow sweeps described above across Stats/Garage/Leaderboard; full regression pass afterward, zero errors. Cleared all test `localStorage` afterward.

---

## 2.62.0 — 2026-09-01 11:40: Batch 142 — Garage hover card TOP SPEED: fixed color-tier inconsistency, retuned values, rounded to 5

Direct follow-up on Batch 140's placeholder speed display. Real bug: the green/yellow/red tier was computed by SORTING the whole 52-car roster and splitting into thirds — a RANK-based split, not a value-based one, so two cars sitting at the identical (or very close) km/h could land in different colors depending purely on where the sort happened to place them relative to the n/3 and 2n/3 cutoffs. Direct feedback caught this exactly ("Road [X] has red on 170, Convertible also 170 but it's yellow — very inconsistent"). Replaced with fixed absolute thresholds, per direct spec: red starts at 200 km/h, yellow at 160 — every car at the same km/h is now always the same color, full stop, no dependency on the rest of the roster.

**Retuned the actual values**, per direct feedback ("Land Speeder, Dragster, F1... should be way faster... one or two cars go up to 250, most fast cars around 220-230"): Land Speeder and Dragster are now the roster's outright fastest at 250; every other `speedClass` car (F1 included — was 213, now 225) clusters 210-240, varied a little by rarity tier and size within the group so they're not all identical. Every `speedClass` car still clears the 200 red threshold on its own — verified live, so RED now means exactly "one of the game's own SPEED CLASS/RACE-set cars," not a coincidence of the old formula's scale. **All values now round to the nearest 5** ("around all speeds to the 5"), per direct request.

**Still a placeholder**, same caveat as Batch 140 — no real per-car speed exists in the simulation; this is display-only on the Garage hover card. A separate, still-undecided design discussion about REAL per-vehicle top speed + a matching multiplier formula is tracked in PLAN.md, not part of this batch.

**Verification**: live-tested in the Browser pane against the full 52-car roster — confirmed every value is a genuine multiple of 5; confirmed it's now mathematically impossible for two cars at the same km/h to land in different tiers (fixed thresholds, not rank); confirmed all 15 `speedClass` cars land in the red tier (8 slow/29 medium/15 fast split); confirmed Land Speeder and Dragster both hit exactly 250 and F1 sits at 225; confirmed the hover card UI reflects the new values/colors correctly for both. Full Stats/Leaderboard/gameplay regression pass afterward, zero errors. Cleared all test `localStorage` afterward.

---

## 2.61.0 — 2026-09-01 11:00: Batch 141 — Stats screen widened to match the main menu, sticky BACK/SCORES footer, empty-chart cursor fix

Three pieces of direct feedback on the Batch 139 Stats redesign:

- **Widened to match the main menu**: `#statsView .settings-panel`'s `max-width` was 380px (sized down from the original "Stats Final" mockup's 700px reference) — per direct feedback ("the gameplay screen is much wider... make it the same wideness as main menu"), now 506px, exactly matching `.game-container`'s own declared width.
- **Sticky BACK/SCORES footer**: per direct feedback, framed explicitly as "for future" too (any screen that might need a scrollbar later should follow this). Only the chart/tiles/streak/collection content scrolls now — BACK/SCORES stay fixed and always visible, never requiring a scroll to reach. New `.stats-panel`/`.stats-scroll` (flex-column + `overflow:hidden` on the panel, `flex:1 1 auto;min-height:0;overflow-y:auto` on the scrolling wrapper) — the exact same mechanism the Garage screen's `.garage-panel`/`.garage-scroll` already used for this (Batch 92), reimplemented under Stats-scoped class names rather than reusing the Garage-named ones, to keep the two screens' styling fully independent.
- **Empty-chart cursor**: "if there are no runs yet... it shows... a special cursor for that" — a real (if minor) bug, not the "two lines" part of the report (that's the chart's own axis border, left+bottom, which is intentional framing and stays regardless of data). `.stz-plot`'s `cursor: crosshair` was unconditional in CSS even with the SVG hidden and empty — now defaults to `cursor: default`, only switching to crosshair via a `.has-data` class toggled in `renderStatsChart()` once there's actually something to hover.

**Verification**: live-tested in the Browser pane — confirmed a genuinely fresh (0-run) save shows `cursor: default` over the empty chart with all polyline/grid data confirmed truly empty (not just hidden); confirmed re-seeding data flips the cursor to crosshair and restores normal hover; confirmed the panel's `max-width` is exactly 506px; confirmed, by shrinking the viewport to force scrolling, that BACK stays at an identical screen position while the content above it scrolls independently; ran a full Stats/Garage(+hover card)/Leaderboard/gameplay regression pass afterward, zero errors. Cleared all test `localStorage` afterward.

---

## 2.60.0 — 2026-09-01 10:15: Batch 140 — Garage car hover card (from the user-provided "garadge_hover_info" mockup), real upright sprite, speed-tier color grouping

Implemented the uploaded hover-card mockup: hovering any real (discovered) car tile in the Garage now shows a floating card with the car's sprite, rarity/name/ownership state, a RUNS / BEST SCORE / SURVIVED stat row, a BASE MULT bar, and a TOP SPEED bar — following the same fixed-position/`getBoundingClientRect()`-driven pattern the leaderboard tooltip and Stats chart tooltip already use, clamped to stay fully inside the viewport (flips to sit above the tile instead of below when there isn't room). Mystery/undiscovered tiles never get a hover listener at all, same as they never get a click listener — their identity still can't leak.

**"Replace the sprite... centered"**, per direct request — the mockup's own placeholder sprite (a mock car drawn from plain colored `<div>`s) is swapped for the REAL car sprite, upright and centered, generalized out of the Garage Showroom's existing `drawGaragePreview()` box-fit-and-scale technique into a new reusable `drawCarSpriteUpright(canvasEl, car, maxW, maxH)` — `drawGaragePreview()` itself now just calls this instead of duplicating the same logic, no behavior change there.

**RUNS / BEST SCORE / SURVIVED** needed real per-car tracking that didn't exist in any form — not `highscores` (top-100-by-score only, would undercount a popular-but-low-scoring car) and not the newer `runHistory` (doesn't know which car was driven). New `allTimeStats.carStats` (`{ carKey: {runs, bestScore, bestSurvivalMs} }`), updated in `recordRunStats()` (same place every other all-time stat already updates, using `selectedCarKey` which was already in scope there). Like `runHistory`/day-streak before it, this starts empty for existing saves — no retroactive backfill possible, only reflects play from this point forward.

**BASE MULT** — extracted a new `carBaseMultiplier(car)` (`1.3 + vehicleMultiplierBonus(car)`, the two multiplier terms that depend only on the car, not on per-run settings like lane count) since no standalone function returning just that existed before; the bar fills relative to the actual max across the whole roster (computed once, cached), not a guessed cap.

**TOP SPEED + green/yellow/red grouping**, per direct request: "depending on the speed of the car... green for slower... yellow for medium... red for very high... it will be grouping cars into their speeds... that's like for future." No real per-car speed exists anywhere in the simulation — confirmed by checking the actual live speed variables, not just assuming: every car drives at the identical `currentSpeed` regardless of which one is selected. Since the user explicitly framed real per-car speed as future work but still wants the grouping UI now, `estimateTopSpeedKmh(car)` derives a placeholder KM/H figure from what the game already encodes about each car — the `speedClass` flag (Batch 136 — sleek race/speed cars run faster) plus size (bigger reads as heavier/slower) — rather than a flat number, so the grouping is actually meaningful today instead of static. Tiers (slow/medium/fast → green/amber/red) are computed by sorting the whole 52-car roster and splitting into thirds, not fixed km/h cutoffs, so the grouping is always 3 visually distinct buckets regardless of the estimate formula's exact scale. **This is explicitly a display-only placeholder, not a real gameplay speed mechanic** — flagged in both this entry and PLAN.md's existing "per-vehicle speed multiplier, not yet implemented" line so it's not mistaken for that separate, still-open item later.

**Verification**: live-tested in the Browser pane — confirmed zero load/console errors; confirmed the 52-car roster splits into an 18/17/17 slow/medium/fast distribution and every one of the 15 `speedClass` cars lands in "fast" as intended; confirmed the hover card renders correctly for all 4 real states (EQUIPPED, OWNED, NEVER DRIVEN, LOCKED — with the exact price); confirmed mouseleave hides it; confirmed the real `saveScore()` path correctly flips NEVER DRIVEN → OWNED and populates RUNS/BEST SCORE/SURVIVED from a real simulated run; confirmed the card stays fully within the viewport both when a tile is near the top and near the bottom (flips above), verified via realistic `scrollIntoView()` + `getBoundingClientRect()` before each hover (an early test run without scrolling first produced misleading off-viewport numbers — not a bug, just an unrealistic test condition, since a tile can't actually be hovered while off-screen); confirmed clicking a tile to equip/buy (which rebuilds the grid) correctly hides the card instead of leaving it anchored to a now-destroyed element; confirmed the Showroom preview canvas renders identically after the `drawCarSpriteUpright()` extraction; ran a full Stats/Leaderboard/gameplay regression pass afterward with zero errors, since this batch touched shared code (`recordRunStats()`, `drawGaragePreview()`). Cleared all test `localStorage` afterward.

---

## 2.59.0 — 2026-09-01 09:20: Batch 139 — Stats screen redesign (from the user-provided "Stats Final" mockup), real run timestamps, leaderboard date icon

Full Stats screen redesign, per the uploaded design doc, implementing every stat it listed:

- **History chart** — 5 view modes (ALL RUNS / LAST N RUNS / AVERAGE OF N / BY PERIOD / cumulative PERFORMANCE SCORE), each with its own param row (run count, block size, DAY/WEEK/MONTH/YEAR grouping, or 7D/30D/3M/12M/ALL range), an SVG line+area chart with grid lines, a peak-run marker, and a hover crosshair/tooltip showing the exact run's key, value, and real date. Ported the mockup's own `series()`/`renderVals()` math (bucketed downsampling that always keeps each bucket's HIGHEST run so records never get averaged away, "nice number" axis scaling, span-aware tick labels) almost verbatim — it's plain JS, not framework-specific. First SVG usage in this codebase (everything else is canvas pixel-art) — a deliberate choice: a smooth analytics line chart reading as pixel-art would look broken, not stylistically consistent.
- **15-tile stat grid** — every stat the old 3-card SCORING/DRIVING/TIME layout showed, plus new ones: CLOSE CALLS (total) and BEST CLOSE CALLS (RUN) (close calls were already tracked per-run, just never accumulated into `allTimeStats`), AVG RUN (average survival time), RUNS TODAY and DAYS PLAYED (both date-bucketed).
- **Day streak panel** — consecutive-days-played counter + all-time best, and a 14-day calendar-tick row.
- **Collection panel** — cars "spotted" by rarity tier, as progress pips + ratio/percent per tier. This mapped directly onto an EXISTING system (`allTimeStats.discoveredCars`, Batch 99's "spotted as NPC traffic" tracking, already separate from owned/purchased cars) — nothing new to invent here, just a new by-rarity display of data already being tracked.

**New data model, since none of this existed before**: a lightweight chronological `runHistory` array (`{score, ts}` per completed run, capped at the most recent 5000) — separate from `highscores` (only keeps the top 100 BY SCORE, silently drops everything else) and from `allTimeStats.recentScores` (last 50 only, no dates) — is what actually powers the chart/streak/RUNS TODAY/DAYS PLAYED math. Also new: `allTimeStats.totalCloseCalls`/`bestCloseCallsRun` (accumulated from the existing per-run `closeCallsThisRun`), and `currentStreak`/`bestStreak`/`lastPlayedDayKey` (compares each run's local calendar day against the last one that updated the streak — same day = no change, consecutive day = +1, any bigger gap = reset to 1). All wired into `recordRunStats()`, which already ran exactly once per completed run.

**Also, per direct request in the same message**: "scores from now on also save the date... each [row] could have a calendar icon and when you hover over it it would say the date." Turned out the date/time WAS already being saved on every `highscores` entry (`saveScore()`'s `date`/`time` fields) — just never shown anywhere in the UI. Added a small hover-only calendar icon to each leaderboard row (reusing the existing `addLbTip()` shared-tooltip mechanism already used for every other field) showing that run's date/time on hover — no data-model change needed for this part, only a UI addition. The icon lives in the leaderboard row's existing empty spacer grid column (5th, deliberately unassigned since Batch 134's real-fix-for-a-real-bug rework of this exact row) rather than adding a new track, so the row's total width and every other column's position are untouched — this row has a documented history of grid-layout bugs from exactly that kind of change, see [[feature-stats-garage]].

Note: `runHistory` starts empty for every existing save — there's no way to backfill dates for runs saved before this batch, so the chart/day-streak/RUNS TODAY/DAYS PLAYED numbers only reflect play from this point forward. Expected, not a bug.

**Verification**: live-tested in the Browser pane — seeded 400 synthetic runs across 30 days plus matching highscores, confirmed every chart mode (including all params) renders correct point counts/values with zero errors; confirmed hover shows the right key/value/date and clears on pointerleave; confirmed the dropdown opens/closes (including click-outside-to-close) without stacking duplicate listeners across re-renders; confirmed zero elements overflow the settings panel's bounds. Confirmed the empty-history state (fresh save, 0 runs) renders a clean "no runs yet" message with no NaN/divide-by-zero anywhere across all 15 tiles, the streak panel, or the collection panel. Ran the REAL save path (`saveScore()`, not just synthetic data) end-to-end and confirmed `runHistory` gets a real entry, `totalCloseCalls` accumulates correctly, and the streak logic is exactly right across all 3 real cases (consecutive day → +1, gap of several days → resets to 1, same day played twice → no double-count). Confirmed the 5000-entry `runHistory` cap trims the oldest entries correctly. Confirmed the leaderboard's calendar icon renders with a working hover tooltip and doesn't shift the rank/car-name/sprite/weight/perf columns. A stray reference to the old Stats screen's coin-icon canvas (`statCoinsIcon`, removed along with the old layout) was caught and fixed — it was crashing page load entirely before the fix. Cleared all test `localStorage` afterward.

---

## 2.58.0 — 2026-09-01 08:30: Batch 137/138 — crash-sequence responders always fully visible, never overlap the wreck or each other, more varied stopping distances

Direct follow-up bug report: "sometimes... you can't see the police and ambulance, they are cut off by the bottom of the screen... make sure they're always not going over the corpse... the corpse can be two lanes long... make sure these cars don't also go on top of each other." Three real bugs in the old `csEnterPhase('arrive')` responder-placement logic, all in the same below-the-wreck-only, single-wreck layout:
1. The standoff distance was measured from the wreck's TOP edge only (`wreckY`), ignoring the wreck's own height — a tall wreck (e.g. a truck) could have responders parked inside its own footprint.
2. Only `CS.wrecks[0]` (the player) was used to find the "corpse's lane" — if the player was mid lane-change when hit, the player and the other vehicle's wrecks can land in different/adjacent lanes, and the second wreck's lane was never excluded.
3. `RESP_GAP` (24) was smaller than a stacked responder's own on-screen height (up to 31 for police) — two responders forced to share a lane could visibly overlap each other.

Rewrote the layout: standoff is now measured from whichever wreck's edge extends furthest; every lane spanned by EITHER wreck is excluded when picking responder lanes; `RESP_GAP` is sized to safely clear the tallest responder. The old "hard floor below the wreck, even if it runs a responder off-canvas" tradeoff is gone — each responder now tries a row below the wreck first, retries at a tighter (but still safe) gap if a full-width stack doesn't fit, and only falls back to a row ABOVE the wreck if there's truly no room below — always fully visible now wins over always-below. On this game's short (260px) canvas, a crash near the very bottom of the player's legal Y range often has no free room below at all, so "sometimes parks ahead of the wreck instead of behind it" is an inherent tradeoff of a canvas this size, not a remaining bug — the closest responder in that fallback still hugs the wreck's edge tightly, only additional same-lane stackers drift further.

Mid-turn follow-up feedback: responders "often are in the similar height, like stop similarly" and, separately, that being placed noticeably above a bottom-of-screen wreck "looks kind of weird." Addressed both: widened the per-responder stagger (`STAGGER`, was `[0,16,6]`, now `[0,24,10]`) so different-lane responders visibly stop at different depths instead of nearly in a row; and added a compression retry — a stacked (2nd/3rd) same-lane responder now first retries BELOW the wreck at the tightest gap that still avoids overlap (`MIN_GAP`) before ever flipping to above, so a squeezed group stays packed close behind the wreck rather than jumping ahead of it whenever there's any way to fit.

**Verification**: live-tested in the Browser pane — ran `csEnterPhase('arrive')` directly against 5000+ randomized wreck position/height/lane-count combinations (3-5 lanes, where lane width ≥ car width) checking three invariants (no responder off-canvas, no responder overlapping either wreck, no two responders overlapping each other): 0 failures. Separately fuzz-tested the full 3-8 lane range (5000 cases) confirming 0 off-canvas and 0 corpse-overlap failures at every lane count (6+ lanes on this canvas has cars visibly wider than a single lane by design — a pre-existing, unrelated game characteristic, not something this fix could or should touch). Triggered a real in-game crash live and visually confirmed both police cars and the ambulance render fully on-canvas, clear of the wreckage and of each other. Zero console errors.

---

## 2.57.1 — 2026-09-01 07:40: Batch 136 — race/speed cars excluded from the new truck classification

Direct follow-up to Batch 135: "speed cars like F1 and race cars aren't supposed to be trucks." `isTruckLike()`'s height check couldn't tell a bulky hauler (Road Train, Fire Engine) from a long but sleek racer (F1, Land Speeder, Dragster) — both could cross the same height threshold for completely different reasons. New `speedClass: true` field added to `GARAGE_CARS`' existing SPEED CLASS (proto/speeder/dragster/hover/jetbike/neon) and RACE (f1/indy/f3/lmh/gt3/attack/stockcar/evhyper/superbike) groups — 15 cars total, marked whether or not they currently cross the height threshold, so a future height/scale tuning change can't silently pull one back into truck territory. `isTruckLike()` now checks `v.garageCar.speedClass` first and exempts those cars from the height rule entirely, regardless of type.

**Verification**: live-tested in the Browser pane — confirmed all 15 speed/race cars carry the new field; confirmed the 3 cars that previously (incorrectly) crossed the threshold (F1, Land Speeder, Dragster) now correctly return `false` from `isTruckLike()`, while the genuine haulers (Road Train, School Bus, Fire Engine, Garbage Truck, Hearse, Camper, Tow Truck, Limousine) still correctly return `true`. Ran a full 800-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.57.0 — 2026-09-01 07:30: Batch 135 — crash-sequence shadow removed, long cars now count as trucks for scoring/energy

**Crash-sequence shadow removed**: per direct feedback ("you can see your car's shadow still") — Batch 116 removed the jump drop-shadow, but a SEPARATE mechanism, a dark "scorch pool" rect drawn under every wreck in the crash sequence (`csDraw()`, Batch 97), was never touched by that removal and is a genuinely different code path. Removed outright, same reasoning Batch 116 already established for this game (a subtle depth cue not worth the upkeep at this scale).

**Long cars now count as trucks for scoring/ability-bar energy**, per direct request, independent of a vehicle's spawn TYPE — many Garage cars (Road Train, School Bus, Fire Engine, Garbage Truck, Camper, Hearse, Tow Truck, Land Speeder, Dragster, Limousine) spawn as `type:'normal'`, since the actual `'truck'` spawn type only covers 5 hardcoded bodies (bus/semi/tanker/flatbed/box) — a visually much longer Garage car was scoring/refilling identically to any small car. New `isTruckLike(v)` (`v.type === 'truck' || v.height >= TRUCK_LIKE_HEIGHT`, threshold set 1px below the smallest official truck body so nothing already truck-classified could fall outside it) now gates all 3 sites that previously checked `v.type === 'truck'` directly: the score/coin points lookup in `creditVehiclePass()`, its ability-bar energy gain, and the jump-over coin bonus at the collision site. One known accepted quirk: F1 (h:34, right at the threshold due to its elongated racing silhouette, not because it's a bulky/long vehicle) also gets classified as truck-like — a simple height threshold can't distinguish "long and heavy" from "long and sleek," and this wasn't worth a more complex heuristic for one borderline car.

**Verification**: live-tested in the Browser pane — computed `isTruckLike()` across the full Garage roster and confirmed it catches every intended long car (with the one known F1 edge case, flagged not hidden); confirmed a simulated pass with a normal-typed-but-tall vehicle (Road Train's real height) grants the truck-tier score/coins/energy (+20 energy, 20-point base score, 2 coins) while an equivalent short normal car still gets the standard tier (+10 energy, 10-point base, 1 coin); confirmed a full crash sequence (real `endRun()` → wreck rendering → `loop()`) runs with zero errors after the shadow removal. Ran a full 800-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.56.2 — 2026-09-01 07:00: Batch 134 — leaderboard name+icon block genuinely moved left (real CSS Grid fix)

Direct follow-up: "moved too much to the right." First attempt narrowed the fixed text column (210px→150px) — this turned out to do NOTHING to the block's actual position, a real misunderstanding of how the grid was behaving: the row's total width is fixed by the panel (not shrink-to-fit), so freeing space from a fixed column just fed straight into the adjacent `1fr` name column instead of shifting anything to its right. Caught this via direct measurement (the icon's x-position was identical before and after the "fix"), not assumed.

Real fix: every element now gets an EXPLICIT `grid-column` position instead of relying on implicit DOM-order placement, with a genuine empty spacer column inserted between the icon and WEIGHT that absorbs all leftover row width. This makes the name+icon block truly left-anchored right after the text column, while WEIGHT/PERF stay right-anchored as before — the leftover space that used to invisibly inflate the name column now sits in the spacer instead. As a side effect, this also let Batch 133's placeholder-span workaround (for rows with no car data) be removed — explicit `grid-column` positioning means a missing element can no longer shift anything, so there's nothing left to work around.

**Verification**: live-tested in the Browser pane — confirmed the icon's x-position genuinely changed (547px, down from 619px) via direct measurement, not just visual impression; confirmed with a worst-case row (10 lanes, 62-minute survival, 6.0x multiplier) that the meta text still doesn't overflow its column; confirmed a row with no car data still renders correctly with the placeholder removed. Ran a full real gameplay→`saveScore()`→`showLeaderboard()` pipeline with zero console errors. Test `localStorage` cleared afterward.

---

## 2.56.1 — 2026-09-01 06:45: Batch 133 — leaderboard: "SCORE" label replaces car name on the score line, car name moves next to the sprite

Direct request: the car name used to sit right after the score number ("5,000 ROAD TRAIN"). Replaced with a plain "SCORE" label there instead ("5,000 SCORE"), and the car name moved into a new dedicated column right before the sprite, right-aligned so it sits flush against the icon regardless of name length — "STOCK" and "ROAD TRAIN" both now end at the exact same x, immediately followed by their respective sprites, matching the icon's own already-fixed position (Batch 131/132).

`.lb-entry`'s grid gained a 6th column for the name (`22px 210px 1fr 120px auto 50px` — the new `1fr` is the name, the icon reverted to a fixed 120px since it no longer needs to absorb flexible space itself). Older saved entries with no `car` field render an empty placeholder cell in the name's slot (not just an omitted element) — CSS Grid places children into columns strictly by DOM order, so skipping the element entirely would have shifted every subsequent cell (icon, weight, perf) one column to the left for any row without car data.

**Verification**: live-tested in the Browser pane — confirmed "SCORE" label renders on every row; confirmed two different-length car names ("ROAD TRAIN" vs "STOCK") both end at the identical right x-coordinate (619px), flush against the icon's left edge (627px); confirmed a row with no saved car data doesn't corrupt the grid (weight/perf stay in their correct columns). Ran a full real gameplay→`saveScore()`→`showLeaderboard()` pipeline end-to-end (not just synthetic test data) with zero console errors. Test `localStorage` cleared afterward.

---

## 2.56.0 — 2026-09-01 06:30: Batch 132 — leaderboard icon moved left (annotated screenshot), close-call speed-scaled color + gap, version number fixed

**Main menu version number fixed**: was a stale hardcoded "v2.1" (unrelated to this project's real `X.Y.Z` version scheme) — now matches the actual CHANGELOG version. Going forward this should be updated alongside every CHANGELOG entry, the same routine as the rest of this project's documentation.

**Leaderboard car icon moved left**, per a directly-annotated screenshot marking exactly how far. The icon column used to start wherever the `1fr` TEXT column happened to end — since text always claimed all available remaining space regardless of how little it actually needed, the icon read as pinned far right (hard against WEIGHT) no matter the row's content. Swapped which column gets the flexible space: text is now a fixed 210px (comfortably fits this game's real row content), and the ICON column is `1fr` instead — so the icon now starts at a constant, much-further-left x for every row, with room to grow into before WEIGHT rather than needing to hug it.

**Close-call gap now scales with live speed**, per direct request ("smaller at low speed, bigger at high speed — don't make it too big"): was a flat `2.4`, now ranges `1.6` (at `baseSpeed`) to `3.0` (at `maxSpeed`) via the same 0-1 speed ratio the live score multiplier's own speed bonus already uses — a modest ±0.6 spread around the old value.

**"CLOSE CALL!" popup text now colored by speed** at the moment the near-miss actually happened (green low / amber medium / red high), captured once when the gap first drops to threshold — not recomputed later when credit actually fires, since that can happen several frames after the closest moment. `ScorePopup` gained an optional `color` param (falls back to the old fixed mint if omitted, though nothing else currently uses this class).

**Verification**: live-tested in the Browser pane — confirmed the version string now reads the current CHANGELOG version; confirmed the icon column's left edge is now identical across rows with different content (Road Train vs. a short "17 STOOK" row) and still doesn't overlap WEIGHT; confirmed `closeCallGapNow()` computes 1.6/2.3/3.0 at base/mid/max speed and `closeCallColorForRatio()` returns green/amber/red at the same 3 points; ran a full simulated close-call scenario end-to-end (not just the isolated formula) at max speed and confirmed the credited vehicle's captured color is genuinely red, not just the formula in isolation. Ran a full 800-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.55.2 — 2026-09-01 05:50: Batch 131 — leaderboard car icon: back to a fixed column, properly sized this time

Direct follow-up: Batch 130's "hug the text" fix (icon positioned right after the score/meta text, inside `.lb-main`'s own flex row) overcorrected — every row's icon started at a DIFFERENT x position depending on how long its own text happened to be, which read as inconsistent/"too far left" for short-text rows and broke the "all cars in one line" expectation entirely.

Reverted to a fixed grid column (`.lb-entry`'s `grid-template-columns`, now includes a dedicated icon slot) so every row's icon starts at the exact same x regardless of content — the actual fix for "align on the left side... all cars in one line." First attempt used a 70px column, but Road Train's real rendered width (~111px at the fixed 26px height from Batch 130) bled past it into WEIGHT's own column at typical panel widths — caught this via direct measurement, not assumed. Widened the column to 120px (matching the icon's own `max-width` cap) so even the longest car in the roster fits with room to spare, no overflow needed.

**Verification**: live-tested in the Browser pane — confirmed all 3 test icons (Road Train/Stock/Jet Bike) start at the identical left x-coordinate via direct `getBoundingClientRect()` measurement; confirmed Road Train's icon no longer overlaps WEIGHT at both desktop and mobile (375px) viewport widths, with real overlap math checked (`right > weightLeft`), not just eyeballed. Ran a full 500-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.55.1 — 2026-09-01 05:30: Batch 130 — pause mute button removed, leaderboard car icon fixed (position + real sizing bug)

**Pause menu MUTE button removed**, per direct request — redundant now that the pause overlay has real volume sliders (Batch 126). Removed the button, its DOM ref, `togglePauseMute()`/`volumeBeforeMute` entirely (nothing else called them), the click listener, and the label-sync line in `setPaused()`.

**Leaderboard car icon — 2 real bugs, both from direct follow-up feedback**: (1) position — the icon sat in its own fixed-width grid column anchored a constant distance from WEIGHT, so it read as floating far right of short text instead of sitting next to it. `.lb-main` is now a flex row (text block + icon), so the icon hugs the text at whatever width it actually has, growing/shrinking naturally with content length. (2) sizing — a real bug, not just a tuning miss: the CSS used `max-height`/`max-width` with `width:auto;height:auto`, but those only cap a canvas from ABOVE — they never scale a canvas UP past its tiny native pixel-art resolution (e.g. Jet Bike's native canvas is only 20×8px). Every icon was rendering at its true native size, unscaled — Road Train's 60×14 native canvas got clipped down to ~8px tall by the old 34px width cap, and shorter cars like Jet Bike were rendering at literally 8px tall with no scaling at all. Fixed with an explicit `height: 26px` (forces scaling, doesn't just cap it) and a generous `max-width: 120px` safety net for the longest car (Road Train renders ~111px wide at full height, comfortably under it).

**Verification**: live-tested in the Browser pane — confirmed the pause MUTE button and all its wiring are gone with zero errors; confirmed all 3 test icons (Road Train, Stock, Jet Bike) now render at a consistent 26px height via direct `getBoundingClientRect()` measurement (was rendering at native 14px/14px/8px respectively before the fix); confirmed the icons visually sit right next to the score/meta text instead of floating toward WEIGHT. Ran a full 800-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.55.0 — 2026-09-01 05:00: Batch 129 — START RUN layout bug, lane-count traffic/multiplier rebalance, real free-lane guarantee gap found and fixed

**Real bug fixed, caught from a user screenshot**: the Settings footer's START RUN button was rendering as an unusable 1px-wide sliver next to BACK. Root cause: `.btn` sets `width:100%`, and BACK's `flex:none` (flex-basis:auto) fell back to that inherited width as its sizing basis — BACK was stretching to fill the ENTIRE footer row, leaving START RUN nothing. Fixed by explicitly overriding `width:auto` on BACK.

**Traffic/multiplier rebalance across lane counts**, per direct feedback ("suicidal doesn't feel the same on 4L and 10L... more lanes but also more cars"): only ONE random lane is checked per spawn attempt, so the same `spawnChance` spread across more lanes meant each individual lane got objectively THINNER traffic as lane count went up — every difficulty tier felt progressively diluted the wider the road got. `spawnChance` now also multiplies by `config.lanes / 4` — per-lane spawn rate stays constant at every lane count (4 lanes is the unchanged reference point), while TOTAL on-screen traffic scales up with lane count. The lane-count multiplier term flipped from a penalty (`-0.1` per lane above 4) to a smaller bonus (`+0.05` per lane above 4) — wide-lane runs are now genuinely busier, not easier, so they're no longer punished for it; 3 lanes keeps its existing `+0.5` as the single biggest lane-based bonus, unchanged.

**Real gap found via direct empirical testing, pre-existing before this batch** (not introduced by the traffic rebalance above — reproduced with 4-lane density completely unchanged from before this batch): `canSpawnAt()`'s free-lane check only ever guards the ONE spawn being decided — it never accounted for several separately-approved spawns later coinciding into a simultaneously-busy top-of-screen moment as they all scroll down together. Caught this directly (not just from a code read) by re-running the free-lane invariant check repeatedly rather than trusting Batch 127's single-pass result: reproduced "all lanes occupied near the top" at 4 lanes/suicidal in roughly 1 of every 4-6 runs of 2000-2500 frames, confirmed every vehicle involved was a normal spawn (not a lane change bypassing the check). Fixed by requiring 2 free lanes instead of 1 at 4+ lanes (more concurrent traffic there to begin with warrants more margin) — 3 lanes keeps the original 1-free-lane rule, already the tightest config by design and never found broken across any test.

**Verification**: live-tested in the Browser pane — confirmed START RUN renders and functions correctly after the fix; confirmed per-lane spawn density is now equalized between 4L and 10L (5.3 vs 5.0 average spawns/lane over 3000 frames) while total traffic scales with lane count (21 → 50 total spawns); confirmed the multiplier now rewards wide lanes instead of penalizing them (10L: 1.3x under the old formula → 2.1x now) while 3L stays the single highest lane-based bonus; **re-ran the free-lane safety check repeatedly (not just once) after finding it could fail** — 0 violations across 6 consecutive 2000-frame trials at 4 lanes plus additional clean runs at 6 and 10 lanes, with total spawn counts confirmed still elevated at higher lane counts (fix didn't quietly undo the density increase). Ran a full 800-frame live gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.54.0 — 2026-09-01 04:15: Batch 128 — per-vehicle score multiplier bonus, based on real car size

Direct request: reward the player's CHOSEN car's own size — longer cars more, wider cars a little, with long vehicles (Road Train especially) scaling progressively harder rather than linearly. This closes a real gap the codebase's own Batch 113 comment had already flagged but never implemented ("a harder base setup — long car, night mode, more lanes — should be rewarded more").

New `vehicleMultiplierBonus(car)`, added into `calculateMultiplier()`: **length** is measured against Stock's own height (24px, the neutral baseline) — shorter cars get no bonus (clamped at 0, never a penalty for being small) and longer cars get `Math.pow(lengthFactor, 1.4) * 0.6`, an exponent >1 so the bonus GROWS FASTER than linear the longer the car gets. **Width** is measured against the native 14px hitbox width, a much smaller effect in both directions (`widthFactor * 0.15`) — narrow vehicles like Jet Bike get a small penalty, wide ones like Monster Truck a small bonus.

Result across the full 47-car roster: Road Train (h:60, more than 2x Stock, by far the longest car) stands out clearly at +1.06x on its own — next highest (Limousine/School Bus, h:44) is +0.46x, less than half — confirming the progressive curve actually produces the intended "Road Train specifically feels disproportionate" effect, not just a smooth ramp. Jet Bike (narrowest, w:8) lands at -0.06x, Go-Kart (short AND narrow) at -0.04x — small penalties, not drastic ones, matching "a bit less but not that much."

Also wired `calculateMultiplier()` into both Garage car-equip click handlers (switching to an owned car, and buying+auto-equipping a new one) — without this the live Settings-screen MULTIPLIER readout would've gone stale the moment a car choice actually started affecting it, the same class of bug Batch 126 already fixed for the lanes stepper.

**Verification**: live-tested in the Browser pane — computed the bonus for every car in `GARAGE_CARS` and confirmed the ranking/magnitudes match intent (Road Train the clear standout, narrow bikes a small penalty, Stock and other baseline-height cars exactly 0); confirmed the Settings-screen MULTIPLIER readout genuinely changes live (1.7x → 2.7x) both from a direct `calculateMultiplier()` call AND from an actual Garage tile click (not just a manual function call); ran a live 800-frame gameplay simulation as Stock with zero console errors. Test `localStorage` cleared afterward.

---

## 2.53.0 — 2026-09-01 03:45: Batch 127 — Difficulty setting (traffic density, speed unchanged)

Follow-up to the difficulty design discussion raised alongside Batch 126 — "do it." New DIFFICULTY row (CALM/RECKLESS/SUICIDAL segmented control, same widget pattern as the rest of the redesigned Settings screen), placed next to ROAD LANES since both affect traffic.

**Scope, exactly as discussed**: traffic density only — `spawnChance` (the main loop's per-frame spawn-roll) now multiplies by `DIFFICULTY_DENSITY[config.difficulty]` (calm 0.6x, reckless 1.0x — today's exact unchanged baseline, suicidal 1.6x). The speed ramp itself is untouched, per direct instruction. Score multiplier gets a small bonus for the added risk (calm +0, reckless +0.15, suicidal +0.4) — reckless (the default) still getting a small bonus, not zero, matches how every other already-baseline setting in this formula works (e.g. 4 lanes already gets +0.1 as its default).

**The free-lane guarantee** (the user's own explicit concern, and the reason this took real verification rather than just shipping the density multiplier): `canSpawnAt()`'s existing `topBlockedLanes` check already refuses a spawn if it would leave zero lanes clear near the top of the screen — this logic didn't need to change, since it re-evaluates fresh on every single spawn attempt regardless of how often those attempts happen. What DID need actual proof, not just code-reading confidence, was whether cranking density to 1.6x could somehow still produce a moment with no clear lane — especially with long vehicles (several Garage cars, trucks) in the mix, which occupy a lane's danger zone longer than short ones.

**Verification**: live-tested in the Browser pane — confirmed the live MULTIPLIER preview updates correctly for all 3 tiers (1.5x/1.65x→1.7x/1.9x at 4 lanes); ran the real safety check directly against the invariant `canSpawnAt()` is meant to protect (not just trusting the code) — 2,000 frames at SUICIDAL density for EACH of 3/4/6/10 lanes, sampling every frame for "are all lanes simultaneously blocked near the spawn zone," with long vehicles (height >40px) confirmed genuinely present throughout each run (940-4,555 sightings depending on lane count) — **zero violations across all 8,000 sampled frames**. Also ran a full real 1,000-frame gameplay simulation at SUICIDAL/4-lanes with zero console errors. Test `localStorage` cleared afterward.

---

## 2.52.0 — 2026-09-01 03:15: Batch 126 — Settings screen redesign (1A "STACK"), renamed from Setup, same slider design added to the pause menu

Ported option 1A ("STACK — one list, plain read") from the user-uploaded `Settings Menu Designs.dc.html`, adapted to the game's own CSS vars/fonts rather than the mockup's raw hex/font values. "Setup" renamed to "Settings" everywhere (main menu button, screen header).

**New row types**, all proxying into the same hidden `<select>` elements every downstream read (`launchGame()`, `calculateMultiplier()`) already used — so none of that logic needed to change, this is a UI skin swap over the same data flow: a stepper (ROAD LANES), segmented controls (CONTROL TYPE, STEERING BUTTON INPUT), toggle switches (HOLD FOR MULTIPLE LANES, TILT STEERING, NIGHT MODE, SKIP CRASH ANIMATION), and restyled native volume sliders (SOUND, AMBULANCE/SIREN VOLUME — kept as real `<input type=range step=0.05>` rather than rebuilding the mockup's own pointer-drag JS, so 5% jumps and keyboard/touch support come for free). Header now shows the live MULTIPLIER readout (was a separate box below the grid); footer gained a START RUN button alongside BACK, calling the same `launchGame()` the main menu's own button uses. Hint text is now always-visible inline copy under each row (matching 1A's own hint pattern) instead of the old hover-triggered tooltip icon — that whole mechanism (`.tip-wrap`/`.tip-icon`/`.tip-text` CSS, its JS injection pass) is now fully orphaned and removed, along with `.settings-grid` and `.setting-range` (also fully orphaned).

**Real bug fixed along the way**: `calculateMultiplier()`'s live Settings-screen preview read `config.lanes` for the lane-count bonus — a field that only ever updates inside `launchGame()`, so the preview stayed stale until a run actually started (night mode's own bonus was already reading its select directly, correctly, this was an inconsistency between the two). Now reads the lanes select directly too. This was a real fix required to make the new stepper feel functional, not an unrelated cleanup — the whole point of promoting MULTIPLIER into the header is that the player watches it update live as they adjust settings.

**Ambulance/siren slider colored red, sound slider colored amber**, per direct request, so the two are visually distinct at a glance.

**Pause menu got the same slider design**, per direct request — 2 new live sliders (not just the existing MUTE toggle) so volume can be fine-tuned mid-run, not just muted. Both Settings' and Pause's copies of each slider (master, siren) are kept in sync by a single new `syncVolumeUI()` — changing either one's slider immediately updates the other, plus `config`/localStorage. `togglePauseMute()` refactored to route through this same function rather than touching each slider by hand.

**Confirmed still holding after the rewrite**: sound still defaults to muted on a first-time session (Batch 124), which structurally gates OFF every sound including sirens (`startSiren()` returns `null` while `config.soundEnabled` is false) regardless of the independent siren slider's own 70% default value.

**Deliberately not included**: the design doc's own DIFFICULTY row (segmented CALM/RECKLESS/SUICIDAL) — raised separately as an open design question in the same message, not a decided feature; see the difficulty discussion below, nothing implemented for it this batch.

**Verification**: live-tested in the Browser pane — confirmed the lanes stepper live-updates the multiplier correctly at 3/9/10 lanes (including the stale-read fix, and the 10-lane cap); confirmed the control-type segmented control and all 4 toggles correctly read/write their hidden selects; confirmed both sliders sync bidirectionally between Settings and Pause (value, %, label, `config`, localStorage) and render the correct colors (amber `#f5b32a`, red `#e63946` — the game's own `--c-amber`/`--c-red`); confirmed START RUN launches a real run and BACK still returns to the menu; confirmed mute/unmute correctly zeros/restores across both sliders' every copy; confirmed a fresh session still defaults to fully silent. Ran 800 live gameplay frames with zero console errors. Test `localStorage` cleared afterward.

---

## 2.51.0 — 2026-09-01 02:30: Batch 125 — all 4 "ready to build" backlog items: ability-usage row, pause mute, siren volume, leaderboard car icons

Picked up all 4 items PLAN.md already had fully scoped with no open questions, in one batch per direct request.

**Result-screen ability-usage row**: new 8th stat-row, label AND which count it shows both depend on which ability the run actually used — `config.ability` is snapshotted onto `CS.snapshot` at crash time so the label can't drift even if config changes before the result screen renders. Jump shows `jumpedOverCount` (a NEW run-scoped counter — deliberately distinct from the existing `jumpsUsed`, which counts ability ACTIVATIONS; one jump can clear 0+ cars), incremented at the exact site that already sets `v.jumpedOver = true`. Ram shows the already-existing `ramsUsed`. `ability === 'none'` hides the row entirely rather than showing a bare "0".

**Pause-menu mute button**: a toggle (not a full volume control, per the PLAN note's own "doesn't need whole settings"), remembers both the master AND siren volume levels from right before muting so unmuting restores them exactly. Keeps the Setup sliders and their localStorage persistence in sync, so muting from pause behaves identically to a real Setup change. Real subtlety caught during implementation: `musicTick()`'s self-perpetuating loop stops rescheduling itself the moment `config.soundEnabled` goes false — just flipping the flag back to true on unmute isn't enough to bring music back, `startMusic()` has to be called explicitly.

**Independent siren volume slider**: new Setup slider + `config.sirenVolume`, persisted the same way `soundVolume` already is. `updateSirenVolume()`'s ceiling formula switched from `0.35 * config.soundVolume` (tied to the master) to `0.35 * config.sirenVolume` — the only site that formula lived. Defaults to 70% (not muted, unlike the Batch 124 master default) since it's meant to matter once the player actually turns general sound on.

**Leaderboard car icons**: per a screenshot showing exactly where they should sit (in the empty space between the score/meta block and WEIGHT, left-aligned), added a new fixed-width grid column and reused `drawCarTileSprite()` — the exact same sideways-sprite renderer the Garage grid already uses — no new rendering code needed, just a new canvas element painted after the row's `innerHTML` is set (same ordering the Garage's own tile-building already relies on).

**Verification**: live-tested in the Browser pane — confirmed both leaderboard icons render real (non-blank) pixel data including a long car correctly producing a wider canvas; confirmed the ability row shows the right label+count for jump/ram and hides entirely for 'none'; confirmed a mute→unmute cycle restores exact prior volume levels for both sliders and the button label syncs correctly; confirmed the siren slider computes fully independently of the master (0.2 vs 1.0 master volume gave identical siren output); confirmed a fresh session still defaults master to muted / siren to 70%, matching Batch 124's intent. Ran 1,000 live gameplay frames including a mid-run pause/mute/unmute cycle with zero console errors. Test `localStorage` cleared afterward.

---

## 2.50.1 — 2026-09-01 01:45: Batch 124 — sound now defaults to muted

Direct feedback: "happened that I am gaming and it starts playing in the background" — a first-time visitor (no saved `soundVolume` in localStorage) got music/SFX at 70% by default. All 3 places that default lived — the Setup slider's initial HTML `value`/label, the `localStorage.getItem('soundVolume') || '0.7'` fallback, and `config`'s own initial `soundVolume`/`soundEnabled` literals — switched from `0.7`/`true` to `0`/`false`. Anyone who already set a volume keeps their saved preference untouched; this only changes what a brand-new player gets before ever touching the slider.

**Verification**: live-tested in the Browser pane with `localStorage` fully cleared (a genuine first-time-visitor state) — confirmed the slider, its label, `config.soundVolume`, and `config.soundEnabled` are all muted/off before touching any setting, and confirmed a real `launchGame()` run also starts muted. Test `localStorage` cleared afterward.

---

## 2.50.0 — 2026-09-01 01:30: Batch 123 — 3 new biomes (Coast/Mountain/River) + river & underpass crossing structures

Ported from a new design doc, `Panorama Biomes.dc.html` (per direct instruction — "implement them + new side structures - river and road," explicitly skipping the doc's own "FULL PANORAMA" demo canvas, which was just a preview stitch, not a feature to build). Real design decisions were resolved with the user before writing any code: the 3 new biomes are added **alongside** the existing 5 (meadow/forest/farm/suburb/city), not replacing any; the doc's full-width lane-aware terrain art was **adapted to the existing narrow 18px side-strip system** rather than rewriting the road-scene renderer; and the 2 new "crossing" structures are **fixed set-pieces**, positioned the same way the existing bridge overpasses are, rather than auto-inserted at every biome boundary.

**3 new biomes** (`BIOMES`/`GROUND`): Coast (asymmetric per the doc — sea eating into the L strip, dense forest fully repainted onto the R strip, "tells you which way you are facing"), Mountain (rising rock face shaded lit-toward-shoulder/dark-away-from-it, snow caps sparsely dusted near the top of each rock band), River (grass fading into a meandering riverbank that snakes along the strip's length via a sine+noise bank offset). Each got its own ground-pass texture, a "hard" (stone-look) shoulder for Mountain/River, and a matching prop table (dense trees on Coast's forest side, sparse rocks/conifers on Mountain, sparse bushes/trees on River's banks) — all reusing the existing sprite functions (`sprTree53`, `sprRock53`, etc.), no new art assets. `BIOME_CYCLE` grew from 800 to 1200 slots (19200→28800px, still a whole multiple of 24) to fit the 3 additions without touching the 5 originals' slot counts.

**2 new crossing structures** (`CROSSINGS`/`drawCrossing()`): a river crossing and a side-road underpass, ported from the doc's `crossHalf()`. Unlike the existing `BRIDGES` (which composite AFTER traffic, since a bridge deck should occlude cars passing under it), crossings are drawn in the GROUND layer — called from `drawRoadScene()` right after the verge-strip blit, BEFORE the asphalt/curb/dash passes — so those redraw the real road cleanly on top and punch a clean line through the crossing scene, the exact layering trick the design doc's own `crossHalf()`+`road()` call order uses. Self-contained (own grass/fringe dressing, doesn't sample whatever biome verge is actually underneath) and full canvas-width, framed by stone abutments and a low parapet right at the road edge either side.

**Verification**: live-tested in the Browser pane — confirmed `BIOMES` slot total (1200×24) exactly matches the new `BIOME_CYCLE`; confirmed `biomeAt()` correctly resolves into all 3 new biomes at their expected cycle offsets, and independent of lane count; sampled real pixel colors from the baked strip buffers to confirm Coast's L/R asymmetry, Mountain's lit/shaded rock banding, and River's grass-to-water transition all render as intended (not blank/black); confirmed both crossing structures draw with zero errors and that the road/curb genuinely repaints on top of the water/underpass band at the road's own position (the layering trick actually works, not just compiles); ran a live 3,000-frame gameplay simulation with zero console errors. Test `localStorage` cleared afterward.

---

## 2.49.0 — 2026-09-01 00:45: Batch 122 — Daily Gift / Missions menu placeholders, "HIGHWAY" kicker simplified

**Menu kicker**: "HIGHWAY 47" → "HIGHWAY 404" (a quick joke, direct request) → **"HIGHWAY"** (final, per direct request) — now reads as one phrase with the title below it: "HIGHWAY RECKLESS DRIVING."

**New placeholder buttons**: DAILY GIFT and MISSIONS added to the main menu as a 3rd `.btn-row`, per direct request ("add for now empty buttons"). Both use the existing `.btn-disabled` class (dimmed, `pointer-events:none`) rather than a click handler that silently does nothing — visibly inert, not broken. Reserves their spot on the menu ahead of PLAN.md's still-unscoped "daily gift" and achievements/missions ideas.

**Verification**: live-tested in the Browser pane — confirmed the kicker text, confirmed both new buttons are genuinely inert (`pointer-events: none`, `.btn-disabled` class present), confirmed the menu panel doesn't overflow its container with the extra row. Ran with zero console errors.

---

## 2.48.3 — 2026-09-01 00:30: Batch 121 — Champion tier hue-rotate slowed 5x

Direct feedback: "the champion color changes colors way too quickly." `legendaryHueShift`'s animation duration bumped 4s → 20s (still `linear infinite`).

---

## 2.48.2 — 2026-09-01 00:20: Batch 120 — dev menu: custom XP/coin amounts instead of fixed 500/1,000

Direct request: "make it so that I can choose to add custom amount of coins/XP." The old ADD 500 XP / ADD 1,000 COINS buttons are now ADD XP / ADD COINS, each paired with its own number input (defaulting to the old 500/1000 values) in a new `.dev-menu-row`. Blank, non-numeric, or negative input falls back to a harmless 0 (no-op click), never a `NaN` written into `allTimeStats`.

**Verification**: live-tested in the Browser pane — confirmed a custom XP amount (1,234) both adds correctly AND crosses a level-up boundary properly (landed at level 2 with the correct 234 leftover XP); confirmed a custom coin amount (777) adds exactly; confirmed a blank XP input and a negative coin input (`-50`) both no-op cleanly with zero change to `allTimeStats`. Ran with zero console errors. Test `localStorage` cleared afterward.

---

## 2.48.1 — 2026-09-01 00:05: Batch 119 — Scores tab multiplier range shows the run's real peak, not a theoretical cap

Direct feedback: "it shows from what is base multiplier and how much it goes up to... change it so it shows the max multiplier you achieved in that run" — e.g. if a run's base was 1.5x but the player only ever reached 2.6x (never touching max speed), the leaderboard should show "1.5x → 2.6x," not "1.5x → 3.0x" (what Batch 113's cap formula would compute as the theoretical ceiling for that base). The fix turned out to need no new tracked field — `entry.multiplier` (the value at crash time) was already established back in Batch 108 as the run's true peak, since the live multiplier only ever climbs during play, never drops. Swapped the leaderboard's second value from the computed `multStart × (1 + SPEED_MULT_BONUS_RATIO)` cap to `entry.multiplier` directly. Hover tooltip reworded from "starting value up to this run's speed cap" to "starting value up to the highest it reached this run."

**Verification**: live-tested in the Browser pane — seeded a fake leaderboard entry (`multStart: 1.5`, `multiplier: 2.6`) and confirmed the rendered range shows "1.5x → 2.6x" (the actual achieved peak), not "1.5x → 3.0x" (the theoretical cap the old formula would have computed) — proves the fix genuinely changed the displayed value, not just the code path. Ran with zero console errors. Test `localStorage` cleared afterward.

---

## 2.48.0 — 2026-08-31 23:50: Batch 118 — level-badge rank names (Rust → Champion)

Direct follow-up, same session as Batch 117: implemented the rank-name text line that had been explicitly deferred pending a names/colors proposal. First round of feedback on the proposal itself: "iron is better than bronze though, maybe replace iron with something else" — correct catch, Iron historically supersedes Bronze (post-Bronze-Age metallurgy), so using it as the tier BELOW Bronze read backwards. Presented 4 alternatives (Rust/Tin/Scrap/Copper); user picked **Rust** — car-themed, no material-hierarchy ambiguity. `LEVEL_TIERS[0].name` renamed Iron→Rust (color unchanged), `LEGENDARY_TIER.name` set to **Champion** (the user's own pick for the level-101+ tier, "will be the best").

New `rankName(level)` returns `"<Tier> <Roman numeral I-X>"` within a 10-level tier (e.g. "Rust I", "Diamond X"), or just "Champion" with no numeral past level 100. Rendered via a new `.level-badge-rank` element added to all 3 level-badge instances (Menu/Garage/Stats), sitting directly above the existing XP line — both now live inside a shared `.level-badge-text` flex-column wrapper (was just the bare XP div before), so the Menu's vertical layout and the Garage/Stats horizontal layout both stack rank-above-XP correctly through the same `order`-based CSS the XP text already used, no per-screen special-casing needed. Rank text color is set dynamically to match that level's tier color (`paintLevelBadge()`'s existing `color` variable), same as the level number already does.

**Verification**: live-tested in the Browser pane — confirmed `rankName()` across every tier boundary (1, 10, 11, 90, 91, 100, 101, 150) returns the correct name+numeral or flat "Champion"; confirmed the rendered rank text color exactly matches the ring/number color for a mid-tier level (Bronze V); confirmed no layout overflow on the Stats badge (`getBoundingClientRect()` well within viewport); confirmed the Garage instance renders correctly too. Ran with zero console errors. Test `localStorage` cleared afterward.

---

## 2.47.0 — 2026-08-31 23:30: Batch 117 — ability bar ready-threshold fix, Garage Stock DEFAULT label, Stats tab cleanup, level-badge legendary tier

**Ability bar mismatch fixed**: the numeric jump threshold (`JUMP_MIN_ENERGY`, raised from 25 to 30 per direct feedback — "at least three or more bars") and the bar's own visual "ready" glow were actually two separate, previously-mismatched checks — the glow was hardcoded to only light up at a full 100%, even though a jump could already fire at 25%+. This was very likely the real source of the reported confusion, not just the exact threshold number. Fixed by making the glow ability-aware: jump now reads `ready` off `JUMP_MIN_ENERGY`, ram still requires 100. Also removed the small tick-mark notch `drawAbilityBar()` used to draw at the old 25% mark — no longer meaningful now that "ready" is shown via the glow itself.

**Garage Stock card**: added a display-only "DEFAULT" label matching the rarity-badge slot every other car uses, implemented as a special case in `buildCarTile()` rather than a real `car.rarity` field — Stock is deliberately excluded from `GARAGE_NPC_RARITY`'s derivation (redundant with the plain sedan NPC body, per Batch 99) and a real rarity field would have accidentally made it spawn as traffic. Also fixes the reported off-center look as a side effect, since Stock's tile now has the same row structure as every other card.

**Stats tab cleanup**: removed the WRECKED BY card and PICKUPS row entirely, along with their now-unused helpers (`drawSidewaysCentered()`, `DEATH_TYPE_LABELS`, `DEATH_FIG_FOOTPRINT`, `DEATH_TYPE_SPRITES`) — `drawSideways()` itself is kept, still used by the Garage's own card-sprite renderer. `allTimeStats.deathsByType` is still tracked in the background even with no display for it — existing user data, no reason to stop collecting it just because this one view went away. "MOST IN ONE RUN" renamed to "MOST DODGED (1 RUN)" for clarity. TOTAL PLAY TIME / LONGEST SURVIVAL now use the same compact `Xm Xs` format as the result screen, instead of `M:SS`.

**Level badge — legendary tier**: added a `LEGENDARY_TIER` (magenta `#ff2ec4`, animated) for level 101+, past Diamond's cap at 100 — permanent, doesn't advance further. The ring and number now hue-rotate through a slow 4s cycle via CSS (`@keyframes legendaryHueShift`) rather than a fixed color, so it reads as the "most legendary" tier without needing a per-frame canvas redraw. 3-digit levels (100+) also get a smaller font (`.level-badge-num-3digit`) so they still fit inside the ring.

**Also confirmed, no code change needed**: close-call score is already 100 base (`CLOSE_CALL_BASE_SCORE`), matching a request that turned out to already be shipped.

**Investigated, not a bug**: the reported ~30-second spawn drought. Ran a live 500-second simulated playthrough (30,000 stepped frames, collision disabled so the run wouldn't end early) tracking every vehicle spawn — longest gap found was 9.3s, with zero gaps anywhere near 20s let alone 30s across 420 total spawns. The spawn system itself doesn't appear capable of producing a genuine 30s drought under normal play; the most likely innocent explanation is the browser tab losing focus/being backgrounded for a stretch (this game's loop is frame-driven via `requestAnimationFrame`, which browsers throttle or pause entirely on an unfocused tab — real time keeps passing with no frames, and therefore no spawns, running). No code change made; flagged to revisit only if it reproduces again with the tab confirmed foregrounded the whole time.

**Deferred, per direct instruction**: Roman-numeral rank names above the level badge's XP text — the user asked to see proposed tier names + which existing colors they'd reuse before any code gets written for that specific piece.

**Verification**: live-tested in the Browser pane — confirmed `JUMP_MIN_ENERGY` reads 30; confirmed `levelTier(100)` still returns Diamond and `levelTier(101)`/`levelTier(150)` both return the new Legendary tier; confirmed `paintLevelBadge()` at level 101 applies both the 3-digit font class and the legendary animation class, and that the animation actually computes as active (`getComputedStyle(...).animationName === 'legendaryHueShift'`) — then confirmed a normal level (42) shows neither, no regression; confirmed Stats tab renders cleanly post-cleanup (no WRECKED BY/PICKUPS elements in the DOM, renamed label present, compact time format in both fields); confirmed the Garage Stock tile's rendered HTML includes the DEFAULT label with the same structure as a rarity-tagged card; ran the 500-second spawn-gap simulation described above. Ran a full live playthrough with zero console errors. Test `localStorage` cleared afterward.

---

## 2.46.1 — 2026-08-31 22:30: Batch 116 — jump drop-shadow removed entirely

Direct feedback with a screenshot: the jump drop-shadow (Batch 111, generalized from an original stock-only one) rendered badly mismatched — too wide or not wide enough — for some cars, especially narrow ones. Rather than debug the exact sizing mismatch, the user asked whether it might be simpler to just remove it ("it doesn't really add anything and only creates unnecessary problems"), and after a quick gut-check discussion, agreed it wasn't worth keeping — at this pixel-art scale and game speed a drop-shadow is a subtle depth cue that's easy to get wrong and low-value either way. Removed `drawJumpShadowNative()` and its call site in `Player.draw()` entirely; `drawPixelCar()`'s own original shadow-drawing (which predates Batch 111 and only ever applied to Stock) is also gone, not just the generalized version — no car gets a jump shadow anymore. PLAN.md's tracking note updated from "done" to "removed," with a note not to re-add without being asked.

**Verification**: live-tested in the Browser pane — confirmed `player.draw()` while jumping produces zero errors across 6 cars spanning very different sizes (Stock, Hot Hatch, School Bus, Road Train, Go-Kart, Jet Bike); confirmed no remaining reference to the removed function anywhere in the file. Ran a full live playthrough with zero console errors.

---

## 2.46.0 — 2026-08-31 22:00: Batch 115 — DISCOVER ALL dev button, no more partial ability bars, ambulance/close-call bonus energy

**Dev menu**: added a 4th action, DISCOVER ALL CARS — sets `allTimeStats.discoveredCars` to every `GARAGE_CARS` key at once, a testing shortcut for skipping the "spot it on the road first" gate car by car.

**No more partial bars**: per direct feedback, releasing (or running out of energy) mid-way through draining a bar used to leave a fractional amount behind (e.g. 71 energy — a bar 1/10th spent). Now the exact frame `jumpHeld` transitions from held to released — whether the player let go via keyup/mouseup (a separate handler that may fire before `update()` runs) or energy simply ran out — `energy` floors down to the nearest whole 10-unit bar, so the bar you were mid-way through using always counts as fully spent. Tracked via a new `this._prevJumpHeld`, compared against the current `jumpHeld` each frame, so the transition is caught exactly once regardless of which of the two release paths triggered it.

**New energy sources**: a GROUNDED ambulance pass (not jumped over) now refills +5 bars (50 energy) instead of the normal +1 — explicitly NOT when jumped over, which falls back to the standard +1 bar, per direct feedback ("it is not the case when you jump over it"). A close call now also refills +4 bars (40 energy), on top of its existing score/XP bonus, gated the same way every other refill site is (idle + past the post-landing recharge delay).

**Verification**: live-tested in the Browser pane — confirmed DISCOVER ALL marks all 52 cars discovered in one click; confirmed releasing mid-drain at 71 energy floors to exactly 70, and running energy fully to 0 naturally still lands correctly on a bar boundary; confirmed a grounded ambulance pass grants exactly +50 energy, a jumped-over ambulance only +10 (same as a normal car), and a normal grounded pass +10; confirmed a close-call credit alone grants exactly +40 energy in isolation, and traced a real close-call through the actual game loop (not just a manual re-simulation) to confirm the code path genuinely fires. Ran a full live playthrough with zero console errors.

---

## 2.45.0 — 2026-08-31 21:00: Batch 114 — dev menu (Add XP / Add Coins / Reset All), bigger lock icon

**New: dev menu**, direct request ("for me, for testing"). A small "DEV" trigger in the main menu's footer (opposite the version number) opens a themed overlay (mint-bordered, to visually distinguish it from the red destructive-confirm dialog) with 3 actions: ADD 500 XP (`gainXP(500)`, persisted, repaints the level badge), ADD 1,000 COINS (`allTimeStats.totalCoins += 1000`, persisted), and RESET ALL PROGRESS — which reuses the exact same 4 localStorage keys the existing `?resetprogress=1` one-shot URL escape hatch already clears (Batch 86), routed through the same themed confirm dialog every other destructive action uses, then reloads the page so every in-memory variable re-initializes from the now-empty storage rather than needing to be hand-reset one by one. This is a deliberate, explicit reversal of Batch 82/86's "no in-UI way to wipe progress" stance — that removal was specifically about protecting PLAYERS from an accidental-deletion button; this is a separate, clearly-labeled dev tool the user asked for directly. Add XP/Add Coins don't need confirmation (non-destructive, reversible via Reset); the dev menu closes itself before opening the Reset confirm dialog, since both overlays share a z-index and would otherwise stack.

**Lock icon made bigger**: per direct feedback ("they are so small they look like they're not symmetrical"), the paint-color lock icon's CSS display size went from 12px to 18px — the canvas itself is still native 12×12 pixel art (`renderLockIcon()`, Batch 107, untouched), only the upscale factor changed, same `image-rendering:pixelated` technique used everywhere else in this file for crisp scaled pixel art. Still fits comfortably inside the 28×28 swatch and stays exactly centered.

**Also**: added a PLAN.md backlog item for a separate siren/emergency-vehicle volume slider (direct request) — confirmed via code read that `updateSirenVolume()` currently derives its ceiling straight off the same master `config.soundVolume` as music/every other effect, so there's no way today to turn sirens down independently. Not implemented, per the request — captured for a future batch.

**Verification**: live-tested in the Browser pane — confirmed the dev menu opens/closes correctly and stays open after Add XP/Add Coins clicks (so repeated testing clicks work); confirmed Add XP correctly triggers a real level-up (500+500=1000 crosses `levelReq(1)`) with the menu's level badge updating live; confirmed Reset All's confirm dialog shows correctly with the dev menu already closed (no overlay stacking), Cancel leaves all stats untouched, and confirming actually clears all 4 keys and reloads to genuinely fresh defaults (level 1, 0 coins) — verified with real seeded data (a fake score entry, a non-default selected car) beforehand to confirm it was really wiped, not just untouched. Confirmed the lock icon's new display size (18×18) via computed style, still exactly centered and still fitting inside its swatch. Ran a full live playthrough with zero console errors.

---

## 2.44.0 — 2026-08-31 20:00: Batch 113 — speed-scaling multiplier is now proportional to base, not a flat +1.0

Discussed as a design question first (was the flat +1.0 bonus at max speed fair to harder base setups — long cars, night mode, more lanes?), then implemented per the user's decision. The live speed bonus (`multiplier` ramping from `baseMultiplier` up to some max as `currentSpeed` approaches `maxSpeed`, Batch 69) used to add a FLAT `+1.0` regardless of how hard the base setup was — meaning a 1.0x-base run doubled at top speed (100% relative gain) while a 2.0x-base run only gained 50%, backwards from "harder setup should be rewarded more for surviving at speed." Now the bonus is proportional: `multiplier = baseMultiplier × (1 + speedRatio × SPEED_MULT_BONUS_RATIO)`, with `SPEED_MULT_BONUS_RATIO = 1.0` meaning every run now doubles at top speed regardless of its base — a 1.6x base run now tops out at 3.2x (was a flat 2.6x). `SPEED_MULT_BONUS_MAX` (the old flat-add constant) renamed to `SPEED_MULT_BONUS_RATIO` since its meaning genuinely changed, not just its value. Also fixed the leaderboard ledger's "start → cap" multiplier range (Batch 109), which computed the cap with the old additive formula (`multStart + SPEED_MULT_BONUS_MAX`) — now `multStart × (1 + SPEED_MULT_BONUS_RATIO)`, matching what actually happens in gameplay.

**Verification**: live-tested in the Browser pane — confirmed `multiplier` exactly equals `baseMultiplier` at zero speed ratio, `baseMultiplier × 1.5` at half speed ratio, and `baseMultiplier × 2` at full speed ratio (tested at base 1.5: 1.5 / 2.3 / 3.0, all exact); confirmed the leaderboard's displayed cap for a `multStart:1.6` entry now shows "1.6x → 3.2x" (was "1.6x → 2.6x" under the old formula); confirmed no other stale reference to the renamed constant remains. Ran a live playthrough to a natural crash with zero console errors.

---

## 2.43.0 — 2026-08-31 19:00: Batch 112 — jump-over score/coin rework, ability bar rebuilt as pass-triggered, Performance Score delta bug fixed

Three items promoted from the previous turn's "future batches" dump straight to implementation.

**Jump-over rewards, now genuinely differentiated from a grounded pass**: score is exactly 2x (`creditVehiclePass()`'s existing `score += Math.round(pts * multiplier)` gained a `jumpMult` factor, 2 when `v.jumpedOver`, applied to both the score add and the XP gain — computed in ONE place, not also at the jump-over collision site, so a jump can never silently stack to 3x). The coin bonus (already meaningfully bigger than a grounded pass, at a full `VEHICLE_POINTS[v.type]`) is nerfed from 10x down to 5x of the grounded-pass baseline, per direct feedback ("I think it's too much") — `Math.round((VEHICLE_POINTS[v.type] || 10) / 2)` at the collision site where `v.jumpedOver` first flips true.

**Ability bar rebuilt from continuous time-based regen to discrete pass-triggered refill**: the old `this.energy += 0.25 + speedRatio * 0.25` per-frame regen (while idle) is gone entirely. Energy now only increases from `creditVehiclePass()` — +10 (1 of the bar's 10 visual cells) for a normal pass, +20 (2 cells) for a truck — gated the same way the old regen was (idle + past the post-landing recharge delay), so a pass credited mid-jump or in the brief cooldown right after landing still doesn't refill. New `this.displayedEnergy` eases toward the real `this.energy` every frame (snapping the last stretch to avoid infinite asymptotic drift) and feeds the ability bar's rendering ONLY in the idle/charge/ready state — jump drain still reads/draws the real energy directly, unaffected, since it was already smooth and didn't need this. This gives the requested fill ANIMATION on each discrete refill without touching gameplay-critical logic (the jump-ready gate and drain both still read the real, un-eased `this.energy`).

**Real bug fixed — Performance Score's "+X" now an honest delta, not an isolated value**: `saveScore()` used to compute `perfScore` as just this run's own weighted contribution at its new rank, with no awareness that every entry now ranked below it just had its own weight shrink by a notch too (and can even get pushed out of the top-100 entirely). Factored the weighted-sum math out of `calculatePerformanceScore()` into a reusable `weightedPerformanceSum(arr)`, and `saveScore()` now snapshots it once BEFORE the new entry is inserted and once AFTER, showing the actual `after − before` delta as "+X" — exactly the fix the user proposed themselves. The stored/displayed AGGREGATE total was always correct (a full recompute every time); only this one per-run figure was overstated.

**Verification**: live-tested in the Browser pane — confirmed jump-over score is exactly 2x a grounded pass across normal/truck vehicle types (40 vs 20, 80 vs 40), confirmed the jump-over coin bonus is exactly 5x the grounded baseline for normal/truck/ambulance (5/10/25); confirmed `creditVehiclePass()` correctly adds +10/+20 energy, and that the refill is fully blocked both while `abilityState==='jumping'` and during an active `rechargeDelay`; confirmed `displayedEnergy` genuinely eases across multiple frames (0→9→16→...→43 over 10 frames) rather than snapping, and fully converges to exact equality once close; confirmed energy no longer passively increases over 200 idle frames with no vehicle passed; confirmed the Performance Score delta math against a hand-seeded 3-entry leaderboard — a new #1 that would have shown "+1100" under the old isolated formula correctly showed "+971" once the 3 existing entries' own shrinking weights were accounted for, and confirmed the simple non-displacing case (nothing shifts) still matches its own isolated value exactly, as it mathematically should. Ran a full live playthrough to a natural crash with zero console errors throughout.

---

## 2.42.0 — 2026-08-31 18:00: Batch 111 — real hitbox bug fixed (36 of 52 cars silently used the default size), jump shadow generalized to every car

**Real bug, direct feedback**: "almost all cars have the same hitbox as the default one... with longer cars you can go off the screen." Root cause: `Player`'s constructor only gave a real per-car hitbox to the 16 `hitboxW` cars from Batch 89 — every other car (all 36 native-14-wide ones: the original 10 plus Batches 102/106's 22+4) fell straight through to the fixed `PLAYER_WIDTH`/`PLAYER_HEIGHT` (18×31) regardless of its own actual size. School Bus (`h:44`) and Fire Engine (`h:42`) were both silently being hit-tested as if they were 31px tall. Since `maxY` is derived from height (Batch 90), an understated height let the reverse-clamp put the player lower than the sprite could actually fit, hanging the visually-taller sprite's bottom off-canvas — exactly the reported symptom.

**Fix, made properly automatic per direct instruction** ("make it automatic... not set every single car with a fixed hitbox... count the sprite size and set the hitbox based on that"): `this.width = Math.round((selCar.hitboxW || 14) * CAR_SCALE); this.height = Math.round(selCar.h * CAR_SCALE);` — no more fixed-constant fallback for any car. This works because both numbers were already sitting right there on every `GARAGE_CARS` entry (width already always defaults to 14 unless `hitboxW` overrides it — that's the field's whole purpose; height is `h`, already used for drawing) — no per-car tuning table needed, the fix just reads what was already declared instead of a shared constant.

**Jump shadow, also generalized** (same session, same principle — "if it's just one shared function, not per-car, you can do it"): the drop-shadow was only ever drawn inside `drawPixelCar()`, the STOCK car's own dedicated sprite function — every other Garage car had NO shadow at all while airborne. Extracted a shared `drawJumpShadowNative(gctx, nativeW, nativeH, bx)`, called once from `Player.draw()` for whichever car is actually selected — same "one shared overlay pass" pattern the brake-light overlay already used (Batch 89). Wings (also jump-only, also currently stock-exclusive) were left alone — only shadows were asked about, and this was already flagged in PLAN.md as staying stock-only.

**Verification**: live-tested in the Browser pane — confirmed `Player.width`/`height` now exactly matches each car's own real dimensions across a spread including School Bus, Fire Engine, Coachbuilt, Road Train, and Go-Kart (previously-`hitboxW` cars numerically unaffected — this only fixed the 36 that were silently wrong); confirmed a School Bus reversed to `maxY` now lands its sprite's bottom edge at exactly `canvas.height - 1`, never past it; confirmed `player.draw()` while jumping produces zero errors across 6 very differently-sized cars, and pixel-sampled the shadow function in isolation to confirm it draws the correct `(nativeW-2)×2` footprint for a car's real width rather than the old hardcoded 14; ran a live playthrough and a forced crash-sequence (Road Train) with the corrected dimensions — zero console errors throughout.

---

## 2.41.0 — 2026-08-31 17:00: Batch 110 — leaderboard LANES/SURVIVED tooltips, compact SURVIVED format, real lock-icon stacking bug fixed

Direct follow-up to Batch 109. (1) LANES and SURVIVED had no hover tooltip at all (every other field did) — added: LANES reuses the design doc's own copy, SURVIVED is new wording matching the result screen's own "SURVIVED" label. (2) SURVIVED now uses the same compact format as the result screen (`formatTimeCompact()`: "6s" / "1m 12s") instead of the leaderboard's old M:SS — a previous batch (98) had deliberately left the leaderboard's time format alone when the result screen switched to compact, but this is a new, explicit direct request to make them match, so that boundary no longer applies here.

**Real bug, caught from direct feedback that the lock icon still looked semi-transparent after Batch 108's fix**: Batch 108 correctly diagnosed and fixed the ANCESTOR-opacity cascade, but the hazard-tape stripe overlay added in the SAME batch (a `::before` with `position: absolute; inset: 0`) reintroduced the identical symptom through a different mechanism — CSS stacking rules always paint a positioned element above a plain static one in the same context, regardless of DOM/pseudo-element order, so the semi-transparent stripes were compositing ON TOP of the lock-icon canvas (itself just a plain static child), not behind it as intended. Fixed by moving the stripe pattern into the swatch's own `background-image` (composited automatically after `background-color`, both always painting before ANY real child regardless of that child's `position`) instead of a separately-positioned overlay layer — this ordering is now correct by construction, not by which trick happens to win a stacking fight. Removed `.color-swatch`'s now-unused `position: relative` (was only there to anchor the removed `::before`).

**Verification**: live-tested in the Browser pane — confirmed SURVIVED renders "6s" for a 6-second run and "1m 12s" for a 72-second run; confirmed hovering LANES and SURVIVED shows the correct tooltip text and hides on mouseleave; confirmed the `::before` pseudo-element is gone entirely (`content: none`) and the stripe pattern is now part of the swatch's own computed `background-image`; confirmed the lock icon canvas itself is still exactly 84 black / 60 white / 0 transparent pixels (unchanged, still solid) with both its own and its ancestor's opacity at 1. Zero console errors across a full live playthrough.

---

## 2.40.0 — 2026-08-31 16:00: Batch 109 — Scores tab "ledger" redesign (user's own 1A doc), +X performance score, C/O font fix

**Result screen**: PERFORMANCE SCORE now shows as "+4,200" instead of a bare "4,200" — both the instant and animated (`countUp`) display paths.

**Scores tab, full redesign** from the user's own `Scores Tab Redesign.dc.html`, implementing option 1A ("LEDGER" — dense rows, hover-labelled numbers), adapted to this game's actual ~300-640px panel width and font scale rather than the mockup's standalone 660px desktop comparison sizing. Each saved run is now a 4-column grid row: rank · (score + car name, then lanes/time/multiplier-range on a second line) · weight% · a bordered PERFORMANCE-SCORE-contribution box. New hover-tooltip system (one shared floating element repositioned per hovered field, mirroring the doc's own `onMouseEnter`/`onMouseLeave` pattern) explains PLACE/SCORE/CAR/MULTIPLIER/WEIGHT/PERFORMANCE SCORE on hover. The header now shows the aggregate PERFORMANCE SCORE total (reusing the existing `calculatePerformanceScore()` the Stats tab already had — not affected by the lane filter, matches the doc: "the weighted sum of every run," not just the visible ones).

Three specific corrections from direct feedback on the doc's own copy: (1) the MULTIPLIER tooltip's "(from settings)" aside removed — just "starting value up to this run's speed cap" now. (2) The per-row PERFORMANCE-SCORE box lost its "PERF" abbreviation entirely — per direct feedback ("don't write any text in that box... only at the top"), it's just the number now; the full "PERFORMANCE SCORE" text appears exactly once, at the header aggregate. (3) The multiplier field now shows the actual settings-derived START value → the theoretical CAP (start + 1.0), not a single number — new `entry.multStart` (= `baseMultiplier` at save time) added to `saveScore()`'s saved entry; older saved runs don't have it and gracefully fall back to showing their one existing `multiplier` value with no arrow, same degradation pattern the car label already used (Batch 92).

**Real bug, also fixed**: the car name in a saved run's meta line (e.g. "COACHBUILT") was inheriting the page's body-default font (DotGothic16), whose C and O glyphs read as nearly identical at small sizes — exactly what was reported. Fixed by giving that field its own `'Silkscreen', monospace` font-family, the SAME choice the user's own design doc already made for this exact field (not a new font invented here) — Garage car-tile names already use Silkscreen too, so this makes car-name rendering consistent game-wide, not just a one-off fix.

**Verification**: live-tested in the Browser pane — seeded a mix of new-format (with `multStart`) and old-format (without) fake entries, confirmed the new ones render a start→cap range and the old ones fall back to a single value with no error; confirmed the header aggregate matches the Stats tab's own `calculatePerformanceScore()` output exactly; confirmed hovering each field shows the correct trimmed tooltip text (verified "(from settings)" is gone) and hides again on mouseleave; confirmed the per-row PERFORMANCE-SCORE box renders with zero extra text, just the number; confirmed repeatedly re-filtering by lane does NOT stack duplicate tooltip listeners on the static header element (the one-time-attached listener still fires exactly once); confirmed the car-name font is now Silkscreen via computed style; ran a real playthrough to a genuine crash and confirmed the freshly-saved score actually has `multStart` populated; confirmed "+X" formatting on both the instant and animated result-screen paths. Zero console errors throughout.

---

## 2.39.0 — 2026-08-31 15:00: Batch 108 — MULTIPLIER → MAX (not AVG), real opacity-cascade bug on the lock icon fixed

Direct follow-up to Batch 107, two corrections.

**MULTIPLIER, take 2**: direct feedback — an AVERAGE multiplier "doesn't tell the user anything," and the two options offered were dropping the row entirely or showing the run's PEAK ("at least it's a kind of information that provides something"). Went with peak, relabeled **MAX MULTIPLIER**. Turns out no new tracking was needed: `multiplier` is speed-derived, and `currentSpeed` only ever climbs (or holds at `maxSpeed`) while `gameActive` — it only decreases in the crash SEQUENCE's own deceleration, which runs after `gameActive` already flips false. So the live `multiplier` value captured at crash time already IS the run's peak by construction; `endRun()`'s snapshot just stores `multiplier` directly again. Verified empirically, not just reasoned about: sampled `multiplier` every frame of a real run and confirmed the running max exactly equals the value left over once the loop stopped (i.e. at crash). Since nothing reads `baseScore` anymore (it only ever existed to compute the now-abandoned average), removed the variable and all 5 of its read/write sites entirely rather than leaving it as dead state.

**Real bug, root-caused**: direct report — "the icons and the background is kind of transparent... shouldn't be at all transparent." The lock icon (Batch 105/107) WAS being drawn as fully solid black+white pixels — confirmed again via `getComputedStyle` on the canvas itself, which read `opacity: 1`. The actual cause: `.color-swatch.locked-swatch` had `opacity: .7` (Batch 105's fade), and CSS `opacity` on a parent dims its ENTIRE rendered subtree regardless of what any individual child's own `opacity` property says — so the solid-black plate was still compositing at 70% on screen, letting the page's background show through and reading as washed-out/transparent. Fixed by dropping the parent `opacity` rule entirely — the hazard-tape stripes added in Batch 107 (their own `.55`-alpha diagonal pattern) already read as "muted/locked" on their own, so there's no separate fade to reintroduce; the lock icon (now unaffected by any ancestor opacity) renders fully solid.

**Verification**: live-tested in the Browser pane — confirmed `.color-swatch.locked-swatch`'s computed opacity is now `1` (was `0.7`); confirmed the lock-icon canvas's own AND its parent's computed opacity both read `1`; sampled `multiplier` every frame across a real run to a crash and confirmed the post-crash value exactly matches the running max seen during play; confirmed the result screen's MAX MULTIPLIER row displays that same value; confirmed zero remaining `baseScore`/`avgMultiplier` references anywhere in the file; zero console errors across a full live playthrough.

---

## 2.38.0 — 2026-08-31 14:00: Batch 107 — result screen's BASE SCORE/MULTIPLIER never actually reconciled with SCORE; hazard-tape locked colors

**Real bug, root-caused**: direct report with a screenshot — 680 BASE SCORE × 1.8 MULTIPLIER = 1,224, but the actual SCORE shown was 1,102, and the user correctly suspected the multiplier math didn't add up. Traced it to `calculateMultiplier()`/the main loop's live speed-bonus update: `multiplier` isn't fixed for the run, it RAMPS from `baseMultiplier` up to `baseMultiplier + 1.0` as `currentSpeed` climbs toward `maxSpeed` over the course of a run (Batch 69, "you get more points as the speed goes up" — a deliberate mechanic, not a bug). Every scoring event applies whatever `multiplier` happens to be AT THAT MOMENT (`score += Math.round(pts * multiplier)`), so the number shown on the result screen — captured at crash time — is only ever the run's PEAK multiplier, never what was actually averaged in across the whole run. `baseScore × peak multiplier` was never going to equal `score` except by coincidence (a very short/instant-death run).

**Fix**: removed the BASE SCORE row entirely (the raw un-multiplied total doesn't mean much on its own and was the thing making the mismatch visible) and changed MULTIPLIER → **AVG MULTIPLIER**, now computed as `score ÷ baseScore` (falls back to the live `multiplier` only for a same-frame crash with nothing to divide by) — an honest number that, by construction, actually reconciles with the score shown right above it. The underlying live-ramping scoring mechanic itself is untouched (still intentional, still drives the HUD's live multiplier and coin payout) — this was a display-layer fix, not a scoring rework. Per direct feedback ("maybe base score isn't needed... too much confusion, doesn't give feedback") rather than just relabeling.

**Also this batch**: locked paint-color swatches — the amber "you can afford this" border (`.buyable-swatch`) is gone; every locked swatch now shares one plain grey border (`#8a93ad`, same grey the car grid already uses for "owned, not equipped"), per direct feedback ("don't include the golden frame and the dark frame, all locked colors should have the grey frame"). Added a diagonal yellow/black hazard-tape stripe overlay (`::before`, paints behind the real lock-icon canvas child by CSS spec) as the new "you don't have this" visual cue.

**Same-turn correction to the lock icon**: the very first pass at `renderLockIcon()` (Batch 105) drew a black lock glyph with a white outline — direct feedback caught this as backwards, the actual ask was "white icon... on black background." Rebuilt as a solid black backing plate (fills the whole 12×12 canvas — none of `GARAGE_COLORS`' 10 colors are literally black, so the plate never disappears against any of them) with the lock silhouette drawn in white on top, black keyhole punched into the white body. Verified via pixel-data sampling: exactly 2 colors present (84 black px, 60 white px, zero transparent/other), and the icon's own bounding-box center still matches its swatch's center exactly (0,0 offset).

**Verification**: live-tested in the Browser pane — reproduced the exact reported numbers (score 1102, baseScore 680) directly and confirmed AVG MULTIPLIER now shows 1.6x (1102÷680=1.621, correctly rounded), not the old misleading 1.8x; confirmed `#goBase` no longer exists in the DOM; confirmed both the instant and animated (`countUp`) result-screen paths render without error and the animated one settles on the correct value after its real timer finishes; confirmed locked swatches read `border-color: rgb(138,147,173)` (#8a93ad) via computed style, the `.buyable-swatch` class is gone from the DOM and its CSS rule removed, and the hazard-stripe `::before` background is present. Zero console errors across a full live playthrough.

---

## 2.37.0 — 2026-08-31 13:00: Batch 106 — 4 new "rarity row filler" cars from Reckless Vehiclesv4.dc.html

User's own upload, direct instruction: "add them." The doc's section 4a is explicit about the purpose (its own title: "RARITY ROW FILLERS — 2 RARE, 1 EPIC, 1 LEGENDARY") — 4 cars, not 3 as first described in chat, specifically sized to round every rarity tier up to a multiple of 3 so the price-sorted, rarity-grouped Garage grid (Batch 104) never ends a section on a half-empty row. Before this batch: common 12 (already fine), rare 13, epic 11, legendary 11 — the latter three each one short of a clean row split. Added: Interceptor (rare, unmarked police-style sedan), Hot Rod (rare, chopped roof/open engine), Super SUV (epic, performance wagon), Coachbuilt (legendary, one-off gold hyper-coupe) — ported verbatim from the doc (same `this.vShell/vGlass/shade` → `bodyShell53/bodyGlass53/shade`, `g.`→`gctx.` mechanical translation already used for Batch 102/103's cars, confirmed identical helper signatures again). Prices used the doc's own suggested values (~1,500 / ~1,800 / ~5,800 / ~18,500) as-is — they already sit cleanly inside the existing per-tier price bands with no collisions against any current price.

Rarity is now common 12 / rare 15 / epic 12 / legendary 12 — every tier an exact multiple of 3 (previously only common was). `GARAGE_NPC_RARITY` needed no separate update: since Batch 103 it's derived automatically from each car's own `rarity` field, so tagging the 4 new cars slotted them into road-spawn odds for free.

**Verification**: live-tested in the Browser pane — confirmed `GARAGE_CARS.length` is now 52 with no duplicate keys; confirmed all 4 new sprites render non-blank pixel data with zero errors; confirmed every rarity section (common/rare/epic/legendary) is now divisible by 3, and the rendered grid's own per-section tile counts match (12/15/12/12) with no partial trailing row; ran a 50,000-sample spawn tally confirming all 4 new cars actually spawn as traffic at rates consistent with their tier (rare pair ~100 hits each, epic ~34, legendary ~10); ran a live playthrough with zero console errors.

---

## 2.36.1 — 2026-08-31 12:15: Batch 105 — fixed uneven car-tile heights, off-center + emoji lock icon

Direct follow-up to Batch 104. (1) Real bug: since the Garage grid grouped cars into rarity sections, a row made up entirely of undiscovered "???" cards (very possible for a still-mostly-locked tier) rendered visibly shorter than a row with at least one real card — CSS Grid sizes each row to its own tallest item independently, and a bare "???" mark has nowhere near a real card's full content stack (rarity badge + 60px sprite + name + price row). Fixed with `min-height: 140px` on `.car-tile` (measured live as the tallest a real card naturally reaches) — now applies uniformly to every tile regardless of which row it lands in, real or mystery alike. (2) The lock EMOJI on locked paint colors (Batch 104) wasn't reliably centered — font glyph metrics for 🔒 don't sit dead-center in their own line box, which is exactly what was reported. Replaced with a small canvas-drawn monochrome icon (`renderLockIcon()`, same established pattern as `renderCoinIcon()` elsewhere in this file) — a black lock silhouette with a 1px white outline dilated around it for contrast against any swatch color, centered by construction (a fixed-size canvas element, not a font glyph) instead of by font metrics. (3) Locked colors also got a partial fade back (`opacity: .7`, was full opacity after Batch 104 removed the old .4 entirely) per direct feedback ("make the colors a little more faded when they're locked").

**Verification**: live-tested in the Browser pane — confirmed every single tile in the grid (mystery, real, and Stock alike) now measures exactly 140px via `getBoundingClientRect()`, was previously as low as ~47px for an all-mystery row; confirmed the lock icon's own bounding-box center matches its parent swatch's center to the pixel (0,0 offset) across multiple locked swatches; confirmed the icon's pixel data contains both black and white non-transparent pixels (60/54 out of 144, the rest transparent corners from the silhouette shape) — a real lock shape, not a blank canvas; confirmed locked swatches read `opacity: 0.7` via computed style. Zero console errors throughout.

---

## 2.36.0 — 2026-08-31 11:30: Batch 104 — Garage layout pass: rarity-grouped grid, single-row colors, "NEW!" discovery alerts

Direct feedback, several pieces in one message. (1) Paint colors: was 2 rows (owned / to-buy), now one single row in `GARAGE_COLORS` order; locked swatches no longer fade (opacity .4) — a lock glyph (🔒) is overlaid instead, using the same 4-directional black-outline text-shadow trick used elsewhere in the file (e.g. the crash-skip hint) so it stays readable against any swatch color, light or dark. (2) The "Car Model:" label above the car grid removed — the new rarity group headers (below) make the grid self-explanatory without it. (3) The Garage car grid is now grouped by rarity — a colored section header (COMMON/RARE/EPIC/LEGENDARY, same colors as Batch 103's per-card badge) with that tier's cars underneath, sorted by price only WITHIN each section; Stock stays first, ungrouped. An undiscovered car still slots into its real rarity section as a "???" card (its rarity is known internally even before it's spotted), so section shape stays stable regardless of discovery progress. (4) `.garage-scroll`'s scrollbar restyled to match the game's palette (`::-webkit-scrollbar-*` + Firefox's `scrollbar-color`) instead of the bare OS default.

**New: "NEW!" discovery alerts.** A car spotted on the road (Batch 99's discovery gate) now also gets added to a new `allTimeStats.newlySpottedCars` list. While anything's in that list, the main menu's GARAGE button shows a red "NEW!" corner badge, and opening the Garage shows that specific card with a red frame + red "NEW!" tag (on top of its normal owned/equipped/locked styling — a dedicated CSS rule declared after the state-color rules so it always wins that tie). The highlight is deliberately cleared on EXIT, not on open, so it stays visible for the whole visit and only resets the next time something new is spotted — matches the spec exactly ("if you go to the garage, everything new... once seen. If you exit, all the new frames/alerts are dismissed").

**Also this batch**: the undiscovered-car "???" mystery card simplified from two "???" marks (a 60px sprite-box one plus a smaller one standing in for the name below it) down to one, which now stretches (`flex:1`) to center within however tall the card actually renders — the old fixed-height version sat visibly high once a real card's extra price/badge rows made the shared grid row taller. Added a "leaderboard car icon" idea to PLAN.md's backlog (sprite next to the car name Batch 92 already shows as text) — not implemented, just captured.

**Verification**: live-tested in the Browser pane — confirmed the grid renders in the exact STOCK→COMMON(12)→RARE(13)→EPIC(11)→LEGENDARY(11) shape; confirmed a forced-new car shows both the red frame and the "NEW!" tag while a merely-discovered (not new) car doesn't; confirmed the menu badge is visible before a Garage visit and gone immediately after clicking BACK, with `newlySpottedCars` actually cleared in `allTimeStats`; confirmed the color picker renders as one row with lock icons on every not-owned swatch and zero opacity fade; confirmed the "Car Model" label text is gone from the DOM; ran a live playthrough long enough for 2 new Garage-car NPCs to spawn and confirmed they landed in `newlySpottedCars` correctly; zero console errors throughout.

---

## 2.35.0 — 2026-08-31 10:00: Batch 103 — car rarity tiers, colored badges, price overhaul, price-sorted Garage

Direct request: "look through all the cars and assign each a rarity... common, rare, epic, legendary... pick them depending on the cars — better looking/very fast/very expensive should be epic or legendary, more normal cars rare/common... make sure legendary doesn't have much less cars than any other rarity... assign prices depending on rarity, vary a little... raise the prices... default/common very cheap... legendary should take a little grind, not very much... make sure the cars are always sorted by price, locked or not, staying in place... make sure the rarities follow the spawning rule so legendary spawns much less than epic/rare/common."

**Rarity assignment**: judged per car (looks/speed/theme, not the old prices) across all 47 non-Stock cars, landing at common 12 / rare 13 / epic 11 / legendary 11 — deliberately close to even so legendary isn't a tiny sliver next to the others. Everyday/utility-shaped cars (Hot Hatch, Wagon, SUV, School Bus, Tractor, etc.) skew common/rare; visibly exotic, fast, or novelty cars (Hypercar, Tank, Steamroller, F1, Land Speeder, etc.) skew epic/legendary. Stock (the free starter) has no rarity — it's not part of the collectible tiering.

**Pricing**: fully rebanded by tier with variation within each tier (not a flat per-tier price): common 60-320, rare 650-2,100, epic 2,800-7,400, legendary 8,500-20,000 (Steamroller, the highest). Calibrated against the user's own estimate of "a couple thousand coins from a good run" — common cars cost a fraction of one run, rare about one run, epic 1-3 runs, legendary 3-8 runs (with coins being only one of several ways to earn a car, per earlier plans — full-level rewards and daily boxes are still deferred/unbuilt).

**Spawning tied to rarity by construction, not just convention**: replaced the separately-maintained `GARAGE_NPC_RARITY` table with one built by iterating `GARAGE_CARS` and looking up each car's own `rarity` in a 4-entry `RARITY_SPAWN_WEIGHT` map (reusing Batch 101's already playtest-tuned weight values 18/0.7/0.25/0.06) — purchase-rarity and road-spawn-rarity are now literally the same field, so they can't drift out of sync again.

**Garage UI**: added a small colored rarity badge (COMMON grey / RARE blue / EPIC purple / LEGENDARY gold) above each discovered car's sprite — kept off the tile's own border/background since Batch 90 already uses those for owned/equipped/locked state, so this is a separate, non-clashing visual channel. The grid now always renders sorted by price ascending (on a sorted copy, not the underlying array — nothing else that reads `GARAGE_CARS` by position, like the default-car fallback, is affected) regardless of ownership, so a card's position never jumps around as you buy things.

**Verification**: live-tested in the Browser pane — confirmed all 48 cars, no duplicate keys, exact 12/13/11/11 rarity split, non-overlapping price bands per tier; confirmed the rendered grid is sorted strictly ascending by price (0 → 20,000) with correct rarity-colored badges, and that buying/equipping a car (Muscle) leaves it in its exact same sorted slot, only its status class changes; ran a 20,000-sample statistical spawn tally confirming a clean monotonic drop common → rare → epic → legendary (≈67% / 2.8% / 0.75% / 0.24% of all traffic); ran a live playthrough long enough for an actual Garage-car NPC to spawn and draw with zero console errors throughout.

---

## 2.34.0 — 2026-08-28 10:00: Batch 102 — 22 new vehicles from Reckless Vehiclesv3.dc.html

User's own upload, direct instruction: "add them to the garage... make their hitboxes... make sure they also appear in gameplay." Ported all of the doc's genuinely NEW content — 13 "FRESH" everyday-traffic bodies (Wagon, Minivan, SUV, Convertible, Stripe Racer, Roadster, Lowrider, Hearse, Camper, Food Truck, School Bus, Fire Engine, Garbage Truck) and 9 "RACE" class vehicles (F1, Indy Oval, F3 Junior, Le Mans Hyper, GT3, Time Attack, Stock Car, EV Hyper, Superbike) — 22 total. The doc's own "heavy/speed/oddity" sections were just a re-listing of Batch 89's already-ported 16 vehicles for reference, not new content, so nothing there needed touching.

**Design decision**: unlike Batch 89's 16 (a wider 24px-native canvas + `hitboxW`, explicitly framed by the doc as a "hitbox vs multiplier" trade-off class with its own mult/box/spd stats), all 22 of these are native 14px-wide — the SAME convention the original 10 Garage cars and every `VEHICLE_BODIES` traffic body already use. The doc gives no mult/box/spd stats for this set (only label/height/color/note), which itself signals they're meant as "more of the everyday/original-10 kind," not the exotic trade-off kind — so no `hitboxW`/offset handling was needed anywhere, and "make their hitboxes" resolves to simply reading each car's real native `h`, same as the original 10.

**Integration reused Batch 99/101's system wholesale rather than building a second parallel one**: added all 22 directly to `GARAGE_CARS` (with an invented first-pass price ladder — 800-2400 for the everyday "fresh" set, 3200-5500 for the sportier "race" set) AND to `GARAGE_NPC_RARITY` (fresh → UNCOMMON, race → RARE) — meaning they spawn as NPC traffic through the exact same `garageCar`-tagged pipeline every other Garage car already uses (`Vehicle.draw()`, crash-sequence wrecks, the discovery gate), rather than extending `VEHICLE_BODIES`' own separate spawn pool. This was a deliberate choice: routing them through `VEHICLE_BODIES` instead would have made them permanently un-discoverable (the discovery-tracking code only watches for `v.garageCar`), and would have meant duplicate, parallel logic for what's functionally the same feature.

**Verification**: live-tested in the Browser pane — rendered all 22 new car-tile sprites directly (`drawCarTileSprite`), confirmed zero errors and zero blank canvases; confirmed `GARAGE_CARS.length` is now 48 (26 + 22) with no duplicate keys; confirmed the Garage grid shows 47 "???" mystery cards (everything except Stock) on a fresh save; force-spawned and scrolled an F1 into view, confirmed `isCarDiscovered()` flips true; forced a crash into an SUV NPC, confirmed the wreck renders at its correct real size (18×34) with zero errors; ran a 20,000-sample statistical tally confirming the new cars slot into the (also just-rebalanced) rarity ordering correctly (fresh-tier ≈80-90 hits, race-tier ≈20-26, alongside the existing common/very-rare tiers); ran full natural playthroughs to a real crash and to the result screen with zero console errors throughout.

---

## 2.33.0 — 2026-08-28 09:45: Batch 101 — Garage-car traffic rarity cut ~7x, per a real playtest

Direct feedback after an actual run: "I got like 4000 score... it was like super long... and I met like half the cars... that's way too often... make it five times less common, or maybe even ten." Cut all 3 non-COMMON tiers (`GARAGE_NPC_UNCOMMON`, `GARAGE_NPC_RARE`, `GARAGE_NPC_VERY_RARE`) and Road Train's own weight to roughly 1/10th their Batch 99 values, kept `GARAGE_NPC_COMMON` unchanged. Verified the FINAL effective reduction (not just the raw divisor, since shrinking the rare pool also makes the unchanged COMMON tier's own share of the whole pool grow) lands at ~6.8x — landing in the middle of the requested 5-10x range, not at either edge. As an explicit side effect of leaving COMMON alone while everything else shrank, Hot Hatch/Rally/Drift's own real spawn rate actually INCREASED (from ~4.8% of all spawns to ~7%) — exactly matching the other half of the request ("basic ones... you can make them much more common").

**Verification**: live-tested in the Browser pane — ran a fresh 20,000-sample statistical tally (same methodology as Batch 99's original verification) confirming the new numbers: Hot Hatch/Rally/Drift still land far ahead of everything else, and every other tier dropped roughly an order of magnitude versus the Batch 99 baseline.

---

## 2.32.1 — 2026-08-27 09:15: Batch 100 — result screen still animates when the crash sequence is skipped

Direct feedback: "when skipping with esc crash cutscene it should still animate score and stuff." `finishCrashSequence()` was calling `showResultScreen(CS.skipped)` — `true` specifically because it was skipped, taking the INSTANT branch (numbers just appear, no `countUp()`, no entrance slide-in) — backwards from what's wanted. Now always calls `showResultScreen(false)`, so the numbers animate in exactly the same way whether the sequence played out fully, was skipped with Escape, or was auto-skipped via Batch 98's "Skip Crash Animation" setting (all 3 paths go through the same `finishCrashSequence()`). The now-write-only `CS.skipped` flag (this was its only reader) was removed entirely, along with its 2 setter sites.

**Verification**: live-tested in the Browser pane — forced a crash, called `skipCrashSequence()` (simulating Escape), confirmed `goScore.textContent` reads "0" immediately after the skip (animating) rather than the final value, confirmed the `go-anim` entrance-animation class is present, waited out the real `countUp()` timers and confirmed the numbers land on the correct final values (2000/1500 in the test). Confirmed the un-skipped natural path still works. Zero console errors.

---

## 2.32.0 — 2026-08-27 09:00: Batch 99 — Garage cars now appear as NPC traffic, rarity-weighted + discovery-gated

Implements both halves of PLAN.md's "GARAGE CARS AS NPC TRAFFIC" entry together, since the second genuinely depends on the first (a car can't be "spotted" on the road if it never spawns there).

### All 26 Garage cars can now spawn as ordinary ("normal"-type) NPC traffic
Per direct feedback ("why don't the game use all of these cars?"). `Vehicle`'s constructor picks from a combined weighted pool — the existing 5-body sedan/hatch/coupe/pickup/van set, PLUS all 25 non-stock Garage cars via a new `GARAGE_NPC_RARITY` table. A garageCar-driven vehicle stores the actual `GARAGE_CARS` entry (`this.garageCar`) alongside the usual `body`/`type`, and `Vehicle.draw()`/the crash sequence's wreck-drawing both gained a branch for it — same `car.draw()` + `carDrawOffsetX53()` offset pattern the player's own sprite and Batch 97's wrecks already use, so a Garage-car NPC (and its wreck, if you hit one) renders at that car's own real size/shape, not a generic body. Stock is excluded — it's the free default, visually redundant with the existing 'sedan' body, and doesn't need a discovery gate.

**Rarity table is a first-pass, not fully user-specified**: only a handful of cars were named directly — Hot Hatch/Rally/Drift common, Monster Truck/Formula rare, Road Train "a little more common" than the rarest tier, Dragster/Land Speeder very rare. Every other car's tier is a reasonable judgment call (utility-shaped cars leaning common, oddity-class leaning rare). Verified via a 20,000-sample tally: hatch/rally/drift ≈1550-1650 each, road train 330, formula/monster ≈200-226, dragster/speeder/tank ≈40-45 — matches the intended common≫road-train>rare≫very-rare ordering exactly. One side effect worth flagging: the 25-car Garage pool's combined weight (≈135) now outweighs the original 5-body pool (95), so roughly 58% of "normal" traffic is now a Garage car rather than a classic sedan/hatch/etc. — not something the user asked to preserve a ratio for, but tunable if Garage cars end up feeling too dominant once actually seen.

### Discovery gate: a car can't be bought until it's been spotted on the road
Per direct spec: "before you spot it, it displays like a blank page with ???... find this car on the road to unlock it... you just need to spot it, you don't need to crash into it." New `allTimeStats.discoveredCars` (persistent array) + `isCarDiscovered(car)` (stock and anything already-owned always count as discovered, so existing saves don't regress). The main loop marks a Garage-car NPC discovered the first frame it's actually on-screen (`v.y + v.height >= 0 && v.y <= canvas.height`), not merely spawned off-canvas. `renderCarGrid()` shows a blank "???" card (reuses the existing fixed-height `.car-tile-sprite` box so row alignment holds, per Batch 96) with a hover title ("Find this car on the road to unlock it") and no click handler at all for any undiscovered car — this sits on top of, not instead of, the existing coin-cost gate (Batch 66/69).

**Verification**: live-tested in the Browser pane — confirmed 25/26 cards render as "???" on a fresh save, Stock does not; confirmed force-spawning and scrolling a Road Train NPC into view flips `isCarDiscovered()` false→true and the Garage grid reveals its real card on next render (mystery count 25→24); confirmed a forced crash into a Jet Bike NPC produces a wreck at that car's own real (10×26) dimensions with zero errors; confirmed real (unforced) gameplay naturally spawns Garage cars within a 5000-frame sample; ran a 20,000-sample statistical tally confirming the rarity ordering; ran full natural playthroughs to real crashes and to the result screen with zero console errors throughout.

---

## 2.31.0 — 2026-08-27 08:15: Batch 98 — crash sequence polish round 2, end-screen readability, skip-crash setting

Direct follow-up feedback on Batch 97, plus new end-screen/settings asks. Split from the large batch of ideas in the same message that are genuinely bigger, separate features — see PLAN.md's new "GARAGE CARS AS NPC TRAFFIC," "GARAGE COLORS UNLOCKED VIA DAILY LETTER COLLECTION," and expanded "BATCH 89 FOLLOW-UP"/"BATCH 40" entries for those.

### Screen shake now scales with speed
Per direct feedback ("faster you're going, the harder the screen shake should be") — `CS.shake` was a flat `7`; now ranges 7 (at/below `baseSpeed`) to 14 (at `maxSpeed`), using the same speedRatio pattern the live multiplier bonus already computes.

### Blur removed; the tire-prop system removed entirely
User's own back-and-forth landed on: real vehicle + rotation + smoke is enough on its own — "screw the props, just without them." Separately, a real bug report ("under your car appears... a strange shadow on the sides") pointed at the SAME root cause: `ctx.filter = 'blur(...)'` on an already-small, rotated pixel-art sprite smears its edges into a soft halo against the dark background, reading exactly like an unnatural shadow. Both `blur` and the `CRASH_PROPS`/`drawCrashPropTire53`/`CS.props` system are gone — wrecks are back to real-vehicle + rotation + smoke + a scorch pool, nothing else. Don't re-add either without being asked again.

### Real bug fixed: responders could still end up driving through the wreck's own lane
Per direct feedback ("I still see police cars driving out of the corpse"). Root cause distinct from Batch 96's fix (which only guaranteed a responder's FINAL resting position stays clear): the lane-selection search list ended with a `0` offset — the wreck's OWN lane — reachable on any road without ~7 free lanes on either side (e.g. any 3-4 lane road with the wreck near the middle). A responder assigned to the wreck's own lane travels straight up that lane during its approach, visually reading as driving through/out of the wreck even though its final Y still stopped short. The wreck's own lane is no longer a candidate at all — verified on a 3-lane road (the exact previously-broken case): no responder shares the wreck's X anymore.

### End screen: clearer labels and time format
"BASE" → "BASE SCORE" (matching the SCORE/PERFORMANCE SCORE naming already used elsewhere on this screen). SURVIVED now uses a new `formatTimeCompact()` — "5s" or "1m 5s" instead of "0:05"/"1:05" — per direct feedback ("no need for unnecessary zeros"). Scoped to the result screen only; the shared `formatTime()` (pause timer, leaderboard, Stats) is untouched since none of those were part of the complaint.

### New Setup setting: Skip Crash Animation
"Buttons you can turn on and off... skip the crashed part, so you can just skip them automatically without using the keybinds." New On/Off select (default Off) — when On, a crash jumps straight to the result screen exactly like pressing Escape (`skipCrashSequence()`), just triggered automatically the moment the sequence would otherwise start.

**Verification**: live-tested in the Browser pane — confirmed shake scales 7→14 across the speed range; confirmed the lane-reuse fix on a forced 3-lane/middle-lane scenario (previously reproducible, now clean); confirmed the Skip Crash Animation setting produces an instant result screen with `CS.skipped=true`; confirmed `formatTimeCompact()` against 0/5s/65s inputs; confirmed the BASE SCORE label renders; confirmed `CS.props` no longer exists on the state object; ran a natural 1081-frame playthrough to a real crash with zero console errors throughout.

---

## 2.30.0 — 2026-08-26 07:45: Batch 97 — crash wrecks now draw the real vehicles involved

Direct feedback on the crash sequence's biggest remaining gap: "if you crash into the semi-truck, it looks weird that it's now suddenly a car." The wreck system used one generic 4-variant "wreck" sprite for literally every crash, always drawn at a fixed car-sized box (`PLAYER_WIDTH`/`PLAYER_HEIGHT`) regardless of what was actually hit — a semi collapsed into something car-shaped every time.

**Fix, per direct spec ("take the car you crashed into, rotate it, blur it, add smoke... same should apply to the user's car")**: wrecks now draw the ACTUAL vehicle involved, reusing the exact draw functions and dimensions gameplay already uses — no new vehicle art needed. The player's wreck uses the same `Player.draw()` branching (stock → `drawPixelCar`, any Garage car → `car.draw()` + `carDrawOffsetX53()` for hitboxW cars); the other vehicle's wreck uses the same `Vehicle.draw()` branching (ambulance → `drawPixelAmbulance`, everything else → `VEHICLE_BODIES[body].draw`). Each wreck keeps its existing random resting `angle`, and now also gets a random `blur` (`ctx.filter = 'blur(...)'`) for a hazy, damaged look. A scorch pool is drawn under each wreck sized to its own real footprint (was a fixed size). `endRun()`'s 2 collision call sites now pass the live `Vehicle` instance through instead of a stripped `{x,y}` object, so the wreck has everything it needs (`body`/`type`/`width`/`height`) to draw itself correctly.

**New optional damage props**: each wreck has a 45% chance of spawning one small prop nearby (currently just a popped tire, `drawCrashPropTire53` — a short list, easy to extend later) — "you could also add a popped tire laying on the side... a few props that could randomly spawn or not."

The old `drawWreck53()` (4 hand-drawn generic wreck variants, ~60 lines) is removed entirely — fully superseded, nothing else referenced it.

**Verification**: live-tested in the Browser pane — confirmed a semi-truck crash produces a wreck at the semi's own real height (73px) instead of the old fixed 31px; confirmed a Garage car (Road Train) player wreck uses that car's own real dimensions (78px) with the hitboxW draw-offset correctly applied; confirmed all 14 `VEHICLE_BODIES` types (sedan through tractor) render their wreck with zero errors, each at its own distinct correct height; confirmed the ambulance-specific draw branch works; confirmed a full sequence (blur filter + real vehicle sprite + scorch pool + random prop) renders a fully opaque canvas with zero console errors and reaches the result screen normally. Visual quality (does the blur/rotation actually read as "wrecked," does the tire prop look right at this scale) hasn't been seen — same screenshot-compositing limitation as the rest of this session.

---

## 2.29.1 — 2026-08-26 07:20: Batch 96 follow-up — close call could still fire right before a real crash

Direct clarification on the item Batch 96 left unresolved: "it still gives you points from close call if you just run into somebody sideways." Confirmed the real mechanism — a car changing lanes into the player moves gradually, so its hitbox-gap always passes THROUGH the close-call threshold on its way to an actual overlap. The old instant "gap ≤ threshold → award" check had no way to distinguish "about to safely clear" from "about to crash" — it always fired first, then the crash still happened a moment later.

**Fix**: deferred crediting. `Vehicle` gained `wasEverClose` — the first frame the gap drops to `CLOSE_CALL_GAP`, it's just marked, nothing awarded. The bonus only fires once the gap grows back OUT past the threshold again, i.e. once the near-miss is confirmed over. This is provably safe from the reported failure mode: an actual collision requires `gap === 0`, which can never satisfy `gap > CLOSE_CALL_GAP`, so a vehicle that goes on to crash into the player can never reach the award branch.

**Verification**: live-tested in the Browser pane — simulated a car gradually swerving from a 9px gap down to an actual collision (10 manual steps): `closeCallCredited` stayed `false` at every single step, confirmed zero close-call points were ever awarded before the crash. Simulated the legitimate case (gap shrinks to 2px, then grows back to 6px): credited exactly once, at the first frame the gap cleared the threshold again, `closeCallsThisRun` incremented exactly once (no double-fire). Re-confirmed the backward-movement exclusion still holds under the new two-phase logic. A natural 620-frame playthrough with real random traffic completed with zero console errors.

---

## 2.29.0 — 2026-08-26 07:00: Batch 96 — crash sequence, Garage alignment, close-call anti-farming

Five pieces of direct feedback.

### Crash sequence: responder no longer parks on top of the wreck
Real bug, not a tuning issue. Responder target positions were shifted up as a group when they'd otherwise run off-canvas, clamped by `maxTargetY` — a comment there claimed "≥114px of clearance below the wreck, even in the worst case," which was true when that clamp was derived from the single fixed `PLAYER_HEIGHT`. Batch 90 gave every car its own real `maxY`, and a short car (Stock, `maxY≈228`) can legitimately crash almost exactly at that old clamp value, leaving ~0px of room — the shift could then push a responder's target AT or ABOVE the wreck's own Y, the opposite of "arrive from below." Added a hard floor (`minTargetY = wreckY + RESP_CLEAR`) so a responder is never placed closer to (or above) the wreck than that, even if honoring it means slightly exceeding the canvas's bottom edge in the most extreme case — a responder's sprite very briefly cut off at the bottom reads far better than one visibly parked on the wreck it's responding to.

### Crash sequence: ends straight into the result screen
The old `resume` phase (~2s: road speeds back up, wrecks/responders scroll away with it) is gone entirely, per direct feedback ("instead of road going further... just show the results screen instantly, looks better"). `beat` now goes straight to `finishCrashSequence()` — exactly what ESC-skip already did all along (`skipCrashSequence()` has always bypassed `resume`); this just makes the sequence's natural end behave the same way. Removed the now-dead `resume`-phase branches in `csEnterPhase()`/`csUpdate()`/the main loop's speed-ramp, and the now-unused `CS.savedSpeed`.

### Garage grid: name/price now align across every card
Per direct feedback ("sometimes the sprite is smaller or bigger and the price/name is moved up"). Since Batch 92/93 each car's sprite renders at its own real aspect ratio, canvas height genuinely varies a lot car to car — everything below it inherited that variance. Wrapped the canvas in a new fixed-height `.car-tile-sprite` box (`object-fit: contain` — still undistorted, still overflow-proof) so every card's sprite AREA is the same height regardless of the individual car's proportions, and the name/price row underneath lines up across the whole grid.

### Close call: harder to trigger intentionally
Per direct feedback ("very hard to trigger intentionally, I don't want it to be used as a farming method"). `CLOSE_CALL_GAP` cut 20% (3 → 2.4px). Also excluded while the player is moving backward (`vVelocity > 0`) — reversing is this game's slowest, most controllable motion, so easing right up to a car behind you in reverse was a much cheaper way to farm the gap than actually threading a tight pass at real speed.

**Steamroller's black frame** — investigated per a direct question. Its draw function fills a solid black base first, then draws the actual body 3-4px inset (vs. the ~1-2px every other car uses) — a deliberate, much thicker margin representing its heavy roller-drum front assembly, not a sizing bug. Flagged back to the user rather than changed, since it reads as intentional industrial styling in the code but might still look oversized at this pixel scale — no code change made pending their call.

**Verification**: live-tested in the Browser pane — confirmed `CS_PHASE_ORDER` no longer contains `'resume'`; confirmed a crash forced at a short car's exact `maxY` (the worst case) collapses all 3 responders to a single shared safe Y rather than any landing above the wreck, and a moderate-room crash still preserves the responder stagger; confirmed a full natural playthrough reaches the result screen correctly with no hang; confirmed every one of 26 Garage cards' name label sits at an identical Y within its row (9/9 rows checked) with zero sprite overflow past its wrap; confirmed the new 2.4px threshold and the backward-movement exclusion both gate correctly. Zero console errors throughout.

---

## 2.28.0 — 2026-08-26 06:30: Batch 95 — close-call polish: floating text, live score count-up, result-screen breakdown

Direct follow-up feedback on Batch 94's close-call bonus, three pieces.

### Floating "CLOSE CALL!" text
New `ScorePopup` class (a text-drawing sibling to the existing dot-based `Particle` class, not bolted onto it — drawing text needs a genuinely different `draw()`) — drifts upward and fades over ~0.75s, showing "CLOSE CALL!" plus the actual awarded points (e.g. "+150") right where the near-miss happened. Kept simpler than the "flies to the score" alternative floated in the request — that would need world-to-DOM coordinate translation and a second tween system; ask if that specific polish is still wanted.

### Live HUD score no longer snaps instantly
Was `hudScore.textContent = score` every frame — a flat instant set. Now eases toward the real value (`displayedScore += Math.ceil((score - displayedScore) * 0.3)` each frame) so a score jump visibly counts up rather than popping, while still resolving in well under a second ("can be a fast animation") — `Math.ceil` guarantees it always actually reaches the target (never asymptotically stalls) since `score` only ever increases in this game.

### Result screen: SCORE label + CLOSE CALLS breakdown row
The big score number at the top had no caption at all — added a small `.go-score-label` "SCORE" directly beneath it. New 7th stat row: label shows the count baked in ("5× CLOSE CALLS"), value shows the total points those close calls earned this run, animated via the same `countUp()` every other result-screen number already uses. `CS.snapshot` gained `closeCalls`/`closeCallPts` fields threaded through from new `closeCallsThisRun`/`closeCallPointsThisRun` run-scoped counters (reset in `launchGame()`, incremented right alongside the existing close-call scoring). The entrance-animation `nth-of-type` delay list (Batch 88's own comment already flagged "needs to grow again if another stat row is ever added") grew 6→7. Per direct confirmation, BASE/MULTIPLIER/SURVIVED/RANK/PERFORMANCE SCORE/COINS EARNED were all left exactly as they are — SURVIVED (M:SS) already existed, no change needed there.

**Verification**: live-tested in the Browser pane — confirmed a close call spawns a popup with the correct text/points and it despawns after its lifespan with zero leftover state; confirmed `displayedScore` eases toward `score` frame-by-frame and fully converges; confirmed the result screen's SCORE label renders and sits directly under the number with no layout overflow (7 stat rows measured, zero overflow past the panel edge); confirmed the CLOSE CALLS row's label correctly reflects the run's real close-call count and its value correctly animates to the real accumulated points (had to actually wait real wall-clock time for this specific check, since `countUp()` uses `setTimeout`/`setInterval` — a different timing system from the frame-stepped `loop()` calls used for the rest of this batch's testing); zero console errors throughout.

---

## 2.27.0 — 2026-08-26 06:00: Batch 94 — "close call" bonus score

New scoring source, per direct spec: squeeze past a vehicle with almost no room to spare, without hitting it, and get a bonus — 100 base points × the live multiplier, same pattern every other score source already uses.

**Detection**: a new `rectGap(r1, r2)` helper computes the real Euclidean distance between two rectangles' nearest edges (0 if overlapping/touching, positive otherwise) — `checkCollision()` only ever answers "did they touch," not "how close was it," which is what a near-miss check actually needs. Each frame, for every vehicle that didn't just collide with the player, if the gap is ≤ `CLOSE_CALL_GAP` (3px, first-pass — at the default 4-lane road two cars centered in adjacent lanes with zero drift sit ~13px apart, so 3px only fires on a genuinely tight squeeze, not an ordinary adjacent-lane pass) it credits once (`v.closeCallCredited`, same one-shot-flag pattern as `jumpedOver`/`passScored`) and awards score + XP (no coins — matches the ram bonus's category, not the coin-earning dodge/jump path).

**The jump case, handled with zero extra logic**: deliberately gated on `player.abilityState !== 'jumping'` — soaring safely over a car mid-air isn't a close call (that's the existing `jumpedOver` bonus's job), but the spec's "mistimed jump — jump late or land late and almost clip something" case needed no special-casing at all: a late/early jump just means the player is grounded (not in `'jumping'` state) at the moment they're tight against a car, which falls straight through to the exact same check already used for ground-level near-misses.

**Verification**: live-tested in the Browser pane by manually constructing exact scenarios and stepping `loop()` directly (this project's established pattern for a background tab where `requestAnimationFrame` doesn't reliably fire on its own) rather than waiting on real elapsed time — confirmed `rectGap()`'s math against known-distance rectangle pairs (overlapping, touching, 3px, a 3-4-5 diagonal); confirmed a 2px gap credits exactly once and doesn't re-fire across further frames while still close; confirmed an actual collision (gap 0, overlapping) does NOT also count as a close call; confirmed a tight gap while `abilityState==='jumping'` does NOT fire (only the normal dodge credit does); confirmed the exact boundary (gap===3 fires, gap===4 doesn't); ran a natural 544-frame playthrough with real random traffic (no forced setup) through to a real crash with zero console errors.

---

## 2.26.0 — 2026-08-26 05:30: Batch 93 — small car sprites now fill their box (Garage grid + showroom)

Direct feedback: "sprites that are small make them as big as they can be in that box (all sprites should work that way)" — narrow/short cars (Jet Bike, Go-Kart, etc.) still looked tiny inside Batch 92's new uniform tiles.

**Root cause**: both the car-tile grid (`drawCarTileSprite()`) and the showroom preview (`drawGaragePreview()`) sized their canvas buffer to a SHARED size (grid: a 60-long footprint, 18-or-31-wide per old/new group; preview: 18-or-31-wide per group) rather than each car's own real dimensions. A short car (`car.h` well under 60) or a narrow one (`hitboxW` well under the shared 24-wide canvas every new car's draw function centers itself within) ended up with a lot of fully-transparent blank canvas around its actual sprite — and since display sizing (`width:100%; height:auto` for the grid, explicit fit-to-stage scaling for the preview) scales the WHOLE buffer including that blank space, a small car's real pixels occupied a much smaller fraction of the same-size box than a big car's did.

**Fix**: both now size their buffer tight to each car's own real dimensions — length = `car.h` exactly (was a shared 60/group-max), width = the car's own real `hitboxW` (was a shared 24-or-14-per-group constant). A `hitboxW` car's draw function still internally assumes the old shared 24-wide canvas (via `carLocalX53()`), so drawing directly into a narrower buffer needs the same offset already proven correct for the live gameplay sprite: the grid's raw (unscaled) pipeline applies `-carLocalX53(car.hitboxW)` directly, the preview (which does go through `drawScaledVehicle`) reuses the existing `carDrawOffsetX53(car)` helper as its draw-origin x, exactly matching how `Player.draw()` already handles this. The old `CAR_TILE_FOOTPRINT` constant is gone (nothing else referenced it).

**Verification**: live-tested in the Browser pane — for all 26 cars, scanned each tile's raw canvas pixel data for the actual drawn (non-transparent) bounding box vs. the full buffer: every car now fills 93–100% of its own buffer on both axes (was as low as ~33% for cars like Jet Bike/Go-Kart before this fix), zero cars render blank. Confirmed zero CSS overflow past any tile's edge and zero showroom-stage overflow across a spread of cars (Jet Bike, Road Train, Monster Truck, Stock). Confirmed a full gameplay launch with a `hitboxW` car equipped still produces correct `Player.width`/`height`/`maxY` (this batch only touched Garage-UI-specific draw functions, not `Player.draw()` itself) and zero console errors throughout.

---

## 2.25.0 — 2026-08-26 05:00: Batch 92 — Garage grid uniform 3-per-row, sticky BACK button, car shown on Scores

Three pieces of direct feedback.

### Garage grid: every car box now uniformly "2 wide," always exactly 3 per row
Previously only cars with `h>=30` spanned 2 columns (Batch 90), everything else stayed at whatever `auto-fill` produced — an inconsistent mix. Per direct feedback ("make it so that every car box is 2 wide, 3 can fit per row"), `.car-grid` is now a fixed `grid-template-columns: repeat(3, 1fr)` and the whole `car.h>=30`/`.car-tile-wide` special-casing is gone — every tile is the same size, always 3 per row, on any viewport.

Also switched sprite sizing from a fixed `height:38px` + `max-width:100%` clamp to `width:100%; height:auto`: the old approach derived display size from a canvas buffer that didn't vary per car, so every car in a size class rendered at the exact same pixel size, and clamping width while height stayed fixed risked visibly distorting whichever car's aspect ratio didn't fit the assumption (old 10 cars are ~3.3:1 native, the 16 Batch-89 cars are ~1.9:1). `width:100%`/`height:auto` always fills the new bigger column and derives height from each canvas's own real proportions — undistorted, and impossible to overflow since width can never exceed its container. Per direct feedback ("all sprites should fit that way").

### Garage BACK button always visible, only the car list scrolls
"The back button should be always visible... you should scroll the cars but back button shouldn't be scrollable." The whole `.settings-panel` (shared by Setup/Stats/Leaderboard too — left untouched there, only Garage asked for this) used to scroll as one block. Garage's panel (`.garage-panel`) is now a flex column: header and showroom keep their natural size, a new `.garage-scroll` wrapper around just the Car Model section is the only flexible/scrollable piece (`flex:1 1 auto; min-height:0; overflow-y:auto`), and BACK sits after it, outside the scroll area, always in view.

### Scores now show which car was driven
`saveScore()`'s entry object gained a `car: selectedCarKey` field; the leaderboard's per-entry meta line (`4L · 1.5x`) now appends the car's label (`4L · 1.5x · ROAD TRAIN`) via a `GARAGE_CARS` lookup. Older saved scores (no `car` field) just show the meta line without a car — no "undefined" text.

**Verification**: live-tested in the Browser pane at both desktop (1280px) and mobile (375px) viewport widths — confirmed exactly 3 tiles per row for all 26 cars (8 rows of 3 + 1 of 2) at both widths, confirmed every tile's canvas fills its full column width with zero overflow past the tile edge (checked Road Train, Jet Bike, Hot Hatch, Stock — one from each old/new size class), confirmed scrolling `.garage-scroll` to its bottom (`scrollTop=99999`) leaves the BACK button's screen position completely unchanged while the outer panel itself has `overflow:hidden` and doesn't scroll at all, confirmed a saved run's leaderboard entry shows the correct car label, confirmed an old-format entry with no `car` field renders cleanly with no "undefined" text, zero console errors throughout.

---

## 2.24.1 — 2026-08-26 04:20: Batch 90 follow-up — wide Garage tiles now actually render a bigger sprite

An independent verification agent, asked to double-check Batch 90's 4 fixes, confirmed all 4 hold up but caught a real gap in fix #1 (long car sprites compressed in the grid): `drawCarTileSprite()`'s canvas buffer is a fixed `CAR_TILE_FOOTPRINT×~31` size for every `hitboxW` car regardless of that car's own `h` — so at the shared `height:38px` CSS display rule, every new car rendered at the exact same pixel size. `.car-tile-wide`'s 2-column grid span gave a long car more surrounding whitespace, not a bigger sprite — not what "let the car take two spots... to fit the sprite" actually asked for. Fixed with `.car-tile-wide > canvas { height: 76px; }` (2x the normal 38px) — verified live: Road Train's tile canvas now displays at 147×76 (was 73.5×38, identical to every other new car), fits within its 226px-wide 2-span tile with no overflow, no console errors.

---

## 2.24.0 — 2026-08-26 04:00: Batch 91 — main menu redesign (level badge promoted to hero element)

User uploaded `carCrash_mainmenu_new.html` — a hand-edited redesign of the main menu, built on top of an old post-Batch-89 snapshot of this file (still had `PLAYER_MAX_Y`/`.car-tile.buyable`, predating Batch 90's Garage fixes — confirmed via grep before touching anything, so only the genuinely new main-menu-specific parts were pulled in, not a wholesale file swap that would have reverted Batch 90's work). Applied the 3 real design changes found in `#menuView`:

1. **Level badge promoted to the menu's hero element.** Was a small 48px ring pinned to the top-right corner (`position:absolute; top:10px; right:10px`, added Batch 79 when the widget was relocated out of gameplay). Now a 96px ring in a centered column, sitting in normal document flow directly below the title — "the second thing you read after the title," per the redesign's own comment. Pure CSS (`flex-direction:column; gap:6px; margin-top:20px; align-self:center` on `#menuLevelBadge`, ×2 size on the ring/canvas/number) — `paintLevelBadge()` draws the ring at a fixed native 24×24 regardless of CSS display size (same pattern as the coin icons), so no JS changes were needed for the resize itself.
2. **Menu title now comes first**, above the level badge (was: badge first, title second — didn't actually matter visually before since the badge was absolutely-positioned out of flow, but now that it's a normal-flow hero element the DOM order determines stacking).
3. **The "CURRENT SETUP" summary panel (lanes/ability/trucks/multiplier) removed entirely** — the redesign's `#menuView` has no `.setup-summary` block at all. Removed the CSS (`​.setup-summary`/`.summary-title`/`.summary-row`/`.summary-mult`) and HTML, then cleaned up the JS this orphaned: `summaryMult.textContent`/`summaryLanes.textContent` writes (in `calculateMultiplier()`/`refreshMenuSummary()`) and their now-dead `const summaryLanes/summaryMult = document.getElementById(...)` declarations — `refreshMenuSummary()` itself stays (it still repaints the level badge on every return-to-menu), just without the line that no longer has anything to write to.

**Deliberately NOT applied**: the mockup's "SETUP" → "SETTINGS" button/screen-title rename — applying it only to the menu button would have created a real mismatch (button says "SETTINGS," the screen it opens still says "Setup"), and renaming the actual Setup screen wasn't part of what was asked ("the main menu look"). Also not applied: anything from the rest of the mockup's stale pre-Batch-90 state (older Garage CSS/JS) — confirmed via grep that Batch 90's fixes are all still intact in the live file after this change.

**Verification**: live-tested in the Browser pane — confirmed DOM order (title → level-badge → actions → footer), confirmed computed styles match the redesign exactly (`flex-direction:column`, `align-self:center`, 96×96 ring), confirmed the old summary elements are completely gone from the DOM (`document.getElementById`/`querySelector` all return null/false), confirmed `refreshMenuSummary()`/`calculateMultiplier()` both still run with zero errors, confirmed bounding-box layout for all 4 menu sections stacks top-to-bottom with no overlap and no overflow past the canvas container (title 32–91px, level badge 111–227px centered horizontally, actions 249–379px, footer pinned to the bottom at 636–661px, all within a 677px-tall container). Screenshot compositing is still broken in this session's Browser pane (same known limitation as every prior batch) — layout confirmed via real `getBoundingClientRect()` data, not an actual visual look.

---

## 2.23.1 — 2026-08-26 03:15: Batch 90 — 4 real bugs fixed on the Batch 89 Garage vehicles

Direct feedback from a screenshot of the new Garage grid caught 4 real bugs in Batch 89's integration, all fixed:

### 1. Long car sprites were compressed in the Garage grid
`.car-tile > canvas { width: auto; max-width: 100% }` clamped a long car's natural display width to a single ~92px-wide grid tile. Fixed exactly as directed: cars with `h >= 30` now get a new `.car-tile-wide { grid-column: span 2; }` class in `renderCarGrid()`, so they claim two grid columns instead of being squeezed into one.

### 2. Garage preview canvas clipped tall cars ("doesn't fit the sprite" / "background is wrong again")
`#garagePreviewCanvas` CSS hardcoded a fixed `width: 72px` display size, but the canvas's native resolution now varies per car (18px old / 31px new, from Batch 89). The same fixed display width meant a different effective scale per car — tall new cars (e.g. Road Train, native height 78) overflowed the showroom stage's fixed 130px height and got clipped, which also explains the "wrong background" symptom (the oversized/clipped foreground canvas visually interfering with the glow layer beneath it). Fixed by computing an explicit `garagePreviewCanvas.style.width`/`style.height` in `drawGaragePreview()` that scales each sprite to fit within the stage while preserving its own aspect ratio.

### 3. Card frame colors simplified + click-to-buy now works on every locked car
Replaced the old amber "buyable" / dimmed "locked" split with the requested 3-state scheme: green border = equipped (unchanged), light grey `#8a93ad` = owned-not-equipped (unchanged), one darker grey `#333b4d` (+ reduced opacity) = not owned, regardless of affordability. Every not-owned card is now clickable (previously only affordable ones were): affording ones still open the normal buy-confirm dialog; unaffordable ones open a "NOT ENOUGH COINS — you need X more" dialog with the BUY button disabled and inert (`showConfirm()` gained an `opts.okDisabled` param; new `.btn-disabled`/`:disabled` CSS actually greys it out and blocks clicks via `pointer-events: none`).

### 4. New car hitboxes were wrong — real bug, not a tuning issue ("Road Train only half has a hitbox")
Root cause: `PLAYER_MAX_Y` was a module-level constant computed once at load time from the fixed old `PLAYER_HEIGHT` (31), used to clamp the player's vertical position. For any car taller than that (Road Train is 78), this let the player sit at a Y where the car's bottom extended far past the canvas — since traffic despawns once off-canvas, that off-canvas portion of the car never had anything to collide with, which is exactly the "only half of it has a hitbox" symptom. Fixed by making the bound a per-`Player`-instance `this.maxY`, computed from the actually-selected car's real height, used both by the vertical-movement clamp and the initial spawn position. The dead `PLAYER_MAX_Y` constant was removed.

**Verification**: live-tested in the Browser pane — confirmed all `h >= 30` cars (Tow Truck, Armored Van, Road Train, Tank, Land Speeder, Dragster, Limousine) render with `grid-column: span 2`; confirmed every not-owned tile has the single darker-grey border with no amber anywhere; confirmed clicking an affordable locked car completes a real purchase (coins deducted, ownership + equip state updated) and clicking an unaffordable one shows the correct shortfall amount with a disabled, inert BUY button (`pointer-events:none`, click has zero effect, dialog stays open); confirmed the Road Train preview canvas (native 31×78) now scales to fit fully within the 90×130 showroom stage with no clipping; confirmed per-car `maxY` for Stock/Kart/Limousine/Tank/Road Train all keep `y + height` within the 260px canvas with zero overflow (previously Road Train alone would have overflowed by ~59px under the old shared constant); confirmed no console errors throughout. **Not independently re-verified**: live pixel-level collision during actual gameplay across a tall car's full body (the `maxY` fix mathematically guarantees the car's hitbox never extends off-canvas anymore, which is the entire mechanism behind the reported bug, but a full played-out collision wasn't simulated on top of the direct math/state checks).

---

## 2.23.0 — 2026-08-26 02:30: Batch 89 — 16 new player vehicles added to the Garage

Ported the "TURN 2 — DRIVABLE ROSTER" section of a design doc the user uploaded (`Reckless Vehiclesv2.dc.html`) — 16 new player-drivable cars across 3 classes (5 Heavy, 6 Speed, 5 Oddity), added to `GARAGE_CARS` alongside the existing 10. Per direct instruction: prices only for now (no mechanics — the doc's own "score multiplier" per vehicle is NOT implemented, purely a display/pricing input), hitboxes adjusted, brake lights confirmed working, and a large coin grant for testing.

### The real problem this batch had to solve: these vehicles aren't the same shape as every existing car
Every one of the original 11 Garage cars (plus all NPC traffic) shares one convention: a 14px-wide native sprite, drawn 1:1 as both the VISUAL body and the GAMEPLAY HITBOX (`Player.width`/`height` has always just been the fixed `PLAYER_WIDTH`/`PLAYER_HEIGHT` constants, regardless of which of the 10 cars was equipped). The new vehicles break that on purpose — bodies range from 8px (jet bike) to 22px (monster truck) wide, all drawn on a shared 24px canvas so they "centre on a lane the same way" (the doc's own words), with the ACTUAL hitbox width given separately per vehicle (e.g. monster truck's 22×28 box on a 24-wide canvas; jet bike's 8×20 box on the same 24-wide canvas). Plugging these into the existing single-width system unchanged would have made every one of them visually render far wider than its lane (drawn at the full 24px canvas scale) while still colliding at the old fixed 18px box — a real, visible mismatch between what the player sees and what actually gets hit.

Solved with 3 pieces, all additive (nothing about the existing 10 cars or any NPC changed):
- `GARAGE_CARS` entries for the new 16 carry a `hitboxW` field (taken directly from the doc's "box" column) that entries for the old 10 simply don't have.
- `Player`'s constructor now sizes `this.width`/`this.height` from the SELECTED car's `hitboxW`/`h` when present, falling straight through to the untouched `PLAYER_WIDTH`/`PLAYER_HEIGHT` constants when it's absent (every existing car, unaffected).
- A new `carDrawOffsetX53(car)` shifts the DRAW position (not the hitbox) so a body that's centered within its own wider 24px canvas still lines up with where the hitbox actually is — verified by rendering each new car and confirming the drawn pixels' bounding box matches its stated hitbox almost exactly (a couple of vehicles overflow by 1-3px where the art itself has wide decorative details like the go-kart's mirrors or the land speeder's outrigger wheels, which is expected, not a bug).

This same fix threads through every OTHER place a car gets drawn: the live gameplay sprite, the red brake-light overlay (this is what "make sure back lights work on them" actually required — the old brake-light code hardcoded light positions assuming a 14px body, which would have put the lights in the wrong place, or off the visible body entirely, for every new car), the Garage preview canvas, and the car-tile grid (`CAR_TILE_FOOTPRINT` also bumped 28→60 so ROAD TRAIN, now the tallest car in the game, doesn't clip).

### Pricing and test money
Prices (3000-9000 coins) are a first-pass ladder loosely keyed to the doc's own "mult" column as a rarity/power proxy — since that multiplier isn't wired to anything yet, this is pricing only, not balance. Per "give me a lot of money for testing" — same problem as an earlier request this session (no tool-level access to the user's actual browser save data) — extended the existing `?resetprogress=1` one-shot URL-parameter pattern with a new `?testcoins=1` that sets `totalCoins` to 999,999 before the page finishes loading, then strips itself from the URL.

**Verification**: live-tested in the Browser pane — confirmed all 26 `GARAGE_CARS` entries (10 original + 16 new) with correct fields; bought and equipped every new car via `buyCar()`, confirmed each renders non-blank pixel data with zero errors; confirmed `Player.width`/`height` match the expected per-car hitbox size for several cars spanning the full range (jet bike 10×26 up to road train 18×78) while old cars (stock, hatch) stayed at the exact unchanged 18×31; confirmed drawn-sprite bounding boxes align with their hitboxes by scanning actual canvas pixel data (not just trusting the math) for 9 cars across both classes; confirmed brake lights render red pixels with no errors for 6 cars spanning old and new; confirmed the Garage preview canvas and 26-tile car grid render with correct per-car sizing and zero errors; ran 8 full 1000-frame gameplay simulations (one per a representative new car, including the widest/narrowest/tallest) with zero console errors and the player always staying within the road's bounds.

---

## 2.22.0 — 2026-08-26 01:50: Batch 88 — Performance Score on results, crash-sequence polish, siren timing, skip-hint visibility

Five separate pieces of direct feedback.

### Result screen now shows this run's Performance Score contribution
The osu-style weighted-decay Performance Score (`calculatePerformanceScore()`, and the per-entry "PERF" tag already shown in the Scores/Leaderboard list) was only ever visible later, when browsing Scores — not right after finishing a run. `saveScore()` already computes this run's global `rank` to build its return value, so the same formula (`score × 0.95^(rank-1)`) was added there too as `perfScore`, threaded through `CS.result` to a new PERFORMANCE SCORE row on the result screen (between RANK and COINS EARNED), animated in via the same `countUp()` every other result-screen number uses.

### Crash sequence: quieter sirens, responders always from the bottom, no more perfect alignment, headlights actually centered
- **Siren volume**: halved specifically for the crash-sequence's own siren (`updateSirenVolume()` gained an optional `volumeScale` parameter, defaulting to 1 everywhere else so the regular gameplay ambulance siren is unaffected) — was sustained at ~85% of max volume for the entire arrive/beat/resume tail of the sequence.
- **Arrival direction**: responders now always enter from BELOW the wreck, never above. The Batch 76 "pick whichever side has more clearance" logic could enter from above the wreck when a crash happened near the bottom of the player's legal Y range — inconsistent with every other vehicle on the road already traveling the same direction. Targets are still clamped to stay on-canvas in that same tight-clearance case, just always toward the bottom edge now instead of switching sides.
- **Perfect alignment**: 3 responders in 3 distinct lanes previously landed at the exact same Y offset from the wreck, reading as an unnaturally straight row. Added a small non-uniform per-responder Y stagger. Caught and fixed a follow-on issue during testing: the original on-canvas clamp applied independently to each responder, so all 3 collapsed back onto the same clamped ceiling whenever the wreck sat in roughly the bottom fifth of the legal Y range — recreating the exact alignment problem the stagger was meant to fix. Reworked to shift the whole staggered group uniformly instead of clamping each one independently, preserving the stagger's shape all the way to the extreme edge of the legal range (verified: 3 distinct target values at every tested Y from 40 to 228, including the worst case).
- **Headlight/light-bar centering**: a real, confirmed bug. The crash-sequence's light-bar overlay used one fixed set of offsets for both responder types, but police are drawn scaled to `PLAYER_WIDTH` (18px) via `drawScaledVehicle()` while the ambulance is drawn directly via `drawPixelAmbulance()` at its own native, un-scaled 14px width. The old offsets were centered correctly for police only (the small light rects) or the ambulance only (the glow rect) — never both. Both are now derived from each responder's ACTUAL rendered width, confirmed centered for both kinds via direct math verification.

### Ambulance siren heard earlier and for longer
"Extend the time the passing ambulance is heard after it disappears... also make it be heard earlier as well." The post-pass fade (`stopSiren()`) was stretched from a ~2.5s tail to ~4s. The pre-warning countdown's volume ramp previously started at the FULL `AMBULANCE_SIREN_RANGE` (effectively silent) for most of the countdown, only becoming audible near the very end — capped to 65% of that range instead, so there's already some audible presence from the start of the warning.

### Escape-skip hint made actually visible
`#crashSkipHint` ("[ESC] SKIP") was 7px at 28%-opacity cream — barely legible. Bumped to 11px, solid white, with a 4-directional black text-shadow (the standard pixel-font outline technique) forming a real frame around the text, per direct request ("white font with dark/black frame").

**Verification**: live-tested in the Browser pane — confirmed Performance Score math matches `score × 0.95^(rank-1)` exactly at both rank 1 and a lower rank with seeded competing scores; confirmed all crash-sequence responder ENTRY points are always below the canvas (`r.y > canvas.height`) across wreck positions spanning the player's full legal Y range (40/134/188/210/228) and lane counts (3/4/10), with all 3 TARGETS remaining on-canvas and mutually distinct in every case, including the extreme worst case; confirmed light-bar/glow centering math is exact for both police (center at 9) and ambulance (center at 7) via direct calculation; confirmed `getComputedStyle()` on the skip hint shows the new size/color/outline; ran a 1500-frame playthrough with a forced ambulance pre-warning and a 12-combination crash-sequence sweep (~7000 frames total) with zero console errors in either case.

---

## 2.21.0 — 2026-08-26 01:15: Batch 87 — real bugs fixed: NPC lane-change overlap, and score timing

Two direct bug reports, both real, both fixed at the root cause rather than tuned around.

### NPCs merging into the same lane and overlapping each other
"Cars switch lanes onto each other - they overlap each other - as they shouldn't." Traced to a genuine race condition in the lane-change state machine: `laneClearForMerge()` — the check that's supposed to stop a vehicle from merging into an already-occupied lane — only ever ran ONCE, at the moment a lane change is first *decided* (`changeLaneTimer` hitting 0). After that, the vehicle sits in an "indicator" (blinking-signal) state for up to `LANE_CHANGE_INDICATOR_MAX` frames before it actually starts moving into the new lane — and everyone else keeps driving during that whole window. Two failure modes fell out of this: (1) a check that was valid when first made could be stale by the time the vehicle actually commits, since another vehicle could drift into that lane in the meantime; (2) two vehicles in adjacent lanes could BOTH independently decide to merge into the lane between them, since neither's original check could see the other's still-pending decision (a vehicle's `.lane` doesn't update to its target until the indicator period ends, so the OTHER vehicle's mid-decision check sees it as "still in its old lane," not as "about to be in mine").

Fixed by re-validating `laneClearForMerge()` right at the moment `this.lane` is about to actually change (indicator → moving transition), not just once back at decision time. This closes both failure modes: a stale check gets caught by the fresh re-check, and a same-frame race gets caught too, since vehicles update sequentially each frame — whichever of two racing vehicles is processed first commits and updates its own `.lane` before the second one's re-check runs. If the lane's no longer clear, the merge aborts (`changingState` reverts to `'none'`, short 30-frame retry) rather than proceeding into an overlap — and this doesn't consume the vehicle's one-time `isLaneChanger` allowance, since it never actually changed lanes.

### Score for passing a car now counts when you actually pass it, not when it scrolls off-screen
"The score for passing an npc should be counted when your car surpasses it, not when the car goes off screen." Previously, score/XP/coins for a dodged vehicle were awarded only once it fully exited the canvas (`v.y > canvas.height` for normal traffic, off the bottom). Since the player's legal Y range (`PLAYER_MIN_Y`–`PLAYER_MAX_Y`, 40–228) sits well above the bottom of the 260px-tall canvas, a vehicle already fully passed and visually behind the player could still have to travel another ~30–220px (depending on where in that range the player was) before credit was actually given — a real, noticeable lag between "I just dodged that car" and the score updating.

Factored the reward logic into `creditVehiclePass(v)` and moved its trigger to the moment the player actually surpasses the vehicle: for normal traffic (approaching from ahead, spawned above), that's when the vehicle's front edge reaches/passes the player's front edge (`v.y >= player.y`); for ambulances (which overtake the player from behind, moving the opposite direction — Batch 52), the mirror condition on their trailing edge. A new `v.passScored` flag guards against firing twice; the vehicle isn't despawned at this moment either — it keeps visibly scrolling away and only gets removed from the `vehicles` array once it's actually off-screen, same as before, just with the reward already banked. The exit-time code path still exists as pure cleanup (despawn + a defensive fallback credit that should never actually trigger, since the surpass condition is always geometrically satisfied before a vehicle can reach its exit edge).

**Verification**: live-tested in the Browser pane — lane-change fix: reproduced the exact same-frame race (two vehicles in adjacent lanes both targeting the lane between them, indicator timers expiring in the same frame) and confirmed the second one now aborts instead of overlapping; reproduced the stale-check case (a vehicle already settled in a lane, another deciding to merge into it based on an old decision) with the same correct abort; confirmed the normal happy-path merge still succeeds when a lane genuinely is clear; ran 6 full playthroughs (~15,000 frames total) at 5 lanes checking EVERY pair of vehicles for `checkCollision()` overlap every single frame — zero overlaps found, zero console errors. Score-timing fix: confirmed via direct frame-by-frame tracking that a normal vehicle now scores ~80 frames before it despawns (previously simultaneous with despawn); confirmed the same for an ambulance overtaking the player; confirmed no double-crediting at the later despawn point in either case; confirmed the jump-over coin-bonus interaction is unaffected (`jumpedOver=true` still correctly skips the coin bonus in `creditVehiclePass()` while still crediting score/XP/dodgedCount).

---

## 2.20.2 — 2026-08-26 00:45: Batch 86 — one-time progress reset via URL parameter

Direct request: "reset all stats for me please and remove all scores" / "remove all bought things" / "i want like the new fresh game." Discovered that the Browser pane tab available to this session renders the file via a sandboxed `data:` URL — `localStorage` throws a `SecurityError` there ("Storage is disabled inside 'data:' URLs"), confirmed directly. That tab is not the user's real gameplay session and Claude has no other access to wherever the user actually plays (their own regular browser, opening the file directly) — there is no tool-level way to reach that origin's storage.

Since the leaderboard's CLEAR button was deliberately removed in Batch 82 (no in-UI way to wipe progress anymore, per direct request), the fix is a manual, one-shot escape hatch rather than a new visible button: opening the file with `?resetprogress=1` appended to its URL now clears `allTimeStats`, `highscores`, `selectedCarKey`, and `playerColor` before anything else on the page reads them, then strips the parameter from the URL via `history.replaceState` so reloading or bookmarking the resulting (now-clean) URL doesn't wipe progress again by accident.

**Verification**: live-tested in the Browser pane — seeded fake progress (level 42, 5000 coins, 2 owned cars, a saved highscore, custom color/car selection), reloaded with `?resetprogress=1`, and confirmed all 4 localStorage keys read back `null`, the in-memory `allTimeStats` reflects fresh defaults (level 1, only `stock` owned), and the URL had the parameter stripped automatically; ran an 800-frame playthrough afterward with zero console errors.

---

## 2.20.1 — 2026-08-26 00:30: Batch 85 — Garage preview background is now a color glow, not a road

Direct correction of Batch 83's static road background, same conversation: "i said remove the background beneath the car and replace it with like color around it." The road-texture attempts (Batch 69 scrolling, Batch 83 static dashes) were never actually what was being asked for — the request was for a plain background, just not a road graphic, and "around it" specifically meant surrounding the car rather than a flat rectangle under it.

Replaced `drawGarageRoadBg()` (dash pattern) with `drawGarageStageBg()` — a soft radial-gradient glow using the car's own live `playerColor`, bright near the car and fading to the stage's dark base (`#12161f`) at the edges. Moved the call from the Garage-open click handler into `drawGaragePreview()` itself, so the glow updates automatically whenever the color changes (car tile click, swatch click), not just when the Garage screen first opens.

**Verification**: live-tested in the Browser pane — confirmed the gradient center pixel value exactly matches the expected 50%-alpha blend of `playerColor` over the dark base (computed by hand for both the default blue and after switching to red, both matched precisely); confirmed the glow updates immediately on a color change with no separate trigger needed; ran a full Garage open/close cycle plus an 800-frame playthrough with zero console errors.

---

## 2.20.0 — 2026-08-26 00:15: Batch 84 — base font swapped from Pixelify Sans to DotGothic16

Direct feedback, with a screenshot of the Stats "SCORING" card's row labels ("RUNS PLAYED", "AVG (LAST 50)", etc.): "im talking about this font - i want to change it to something different (numbers look too similar to letters)." This is the game's DEFAULT font, set once on `body` and inherited by anything without an explicit override — mainly all 4 screen titles (Setup/Garage/Stats/Scores), every `<select>` dropdown, and every stat-row LABEL (the VALUES next to them are already VT323, changed for this exact reason back in Batch 70 — see the code comment history at `.stat-row span:last-child`). Swapped the Google Fonts `<link>` and `body`'s `font-family` from `'Pixelify Sans'` to `'DotGothic16'` — a clean dot-matrix pixel font with clearly distinct digit/letter shapes, different enough from Silkscreen's thick blocks to avoid reintroducing the "visually inconsistent" complaint that got Pixelify Sans picked over Silkscreen in the first place (Batch 68/70 history, same comment block).

Also fixed a stale, actively wrong code comment discovered while tracing this: `.stat-row span:first-child` (the labels) had a comment claiming "labels always stay Silkscreen, untouched throughout" — but that span has no font-family rule of its own at all, so it was always inheriting the BODY default (Pixelify Sans, now DotGothic16), never Silkscreen. Confirmed via `getComputedStyle()` before writing the correction. This is exactly why the "(LAST 50)" digits in a LABEL string were affected by the same complaint that had already been fixed for stat VALUES — the fix never reached the labels because the comment said it didn't need to.

**Verification**: live-tested in the Browser pane — confirmed `getComputedStyle()` on `body`, a stat-row label, and a `<select>` all report `DotGothic16` as the active font; confirmed (since DotGothic16 is a Japanese font with ~120 Unicode-range subsets, most of which report `unloaded` in `document.fonts` since they cover characters this game never uses) that the actual Latin-range subset our text needs reports `loaded`, and confirmed via `canvas.measureText()` that DotGothic16 measures differently from the Courier New fallback (176px vs. 211px for the same string) — proof it's genuinely rendering, not silently falling back; ran a full navigation sweep (Setup/Garage/Stats/Scores open+close) plus an 800-frame simulated playthrough with zero console errors.

---

## 2.19.4 — 2026-08-26 00:05: Batch 83 — Garage road background restored as a static image

Direct follow-up in the same message as the font feedback: "you did not remove the moving road beneath the preview car in Garage as i asked you too - replace it with a background." Batch 82 (previous turn) had removed the scrolling road-strip entirely per a "remove the moving road" request — verified at the time via `document.getElementById('garageRoadBg')` returning null, which WAS a correct, complete removal of what was literally asked. This message clarifies the actual intent: the complaint was about the MOTION, not the background's existence — a bare card-color box wasn't the wanted result either.

Re-added `#garageRoadBg` (HTML canvas + CSS, absolute-filling `.showroom-stage` same as before) and a new `drawGarageRoadBg()` that draws the same dash pattern (same proportions/shading/wear-variety as the real gameplay road) but **once**, with no `requestAnimationFrame` loop and no offset that advances over time — genuinely static, not just a very slow scroll. Called once when the Garage view opens (`garageBtn`'s click handler), not tied to color/car changes since a static image doesn't need refreshing.

**Verification**: live-tested in the Browser pane — confirmed `#garageRoadBg` exists again with non-background-color pixel data (dashes actually drawn, not blank); confirmed `typeof garageRoadAnimTick === 'undefined'` (the old animated version's function is genuinely gone, not just unused); ran repeated Garage open/close cycles plus a 1000-frame playthrough with zero console errors.

---

## 2.19.3 — 2026-08-26 00:00: Batch 82 — CLEAR removed from Scores, no way to delete saved runs

Direct feedback: "remove the Clear option from scores - now you cant delete anything." Removed the CLEAR button from the Leaderboard/Scores screen entirely (HTML, its `clearBtn` JS reference, and its click handler that called `localStorage.removeItem('highscores')` + reset the score-derived stats) — BACK is now the only button in that row. The now-unused `.btn-small` CSS rule (its only caller) was removed too. `showConfirm()` — the reusable themed confirm dialog, also used for Garage car/color purchases — had its CLEAR-SCORES-specific default title/text (`'CLEAR SCORES?'` and the long deletion-warning paragraph) replaced with generic empty-string fallbacks, since the only caller that relied on those defaults is now gone; the 2 remaining callers (buy car, buy color) already always pass their own explicit title/text, so this has no visible effect on them.

**Verification**: live-tested in the Browser pane — confirmed the CLEAR button is gone from the DOM and `clearBtn` has zero remaining references anywhere in the file (grep); confirmed BACK still closes the Scores screen correctly; confirmed the purchase confirm dialog (Garage) still shows real, non-blank title/text when triggered through the normal buy flow, unaffected by the default-text change; ran a full playthrough with zero console errors.

---

## 2.19.2 — 2026-08-25 02:45: Batch 81 — Garage header reordered to match Stats

Direct feedback: "in garage have the level in the same place as the in stats -> move the coins to the middle (they should be now in between level and the text Garage)." The level badge was a separate row below Garage's header (added that way in Batch 79); moved it INTO the `.view-header` row itself, as a third flex item alongside the existing title and coin-total — matching how Stats' header already places its level badge. `.view-header`'s existing `justify-content: space-between` handles the 3-item layout automatically (title at the left edge, level badge at the right edge, coin-total sitting in the equal gap between them) — no new CSS needed, just reordering the 3 existing elements into one row instead of two.

**Verification**: live-tested in the Browser pane — confirmed the header's 3 children read left-to-right as `H3` (Garage) → `.coin-total` → `.level-badge` via `getBoundingClientRect()`, with the coin-total genuinely sitting in the midpoint gap between the other two (not just visually near it); confirmed no overflow past the settings-panel's right edge; confirmed the level badge still paints the correct level/XP after navigating to Garage.

---

## 2.19.1 — 2026-08-25 02:35: Batch 80 — level ring's gray square background fixed to transparent

Direct feedback right after seeing Batch 79's relocated level widget: the ring canvas showed a solid gray square behind it, and the user asked for a list of the tier colors picked. The gray square was a real, simple bug — this codebase's global `canvas { background-color: #5a5f66; }` rule applies to every canvas element unless explicitly overridden (the coin icon classes already do this via `background: transparent`), and the new `.level-badge-ring-wrap canvas` rule never got that override when it was added in Batch 79. Added `background: transparent` (plus `image-rendering: pixelated`, also missing — needed to keep the 24→48px upscale crisp rather than browser-smoothed) to that one rule, which covers all 3 widget instances (Menu/Garage/Stats) since they share the same CSS class.

Tier colors (`LEVEL_TIERS`, unchanged from Batch 77 — reported to the user directly, not modified this batch): Iron `#8a93a3` (1-10), Bronze `#cd7f32` (11-20), Silver `#cbd2d9` (21-30), Gold `#f5b32a` (31-40), Emerald `#2ee6b0` (41-50), Sapphire `#4f6ef7` (51-60), Ruby `#ff4757` (61-70), Amethyst `#9b59b6` (71-80), Platinum `#cfe3f0` (81-90), Diamond `#7ff5ff` (91+, capped).

**Verification**: live-tested in the Browser pane — confirmed `getComputedStyle().backgroundColor` reads `rgba(0,0,0,0)` (transparent) for the ring canvas in all 3 placements (Menu, Garage after navigating to it, Stats after navigating to it).

---

## 2.19.0 — 2026-08-25 02:20: Batch 79 — level widget relocated to menus, Escape as a general back key, coin icon size fix

Three separate pieces of direct feedback.

### Player level widget moved out of gameplay, into Main Menu / Garage / Stats
"It doesn't look at all like the one i gave you (the file design), it is not displayed in Stats and Garage and Main menu — it shouldn't be displayed in gameplay." The gameplay-HUD version (a 20px chip squeezed next to the score) is gone entirely — `#hudLevel` and its CSS/JS removed, along with its per-frame repaint in the main game loop. Replaced with THREE separate instances of the same widget (Main Menu top-right corner, Garage below its header, Stats in a new header row mirroring Garage's), all painted by one shared `paintLevelBadge(ringCanvas, numEl, xpEl)` function — repainted only when that screen becomes visible (`refreshMenuSummary()`, `showStats()`, the Garage button's click handler), not every frame, since none of these screens are live during gameplay. The ring itself is now much closer to the actual design doc: native 24×24 canvas with the doc's exact radii (8.2/11.2), CSS-scaled to 48px display (2×) so it stays crisp pixel art instead of a smoothed circle — was a flat 20×20 1:1 canvas before, nowhere near the doc's chunkier look. The one-line XP readout (`837/1550`) from the previous round of feedback is kept as-is — that fix wasn't what this complaint was about.

### Escape now works as a general "back" key
"The esc still doesn't work as a back button in most windows." Previously Escape only did two things: skip the crash sequence, and toggle the pause menu during gameplay. Added a new priority-ordered branch (checked before the pause-toggle line, each firing a `return` so only one thing happens per keypress): closes the confirm dialog, or clicks whichever screen's own visible BACK button is relevant (Setup, Garage, Stats, Leaderboard), or — for the Game Over screen specifically, which is a DOM overlay inside `gameView` rather than its own view, detected via `gameView.classList.contains('active') && !gameActive && !CS.active && gameOverHud.style.display !== 'none'` — clicks the MENU button. Each branch clicks the SAME button element the screen's own UI already uses rather than duplicating that button's logic, so it can't drift out of sync if those handlers change later.

### Garage price-tag coin icon resized to match the header's coin icon
"The coin icon in garage next to the price is way too small — make it the same size as the one in top right (that shows how much money you have got)." `.coin-icon-sm` (used on locked/buyable car tiles' price badges) was 5×5px — the end result of TWO earlier rounds of "still too big" feedback (Batch 68, Batch 70) that had gone the other direction. Set to 22×22px, exactly matching `.coin-icon-lg` (the Garage header's own total-coins display) rather than picking an in-between value — a direct, unambiguous instruction, not a judgment call.

**Verification**: live-tested in the Browser pane — confirmed the old gameplay-HUD level elements (`#hudLevel` and children) are completely gone and no console errors occur across a 1500-frame simulated playthrough; confirmed all 3 new level-badge instances render the correct level/XP/tier-color after setting `allTimeStats.playerLevel`/`playerXP` directly, both immediately (Menu) and after navigating to Garage/Stats and back; confirmed the ring canvas produces non-blank pixel data at its native 24×24 resolution; confirmed Escape closes Setup, Garage, Stats, Leaderboard, the confirm dialog, and the Game Over screen (via a forced `endRun()` + `skipCrashSequence()`), each landing back at the correct screen; confirmed Escape's existing pause-toggle behavior during actual gameplay is unaffected (still toggles pause on and off); confirmed `getComputedStyle()` shows the Garage price-tag icon and header icon are both exactly 22×22px; confirmed `getBoundingClientRect()` layout checks show no overflow past the canvas/panel edge for any of the 3 level-badge placements.

---

## 2.18.1 — 2026-08-25 01:40: Batch 78 — nitro/score-boost pickups removed

Direct feedback right after 2.18.0 shipped: "remove everything that has to do with the pickups... its a bit complicated and i dont want to overcomplicate the game." Full removal of both pickups and everything that supported them — sprites (`drawPickupNitro`, `drawPickupScoreBoost`, `pxStamp`, the bolt pixel patterns), the `pickups` array and its spawn/update/collision/draw loop in `loop()`, the nitro speed-boost and score-boost multiplier logic (the two `score +=` sites are back to their pre-Batch-77 form, no boost factor), the active-effect HUD chips (`#pickupChips` and its two children, in both HTML and CSS), the spawn-timer state and `rollPickupSpawnDelay()`, and every reset/cleanup call site that referenced them (`launchGame()`, `exitToMenu()`, `endRun()`). `allTimeStats.totalPickups` and the Stats tab's PICKUPS row are left in place exactly as they were BEFORE Batch 77 — an inert placeholder reading 0, matching the state this project has been in since Batch 61 first added the Stats tab, not something added or owned by the pickups work being removed here.

**The player level widget (ring, one-line XP readout, 10-tier color system) was NOT touched** — the user's feedback named "pickups" specifically, and leveling is a separate system with no dependency on pickups (`gainXP()` is called from the same two score sites, using the raw point values, unaffected either way).

**Verification**: grepped for every pickup-related identifier (`nitro`/`Nitro`/`NITRO`, `scoreBoost`/`ScoreBoost`/`SCORE_BOOST`, `pxStamp`, `PICKUP_SIZE`, `pickupsThisRun`, `renderPickupIcon`) — zero remaining matches; a separate case-insensitive `pickup` grep confirms only pre-existing, unrelated matches survive (the `pickup` vehicle body type, the `totalPickups`/`statPickups` placeholder). Live-tested in the Browser pane: no console errors on load; ran a 2000-frame simulated playthrough with no errors; confirmed the level widget still updates correctly (ring, one-line XP text) with no pickup code present; confirmed the removed DOM elements (`#pickupChips`, `#nitroChip`) are genuinely gone from the page.

---

## 2.17.1 — 2026-08-25 00:30: Batch 76 — responders now spread across lanes, not stacked in one

Immediate follow-up after 2.17.0 shipped, same session: user reported responders arriving in the SAME lane as the player/each other, overlapping. Batch 75's "room-aware stacking" fix picked which side of the wreck (above/below) had Y clearance but kept every responder at the same X (the wreck's own lane) — correct for the off-canvas bug it targeted, but not what "arrive on the side" means. In `csEnterPhase('arrive')`: compute the wreck's lane index from its X, then pick 3 lanes near it (immediate neighbors first, expanding outward), skipping any lane that's off the actual road (`config.lanes`, which can be as few as 3) rather than clamping onto an edge lane multiple responders would then share. Falls back to reusing a lane (with the existing Y-offset stack as an anti-overlap fallback) only when the road genuinely doesn't have 3 lanes to spare — verified this only ever happens transiently on a 3-lane road, where all 3 lanes get used anyway.

**Verification**: live-tested in the Browser pane at 3/4/10-lane road widths with the wreck in the leftmost, middle, and rightmost lane each — confirmed all 3 responders land in 3 distinct, valid lanes in every case (including both edges of a 3-lane road, where there's no slack at all); confirmed a full phase cycle at the bottom of the player's legal Y range in the leftmost lane runs 581 frames with no errors.

---

## 2.17.0 — 2026-08-25 00:00: Batch 75 — crash sequence refinements from real feedback

Replaces the instant `endRun()` → Game Over cut with a 6-phase sequence: impact flash + shake → wrecks smoulder → distant siren + a typed-out newspaper clipping → police/ambulance arrive → light bars flash → traffic resumes and the scene drifts off-screen → the result screen counts up instead of appearing fully-formed. Escape skips straight to the final result at any point.

Applied from a detailed external patch spec, but NOT pasted in verbatim — read the actual current code at every integration point first and adapted anywhere the spec's assumptions had drifted from this file's real state (it explicitly flagged several of its own guesses as unverified, correctly it turned out). Real deviations from the spec, and why:

- **Timing model**: the spec used `performance.now()`/millisecond phase durations with its own delta-time tracking. Every other timer in this codebase (`changeLaneTimer`, `indicatorTimer`, the `currentSpeed` ramp itself) is a plain per-frame counter, not wall-clock time — rewrote the whole state machine to match (`CS.t`/`CS.total` increment by 1 per rendered frame, `CS_PHASES` are frame counts at an assumed 60fps: flash=11, hold=72, sirens=108, arrive=120, beat=60, resume=120). Avoids introducing a second timing convention into the file, and the newspaper typewriter effect became a plain `slice()` proportional to phase progress instead of a separate `setInterval` clock that would drift from the rAF loop and need its own cleanup path.
- **`drawFn` closures**: the spec's wreck-drawing callback declared a `(c) =>` parameter expecting to receive the canvas context — but this codebase's `drawScaledVehicle()` always calls `drawFn()` with zero arguments, every existing body-draw call site captures the outer `ctx` directly in its closure instead. Fixed to match.
- **`loop()` integration**: the spec's plan would have called `drawRoadScene()` a second time and/or drawn UNDER the existing `else { rgba(0,0,0,0.85) fillRect }` Game Over dark overlay, which it didn't seem to account for. Actual integration: `roadOffset`/`currentSpeed` control was added to the EXISTING `if (gameActive) {...}` road-scroll block (as an `else if (CS.active)` branch, before the single existing `drawRoadScene()` call), and sequence rendering was added as a new `else if (CS.active)` branch alongside the existing dark-overlay `else`, not a bolted-on block after it.
- **`endRun()` reset function**: the spec guessed `startGame()` — this codebase's actual reset/retry function is `launchGame()`.
- **`{cars}`/`{speed}` newspaper placeholders**: the spec guessed a `passedCount` variable (doesn't exist) and an invented `currentSpeed × 18` conversion. Used the real `dodgedCount` stat and the same `speedToKmh()` the live HUD already displays, instead of a second/different speed formula existing side-by-side with the HUD's own.
- **`{culprit}` naming**: the spec's `CULPRIT_NAMES` was keyed by vehicle BODY (sedan/hatch/taxi/etc.) — but `endRun()`/newspaper only ever receive the vehicle's `type` (normal/truck/reckless/motorbike/tractor/ambulance), so a body-keyed map would have silently fallen back to "ANOTHER VEHICLE" for almost every crash. Reused the existing `DEATH_TYPE_LABELS` (already exactly this type→name mapping, used by the Stats WRECKED BY card) instead of maintaining a second parallel name list.
- **Responder color**: the spec passed an invented color into `drawBodyPolice53()` — that function actually takes no color parameter at all (fixed livery, unlike every other body-draw function); the extra arg would have been silently ignored. Called it correctly with no color arg. Ambulance responder color needed no invention either — `v.color` is already the ambulance's real spawn color (`'#f8f9fa'`), used directly instead of a guessed hex value.
- **CSS `nth-of-type` row count**: the spec assumed 6 stat-rows in the Game Over stat-box; this build actually has 5 (BASE/MULTIPLIER/SURVIVED/RANK/COINS EARNED — COINS EARNED didn't exist when the spec was likely drafted). Adjusted the entrance-animation delays to match.

**Verification**: live-tested in the Browser pane — triggered the full sequence via a simulated collision and stepped it frame-by-frame through all 6 phases to completion with no errors; confirmed the newspaper headline reveals progressively (`"INVESTIGATORS BA"` partway through, matching the expected fraction of phase progress); confirmed Escape-skip shows final values instantly with no animation class, while letting the sequence play through shows `0` initially then animates up via `countUp()` to the exact correct final numbers (score 850, base 800, coins 60 = 40×1.5 multiplier, matching the math exactly); confirmed the no-geometry fallback (`endRun(type)` with no rects) still does the old instant cut unchanged; confirmed all 4 wreck variants render visible, non-empty pixel data with no errors; confirmed `launchGame()` correctly resets all crash-sequence DOM/state even from a deliberately-dirtied mid-sequence state. Couldn't verify the VISUAL result (screen shake, wreck positioning/color, responder light-bar flashing, newspaper layout) — Browser pane screenshots weren't compositing this session, same known limitation as recent sessions; this is now the single largest piece of unverified-visually work in the project.

## 2.15.0 — 2026-08-26 00:10: Batch 73 — Garage redesign round 2, from a real screenshot

User sent a screenshot of the actual rendered Garage this time — caught a real CSS bug my own tooling couldn't see, plus several structural requests.

### Real bug: card cost coin icons were rendering at 38×38px, not 5×5px
`.car-tile canvas` (added to size the car SPRITE canvas, a descendant selector matching ANY canvas anywhere inside a card) had higher CSS specificity (class+type) than `.coin-icon-sm` (class only) — so it silently overrode the coin icon's own sizing rule, forcing it up to 38px regardless of what `.coin-icon-sm` said. Fixed by changing the sprite rule to `.car-tile > canvas` (direct-child only) — the coin icon is nested inside `.car-tile-lock`, two levels deep, so it was never meant to be caught by that rule at all. **This is a case where a screenshot found something structural verification genuinely could not** — every earlier check confirmed `.coin-icon-sm{width:5px}` existed and was being applied to the right element; none of them re-derived the actual CASCADE-WINNING rule, which required knowing both selectors' specificity.

### Showroom simplified — removed the redundant model name + EQUIPPED tag
The equipped car is already shown clearly in the Car Model grid below (mint border + its own EQUIPPED tag) — the duplicate name/tag above the paint picker was redundant, per direct feedback. (Side effect of removing the DOM elements: `drawGaragePreview()` still had a line writing to the now-gone `#showroomModel` — a real `TypeError` that was silently swallowing the rest of `garageBtn`'s click handler, leaving the ENTIRE Car Model grid empty. Caught and fixed via live testing before this shipped, not by the user.)

### Paint colors split into two rows: owned, and a "TO BUY" row
`GARAGE_COLORS` — colors moved from a bare `color→cost` map to a full array (name+color+cost, matching `GARAGE_CARS`'s own shape) since the picker now needs to render dynamically rather than toggle classes on fixed HTML. `renderColorPicker()` rebuilt from scratch (was: static swatches, listeners attached once) to actually construct swatch elements into `#colorPickerOwned`/`#colorPickerBuy` based on live ownership, matching `renderCarGrid()`'s rebuild-every-call pattern — a color needs to physically MOVE rows when bought, which toggled classes on fixed elements couldn't do. The "TO BUY" label is amber-tinted to match the buyable-cue color language elsewhere.

### Car cards: explicit 3rd "owned, ready to go" state
Previously only had equipped (mint)/buyable (amber)/locked (dimmed) — an owned-but-not-currently-equipped car had no explicit styling, just the default border. Added `.car-tile.owned` (light grey border) so it reads as a deliberate state rather than "no state." Same grey-cue idea extended to color swatches (`.buyable-swatch`, amber border, mirroring cars).

### Garage road background now matches the real gameplay road exactly
Was a smaller/plainer placeholder (`dh=7,dp=15`, flat single color, no wear variety) — per direct feedback ("make it identical to the gameplay"), now uses the SAME dash proportions, 2-tone shading + dark underside, and the same 1%-missing/4%-faded wear variety as `drawRoadScene()`'s real lane dashes.

**Verification**: live-tested in the Browser pane — confirmed the coin-icon fix (`getComputedStyle` → 5px×5px, was 38px); confirmed the `showroomModel` TypeError was real (reproduced it before the fix, confirmed gone after) and that the whole Car Model grid was empty as a direct consequence — a serious regression caught before it reached the user; confirmed all 4 card states render with the right class (`equipped`, `owned`, `buyable`, `locked`) against a realistic coin/ownership scenario; confirmed the color picker splits 2 owned / 8 to-buy correctly; confirmed `drawGarageRoadBg()` runs without error and produces visible dash pixels matching the expected light fill color.

## 2.14.2 — 2026-08-25 23:20: Road-stripe wear/fade set to exact requested rates

Follow-up to 2.14.1 — user gave exact numbers: missing-dash chance set to 1%, faded-dash chance to 4% (verified with a 10,000-sample run: 0.99% / 4.29%, matching).

## 2.14.1 — 2026-08-25 23:15: Road-stripe wear/fade made much rarer

User confirmed the Batch 69 road-stripe variety itself (missing/faded dashes) works as intended and liked it — just wanted it rarer. Missing-dash chance cut 10%→3%, faded-dash chance cut 15%→7% (verified with a 10,000-sample run: 3.03% / 7.22%, matching). No other change — the flicker bug from 2.14.0 was a separate, already-fixed issue (the two probabilities here are unrelated to that sign error).

## 2.14.0 — 2026-08-25 23:00: Batch 71 — road-stripe flicker regression fix, siren rework, speed ramp

### Real bug found: road stripes (and night-mode building lights) were flickering
Both 2.12.0 additions computed a "stable per-dash world-position index" as `Math.round((y + offset) / dp)` — wrong sign. The dash-placement loop guarantees `y ≡ offset (mod dp)`, so the invariant quantity is `(y - offset)`, not `(y + offset)` — the `+` version drifts by roughly 2×offset as the road scrolls, so the "same" physical dash got a different pseudo-random seed almost every frame instead of a stable one. This is almost certainly also the cause of the reported "NPC cars look blurry/stuttery" — flickering stripes right next to moving traffic reads as general visual noise around the cars, even though the car sprites themselves were never touched. Fixed both occurrences (`dashIdx`, `bIdx`) to `(y - offset)`.

### Game speed ramp cut ~40%
`currentSpeed += 0.0005` → `0.0003` per frame — per direct feedback ("game speeds up way too fast"), first-pass tuning number.

### Ambulance siren rework
Three changes, all from one piece of feedback: "the sound should be played right as the warning goes off, not only when the ambulance goes by... and after it passes, still played but going off in the distance."
- **Starts at the pre-warning, not at spawn.** `pendingAmbulances.push()` now calls `startSiren()` immediately (was only called in the `Vehicle` constructor, i.e. once the countdown already ended and the real vehicle existed). During the countdown, `updateSirenVolume()` is fed a SYNTHETIC distance (`AMBULANCE_SIREN_RANGE × timer/totalWarnFrames` — starts near-silent, reaches 0/loudest exactly as the countdown ends) since there's no real vehicle position yet to measure against.
- **Handoff, not a second siren.** `Vehicle`'s constructor takes an optional 3rd `presetSiren` param — when the countdown ends and the real ambulance spawns, it's passed the SAME siren instance the pending-warning already started, rather than creating a new oscillator (which would double up/glitch). `new Vehicle(pa.lane, 'ambulance', pa.siren)`.
- **Longer fade-out.** `stopSiren()`'s decay time-constant went from 0.1s to 0.6s and the oscillator stop time from `now+0.4s` to `now+2.5s` — a genuinely audible ~2.5s trailing fade instead of a "just avoid a click" cutoff.

**Verification**: live-tested in the Browser pane — confirmed the OLD dash-seed formula drifted for the same physical dash across increasing offsets (0→7→18) while the FIXED formula stays constant (0→0→0); confirmed a pending-ambulance siren correctly gets hand off to its real `Vehicle` instance (`v.siren === pa.siren`, `activeSirens` count unchanged, no duplicate oscillator); confirmed `updateSirenVolume()`/`stopSiren()` run without error against the new synthetic warning-phase distance and the lengthened fade. Couldn't confirm the flicker/blur fix VISUALLY (Browser pane screenshots still not compositing this session) — the math fix is verified correct, but whether it fully resolves the perceived blur needs the user's own look.

## 2.13.0 — 2026-08-25 22:15: Batch 70 — Garage road/purchase fixes, Stats font/layout/leaderboard fixes

Two rounds of follow-up feedback after actually seeing 2.12.0's work, addressed together.

### Garage
- **Preview car looked like it was straddling the lane divider** — `drawGarageRoadBg()` drew ONE dash line dead-center, exactly where the (also centered) preview car sits. Now draws lane-boundary lines to either SIDE of the car instead, near the stage's edges — nothing runs under the car, matching how a real lane looks from above.
- **Purchases now require confirmation** — `showConfirm()` (previously hardcoded to the CLEAR SCORES text) is now reusable: takes optional `{title, text, okLabel, danger}`, defaulting to the original CLEAR SCORES wording so that call site didn't need to change. Both the car-buy and color-buy click handlers now show a themed confirm ("BUY HOT HATCH? This costs 150 coins.") before `buyCar()`/`buyColor()` ever runs — coins are never touched until the user confirms.
- **Coin icon in card cost labels halved again** (10px → 5px) — still "way too big" per feedback even after the first size pass.

### Stats
- **Stat-value font changed a third time** — Silkscreen (digits confused with letters) → Pixelify Sans 2.9.0 (fixed that, read as inconsistent with the rest of the UI) → Silkscreen again 2.11.0 (matched the UI, reintroduced the digit-confusion complaint) → **VT323** now (2.13.0) — a purpose-built terminal/counter font, unambiguous digits, still reads as "retro" without being a stylistic mismatch. Only one weight available on Google Fonts, so size was bumped instead of using bold.
- **"COINS" renamed to "TOTAL COINS"**, and fixed a real layout bug where the coin icon could wrap onto its own line above the text — the label was a plain inline `<span>`, now `.stat-row-icon-label` (`inline-flex; white-space:nowrap`) keeps icon+text together on one line.
- **WRECKED BY card now spans the full width** (both grid columns) instead of sharing a row with TIME ON THE ROAD — gives the death-figure sprites real room (the tractor's rounder silhouette was still reading as cut off in the old half-width column even after 2.12.0's aspect-ratio fix). `.fig-grid` also switched from a fixed 2-column layout to `repeat(auto-fill, minmax(90px,1fr))` to actually use the new space. TIME ON THE ROAD sits alone in its row at normal half-width — it only has 2 rows of data since 2.12.0 removed Highest Multiplier, so the leftover space reads fine.

### Scores / leaderboard
- **"PP" renamed to "PERF"** — per direct feedback ("I didn't ask for that, I'd rather it say performance score") — shown as "PERF 950" instead of "950 PP", avoiding both the osu-specific jargon and an awkward two-letter abbreviation.
- **Time now shown as M:SS** ("1:30") instead of raw seconds ("90s") — reuses the existing `formatTime()` helper (`entry.timeSurvived` is stored in seconds, so `formatTime(entry.timeSurvived * 1000)`).

**Verification**: live-tested in the Browser pane — road-bg dashes confirmed drawn near the stage edges (x=4, x=w-6) not center; buy confirmation confirmed to leave coins/ownership untouched until `confirmOkBtn` is clicked, then correctly deducts/marks-owned/auto-equips (tested with Formula: 5000→800 coins, owned, auto-equipped); stat-value computed font confirmed `VT323, monospace`; the coin-total label confirmed `white-space:nowrap` and correct "TOTAL COINS" text; `.stat-card-wide`'s computed `grid-column` confirmed `1 / -1`; the tractor figure's rendered size confirmed aspect-correct (94×30, close to the native 56:16 ratio) instead of the old distorted stretch; leaderboard time/PERF label confirmed exact text ("1:30", "PERF 1,000").

## 2.12.0 — 2026-08-25 21:30: Batch 69 — a 27-item feedback pass across nearly every system

The user's largest single feedback message this project — 27 items. 24 implemented here; 1 (obstacles/warning signs) deliberately deferred and asked about, since it was already flagged in PLAN.md as needing a design pass before this message and nothing in it actually specified what the obstacle is or does, just that a warning sign should announce it. Two items were direct questions, answered in chat rather than code: the rightmost number on the Scores screen is time survived; the Steering Buttons control's forward/backward gap (below) was a real bug this exposed.

### Bug fixes
- **Motorbike centering** — `drawBodyBike53`'s coordinates assumed the same 14px-wide native canvas every other body uses, but the motorbike is the one body with a narrower `width` override (6px, for its narrow hitbox) — `drawScaledVehicle()` centers on the vehicle's own declared width, not on wherever the draw function's coordinates happen to be centered, so the sprite rendered ~4px off-center. Every x-coordinate shifted -4 to center for its real width.
- **Gray canvas backgrounds** (coin icon, Garage card sprites) — the global `canvas{background-color:#5a5f66}` rule (for the main game canvas) was leaking through on every small icon/sprite canvas. Added explicit `background:transparent`.
- **Garage card / Stats tractor sprites "don't fit"** — same root cause in both places: a canvas with a hardcoded CSS `width` independent of its own real aspect ratio stretched the sprite to fill it. Fixed with `height` fixed + `width:auto` (derives from the canvas's real `width`/`height` attributes) — reads worst on the tractor's rounder silhouette but affected every figure.
- **Steering Buttons control had no forward/backward input at all** — a real gap the user's own question exposed: when Control Type was Steering Buttons, neither keyboard scheme was active, so Up/Down had nothing to key off. Up/Down (and W/S) now always work for accel/brake regardless of Control Type — it isn't a lane-steering input, so it was never supposed to be gated by that choice.

### Garage / coins
- **Sprites rotated to fit + bigger cards** — same fix pattern as the sprite-fit bug above, taken further: card sprites now draw rotated 90° (reusing the Stats WRECKED BY figures' `drawSideways` helpers) so the car's long axis lies along the card's wide axis, plus bigger `minmax()` grid cells and padding.
- **Garage header shows coin total**, opposite the "Garage" title — new `.view-header` class.
- **Removed the 🔒 lock icon** — the dimmed styling already conveys "can't have this yet," the cost figure alone is enough.
- **Real coin icon** — user uploaded `coin-preview.html`, a complete pixel-art coin sprite (`drawPixelCoin()`, 16×16, car silhouette). Ported verbatim, replaces the 🪙 emoji placeholder everywhere; smaller variant (`.coin-icon-sm`) for the Garage's per-card cost figures.
- **Cars must be actively bought, not auto-unlocked** — reaching a coin threshold used to make a car available automatically; now `allTimeStats.ownedCars` tracks real purchases (`buyCar()` deducts coins, permanent) and a card has 4 states: equipped, owned-not-equipped, affordable-buyable (amber border, click to buy+auto-equip), locked.
- **Colors must be unlocked too** — same buy pattern (`allTimeStats.ownedColors`, `COLOR_COSTS` — a first-pass cosmetic price ladder, Blue free/default). Locked swatches are dimmed; cost shown via the native title tooltip (swatches are too small for on-swatch text).
- **Garage preview car now drives on a road** — was a bare background; added a small scrolling road strip (asphalt + center dashes, deliberately simpler than the full biome road system) behind the preview, animated via its own small rAF loop tied to the Garage view's open/close rather than the main game loop.

### Scoring / stats
- **Performance Score contribution shown per score** on the leaderboard screen (top 100 only — the leaderboard is already capped there) — `score × 0.95^(rank-1)`, rank computed against the GLOBAL sort so a lane-count filter doesn't shift it.
- **Removed "BEST xxx"** from the main menu's bottom-left corner, and **"HIGHEST MULTIPLIER"** from the Stats TIME ON THE ROAD card (tracking itself untouched, just not displayed).
- **Clearing scores now also resets score-specific stats** (Total Score, the Avg-Last-50 sample) — NOT coins or any other lifetime stat (driving/time/deaths). Confirm dialog text updated to say so.
- **Score multiplier now has a live speed component** — `multiplier = baseMultiplier + speedRatio × SPEED_MULT_BONUS_MAX` (up to +1.0 at max speed), recomputed every frame. Everything that already read `multiplier` (scoring, HUD, coins-at-end, Game Over/leaderboard) picks this up automatically — it was already the single value all of those flowed through.
- **Quitting mid-run now saves score and coins** — `exitToMenu()` calls `saveScore(null)` when `gameActive` is still true at the moment of quitting (a run that already crashed has already set it false via `endRun()`, so this can't double-save).

### NPC traffic / difficulty
- **Non-reckless vehicles can no longer merge into the player's lane at point-blank range** — `laneClearForMerge()` now also checks distance to the player specifically (a bigger buffer than the vehicle-vehicle one, first-pass tunable), except for reckless drivers, who keep the existing chaotic behavior on purpose.
- **Reckless drivers' speed range widened** — was actually narrower than normal traffic's own range (+0.3 to +0.8 vs normal's -0.5 to +1.0); now -0.2 to +1.6, genuinely the widest/most unpredictable of any type.
- **Road stripe variety** — a stable per-dash pseudo-random pick (seeded by a world-position-invariant index, not raw screen y, so a dash doesn't flicker between frames) makes ~10% of dashes worn away entirely and ~15% rendered faded, like real road wear.

### Player feel
- **Forward/backward movement halved** — every vertical constant (`V_MAX_BASE/TOP`, `V_ACCEL`, `V_FRICTION`, `V_BRAKE`) scaled ×0.5, preserving their relative ratios.
- **Lane-switching sensitivity reduced ~20%** (`HORIZONTAL_GLIDE_SPEED_BASE/MAX` ×0.8) — first-pass tuning.
- **Brake lights** when moving backward (`vVelocity > 0` — this game's Down key doubles as brake+reverse, so "moving backward" is the practical brake signal). Drawn as a second overlay pass in the same transformed space rather than added to all 11 car sprites individually.
- **Control Type reverted to a 2-way choice** (Arrows/WASD combined vs Steering Buttons) — the previous strict 3-way split (separating Arrows from WASD) is undone per direct request ("combine arrows keys and WASD, they can be used together").

### Night mode overhaul
Darkness raised from 0.72 to 0.9 alpha (should be genuinely hard to see without a light source, not just dimmed). Three light sources now punch through it: the player's headlight cone (narrower/more forward-biased than before), a small warm glow at every NPC vehicle's own position (ambulances tinted blue-white) so traffic reads as "a car with lights" rather than a slightly-less-dark blob, and scattered roadside window-light glows standing in for the biome's houses/buildings (deterministic per scroll position via the same seeded-pseudoRandom pattern as the road-stripe wear).

**Verification**: the Browser pane's rAF/frame compositing was stalled again this session (`roadOffset` never advanced even with the tab fronted) — a known, previously-documented environment limitation, not a code issue. Verified via direct function calls instead: `buyCar()`/`buyColor()` correctly deduct coins and mark ownership (200→50 coins, 100→20 coins, matching exact costs); `exitToMenu()` correctly saved a score when called with `gameActive=true` and did NOT double-save on a second call after `gameActive` was false; `laneClearForMerge()` correctly blocked a close normal-type merge into the player's lane, allowed a far one, and let a reckless-type merge close anyway; the live-multiplier formula produced exactly 2.7 for `baseMultiplier=1.7` at max speed ratio; `Player.draw()` with `vVelocity>0` (brake lights active) and the full night-mode draw block (manually replicated) both ran with no errors; the Garage/Stats screens loaded with the removed elements actually gone and the new ones present. No console errors on page load or during any of the above.

## 2.11.0 — 2026-08-25 19:55: Batch 68 — real coin sprite, Garage card fixes, reverted stat-value font

Four follow-up fixes from the user actually looking at 2.10.0's Garage/coin work.

### Real coin icon (user uploaded `coin-preview.html` — a complete, ready-to-use sprite)
Ported `drawPixelCoin()` verbatim: a 16×16 struck-disc coin with a front-on car silhouette punched into it. Replaces the 🪙 emoji placeholder everywhere: Game Over, Stats, and the Garage grid's locked-tile cost. A small `renderCoinIcon(canvasEl)` helper fills a `<canvas class="coin-icon">` with it at native resolution; CSS scales the display size (14px inline, 22px for the Garage header).

### Garage card sprites — fixed the actual "doesn't fit" cause, made cards bigger
The car sprite is natively tall/narrow (matches its in-game orientation) but the card is a short/wide box. Drawing it upright into a canvas whose CSS `width` was hardcoded independent of its native aspect ratio meant the sprite got stretched horizontally to fill that width — that non-uniform stretch was the actual "doesn't fit" bug, not a sizing issue. Fixed two ways together: (1) the sprite is now rotated 90° (`drawSideways`/`drawSidewaysCentered` — the same helpers the Stats WRECKED BY figures already used), so its long axis lies along the card's wide axis; (2) the canvas's CSS is `height` fixed + `width: auto`, so the displayed size always matches whatever aspect ratio the canvas's own `width`/`height` attributes describe — no distortion possible regardless of future size tweaks. Also bumped the grid's minimum card size (68px→92px) and internal padding, per "make these car boxes bigger."

### Garage header now shows the player's coin total
`.view-header` (title left, arbitrary content right via `justify-content: space-between`) — Garage is the first view to use it; other views still use a bare `<h3>`. Shows the coin icon + `allTimeStats.totalCoins`, refreshed every `renderCarGrid()` call (garage open, car equip, color change).

### Removed the 🔒 lock icon from locked cards
Per direct feedback ("no need for lock icon, the cost is enough") — a locked card is already visually distinct via its dimmed/opacity styling; the cost figure alone (now with the real coin icon next to it) carries the needed information.

### Reverted stat-value font from Pixelify Sans back to Silkscreen
2.9.0's font swap (aimed at fixing "50 is hard to read") turned out to read as visually inconsistent against the rest of the UI once actually seen — buttons, window titles, and every other piece of chrome use Silkscreen, and Pixelify Sans stood out as a mismatch. Reverted `.stat-row span:last-child` and `.fig-val` to Silkscreen (bold, slightly larger than the original — 12px/10px vs the pre-2.9.0 10px — to still address the original legibility complaint without changing font family this time).

**Verification**: live-tested in the Browser pane — Garage grid tile canvases now measure 28×18 (the rotated footprint × `PLAYER_WIDTH`, matching the sprite's real proportions exactly, confirmed via `getImageData` showing a non-empty car silhouette filling ~60% of the canvas as expected for a car shape); the coin icon's pixel data confirmed both its yellow body and black outline render; the Garage header's coin total updated correctly (1,250 → tiles unlocked up to that cost, locked above it); `.view-header` confirmed as a `flex`/`space-between` row with exactly the title and coin-total as its two children; stat-value computed style confirmed `Silkscreen, 700`. Screenshots weren't compositing in this session (same known Browser-pane limitation as earlier) — verified structurally/via pixel data instead, per established fallback practice.

## 2.10.0 — 2026-08-25 19:15: Batch 66/67 — Coin currency + Performance Score, answering last version's open questions

The two items held back from 2.9.0 pending user decisions — both now answered and implemented.

### Coins (Batch 66)
`coinsThisRun` accumulates silently through a run (never shown live, per user spec — "you only see them at the end") and is revealed on the Game Over screen multiplied by the run's score multiplier, same pattern as score itself. Two earn rates per vehicle, both derived from the existing `VEHICLE_POINTS` map so there's only one place vehicle "value" is defined: a clean grounded pass earns `round(points/10)` coins (normal/motorbike/tractor=1, truck/reckless=2, ambulance=5); jumping clean over one (bounding boxes overlap while `abilityState==='jumping'`) earns the FULL point value instead (10/20/20/10/10/50). A new `Vehicle.jumpedOver` flag (set the first frame the jump-immunity branch catches a real overlap) guards against double-counting the same vehicle at both its jump-pass moment and its later off-screen exit. `allTimeStats.totalCoins` is the persistent total; a 🪙 placeholder (plain emoji, no hand-drawn art) stands in until the user's own coin/car icon design is ready — swapping it later is a pure presentation change, no data model impact.

**Coins replace total-score as the Garage's unlock currency** (per user decision — this was the more invasive of the two options offered). `GARAGE_CARS[].unlock` values changed from score-point thresholds to coin costs (old thresholds ÷10, preserving the same relative pacing between cars — a first-pass conversion, flagged in PLAN.md for a real playtest since coin income depends heavily on how much a player jumps vs. just passes). `isCarUnlocked()` now checks `allTimeStats.totalCoins`. The Garage grid's locked-tile label changed from "🔒 {pts} PTS" to "🔒 🪙{cost}".

### Performance Score (Batch 67)
osu!-style weighted decay, per user's own reference and confirmed formula: sort your best runs descending, rank 1 counts in full, each subsequent rank counts for 95% of the previous rank's weight (`score × 0.95^(rank-1)`), summed across your top 100 saved runs. Computed live in `calculatePerformanceScore()` from the `highscores` array rather than stored/kept in sync separately — that array is already sorted-by-score, so there's nothing extra to maintain.

This required raising the leaderboard's own storage cap from top-10 to top-100 (`saveScore()`'s `scores.slice(0, 100)`, was `.slice(0, 10)`) so there's an actual top-100 to draw from — the leaderboard screen itself also now shows up to 100 entries instead of 10 as a direct consequence (it already rendered whatever was in storage with no separate display cap, so this needed no UI code change, just relies on normal page scroll for the longer list). Shown in the Stats tab's SCORING card as "PERFORMANCE SCORE", alongside a new "🪙 COINS" row for the new currency.

**Verification**: live-tested in the Browser pane — `recordRunStats()` correctly computes `coinsThisRun × multiplier` and persists it to `totalCoins`; a simulated grounded pass + jump-over pair produced exactly the expected 1+20=21 coins; `endRun()` correctly displayed 21 on the Game Over screen and persisted it; the Garage grid correctly unlocked Stock/Hot Hatch/Rally and kept Drift+ locked at a simulated 400 coins; `calculatePerformanceScore()` against 3 seeded scores (1000/800/600) matched the hand-computed weighted sum (2302) exactly.

## 2.9.0 — 2026-08-25 18:30: Batch 65 — NPC fairness/difficulty fixes, new scoring, Garage/Stats redesign

Seven changes from one large user request, batched and implemented in order without stopping for confirmation between them (per explicit user instruction). Two related items from the same request — a coin/currency system and a "Performance Score" top-100-ranks system — are intentionally NOT included here; both are genuinely underspecified (coin art not yet provided, PP-style formula not yet confirmed) and are pending a follow-up answer from the user rather than guessed at.

### NPC traffic: one lane per maneuver, always
Reckless drivers had a rare (5%) chance to dive two lanes in a single maneuver — removed entirely per user feedback ("hard to predict"). Every lane-change is now always exactly one lane, for every type.

### NPC traffic: fixed "cars speed up with you" — the game now actually gets harder at speed
Root cause: each vehicle's `speedOffset` (how fast it moves relative to the player) was clamped at spawn to `[currentSpeed*0.75, currentSpeed*1.5]` — using the LIVE, still-ramping `currentSpeed`, not a fixed reference. Since most on-screen traffic at any moment was spawned recently, this meant late-run vehicles kept getting their speed rescaled to match whatever the player's speed had ramped to by then, so the relative closing-speed gap stayed a roughly constant fraction of `currentSpeed` all run instead of genuinely widening. Changed the clamp to bound against the constant `baseSpeed` instead — identical behavior at the very start of a run (`currentSpeed === baseSpeed` then), but now the gap between the player's rising speed and traffic's fixed-band speed actually grows as a run goes on. Ambulances are unaffected (their overtake speed is deliberately `currentSpeed`-proportional by design, not implicated in this bug).

### New point values (multiples of 10, per user spec)
`VEHICLE_POINTS = { normal: 10, reckless: 20, truck: 20, motorbike: 10, tractor: 10, ambulance: 50 }`, replacing the old flat 10-for-anything dodge score. Confirmed in passing: the multiplier already applied live to the HUD score in real time (`score += Math.round(pts * multiplier)` on every dodge, not just at run end) — no change needed there, just carried the same pattern into the new per-type values.

### Control Type: strict 3-way choice (was a 2-way keys/buttons toggle that conflated Arrows and WASD)
`controlTypeSetting` is now Arrow Keys / WASD / Steering Buttons — exactly one active at a time. Previously "Arrows / WASD" was a single option that accepted both simultaneously; now picking WASD makes the Arrow keys fully inert and vice versa, addressing the user's keyboard-rollover concern. Also re-verified (and reconfirmed working) that W/S drive vertical accel/brake, first fixed last version (2.8.1).

### Ambulance warning redesign
Removed `#hudAmb`, the small DOM corner badge ("! AMBULANCE !") the user couldn't read at its size. In its place, the existing flashing red pre-warning lane stripe now carries a large sideways white "AMBULANCE" (`ctx.rotate(Math.PI/2)`, Silkscreen bold 11px) drawn directly on the canvas, flashing in sync with the stripe since it's in the same conditional block.

### Stats tab redesign (per user-provided mockup)
Three stacked boxes → a 2x2 `.stat-card` grid (SCORING / DRIVING / TIME ON THE ROAD / WRECKED BY). WRECKED BY is no longer a plain text list — it's a `fig-grid` of rotated vehicle-sprite figures (reusing the game's own `VEHICLE_BODIES` draw functions, extended from the mockup's original 4 types to all 6 real death types: normal/reckless/truck/motorbike/tractor/ambulance) with count+percentage captions, consistent zero-state styling. Also fixed the "AVG (LAST 50)" readability complaint: stat VALUES (`.stat-row span:last-child`, used by Stats/Game-Over/Pause alike) now render in Pixelify Sans instead of Silkscreen — Silkscreen's digits were hard to tell apart at 10px; labels stay Silkscreen.

### Garage redesign (per user-provided mockup + follow-up spec)
Two changes: (1) the top preview became a "showroom" — a bordered stage box beside an info panel showing the equipped model's name, an EQUIPPED tag, and the paint swatches (moved here from their own separate section, per the mockup). (2) The car list — previously `flex-direction:column` stacked full-width rows — is now a wrapping `grid-template-columns: repeat(auto-fill, minmax(68px,1fr))` grid of square cards, each showing an actual small sprite of that car (not just its name), per the user's explicit follow-up ("not lines... a grid of cards"). Locked/unlocked/equipped states and the underlying unlock-by-score logic are unchanged from Batch 64 — this was a pure layout/visual pass.

**Verification**: live-tested in the Browser pane for every item except the ambulance sideways text, which the pane's screenshot/rAF compositing wasn't working for in this session (a known, previously-documented environment limitation, not a code issue) — confirmed correct instead by directly replicating the exact draw call against the live canvas and reading back the resulting pixels, which matched expectations exactly.

## 2.8.1 — 2026-08-25 17:05: Fix — W/S never actually controlled acceleration/braking

User reported W and S weren't working for "WSAD steering." Turned out vertical accel/brake (`vKeys.up`/`vKeys.down`) was always keyed off `ArrowUp`/`ArrowDown` only — `A`/`D` were wired for lane-changing (alongside Arrow Left/Right) but `W`/`S` had never actually been wired to anything, despite every "Control Type" label in this game calling the keyboard scheme "Arrows / WASD". Added `w`/`W`/`s`/`S` alongside `ArrowUp`/`ArrowDown` in both the `keydown` and `keyup` handlers. Verified live: dispatching a `w` keydown sets `vKeys.up`, holding `s` for real frames (game loop running, tab fronted) accelerated the car downward until it hit `PLAYER_MAX_Y`, matching the existing Up/Down behavior exactly.

## 2.8.0 — 2026-08-25 16:40: Steering buttons redesign + Control Type selector

Three related changes to the on-screen steering-buttons feature (Batch 50), all from the same user request.

### Framed strip + sliding button indicator
`.steering-track` previously had only a `border-top` and relied on the active `.lane-zone` flatly recoloring itself — looked like a plain colored strip, not a control. It now has a full `border` + its own panel background (`var(--c-panel)`), each lane zone is styled as its own bordered/rounded slot, and a separate `.steering-indicator` element — styled like the game's existing `.btn` (bordered, hard drop-shadow) in `--c-mint` — slides (`transition: left/width`) to the active lane's real `offsetLeft`/`offsetWidth` (read from the DOM, not a % guess, so it stays correct regardless of the track's own padding/gap). The old `.lane-zone.active` recolor is gone — the indicator alone now shows state.

### Steering Button Input: Hold & Drag vs Move to Steer
New setting (`steeringButtonModeSetting` → `config.steeringButtonHoverMode`). Hold & Drag is the original behavior (press, then drag). Move to Steer adds a dedicated `mousemove` listener directly on the track (separate from the existing window-level one used for hold-drag) that calls `steeringTrackGoTo()` on any hover, no mouse button needed. Touch is unchanged either way — a touchscreen has no hover state, so it always works by holding a finger down and dragging, same as before.

### Control Type replaces the Steering Buttons on/off toggle
"Steering Buttons: Off/On" was additive — keyboard lane-changing (Arrow/A/D) always worked regardless. Replaced with `controlTypeSetting`: **Arrows / WASD** or **Steering Buttons**, mutually exclusive. When Steering Buttons is selected, the `ArrowLeft/Right`/`A`/`D` handlers in both `keydown` and `keyup` are skipped entirely (`ArrowUp`/`Down` for accel/brake are untouched — those aren't a steering input). The `keyup` guard matters as much as the `keydown` one: without it, a stray arrow-key release while Steering Buttons was active would still fire `snapToNearestLane()` off stale/unset `pressStartLane` state and yank the car sideways.

### Follow-up fix: click/hover zone detection now matches the visible button exactly
Caught immediately by the user looking at the redesign: `steeringTrackGoTo()` still computed the target lane as `floor((clientX - trackRect.left) / trackRect.width * lanes)` — a fraction of the whole track's rect. Once the track gained padding/gaps for the framed look, that no longer lines up with where the buttons are actually drawn, worst at the two edges — flicking to what looks like the last button could land the car one lane short. Rewrote it to walk the real `steeringZoneEls[i].getBoundingClientRect()` of each zone and pick whichever one the pointer's `clientX` actually falls under, so the clickable/hoverable area is always pixel-exact with the visible button, regardless of any padding/gap tuning later.

**Verification**: live-tested in the Browser pane — clicking a lane zone moves `targetX` correctly; Steering Buttons control type makes `ArrowRight` a no-op (`targetX` unchanged) with the track framed and visible; Arrows/WASD control type hides the track and `ArrowRight` moves `targetX` normally; hover mode moves the car on an un-pressed `mousemove` over the track, hold-drag mode ignores the same event; clicking 1px inside the last/first zone's own edge and clicking mid-zone all resolved to exactly that zone's lane center, confirmed against `laneCenterX()`. Not yet tested with an actual physical mouse drag/hover or a real touchscreen — see PLAN.md's Batch 45 follow-up.

## 2.7.0 — 2026-08-25 15:50: Batch 64 — Garage: 10 player cars + unlock system

Second half of the vehicle-fleet work — the actual Garage shop, replacing the Batch 60 "STOCK — more coming soon" placeholder. 10 selectable player car bodies (Stock, Hot Hatch, Rally, Drift, Offroad, Muscle, Classic, Supercar, Hypercar, Formula), each drawn in the player's own chosen color (model and color are independent choices, same as the design doc's own framing) — added a `GARAGE_CARS` registry (key/label/native height/draw fn/unlock threshold).

### Unlock system
No currency/economy exists in this game, so unlocking is progression-based: each car needs a cumulative `allTimeStats.totalScore` (Batch 61's data) to unlock, from 1,500 (Hot Hatch) up to 42,000 (Formula) — a natural "keep playing, unlock more" curve using a stat the player already earns just by playing, rather than inventing a whole new spendable-currency system for a "for now" groundwork batch. Garage now shows all 10 as a grid: equipped (mint border), unlocked-and-selectable (click to equip), or locked (dimmed, shows the exact score needed, not clickable). Selection persists to `localStorage` (`selectedCarKey`).

### Collision boxes stay fixed regardless of car choice
Per the design doc's own explicit framing — "traffic collision boxes stay identical whichever you drive" — `Player.height` stays `PLAYER_HEIGHT` no matter which car is equipped; only the drawn sprite's own native proportions vary (a Hot Hatch draws visually shorter than a Formula car, by design), so no car is a hidden gameplay advantage/disadvantage. The Garage preview canvas resizes to each car's own aspect ratio for an accurate preview, independent of the fixed in-game hitbox.

### STOCK keeps the original sprite exactly
`drawPixelCar` (the actual current player sprite, including jump-wings) is still used verbatim when STOCK is equipped — zero visual change for anyone who never opens the Garage. The other 9 cars use plain body draws with no jump-wings art (the ability itself works identically on every car; only the airborne visual flourish is stock-only, to avoid retrofitting wing art onto 9 more sprites for a "for now" batch).

### Verification
Live-tested via the Browser pane: confirmed the default state shows only STOCK unlocked+equipped, all 9 others locked with their correct threshold text; simulated reaching 5,000 total score and confirmed Hot Hatch/Rally correctly became selectable while higher-tier cars stayed locked; clicked Hot Hatch and confirmed the selection, equipped/select label swap, and localStorage persistence all update correctly; confirmed clicking a still-locked car (Formula) does nothing (no click handler attached); confirmed the preview canvas resizes and repaints correctly for the new car; confirmed real gameplay renders the selected non-stock car correctly and that activating the jump ability while a non-stock car is equipped throws no error (the extra wings-related arguments are simply unused, not a crash); switched back to Stock and confirmed it's pixel-identical to the pre-Garage player sprite; ran 200 frames with zero errors. Zero console errors throughout.

---

## 2.6.0 — 2026-08-25 15:10: Batch 63 — Traffic vehicle fleet expansion

First half of the vehicle-fleet work (`reckles vechicles_new/Reckless Vehicles.dc.html`). Replaces the old 3-sprite traffic system (one generic car shape, one truck, one ambulance) with a fleet of 14 distinct bodies, layered onto the existing 4 behavioral types rather than replacing them — `type` (normal/truck/reckless/ambulance, plus 2 new ones) still drives speed/lane-change behavior exactly as before; a new `body` field picks which sprite gets drawn, sized from its own native dimensions in a new `VEHICLE_BODIES` registry instead of a flat per-type height constant.

### New bodies
Sedan, hatchback, coupe, pickup, van, taxi, police (cars); bus, semi, tanker, flatbed, box truck (trucks); motorbike, tractor (special). The semi is a genuine fix, not just new art — the old truck sprite drew the trailer at the top and the cab at the bottom, which read as driving backwards next to every car (windshield/headlights always at the top); the new one is cab-forward with the trailer trailing behind, a coupling gap, mirrors on the cab, and a proper tail. Ambulance keeps its existing dedicated sprite untouched, per the design doc's own note.

### Spawn integration
- `type:'truck'` picks a body weighted toward the common utility ones (box 40%, bus 20%, semi 15%, tanker 15%, flatbed 10%).
- `type:'reckless'` only picks sportier bodies (sedan/hatch/coupe) — a weaving reckless driver in a van didn't read right.
- `type:'normal'` picks from the everyday car bodies, with an 8% chance to become a taxi or police car — but ONLY while the road is actually in the city biome (`biomeAt(-roadOffset)`), so they read as city dressing rather than appearing everywhere.
- Two new standalone types: `motorbike` (narrow hitbox — `Math.round(6×CAR_SCALE)` instead of the usual 18px — fast, frequent lane changes, 5% of spawns) and `tractor` (near-zero relative speed so it feels like a slow-moving obstacle you rapidly close in on, never changes lanes, farm-biome-gated — the spawn roll's tractor band silently falls through to normal traffic outside the farm biome rather than re-rolling).
- `canSpawnAt()`'s vertical-clearance check now reads each vehicle's own `v.height` instead of a flat per-type constant, since a bus and a hatchback are no longer the same size.
- Removed `drawPixelTruck` (the old backwards-reading sprite) and the now-unused `TRUCK_HEIGHT` constant as dead code.

### Verification
Live-tested via the Browser pane: force-constructed and drew 40 instances of every type (240 total) with zero errors, confirming every body variant renders; confirmed taxi/police only appear when a forced `roadOffset` places the biome check in 'city' (13/200 and 4/200 in a city-biome sample, zero in earlier non-gated samples); confirmed every body's computed height matches its registry entry × `CAR_SCALE` exactly; confirmed the tractor spawn-roll band produces tractors 100% of the time when forced into the farm biome and 0% of the time otherwise (controlled roll-value test, not just observation); ran 3000 frames of real gameplay (with an actual crash partway through) and confirmed a healthy mix of body types appeared, the canvas stayed fully painted throughout, and the resulting `deathsByType` stat correctly recorded the killing vehicle's behavioral `type` — confirming Batch 61's stats system and this batch's new vehicle system integrate cleanly. Zero console errors throughout.

---

## 2.5.0 — 2026-08-25 14:00: Batch 62 — Stats tab UI

Final batch of the Stats-tab request — the actual screen, built on Batch 61's data layer. Added a STATS button to the main menu (now a 2-button row alongside GARAGE, below SETUP/SCORES). New `#statsView`, styled identically to the other panel screens (`.settings-panel`, reusing the existing `.stat-box`/`.stat-row` styling from the pause/run-summary screens rather than introducing new CSS).

Shows: runs played, total score, average score, average score over the last 50 runs, best score (pulled from the existing leaderboard's top entry), vehicles passed (total and best-single-run), jumps, lane switches, pickups collected, total play time, longest single-run survival time, highest multiplier reached, and a "Deaths By Vehicle" breakdown (one row per vehicle type, sorted by count descending, with a percentage of total deaths) — a plain-object-keyed breakdown, so new vehicle types from the upcoming fleet expansion will show up automatically with an upper-cased fallback label, no code change needed. An empty state ("No runs yet") shows before the player's first run.

### Verification
Live-tested via the Browser pane: seeded synthetic stats and confirmed every displayed number computes correctly (average score, average-last-50, formatted play time and longest survival via the existing `formatTime()`, death percentages summing correctly and sorted by count); confirmed the empty-state message shows correctly with zero runs; then ran one real end-to-end flow through the actual game (dodge a vehicle, get hit by another) and confirmed the Stats screen reflects the real run afterward (`runsPlayed: 1`, `dodged: 1`, "NORMAL CARS 1 (100%)"), not just manually-seeded data. Zero console errors throughout.

---

## 2.4.1 — 2026-08-25 13:35: Batch 61 — Stats tracking (data layer, no UI yet)

Second of the Stats-tab batches — persistent all-time stat tracking, no visible screen yet (that's Batch 62). New `allTimeStats` object (merged over defaults from `localStorage` on load, so future new fields still get sane defaults for existing players) tracks: `runsPlayed`, `totalScore`, `totalDodged`, `totalJumps`, `totalLaneSwitches`, `totalGameTimeMs`, `totalPickups` (wired now, stays 0 until road pickups exist), `deathsByType` (a plain object keyed by vehicle type — `normal`/`truck`/`reckless`/`ambulance` today, new types from the upcoming vehicle-fleet expansion slot in with zero Stats-side changes), `recentScores` (rolling last-50, for "average of last 50"), plus three extras beyond the original ask: `longestSurvivalMs`, `highestMultiplier`, `mostDodgedInRun`. Updated once per completed run, from the same point `saveScore()` already runs.

Needed one genuinely new piece of tracking: **lane switches weren't counted anywhere before this**. Added `Player.currentLane` (the rounded lane index, initialized at spawn) and a check at the end of `Player.update()` — whenever it changes from the previous frame, `laneSwitchesThisRun` increments. This counts actual completed lane changes regardless of input method (keys, steering buttons, touch, tilt), not raw key presses — a press that hits the road edge and doesn't actually move the car correctly does NOT count.

Also needed `endRun()`/`saveScore()` to know WHAT killed the player, to feed `deathsByType` — both now take an optional `vehicleType` parameter, passed from the two collision branches that call `endRun()` (`v.type`).

### Verification
Live-tested via a full simulated run: 3 lane-change key presses (one of which hit the road edge and correctly did NOT count) → 2 registered switches; forced 2 vehicle despawns → `dodgedCount`/`totalDodged` both 2; forced 1 jump → `totalJumps` 1; forced a fatal collision with a `reckless`-type vehicle → `deathsByType.reckless` correctly incremented to 1, confirming the vehicle-type plumbing through `endRun(v.type)` works. Confirmed `allTimeStats` (runsPlayed, totalScore, totalDodged, totalJumps, totalLaneSwitches, deathsByType, recentScores, mostDodgedInRun, highestMultiplier — all matching the run's actual numbers) persists correctly across a full page reload. Zero console errors.

---

## 2.4.0 — 2026-08-25 13:10: Batch 60 — Garage tab (button + groundwork)

First of several batches from a new user request (Stats tab, Garage tab, plus a heads-up that a much bigger vehicle-fleet expansion design is coming — see `PLAN.md`'s Batch 60-63+ entries for the full breakdown). This batch is deliberately scoped small per the user's own framing ("for now just make the button and maybe some ground work").

- Added a GARAGE button to the main menu, below the SETUP/SCORES row.
- New `#garageView`, styled identically to Setup/Leaderboard (`.settings-panel`).
- Relocated the car-color swatch picker from Setup into Garage — it belongs there thematically now that Garage is "where the player customizes their car," and Setup is left as pure gameplay settings.
- Added a live car preview canvas in Garage that renders the actual player sprite (via the existing `drawScaledVehicle`/`drawPixelCar`, not just a flat color square) in the currently-selected color, redrawing immediately when a swatch is clicked.
- Added a placeholder "Car Model" section (a single STOCK tile, marked equipped) with a "more cars coming soon" note — groundwork for the future car-unlock system, no real model-switching or purchase logic yet (that's a separate, larger batch once the new vehicle designs are scoped).
- Removed the "SPEED: ACCELERATING" row from the main menu's CURRENT SETUP summary card, per direct user feedback — it's no longer a real setting (speed mode was hardcoded since Batch 38) and reads as misleading, implying a choice that doesn't exist.

### Verification
Live-tested: Garage view opens/closes correctly from the menu, the preview canvas paints the sprite (554 non-transparent pixels), clicking a swatch updates `playerColor` and immediately re-renders the preview with the new color (confirmed by sampling for the expected red pixel value after clicking the red swatch), and the SPEED row is confirmed absent from the summary card's HTML. Zero console errors.

---

## 2.3.1 — 2026-08-25 12:45: Batch 59 — Biomes made 10x longer

User feedback: biomes cycled by too fast. Since every `BIOMES` segment's slot count was multiplied by the same factor (10x), the whole 1920px cycle scales uniformly — every other hardcoded position in the system (bridge Y positions, the hand-placed sign/chevron/wreck Y positions in `makeStrip()`'s `set` arrays) is exactly 10x its old value too, not independently re-tuned; prop *density* within each biome is unchanged (more slots at the same per-slot odds, not stretched/distorted art). `BIOME_CYCLE` 1920→19200, meadow 14→140 slots, forest 18→180, farm 12→120, suburb 14→140, city 16→160, meadow-loop-out 6→60 (still sums to 800×24=19200). `ROAD_OFFSET_WRAP` recomputed from 40320 to 403200 (`LCM(576, 19200, 28, 16)`) — same reasoning as Batch 58, this constant has to be recomputed any time a periodic sub-pattern's period changes, or the Batch 55/56 stutter bug comes back.

### Verification
Confirmed `BIOMES` still sums to exactly 800 slots (=19200px=`BIOME_CYCLE`) and `ROAD_OFFSET_WRAP` divides evenly by all 4 periods (576/19200/28/16). Re-ran the dash-phase continuity check across the full new 403200-unit wrap (80,640 steps) with zero discontinuities. Measured actual biome duration in a live simulated run: 1694 frames (~28s at 60fps) spent in the meadow biome before crossing into forest — matches the expected ~10x increase from the original ~2-3s. Confirmed a bridge still renders correctly (fully painted, 19 distinct colors) at its new, proportionally-scaled position.

---

## 2.3.0 — 2026-08-25 12:20: Batch 58 — Biome loop (roadside scenery overhaul)

Implemented from a second design mockup the user shared (`Car Crash Game UI Design2/Reckless Driving UI.dc.html`, sections labeled "2a/2b/2c" — the "1a-1g" sections from the first mockup were already implemented in Batch 53). Replaces the old fixed 24-slot/576px verge cycle (a single, roughly-random scattering of grass/bush/tree/one landmark) with a 1920px/80-slot cycle that runs through 5 named biomes in sequence — meadow → forest → farmland → suburbs → city → a short meadow "loop-out" that closes the cycle invisibly — each with its own ground colors, density and prop table, plus two bridge overpasses and a handful of fixed-position hazard signs/wrecks. Asphalt (the grey road surface itself) is untouched — it stays on its existing 576px cycle, matching the design doc's own separation between "the road" and "the biome loop."

### New prop sprites
14 new roadside sprites, each in the same 14×24-slot format as the existing ones: conifer, hedge, hay bale, barn, tower (city high-rise, 3 window-lit color variants), streetlamp, billboard, warning sign, chevron, deer, cow, wreck, mailbox, fence run.

### Biome ground and props
`makeStrip(side)` builds an 18×1920px buffer per side: a ground pass (per-biome base/dark/light grain, plus biome-specific texture — plow rows in farmland, expansion-joint lines in the city, scattered leaf-litter specks in the forest), a dithered blend into the previous biome's color over the first slot of each new segment (so transitions read as gradual, not a hard seam), a shoulder/dirt strip next to the curb (tinted per biome, sharper-edged for city/suburb than the natural biomes), and a prop-placement pass with a genuinely different table and density per biome (meadow: trees/bushes/cows/rocks/fences; forest: denser conifers/trees/rocks/deer; farmland: barns/hay/fences; suburbs: houses/hedges/lamps/mailboxes; city: lamps/billboards/towers placed via a variable-spacing walk rather than fixed slots). A handful of warning signs, chevrons, and one wreck are hand-placed at fixed positions in the cycle (different per side) rather than randomly rolled, so they land somewhere meaningful — before the forest, at the city approach, etc.

### Bridges
Two overpasses per cycle (one in the forest, one in the city). The deck is drawn as a separate pass, called from the game loop *after* traffic and the player are drawn, so vehicles genuinely disappear underneath for the ~0.5s it takes to cross — a cast shadow band on the road tells you it's coming. This is purely visual occlusion; collision detection is unaffected (a car hidden under the deck can still be hit), which seemed like the right tradeoff given the design doc frames it as a cosmetic effect, not a new gameplay mechanic. Bridges also block tall/blocking props from spawning near their approach (`nearBridge()`) so nothing overlaps the deck. Adapted from the design's fixed-160px-canvas version to scale with the game's actual per-lane-count canvas width (pillars stay a fixed 6px from each outer edge regardless of width; city light accents scale proportionally).

### Shared between menu and gameplay
The verge strip doesn't depend on lane count at all (unlike asphalt, which does), so it's built once, lazily, and shared between the main menu's decorative background and the real game canvas — the menu now shows the same cycling biomes. Only the asphalt buffer is still built separately per context (menu: fixed 4-lane; game: the player's actual lane count), same as before.

### `roadOffset` wrap raised to 40320
Was 4032 (`LCM(576 asphalt, 28 dash, 16 curb)`). Since the verge now cycles on a *different* period (1920) than the asphalt (576), and 1920 isn't a multiple of 576, the wrap constant had to become `LCM(576, 1920, 28, 16) = 40320` to keep every periodic sub-pattern in sync — getting this wrong would have reintroduced the exact dash-phase stutter fixed in Batch 55/56.

### Removed
`makeVerge53()`, `VERGE_SLOTS_L`/`VERGE_SLOTS_R`, and the two sprite functions only that old system used (`sprFence53`, `sprSign53` — the biome system uses different, purpose-built `sprFenceRun53`/`sprWarn53`/`sprChevron53` instead) — all dead code once the biome system replaced them.

### Verification
Live-tested via the Browser pane: confirmed the menu and a 7-lane game session both render fully painted (99.8%+ non-transparent pixels) with zero console errors; sampled the actual verge buffer's ground colors well inside each of the 5 biome segments and confirmed each one's own base color dominates its region (0.24-0.8 match fraction — lower in farmland/city because of dense plow-row lines and towers/lamps, which is expected, not a bug); ran 2000 simulated frames (2.15 full biome cycles, crossing both bridges multiple times) with the canvas staying fully painted throughout and zero errors; re-ran the Batch 55/56 dash-phase continuity check against the new 40320 wrap value across a full cycle (13,450 steps) with zero discontinuities, confirming the stutter fix wasn't reintroduced; directly rendered a bridge into view and confirmed it paints a fully-covered, multi-colored deck (18 distinct colors: grain, pillars, accent lights) rather than a blank/broken region.

---

## 2.2.0 — 2026-08-25 11:35: Batch 57 — Distance-based ambulance siren

Added a synthesized siren sound (Web Audio, no external audio assets — consistent with the rest of the sound system) tied to each ambulance's live distance from the player: silent when it's far off, swells as it closes in, peaks right as it draws level with the player, then fades back out as it pulls away — the classic passing-emergency-vehicle effect, per direct user request.

### Implementation
- `startSiren()` builds a continuous sawtooth oscillator with a sine LFO wobbling its pitch (~1.15Hz, ±180Hz around a 750Hz center — a "nee-naw" wail) through a per-siren `GainNode` starting silent; called once per ambulance `Vehicle` at construction (`this.siren`), tracked in a module-level `activeSirens` list.
- `updateSirenVolume(siren, dist)` — called every frame in the main loop for each on-screen ambulance, using `Math.abs(ambulance center Y - player center Y)` as the distance — computes `vol = 0.35 * config.soundVolume * clamp(1 - dist/AMBULANCE_SIREN_RANGE, 0, 1)²` (squared falloff: quiet and barely-there far away, ramps up sharply once close) and eases the gain toward it (`setTargetAtTime`, ~80ms time constant) so it swells/fades smoothly rather than stepping. `AMBULANCE_SIREN_RANGE = CANVAS_HEIGHT * 0.75` (195px) — outside that distance the siren is fully silent.
- `stopSiren(siren)` fades the gain out and stops the oscillators ~0.4s later (avoids an audible click from a hard stop), removing it from `activeSirens`. Called from the natural despawn path (ambulance exits off the top) and, as a safety net, from `endRun()` (covers the ambulance-collision case, where the crashing vehicle itself is never spliced from `vehicles`, plus any *other* ambulance that happens to be active in a different lane), `exitToMenu()`, and the start of `launchGame()`.

### Verification
Reset a stale `soundVolume: "0"` left in localStorage from earlier test sessions (was silently making every sound effect no-op, unrelated to this feature) before testing. Confirmed the actual volume curve by intercepting `AudioParam.setTargetAtTime` across a simulated approach-pass-departure distance sweep (400→0→400px): silent at and beyond 195px, rising smoothly through 0.013→0.058→0.135→0.2205 to a peak of exactly 0.245 (`=0.35×0.7`) at distance 0, then symmetric back down — matches the requested "louder as it approaches, loudest when passing, quieter as it leaves" exactly. Confirmed the full lifecycle via forced-RNG live tests: siren is present in `activeSirens` immediately on spawn, and gone from it both after a natural despawn (ambulance crosses and exits off-screen) and after a crash caused by a *different* vehicle while the ambulance was still active (exercising the `endRun()` safety net specifically, not just the despawn path) — zero console errors throughout.

---

## 2.1.2 — 2026-08-25 11:05: Batch 56 — Verge/asphalt scrolled backwards

User reported the green verge and grey asphalt were scrolling in the *opposite* direction from the white lane dashes (dashes were correct). Confirmed by deriving the canvas-position formula for a fixed buffer row vs. a fixed dash: the buffer blit used `y = -o + k*VERGE_PERIOD` (canvas position of a given buffer row *decreases* as `offset` grows → scrolls up), while the dashes and curbs both use `+offset`-derived phases (canvas position *increases* as `offset` grows → scrolls down) — an exact sign mismatch between the two halves of the same `drawRoadScene()` function, left over from the Batch 53 rewrite. Fixed by flipping the buffer blit to `y = o + k*VERGE_PERIOD`, matching the dashes'/curbs' direction. Verified algebraically (a fixed buffer row and a fixed dash now both shift by the same +10 canvas-y per +10 offset) and confirmed directly against the live source (`drawRoadScene.toString()` now contains `o + k * VERGE_PERIOD`, not `-o + ...`), plus a full canvas-paint check on both the menu and an active game session with zero console errors.

---

## 2.1.1 — 2026-08-25 10:40: Batch 55 — Menu road stutter fix, demo car centering

### Fixed a real, structural stutter bug in the scrolling road (affects both menu and gameplay)
User reported the menu's road "stutters like every 4-5 seconds." Root cause: `drawRoadScene()` reduces its scroll offset to `o = offset % 576` (`VERGE_PERIOD`, needed for the buffer-tiling math), then derived the lane-dash and curb phase from `o % 28`/`o % 16` — but 576 is not a multiple of 28 (576/28 ≈ 20.57), so every time `o` wrapped (every 576px of scroll), the dash pattern's vertical phase jumped ~14-16px in a single frame. This happened regardless of the outer `roadOffset` variable's own wrap point (4032, chosen specifically as a common multiple of 576/28/16) — that wrap didn't help because `drawRoadScene` re-derives `o` via its own `% 576` on every call, independent of the caller. Confirmed by direct calculation: crossing the 576 boundary, the old dash-phase formula jumped from 15 to 1 (a discontinuous -14), the fix's formula goes from 15 to 17 (a normal, continuous +2 matching one frame's actual movement). Fixed by deriving the dash and curb phase from the raw, unreduced `offset` parameter instead of the buffer-tiling-only `o` — verified via a 3000-frame simulation crossing multiple 576-boundaries (and the full 4032 wrap) with zero discontinuities. This bug affected the real game canvas too, not just the menu, and got *more* frequent as `currentSpeed` rose through a run (as often as ~every 1.6s near max speed) — just less noticeable there since gameplay draws attention elsewhere.

### Fixed decorative menu cars not being centered in their lanes
The main menu's 3 decorative background cars used hand-picked x-coordinates (60, 29, 91) that didn't actually match the menu road's real lane centers (24.5, 55.5, 86.5, 117.5 for lanes 0-3) — each was off by exactly 4.5px. Replaced with `MENU_LANE_X[]`, computed directly from the menu's fixed road geometry (same values `drawMenuScene()` already passes to `drawRoadScene()`) rather than eyeballed. Also widened the cars' vertical wrap range from `[-40, 260)` to `[-40, 300)` so a car fully clears the bottom edge before teleporting back to the top, instead of still being a visible sliver at the moment it wrapped.

### Hardened `makeAsphalt53()` against a latent lane-count mismatch
It read the mutable global `config.lanes` internally instead of taking lane count as a parameter — harmless today since the menu's demo buffer happens to build on first page load, before `config.lanes` could differ from its default of 4, but fragile: if the player changed lanes in Setup before the menu's buffer first built, the baked-in asphalt wear/seam pattern would silently mismatch the menu's hardcoded 4-lane dash drawing. Now takes `lanes` explicitly at both call sites (game: `config.lanes`; menu: hardcoded `4`, matching its fixed demo road).

### Verification
Live-tested via the Browser pane: directly computed the dash-phase discontinuity for both the old and new formula across a 576-boundary crossing to confirm the fix (old: -14 jump, new: +2 normal delta); ran a 3000-frame simulation of the phase computation across multiple wrap boundaries with zero jumps larger than a normal per-frame delta; confirmed `MENU_LANE_X` computes to the exact expected lane-center values; ran the menu scene and an active game session for hundreds of frames each with full canvas-paint checks and zero console errors.

---

## 2.1.0 — 2026-08-25 09:55: Batch 54 — Post-redesign fixes and tuning

Follow-up round after Batch 53's UI/art redesign, based on direct user feedback plus one real bug found while investigating a feature request.

### Ambulance bug fix: it wasn't spawning at all
User reported the ambulance never spawns. Root cause: Batch 52 made ambulances spawn below the visible canvas (`y = canvas.height + 10`) and travel upward, but the despawn/score check (`v.y > canvas.height || v.y < -v.height - 20`) still applied the "off the bottom" half of that condition to every vehicle type, including ambulances — since an ambulance's spawn `y` is already past that threshold, it satisfied the despawn condition on the very first frame it existed and got silently removed (with score/dodge credit) before ever being drawn on-screen. Confirmed via a forced-RNG live test: before the fix, a queued ambulance's countdown completed but `vehicles` stayed empty; after the fix, the ambulance persists, visibly crosses the screen, and properly despawns off the *top* once it's actually exited. Fix: despawn direction is now type-aware — ambulances only despawn off the top, everything else only off the bottom.

### Ambulance slowed to 0.75x its overtake speed
Per direct request. Its relative speed (how fast it visually closes in on/passes the player) was `2.0-2.5×currentSpeed`; now `1.5-1.875×currentSpeed`.

### Car sprite reverted to the original pixel art
Batch 53 restyled `drawPixelCar` (used for the player and normal/reckless NPCs, not trucks/ambulances) to match the UI design doc's shading and made it direction-aware. User asked to go back to the original sprite — reverted verbatim to the pre-Batch-53 version (recovered from `Car Crash Game UI Design/uploads/Car Crash/carCrash.html`, a stale uploaded copy of the game from before that redesign), including dropping the now-unused `dir` parameter and the `Vehicle.dir`/`'up'`-argument plumbing Batch 53 added to support it. Road, HUD, menu, and every other Batch 53 visual change are unaffected — this reverted only the car sprite.

### Energy bar relocated to top-left, next to the pause button
Was a full-width bar across the bottom of the screen (with a small "JUMP"/state label row above it). Now sits directly to the right of the pause button in a new `#hudLeft` row, height matched exactly to the pause button's height with the bar's aspect ratio (140:16) preserved — so it comes out narrower rather than stretched. The separate label row is gone entirely (was showing "JUMP" + a READY/percentage/IN USE state that's now redundant with the bar's own visual states — hazard stripes while draining, marching border when full). The underlying energy/hold-to-fly mechanics are unaffected; this is drawing/layout only.

### Top-right HUD and pause button sized up ~1.5x
Score/multiplier/speed chips and the pause button were all reported as too small — every relevant font-size and padding scaled up ~1.5x (pause button 26px → 39px square, matching the energy bar's new height).

### Leaderboard: button sizing, overflow, and a themed confirm dialog
- BACK and CLEAR were both full-width flex buttons before; CLEAR (destructive) is now a small fixed-width (58px) button and BACK (safe, routine) is the full-width one — matches the convention used elsewhere (RESUME is prominent, QUIT is not).
- Fixed a horizontal scrollbar on the leaderboard/setup panels: `.settings-panel` was missing `overflow-x: hidden` (only had `overflow-y: auto`), and per a CSS quirk, setting one overflow axis to `auto` while leaving the other at its default `visible` silently forces *both* axes to `auto` — so anything even slightly too wide triggered a horizontal scrollbar. Also added `min-width: 0` to `.btn-row .btn` so long button labels can't force a row wider than its container.
- CLEAR now opens a themed confirmation dialog (`#confirmOverlay`/`#confirmBox`, styled like the rest of the game's panels — dark background, red accent border, Silkscreen title) instead of deleting immediately — Cancel or clicking outside the dialog backs out with no changes, Clear proceeds.

### Verification
Live-tested via the Browser pane (canvas/DOM inspection, same approach as Batch 53 — screenshots still weren't compositing in this session): confirmed pause button/energy bar/HUD chip computed sizes match the new 1.5x targets exactly; confirmed the reverted `drawPixelCar` now takes 6 params (was 7) and renders the old sprite's exact colors (`#ffeaa7` headlights, `#ff4757` taillights); confirmed a forced-RNG ambulance spawn now survives past its first frame, travels up through the visible canvas, and despawns off the top with correct score/dodge credit, with its relative speed measured at ~1.87x `currentSpeed` (within the new 1.5-1.875x target, was 2.0-2.5x); confirmed the leaderboard's BACK button is now ~473px (full width) vs CLEAR's fixed 58px, with zero scrollWidth/clientWidth overflow; confirmed the confirm modal blocks deletion until explicitly confirmed (Cancel leaves scores untouched, Confirm clears them) via a full click-through simulation; ran a complete menu→setup→back→start→pause→resume→collision→game-over→menu flow with zero console errors throughout.

---

## 2.0.0 — 2026-08-25 08:40: Batch 53 — Full UI/art redesign (menu, road, HUD, pause, leaderboard, run summary)

Implemented against a user-supplied design mockup (`Car Crash Game UI Design/Reckless Driving UI.dc.html`), covering every screen except the car color/skin picker (explicitly excluded, left as-is). All gameplay mechanics — steering, vertical physics, NPC behavior, jump ability's energy/hold logic, collision rules — are untouched; this batch is presentation only, plus a few small new stat trackers needed to feed the new screens.

### New fonts and palette
Added Google Fonts 'Silkscreen' (headers, numbers) and 'Pixelify Sans' (body text). Introduced a CSS custom-property palette (`--c-red #e63946`, `--c-amber #f5b32a`, `--c-mint #2ee6b0`, `--c-night #12161f`, etc.) matching the design doc, used throughout the new/restyled CSS.

### Main menu split into Menu + Setup
The old single combined settings panel is now two screens: a slim main menu (title over a live-scrolling decorative road canvas, START RUN / SETUP / SCORES buttons, a read-only "CURRENT SETUP" summary card showing lanes/speed/ability/trucks/multiplier and best score) and a new **Setup** screen holding the actual settings form (lane count, tilt, steering buttons, hold-for-multiple-lanes, sound, night mode, car color picker — relocated unchanged) with its own BACK button.

### Road/verge art rebuilt as pre-rendered buffers
Replaced the old per-frame procedural tile-drawing loops with the design doc's buffer-and-blit approach: `makeVerge()`/`makeAsphalt()` pre-render a 576px-tall texture per side (grass/bush/tree/house/fence/sign sprites, weighted variety per a 24-slot table) and per lane-count (asphalt: grain, wheel-path wear bands, lane-boundary seams, repair patches), rebuilt only when lane count changes (`rebuildRoadBuffers()`) and blitted each frame (`drawRoadScene()`) — cheaper than the old approach and reused by both the main menu's demo road and the real game canvas. `roadOffset` now wraps at 4032 (LCM of the verge/dash/curb periods 576/28/16) instead of the old 336, so nothing desyncs at the wrap point.

### Car sprite redesign (player + normal/reckless NPCs only)
`drawPixelCar()` rewritten to the design's shading style and made direction-aware (`dir: 'up'|'down'`) — headlights/taillights now orient toward actual travel direction, so the ambulance (which drives *up* the screen since Batch 52) renders correctly reversed instead of looking backwards. Trucks and ambulances keep their existing sprites unchanged (no mockup provided for them, out of scope).

### Energy bar rebuilt as a canvas-drawn 10-cell bar
Replaced the old DOM `.ability-bar`/fill-width approach with `drawAbilityBar()`, a canvas port of the design's 10-cell bar: each cell's color depends on its own position (red→amber→green), a permanent notch marks the 25% take-off threshold, the frame goes hazard-striped while draining and marches with a dashed green outline once full. Reads the exact same `energy`/`abilityState`/`jumpHeld` values as before — the jump mechanic itself (`JUMP_MIN_ENERGY`, hold-to-fly, drain/recharge timing) is byte-for-byte unchanged per explicit instruction.

### In-game HUD redesign
Score/multiplier/speed now show as stacked chips top-right (dark chip background, amber multiplier, muted speed); pause button restyled to a small "II" icon top-left. Speed is now shown as **km/h** instead of the old raw internal unit — `speedToKmh()` is a cosmetic linear conversion (`round(currentSpeed × 34)`) picked to land roughly in a 50–200 km/h range across the game's actual speed range; `currentSpeed` has no inherent real-world scale, so this is a display-only invented mapping, not a physical unit.

### Pause screen redesign
Now a stats box (SCORE / TIME / DODGED / JUMPS) plus RESUME / RESTART / QUIT buttons. Needed two new trackers that didn't exist before: `dodgedCount` (incremented alongside the existing score bump when a vehicle is successfully passed) and reused the existing `jumpsUsed`.

### Leaderboard redesign
Rows now show rank/score/lanes+multiplier/survival-time with gold/silver/bronze styling for the top 3 and a highlight on the just-played run. Filter chips are **lane-count only** (ALL + one chip per lane count that has scores) — the old mode/ability filter chips were dropped since those settings are hardcoded now and filtering by them would do nothing; confirmed this scope with the user before implementing (three options offered, "lane-count filter only" chosen).

### Run summary / game-over screen redesign
"WRECKED" title, final score, a "NEW PERSONAL BEST" banner when applicable, and a stats box (BASE score / MULTIPLIER / SURVIVED / RANK), then RETRY / SCORES / MENU buttons. Needed two new bits of tracking: `baseScore` (pre-multiplier score, accumulated alongside `score` at the same increment points) and a rank computation in `saveScore()` (sorts, finds the new entry's index before slicing to top 10, returns `null` if it didn't make the cut) plus an `isNewBest` check (true if the leaderboard was empty or this score beats the previous max).

### Verification
Screenshots weren't available in this session (Browser pane wasn't displaying/compositing), so verification was done via direct canvas pixel sampling and DOM/state inspection instead: confirmed the menu canvas paints fully (205+ unique colors, no black gaps) at multiple lane counts including 6-lane with night mode; walked the full Menu→Setup→back, Menu→Game→Pause→Resume, Menu→Game→Restart, Menu→Game→Quit, and Menu→Scores→Back navigation graph via simulated clicks; forced a vehicle despawn to confirm `score`/`baseScore`/`dodgedCount` all increment correctly together; forced a collision to confirm the run-summary screen populates BASE/MULTIPLIER/SURVIVED/RANK and the personal-best banner correctly (both the "didn't rank" and "new #1" cases, against the real pre-existing 10-entry leaderboard in this browser profile); confirmed the leaderboard's lane-only filter chips and simplified meta text render as specified; confirmed both Google Fonts loaded (`document.fonts` reports `loaded` for Pixelify Sans and Silkscreen); confirmed steering-buttons track builds the right zone count and frame-height math still accounts for it; zero console errors throughout. A fake test score (1000 pts) written during verification was removed from `localStorage` afterward so it doesn't pollute the real leaderboard.

---

## 1.41.0 — 2026-08-25 06:10: Batch 52 — Ambulance overtakes from behind, optional single-lane-per-press

### Ambulance now spawns behind the player and overtakes from behind
The previous fix (Batch 48) made the ambulance's speed proportional instead of a flat bonus, but the user confirmed via direct visual check that it still "came from the wrong way" — clarified specifically: it appeared ahead of the player and rushed toward them, when it should appear from behind and overtake, like real traffic. Root cause wasn't speed at all — every vehicle type spawns ahead of the player (off-screen top) and moves down; the ambulance was no exception, so it looked like oncoming traffic rushing at the player rather than emergency traffic catching up and passing. Fixed by giving the ambulance a genuinely different spawn/motion model: spawns off-screen at the *bottom* (`canvas.height + 10`, was `-height - 10` like everything else) and moves *up* (its `speedOffset` sign flipped positive, so `speed = currentSpeed - speedOffset` comes out negative — same `2.0-2.5×currentSpeed` magnitude as before, just reversed). The shared despawn-and-score check (`v.y > canvas.height`, previously the only exit condition, for traffic leaving off the bottom) now also fires when a vehicle exits off the *top* (`v.y < -v.height - 20`), so the ambulance is correctly cleaned up and scored once it's overtaken and gone.

### New setting: Hold for Multiple Lanes (on by default)
Turning it off makes every arrow/A-D press move exactly one lane, no matter how long the key is held — holding no longer glides across multiple lanes at all. Implemented by never setting `hHeldDir` true when the setting is off (so `Player.update()`'s glide branch never triggers); each non-repeat keydown instead directly sets `player.targetX` one lane over via the existing `laneCenterX()`/`currentLaneIndex()` helpers.

### Verification
- Ambulance: confirmed via live screenshots (not just code) — placed one near the player's own Y and watched it move up and away over successive frames, matching "comes from behind, overtakes, continues ahead." Spawn Y (270) confirmed below `canvas.height` (260); despawn-off-the-top confirmed via the same mechanism scoring/removing it once it exited above `-height-20`.
- Setting: with "Hold for Multiple Lanes" off, a 60-frame hold of ArrowRight moved exactly one lane (not multiple); default (on) behavior unaffected.
- No console errors after any of the above

---

## 1.40.0 — 2026-08-25 05:35: Batch 51 — Guaranteed one-lane tap, no more straddle-spawn

### A very quick tap could fail to change lanes at all
Release always rounded to the nearest lane based on actual traveled distance — a tap short enough that the car hadn't crossed halfway to the next lane rounded right back to the lane it started in, so the input did nothing. `snapToNearestLane(direction, startLane)` now takes the press direction and the lane index captured when the hold began (`pressStartLane`, set on the keydown down-edge only, not on native key-repeat); if release would otherwise round back to that same starting lane, it forces exactly one lane over in the pressed direction instead. A hold long enough to actually travel multiple lanes is unaffected — the forced case only applies when the rounded result is a no-op. New shared `currentLaneIndex()` helper (also now used by `updateSteeringTrackActive()`, replacing its own duplicate of the same calculation).

### Player no longer spawns straddling two lanes at an even lane count
`Player`'s starting `x` was the raw geometric center of the road — exactly on a lane boundary for any even lane count (the default 4-lane setting included). Now computed as the center of a specific lane index (`Math.floor(config.lanes/2)`, arbitrary but consistent — "you decide, doesn't matter which" per the user), which lands on an actual lane center for both even and odd counts.

### Verification
- Simulated a zero-frame tap (keydown immediately followed by keyup, no `update()` calls in between) — the car still ended up exactly one lane over after settling
- A 40-frame hold from lane 0 correctly traveled 3 lanes (not forced to 1), confirming the guarantee only kicks in for genuine no-op taps
- Default 4-lane spawn: car's center lands exactly on `laneCenterX(2)`, not the old straddle point; 5-lane spawn (odd, already correct before) still lands exactly on `laneCenterX(2)`, confirming no regression
- No console errors

---

## 1.39.0 — 2026-08-25 05:00: Batch 50 — Speed HUD, multiplier floor, optional steering buttons

### Speed shown in the HUD
New `#hudSpeed` DOM overlay element ("SPEED: X.X"), below score/multiplier, updated every frame from `currentSpeed`.

### Multiplier can no longer start below 1.0x
`calculateMultiplier()`'s floor changed from `Math.max(0.4, ...)` to `Math.max(1.0, ...)`. At high lane counts (9-10) the lane-count penalty (`-0.1` per lane above 4) could push the total under 1.0x — user: settings should only add a bonus or shrink one, never turn into an outright penalty below the baseline.

### Optional on-screen steering buttons (mouse-drag control reintroduced, redesigned)
The old free-drag mouse slider (removed in Batch 41) is not back — this is a different control. New `.steering-track` bar, one zone per lane spanning the game's width, shown below the canvas **only when explicitly enabled** (new "Steering Buttons" setting, off by default, matching the "off = more screen for gameplay" tradeoff the user described). Clicking or press-and-dragging across zones sends the car straight to that lane's center via the same `player.targetX`/`laneCenterX()` mechanism arrow-key lane-snapping already uses — not a free/analog position, discrete lane-jumps only, matching "your car behaves the same as with arrow keys." The zone matching the player's current lane is highlighted each frame (`updateSteeringTrackActive()`) as a visual "you are here" indicator.
- `laneCenterX(lane)` extracted as a shared helper (previously duplicated inline in `snapToNearestLane()`)
- `sizeGameFrame()` now also subtracts the track's fixed 44px height from available vertical space when the setting is on, so the canvas still comes out undistorted and the frame still exactly fits the viewport
- Setting is read into `config.steeringButtonEnabled` at `launchGame()` time (not persisted to localStorage, matching the majority of this menu's settings)
- Cleaned up a stale doc-comment left over from Batch 48's removal of `getArrowTarget()` that had drifted onto the wrong function

### Verification
- Multiplier: `config.lanes=10`/`9` now both floor at exactly `1.0` (previously `0.8`/`0.9`); `config.lanes=4` unaffected at `1.5`
- Steering track: enabling the setting shows a 4-zone track matching 4 lanes; clicking the rightmost/leftmost zones set `player.targetX` to exactly `laneCenterX(3)`/`laneCenterX(0)`; `updateSteeringTrackActive()` correctly highlighted the zone matching a manually-set player position
- Frame still fills the viewport with the setting on (340px frame in a 380px/40px-padded viewport, track visible) and off (same 340px, track hidden) — confirms the CHROME/track-height accounting is correct in both states
- No console errors after any of the above

---

## 1.38.0 — 2026-08-25 04:10: Batch 48 — Fully smooth steering, proportional ambulance speed

### Horizontal steering is now smooth from the very first frame
Batch 45's model still did a discrete "snap to the next lane" on the initial press, only switching to a continuous glide once that snap had essentially arrived — user felt that initial snap as a jump before the smooth part kicked in. Simplified: holding a direction now glides continuously at `glideSpeed` starting immediately on press, no discrete step first. Releasing still calls `snapToNearestLane()` (unchanged) to round to the nearest lane, eased in via the existing LERP. `getArrowTarget()` — the function that computed the initial snap target — is now dead code and was removed entirely, along with the initial-press-only branch in the keydown handler.

### Ambulance speed made proportional to currentSpeed
User: the ambulance looked like it was going in a different direction than the rest of traffic and didn't make sense — it should come in the same direction everyone drives, just faster. Investigated by measuring actual per-frame movement rather than guessing: the ambulance's sign was already correct (same nominal on-screen direction as all visible traffic — vehicles moving the *other* way never actually become visible given the spawn/despawn model, so a literal direction flip wasn't the issue). The real problem was scaling: every other vehicle type's `speedOffset` is a fraction of `currentSpeed`, but the ambulance's was a flat `+2.5-3.0×CAR_SCALE` bonus independent of `currentSpeed` — at the start of a run (`currentSpeed≈1.56`) that fixed bonus was 2-3x `currentSpeed` itself, making the ambulance look completely disconnected from how everything else on the road was moving, right when players are most likely to be paying close attention. Changed to `speedOffset = -currentSpeed × (1.0-1.5)`, giving a speed consistently `2.0-2.5×currentSpeed` at any point in a run — same relative "clearly the fastest thing on the road" feel early or late, matching how every other vehicle type already scales.

### Verification
- Scripted: holding ArrowRight showed a constant 2.86px/frame delta from the very first frame (was previously eased from ~1.56 down before glide kicked in), settling cleanly to the target lane center on release
- Ambulance speed sampled at `currentSpeed=1.56` (ratio 2.42×) and `currentSpeed=4.0` (ratio 2.23×) — consistent ~2.2-2.4× scaling at both low and high game speed, confirming the proportional fix
- No console errors

### Added to backlog (not implemented — see PLAN.md)
Batch 49: static road obstacles (crashed cars, debris) to dodge, alongside moving traffic — user's own framing, explicitly "for a future batch," not scoped further.

---

## 1.37.0 — 2026-08-25 03:20: Batch 47 — Full-screen game frame, reckless drivers toned way down

### Reckless drivers were the real source of "cars change lanes too often"
Normal/truck lane-changers stop after one change; reckless drivers re-roll forever — that made them the dominant visual impression even after normal/truck frequency and NPC transition speed were both tuned down twice already. They were 23% of all spawns (`roll < 0.25` of the non-ambulance range); cut to 10% (`roll < 0.12`). Their re-roll timer (how often the SAME reckless car changes lanes again) widened from 70-170 frames (1.2-2.8s) to 150-300 frames (2.5-5s), in both the constructor and the post-change re-roll.

### Game frame now genuinely fills the screen
User's diagnosis was exactly right: the visible bordered frame (`.game-container`) was already filling available height, but the *canvas inside it* wasn't — leaving empty space between frame and gameplay. Root causes, found by actually measuring computed layout rather than guessing:
- A stale `.instructions` block (leftover control-hint text, still referencing "drag the blue slider" — a control removed two batches ago) sat below the game view as a `display:block` sibling in `body`'s flex column, silently eating ~90px of the vertical space the frame should have gotten. **Removed entirely**, along with the `<h1>RECKLESS DRIVING</h1>` title and the "Complete the verification to prove you are human!" subtitle — all three were explicitly asked to go.
- `.game-footer` (by this point just holding the Retry/Menu buttons) removed too — those buttons moved *into* the existing `#gameOverHud` DOM overlay (which already showed "CRASHED!" + score on top of the canvas) instead of living in a separate footer bar below it.
- CSS `aspect-ratio` + percentage-height + `max-width` together, on a plain (non-replaced) `.game-container` div, turned out to resolve inconsistently depending on which dimension was actually binding — correct when height was the tighter constraint, silently non-uniform (stretched pixel art) when width was, e.g. on a narrow mobile viewport. Replaced with a `sizeGameFrame()` JS function that computes the frame's exact width/height directly (largest box matching the canvas's true aspect ratio that fits the viewport, accounting for the fixed border/padding "chrome" around the canvas so the canvas itself — not just the outer frame — comes out undistorted), called from `applyLaneLayout()` and on window resize.

### Verification
- Spawn distribution over 20,000 simulated rolls: reckless 10.2% (target ~10%, was ~23%), truck 19.8%, normal 68% — matches the new thresholds
- Reckless `changeLaneTimer` samples all fell in the new 150-300 frame range
- Game frame measured filling available height exactly (942px frame in a 982px-tall/40px-padded viewport) with the canvas's rendered aspect ratio matching its true internal ratio (0.541 vs 0.538) on desktop; on a clamped-by-width mobile viewport (375×812) the frame correctly shrank to 335×598 (still ratio-correct, no stretching) instead of distorting; live resize recomputation confirmed via manual event dispatch (the Browser pane's programmatic resize doesn't fire a real `resize` event, unlike an actual browser window)
- Relocated game-over Retry/Menu buttons confirmed rendering and clickable (`pointer-events:auto`) inside `#gameOverHud`
- No console errors after any of the above

---

## 1.36.0 — 2026-08-25 02:30: Batch 46 — Smooth multi-lane glide, slower/accelerating vertical, calmer NPC lane changes

Three more fixes from continued playtesting of Batch 44/45:

### NPC lane-change speed halved again
`laneChangeSpeed` still looked "way too quick" once precise lane-snap made the comparison to the player's own settled movement more obvious. Normal `0.6-0.9 → 0.3-0.45` (pre-`CAR_SCALE`), reckless `1.0-1.4 → 0.5-0.7`.

### Smooth multi-lane hold (no more stop-start at every lane)
Holding an arrow to cross several lanes used to re-trigger a discrete lane-snap on every native key-repeat event, each one fully settling (LERP converges in ~100ms) well before the next repeat fired ~220ms later — a visible dead pause at every lane. Reworked: the initial press still snaps to the next lane exactly as before (`getArrowTarget`); if the key is still held once that snap has essentially arrived (`|targetX - x| < 0.75`), `Player.update()` switches to a continuous glide at `HORIZONTAL_GLIDE_SPEED_BASE/MAX` (renamed from `MOVE_SPEED_BASE/MAX`, values unchanged) instead of waiting for another snap, keeping `targetX` locked to `x` so the LERP is a no-op mid-glide. Releasing the key calls the new `snapToNearestLane()`, which rounds the car's actual current position to the nearest lane center and lets the LERP ease the last bit in — so it still always comes to rest exactly on a lane, just via a smooth glide-then-settle instead of a staircase. `LANE_SNAP_REPEAT_MS`/`lastLaneSnapTime` are gone; `hHeldDir={left,right}` tracks the raw held state instead.

### Vertical movement: slower top speed, plus acceleration/friction/braking
Was an instant constant speed the moment a key was pressed — user wanted it slower and physically eased. New model (`Player.vVelocity`, signed): holding Up/Down accelerates toward a top speed (`V_ACCEL`) instead of snapping to it; releasing coasts to a stop via friction (`V_FRICTION`) rather than stopping dead — "release then move a little more"; pressing the opposite direction while still moving decelerates faster than friction alone (`V_BRAKE`, an actual brake) before reversing into acceleration the other way. Top speed itself also dropped: `V_MAX_BASE=1.3×CAR_SCALE` / `V_MAX_TOP=2.2×CAR_SCALE` (was `MOVE_SPEED_BASE/MAX` = `2.2/3.5×CAR_SCALE`, now horizontal-only, renamed `HORIZONTAL_GLIDE_SPEED_BASE/MAX`). Velocity is zeroed on hitting `PLAYER_MIN_Y`/`MAX_Y` so it doesn't sit "pressing against the wall" building unused velocity.

### Verification
- Scripted: holding ArrowRight for 90 frames showed the LERP ease (delta 1.56→0.09 px/frame) transition directly into a flat 2.86px/frame glide with no dead-zero stretch in between, then a clean settle to the exact lane center on release
- Vertical: acceleration ramped `-0.169 → -1.69` (exactly `V_MAX_BASE`) over 10 frames while held; released, coasted `-1.586 → 0` over ~16 frames; braking (Down while still moving up at `-1.69`) crossed zero in 5 frames then began accelerating the other way — all matching the designed rates
- NPC `laneChangeSpeed` samples: normal 0.405-0.582 (target 0.39-0.585), reckless 0.683-0.902 (target 0.65-0.91) — both in range
- No console errors after any of the above

---

## 1.35.0 — 2026-08-25 01:40: Batch 44 — Steering reverted to lane-snap, plus playtest fixes

Four fixes from a single round of playtesting feedback after Batch 41-43:

### Steering reverted back to lane-snap (Batch 41 undone for horizontal only)
User tried full free horizontal movement for a while and it didn't work out — holding a key was imprecise, a slight over/under-hold could clip a car that would've been avoidable with precise lane positioning, which felt like bad luck rather than a mistake. Horizontal is lane-snap again: arrows/A-D set `player.targetX` to the next lane center (`getArrowTarget()`, restored from before Batch 41, "smart" center-first behavior only — the old Nearest/Smart mode setting was not reinstated, wasn't asked for), and `Player.update()` eases toward it with the same speed-scaled `steerLerp` (`0.12 → 0.30` base→max speed) Batch 39 tuned. Vertical (Up/Down) is untouched — still free/continuous, that was never the complaint. Touch-drag now sets `targetX` instead of `player.x` directly (a direct write would've fought the new easing every frame). `hKeys` is gone entirely.
- New: cosmetic banking-tilt animation while actively snapping between lanes — `player.tiltAngle`, derived each frame from that frame's actual horizontal movement (`dx * TILT_SENSITIVITY`, clamped to `±MAX_TILT_ANGLE = 0.3 rad`), so it eases in fast and back to level naturally as the car settles, no separate state machine needed. `drawScaledVehicle()` now takes `width`, `height`, and an optional `angle`, rotating around the sprite's center before the existing `CAR_SCALE` transform — NPCs still call it with no angle (level), only the player banks

### NPC lane-change frequency halved again
Normal car chance `0.15 → 0.075`, truck chance `0.08 → 0.04` — user felt lane-changing was still way too frequent even after Batch 39's reduction.

### Stutter fix
Root cause: `drawScaledVehicle` (Batch 42) translated by `Math.floor(x, y)` before scaling. Slow-moving vehicles (sub-1px world speed is common, e.g. a car matched close to the player's own speed) would hold at the same floored pixel for 2-3 frames then jump — always existed, but got more visible once `CAR_SCALE`'s `ctx.scale` made each jump bigger on screen. Fix: translate by the raw unfloored position — costs a hair of edge anti-aliasing during motion, motion reads as smooth.

### Canvas height is no longer a fixed internal resolution
Previously the canvas was sized by width (`width:100%` of its container) with height following via `aspect-ratio`, so a short viewport (small window, landscape phone) could make the page taller than the screen and force a scrollbar — user explicitly didn't want that. Reworked the whole vertical chain (`body` → `.view.active` → `.game-container` → `.canvas-container` → `canvas`) into a flex column where every level can shrink (`min-height:0`, `flex:1 1 auto`), with `body` given a hard `height:100dvh` instead of `min-height:100vh`. The canvas itself switched from `width:100%; max-width:480px; aspect-ratio:...` to `width:auto; height:100%; max-width:100%; max-height:480px` — a replaced element with a real intrinsic aspect ratio (from its `width`/`height` attributes) auto-fits within whichever constraint (available width or available height) is tighter, the same mechanism responsive images use with `object-fit:contain`. `body` keeps `overflow-y:auto` only as a safety net (e.g. an unusually tall settings panel on a tiny screen); it should never actually trigger during normal play.

### Verification
- Scripted: one ArrowRight press moved the car exactly to the next lane center (delta = laneWidth = 26px on the second press, since the default start is mid-lane); `tiltAngle` was non-zero and decaying mid-transition, back to 0 once settled; vertical movement unaffected
- Resized the live page to 700×380 (short landscape) and 375×812 (mobile portrait) — `document.body.scrollHeight <= window.innerHeight` held in both, canvas visibly shrank to fit at the short viewport
- No console errors after any of the above

---

## 1.34.0 — 2026-08-25 00:20: Batch 42 — Tighter lanes, bigger cars, matching world speed

Direct follow-on to Batch 41. User's framing: today's lanes are roughly 2x a car's width — unrealistic — but the fix should be "grow the car sprite to fill more of the lane," not "shrink the lane's pixel math." Confirmed two numeric targets before implementing (guessing wrong here would've meant redoing math across rendering, collision, and spawn logic together): car ≈ 70% of lane width, and world/movement speed scaled by the same ratio as the size increase.

### Sizing
- New `CAR_SCALE = 1.3` (30% bigger) drives everything: `PLAYER_WIDTH = round(14×1.3) = 18`, `PLAYER_HEIGHT = round(24×1.3) = 31`, `TRUCK_HEIGHT = round(56×1.3) = 73` — replace the old hardcoded `14`/`24`/`56` literals wherever they represented an actual hitbox/position (Player and Vehicle constructors, `laneClearForMerge`, `canSpawnAt`'s vertical-gap check)
- `REF_LANE_WIDTH` raised `17 → 26` (`round(PLAYER_WIDTH / CAR_FILL_RATIO)`, `CAR_FILL_RATIO = 0.7`) — measured result: car width / lane width ≈ 0.69, matching target
- `applyLaneLayout()`'s lane-count-scaling special case removed: **all** lane counts now use `REF_LANE_WIDTH × lanes` for the road/canvas width, not just 8-10 (≤7 used to share a fixed 124px road regardless of count, which is what made low lane counts feel disproportionately loose)
- The three `drawPixelCar`/`drawPixelTruck`/`drawPixelAmbulance` functions still draw at their original 14×24 (or 14×56) design resolution internally — untouched. New `drawScaledVehicle(x, y, drawFn)` helper wraps each of the 4 call sites in `ctx.translate` + `ctx.scale(CAR_SCALE, CAR_SCALE)` instead, so the exact same pixel art renders bigger without touching a single `fillRect` coordinate

### Speed
- `baseSpeed`/`maxSpeed`/`currentSpeed`, `MOVE_SPEED_BASE`/`MOVE_SPEED_MAX` (player movement), `LANE_CHANGE_WARNING_DISTANCE`, NPC `speedOffset` ranges (all 4 vehicle types), and NPC `laneChangeSpeed` ranges (normal + reckless) all multiplied by `CAR_SCALE` — everything that was a px/frame or px distance calibrated against the old car size now scales with the new one
- `speedOffset`'s spawn-time clamp (`currentSpeed × 0.75 / 1.5`) needed no direct change — it's already relative to `currentSpeed`, which is itself scaled

### Verification
- Scripted checks against the live game: `REF_LANE_WIDTH=26`, `PLAYER_WIDTH=18`, `PLAYER_HEIGHT=31`, fill ratio `0.69` (target 0.7), `baseSpeed=1.56`/`maxSpeed=5.85` (both ×1.3 of the pre-Batch-42 values), `TRUCK_HEIGHT=73`, lane-change speed samples in the scaled 0.78-1.17 range
- Pixel-sampled the player's sprite bounding box after render (`ctx.getImageData`) — 100% of pixels in the box were non-background color, confirming the scaled sprite draws correctly (not blank, not throwing) after the `ctx.scale` rework; no console errors

### Not done in this batch
- Batch 43 (verification/tuning pass) is next: collision-feel playtest with the bigger cars, whether the "boxed in with no escape" concern got better or worse, general retuning

---

## 1.33.0 — 2026-08-24 23:15: Batch 41 — Lane-snap steering removed, full free movement

User decided (after weighing the lane-snap-vs-free-movement tradeoff discussed for Batch 39) to drop lane-snap steering entirely: horizontal movement is now continuous/free, matching how vertical movement (Batch 33) already worked, instead of snapping between lane centers.

### Removed
- The entire lane-snap steering system: `getArrowTarget()`, `LANE_SNAP_REPEAT_MS`/`lastLaneSnapTime`, the `arrowMode` setting (Smart/Nearest select + its localStorage persistence) — none of it applies once movement isn't lane-based
- The visible mouse-drag `#controlSlider` control and its CSS (`.slider-wrapper`, `.control-slider*`) — was the last remaining "snap to a slider position" input; superseded by direct key-driven movement (this also incidentally finishes what Batch 28 was scoped to do, since the slider is gone)
- `player.targetX` — no longer meaningful without a slider target to track

### Added / changed
- New shared `hKeys = {left, right}` state (mirrors `vKeys`), set directly by ArrowLeft/A and ArrowRight/D on keydown/keyup — both axes now move the same way: hold a key, car moves continuously, released key stops it, clamped to road/canvas bounds
- `VERTICAL_SPEED_BASE`/`VERTICAL_SPEED_MAX` renamed to `MOVE_SPEED_BASE`/`MOVE_SPEED_MAX` (2.2 → 3.5 px/frame, scaled by the existing `speedRatio`) and now drive **both** axes — this was the direct fix for the player's own complaint that horizontal (fast, lane-snapped) and vertical (slower, free) felt inconsistent with each other
- Touch-drag-on-canvas (mobile, deferred) reworked from "drag the hidden slider by percentage" to directly repositioning `player.x` 1:1 with the finger, scaled by `canvas.width / rect.width` since canvas internal resolution differs from its displayed CSS size
- Tilt steering (mobile, deferred) reworked from "snap the slider to a gamma-proportional position" to nudging `player.x` by `moveSpeed` toward the tilt direction each frame, same speed budget as keys — kept it minimally functional rather than fully redesigning, per the standing "don't invest in mobile" instruction

### Verification
- Scripted check via `player.update()` with `hKeys`/`vKeys` set: player moved from x=73 to x=128 (= `ROAD_BORDER_RIGHT - player.width`, correctly clamped) while holding right+up, then to x=62 while holding left+down — both axes moved smoothly and independently, no console errors
- Confirmed no leftover references anywhere in the file to `controlSlider`, `selectArrowMode`, `arrowMode`, `getArrowTarget`, `LANE_SNAP_*`, `targetX`, or `VERTICAL_SPEED_*`

### Not done in this batch (planned as follow-ups — see PLAN.md)
- Batch 42: shrink the effective lane/car size ratio (tighter, more realistic lanes achieved by growing the car sprite, not shrinking lane pixel math) and fix lane-count canvas scaling so all lane counts (not just 8-10) scale proportionally
- Batch 43: verification/tuning pass once Batch 42 lands (collision math with bigger cars, spawn safety margins, NPC lane width vs. player free movement)

---

## 1.32.1 — 2026-08-24 22:30: NPC lane-change speed + vertical movement speed-scaling fixes

Two direct fixes from user feedback after playtesting Batch 39/33: NPC lane changes felt "way too slow... stuttering", and the player's vertical movement felt sluggish compared to horizontal steering.

- `Vehicle.laneChangeSpeed` raised ~3x: normal `0.2–0.3 → 0.6–0.9`, reckless `0.35–0.5 → 1.0–1.4` — a lane crossing at speed 0.75 now takes ~0.7s (was ~2.05s)
- Vertical movement changed from a flat `VERTICAL_SPEED = 1.5px/frame` to speed-scaled `VERTICAL_SPEED_BASE = 2.2` → `VERTICAL_SPEED_MAX = 3.5`, using the same `speedRatio` pattern as `steerLerp`, so both axes scale with game speed consistently (superseded again in 1.33.0 when horizontal became free-moving too, but the actual px/frame values carried forward)
- Verified via scripted checks: `normalSpeedRange: [0.62, 0.89]`, `recklessSpeedRange: [1.01, 1.39]`, `verticalSpeedAtBase: 2.2`, `verticalSpeedAtMax: 3.5`

---

## 1.32.0 — 2026-08-24 21:30: Batch 39 — Fairness & difficulty tuning, following a design discussion

User raised a genuine dilemma: lane-snap steering prevents cheesing (straddling two lanes so nothing can hit you) but felt unfair against fast NPC lane-changers at high speed. Researched genre precedent before recommending a direction — see chat for the full writeup and sources. Conclusion: keep lane-snap (it's the standing convention across the whole lane-runner genre, not an arbitrary anti-cheese hack — even modern touchscreen games with full analog capability keep choosing it, for the same collision-fairness reason), and fix the reaction-time economy around it instead. User agreed and specified the following, all implemented:

### More lookahead
- Canvas internal height raised `220 → 260` (new `CANVAS_HEIGHT` constant) — a moderate ~18% increase per "don't overdo it"
- `PLAYER_MAX_Y` (now `CANVAS_HEIGHT - 24 - 1 = 235`) and the `canSpawnAt` vertical-safety threshold (`140 → 165`, new `SPAWN_SAFETY_Y = round(140 * CANVAS_HEIGHT/220)`) scaled proportionally
- `PLAYER_MIN_Y` (40) and the player's default start (`canvas.height - 35`, now 225) needed no change — they already reference the height dynamically or don't depend on it

### NPC lane-change frequency lowered, trucks now eligible
- Normal car lane-changer chance: 25% → 15% (was 45% originally, two batches ago)
- Trucks can change lanes now too, but rarely: 8% chance (were never lane-changers before), same timer pacing as normal cars once eligible

### NPC warning now scales with distance, not a fixed frame count
- New `LANE_CHANGE_WARNING_DISTANCE = 90px` target; `indicatorFrames = round(90 / vehicleScreenSpeed)`, clamped to `[LANE_CHANGE_INDICATOR_MIN=25, LANE_CHANGE_INDICATOR_MAX=150]` frames
- A fixed frame count was covering less and less road distance as `currentSpeed` rose through a run, silently shrinking the real reaction window as the game got harder — this keeps the covered distance roughly constant instead
- Reckless indicator is 75% of the (now distance-scaled) normal duration, same formula then × 0.75

### Player steering sped up
- `steerLerp`: `0.045 → 0.18` (base→max speed) raised to `0.12 → 0.30` — noticeably snappier immediately, still eased/animated rather than an instant teleport

### Confirmed already existing (no work needed)
- Max game speed is already hard-capped (`maxSpeed = 4.5`); `currentSpeed` never grows past it. Told the user this rather than re-implementing.

### Explicitly out of scope
- Mobile-specific changes (tilt steering etc.) — user is planning a from-scratch native Android app later and doesn't want mobile work invested in this HTML prototype in the meantime
- Jump rework — logged as **Batch 40** with the full spec the user gave (fixed duration again, tuned so a perfectly-timed jump at base speed just barely clears one car), explicitly deferred to next batch, not implemented now

### Verification
- Canvas height/player bounds/spawn-safety threshold all scaled to the expected values (260/40/235/165)
- Lane-changer rates measured over 2000 trials each: 15.4% normal (target 15%), 7.65% truck (target 8%)
- Indicator distance-scaling confirmed shorter at higher speed (149 frames at base speed vs 79 at max for normal cars); reckless landed within rounding of exactly 75% of normal at both speeds tested (112/149=0.752, 59/79=0.747)
- `steerLerp` values matched exactly: 0.12 at base, 0.30 at max
- No console errors on load

---

## 1.31.1 — 2026-08-24 21:10: Speed clamp moved from live per-frame to spawn-time only

1.31.0's clamp recomputed the `[0.75, 1.5]` bound every frame using the live `currentSpeed` — which keeps rising through a run, so the boundary itself creeps, causing visible twitch/stutter for any vehicle sitting near it.

- Moved the clamp into the `Vehicle` constructor: `speedOffset` is bounded once, using `currentSpeed` at the moment of spawn, then never touched again
- `update()` reverted to the plain `speed = currentSpeed - this.speedOffset` — no per-frame clamping at all
- A vehicle's own speed is now perfectly smooth for its entire lifetime; its ratio to the player's (still-rising) speed naturally drifts after spawn, which is expected and fine — only the *initial* relative speed needed bounding
- Ambulances remain exempt (unchanged)
- Verified: `speedOffset` stayed bit-for-bit identical across 50 simulated frames of `currentSpeed` rising by 0.01/frame after spawn (previously it would have shifted every frame)

---

## 1.31.0 — 2026-08-24 21:00: NPC vehicle speed bounded directly relative to the player

Direct user request: "no car can go slower than 0.75 speed of player and no faster than 1.5x (except ambulance)." Replaces the earlier `Math.max(currentSpeed*0.35, ...)` screen-speed floor (Batch 19) with a more direct, two-sided bound.

- `Vehicle.update()` now clamps `speedOffset` (each vehicle's own world-space speed) to `[currentSpeed*0.75, currentSpeed*1.5]` before computing screen-relative motion — recomputed every frame since `currentSpeed` keeps rising through a run
- Ambulances are exempt, using their raw (very negative) `speedOffset` unclamped, same as always
- This means a vehicle can now legitimately drift backward on screen if its speed is genuinely close to the 1.5x ceiling (a car going 1.5x your speed pulling away from you is expected, correct behavior) — the earlier floor was specifically about preventing an *illusion* of reversal from a vehicle that was actually just slow, which this design also happens to fix as a side effect for the common case, since fixed `speedOffset` ranges (roughly -0.5 to +2.0 across all types) fall further and further below the growing `0.75×currentSpeed` threshold as the game speeds up

### Verification
- Reverse-derived each vehicle's effective world speed from its actual screen motion, at 3 game speeds (base/mid/max) × 4 types: ratio landed at exactly 0.75 whenever the type's raw `speedOffset` was below that floor (which was every non-ambulance type at every tested speed except one), and ambulance ratios were wildly outside [0.75, 1.5] every time, confirming the exemption held
- Forced a truck's `speedOffset` to 2.0 at base speed (where `1.5×currentSpeed = 1.8 < 2.0`) — confirmed it clamped down to exactly the 1.5 ceiling

---

## 1.30.0 — 2026-08-24 20:45: Jump reworked into true hold-to-fly + Batch 32 visual redesign

The 1.29.0 jump rework (proportional-duration, but still a pre-computed fixed countdown once started) wasn't quite what was wanted — reworked into genuine hold-to-fly, plus pulled Batch 32's visual redesign forward since it touches the same code.

### Hold-to-fly
- `useAbility()` no longer pre-computes a duration — it just starts the jump (`jumpHeld = true`) if `energy >= JUMP_MIN_ENERGY` (25%, new constant — the floor only gates takeoff, not how far you can drain once airborne)
- Energy now drains in real time only while the key/bar is actually held (`JUMP_DRAIN_PER_FRAME`), not spent upfront
- Releasing early (space keyup, or mouseup/touchend on the ability bar) sets `jumpHeld = false`, which stops the drain immediately — whatever energy is left stays as-is, it's not zeroed just because you let go
- Added a `keyup` listener for Space (there wasn't one before — keydown alone can't detect release) and converted the ability bar from a single `click` to `mousedown`+`mouseup`/`touchstart`+`touchend` (plus `mouseleave` as a safety net for dragging off the bar mid-press) so touch/mouse users get the same hold-and-release control as keyboard

### Bigger energy pool
- `JUMP_FULL_DRAIN_MS` raised from 1000ms to 2500ms — a full-charge, continuously-held flight now lasts 2.5x as long

### Flight height replaces the duration-based arc
- New `flightHeight`/`jumpHeld` state: rises at `FLIGHT_RISE_SPEED` (0.8px/frame) up to `MAX_FLIGHT_HEIGHT` (14px) while held, falls at `FLIGHT_FALL_SPEED` (1.2px/frame) once released or out of energy — lands (`abilityState` back to `idle`, `rechargeDelay` starts) only once height reaches 0
- This replaces the old sine-arc-over-fixed-duration visual entirely; `drawPixelCar` now takes `flightHeight` directly instead of `activeAbilityTime`/`activeAbilityMaxTime`

### Batch 32 — Jump meter visual redesign (pulled forward)
- Bar enlarged 70×14px → 84×18px
- New black-and-yellow diagonal hazard-stripe border via `border-image: repeating-linear-gradient(...)`
- Charging fill color now computed per-frame by `energyColor(pct)` (red→yellow→green), set as inline style so it tracks energy continuously
- Active/flying fill animates through the full color spectrum via `filter: hue-rotate(360deg)` over 1.2s
- Green marching-ants "ready" cue kept as-is (Batch 18), still specifically means 100% full — distinct from the new 25% activation floor

### Verification (against the real running game)
- Jump blocked at 20% energy, allowed at exactly 25%
- 10 held frames: energy dropped by exactly 6.66 (0.666/frame), flightHeight rose to exactly 8 (0.8/frame)
- Releasing mid-air preserved the exact remaining energy (18.336) through to landing, unchanged
- `rechargeDelay` measured to start precisely when landing actually completed mid-sequence, not at the moment of release (283.42ms remaining after 20 test frames, matching hand calculation)
- Full 100%-energy continuous hold drained in 151 frames (≈2516ms), matching the 2500ms target
- `energyColor(0/25/50/75/100)` returns pure red, red-orange, pure yellow, yellow-green, pure green exactly as specified
- No console errors on load

---

## 1.29.0 — 2026-08-24 20:15: Batch 34 — Jump Ability Rework

### Usable any time, duration scales with charge
- `useAbility()` no longer requires `energy >= 100` for jump — just `energy > 0`
- `activeAbilityTime = (this.energy / 100) * JUMP_MAX_DURATION` (new constant, 1000ms — same peak duration jump always had), so a 40% charge gives a 400ms hop, 100% gives the full 1000ms as before

### Energy drains in real time, not spent upfront
- Previously `useAbility()` zeroed energy instantly on activation and ran a fixed timer regardless of charge
- Now energy tracks the countdown directly while jumping: `this.energy = (activeAbilityTime / JUMP_MAX_DURATION) * 100`, recalculated every frame — so running out of energy mid-air is the same event as the jump timer hitting zero, not a separate condition to handle

### Wings while airborne
- `drawPixelCar`'s `isJumping` branch now draws a wing on each side (`#dfe6e9` with a `#95a5a6` shade line), extending outward from the car body

### Jump arc fixed to scale with each jump's own duration
- Found while implementing: the existing arc calculation divided by a hardcoded `1000`, which would have made a partial-charge jump barely lift off the ground (since `progress` would only ever reach e.g. 0.4) instead of doing a full, just-shorter arc
- Added `activeAbilityMaxTime`, captured at takeoff (`this.activeAbilityMaxTime = this.activeAbilityTime`) and threaded through to `drawPixelCar` as a new parameter; arc progress is now `activeAbilityTime / activeAbilityMaxTime`, always spanning a full 0→1→0 sine cycle regardless of jump length

### Post-landing recharge delay
- New `rechargeDelay` field, set to `JUMP_RECHARGE_DELAY` (500ms) whenever a jump ends; the per-frame recharge only runs once it's counted down to 0

### Scope note
- Ram Shield's `energy >= 100` gate and fixed-duration behavior were left untouched — this rework was jump-specific per the request, and Ram Shield is unreachable anyway (Batch 37)

### Verification
- Against the real running game: 40% energy → exactly 400ms `activeAbilityTime`; jump correctly ends when energy reaches 0 (25 frames, ≈416ms); energy held at 0 through the 500ms delay window, only began recharging after; 100% energy still gives exactly 1000ms; a 0%-energy jump attempt is a correct no-op (ability state unchanged)

---

## 1.28.0 — 2026-08-24 19:45: Batch 33 — Player Vertical Movement

Previously flagged as needing a real scoping pass before implementing. User picked it as the next technical batch; scoping turned out simpler than the original note feared.

### Scoping findings
- Collision (`checkCollision`), spawn safety (`canSpawnAt` — checks distance from the top of the screen, not from the player), scoring (`v.y > canvas.height`, screen-exit not player-relative), and HUD/ability-bar positioning (CSS-positioned relative to the canvas container) were all already position-agnostic. None needed changes to support a variable player Y.

### Design decisions (not pre-specced — flagging in case any need correcting)
- Up/Down held continuously for free vertical movement, not lane-style discrete snapping. Reasoning: the original request said "no fixed height," which reads as free positioning; also, vertical movement doesn't have the "straddle two positions" cheese risk that motivated making horizontal steering snap-only (Batch 38)
- Range: `PLAYER_MIN_Y = 40` (near top — aggressive, closer to where traffic spawns, less reaction time) to `PLAYER_MAX_Y = 195` (near bottom — cautious, more reaction time)
- Speed: `VERTICAL_SPEED = 1.5` px/frame
- Default start position unchanged at `canvas.height - 35` (185), to preserve the existing game feel on launch — gives generous forward room, modest backward room
- Deliberately did not touch the scoring/multiplier model — scoring stays screen-exit-based rather than player-relative, to avoid an unrequested rebalance

### Implementation
- New `vKeys = { up, down }` state, set via keydown/keyup for `ArrowUp`/`ArrowDown` only (separate from the snap-based left/right handling, which stays keydown-only)
- Reintroduced a minimal `keyup` listener — removed entirely in Batch 38, now back just for these two keys
- `Player.update()` applies `this.y = Math.max(PLAYER_MIN_Y, this.y - VERTICAL_SPEED)` / `Math.min(PLAYER_MAX_Y, this.y + VERTICAL_SPEED)` while held
- `vKeys` reset in `launchGame()` in case a key was held through a game-over/menu transition

### Verification
- 20 frames of held Up moved the player exactly 30px (1.5 × 20); releasing stopped movement immediately
- 200 frames of held Down clamped exactly at the 195 max; 400 frames of held Up clamped exactly at the 40 min — both resistant to overshoot despite far more frames than needed to reach the bound

---

## 1.27.0 — 2026-08-24 19:15: Batch 27 — Holding arrow/A-D keys now keeps advancing lanes

- Removed the `!e.repeat` guard that blocked held-key repeat events entirely — previously only the initial physical press triggered a lane snap, holding did nothing further
- Replaced with a throttle: new `LANE_SNAP_REPEAT_MS = 220` constant and `lastLaneSnapTime` allow at most one repeat-triggered snap every 220ms, so holding a key advances lanes continuously but at a controlled pace, rather than the browser's native key-repeat rate blowing through several lanes almost instantly
- Applies uniformly to arrows and A/D, since both share the same snap logic since Batch 38
- Verified with a scripted sequence that forced `player.update()` between steps to simulate real frame timing (a background test tab throttles `requestAnimationFrame`, which would otherwise stall `player.targetX` and produce a false negative): press → advance, +50ms repeat → correctly blocked, +300ms repeat → correctly advances to the next lane

---

## 1.26.0 — 2026-08-24 19:00: Batch 35 — NPC lane changes made less frequent

- Normal car lane-changer chance: 45% → 25%
- Normal car re-roll timer: 30-110 frames (0.5-1.8s) → 90-240 frames (1.5-4s)
- Reckless re-roll timer: 35-90 frames (0.58-1.5s) → 70-170 frames (1.17-2.83s), both at construction and after each completed lane change
- Verified with scripted checks: 1000 normal-vehicle trials gave a 25.6% changer rate (target 25%); timer ranges landed exactly at [90,239] and [70,169] as designed

---

## 1.25.0 — 2026-08-24 18:30: Settings simplification — Game Mode, Semi Trucks, Weather removed; A/D now snaps to lanes

Direct user request: "there is no weather, semi trucks are always enabled, always accelerating speed and no A/D sensitivity bc you should be only able to switch lanes."

### Three settings locked to their existing value and removed from the menu
- Game Mode → always `'accelerating'`; the constant-speed code path is gone (the `currentSpeed < maxSpeed` speed-ramp check no longer has a mode condition)
- Semi Trucks → always enabled; the truck-spawn roll no longer checks `config.hasTrucks`
- Weather → removed entirely, not just locked. This one took the underlying feature with it: `drawRain()`, the `rainDrops` array, and its `+0.1x` multiplier bonus are all gone, since there's no weather system left to drive them

### A/D steering reworked from incremental to lane-snap
- Removed the A/D Sensitivity setting along with the incremental-slider mechanism it controlled: `handleInput()` (called every frame while a key was held), the `keys{}` object tracking held-key state, the low/medium/high sensitivity map, and the Shift-held burst multiplier
- A/D now fires through the exact same keydown-triggered, once-per-press `getArrowTarget()` lane-snap logic arrow keys already used — same Smart/Nearest mode behavior, same `!e.repeat` guard
- Relabelled the "Arrow Keys" setting to "Lane Switching" since it now governs both input methods
- This was the actual point of the request: lane switching is now the only way to steer with the keyboard — no more free incremental positioning between lanes

### Multiplier calc adjusted
- Mode/trucks conditionals collapsed to unconditional bonuses at their existing values (`+0.3` accelerating, `+0.2` trucks) so scores don't silently shift
- Weather's `+0.1x` bonus removed since the setting no longer exists

### Verification
- Fresh launch against the real running game: `config.mode === 'accelerating'`, `config.hasTrucks === true`, multiplier computes to 1.5x with menu defaults (matches manual math: 1.0 + 0.3 + 0.1 lanes + 0.2 trucks − 0.1 jump)
- Dispatched real `d` then `a` keydown events: slider snapped 50 → 64 → 36 (discrete lane jumps), not incremental steps
- No console errors on load; DOM check confirmed all 4 removed `<select>` elements (`gameMode`, `trafficTrucks`, `weatherSelect`, `keySensitivity`) no longer exist, and the settings grid shows exactly the 5 remaining controls

---

## 1.24.0 — 2026-08-24 18:15: Batch 20 — Pause Screen Overhaul + Bug Fix

Merged with the old Batch 26 (pause overlay stacking-black bug), since moving the pause screen to a DOM overlay resolves that bug structurally rather than needing a separate patch.

### New DOM pause overlay
- `#pauseHud` (same pattern as `#gameOverHud`): PAUSED title, Resume button, Menu button, own CSS background instead of a canvas fill
- New `setPaused(val)` helper centralizes every place that used to set `gamePaused` directly, keeping the DOM overlay in sync automatically
- Escape key now toggles pause alongside P (same activation condition)
- Resume button → `setPaused(false)`; Menu button → existing `exitToMenu()`

### Bug fixed structurally, not patched
- The old canvas-drawn overlay redrew its `rgba(0,0,0,0.62)` fill every frame without a `clearRect`, compositing on top of itself and drifting to solid black within about a second
- The `loop()` pause branch no longer draws anything — the last real game frame stays untouched on the canvas, with the DOM overlay sitting on top of it, styled once via CSS and never needing per-frame redrawing. The bug class (repeated non-cleared canvas fills) can't recur here since there's no longer any canvas drawing involved in the pause state at all

### Verification
- Tested against the real running game (not a reimplementation): P pauses, Escape un-pauses and re-pauses, Resume button un-pauses, Menu button while paused correctly returns to the menu and resets `gameActive`/`gamePaused` — no console errors
- Visual screenshot wasn't obtainable this session (Browser pane stopped compositing), so this relied on DOM-state verification only; worth a visual glance next time the pane is available

---

## 1.23.0 — 2026-08-24 18:00: Special ability locked to Jump

Direct user request: "the special ability is always jump (there is no ram and you can't disable it)."

- Removed the "Special Ability" setting (select with Disabled/Jump/Ram Shield) from the menu entirely
- `config.ability` is now hardcoded to `'jump'` in `launchGame()` instead of read from a select
- Multiplier calc simplified: the `none`(+0.5)/`jump`(-0.1)/`ram`(-0.2) branching collapsed to an unconditional `-0.1` (jump's old penalty)
- **Scoping decision, worth flagging**: only removed the setting and its config wiring. Left the Ram Shield mechanic itself in place but unreachable (`Player.useAbility()`'s ram branch, the ramming collision/score/sound logic, `ramsUsed` stat, leaderboard's `ram` label) rather than fully stripping it — full removal would touch the leaderboard's stored-entry schema and existing localStorage data, which felt like more than was asked for a setting-removal request. Say the word if you want it torn out completely too.
- Verified: fresh launch confirms `config.ability === 'jump'`, no console errors, ability bar still displays

---

## 1.22.0 — 2026-08-24 17:45: Jump now protects against ambulances

Direct user request, not a bug fix — this was previously a deliberate rule (ambulance = instant death regardless of ability).

- Reordered the collision branch in the main loop: `player.abilityState === 'jumping'` is now checked first, before the ambulance-specific instant-death branch, so a timed jump grants immunity to ambulances the same way it already did for normal traffic
- Ram Shield intentionally still doesn't protect against ambulances — unchanged, wasn't part of the request
- Removed the now-unreachable duplicate `abilityState === 'jumping'` branch further down the if-chain
- Verified against the actual running game loop (not a reimplementation): a jump-timed collision with an ambulance survives (`gameActive` stays `true`), a non-jumping hit still ends the game, and a ramming hit still ends the game

---

## 1.21.6 — 2026-08-24 17:30: NPC lane-change oscillation fixed

User reported cars change lanes back and forth. Root cause: reckless drivers (the only type that keeps re-rolling lane changes indefinitely) pick a fresh random direction on every decision with zero memory of which lane they just came from, so lane2→lane1→lane2→lane1 was a real possibility every time both directions happened to be open.

- New `this.previousLane` field, set to the pre-change lane every time a lane change completes
- The lane-change direction options now exclude `previousLane` — with a fallback: if excluding it leaves zero options (e.g. at the very edge of the road, where only one direction physically exists), the exclusion is dropped for that decision so the vehicle doesn't get permanently stuck
- `previousLane` clears after being read once, so it only ever blocks the single decision immediately following a completed change, not future ones
- Verified with a scripted 30-decision run for a reckless vehicle on a 6-lane road: 5 reversals occurred total, and a follow-up automated check confirmed every single one happened exactly at a road edge (lane 0 or lane 5) — zero interior back-and-forth

---

## 1.21.5 — 2026-08-24 17:15: Speed floor now scales with game speed — "cars look reversed" report

Raising the flat floor to 0.5 in 1.21.4 wasn't enough — user reported slow vehicles now look like they're driving in reverse.

- Root cause: the road markings scroll at `currentSpeed`, which grows from 1.2 to 4.5 over a run. A flat floor (0.2, then 0.5) stays fixed while the scroll rate keeps climbing, so at higher game speeds a slow vehicle's speed falls far enough behind the scroll rate that it visually reads as sliding backward through the dashes — even though its absolute screen position never actually decreases
- Fixed by making the floor proportional instead of flat: `speed = Math.max(currentSpeed * 0.35, currentSpeed - this.speedOffset)` — a vehicle's speed can never drop below 35% of the current road-scroll rate, at any point in a run
- Verified: worst-case truck (`speedOffset = 2.0`) held exactly a 0.35 speed-to-scroll ratio at base speed (1.2) and mid speed (2.5), where the floor is the binding constraint; at max speed (4.5) the raw formula already exceeds the floor, giving a 0.56 ratio

---

## 1.21.4 — 2026-08-24 17:00: Speed floor raised — "cars not moving" report

User confirmed the Batch 19 min-speed clamp existed but was still seeing vehicles that looked stalled.

- Floor raised from `0.2` to `0.5` px/frame — `0.2` was technically non-negative (fixed the original backward-drift bug) but nearly imperceptible: a truck with a near-max `speedOffset` (2.0) at base game speed (1.2) was pinned there, taking ~18s to cross the screen
- Verified: same worst-case truck now moves at `0.5` px/frame, ~7.3s to cross the screen

---

## 1.21.3 — 2026-08-24 16:45: Reckless two-lane skip made rare

- Rate lowered from 20% to 5% (`Math.random() < 0.2` → `< 0.05`) per user feedback ("make switching two lanes very rare")
- Verified with 3000 scripted trials: exactly 5.0% two-lane rate

---

## 1.21.2 — 2026-08-24 16:30: Lane-change speed still too fast — abandon eased motion, restore constant velocity

Retuning the eased/LERP motion in 1.21.1 wasn't enough — user asked for it to go back to how it felt before Batch 19 entirely, not just slower easing.

- Removed `laneChangeLerp` and the `this.x += gap * lerp` eased movement
- Restored the original constant-velocity style (`this.x += Math.sign(gap) * this.laneChangeSpeed`), the same movement math Batch 19 replaced
- Kept the "randomized lane change speed" requirement by randomizing the new `laneChangeSpeed` field per vehicle around the old fixed constants instead of using a single fixed value: normal 0.2-0.3 (was fixed 0.25), reckless 0.35-0.5 (was fixed 0.4)
- Verified by simulating a full lane crossing at the old fixed 0.25 speed: 123 frames (~2.05s), matching the original pre-Batch-19 pacing exactly

---

## 1.21.1 — 2026-08-24 16:15: Batch 19 feedback fixes — revert off-center cars, slow down lane changes, fix arrow-key direction bug

### Bell-curve lane offset reverted
- Cars looked off-center in a way that didn't read well — removed `this.laneOffset` entirely; `Vehicle` spawn `x` and lane-change `destX` are back to exactly centered, matching pre-1.21.0 behavior

### Lane-change speed slowed down
- The eased `laneChangeLerp` values from 1.21.0 were noticeably too fast (reckless 0.10-0.16, normal 0.06-0.10 — converged in as little as ~0.3s)
- Retuned to reckless 0.04-0.07, normal 0.02-0.035, closer to the original ~2-second-per-lane pacing the constant-velocity version had

### Player arrow-key direction bug fixed (found via this same feedback, unrelated to the NPC changes above)
- Reported: from the default starting position, pressing either arrow key moved the car right — left never worked
- Root cause: in `getArrowTarget()`'s 'smart' mode, the default starting position for an even lane count sits exactly on a lane boundary (e.g. 4 lanes: exactly between lane 1 and lane 2), equidistant from both neighboring lane centers. `Math.floor(relX / lw)` always resolves an exact boundary toward the lane on the right, so `curLane` came out the same regardless of which direction was pressed — and since the position wasn't within either lane's "safe zone," the code always centered into that same (right) lane
- Fixed by detecting the exact-boundary case (`Math.abs(relX - curLane * lw) < 0.5`) and breaking the tie using the pressed direction, so left correctly resolves to the lane on the left and right to the lane on the right
- Verified: from the exact starting position, `getArrowTarget(-1)` now returns a target left of start and `getArrowTarget(1)` a target right of start

### Verification (scripted)
- Confirmed 200 freshly-constructed vehicles all spawn at the exact centered `x` (no offset)
- Confirmed 20 sampled `laneChangeLerp` values per type fall within the new tuned ranges
- Confirmed both arrow directions move the correct way from the default start position

---

## 1.21.0 — 2026-08-24 15:45: Batch 19 — NPC Vehicle Behavior Overhaul

Merged with the old Batch 24 (NPC lane-change easing) since both live in `Vehicle.update()`.

### Bell-curve lane position
- `this.laneOffset` computed once per vehicle from an Irwin-Hall approximation (average of 3 `Math.random()` calls, recentered to a signed bell shape), clamped to `(laneWidth - width)/2 - 1` so it never pokes into a neighboring lane
- Applied to both the spawn `x` and every lane-change destination `destX`, so a vehicle keeps one consistent driving line for its whole lifetime instead of re-centering on every lane change

### No overlap during lane changes
- New `laneClearForMerge(lane, y, height, self)`: false if any other vehicle already in `lane` is within a 26px vertical safety buffer
- Combined with the existing `laneReservedForAmbulance` check inside the lane-change direction options in `Vehicle.update()`

### Speed floor
- `let speed = Math.max(0.2, currentSpeed - this.speedOffset);` — previously a vehicle with a large positive `speedOffset` (trucks especially, up to +2.0) could compute a negative or zero speed early in a run when `currentSpeed` was still low, making it appear to drift backward up the screen

### Eased, randomized lane-change motion (absorbs old Batch 24)
- Replaced the fixed constant-velocity movement (`0.4`/`0.25` px/frame) with LERP-style easing: `this.x += gap * this.laneChangeLerp`
- `laneChangeLerp` is randomized per vehicle at construction — reckless 0.10-0.16, normal 0.06-0.10 — so lane changes glide at a natural variety of speeds instead of every vehicle of a type moving identically

### Reckless 20% two-lane skip
- When a reckless driver's lane-change roll lands, there's now a 20% chance it attempts a 2-lane jump instead of 1
- The 2-lane target is independently validated (bounds, ambulance reservation, overlap) before committing — falls back to the already-validated 1-lane move if the 2-lane target isn't clear

### Verification (scripted, not full visual runs)
- Bell curve: 2000 samples stayed within the computed bound; 56% landed within ±2px of center vs. ~27% expected from a uniform distribution — confirms genuine bell shape, not uniform
- Overlap: a vehicle placed near another in the only available adjacent lane correctly failed to find any lane-change option
- Speed clamp: hit exactly the 0.2 floor when given a near-maximum `speedOffset` at base game speed
- `laneChangeLerp` variety: 20/20 trials produced distinct values
- Reckless 2-lane skip: 2000 trials → 21.1% two-lane rate (target 20%)

---

## 1.20.1 — 2026-08-24 15:15: Ambulance lane-reservation follow-up fix

Found via user playtesting: an ambulance still drove through another car after Batch 17. Root cause — the lane clear in 1.19.0 was a one-time snapshot at the moment of queueing, and `canSpawnAt` only blocked *new* vehicle spawns; neither stopped a car already in an adjacent lane from independently rolling a lane-change decision into the ambulance's reserved lane during the countdown.

- New `laneReservedForAmbulance(lane)` helper: true while a lane has a pending ambulance OR a live ambulance currently on screen
- `canSpawnAt()` now uses this helper (was checking `pendingAmbulances` directly — same behavior, now also covers live ambulances)
- `Vehicle.update()`'s lane-change direction roll now excludes any adjacent lane that's reserved, so cars physically cannot choose to merge into an ambulance's path
- Verified with 500 scripted trials from an adjacent lane: reserved lane chosen 0/500 times, open lane chosen 500/500 (confirms cars aren't getting stuck with no valid option)
- Known remaining gap, not fixed: a car already mid-turn-signal (`changingState === 'indicator'`) with a target lane that becomes reserved in the same window will still complete that lane change — narrow timing window, not the reported issue

---

## 1.20.0 — 2026-08-24 15:00: Batch 18 — Ability Bar Overhaul

### READY! button removed
- Deleted the HTML button, `.ability-ready-btn` CSS, `@keyframes blink`, the `abilityBtn` JS reference, and its click listener

### Energy bar is now a DOM overlay, not canvas-drawn
- New `#abilityBar` / `#abilityBarFill` elements, positioned top-right of the canvas via `position:absolute` (mirrors the pause button's top-left placement) — `pointer-events:auto` on just this element (unlike the rest of `#gameHud`, which is `pointer-events:none`), so it's tappable/clickable without needing a dedicated button, and without blocking canvas touch-drag steering elsewhere
- This also restores a way to trigger abilities on mobile now that the only tap target (the button) is gone
- Removed the old canvas-drawn version (`ctx.fillRect`-based bar in the main `loop()`)
- Fill width and color (blue while charging, red while an ability is active) updated every frame in `Player.update()`

### "Marching ants" ready indicator
- New `.ability-bar.ready` CSS class — four animated `linear-gradient` stripes (one per edge) create a crawling dashed border, replacing the button's old blink animation as the "it's ready" cue
- Toggled based on `energy >= 100 && abilityState === 'idle'`
- Tuned padding/stripe size (1px→3px) after an initial pass rendered too thin to read clearly at the bar's 70×14px size

### Recharge scales with speed
- `this.energy += 0.25` (fixed) → `this.energy += 0.25 + speedRatio * 0.25` (0.25/frame at base speed — unchanged from before, 0.5/frame at max speed), reusing the `speedRatio` already computed for the speed-scaled steering LERP
- Verified via scripted checks: 10 frames at base speed → +2.5 energy; 10 frames at max speed → +5.0 energy

---

## 1.19.0 — 2026-08-24 14:30: Batch 17 — Ambulance Rework

- Spawn rate halved-plus: `roll < 0.05` → `roll < 0.02` (ambulances are now rarer)
- Queueing an ambulance now clears its lane first: `vehicles = vehicles.filter(v => v.lane !== lane)` runs right before the `pendingAmbulances.push()`, so the ambulance gets a straight run instead of possibly plowing through cars already ahead of it
- `canSpawnAt(lane)` now checks `pendingAmbulances` first and returns `false` immediately if that lane already has a countdown running, so no new traffic spawns into a lane that's about to be an ambulance's path
- Verified with scripted checks (not full visual runs, per token-conservation preference): confirmed the target lane is cleared while an unrelated lane's vehicle survives, confirmed `canSpawnAt` blocks the ambulance's lane but not others

---

## 1.18.0 — 2026-08-24 14:00: Batch 16 — Road Scenery Fix

### Left side flashing fixed (root cause)
- The 14-slot procedural scenery (tall grass/bush/tree) indexed `LEFT_SLOTS[(baseSlot + ti) % numSlots]`, where `ti` is the loop counter and `baseSlot = floor((roadOffset%336)/24)`
- Traced the bug by hand: every time `pixOff` (`roadOffset % 24`) wraps past 0 — about every 24px of scroll — the loop's `ti` values all shift up by 1 to keep drawing the same screen rows, while `baseSlot` also increments by 1 at that same moment. Their sum jumps by +2 instead of staying constant, so a physical tile's slot index (and therefore its type) changed every ~24px, reading as trees/bushes flickering mid-scroll
- Fixed by computing `slotOffset = ti - baseSlot - 1` instead, which cancels out exactly at the wrap (derivation: `ly - roadOffset` is always an exact multiple of the tile period, and equals `tilePeriod * (ti - baseSlot - 1)`, so this quantity is the tile's true world-space identity, invariant under scrolling)
- Verified with a scripted check: simulated `roadOffset` from 0 to 400 (crossing multiple 24px wraps and the outer 336px wrap), tracked the tile that starts at y≈100, confirmed its computed type never changes — 0 issues found
- Also reduced scenery density per the original plan: `LEFT_SLOTS` changed from 7 grass/4 bush/3 tree to 9 grass/3 bush/2 tree

### Right side hedge redesigned
- Removed the two-layer teal bush-square grid (`#28b5b5`/`#1a9090`, periods 16 and 24) that read as flashing/checkerboard-like while scrolling
- Replaced with the same world-position slot system as the left side (same `slotOffset` formula, so no risk of the same flashing bug), alternating between two organic hedge-clump shapes (`#1f5f49`/`#2a7359` fuller clump, `#256b52`/`#2f8065` smaller clump) drawn over the solid dark hedge base — clumps overlap the base fully so there are never gaps, reads as one continuous hedge wall instead of a repeating grid

---

## 1.17.0 — 2026-08-24 13:30: Batch 15 rework — scale everything together, not just vehicles

User clarified the original ask: at high lane counts, EVERYTHING should visually scale down together (cars, background scenery, lane dividers, road), not just vehicle sprites. Replaces the 1.16.0 per-vehicle-sprite scaling with a structural fix.

### Road + canvas grow instead of vehicles shrinking
- New `applyLaneLayout(lanes)`, called from `launchGame()` right after `config.lanes` is set: for lanes ≤7, road width stays the original fixed `124` (unchanged, byte-for-byte same as before Batch 15); for 8–10 lanes, road width becomes `17 * lanes` so every lane always keeps the same ~17px width the game already had at 7 lanes — canvas resolution grows to `roadWidth + 36` (36 = both 18px side margins) and `canvas.style.aspectRatio` is updated to match
- Because the canvas is still displayed at the same fixed CSS size (`width:100%; max-width:480px`), the browser's own scaling now shrinks the wider canvas back down — road, lane dividers, curbs, background scenery, and vehicles all shrink together as one image, instead of each element needing its own scale logic
- `ROAD_BORDER_LEFT`/`ROAD_BORDER_RIGHT`/`ROAD_WIDTH` changed from `const` to `let`, recomputed each launch
- Hardcoded curb/hedge pixel offsets (`142`, `146`, `148`, `151`, `155`, `16`) rewritten relative to `ROAD_BORDER_LEFT`/`ROAD_BORDER_RIGHT` so they track the new dynamic road width instead of assuming the old fixed 160px canvas

### Reverted the 1.16.0 per-vehicle scaling
- Removed `computeVehicleWidth()`, the `width` parameters on `drawPixelCar`/`drawPixelTruck`/`drawPixelAmbulance`, and their `ctx.scale()` transforms — no longer needed since lane width now structurally never drops below 17px (vs. down to 12px before), so native 14px vehicles always fit without shrinking
- `Player.width` and `Vehicle.width` reverted to a flat `14`

---

## 1.16.0 — 2026-08-24 13:00: Batch 15 — Lanes Up to 10 (superseded by 1.17.0)

### Road Lanes setting extended to 6–10
- Added `<option>`s for 6, 7, 8, 9, and 10 lanes to the `laneCount` select
- Multiplier penalty extended: `-0.1x per lane above 4` (was previously fixed at `-0.1x` for exactly 5 lanes, with no adjustment above that)

### Vehicles narrow to fit tight lanes (8+ lanes)
- New `computeVehicleWidth(lanes)` helper: returns the native 14px width unchanged for lanes ≤7 (still fits with margin), and shrinks down to a floor of 8px for lanes 8–10 so vehicles never overlap their neighboring lane
- Applied to both `Player` and `Vehicle` hitbox width (previously hardcoded to `14` in both constructors)
- `drawPixelCar`, `drawPixelTruck`, and `drawPixelAmbulance` now accept a `width` parameter and apply a horizontal `ctx.scale()` transform around the sprite's own origin when it differs from the native 14px — the pixel art itself is still drawn with its original hardcoded offsets, just visually compressed to match, so no per-pixel redrawing was needed

### Found while testing (not fixed, logged as Batch 26)
- Pausing the game restacks the semi-transparent dark overlay every frame without clearing first, so the screen drifts to solid black within about a second instead of staying at 62% over the frozen last frame

---

## 1.15.1 — 2026-08-24 12:30: Steering feel — slower at game start

- Base steering LERP factor lowered from `0.08` to `0.045` (max speed cap unchanged at `0.18`) — lane switching at the start of a run was still too fast

---

## 1.15.0 — 2026-08-24 12:00: Batch 14 fixes — Lane-snap bug + speed-scaled steering

### Nearest/Smart arrow-snap bug fixed
- `getArrowTarget()` was computing the current lane reference from `player.x` (the live, still-animating position) instead of `player.targetX` (the last commanded destination)
- Because the player's position only reaches its target asymptotically (~0.3-0.5s), pressing an arrow key again before that settled re-read a position that hadn't caught up yet, so it kept re-targeting the same adjacent lane instead of advancing further — outer lanes were effectively unreachable at normal tap speed
- Fixed by reading `player.targetX` instead of `player.x` in the carCenterX calculation
- Found a second, smaller edge case while testing: the slider-percentage round trip (px → % → px) can leave `targetX` a fraction of a pixel off its true lane center, which flipped the `cx < carCenterX` / `cx > carCenterX` comparisons in "nearest" mode and made it re-select the current lane instead of the next one. Added a 1px tolerance (`EPS`) to those comparisons

### Player steering LERP now speed-scaled, slower overall
- Replaced the fixed `0.25` LERP factor with `0.08 + speedRatio * 0.10` (0.08 at base speed, capped at 0.18 at max speed), where `speedRatio` is `currentSpeed` normalized between `baseSpeed` and `maxSpeed`
- Applies uniformly to every input method (arrow snap, A/D keys, slider drag, touch drag, tilt) since they all funnel through the same `controlSlider.value` → `targetX` → LERP path in `Player.update()`
- Result: steering feels more deliberate at low speed, quicker (but never instant) as the game speeds up; a new arrow press mid-transition still redirects immediately from the current position (already true of LERP, unaffected by this change)

---

## 1.14.0 — 2026-08-24 01:00: Batch 14 — Steering Overhaul

### Auto-lane-center removed
- Removed setting UI, config fields (`autoCenter`, `autoCenterStrength`), update loop logic, localStorage key, and multiplier penalty
- `sliderMouseDown` tracking also removed (was only needed to guard auto-center)

### Arrow keys now snap to lane centers
- `ArrowLeft`/`ArrowRight` no longer do incremental slider adjustment
- On each press (not on hold repeat), calls `getArrowTarget(dir)` → sets slider to snap position → car LERPs smoothly via existing code
- **Smart mode** (default): if car body is safely within current lane (`|offset| ≤ (laneWidth − carWidth) / 2`), arrow jumps to adjacent lane; otherwise centers in current lane first
- **Nearest mode**: always moves to the nearest lane center strictly in the pressed direction; if car center is between lanes, presses each direction to the nearest center on that side
- Choice persisted to `localStorage` (`arrowMode`)

### A/D keys unchanged
- Still do incremental slider steering with sensitivity + Shift burst
- Key Sensitivity setting relabelled "A/D Sensitivity" and tooltip updated

---

## 1.13.0 — 2026-08-24 00:30: Batch 13 — Post-Testing Fixes Round 2

### Crash screen text fixed
- `CRASHED!` and score now rendered via DOM `#gameOverHud` overlay (CSS-sharp at any display size)
- Canvas game over branch now only draws the dark background rect; all `ctx.fillText` calls removed
- `gameOverHud.style.display = 'flex'` on crash, `'none'` on retry/exit

### Auto-center no longer fights mouse drag
- Added `sliderMouseDown` flag: set `true` on slider `mousedown`, `false` on window `mouseup`
- `noInput` guard in auto-center now includes `&& !sliderMouseDown`

### Ambulance warning time reduced and speed-scaled
- Base warning: 150 frames (~2.5s at 60fps) instead of 180
- Scales: `max(60, round(150 * baseSpeed / currentSpeed))` → at max speed ≈ 1s warning

### Road left side variety
- Replaced repeating grass dots + fence posts + flowers with a 14-slot procedural system
- Each 24px-tall slot draws one of three types: small tree, bush/shrub, or tall grass tufts
- Different shapes, not cloned — pattern cycles through 14 unique positions over 336px

### Road jitter fixed (root cause)
- `roadOffset %= 40` → `roadOffset %= 336` (= LCM of all tile periods: 16, 24, 28)
- Previously: wrap at 40 caused all tile loops to jump at mismatch (e.g. 40 % 24 = 16 → 16px jump)
- Now all periods divide 336 evenly → no jump on wrap

### Pause button redesigned
- Now a compact 26×26px square button with ⏸ unicode pause symbol
- Removed wide padding and thick border; looks like an actual pause icon

### Up arrow key detached
- `ArrowUp` and `ArrowDown` now call `e.preventDefault()` in keydown when game is active
- Previously browser used arrow keys to control focused `<input type=range>`, causing phantom steering

---

## 1.12.0 — 2026-08-23 23:30: Batch 12 — Polish & Bug Fixes

### Yellow lights bug fixed
- Removed reckless speed-line rects (`fillRect` at `y-5` and `y-9`) from `Vehicle.draw()` — were displaying as 3 yellow buttons above car sprites

### Ambulance 3-second pre-warning
- New `pendingAmbulances = [{lane, timer}]` queue; ambulance spawns are intercepted instead of direct `vehicles.push()`
- 180-frame (3s @ 60fps) countdown per pending ambulance; flashing red lane overlay + red top bar + white `!` pixel drawn in that lane
- Actual vehicle spawns when timer reaches 0

### Lane changes slower
- Normal car indicator: 50 → 90 frames (signal visible for 1.5s)
- Reckless car indicator: 8–18 random → fixed 60 frames (still shorter than normal but visible)
- Movement speed: 0.8 → normal cars 0.25 px/frame, reckless 0.4 px/frame

### Blurry HUD text fixed
- Score, multiplier, and ambulance warning moved from `ctx.fillText()` on the 160px canvas to a DOM `#gameHud` overlay (positioned absolute over canvas-container)
- DOM text renders at full CSS resolution — sharp at any display size
- `gameHud.style.display` toggled in launchGame, exitToMenu, and crash handlers

### Road side variety
- Left grass: wider grass patch per tile, fence posts every 24px (dark brown), yellow flower dots every 40px
- Right hedge: second darker bush layer (`#1a9090`) at 24px offset period for depth

### Road jiggling fixed
- Added `Math.floor()` to `roadOffset % period` in left curb, right curb, bush, and lane divider tile loops

---

## 1.11.0 — 2026-08-23 22:45: Batch 11 — Post-Testing Fixes

### Canvas display size fix
- Root cause: `.game-container { width: 100% }` resolved against itself in a flex-shrink context, collapsing to content (button) width
- Fix: changed to `width: 506px; max-width: calc(100vw - 40px)` — definite pixel width, scales down on mobile

### Reckless driver direction
- Changed `speedOffset` from `-(0.2–0.7)` (oncoming, come at player) to `+(0.3–0.8)` (same-direction, player approaches and overtakes while they weave)

### Background music
- Web Audio lookahead scheduler at 130 BPM, 16-step pattern (A-minor pentatonic)
- Instruments: kick drum (sine pitch-drop), hi-hat (filtered noise), sawtooth bass, square melody (2× octave)
- `startMusic()` called on game launch; `stopMusic()` on crash and exit-to-menu
- Volume = `config.soundVolume × 0.2` (quiet background; uses existing sound volume setting)

---

## 1.10.0 — 2026-08-21 20:45: Batch 10 — Gameplay Balancing

### Reckless drivers toned down (10.1)
- Speed: `speedOffset` changed from -0.5–-1.5 → -0.2–-0.7 (significantly slower relative to traffic)
- Lane change frequency: timer changed from 10–50 frames → 35–90 frames (much less frantic)
- Indicator: timer changed from 0–7 frames → 8–18 frames (still short, but now always visible for at least a few frames)
- Both the constructor and the post-lane-change timer reset updated

### Slower game start (10.2)
- `baseSpeed` + `currentSpeed` init: 2.0 → 1.2 (calmer opening)
- Acceleration rate: 0.0008 → 0.0005 per frame (smoother ramp-up)
- `maxSpeed`: 5.5 → 4.5 (peak is still challenging, not physically insane)

### Better always-a-path guarantee (10.3)
- Same-lane spawn block: extended from `v.y < 60` → `v.y - vH < 140` where `vH` is 56 for trucks, 16 for others — accounts for truck body height so a tall truck doesn't get spawned on top of
- All-lanes blockage check: extended from `v.y < 65` → `v.y < 140` — catches vehicles in the lower half of the road before they reach the player

---

## 1.9.0 — 2026-08-21 20:30: Batch 9 — Settings UI Polish

### Two-column settings layout (9.1)
- Settings groups (Game Mode through Key Sensitivity) wrapped in `.settings-grid`
- At ≥600px: 2-column CSS Grid with 20px column gap; `.settings-panel` max-width raised to 640px
- Car Color, multiplier box, and Start/Leaderboard buttons remain full-width below the grid
- Mobile stays single column (default `grid-template-columns: 1fr`)

### Sound volume slider (9.2)
- Replaced "Enabled/Disabled" select with `<input type="range" min="0" max="1" step="0.05">` (default 0.7)
- Label shows live percentage (e.g. "70%"), updates on drag
- `config.soundVolume` applied to all Web Audio gain nodes; `config.soundEnabled` derived from `volume > 0`
- Saved to localStorage (`soundVolume`), restored on page load

### Auto-lane-center strength slider (9.3)
- Replaced "Off/On" select with `<input type="range" min="0" max="1" step="0.1">` (default 0)
- Label shows "Off" at 0, decimal value (e.g. "0.3") above 0
- Pull factor = `autoCenterStrength × 0.4` (0.1 → same 0.04 as before; 1.0 → strong 0.4)
- Multiplier penalty (-0.1×) only when > 0; saved to localStorage (`autoCenterStrength`)

### Info tooltips (9.4)
- `data-tip` attribute added to 9 setting groups (all except Sound and Car Color)
- JS injects ℹ icon at end of each label; hover (desktop) or tap (mobile) shows tooltip
- Tooltips explain what each setting does and its multiplier effect
- Tap outside to close; only one tooltip open at a time

---

## 1.8.0 — 2026-08-21 20:15: Batch 8 — Key Sensitivity Setting + Shift Modifier

### Key Sensitivity setting
- Added "Key Sensitivity" select to the menu (Low / Medium / High)
- Maps to `slideIncrement` values: Low = 1.5, Medium = 3, High = 5
- Preference persisted to `localStorage` (`keySensitivity` key); restored on page load

### Shift key burst modifier
- When Shift is held during arrow/A/D steering, `increment` is multiplied by 2.5×
- Examples: Low+Shift = 3.75, Medium+Shift = 7.5, High+Shift = 12.5
- Allows fine default control with a burst option when needed

---

## 1.7.0 — 2026-08-21 20:00: Batch 7 — Canvas Size, READY Button Reposition, Retry Button

### Canvas size
- Canvas `max-width` increased from `320px` → `480px`; `aspect-ratio: 160/220` preserved so pixelated upscaling stays crisp
- `.game-container` `max-width` increased from `342px` → `506px` to contain the larger canvas
- On mobile, `width: 100%` continues to shrink both naturally

### READY button moved to footer
- Removed `position: absolute; top: 20px; right: 20px` from `.ability-ready-btn` — button no longer overlaps gameplay
- Moved `<button id="abilityBtn">` from canvas-container into the game-footer, directly below the slider
- Set `width: 100%; margin-bottom: 5px` so it spans the full footer width and stays touch-friendly

### Retry + Menu on game over
- Added `<button id="retryBtn">RETRY</button>` as primary game-over action (full-width blue button)
- Renamed `returnBtn` text from "Return to Settings" → "Menu" (secondary, gray style)
- Both wrapped in `#gameoverBtns` div; shown on crash (`display: flex`), hidden during active game and on menu exit
- `retryBtn` click calls `launchGame()` — restarts immediately with same settings (config not re-read from selects since menu is not visited)
- Game-over canvas text updated: "Use RETRY or MENU below."

---

## 1.6.0 — 2026-08-21 19:30: Batch 6 — Pause, Auto-center, Sound, Night Mode, Rain

### Pause
- `gamePaused` state variable; toggled with P key or the `| |` button (top-left of canvas)
- Loop restructured: `clearRect` moved after view/pause checks — last game frame stays visible under the pause overlay
- Pause overlay: 62% dark + "PAUSED" text + "P / tap button to resume" hint
- `gamePaused` reset to `false` on both game start and `exitToMenu`
- Pause button shows on game start, hides on exit to menu
- Space bar ability use guarded: only fires when `!gamePaused`

### Auto-lane-center
- New setting: "Auto-lane-center: Off / On (-0.1x)"
- When on and no keyboard/touch/tilt input detected: slider is gently pulled (0.04 factor) toward the nearest lane center
- Player can override at any time — active steering wins immediately
- Excluded when tilt steering is active

### Sound effects (Web Audio API — no external deps)
- New setting: "Sound: Enabled / Disabled"
- `audioCtx` created lazily on first sound; auto-resumed if suspended (handles browser autoplay policy)
- `playSound('crash')` — white noise burst (0.35s), played on any game-ending collision
- `playSound('jump')` — ascending square-wave tone (220→660Hz, 0.18s), played on jump activation
- `playSound('ram')` — descending sawtooth thud (110→40Hz, 0.2s), played each time a vehicle is rammed

### Night Mode
- New setting: "Night Mode: Off / On (+0.2x)"
- After drawing player, a 72% dark-navy overlay covers the canvas
- Radial gradient "headlight glow" drawn in front of the player car (yellow-white, fades at radius 68)
- HUD and rain drawn on top of the overlay (remain readable)

### Rain
- New setting: "Weather: Clear / Rain (+0.1x)"
- `drawRain()` maintains pool of 65 drops; each is a short angled line (speed 4–7px/frame)
- Drawn last in the loop — falls over all game elements including game over overlay
- Drops pause with the game (`gamePaused` check)
- `rainDrops` array reset on each game start

### Multiplier changes
- Night Mode: +0.2x
- Rain: +0.1x
- Auto-lane-center: -0.1x
- Change listeners added for all three new selects

---

## 1.5.0 — 2026-08-21 19:15: Batch 5 — Local Score Ranking

### Score tracking
- Per-game session tracks: `jumpsUsed`, `ramsUsed`, `gameStartTime` (reset on each `launchGame()`)
- `jumpsUsed` increments inside `Player.useAbility()` on jump activation
- `ramsUsed` increments each time a vehicle is destroyed by the ram shield
- Time survived = `(Date.now() - gameStartTime) / 1000` at game over
- Fixed potential double-save bug: vehicle loop now breaks on `!gameActive`

### Score saving (`saveScore()`)
- Called on every game over (normal crash + ambulance collision)
- Saves to `localStorage` key `highscores` as JSON array
- Each entry stores: score, timeSurvived, multiplier, mode, lanes, ability, hasTrucks, jumpsUsed, ramsUsed, date, time, isLatest
- Most recent entry flagged `isLatest: true`; all previous entries set to `false`
- Array sorted by score descending, trimmed to top 10

### Leaderboard view (VIEW 3)
- New `leaderboardView` div (`#leaderboardView`)
- Accessible via "View Leaderboard" button on menu screen
- Each entry shows: rank, score, time survived, date/time, config (lanes/mode/ability/multiplier) and stat details (jumps, cars rammed, trucks)
- Latest score entry highlighted with blue left-border + blue tint
- Scrollable list (max-height 320px)
- "Back" button returns to menu; "Clear All" wipes localStorage and refreshes view

### Menu button
- "START VERIFICATION" renamed to "START GAME" (cleanup from CAPTCHA removal)

---

## 1.4.0 — 2026-08-21 19:00: Batch 4 — Traffic Overhaul

### New vehicle types
- **Normal cars** — 5-color palette, 45% chance to change lanes with full turn signal (50 frames), speed ±mix
- **Reckless drivers** — hot/warm color palette (orange, yellow, red, pink), always change lanes, very short/no indicator (0–7 frames), move faster (speedOffset -0.5 to -1.5), keep changing lanes after first change (not just once)
- **Ambulance** — white with red cross + red stripe, alternating red/blue flashing roof lights, extremely fast (speedOffset -2.5 to -3.0), instant death on contact regardless of jump/ram ability; blinking `! AMBULANCE !` HUD warning when on screen
- **Trucks** — 4 cab colors, slow (speedOffset +0.8 to +2.0), no lane changes (unchanged behavior, new colors)

### Speed variation
- Normal: speedOffset -0.5 to +1.0 (some faster, some act like obstacles)
- Reckless: always faster than road scroll
- Trucks: noticeably slow, clog lanes
- Ambulance: very fast, only on screen briefly

### Spawn rates (per spawn event)
- Ambulance: 5%, Reckless: 20%, Truck: 20% (if enabled), Normal: 55%

### Speed lines
- Reckless cars draw 3 small golden streak lines above them (trailing in direction of movement)

### `drawPixelAmbulance()` function added

### Collision changes
- Ambulance now triggers instant game over regardless of player ability state (jump / ram do not protect)
- Ambulance explosion uses both red and blue particles

---

## 1.3.0 — 2026-08-21 18:45: Batch 3 — Car Color Customization

- Added 10-color swatch picker in the settings menu (Blue, Red, Green, Orange, Purple, Pink, Cyan, White, Gold, Navy)
- Selected color is applied to the player car in `drawPixelCar()` — replaces hardcoded `#4a75a0`
- Crash explosion particles also use the chosen player color
- Choice persists across sessions via `localStorage` (`playerColor` key)
- Swatch picker shows which color is currently selected (white border + blue glow ring + scale)
- CSS: `.color-picker` (flex wrap, 8px gap), `.color-swatch`, `.color-swatch.selected`

---

## 1.2.0 — 2026-08-21 18:30: Batch 2 — Mobile Support

### Responsive layout
- Canvas: removed fixed `320px×440px`, now uses `width: 100%; max-width: 320px; aspect-ratio: 160/220` — scales down on small screens while staying crisp (pixelated upscaling preserved)
- `.game-container`: added `width: 100%; max-width: 342px; box-sizing: border-box`
- `.settings-panel`: changed `width: 320px` → `width: 100%; max-width: 320px`
- Ability button: increased padding and added `min-height: 44px` (meets mobile tap-target size)

### Touch drag steering
- Added `touchstart` / `touchmove` / `touchend` listeners on the canvas
- Dragging finger left/right across the canvas updates the slider proportionally to the drag distance vs. canvas width
- `{ passive: false }` used so `e.preventDefault()` can block scroll while dragging

### Tilt (gyroscope) steering
- Added "Tilt Steering" option in settings menu (Disabled by default)
- `deviceorientation` event listener tracks `gamma` (left/right device tilt) at all times
- When tilt is enabled: `±25°` tilt range maps to full slider travel, with `±3°` deadzone to prevent drift
- `enableTilt()` async function handles iOS 13+ `DeviceOrientationEvent.requestPermission()` call automatically when game starts
- On Android/desktop: permission is not required, tilt activates immediately

---

## 1.1.0 — 2026-08-21 18:00: Batch 1 — Core Fixes & Polish

### CAPTCHA box removed
- Removed `.captcha-window` wrapper div and all its CSS (fake browser-window border/shadow/bg)
- Removed `.captcha-header` block ("Steer the car and don't crash" heading) from HTML and CSS
- Renamed `.captcha-footer` → `.game-footer` with dark background (`#1a202c`) to match theme
- Updated `.slider-wrapper` colors to dark theme (`#2d3748` bg, `#4a5568` border)
- Updated `.canvas-container` background from light gray to dark (`#0f141d`)
- Added `.game-container` CSS replacing `.captcha-window` (clean border, no fake CAPTCHA look)

### Road animation fix
- Fixed left-side grass animation: was broken (position calculation was wrong, dots flew around); now uses proper scrolling loop matching how lane dividers work
- Added left curb strip at x=16 (alternating dark/light tiles, mirroring the right curb at x=142)
- Both curbs now scroll in perfect sync with road

### Car movement smoothing
- Increased player LERP factor from `0.12` → `0.25` (car reaches target position ~2x faster, fewer "stuck" frames between pixel jumps)
- Increased keyboard slide increment from `2.4` → `3` (more responsive arrow key / A&D steering)

---

## 1.0.0 — 2026-08-21 (baseline)
Initial version of the game as inherited from previous development session.

**Features present at baseline:**
- Single HTML file, no external dependencies
- Menu screen with settings: game mode, lane count, semi trucks, special ability
- Score multiplier calculated from settings
- Top-down pixel-art car game on HTML Canvas (160x220 internal resolution, displayed 2x)
- Player car steerable via: arrow keys, A/D keys, mouse slider
- Scrolling road with lane dividers, grass/curb sides, hedge wall on right
- Traffic cars with random colors; red cars change lanes with turn signals
- Semi-truck traffic vehicles (larger, 56px tall)
- Two special abilities: Jump (fly over cars) and Ram Shield (destroy cars)
- Energy bar HUD, score display, multiplier display
- Particle explosion effect on crash
- Game Over overlay with score display
- "Return to Settings" button after game over
- Flashing "READY!" button for ability activation
