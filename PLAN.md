# PLAN

Open work only. Everything from the lettered batches A-M (2026-09-23) is finished and lives in
CHANGELOG.md under its own version heading; the full old plan is in git history (`git log -- PLAN.md`).

## Open

### Waiting on a decision (asked 2026-09-25, Batch 556 — not started)

- [x] ~~Reset old survival times~~ — done, Batch 557 (scores and earned achievements kept).
- [x] ~~Total playtime in Stats~~ — done, Batch 557 (TIME PLAYED + TIME DRIVING in TOTALS).
- [x] ~~LEGENDARY label cut off~~ — done, Batch 557 (measured auto-fit).
- [x] ~~Save transfer between devices~~ — done, Batch 564 (file only, option A). Still to do: try it
  for real once built - the Android plugin and the packaged Windows dialog have not run yet.
- [ ] **CONTROLS HEIGHT default.** Shipped at LOW (Batch 554). User: "ok" - once the SPLIT testers
  settle on MID or HIGH, make that the default (the `selected` option on #tcHeightSetting).

### Done in Batch 563

- [x] ~~MULTI-LANE HOLD is never saved~~ — saved now, and so are SKIP CRASH ANIMATION and DIFFICULTY.

### Done in Batch 559

- [x] ~~LANE CHANGE SPEED setting~~ — 1-5, glide x0.6-x1.5 and the diagonal step with it.
- [x] ~~Tap the road for the ability~~ — TAP ROAD FOR ABILITY, never with the floating joystick.

### Done in Batch 558

- [x] ~~Controls editor with a live preview~~ — CONTROLS screen, real game screen scaled into a preview.
- [x] ~~Diagonal hold keeps changing lanes (CROSS)~~ — one lane per 600 ms.
- [x] ~~Fixed joystick on the wrong side~~ / ~~energy bar jump sound~~ / ~~remember lane count~~.

### Decided and done (Batch 556)

- [x] ~~QUIT dialog vs behaviour~~ — user chose: a quit saves nothing; message now matches.
- [x] ~~Licensing~~ — all rights reserved (commit 2ce5219); Jersey 10 added to its font list.
- [x] ~~Compact Scores meta line~~ — user: the cars still fit, no change needed.
- [x] ~~Unused files / docs + AGENTS.md / design files in history~~ — all removed.

### Parked

- [ ] **Drag-to-place layout editor.** Designed with the user on 2026-09-24 (presets as read-only
  templates, dragging turns a layout into CUSTOM, a HUD-free frame, overlap blocked), then set aside:
  the player complaint turned out to be one axis - height - and CONTROLS HEIGHT answers it for a
  fraction of the cost. Revisit only if players ask for placement specifically.

### Carried over

- [x] ~~Points for being near an NPC crash~~ — done, Batch 551 (25, same or adjacent lane).
- [x] ~~Scores tab compaction~~ — done, Batch 551 (`i` icon, measured 560px threshold).
- [ ] **Comment cleanup, remaining.** 14 multi-attempt narrative blocks still to compress (~230
  lines). Rule that has held so far: keep every measurement and every "why not the obvious thing",
  drop only the batch-by-batch retelling. Several of the biggest blocks turned out to be almost
  entirely load-bearing engineering, so the real yield is well under the raw line count.
- [ ] **No Windows launch screen.** Android got one in Batch 548; the desktop build still has none.
- [ ] **Tutorial does not cover the cross/split arrow layouts or the diagonals.** Open question
  whether it should.

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
