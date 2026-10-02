#!/usr/bin/env python3
"""Le o perfil publico de cada @ da lista de lives e grava data/lives.json (mesmo schema de leads).
Uso: python3 scripts/add_lives.py ruanbrasil__ larabritonareal ...   (build_leads.py incorpora o arquivo)"""
import json, re, sys, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
WPP_LINK = re.compile(r"wa\.me/(\d{10,13})|phone=(\d{10,13})")
out = []
for h in sys.argv[1:]:
    h = h.strip().lstrip("@")
    req = urllib.request.Request(f"https://www.tiktok.com/@{h}", headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
    try:
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        blob = re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.S)
        info = json.loads(blob.group(1))["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
        u, s = info["user"], info["stats"]
    except Exception as e:
        print("FALHOU", h, e); u = s = None
    sig = (u or {}).get("signature", "")
    link = ((u or {}).get("bioLink") or {}).get("link", "") if u else ""
    em = EMAIL.search(sig + " " + link)
    wp = WPP_LINK.search(link + " " + sig)
    out.append({
        "usuario": h, "nome": (u or {}).get("nickname", h), "url": f"https://www.tiktok.com/@{h}",
        "seguidores": (s or {}).get("followerCount", 0), "curtidas_total": (s or {}).get("heartCount", 0),
        "videos": (s or {}).get("videoCount", 0), "verificado": bool((u or {}).get("verified")),
        "bio": sig, "link_bio": link, "email": em.group(0) if em else "",
        "whatsapp": (wp.group(1) or wp.group(2)) if wp else "",
        "nichos": [], "nicho_principal": "Vendas por live", "sinais_30mais": [], "score_30mais": 0,
        "pais_br": (u or {}).get("region", "BR") == "BR", "idioma_pt": 1.0, "ultimo_post": "",
        "media_views": 0, "engajamento": 0, "amostra_videos": 0, "dias_sem_postar": 0,
        "faixa": "A - Prioritário", "motivo_exclusao": "", "vende_live": True,
        "origem": "lista do cliente (vende por live)", "status": "Novo", "obs": "",
    })
    print(f"@{h}: {out[-1]['seguidores']} seg | {sig[:60]!r} | {out[-1]['link_bio']}")
json.dump(out, open("data/lives.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
