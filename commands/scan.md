---
description: Scan companies hiring in a zone/sector and rank them as B2B prospects
argument-hint: <need or role> in <department/city>
---

Detect company needs and build a ranked prospect list using the `needs-radar` MCP server (`scan_besoins` tool).

User request: $ARGUMENTS

Steps:
1. Parse the target: a need/role keyword (e.g. "developer", "site web", "data") and a zone (department number like 69, or a city → INSEE code).
2. Call `scan_besoins` (default maxOffres 100).
3. Present the **ranked prospects** (`fiches`): Company · openings · staff size · sector · `[hot]` if recent. Note how many staffing agencies were set aside.
4. Briefly read the market aggregations (overall hiring volume in the zone).
5. Offer the enrichment flow for the top prospects: cross-reference a company registry (by name) and open data (public grants/tenders), pull recent news / the decision-maker, then summarize the likely need + an angle of approach.
6. Keep it ethical: this is for legitimate, personalized B2B outreach — not mass mailing.
