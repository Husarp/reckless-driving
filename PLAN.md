# PLAN

Pruned to five real items on 2026-09-22 (direct instruction): everything else was completed,
superseded, or discarded. The full old plan is in git history (`git log -- PLAN.md`), and every
completed item's story is in CHANGELOG.md.

## Open

- [x] **DONE (2026-09-22, Batch 477, v3.3.0)** — hero row (BEST SCORE + PERFORMANCE SCORE) plus SCORING / SURVIVAL / TOTALS / HABIT ledger panels; all 15 stats kept, nothing hidden.

- [x] **DONE (2026-09-22, Batch 488, v3.7.0) — Better achievement icons.** 57 achievements share a 6-shape icon set (`ACH_ICONS`: car,
  star, road, clock, bus, lock), so most cards repeat one of six pictures. Check the archived
  design docs FIRST — `old/Achievements Tab.dc.html`, `old/achievementscontentbrief.html`,
  `old/Booster Icons 3x1.dc.html` — they may hold an unported icon set. Same `[x,y,w,h]`
  pixel-rect shorthand, 16x16 viewBox (the Batch 413 gear fix is the precedent).

- [x] **DONE (2026-09-22, Batch 486, v3.6.4) — Booster preview popup**: a plain unlabeled window with no consistent size across
  boosters, reads as "appears out of nowhere". Wants a fixed size and the booster's name in it.

- [x] **DONE (2026-09-22, Batch 486, v3.6.4) — Last cutscene: wrong police positioning.** User-reported, never pinned down — reproduce
  in the crash sequence's final phase and fix.

- [ ] **DEFERRED by direct instruction (2026-09-22) — do not action without asking.** Make the DEV
  menu unreachable in normal play. It is currently a plain `DEV` label in the main-menu footer that
  opens on one click, next to the version number, and it grants Add XP / Add Coins / Reset All — so
  any player can hand themselves everything by accident. Options when it is wanted: hide it behind a
  deliberate gesture, gate it on a localStorage flag, or strip it from packaged builds only. User
  still uses it as-is, so it stays until they say otherwise.

- [x] **DONE (2026-09-22, Batch 487, v3.6.5) — `witness_crash` removed from the daily pool.** Measured at ~1 crash per 21 simulated minutes and 0 on 4+ lanes; `NPC_INATTENTIVE_CHANCE` proved NOT to be the cause (100% inattentive still gave 0). Achievement kept.
  Measured then: 0 crashes in 5 simulated minutes at 4 lanes/RECKLESS. `NPC_INATTENTIVE_CHANCE`
  (0.10) is the tuning knob, or re-scope the mission.

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
