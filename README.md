<h1 align="center">📡 Needs Radar MCP</h1>

<p align="center">
  <b>Every job posting is a buying signal. Turn them into a ranked list of companies that need what you sell.</b>
</p>

<p align="center">
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-stdio-blue" alt="MCP"></a>
  <img src="https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen" alt="Zero dependencies">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="MIT">
  <img src="https://img.shields.io/badge/status-unofficial-lightgrey" alt="Unofficial">
</p>

<p align="center">
  <!-- Demo: a GIF of Claude Code scanning prospects through this MCP. See assets/README.md to record one. -->
  <img src="assets/demo.gif" alt="Claude Code using the Needs Radar MCP" width="720">
</p>

---

A company hiring two React developers isn't just "hiring." It has a **web project**, a **budget**, and a stack of adjacent needs nobody is selling to yet — design, DevOps, SEO, AI.

Cold-prospecting tools sell you stale lists. **Needs Radar reads the job market as a signal of intent.** Point it at a region or a need, and it returns the companies hiring *right now*, ranked by how hot the signal is — the raw material for B2B prospecting that actually lands.

> Reverse B2B prospecting: instead of "who might buy?", ask "who just showed they're investing?"

## The idea in one picture

```
Job postings  ─►  group by company  ─►  score the signal  ─►  ranked prospects
(intent signal)   (who's hiring)        (volume·size·recency)  (hottest first)
```

A company posting **5 fresh openings** is investing harder than one posting a single old listing. Needs Radar makes that visible and sortable.

## Why it works

- 🎯 **Intent over interest.** A live job posting is the strongest public signal that a company is spending money on a problem.
- 📈 **Intensity scoring.** `openings × 3 + company-size weight + recency`. More fresh roles = hotter need.
- 🧹 **Clean prospects.** Staffing agencies and anonymous reposts are separated out, so your list is real companies hiring directly.
- 🆓 **Free & official source.** Built on France Travail's official API — no scraping, no per-lead fees.
- 🔌 **Composable.** It returns the raw companies; your agent enriches them (registry data, public grants, the decision-maker) and writes the pitch.

## Install (1 minute)

```bash
git clone https://github.com/mohamed-amine-ben-mallessa/needs-radar-mcp.git
cp needs-radar-mcp/.env.example needs-radar-mcp/.env
# paste your free France Travail credentials into .env  (see CONFIGURATION.md)
```

Point any MCP client at it:

```json
{
  "mcpServers": {
    "needs-radar": {
      "command": "python",
      "args": ["/absolute/path/to/needs-radar-mcp/server.py"],
      "env": {
        "FT_CLIENT_ID": "your_client_id",
        "FT_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

Zero dependencies — pure Python standard library.

## What you can ask

```
"Scan companies hiring developers around Lyon (69) — give me the 5 hottest prospects."
"Who's hiring for 'site web' needs in Bordeaux right now?"
"Market stats: how tense is the data-engineer market in Île-de-France?"
```

### Example output

> *"Companies hiring developers in Lyon (69)?"*

```
80 offers scanned → 24 direct prospects (2 staffing agencies set aside)

[27] AMILTONE        — 7 openings — 200–249 staff — Software dev   [hot]
[19] ALTECA          — 4 openings — 200–249 staff — IT consulting  [hot]
[10] WINSIDE LYON    — 2 openings —  10–19 staff  — IT consulting  [hot]
...
```

Score = `openings×3 + size + recency`. `[hot]` = at least one posting in the last 30 days.

## The 2 tools

| Tool | Does | Returns |
|------|------|---------|
| **`scan_besoins`** | Scan openings for a zone/sector/role, group by company, score the need | Ranked **prospect cards** (+ staffing agencies separated, + market aggregations) |
| **`market_stats`** | Market tension for a role/zone | Total offers, contract mix, experience demand, cadre share |

## The full prospecting flow (composable)

Needs Radar gives you the **raw signal**. A capable agent turns each prospect into a brief by chaining tools you already have:

```
needs-radar scan_besoins
        │  who's hiring (the intent signal)
        ▼
company registry  →  size, age, financial health, NAF
open-data sources →  public grants, public tenders won  (budget signals)
web/search/social →  recent news, funding, decision-maker
        ▼
LLM  →  the real need · why they're a fit · what to pitch · a drafted opener
```

The server stays focused (signal detection); enrichment and reasoning live in the agent. See **[BRAINSTORM.md](./BRAINSTORM.md)** for the staged design.

## Requirements

- **Python ≥ 3.8** — standard library only
- A free **[France Travail developer account](https://francetravail.io)** with the *Offres d'emploi v2* API subscribed (same credentials as the [France Travail MCP](https://github.com/mohamed-amine-ben-mallessa/francetravail-mcp))

## Limitations (read before you ship)

- 🇫🇷 **France only.** Source is France Travail. Combine with other job sources for wider coverage.
- 🪪 **No SIRET on offers.** You get company name + sector + size band, not the SIRET. Registry cross-referencing is by name (imperfect matching).
- 🧩 **Recruiting agencies still slip through.** Temp agencies are filtered by NAF code, but consulting/recruitment firms (different NAF) may appear as "prospects" — your enrichment/LLM step should flag them.
- 📊 **Scoring is a heuristic, not truth.** Volume + size + recency is a starting signal, not a guarantee of fit. Tune it for your ideal customer.
- ⚖️ **Use it ethically.** This is for legitimate B2B prospecting. Personalize every outreach. Don't spam.

## Roadmap

See **[BRAINSTORM.md](./BRAINSTORM.md)** — automatic registry/open-data enrichment, an LLM `analyze_prospect` tool (need + angle + drafted message), multi-source scanning (beyond France Travail), and scheduled "new needs in my zone" alerts.

## Data source

Built on the official **France Travail** *Offres d'emploi v2* API
([francetravail.io](https://francetravail.io)). The job data is provided by France Travail;
this project only calls their public API and analyzes the results.

## Built by & used by

Created and maintained by **Mohamed Amine Ben Mallessa**.

- 🏢 **[Sollea AI](https://sollea-ai.com)** — used in production.
- 🎯 **[Soléane](https://sol-ane.vercel.app/)** — B2B prospecting & outsourced sales firm,
  using Needs Radar for live hiring-signal prospecting.

## Disclaimer

> **Unofficial project.** Independent, open-source MCP server. **Not developed, affiliated with,
> sponsored, or endorsed by France Travail.** "France Travail" / "Pôle Emploi" and their logos
> are trademarks of their respective owners. This project only consumes France Travail's public
> API under their terms of use. For **legitimate, personalized B2B prospecting only** — respect
> the API conditions, rate limits, and applicable data-protection rules (GDPR).

## License

MIT.
