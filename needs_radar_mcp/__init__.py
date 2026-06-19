#!/usr/bin/env python3
"""
MCP Needs Radar — détecte les besoins d'entreprises à partir des offres d'emploi.

Principe : une offre d'emploi = un signal d'investissement/projet. On scanne les offres
(France Travail, et plus tard jobspy), on REGROUPE par entreprise, on calcule un score
d'intensité du besoin, et on sort des fiches prospects exploitables.

v1 : scan France Travail groupé + scoring simple. (LLM / INSEE / data.gouv = étapes suivantes.)

Transport : stdio JSON-RPC pur (sans dépendance SDK). stdout = JSON-RPC, logs sur stderr.
Auth FT : OAuth2 client credentials (FT_CLIENT_ID / FT_CLIENT_SECRET en env).
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from collections import defaultdict

def log(*a):
    print(*a, file=sys.stderr, flush=True)

# ── France Travail auth + appel (réutilise le même mécanisme que le MCP francetravail) ──
FT_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
FT_API = "https://api.francetravail.io/partenaire/offresdemploi/v2"
SCOPE_OFFRES = "api_offresdemploiv2 o2dsoffre"
_tok = {}

def ft_token():
    now = time.time()
    if _tok.get("t") and _tok["exp"] - 30 > now:
        return _tok["t"]
    cid = os.environ.get("FT_CLIENT_ID", "").strip()
    csec = os.environ.get("FT_CLIENT_SECRET", "").strip()
    if not cid or not csec:
        raise RuntimeError("FT_CLIENT_ID / FT_CLIENT_SECRET manquants.")
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": cid,
        "client_secret": csec, "scope": SCOPE_OFFRES,
    }).encode()
    req = urllib.request.Request(FT_TOKEN_URL, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    _tok.update(t=d["access_token"], exp=now + int(d.get("expires_in", 1500)))
    return _tok["t"]

def ft_search(params):
    url = FT_API + "/offres/search?" + urllib.parse.urlencode(
        {k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ft_token()}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        if e.code == 204:
            return {}
        if e.code == 206:
            raw = e.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
        raise RuntimeError(f"HTTP {e.code} — {e.read().decode('utf-8','replace')[:200]}")

# ── Scoring d'intensité du besoin (simple et lisible) ──
# Tranches d'effectifs FT → poids "taille" (PME = cible idéale, pondérée haut ;
# micro et très grands groupes = un peu moins prioritaires pour de la prospection).
_EFFECTIF_SCORE = {
    "0 salarié": 1, "1 ou 2 salariés": 1, "3 à 5 salariés": 2, "6 à 9 salariés": 2,
    "10 à 19 salariés": 3, "20 à 49 salariés": 4, "50 à 99 salariés": 4,
    "100 à 199 salariés": 3, "200 à 249 salariés": 3, "250 à 499 salariés": 2,
    "500 à 999 salariés": 1, "1 000 à 1 999 salariés": 1,
}

def _recency_bonus(date_str):
    """Offre récente = besoin plus chaud. +3 si <7j, +1 si <30j."""
    if not date_str:
        return 0
    try:
        # format ISO 2026-05-28T17:42:15.379Z
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
        if days <= 7:
            return 3
        if days <= 30:
            return 1
    except Exception:
        pass
    return 0

def tool_scan_besoins(args):
    """Scanne les offres, regroupe par entreprise, score l'intensité du besoin."""
    n = int(args.get("maxOffres", 100))
    n = max(10, min(n, 150))
    params = {
        "motsCles": args.get("motsCles"),
        "departement": args.get("departement"),
        "commune": args.get("commune"),
        "region": args.get("region"),
        "distance": args.get("distance"),
        "codeROME": args.get("codeROME"),
        "range": f"0-{n-1}",
    }
    data = ft_search(params)
    offres = data.get("resultats", []) if isinstance(data, dict) else []

    groupes = defaultdict(lambda: {"offres": [], "effectif": None, "naf": None,
                                   "secteur": None, "recence": 0})
    for o in offres:
        nom = (o.get("entreprise", {}) or {}).get("nom") or "(employeur anonyme)"
        g = groupes[nom]
        g["offres"].append({
            "intitule": o.get("intitule"),
            "lieu": (o.get("lieuTravail", {}) or {}).get("libelle"),
            "contrat": o.get("typeContratLibelle") or o.get("typeContrat"),
            "rome": o.get("romeLibelle"),
            "date": o.get("dateCreation"),
            "url": (o.get("origineOffre", {}) or {}).get("urlOrigine"),
        })
        g["effectif"] = o.get("trancheEffectifEtab") or g["effectif"]
        g["naf"] = o.get("codeNAF") or g["naf"]
        g["secteur"] = o.get("secteurActiviteLibelle") or g["secteur"]
        g["recence"] = max(g["recence"], _recency_bonus(o.get("dateCreation")))

    # NAF des intermédiaires (intérim, recrutement) → ce ne sont pas des prospects directs
    # 78.20Z agences travail temporaire · 78.10Z placement de main d'œuvre · 78.30Z autre mise à dispo
    INTERMEDIAIRE_NAF = {"78.20Z", "78.10Z", "78.30Z"}

    fiches, intermediaires = [], []
    for nom, g in groupes.items():
        nb = len(g["offres"])
        taille = _EFFECTIF_SCORE.get((g["effectif"] or "").strip(), 2)
        # Score = intensité recrutement (x3, signal le plus fort) + taille + récence
        score = nb * 3 + taille + g["recence"]
        fiche = {
            "entreprise": nom,
            "score": score,
            "nbOffres": nb,
            "effectif": g["effectif"],
            "secteur": g["secteur"],
            "codeNAF": g["naf"],
            "signalRecent": g["recence"] > 0,
            "offres": g["offres"],
        }
        anonyme = nom == "(employeur anonyme)"
        intermediaire = (g["naf"] in INTERMEDIAIRE_NAF) or anonyme
        (intermediaires if intermediaire else fiches).append(fiche)

    fiches.sort(key=lambda f: f["score"], reverse=True)
    intermediaires.sort(key=lambda f: f["score"], reverse=True)

    # agrégations de marché (bonus gratuit)
    aggs = {}
    for f in (data.get("filtresPossibles", []) if isinstance(data, dict) else []):
        aggs[f.get("filtre")] = {v.get("valeurPossible"): v.get("nbResultats") for v in f.get("agregation", [])}

    return {
        "zone": args.get("departement") or args.get("commune") or args.get("region") or "national",
        "totalOffresScannees": len(offres),
        "entreprisesDetectees": len(fiches),
        "marche": aggs,
        "fiches": fiches,
        "intermediaires": intermediaires,  # intérim / cabinets de recrutement / anonymes (pas des prospects directs)
        "note": "Score = nbOffres×3 + taille(PME pondérée) + récence. 'fiches' = vrais prospects (entreprises qui "
                "recrutent en direct), triés par intensité du besoin. 'intermediaires' = intérim/recrutement/anonymes "
                "mis à part. Enrichir les fiches via INSEE (search_entreprises par nom) + data.gouv (aides/marchés publics), "
                "puis analyse LLM pour l'angle commercial.",
    }

def tool_market_stats(args):
    """Stats de marché d'un métier/zone via les agrégations France Travail."""
    params = {
        "motsCles": args.get("motsCles"),
        "departement": args.get("departement"),
        "region": args.get("region"),
        "codeROME": args.get("codeROME"),
        "range": "0-1",
    }
    data = ft_search(params)
    aggs = {}
    for f in (data.get("filtresPossibles", []) if isinstance(data, dict) else []):
        aggs[f.get("filtre")] = {v.get("valeurPossible"): v.get("nbResultats") for v in f.get("agregation", [])}
    # interprétation lisible
    contrats = aggs.get("typeContrat", {})
    total = sum(contrats.values()) if contrats else 0
    return {
        "zone": args.get("departement") or args.get("region") or "national",
        "totalOffres": total,
        "repartitionContrats": contrats,
        "repartitionExperience": aggs.get("experience", {}),
        "repartitionQualification": aggs.get("qualification", {}),
        "natureContrat": aggs.get("natureContrat", {}),
        "legende": {
            "experience": "0=débutant, 1=<1an, 2=1-3ans, 3=>3ans, 4=expérimenté",
            "qualification": "0=non-cadre, 9=cadre, X=non précisé",
            "natureContrat": "E1=contrat classique, E2=alternance, FS/NS=autres",
        },
    }

TOOLS = [
    {
        "name": "scan_besoins",
        "description": "Détecte les BESOINS d'entreprises à partir des offres d'emploi France Travail, par zone géo / secteur / métier. Regroupe les offres par entreprise et score l'intensité du besoin (nb d'offres ouvertes = signal fort). Sort des fiches prospects triées : entreprise, nb d'offres, secteur, effectif, NAF, postes recherchés. Idéal pour la prospection B2B : une entreprise qui recrute a un projet, un budget, et des besoins connexes non couverts. Filtres : motsCles, departement (ex '69'), commune, region, distance (km), codeROME, maxOffres (10-150, défaut 100).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "motsCles": {"type": "string", "description": "Domaine/besoin (ex 'développeur', 'data', 'marketing digital')"},
                "departement": {"type": "string", "description": "Code département (ex '75', '69')"},
                "commune": {"type": "string", "description": "Code INSEE commune"},
                "region": {"type": "string"},
                "distance": {"type": "integer", "description": "Rayon km autour de la commune"},
                "codeROME": {"type": "string", "description": "Code ROME pour cibler un métier précis"},
                "maxOffres": {"type": "integer", "description": "Nb d'offres à scanner (10-150, défaut 100)"},
            },
        },
    },
    {
        "name": "market_stats",
        "description": "Statistiques de marché d'un métier/secteur sur une zone (via les agrégations France Travail) : nombre total d'offres, répartition CDI/CDD/alternance, niveaux d'expérience demandés, part de cadres. Utile pour cibler les zones qui recrutent le plus, ou évaluer la tension d'un métier.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "motsCles": {"type": "string"},
                "departement": {"type": "string"},
                "region": {"type": "string"},
                "codeROME": {"type": "string"},
            },
        },
    },
]

DISPATCH = {"scan_besoins": tool_scan_besoins, "market_stats": tool_market_stats}

def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def handle(msg):
    mid = msg.get("id")
    method = msg.get("method")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
            "serverInfo": {"name": "needs-radar", "version": "1.0.0"}}}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        p = msg.get("params", {})
        fn = DISPATCH.get(p.get("name"))
        if not fn:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Outil inconnu: {p.get('name')}"}}
        try:
            res = fn(p.get("arguments", {}) or {})
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]}}
        except Exception as e:
            log("ERREUR", p.get("name"), ":", repr(e))
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": f"Erreur: {e}"}], "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Méthode inconnue: {method}"}}
    return None

def main():
    log("needs-radar MCP démarré (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            send(resp)

if __name__ == "__main__":
    main()
