# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are deployed to Vercel production.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.
- Web UI task data now loads from the Apps Script `action=today` endpoint via `web/data.js`.
- Root `vercel.json` rewrites serve the static web app from `web/` on Vercel.
- Latest production deploy was run from `web/` and aliased to `https://web-pouroas-projects.vercel.app`.
- `web/app.jsx` now accepts both API `DD/MM/YYYY` dates and existing `YYYY-MM-DD` dates when parsing and filtering Today tasks.
- The web status bar now renders outside `.task-scroll` and stays pinned beneath the scrollable task list.
- `logic/config.py` now reads the iCloud app password from `TODO_WIDGET_ICLOUD_PASSWORD`; local `.env` files are ignored and the previously hardcoded credential should be rotated.

## What Changed This Session
- Deployed production to `https://web-ddw555h5n-pouroas-projects.vercel.app`; Vercel also aliases it to `https://web-pouroas-projects.vercel.app` and `https://web-beta-five-31.vercel.app`.
- Ran `vercel build --yes` from `web/`; build completed successfully.
- Verified deployment with `vercel inspect`; status was Ready. Direct HTTP checks failed locally due a Windows TLS client error.
- Normalized `AGENTS.md` Markdown after escaped session-context text appeared in the working tree.
- Removed the hardcoded iCloud app password from `logic/config.py`, replaced it with `TODO_WIDGET_ICLOUD_PASSWORD`, and ignored local `.env` files.
- Attempted required Obsidian daily log entries; the CLI could not connect because Obsidian was not running.
- Fixed `parseDate` in `web/app.jsx` to support `DD/MM/YYYY` and empty values safely.
- Updated Today filtering to use parsed date comparison rather than raw `YYYY-MM-DD` string comparison.
- Moved the status bar JSX outside `.task-scroll` and adjusted `.win`/`.statusbar` CSS to prevent footer overlap.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Rotate the exposed iCloud app password and set the new value in `TODO_WIDGET_ICLOUD_PASSWORD` before using desktop calendar scheduling.
- Open the deployed web UI and confirm API dates display in the Today list without footer overlap.
