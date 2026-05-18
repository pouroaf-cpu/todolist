# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are committed and pushed to `origin/master` in commit `2541652`.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.
- Web UI task data now loads from the Apps Script `action=today` endpoint via `web/data.js`.
- Root `vercel.json` rewrites serve the static web app from `web/` on Vercel.
- Latest production deploy was run from `web/` and aliased to `https://web-pouroas-projects.vercel.app`.

## What Changed This Session
- Deployed the linked Vercel `web` project from the `web/` folder to production.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Open `https://web-pouroas-projects.vercel.app` and confirm the UI loads.
