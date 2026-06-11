---
name: needs-radar
description: >
  Detect company needs and generate ranked B2B prospect lists from job postings (reverse
  prospecting) via the needs-radar MCP server. Use when the user wants to find prospects,
  see who is hiring in an area/sector, do B2B prospecting, identify potential clients/leads,
  or analyze a territory's hiring market. A company that is hiring has a project, a budget,
  and adjacent unmet needs. Keywords: prospect, prospecting, lead, B2B, who is hiring,
  potential clients, sales opportunity, hiring signals, company needs.
license: MIT
---

# Needs Radar — reverse B2B prospecting from job postings

A job posting is a buying signal. Use the `needs-radar` MCP server to turn postings into ranked prospects. Respond in the user's language.

## Tools
| Tool | Use |
|------|-----|
| `scan_besoins` | scan openings for a zone/sector/role → ranked prospect cards (+ staffing agencies separated, + market aggregations) |
| `market_stats` | market tension for a role/zone (volume, contract mix, experience demand) |

`scan_besoins` params: `motsCles` (need/role), `departement` (e.g. "69"), `commune` (INSEE), `region`, `distance`, `codeROME`, `maxOffres` (10–150, default 100).
Score = openings×3 + company-size weight (SMEs favored) + recency. `signalRecent: true` = hot (posting < 30 days).

## Full prospecting flow (compose with other tools the agent has)
The server returns the **raw signal**. To produce a real prospect brief, chain:
1. `scan_besoins` → companies hiring in the target.
2. Enrich each promising one: company registry (search by name → size, age, status, leadership), open-data (public grants/tenders = budget signals), web/search/social (news, funding, decision-maker).
3. LLM analysis: the real underlying need · why it's a fit · what to pitch · a drafted opener. A fast/cheap model is enough; fall back across providers to avoid rate limits.
4. Deliverable: prospect cards (company · need · why · offer · drafted message). Offer to save to a notes vault or export CSV.

## Variants
- **By zone**: `scan_besoins(departement="69")` with no keyword → everyone hiring in Lyon.
- **By need**: `scan_besoins(motsCles="site web")` → companies with a web need.
- **Multi-source**: cross with other job sources for companies absent from France Travail; dedupe by name.

## Notes & ethics
- France only (France Travail source). No SIRET in offers → registry matching is by name (imperfect).
- Staffing agencies are filtered by NAF; consulting/recruitment firms may still appear — flag them in analysis.
- Scoring is a transparent heuristic, not ground truth. Tune for the ideal customer.
- Legitimate, personalized B2B outreach only. Never spam.

## Setup
Needs `FT_CLIENT_ID` / `FT_CLIENT_SECRET` (free France Travail app subscribed to "Offres d'emploi v2"). See CONFIGURATION.md.
