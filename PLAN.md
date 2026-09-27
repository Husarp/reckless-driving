# PLAN

Open work only. Everything from the lettered batches A-M (2026-09-23) is finished and lives in
CHANGELOG.md under its own version heading; the full old plan is in git history (`git log -- PLAN.md`).

## Open

### Waiting on a decision (asked 2026-09-25, Batch 556 — not started)

- [x] ~~Reset old survival times~~ — done, Batch 557 (scores and earned achievements kept).
- [x] ~~Total playtime in Stats~~ — done, Batch 557 (TIME PLAYED + TIME DRIVING in TOTALS).
- [x] ~~LEGENDARY label cut off~~ — done, Batch 557 (measured auto-fit).
- [x] ~~Save transfer between devices~~ — done, Batch 564 (file only, option A). Android device ID
  and IMPORT proven on a real phone (Pixel 7 restore, 2026-09-26). Not yet run for real: EXPORT on
  Android (the system save screen) and anything in the packaged Windows app.
- [ ] **CONTROLS HEIGHT default.** Shipped at LOW (Batch 554). User: "ok" - once the SPLIT testers
  settle on MID or HIGH, make that the default (the `selected` option on #tcHeightSetting).

- [ ] **Letters picked up in the air?** Reported 2026-09-26: "you must be on the road to collect a
  letter, not jumping". The game already refuses a pickup while jumping (since Batch 431), and a test
  confirmed it (a letter under the car at take-off was never collected). Asked the user which car and
  when exactly - possibly the pickup the moment the car lands, which counts as on the road.

- [x] ~~The ability badge ignores CONTROLS SIZE on phones~~ — fixed, Batch 567 (79 / 104 / 129 on a OnePlus 6).

- [x] ~~Same-size lanes on phones, with the road panning sideways~~ — done, Batch 568 (v3.31.0).
  Left open: tune the lane multipliers after playtesting; 3 lanes on a phone kept as is (roadside art).
  Proposed by the user 2026-09-27:
  on a phone, more lanes shrink the whole view, so 10 lanes sees far ahead and is "overpowered", and
  players stick to few lanes because they are easier to see. Measured (375x812): look-ahead vs 4 lanes
  is 0.83x at 3, 1.38x at 6, 2.13x at 10, lanes 84px wide at 3 down to 33px at 10. PC is already fair
  (one zoom, the road just gets wider). Idea: one fixed zoom on phones too; when the road is wider than
  the screen the camera follows the player sideways. DECIDED 2026-09-27, in progress:
  - zoom: the size 4 lanes have today (my pick, user said "start"); 3 lanes gains roadside, 5-10 pan;
  - ambulances AND letters spawn in any lane; an off-screen one gets an arrow at the screen edge;
  - multipliers unchanged for now - user will playtest; maybe MORE lanes = MORE multiplier later;
  - a thin lane-position strip, with an on/off setting (removed again in Batch 569 - "we don't need it").

- [x] ~~Lane multipliers~~ — done, Batch 570 (option B: traffic made even, re-tested, 3 x1.10 / 4 x1.00 / 10 x0.82).
- [x] ~~HIGH ROLLER tiers~~ — done, Batch 571 (2.5 / 3.5 / 4.5 / 5.5x; best reachable 5.65x).

- [x] ~~Pause button easier to hit on small screens~~ — done, Batch 573 (invisible area, 31x31 -> 44x63px).

- [ ] **Bigger text (a setting).** Asked 2026-09-27: text in Missions, Awards and elsewhere is too small
  on a phone; the user asked for ideas on how to scale it without things not fitting. Proposal sent -
  awaiting a choice.

### Done in Batch 574

- [x] ~~Settings: BACK only~~ / ~~GIFT link colours in the Missions footer~~ / ~~update check hangs~~
  (10s timeout and a plain message; the phone's Lockdown VPN was blocking all name lookups).

### Done in Batch 572

- [x] ~~Full energy bar: stripes only top and bottom, and blinking~~ — one path round the frame, moving clockwise.

### Done in Batch 565

- [x] ~~Results list remembers its scroll position~~ — always opens at the top.
- [x] ~~Ability needs 3 cells~~ — one cell is enough for jump and ram.
- [x] ~~Stock goes 200 instead of 170~~ — the 200 km/h floor removed; all 58 cars stop at their rating.

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
- [x] ~~Comment cleanup, remaining~~ — done, Batch 566 (18 blocks, 144 lines; five stale ones corrected).
- [x] ~~No Windows launch screen~~ — done, Batch 566 (`app/splash.html`, same art as Android).
- [ ] **Tutorial does not cover the cross/split arrow layouts or the diagonals.** Open question
  whether it should.

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
