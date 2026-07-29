# ryanhambleton.space

Personal portfolio — Next.js 16, React 19, Tailwind CSS v4.

## New here? Start learning

**→ [docs/START_HERE.md](docs/START_HERE.md)** — your step-by-step learning path from domain to live site.

Quick start:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Edit your content (no React required)

See [content/EDIT_THESE_FIRST.md](content/EDIT_THESE_FIRST.md) — start with `content/site.json` and `content/resume.json`.

## Deploy

When ready to go live: [docs/module-9-deploy.md](docs/module-9-deploy.md)

## Transparensea (Lab product)

**Transparensea** — Model Transparency, Adoption & Impact — is the AI/ML insight companion demo in this repo.

| Item | Location |
|------|----------|
| Streamlit app | [`streamlit/model-ops-dashboard/`](streamlit/model-ops-dashboard/) |
| Product docs | [`docs/transparensea/`](docs/transparensea/) |
| Lab pages | `/lab/analytics-explorer`, `/lab/transparensea` |

Local run: `cd streamlit/model-ops-dashboard && streamlit run app.py`

## Project structure

| Folder | Purpose |
|--------|---------|
| `app/` | Pages and routes |
| `components/` | Reusable UI |
| `content/` | Your JSON + MDX content |
| `docs/` | Learning modules, architecture, Transparensea product docs |
| `lib/` | Content loaders and helpers |
| `public/` | Images, resume PDF |
| `streamlit/` | Transparensea and other Streamlit demos |

## Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Local development server |
| `npm run build` | Production build (run before deploy) |
| `npm run lint` | Check code style |
