# ryanhambleton.space

> **Identity source of truth.** Active development must occur only at the canonical local path below. Do not develop from `Drive\Cursor\ryanhambleton-space`, archives, or other copies.

Secret values must **never** be written into this file. Document env var *names* and secret *filenames* only.

Current state: [`STATUS.md`](STATUS.md) · Sequencing: [`ROADMAP.md`](ROADMAP.md) · Settled decisions: [`DECISIONS.md`](DECISIONS.md)

> **Next.js 16 caution.** This project's APIs, conventions, and file structure may differ from older knowledge. Read the relevant guide under `node_modules/next/dist/docs/` before writing code, and heed deprecation notices. See [`AGENTS.md`](AGENTS.md).

---

## Identity

| Field | Value |
|------|-------|
| Project name | ryanhambleton.space |
| Purpose | Personal portfolio site (Next.js) plus optional Lab/Streamlit demos |
| Status | Active production site (Vercel `rhspace` → ryanhambleton.space) |
| Canonical local path | `C:\Users\rhamb\Drive\Ry_Studio\01_Development\Projects\ryanhambleton-space` |
| Canonical GitHub | `https://github.com/b4n4n4st4nd-ops/ryanhambleton-space` |
| Default branch | `main` |
| Active development branch | `main` (production site). Lab / Transparensea Streamlit work: `feature/transparensea-lab` |

## Stack

- Next.js 16 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4
- Content via JSON/MDX under `content/`
- Optional Lab Streamlit apps under `streamlit/` (primarily on `feature/transparensea-lab`). Note: `streamlit/model-ops-dashboard/` is present on `main` today, but nothing builds or deploys it — it runs locally only

## Repository structure

| Path | Role |
|------|------|
| `app/` | Next.js routes |
| `components/` | UI |
| `content/` | Site content |
| `docs/` | Learning modules / architecture |
| `lib/` | Loaders and helpers |
| `public/` | Static assets |
| `streamlit/` | Lab Streamlit apps (when present on branch) |

## Setup

```powershell
cd "C:\Users\rhamb\Drive\Ry_Studio\01_Development\Projects\ryanhambleton-space"
npm ci
```

## Run locally

```powershell
npm run dev
```

Open **http://localhost:3000**

## Test / validation

```powershell
npm run lint
npx tsc --noEmit
npm run build
```

## Development servers / ports

| Service | Expected port / address | Notes |
|---------|-------------------------|-------|
| Next.js dev | `http://localhost:3000` | Report listeners before starting |
| Streamlit Lab (when used) | typically `8501` | Only on branches that include Streamlit apps |

## Deployment targets

| Target | Status / notes |
|--------|----------------|
| Vercel project `rhspace` | Production domain **ryanhambleton.space** |
| GitHub | `b4n4n4st4nd-ops/ryanhambleton-space` (public) |

No production deploy / DNS / Vercel project renames without explicit approval.

## Environment and secrets

Env var **names** only — values live in `.env.local` and Vercel:

- `NEXT_PUBLIC_SITE_URL` — canonical / OG metadata base
- `AGENT_DEMO_MODE` — `mock` gives interview-safe hardcoded responses from `/api/agent`
- `OPENAI_API_KEY` — optional, server-only, for live agent responses; never prefixed `NEXT_PUBLIC_`

- Local secret filenames: `.env.local` (gitignored)
- Never commit filled env files

## Current limitations

- Canonical day-to-day work is this Projects path on `main`
- Transparensea Lab Streamlit experience lives on `feature/transparensea-lab` until merged
- Standalone Transparensea product repo is separate (`transparensea`) when under Projects

## Archive / successor

| Field | Value |
|------|-------|
| Former Cursor secondary | `C:\Users\rhamb\Drive\Cursor\ryanhambleton-space` (archive after Lab preservation) |
| Successor | This canonical Projects path |

## Canonical root checks

```powershell
Get-Location
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status --short
```

If toplevel path or remote does not match this file, **stop immediately**.
