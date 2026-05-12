# todo_widget — Codex Instructions

Read first: C:/Users/PFrew/Projects/_agent-system/RULES.md

## Stack
Not detected (no package.json or requirements.txt found)

## Code Review Role
You are the code quality gate for this project.
After any Aider/Qwen session per HANDOFF.md:
1. Run: git diff
2. Review all changes against RULES.md failure patterns
3. Fix minor issues directly
4. Document anything structural in HANDOFF.md under "Issues Found"
5. If new failure pattern found, append to C:/Users/PFrew/Projects/_agent-system/RULES.md with date and project name

## On START of every session
1. Read HANDOFF.md
2. Read C:/Users/PFrew/Projects/_agent-system/RULES.md
3. If last agent was Aider/Qwen, run git diff and review before doing anything else

## On END of every session
1. Update HANDOFF.md:
   - Agent: Codex
   - Date: (today)
   - What was reviewed/built/changed
   - Issues found and fixed
2. Run:
   obsidian daily:append content="- [todo_widget/Codex] {one line summary}"
   obsidian daily:append content="- [ ] {next action}"

## Obsidian Log Tag
Use [todo_widget/Codex] in all obsidian daily:append commands

## Vercel Deployment
When the user says "push to vercel" or when the Obsidian daily note
contains "- [ ] [todo_widget] Push to Vercel":

1. Check vercel is linked — run: vercel whoami
2. If not linked run: vercel link
3. Run: vercel --prod
4. Confirm deployment succeeded
5. Log deployment URL to HANDOFF.md under "Deployments"
6. Run: obsidian daily:append content="- [todo_widget/Codex] Deployed to Vercel — {URL}"
7. Mark the Obsidian task complete

## Deployment Checklist (run before every vercel --prod)
- [ ] Run git diff — no uncommitted Qwen/Aider code unreviewed
- [ ] Check HANDOFF.md — Code Review Status shows Codex reviewed
- [ ] No API keys in client-side code
- [ ] Build passes locally — run: npm run build
