#!/usr/bin/env python3
"""Gera crm/cliente.html (arquivo unico, dados embutidos) a partir de data/leads.json.
Nao commitar: contem dados de terceiros."""
import json
leads = json.load(open("data/leads.json", encoding="utf-8"))
for l in leads:
    l["bio"] = l["bio"][:300]
html = open("crm/index.html", encoding="utf-8").read()
data = json.dumps(leads, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("/*LEADS_PLACEHOLDER*/", "window.__LEADS__=" + data + ";")
open("crm/cliente.html", "w", encoding="utf-8").write(html)
print("crm/cliente.html gerado com", len(leads), "leads")
