# todo_widget Memory

## Current Status
- Existing GitHub remote: https://github.com/pouroaf-cpu/todolist.git
- `web/` todo app files are committed and pushed to `origin/master` in commit `2541652`.
- `web/.vercel/` remains ignored and should stay out of Git.
- Desktop app task loading now calls the Apps Script endpoint with `action=today`.

## What Changed This Session
- Fixed `logic/api.py` so `load_tasks_async` sends `params={"action": "today"}` instead of `params={"view": "today"}`.
- Updated `HANDOFF.md` for Codex session tracking.

## Next Steps
- Run the app and confirm today's tasks load from Google Apps Script.
