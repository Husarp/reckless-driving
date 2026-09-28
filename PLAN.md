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

- [x] ~~Bigger text (a setting)~~ — done, Batch 575 (option C: ~11px floor on phones + TEXT SIZE 100/115/130%).

- [ ] **TEMPORARY: remove `convertOldLaneRateScores`** (Batch 577, the one-time conversion of old
  Scores to the new lane multipliers). User: leave it "for a couple of updates" - at EVERY release,
  remind the user and ask whether to remove it now. Remove the whole block between the TEMPORARY
  markers after `const LANE_MULT` (the `laneRatesConverted` flag in saves can stay, it is harmless).

- [ ] **Rename "Car Crash" to "Reckless Driving" everywhere** (asked 2026-09-27) - it is the game's real
  name. Not started: needs a list of where "Car Crash" / carCrash still appears (file names, folder,
  docs, code comments, build scripts, the repo folder) and which of those are safe to rename.
- [x] ~~Android updates through Android's own download service~~ — done, Batch 579 (v3.34.0), like
  Lexling. Not yet tried on a phone: needs 3.34.0 installed and a newer release to update to.
- [x] ~~Awards bar: design A1 "DITHER BAR"~~ — done, Batch 580 (v3.34.1), with square pixels and at least
  2 solid columns per earned tier.
- [x] ~~Version numbers in release file names~~ — from v3.33.3 on, and every past release renamed
  (2026-09-27): 41 files across reckless-driving, lexling and lockdown, with their notes to match.
- [x] ~~GIANT SNAIL's flat +0.20~~ — kept, by decision: 250 km/h is hard to survive and it has no ability.

- [ ] **Level-reward cars** (asked 2026-09-28, waiting on the owner's pick). At levels 10, 20 ... 100 a
  window like the Daily Gift's reveal pops up and the player claims a car. The owner picks which cars (the PC
  test client has everything unlocked to choose from). Open: do those cars leave the shop and go into the
  SPECIAL section? -> YES (2026-09-28): they leave the shop and join SPECIAL. DONE for the TANK at level 50
  (Batch 589). "The booster at level 20" = the UNDERGLOW boost type (was level 10) - done, Batch
  590. The Bumper Car stays in the boxes.
- [ ] **Boosters** (idea, 2026-09-28). Bought in the shop, equipped, and used up in the next run. Examples:
  accelerate twice as fast (reach top speed sooner); +X% coins and XP for that run. Open: fixed or rising
  prices, and whether boxes can drop them.
  Also: a booster that makes Daily Word letters appear on the road more often.
- [ ] **Upgrading owned cars** (idea, 2026-09-28). Clicking a car in the Garage opens a panel over the lower
  half of the screen - also for cars not bought yet (not for undiscovered ones), where it says the car has to
  be bought: the new place to buy a car, and it shows the car's stats. Once bought it shows the stats and the
  car's LEVEL (each level raises all stats by ~5-10%?); a car levels up through tasks driven in it (drive X
  km, jump X times, score X...). It also has MODULES to upgrade: acceleration, how fast it moves up and down,
  coin earnings, XP multiplier, top speed. A car at max level with every module maxed gets an extra bonus,
  looks especially cool in the Garage (with a new tab for maxed cars), and gets a cool in-game effect (a
  trail? wings instead of boosters?).
- [x] ~~Reckless drivers pay 1.5x~~ — reckless is a way of driving on any vehicle now, x1.5 of it (Batch 590).
- [ ] **Paints per car** (future, 2026-09-28, part of the car-upgrades plan). Each car buys its OWN paints (not one
  colour for every car); PRISM stays for all cars. A paint from a box goes to a random vehicle. Some paints can be
  bought per vehicle, some can't. Paints may get rarity ranks. When this lands: players who bought paints get
  their coins back plus some compensation, and every paint is locked again.
- [ ] **Daily Gift gives several rewards at once** (future, 2026-09-28): some coins, some XP, maybe a paint -
  instead of one thing.
- [x] ~~Ram the cones and the car~~ — TOW AWAY ZONE (Batch 589).
- [x] ~~Best reachable multiplier~~ — MAX on the START button, same button height (Batch 589).
- [ ] **Daily Word box rework** (idea, "maybe", depends on boosters): no XP or coins - a chance of a booster,
  a smaller chance of a paint, a very small chance of a car.

### Done in Batch 592

- [x] ~~Ambulance crashes on their own~~ — the signalling-lane rule and the staged cut-ins are removed; the award is
  CALL AN AMBULANCE! BUT NOT FOR ME! (very rare now: 0 in 78 simulated ambulances).

### Done in Batch 591

- [x] ~~Runs pay too many coins next to missions~~ — halved (COIN_EARN_SCALE 50 -> 25).

### Done in Batch 588

- [x] ~~Passes at 50%, jump-over top-up, close calls only if you survive, Word XP fill~~
- [x] ~~The drill rams, no double-tap re-ram, ABILITY INDICATOR setting~~
- [x] ~~Garage MULT sort + OWNED filter, Fire Engine 170 / Limousine 160, FPS text size~~

### Done in Batch 586

- [x] ~~Gift/Word coins x4, coin missions follow the level (10k/20k/40k +500 a level), Extra Box 300k +50k~~
- [x] ~~WHO CALLS THE AMBULANCE? reachable~~ — a quarter of ambulances get a driver who cuts in; ambulances never brake.
- [x] ~~Energy bar not dimmed while paused~~ / ~~grey screen after coming back~~ / ~~tutorial amounts~~
- [x] ~~Ramming bonus x2~~ — the energy a kill refunds doubled (Batch 587); the points stay 1.2x a pass.

### Done in Batch 585

- [x] ~~Ambulance drove through a truck (10 lanes)~~ — never takes a lane a car is signalling into; ambulances
  crash like other traffic; secret award WHO CALLS THE AMBULANCE?.
- [x] ~~Old square coin in Gift/Word rewards~~ — the real coin sprite.
- [x] ~~Garage: sort buttons wrap / boost cards uneven / coins off-centre~~ — fixed.

### Done in Batch 583

- [x] ~~Follow the shared app rules (from Lexling)~~ — X until the next start, the Windows installer named with
  its version (with progress, deleted at the next start), a failed update: TRY AGAIN + GITHUB.
- [x] ~~Update banner pushes the version off a phone~~ — the road gap gives up exactly the banner's height.

### Done in Batch 582

- [x] ~~Android updates: back to the game installing them itself~~ — with the percentage, and the install
  carrying on by itself after "install unknown apps" is allowed. The default for all projects
  (APP-STANDARDS.md); Lexling still has to switch (its own chat).

### Done in Batch 581

- [x] ~~No banner after starting offline~~ — a failed check retries every 30s and on the connection coming back.
- [x] ~~VERSION row squashed on a phone~~ — the buttons move below the text when they don't fit.

### Done in Batch 578

- [x] ~~Update check on every return to the game~~ — checks on launch and on every return (GitHub at most
  every 5 minutes); closing the banner hides it only until the next return.
- [x] ~~Car multipliers in 0.05 steps~~ — rounded in one place; x0.99 / x1.01 cars are x1.00; old Scores
  only go down (a run whose car rate rose is left as it is).

### Done in Batch 577

- [x] ~~Old Scores show multipliers that can't be reached any more~~ — converted to today's lane rates, once (option B).

### Done in Batch 576

- [x] ~~Everything runs faster on the Samsung (120Hz)~~ — the game ticks 60 times per second of real time on any screen.

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
