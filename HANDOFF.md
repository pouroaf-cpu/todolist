# todo_widget — Agent Handoff

## Last Agent
- Agent: Codex
- Date: 2026-05-18
- Status: Complete

## What Was Built/Changed
- Fixed task loading API parameter in `logic/api.py`.
- Changed the Google Apps Script load request from `view=today` to `action=today`.

## Decisions Made (and why)
- Used the Apps Script API's expected `action` parameter so today's tasks can load correctly.

## Issues Found By Other Agents
- None recorded.

## Code Review Status
- Reviewed by Codex: [x] Yes [ ] No
- Issues found: `load_tasks_async` used `params={"view": "today"}` while the API expects `params={"action": "today"}`.
- Issues fixed: Updated the GET request parameter.

## Next Actions
- [ ] Run the app and confirm today's tasks load from Google Apps Script.
