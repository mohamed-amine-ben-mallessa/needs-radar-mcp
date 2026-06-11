# Needs Radar — design notes & roadmap

Working document. The *why* behind the server and where it's headed.

## Core insight

A job posting is the most reliable **public buying signal** a company emits. To post a role, a company has decided to spend money on a problem — and usually has adjacent, unmet needs around that same problem (a company hiring frontend devs likely also needs design, DevOps, SEO, QA, sometimes AI). Aggregators sell stale contact lists; we read live intent instead.

So: **reverse the prospecting question.** Not "who might be interested?" but "who just proved they're investing — and in what?"

## Staged architecture (intentional)

The design is deliberately built in stages so each layer can be validated before adding the next:

```
Stage 1 — SCAN     (shipped)  group offers by company, score intensity
Stage 2 — STATS    (shipped)  market aggregations per role/zone
Stage 3 — ENRICH   (planned)  company registry + open data per prospect
Stage 4 — ANALYZE  (planned)  LLM → real need + sales angle + drafted message
```

Stage 1 ships raw, explainable data first. No black-box LLM scoring before the inputs are trustworthy. This is a feature, not laziness — you can read exactly why a company ranks where it does.

## Scoring (Stage 1)

`score = openings × 3 + size_weight + recency_bonus`

- **openings × 3** — the dominant term. Multiple open roles = stronger, more urgent investment.
- **size_weight** — a band mapped from the employer headcount range. SMEs (≈10–99) are weighted highest: big enough to have budget, small enough to be reachable and to feel a single vendor's impact. Micro and very large orgs are weighted lower for prospecting purposes.
- **recency_bonus** — +3 if a posting is < 7 days old, +1 if < 30 days. Hot need vs. lingering listing.

Heuristic, transparent, tunable. Explicitly *not* presented as ground truth.

## Noise handling

Job feeds are polluted for prospecting purposes by intermediaries:

- **Temp/staffing agencies** (NAF `78.20Z`, `78.10Z`, `78.30Z`) repost dozens of client roles under their own name → they'd dominate any volume-based score. Filtered into a separate `intermediaires` bucket.
- **Anonymous employers** — France Travail sometimes hides the employer name → also bucketed aside.
- **Recruitment/consulting firms** with a *consulting* NAF (not staffing) still appear as prospects. We don't hard-filter them (some are legit targets); the downstream LLM step should flag them.

## Data reality (from the France Travail offer object)

What we get per offer: company **name**, `secteurActiviteLibelle`, `codeNAF`, `trancheEffectifEtab` (headcount band), location, ROME, contract, creation date, application URL. The **aggregations** (`filtresPossibles`) give free market stats.

What we *don't* get: **SIRET**. So registry enrichment (Stage 3) must match by company name — imperfect, needs fuzzy matching and human/LLM confirmation.

## Roadmap

### Stage 3 — enrichment (per prospect)
- [ ] **Company registry lookup by name** → SIREN, exact size, age, legal status, leadership. (No SIRET in offers, so name-match + confidence score.)
- [ ] **Open-data signals** → public grants/subsidies received, public tenders won. Strong budget/project indicators.
- [ ] **Web/news/social** → recent funding, product launches, the likely decision-maker.
- [ ] Cache enrichment so re-scans are cheap.

### Stage 4 — LLM analysis
- [ ] `analyze_prospect(company, offers, context)` → structured: **the real underlying need**, **why it's a fit**, **what to pitch**, **a drafted opener**. Model-agnostic; a fast/cheap model is enough for extraction. Fall back across providers to dodge rate limits.

### Coverage & ops
- [ ] **Multi-source scan** — add other job sources beyond France Travail (international, private tech) and dedupe by company name.
- [ ] **Scheduled alerts** — daily scan of a saved zone/sector → "new needs detected since yesterday" (passive prospecting).
- [ ] **Tunable scoring** — expose weights as parameters / an ideal-customer profile.
- [ ] **Export** — CSV / structured handoff to a CRM or notes vault.

## Non-goals
- Not a CRM. It produces signals and briefs; it doesn't manage the pipeline.
- Not a spam cannon. The README is explicit: legitimate, personalized B2B outreach only.
- Not a registry. It points at companies; authoritative company data comes from official registries it can call.

## Ethics
Public job data, used to inform legitimate B2B outreach, is fair game. The line we hold: enrich and reason to *personalize* outreach, never to mass-blast. Quality of fit over volume.
