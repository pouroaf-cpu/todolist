# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are committed and pushed to `origin/master` in commit `2541652`.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.
- Web UI task data now loads from the Apps Script `action=today` endpoint via `web/data.js`.
- Root `vercel.json` rewrites serve the static web app from `web/` on Vercel.

## What Changed This Session
- Added root `vercel.json` to fix Vercel `404: NOT_FOUND` by routing `/` to `/web/index.html`.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Confirm the Vercel deployment URL loads the web UI instead of `404: NOT_FOUND`.
