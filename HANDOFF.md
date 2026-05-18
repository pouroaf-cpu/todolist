# todo_widget — Agent Handoff

## Last Agent
- Agent: Codex
- Date: 2026-05-18
- Status: Complete

## What Was Built/Changed
- Deployed the web app to Vercel production from `web/`.
- Normalized `AGENTS.md` back to valid Markdown after escaped instruction text was present in the working tree.
- Removed a hardcoded iCloud app password from `logic/config.py`; scheduling now reads `TODO_WIDGET_ICLOUD_PASSWORD` from the environment and local `.env` files are ignored.
- Fixed `web/app.jsx` date parsing so task due dates support both `DD/MM/YYYY` from the API and existing `YYYY-MM-DD` values.
- Updated Today filtering to compare parsed dates, so `DD/MM/YYYY` tasks due today are not hidden.
- Moved the status bar outside the task scroll container and updated CSS so the footer stays pinned below the scrollable task list.

## Decisions Made (and why)
- Deployed from `web/` because that folder contains `index.html`; deploying from the repo root can produce the `404: NOT_FOUND` page.
- Used `parseDate` for Today filtering because raw string comparison only works for `YYYY-MM-DD` and fails for the API's `DD/MM/YYYY` format.

## Issues Found By Other Agents
- None recorded.

## Code Review Status
- Reviewed by Codex: [x] Yes [ ] No
- Issues found: Date parsing and Today filtering did not handle API `DD/MM/YYYY` dates; status bar was inside the task scroll area; `logic/config.py` contained a hardcoded iCloud app password; `AGENTS.md` had escaped Markdown from session context.
- Issues fixed: Added dual-format date parsing, parsed-date Today filtering, moved status bar outside `.task-scroll` with fixed footer sizing, moved the iCloud password to `TODO_WIDGET_ICLOUD_PASSWORD`, and normalized `AGENTS.md`.
- Obsidian logging: Attempted required `obsidian daily:append` entries, but the CLI returned "unable to find Obsidian" because Obsidian was not running.

## Deployments
- 2026-05-18: Production deployed from `web/` to `https://web-ddw555h5n-pouroas-projects.vercel.app`; aliased to `https://web-pouroas-projects.vercel.app` and `https://web-beta-five-31.vercel.app`. Vercel inspect status: Ready.
- 2026-05-18: Production deployed from `web/` to `https://web-l4a53x0uk-pouroas-projects.vercel.app`; aliased to `https://web-pouroas-projects.vercel.app`.

## Next Actions
- [ ] Rotate the exposed iCloud app password and set the replacement in `TODO_WIDGET_ICLOUD_PASSWORD` for local desktop scheduling.
- [ ] Open the deployed web UI and confirm API dates display in the Today list without footer overlap.
