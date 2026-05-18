# todo_widget — Agent Handoff

## Last Agent
- Agent: Codex
- Date: 2026-05-18
- Status: Complete

## What Was Built/Changed
- Added root `vercel.json` rewrites so Vercel serves the static app from `web/`.
- Mapped `/` to `/web/index.html` and all asset paths to `/web/:path*`.

## Decisions Made (and why)
- Kept the existing `web/` folder structure and fixed routing at the deployment layer instead of moving app files.

## Issues Found By Other Agents
- None recorded.

## Code Review Status
- Reviewed by Codex: [x] Yes [ ] No
- Issues found: Vercel can return `404: NOT_FOUND` when the deployment root has no `index.html`.
- Issues fixed: Added root rewrites to serve the static web app from `web/`.

## Next Actions
- [ ] Confirm the Vercel deployment URL loads the web UI instead of `404: NOT_FOUND`.
