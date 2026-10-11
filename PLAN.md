# PLAN

Open work only, sorted. Finished work lives in CHANGELOG.md (local only, never on GitHub).
Nothing here names a secret award or says how to get one - PLAN.md is public (AGENTS.md house rules).

## Next update

Order to build in: bugs, then balance, then the visual changes, then sounds (the biggest). Release notes for
it: short, and only "added/edited N secret awards" if any change.

### Bugs (checked against the code)

Full findings for the 2026-10-09 items (line numbers, measurements, test scripts): notes/plan-check-2026-10-09.json and
notes/audio-bug/FINDINGS.md (local only).

- [ ] **TAP ROAD FOR ABILITY visible with the floating joystick** (2026-10-09). Not reproduced: the code hides it with
  JOYSTICK + FLOATING ON. Visible by design in ARROWS and with a fixed joystick. Needs a screenshot from the owner.

### Rebalancing

- [ ] **Daily streak makes the Daily Gift better** (owner, 2026-10-04; parked 2026-10-12: "leave for now"): the longer your streak, the better the gift -
  e.g. a growing bonus up to +50% (150%) and/or extra items at streak milestones (7, 14, 30 days...). Shown in the
  GIFT tab. Needs numbers.

- [ ] **XP only from missions and the Daily Gift?** (owner's idea, 2026-10-09, decision needed). My view: not as
  stated - XP becomes a fixed daily ration (a 2-hour session = one short run), the level turns into a "days logged in"
  counter and slows the coin economy, which scales with level. Pace from missions+Gift+Word only: ~1 level a day; level
  100 in ~94 days (~156 with Harder levels). Recommended middle path: keep run XP but scaled down, and level-scaled XP
  missions. Options: (1) keep today, (2) middle path, (3) the full idea - which should then replace Harder levels.

### New and changed

- [ ] **Level-up rewards vs the slower levels** (2026-10-11): levels now need +100 XP each (3.41); check the level-up
  rewards still feel right at the slower pace.
### At release time

- [ ] **TEMPORARY: remove `convertOldLaneRateScores`** (Batch 577, the one-time conversion of old
  Scores to the new lane multipliers). User: leave it "for a couple of updates" - at EVERY release,
  remind the user and ask whether to remove it now. Remove the whole block between the TEMPORARY
  markers after `const LANE_MULT` (the `laneRatesConverted` flag in saves can stay, it is harmless).

## Later

### Waiting on the owner

- [ ] **Extra Boxes are switched off (Batch 683, owner 2026-10-12)** until they get a new price. Since Batch 682 a box
  pays the Word bundle (avg coins 145k at level 10, 436k at 50, 800k at 100) but cost 300k + 50k per box that day.
  Owner floated 500,000. Suggestion: a price that grows with level (~60-80% of the box's average payout). Turning them
  back on is `EXTRA_BOXES_ENABLED = true`. While off, the LUCKY STREAK award (3 Extra Box paints in a row) can't be
  earned - decide whether it should count Gift/Word paints instead.

- [ ] **Level-reward cars** (asked 2026-09-28, waiting on the owner's pick). At levels 10, 20 ... 100 a
  window like the Daily Gift's reveal pops up and the player claims a car. The owner picks which cars (the PC
  test client has everything unlocked to choose from). Open: do those cars leave the shop and go into the
  SPECIAL section? -> YES (2026-09-28): they leave the shop and join SPECIAL. DONE for the TANK at level 50
  (Batch 589). "The booster at level 20" = the UNDERGLOW boost type (was level 10) - done, Batch
  590. The Bumper Car stays in the boxes.
- [ ] **Small rewards for every level up** (owner, 2026-10-04): today only a few levels give something (Underglow at
  20, the Tank at 50, Prism at 100). Idea: every level up pays a small amount of coins, and every 10th level a bigger
  reward, shown in the same claim window as the level-50 Tank. Proposal to tune: 5,000 + 500 x level coins per level
  (about one coin mission's worth at low levels), plus a free Extra Box every 10th level. Fits with the level-reward
  cars item above.
- [ ] **CONTROLS HEIGHT default.** Shipped at LOW (Batch 554). User: "ok" - once the SPLIT testers
  settle on MID or HIGH, make that the default (the `selected` option on #tcHeightSetting).
- [ ] **Tutorial does not cover the cross/split arrow layouts or the diagonals.** Open question
  whether it should.

### Ideas (not scheduled)

- [ ] **Police chase with wanted stars** (owner's idea, 2026-10-03/04 - a big system, think it through before
  building; parked for now). Police cars sometimes appear on the road. Provoking them earns WANTED STARS, like GTA 5:
  passing one too fast in the NEXT lane (not two lanes away), ramming a car near it, jumping over it, or jumping a car
  near it. Bigger offences give more stars; more stars = a harder and longer chase. The star bar slowly drains; when
  it empties the chase ends and pays a reward that grows with how hard it was (base score and base coins x your
  multiplier). Chase hazards, unlocked by star level:
  - ROADBLOCKS: red-and-white barriers and parked police cars across up to ~80% of the lanes (8 of 10), announced
    with the same warning as the coned breakdown; fit through the gap, or jump the shorter ones.
  - POLICE FROM BEHIND, like ambulances but many and a bit faster than you: weave between them; you can't overtake
    them; jumping backwards over one helps, ramming is mostly useless here.
  - HELICOPTER: an ambulance-style warning plus the helicopter's shadow; a few seconds later your lane (or your lane
    and its neighbours, by stars) is bombed with explosions.
  Also needed: new crash titles for these deaths on the results screen (like T-BONE); how much normal traffic during a
  chase and whether passes still score; a chase multiplier bonus (e.g. +50% at high stars) so chases are dangerous but
  worth it. Earlier proposal kept for reference: escape by surviving / getting away / a takedown, a cut-in that you
  can jump, red/blue light bar and a police siren, no ambulances during a chase, police with their own city spawn roll.
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
- [ ] **Bigger energy bar as a car upgrade** (idea, 2026-10-04, part of the car-upgrades plan): a module that gives a
  car more energy (a bigger bar, more cells).
- [ ] **Paints per car** (future, 2026-09-28, part of the car-upgrades plan). Each car buys its OWN paints (not one
  colour for every car); PRISM stays for all cars. A paint from a box goes to a random vehicle. Some paints can be
  bought per vehicle, some can't. Paints may get rarity ranks. When this lands: players who bought paints get
  their coins back plus some compensation, and every paint is locked again.
- [ ] **Phone notifications** (owner, 2026-10-05): Android notifications that bring the player back - the daily
  streak (about to break), the Daily Gift being ready, and unclaimed missions/rewards. Needs a local-notifications
  plugin in the Capacitor app, the notification permission, an on/off setting, and a limit on how often they fire.
- [ ] **Discounts on vehicles** (owner, 2026-10-05): some cars in the shop are on sale for a while (e.g. a rotating
  daily/weekly deal), shown with the old price crossed out. Open: how many cars at once, how big the discount, how
  long it lasts.
- [ ] **Daily Word box rework** (idea, "maybe", depends on boosters): no XP or coins - a chance of a booster,
  a smaller chance of a paint, a very small chance of a car.
- [ ] **Rename "Car Crash" to "Reckless Driving" everywhere** (asked 2026-09-27) - it is the game's real
  name. Not started: needs a list of where "Car Crash" / carCrash still appears (file names, folder,
  docs, code comments, build scripts, the repo folder) and which of those are safe to rename.

### Parked

- [ ] **Drag-to-place layout editor.** Designed with the user on 2026-09-24 (presets as read-only
  templates, dragging turns a layout into CUSTOM, a HUD-free frame, overlap blocked), then set aside:
  the player complaint turned out to be one axis - height - and CONTROLS HEIGHT answers it for a
  fraction of the cost. Revisit only if players ask for placement specifically.

### Not yet tried for real

- [ ] **Save transfer:** EXPORT on Android (the system save screen) and anything in the packaged Windows app.
  Android device ID and IMPORT are proven (Pixel 7 restore, 2026-09-26).

## Standing conventions

- [ ] **After any notable batch, update the game's own ABOUT/tutorial.** Two halves: refresh the
  HOW IT WAS BUILT figures at milestones (versions = `##` headings in CHANGELOG.md, batches =
  highest Batch number, changes = bullet + bold-paragraph count, days = distinct heading dates vs
  span), and check whether new systems need a tutorial card or make existing copy stale — the
  "Nine heavy vehicles" and "58 cars to find" drift from Batch 474 is exactly the failure mode.
