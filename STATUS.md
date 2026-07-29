# STATUS — ryanhambleton.space

> Shared working state for Ryan, ChatGPT, Cursor, and other development agents.
> The committed repository is the source of truth. Update this file in the same commit as the work it describes.
> Identity: [`PROJECT.md`](PROJECT.md) · Sequencing: [`ROADMAP.md`](ROADMAP.md) · Decisions: [`DECISIONS.md`](DECISIONS.md)

| Field | Value |
|------|-------|
| Last updated | 2026-07-28 |
| Updated by | Cursor agent session |
| Current phase | **Live production**, maintained |
| Active branch | `main` |
| Baseline commit at update | `b87a6b2` |
| Working tree at update | Clean, in sync with `origin/main` |

> **This repository deploys production.** Vercel project `rhspace` serves `ryanhambleton.space`. Pushing `main` is a production action. Prefer a branch and preview deployment, and get explicit approval before touching `main`, Vercel settings, env vars, domains, or DNS.

## Current phase

The site is live and stable. Content is the main editing surface; no framework work is in flight.

## Completed work

- Next.js 16 App Router site with 29 prerendered pages
- Portfolio restructured into four practice sections (`a2b5d0b`)
- 17 portfolio entries under `content/portfolio/`, several with long-form MDX case studies
- Flagship dashboards shipped: marketing performance, predictive model performance impact, executive KPI, market insights
- Standardized portfolio JSON schema across content entries
- Art section with an MDX entry (`soak-live-set`)
- Lab section including an agent-shell demo backed by `/api/agent`, defaulting to mock mode
- Separate Streamlit model-ops dashboard demo under `streamlit/model-ops-dashboard/`
- Learning documentation: modules 0–9 plus architecture, deployment, and content guides
- Canonical workspace established at the `Ry_Studio` Projects path, including `PROJECT.md` (`b87a6b2`)
- Coordination documents added: `STATUS.md`, `ROADMAP.md`, `DECISIONS.md`, and `docs/decisions/`; `PROJECT.md` extended with cross-links, the Next.js 16 caution, and env var names (this change)

## Validation results

Run 2026-07-28 from the canonical root on `main`:

| Check | Command | Result |
|------|---------|--------|
| TypeScript | `npx tsc --noEmit` | **Pass** (exit 0) |
| Lint | `npm run lint` (ESLint 9 flat config) | **Pass** (exit 0), no warnings |
| Production build | `npm run build` | **Pass** (exit 0) — Next.js 16.2.9 Turbopack, compiled in 5.5s, 29 static pages generated |

Static checks only, run locally. Not exercised: browser smoke test of any route, the `/api/agent` endpoint, the Streamlit app, and the local Python scripts. No deployment was performed and no live production URL was checked. **Do not claim the deployed site was verified.**

## Known issues

1. **Next.js 16 knowledge hazard.** `AGENTS.md` warns that this version's APIs and conventions differ from older training data, and that guides under `node_modules/next/dist/docs/` must be read before writing code. Treat confident-sounding Next.js advice from any agent as suspect until checked against those docs.
2. **The Vercel project name does not match the repository.** The project is `rhspace` while the repository is `ryanhambleton-space`. Renaming is cosmetic and unapproved; the mismatch is a standing source of confusion.
3. **A second local clone may exist** at `Drive\Cursor\ryanhambleton-space` pointing at the same remote. It is **not** canonical. Never develop there.
4. **`ryanhambleton-space-legacy-stub`** is a separate GitHub archive holding pre-rename stub history, historically tied to the Vercel project `rhvercel`. It is not this site and must not be deleted until explicitly retired.
5. **The agent demo is mock-only by default.** `/api/agent` returns hardcoded responses unless `AGENT_DEMO_MODE` is changed and an API key is supplied.
6. **The Streamlit dashboard is outside the deployment.** `streamlit/model-ops-dashboard/` is present on `main`, but nothing builds or deploys it, so visitors cannot reach it from the live site.
7. **No tests and no CI.** No automated test suite, and no continuous integration gate before production deploys.
8. **No `typecheck` npm script.** Use `npx tsc --noEmit`; `npm run build` also runs TypeScript.
9. **Four unmerged remote branches are open**, only one of which is mentioned in any document:

| Branch | Note |
|--------|------|
| `feature/transparensea-lab` | The only one documented — `PROJECT.md` names it as where Lab / Transparensea Streamlit work lives |
| `feature/transparensea-demo-v1` | Second Transparensea-related branch; relationship to the first is unrecorded |
| `cursor/add-reporting-portfolio-examples-aca5` | Agent-generated branch, undocumented |
| `cursor/joes-golf-club-site-e6a7` | Agent-generated branch referencing another product, undocumented |

Whether each is active, abandoned, or awaiting review is unknown, and no document explains the boundary between the two Transparensea branches here and the separate `transparensea` repository.

10. **A stale local branch** `migrate/import-cursor-working-tree` exists locally but not on `origin`.

## Exact next step

Triage the four open remote branches in known issue 10 — decide which are active, which are abandoned, and in particular how `feature/transparensea-lab` and `feature/transparensea-demo-v1` relate to the separate `transparensea` repository. Two branches touching the same idea across two repositories is how duplicated work starts.

No feature work is queued otherwise. This repository is in maintenance, and the studio holds it as "do not modify without a supervised approved plan."

When work does resume, the safe path is: branch from `main`, run the three static checks above, open a pull request, review the Vercel preview deployment, and only then merge with Ryan's explicit approval.
