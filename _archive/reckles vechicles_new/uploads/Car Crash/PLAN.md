# Reckless Driving — Development Plan

## Status legend
- [ ] Not started
- [~] In progress
- [x] Done

Completed batches are no longer listed here — the full history (what changed, why, and how it was verified) lives in `CHANGELOG.md`. This file is a forward-looking backlog only.

---

## TECHNICAL (mechanical/gameplay impact — do these first)

## BATCH 45 — Post-Batch-48 Verification & Tuning Pass (NEXT UP)
Batches 44, 46, 47, and 48 (steering back to lane-snap then made fully smooth, accelerating/braking vertical movement, NPC lane-change frequency and reckless-driver spawn share both cut down, stutter fix, full-screen JS-computed responsive frame, proportional ambulance speed) are done — see CHANGELOG.md 1.35.0-1.38.0. Everything below has only been scripted-verified (exact numeric behavior confirmed against the live game state), not actually played by a human — that's what this batch is for.
- [ ] Actually play a run and confirm the fully-smooth glide (Batch 48) feels right — verified numerically (constant delta from frame 1) but not by feel
- [ ] Tune the vertical accel/friction/brake feel (Batch 46: `V_ACCEL=0.13`, `V_FRICTION=0.08`, `V_BRAKE=0.25`, all ×`CAR_SCALE`) — these are first-pass numbers, not confirmed against user feedback yet
- [ ] Confirm collision detection (`checkCollision`, width/x-based) still behaves correctly with the bigger car sprites — should just work since it's rect-overlap based, but verify, not assume
- [ ] Playtest whether the "boxed in by 3+ converging cars, no jump available, feels unlucky not skill-based" concern is better or worse now that lane-snap is back
- [ ] Sanity-check the lane-change banking tilt animation (Batch 44) at different game speeds and lane counts — tune `MAX_TILT_ANGLE`/`TILT_SENSITIVITY` if it looks too subtle or too exaggerated
- [ ] Confirm NPC traffic still feels alive now that reckless drivers are down to 10% of spawns (was 23%) with a 150-300 frame re-roll (was 70-170) on top of normal/truck's already-halved frequency — not so calm that traffic feels static
- [ ] Test the JS-computed full-screen frame (Batch 47, `sizeGameFrame()`) on an actual device with a real window resize — the Browser pane's programmatic resize doesn't fire a genuine `resize` event, so live-resize recomputation was only verified via manually dispatching one
- [ ] Confirm the ambulance (Batch 48, now `2.0-2.5×currentSpeed`) actually reads as "same direction as traffic, just faster" rather than the old "looks wrong" complaint — this was fixed based on a code-level scaling analysis (proportional vs. flat bonus), not a direct visual confirmation, since no screenshot was available when it was diagnosed

## BATCH 49 — Static Road Obstacles
User's own framing, explicitly flagged as a future batch, not scoped further: add static (non-moving) obstacles on the road to dodge alongside regular traffic — e.g. crashed cars, debris. Distinct from Batch 36's road *pickups* (collectibles) — these would be hazards, not collectibles.
- [ ] Not scoped yet: what "crashes" the player on contact vs. what's just visual, whether they use the same spawn/despawn system as vehicles or a separate one, whether they can appear in a way that (like vehicles) never blocks all lanes at once, art/sprite work needed
- [ ] Needs a real design pass before implementing

## BATCH 40 — Jump Rework: Back to Fixed Duration
The hold-to-fly jump is being reworked again — user found it too strong ("a little OP") and wants a simpler, fixed-duration model back, but re-tuned:
- [ ] Remove hold-to-fly (`jumpHeld`, real-time energy drain, release-to-land-early) — back to: press once, fixed time in the air, like the very first jump implementation
- [ ] Duration tuning target given directly: at the SLOWEST game speed (`baseSpeed`), a perfectly-timed jump should cover *almost* enough distance to clear one normal car — not more. Reasoning: at base speed you shouldn't really need to jump over cars at all, jump is more of a high-speed panic button
- [ ] Because duration is fixed in time (ms) while the road scroll rate keeps rising with `currentSpeed`, the DISTANCE a fixed-duration jump covers grows automatically as the game speeds up — no extra scaling logic needed, just pick the right fixed duration and "clears almost everything at high speed" falls out naturally
- [ ] Needs actual math/playtesting to pick the duration: figure out roughly how many px/frame a normal car's relative screen speed is at `baseSpeed` (given the 0.75x-1.5x spawn-time speed clamp), multiply by a target duration, check the covered distance against a car's length (`PLAYER_HEIGHT`, 31px as of Batch 42, was 24) plus a safety margin
- [ ] Should still be capped/gated somehow — user said "it's also should be capped" but didn't specify exactly how (cooldown between jumps? energy-gated like before?). **Needs a follow-up question before implementing.**
- [ ] Wings and the ability-bar visuals (already implemented) stay as they are — this is scoped to the ability's *timing/energy* model only

## BATCH 29 — Delayed Game Start (NEEDS DESIGN DISCUSSION — not ready to implement)
- [ ] Idea, not yet speced: player starts positioned in the middle lane (for an odd lane count, this is a true single center lane; current behavior for even counts — sitting between the two middle lanes — presumably stays as-is)
- [ ] The run doesn't actually "start" (score counting, speed ramp-up) until the player's first real lane-change input (arrow key or A/D — both are equivalent now), NOT an ability/jump activation
- [ ] While waiting for that first input (and specifically for odd lane counts), keep the middle lane clear of all traffic and ambulances so the player can't be hit while just sitting still pre-start
- [ ] Also considering: prevent nearby cars from lane-changing into the player's lane in a way that guarantees a hit near the start — user was unsure whether disabling lane-changing entirely near the start removes too much of the challenge, wants to think it over
- [ ] Not scoped yet — revisit with the user before implementing

## BATCH 23 — Agent Design Review
- [ ] Dispatch an agent to analyze the current design, suggest improvements, compare with similar games

## BATCH 36 — Road Pickups
- [ ] Idea, not yet speced: collectible pickups that spawn on the road, same general system as vehicle spawning
- [ ] **Score multiplier pickup** — temporary, time-limited multiplier boost
- [ ] **Golden honk pickup** — for X seconds after collecting, no NPC car will change lanes onto the player's lane, and any car already in the player's lane changes out of it
- [ ] **Daily letter pickup** — collect letters (one per day / per run?) that spell out a word over time; completing the word grants a reward (skin or in-game currency). Needs its own design pass: what determines which letter appears, how "daily" is tracked, what the reward economy looks like (ties into Batch 31's shop system)
- [ ] Not scoped yet — genuinely new game system (spawn logic, collision-with-player detection separate from crash collision, HUD indicators, persistence for daily-letter progress), needs real design work before implementing

## BATCH 31 — Car Shop / Unlockable Player Models
- [ ] Later-stage idea: once Batch 21's player model variety exists, add a shop system for buying/unlocking additional player car models (not just colors)
- [ ] Bigger system than a typical batch — needs its own scoping pass when picked up (currency/unlock source, where the shop UI lives, whether it persists via localStorage like the leaderboard)

## Small tuning leftovers (not big enough for their own batch)
- [ ] Achievements — e.g. "Survived 60 seconds", "Rammed 10 cars", "No abilities used" (idea from early planning, never scoped further)
- [ ] Consider increasing the minimum gap between spawns in the same lane (old idea, never revisited)
- [ ] "Close call" bonus score — extra points for narrowly avoiding a vehicle without hitting it. Originally noted as only meaningful once slider-cheese was impossible; the mouse-drag slider is gone as of Batch 41, so this is now viable, just not scoped

---

## VISUAL / PRESENTATION ONLY (no mechanical impact on the game — do these last)

## BATCH 21 — Vehicle Visual Variety: Models + Colors
- [ ] Truck: show front-facing cab (headlights toward player); car variants: taxi, compact, sedan details
- [ ] Also cover player car models, not just NPC traffic — more body-shape options for the player to pick, same spirit as the existing car color picker
- [ ] Expand NPC color palettes (currently 4-5 fixed colors per vehicle type) with more random variety
- [ ] Vehicles don't need to be a single flat color — e.g. trucks could have the cab one color and the trailer another (keep the second tone neutral — white/gray/black — so combinations don't clash)

## BATCH 25 — Player Crash Animation
- [ ] Right now the player car just disappears the instant a collision is detected (only the particle burst remains, drawn over a dark overlay) — add an actual crash animation for the player car itself (e.g. spin/flip/skid) before the game-over overlay takes over

## BATCH 22 — Music Overhaul
- [ ] Softer gameplay music; multiple tracks; optional speed-scaling BPM; chill menu/pause music

---

## MOBILE (deferred — not batches, just a holding area)
User is planning a from-scratch native Android app rebuild later, treating this HTML version purely as a prototype/proof of concept. **Do not implement anything in this section without being asked explicitly** — no work should be invested in mobile-specific behavior here in the meantime.

- [ ] Touch-drag on mobile should feel natural (no lag/jump) — follows the finger 1:1 by setting `player.targetX`, but never verified on an actual touch device
- [ ] Test on portrait and landscape orientations — never done
- [ ] Tilt steering sets `player.targetX` proportionally to tilt angle (matches the pre-Batch-41 slider behavior) — never redesigned or tuned properly, since mobile input is out of scope until the native rebuild

---

## Notes & Constraints
- Game is a single HTML file — keep it that way unless complexity demands splitting
- No external libraries/frameworks unless absolutely necessary
- Must work on both desktop (keyboard + mouse) and mobile (touch + tilt) for now, but see the Mobile section above — no further mobile investment until the native app rebuild
- Target browsers: Chrome, Firefox, Safari (iOS), Chrome (Android)
- **Steering, current state (2026-08-25, Batch 44/46/48)**: horizontal is fully smooth/continuous while a key is held (glides from the very first frame, no discrete snap first), rounding to the nearest lane center only on release; vertical has acceleration/friction/braking physics — not an instant constant speed. History: lane-snap was the original design (research-backed, genre convention) → Batch 41 removed it in favor of full free movement on both axes → after playtesting, Batch 44 reverted horizontal back to lane-snap (discrete snap-then-glide) because free movement's overshoot/undershoot felt like bad luck rather than a skill issue → Batch 48 simplified further, removing the initial discrete snap so holding a key is smooth from the first frame; vertical stayed free since that was never the complaint, then got its own physics rework in Batch 46. Don't remove the lane-center-on-release behavior without being asked — free movement (never rounding to a lane) has been tried and rejected once already.
