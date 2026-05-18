# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are committed and pushed to `origin/master` in commit `2541652`.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.
- Web UI task data now loads from the Apps Script `action=today` endpoint via `web/data.js`.

## What Changed This Session
- Replaced hardcoded web `SAMPLE_TASKS` with a live Apps Script fetch.
- Added browser loading and retryable error states before React renders.
- Kept `app.jsx` unchanged by populating `window.SAMPLE_TASKS` after the fetch succeeds.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Open the web UI in a browser and confirm live tasks render correctly.
