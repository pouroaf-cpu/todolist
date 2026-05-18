# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are committed and pushed to `origin/master` in commit `2541652`.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.
- Web UI task data now loads from the Apps Script `action=today` endpoint via `web/data.js`.
- Root `vercel.json` rewrites serve the static web app from `web/` on Vercel.
- Latest production deploy was run from `web/` and aliased to `https://web-pouroas-projects.vercel.app`.
- `web/app.jsx` now accepts both API `DD/MM/YYYY` dates and existing `YYYY-MM-DD` dates when parsing and filtering Today tasks.
- The web status bar now renders outside `.task-scroll` and stays pinned beneath the scrollable task list.

## What Changed This Session
- Fixed `parseDate` in `web/app.jsx` to support `DD/MM/YYYY` and empty values safely.
- Updated Today filtering to use parsed date comparison rather than raw `YYYY-MM-DD` string comparison.
- Moved the status bar JSX outside `.task-scroll` and adjusted `.win`/`.statusbar` CSS to prevent footer overlap.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Open the local or deployed web UI and confirm API dates display in the Today list without footer overlap.
