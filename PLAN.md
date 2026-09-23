# PLAN

Open work only. Everything from the lettered batches A-M (2026-09-23) is finished and lives in
CHANGELOG.md under its own version heading; the full old plan is in git history (`git log -- PLAN.md`).

## Open

### Waiting on a decision

- [ ] **Compact Scores row: the meta line still wraps inside the row.** The row itself is one line and
  the `i` works, but at 264px "5L / 1m 32s / 1.00x -> 3.40x" needs about 150px and has roughly 98.
  Something has to give at that width. Cheapest candidates, neither done because neither was asked
  for: drop the car NAME in compact mode (the sprite beside it already identifies the car), or show
  only the multiplier's peak instead of the start-to-peak range. Asked in chat.
- [ ] **Licensing the repo.** Asked in chat; answered there. Not acted on.
- [ ] **Free placement for the touch controls (drag-and-drop editor).** User's own idea: pick a
  position manually for the fixed joystick, the arrows and/or the ability button, anywhere on the
  gameplay screen, with an edit mode and save/cancel. Feasibility answered in chat (the honest
  answer is that the drag part is easy and the INTERACTION with the existing layout/fit machinery is
  the expensive part). Not started, and not to be started until the shape is agreed.

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
