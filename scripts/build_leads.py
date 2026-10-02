#!/usr/bin/env python3
"""Agrega o dataset do clockworks/tiktok-scraper (1 linha por video) em 1 lead por perfil.
Uso: python3 scripts/build_leads.py data/tiktok_raw.json data/leads.json
"""
import json, re, sys, statistics as st
from collections import defaultdict, Counter
from datetime import datetime, timezone

src, dst = sys.argv[1], sys.argv[2]
rows = json.load(open(src, encoding="utf-8"))

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
WPP = re.compile(r"(?:\+?55)?\s*\(?\d{2}\)?\s*9?\d{4}[-.\s]?\d{4}")
WPP_LINK = re.compile(r"(wa\.me/\d+|api\.whatsapp\.com\S*|whats\w*)", re.I)

NICHOS = {
    "Academia": ["academia", "musculacao", "treino", "personal", "hipertrofia", "fit"],
    "Alimentação": ["alimentacao", "receita", "nutri", "dieta", "emagrec"],
    "Suplementação": ["suplement", "whey", "creatina", "vitamina", "colageno"],
    "Corrida/Triatlo": ["corrida", "corredor", "triathlon", "triatlo", "maratona"],
    "CrossFit": ["crossfit"],
    "Bem-estar": ["bemestar", "bem-estar", "menopausa", "longevidade", "saude", "vida saudavel", "vidasaudavel"],
}
IDADE30 = ["40+", "40mais", "50+", "30+", "depois dos 40", "depois dos 30", "menopausa", "madura",
           "maturidade", "longevidade", "acima dos 40", "quarentona", "cinquentona", "master",
           "mulher 40", "40 anos", "50 anos", "45 anos", "35 anos", "mae de"]

OFFTOPIC = ["bolo", "confeit", "recheio", "doceria", "brigadeiro", "salgado", "marmita"]

def norm(s):
    import unicodedata
    return unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()

by = defaultdict(list)
for r in rows:
    a = r.get("authorMeta") or {}
    if a.get("name"):
        by[a["name"]].append(r)

leads = []
for name, vids in by.items():
    a = vids[0]["authorMeta"]
    sig = a.get("signature") or ""
    link = a.get("bioLink") or ""
    texto = norm(" ".join([sig] + [v.get("text") or "" for v in vids] +
                          [(" ".join(h.get("name", "") if isinstance(h, dict) else str(h) for h in (v.get("hashtags") or []))) for v in vids] +
                          [v.get("searchQuery") or "" for v in vids]))
    off = any(w in texto for w in OFFTOPIC)
    cont = {n: sum(texto.count(k) for k in kws) for n, kws in NICHOS.items()}
    nichos = [] if off else [n for n, c in sorted(cont.items(), key=lambda x: -x[1]) if c > 0]
    hits = [k for k in IDADE30 if norm(k) in texto]
    plays = [v.get("playCount") or 0 for v in vids]
    eng = [((v.get("diggCount") or 0) + (v.get("commentCount") or 0) + (v.get("shareCount") or 0)) / v["playCount"]
           for v in vids if v.get("playCount")]
    dates = sorted(v["createTimeISO"] for v in vids if v.get("createTimeISO"))
    langs = Counter(v.get("textLanguage") for v in vids)
    locs = Counter(v.get("locationCreated") for v in vids if v.get("locationCreated"))
    email = EMAIL.search(sig) or EMAIL.search(link)
    m = re.search(r"wa\.me/(\d{10,13})", link + " " + sig) or re.search(r"api\.whatsapp\.com\S*phone=(\d{10,13})", link + " " + sig)
    m2 = WPP.search(sig)
    wpp = m.group(1) if m else (re.sub(r"\s+", " ", m2.group(0)).strip() if m2 and len(re.sub(r"\D", "", m2.group(0))) >= 10 else None)
    fans = a.get("fans") or 0
    br = (locs.get("BR", 0) > 0) or langs.get("pt", 0) > 0
    score = min(100, len(hits) * 25 + (20 if "Bem-estar" in nichos else 0) + (10 if email else 0) + (10 if wpp else 0))
    ult = dates[-1] if dates else ""
    dias = (datetime.now(timezone.utc) - datetime.fromisoformat(ult.replace("Z", "+00:00"))).days if ult else 9999
    motivo = []
    if not br: motivo.append("Fora do Brasil")
    if fans < 5000: motivo.append("Menos de 5 mil seguidores")
    if fans > 500000: motivo.append("Acima de 500 mil (mega)")
    if not nichos: motivo.append("Nicho fora do foco")
    if not motivo:
        faixa = "A - Prioritário" if (score >= 50 or email or wpp) else "B - Qualificado"
    else:
        faixa = "C - Fora do perfil"
    leads.append({"faixa": faixa, "motivo_exclusao": "; ".join(motivo), "dias_sem_postar": dias,
        "usuario": name, "nome": a.get("nickName") or name, "url": a.get("profileUrl"),
        "seguidores": fans, "curtidas_total": a.get("heart") or 0, "videos": a.get("video") or 0,
        "verificado": bool(a.get("verified")), "bio": sig, "link_bio": link,
        "email": email.group(0) if email else "", "whatsapp": wpp or "",
        "nichos": nichos, "nicho_principal": nichos[0] if nichos else "Outros",
        "sinais_30mais": hits, "score_30mais": score,
        "pais_br": bool(br), "idioma_pt": langs.get("pt", 0) / len(vids),
        "ultimo_post": dates[-1] if dates else "",
        "media_views": int(st.mean(plays)) if plays else 0,
        "engajamento": round(st.mean(eng) * 100, 2) if eng else 0,
        "amostra_videos": len(vids),
        "status": "Novo", "obs": "",
    })

leads.sort(key=lambda l: (l["faixa"][0] != "C", l["score_30mais"], bool(l["email"]), l["seguidores"]), reverse=True)
json.dump(leads, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n = len(leads)
print("leads:", n, "| BR:", sum(l["pais_br"] for l in leads), "| email:", sum(bool(l["email"]) for l in leads),
      "| whatsapp:", sum(bool(l["whatsapp"]) for l in leads), "| score>0:", sum(l["score_30mais"] > 0 for l in leads))
print("seguidores >=5k:", sum(l["seguidores"] >= 5000 for l in leads), "| 5k-500k BR:",
      sum(5000 <= l["seguidores"] <= 500000 and l["pais_br"] for l in leads))
print(Counter(l["nicho_principal"] for l in leads))
print(Counter(l["faixa"] for l in leads))
