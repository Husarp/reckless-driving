# Agent rules — Reckless Driving

The game is `carCrash.html` — a single self-contained HTML file
(~12,000 lines, all HTML/CSS/JS inline). `PLAN.md` is the forward-looking
backlog, `CHANGELOG.md` the full history. Read both before non-trivial work.

## Hard constraints (from PLAN.md "Notes & Constraints")
- Keep the game a SINGLE HTML file unless complexity genuinely demands
  splitting.
- No external libraries or frameworks unless absolutely necessary.
- Target browsers: Chrome, Firefox, Safari (iOS), Chrome (Android).
- Mobile section of PLAN.md is frozen: do NOT implement mobile-specific
  behaviour without an explicit ask. A native Android rebuild is planned
  separately; this HTML version is a prototype.

## Do not re-litigate settled decisions
These were built and deliberately reverted or removed. Do not re-add or
re-propose without an explicit ask:
- Free (non-lane-snapping) horizontal movement — tried, rejected.
- Lane-change banking tilt — removed in Batch 210.
- Night mode — built out fully, then scrapped in Batch 188.

## House rules
- When the user asks a question, ANSWER it. Do not silently implement
  instead. If an idea needs scoping, say so and log it to PLAN.md.
- Patch `carCrash.html` with targeted edits. Never rewrite the file.
- Append to `CHANGELOG.md` after every meaningful change, using the
  existing format: `X.Y.Z — YYYY-MM-DD HH:MM: Batch N — <description>`
  (X = major overhaul, Y = feature, Z = fix/tweak). Newest entry at top.
  Continue the existing batch numbering.
- Update `PLAN.md` when scope or decisions change. Completed items move
  out of PLAN.md into CHANGELOG.md — PLAN.md is a backlog only.
- Changelog entries describe what changed, why, and how it was verified —
  match the existing level of detail.
- Commit to git after each working state.

## Workspace specifics
- Live preview: port 8080 serves `~/game/`. The game is at
  `/carCrash.html`. Restart after edits is NOT needed — just refresh.
- Uploads: port 8090 drag-and-drop page. Files land in `~/game/incoming/`,
  or `~/game/assets/` with the checkbox ticked. Use this instead of chat
  attachments, which block `.html`.
- Verification limit: gameplay cannot be tested from the agent side. After
  changes, confirm the file parses and state exactly what the user should
  look for on refresh.
