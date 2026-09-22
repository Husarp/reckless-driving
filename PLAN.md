# PLAN

Pruned to five real items on 2026-09-22 (direct instruction): everything else was completed,
superseded, or discarded. The full old plan is in git history (`git log -- PLAN.md`), and every
completed item's story is in CHANGELOG.md.

## Open

- [x] **DONE (2026-09-22, Batch 477, v3.3.0)** — hero row (BEST SCORE + PERFORMANCE SCORE) plus SCORING / SURVIVAL / TOTALS / HABIT ledger panels; all 15 stats kept, nothing hidden.

- [x] **DONE (2026-09-22, Batch 488, v3.7.0) — Better achievement icons.** 57 achievements share a 6-shape icon set (`ACH_ICONS`: car,
  star, road, clock, bus, lock), so most cards repeat one of six pictures. Check the archived
  design docs FIRST (they were deleted in Batch 500 — recover from git history if needed).
  Same `[x,y,w,h]` pixel-rect shorthand, 16x16 viewBox.

- [x] **DONE (2026-09-22, Batch 486, v3.6.4) — Booster preview popup**: a plain unlabeled window with no consistent size across
  boosters, reads as "appears out of nowhere". Wants a fixed size and the booster's name in it.

- [x] **DONE (2026-09-22, Batch 486, v3.6.4) — Last cutscene: wrong police positioning.** User-reported, never pinned down — reproduce
  in the crash sequence's final phase and fix.

- [x] **DONE (2026-09-22, Batch 489, v3.7.1) — DEV menu closed off.** Hidden and inert unless
  `localStorage.devMenu === 'on'`. The same gate now covers `?testcoins=1` (999,999 coins) and
  `?resetprogress=1` (wipes every save), both of which were reachable by any player in a public repo.

- [x] **DONE (2026-09-22, Batch 487, v3.6.5) — `witness_crash` removed from the daily pool.** Measured at ~1 crash per 21 simulated minutes and 0 on 4+ lanes; `NPC_INATTENTIVE_CHANCE` proved NOT to be the cause (100% inattentive still gave 0). Achievement kept.
  Measured then: 0 crashes in 5 simulated minutes at 4 lanes/RECKLESS. `NPC_INATTENTIVE_CHANCE`
  (0.10) is the tuning knob, or re-scope the mission.

- [ ] **Badge idea (secret): bump the ambulance.** User's idea, 2026-09-23. Note before building it:
  ambulances are currently EXEMPT from the BUMPER CAR's launch for the same reason they are exempt
  from ramming — instant death is the ambulance's whole identity, and the launch branch skips them
  explicitly. So this needs a deliberate decision first: either carve out an exception so the bumper
  (and only the bumper) can launch one, or scope the badge to something else that counts as
  "bumping" it. Pairs with the existing BAD SAMARITAN (deliberately ram an ambulance) and
  CEASE AND DESIST (silence one with the Tank).

- [ ] **Better ability display/indicator in the Garage.** User's idea, 2026-09-23. The card currently
  states the ability as a text row (`abilityLabelFor()` — JUMP / SHIELD BUMP / TANK SHOT / BUMPER
  LAUNCH / none), which reads as a spec-sheet line rather than as the thing that most changes how a
  car plays. Wants it to actually communicate. The design docs were deleted in Batch 500; git history has them if needed.

- [ ] **Mission / badge idea: scatter the cones without hitting the car.** User's idea, 2026-09-23.
  Road obstacles come in two kinds and behave differently: cones can be driven straight through and
  scatter, a broken-down car cannot. The idea is to reward threading an obstacle — plough the cones
  while missing the vehicle. Fits as either a daily (`sum` across the day, like `pass_cars`) or a
  secret badge. Check first that scattering is actually detectable as an event and how often cones
  appear, since that is exactly what killed `witness_crash` as a daily (Batch 487): measure the rate
  BEFORE adding it to the pool.

- [ ] **Build papercut: the self-test fails silently if the game is already open.** Found 2026-09-23
  (Batch 506). `build.ps1` runs the freshly built exe hidden and waits for `GAME_VERSION`, but the
  app serves itself on a fixed `127.0.0.1:42017`. If an installed copy is already running it owns
  that port, the test instance never loads, and the build dies with "the game never finished
  loading" — which reads as "your edit broke the game" rather than "close the game first".
  Either detect the port being held and say so, or have the self-test pick a free port.

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
