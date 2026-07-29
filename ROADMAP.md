# Roadmap — ryanhambleton.space

Ordered intentions only. **Nothing below is authorized until explicitly approved**, and this repository serves production.

Current state: [`STATUS.md`](STATUS.md) · Decisions: [`DECISIONS.md`](DECISIONS.md) · Identity: [`PROJECT.md`](PROJECT.md)

## Done

- Next.js 16 App Router site live on `ryanhambleton.space` via Vercel project `rhspace`
- Portfolio restructured into four practice sections
- Flagship dashboard case studies published
- Standardized portfolio JSON schema
- Art and Lab sections, including the agent-shell demo
- Streamlit model-ops dashboard demo (local, outside the deployment)
- Learning documentation modules 0–9
- Canonical local workspace and repository rename settled (`rhspace` → `ryanhambleton-space`)

## Near term (content, lowest risk)

Content changes carry the least risk because they need no framework work:

1. Keep `content/` entries current — portfolio, resume, about
2. Add case-study MDX for portfolio entries that only have JSON
3. Keep the resume PDF in `public/` aligned with `content/resume.json`

## Later (approval-gated)

4. Decide whether `/api/agent` ever runs live rather than mock, which requires an `OPENAI_API_KEY` in Vercel and a cost decision
5. Decide whether the Streamlit demo becomes reachable from the site, stays local, or is retired
6. Optional cosmetic rename of the Vercel project `rhspace` → `ryanhambleton-space`
7. Consider a CI gate — typecheck, lint, build — before production deploys, given there is none today
8. Retire `ryanhambleton-space-legacy-stub` once it is certainly no longer needed

## Out of scope until approved

- Pushing `main` without approval — it deploys production
- Vercel project, env var, domain, or DNS changes
- Framework or major dependency upgrades
- Deleting the legacy stub repository
- Developing from `Drive\Cursor\ryanhambleton-space`, Apps, or archives
- Adding paid third-party services

## Working agreement

Branch from `main`, run `npx tsc --noEmit`, `npm run lint`, and `npm run build`, open a pull request, review the Vercel preview, then merge only with Ryan's explicit approval.
