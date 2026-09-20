# CHANGELOG — Reckless Driving

All notable changes to this project are listed here.
Format: `X.Y.Z — YYYY-MM-DD HH:MM: <description>`
- X = major overhaul, Y = new feature/update, Z = minor fix or tweak

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
<!-- New entries go here, above the baseline -->
