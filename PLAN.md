# PLAN

Open work only. Everything from the lettered batches A-M (2026-09-23) is finished and lives in
CHANGELOG.md under its own version heading; the full old plan is in git history (`git log -- PLAN.md`).

## Open

### Waiting on a decision (asked 2026-09-25, Batch 556 — not started)

- [ ] **Reset the survival times already recorded?** Batch 556 stopped pause and screen-off time from
  counting, but runs saved before it keep their inflated times (some ~3 hours). Note: every ANDROID
  player starts from an empty save anyway, because the release key forces a reinstall - so a reset
  only matters on Windows. Scope to confirm: the run list's `timeSurvived`, the per-car best
  survival, and any survival-based achievement progress.
- [ ] **Total playtime in Stats.** User's own idea: count app time, but stop counting after 5 minutes
  without input (AFK). Open: count ALL screens (menus, Garage, pause), or only gameplay? And where it
  sits in Stats.
- [ ] **LEGENDARY label cut off on the phone** (Stats collection). Not reproducible in the browser at
  375px - the 7px Silkscreen fits there - so it is a font-rendering difference on the device. User
  suggested auto-shrinking the font when it does not fit; recommended in chat, awaiting a yes.
- [ ] **Save transfer between devices.** User's design: a device ID that survives reinstalls, an
  export bound to the TARGET device's ID so one file cannot be shared around, confirmations and a
  "do not close the app" warning, in a new "Other" section of Settings. Answered in chat with the
  honest limits (no client-side scheme is uncrackable; Android's ID is stable per signing key, which
  the new release key now makes possible). Several design questions open - see chat of 2026-09-25.
- [ ] **CONTROLS HEIGHT default.** Shipped at LOW (Batch 554). User: "ok" - once the SPLIT testers
  settle on MID or HIGH, make that the default (the `selected` option on #tcHeightSetting).

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
