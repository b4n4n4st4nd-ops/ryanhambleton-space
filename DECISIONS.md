# DECISIONS — ryanhambleton.space

> Chronological log of **settled** product, architecture, content, and workflow decisions.
> Full Architecture Decision Records live in [`docs/decisions/`](docs/decisions/README.md); this file is the summary index that links to them.
>
> Rules for this file:
>
> - Record a decision only after explicit approval from Ryan or verifiable evidence in this repository.
> - Never record a proposal or idea here as though it were settled — use "Open decisions" below.
> - Never delete a superseded decision; mark it superseded and link forward.

## Settled decisions

| Date | Decision | Evidence | ADR |
|------|----------|----------|-----|
| 2026-07 | The site **is** the product — this is a portfolio, not a product with a separate marketing page | studio `PROJECT_REGISTRY.yaml` (`web_landing_page: site-is-the-product`) | — |
| 2026-07 | Next.js App Router on **Next.js 16** with React 19, TypeScript, and Tailwind CSS v4 | `package.json` | — |
| 2026-07 | Content lives as **JSON + MDX under `content/`**, editable without touching React | `content/EDIT_THESE_FIRST.md`, `docs/content-guide.md` | — |
| 2026-07 | Portfolio entries follow a **standardized JSON schema** rather than ad-hoc shapes | `5b495a4`, `content/portfolio/` | — |
| 2026-07 | Detail routes are **prerendered** from content via `generateStaticParams` rather than fetched at runtime | build output, `app/portfolio/[slug]` | — |
| 2026-07 | Dashboard datasets are committed as JSON under `content/data/dashboards/` — no database | `content/data/dashboards/` | — |
| 2026-07 | The agent demo defaults to **mock mode** (`AGENT_DEMO_MODE=mock`) so it is interview-safe and costs nothing | `.env.example`, `app/api/agent/route.ts` | — |
| 2026-07 | Any OpenAI key is **server-only** and never prefixed `NEXT_PUBLIC_` | `.env.example` | — |
| 2026-07 | The Streamlit model-ops dashboard is a **separate Python demo**, not part of the Next.js build or deployment | `streamlit/model-ops-dashboard/`, build output | — |
| 2026-07 | Portfolio is organized into **four practice sections** | `a2b5d0b` | — |
| 2026-07 | The site carries learning documentation (modules 0–9) as a first-class artifact, not just product code | `docs/` | — |
| 2026-07-13 | GitHub repository renamed `rhspace` → `ryanhambleton-space`; the **Vercel project stays `rhspace`** | studio `PROJECT_REGISTRY.yaml`, `CHANGELOG` | — |
| 2026-07-13 | `ryanhambleton-space-legacy-stub` is retained as a temporary archive of pre-rename stub history and is **not deleted** until explicitly retired | studio `PROJECT_REGISTRY.yaml` | — |
| 2026-07-13 | This production site is **not modified from the studio** without a supervised, approved plan | studio `ROADMAP.md`, `.cursor/rules/ryan-studio-core.mdc` | — |
| 2026-07-28 | Canonical local root is the `Ry_Studio` Projects path; `Drive\Cursor\ryanhambleton-space`, Apps copies, and archives are non-canonical | `b87a6b2`, `.cursor/rules/canonical-root.mdc` | — |
| 2026-07-28 | Agents must read `node_modules/next/dist/docs/` before writing code, because Next.js 16 differs from older training data | `AGENTS.md` | — |
| 2026-07-28 | `STATUS.md` carries current shared state; this file indexes decisions; `docs/decisions/` holds full ADRs | This change | — |

## Open decisions

**Not approved — do not act on these.**

| # | Question | Context | Blocks |
|---|----------|---------|--------|
| 1 | Does `/api/agent` ever run live instead of mock? | Requires an `OPENAI_API_KEY` in Vercel and an ongoing cost decision | Agent-shell demo depth |
| 2 | Does the Streamlit dashboard become reachable from the site, stay local, or get retired? | Nothing currently builds or deploys it, so visitors cannot reach it | Lab / portfolio completeness |
| 3 | Rename the Vercel project `rhspace` → `ryanhambleton-space`? | Purely cosmetic; recorded in the studio as optional later work | Naming consistency only |
| 4 | Add a CI gate (typecheck, lint, build) before production deploys? | There is none today, and pushing `main` deploys production | Deploy safety |
| 5 | When is `ryanhambleton-space-legacy-stub` retired? | Held as an archive, tied historically to Vercel project `rhvercel` | Repository cleanup |
| 6 | Is the second clone at `Drive\Cursor\ryanhambleton-space` removed? | Same remote, non-canonical, a standing risk of divided work | Workspace hygiene |
| 7 | What happens to the four open remote branches — two Transparensea feature branches and two agent-generated `cursor/*` branches? | None is documented; status unknown | Branch hygiene; avoiding duplicated work |
| 8 | Where does Transparensea work belong — this repository's Lab section, the standalone `transparensea` repository, or both with a stated boundary? | The studio registry calls them distinct but defines no boundary, while two branches here carry the name | Preventing parallel implementations |

## Superseded

| Date | Superseded decision | Replaced by |
|------|--------------------|-------------|
| 2026-07-13 | GitHub repository named `rhspace`; personal-site migration status `in-progress` | Renamed to `ryanhambleton-space`; migration recorded complete |
| 2026-07-13 | Vercel project `rhvercel` associated with the personal site | `rhspace` is the production project for `ryanhambleton.space`; `rhvercel` is historically tied to the legacy stub |
