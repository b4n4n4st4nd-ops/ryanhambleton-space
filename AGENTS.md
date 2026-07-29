<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# AGENTS.md — ryanhambleton.space

Read [`PROJECT.md`](PROJECT.md) first.

## Project-specific context

| Field | Value |
|------|-------|
| Purpose | Personal portfolio at ryanhambleton.space |
| Approved stack | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| Current phase | Production site on `main`; Lab/Transparensea Streamlit on `feature/transparensea-lab` |
| Non-goals | Silent production/DNS/Vercel changes; inventing portfolio claims |
| Testing | `npm run lint`, `npx tsc --noEmit`, `npm run build` |
| Deployment | Vercel `rhspace` — approval required for prod/DNS changes |

## Required preflight

```powershell
Get-Location
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status --short
```

Stop on path/remote mismatch vs `PROJECT.md`. Do not continue in `Drive\Cursor\...` or archives.

## Operating rules

1. Inspect before changing.
2. Prefer small reversible phases.
3. Never expose secrets; never commit `.env.local`.
4. Do not invent content, credentials, or integrations.
5. Do not merge Lab branches or deploy without explicit instruction.
6. Distinguish static checks from runtime smoke tests.
