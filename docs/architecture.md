# ryanhambleton.space — Architecture

## Overview

Personal portfolio built with **Next.js 16 App Router**, **React 19**, **Tailwind CSS v4**, and a **hybrid JSON + MDX** content layer. Static pages are generated at build time; interactive demos live under `/lab`.

## Routes

| Route | Type | Data source |
|-------|------|-------------|
| `/` | Static | `content/site.json`, featured portfolio JSON |
| `/about` | Static | `content/about.mdx` |
| `/portfolio` | Static | `content/portfolio/*.json` grouped into four practice sections |
| `/portfolio/[slug]` | SSG | JSON metadata + interactive dashboard **or** MDX / live-product page |
| `/art` | Static | `content/art/*.json` |
| `/art/[slug]` | SSG | JSON + `*.mdx` |
| `/resume` | Static | `content/resume.json` |
| `/lab` | Static index | `content/lab/*.json` |
| `/lab/agent-shell` | Client + API | `app/api/agent/route.ts` |
| `/lab/[slug]` | Dynamic | iframe embed for Streamlit demos |

## Content model

- **JSON** — project metadata (`primaryPractice`, capability/technology tags, `projectType`, status, thumbnail, links)
- **MDX** — optional STAR case studies (Situation, Task, Action, Result)
- **Loaders** — `lib/content/index.ts` reads files at build time and groups published projects by practice

### Portfolio practices

1. AI Product Development & Implementation
2. BI Reporting & Visualization
3. Solution Architecture & Strategy
4. Web & App Development

Primary practice places the card; tags communicate overlap.

## Component map

```
components/
  layout/     SiteHeader, SiteFooter, ThemeToggle
  ui/         Button, Badge, SectionHeading, PageHero, SkillPills
  portfolio/  ProjectCard, PortfolioPracticeSections
  art/        ArtGallery
  resume/     Timeline
  lab/        AgentChat, AgentLogsPanel, DemoCard, DemoFrame
  dashboards/ Shell, charts, demos
```
## V2 agent demo pattern

```
Browser (AgentChat) → POST /api/agent → OpenAI gpt-4o-mini OR mock mode
```

- API keys in `OPENAI_API_KEY` (server-only)
- `AGENT_DEMO_MODE=mock` for interview-safe hardcoded responses
- Agent logs returned as structured JSON for the expandable Logs panel

## Streamlit embed pattern

Deploy app to Streamlit Community Cloud → set `embedUrl` in `content/lab/*.json` → `/lab/[slug]` renders `DemoFrame` iframe.

### Transparensea

Flagship Lab product: **Transparensea** (Model Transparency, Adoption & Impact) — predictive-model visualization and reporting companion.

- App: `streamlit/model-ops-dashboard/`
- Docs: [`docs/transparensea/`](./transparensea/)
- Lab JSON: `content/lab/analytics-explorer.json`, `content/lab/transparensea.json`
- Demo brand: fictional **A.Typical** with synthetic data (not employer data)
- Separate from portfolio case study `predictive-model-performance-impact`

## Deployment

GitHub → Vercel → `ryanhambleton.space`. See [deployment.md](./deployment.md).
