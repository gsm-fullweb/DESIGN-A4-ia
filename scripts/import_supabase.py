#!/usr/bin/env python3
"""Importa data/leads.json para o Supabase (upsert por usuario).
Uso: SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 scripts/import_supabase.py
Nunca commitar a service key."""
import json, os, urllib.request

url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_KEY"]
CAMPOS = ["usuario","nome","url","faixa","motivo_exclusao","nicho_principal","nichos","seguidores",
          "curtidas_total","videos","verificado","engajamento","media_views","score_30mais",
          "sinais_30mais","pais_br","bio","link_bio","email","whatsapp","vende_live"]
leads = json.load(open("data/leads.json", encoding="utf-8"))
rows = [{k: l.get(k) for k in CAMPOS} for l in leads]  # status/obs/redes ficam fora: nao sobrescreve o CRM
for i in range(0, len(rows), 200):
    req = urllib.request.Request(
        f"{url}/rest/v1/leads?on_conflict=usuario", data=json.dumps(rows[i:i+200]).encode(), method="POST",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Prefer": "resolution=merge-duplicates,return=minimal"})
    urllib.request.urlopen(req).read()
    print("enviados", min(i + 200, len(rows)), "/", len(rows))
