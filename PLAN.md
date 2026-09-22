# PLAN

Pruned to five real items on 2026-09-22 (direct instruction): everything else was completed,
superseded, or discarded. The full old plan is in git history (`git log -- PLAN.md`), and every
completed item's story is in CHANGELOG.md.

## Open

- [x] **DONE (2026-09-22, Batch 477, v3.3.0)** — hero row (BEST SCORE + PERFORMANCE SCORE) plus SCORING / SURVIVAL / TOTALS / HABIT ledger panels; all 15 stats kept, nothing hidden.

- [ ] **Better achievement icons.** 57 achievements share a 6-shape icon set (`ACH_ICONS`: car,
  star, road, clock, bus, lock), so most cards repeat one of six pictures. Check the archived
  design docs FIRST — `old/Achievements Tab.dc.html`, `old/achievementscontentbrief.html`,
  `old/Booster Icons 3x1.dc.html` — they may hold an unported icon set. Same `[x,y,w,h]`
  pixel-rect shorthand, 16x16 viewBox (the Batch 413 gear fix is the precedent).

- [ ] **Booster preview popup**: a plain unlabeled window with no consistent size across
  boosters, reads as "appears out of nowhere". Wants a fixed size and the booster's name in it.

- [ ] **Last cutscene: wrong police positioning.** User-reported, never pinned down — reproduce
  in the crash sequence's final phase and fix.

- [ ] **`witness_crash` mission may be unachievable since NPC crashes got rarer (Batch 431).**
  Measured then: 0 crashes in 5 simulated minutes at 4 lanes/RECKLESS. `NPC_INATTENTIVE_CHANCE`
  (0.10) is the tuning knob, or re-scope the mission.

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
