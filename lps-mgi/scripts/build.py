#!/usr/bin/env python3
"""
Build script: LPs de SEO (MGI) -> versão auto-contida (dist-standalone) e
versão pronta para Cloudflare Pages (dist-web).

Uso:
    python3 build.py

Lê os fragmentos HTML originais em ./source/*.html (blocos WordPress
"wp:html" — sem <!DOCTYPE>/<head>/<body>) e gera:

  - dist-standalone/<slug>.html
        Documento HTML5 completo e autocontido: CSS já embutido é movido para
        <head>, imagens locais/da biblioteca de mídia viram data URI base64.
        Continuam dependendo de internet apenas os serviços que são,
        de fato, serviços externos (não "assets da página"): Google Fonts,
        o script do formulário HubSpot e, quando existirem, vídeos .mp4
        (não são embutidos por serem grandes demais para base64) e imagens
        de terceiros que estourariam o limite de 5MB do arquivo final
        (ver PER_PAGE_EXTRA_REMOTE_HOSTS).

  - dist-web/<slug>.html + dist-web/assets/img/<slug>/*
        Documento HTML5 completo com as imagens baixadas e referenciadas por
        caminho relativo (./assets/img/<slug>/arquivo.ext), pronto para
        deploy estático. index.html, 404.html, _headers, _redirects e
        wrangler.toml também são gerados.

Reexecutar este script é seguro e idempotente: baixa os assets uma vez para
./.cache/ e reaproveita nas próximas rodadas (apague ./.cache/ para forçar
um novo download).

Não edite os arquivos dentro de dist-standalone/ ou dist-web/ à mão — eles
são sempre regerados a partir de source/. Edite apenas os arquivos em
source/ (ou peça o arquivo original atualizado) e rode o script de novo.
"""
import re
import os
import sys
import json
import base64
import shutil
import mimetypes
import urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # lps-mgi/
SRC_DIR = os.path.join(HERE, "source")
STANDALONE_DIR = os.path.join(HERE, "dist-standalone")
WEB_DIR = os.path.join(HERE, "dist-web")
CACHE_DIR = os.path.join(HERE, ".cache")

PAGES = {
    "locacao-de-notebooks": "Locação de Notebooks Corporativos de Alta Performance",
    "locacao-de-dispositivos-moveis": "Locação de Dispositivos Móveis Corporativos",
    "robos-para-limpeza": "Robôs Autônomos para Limpeza e Higienização de Grandes Áreas",
    "robos-para-logistica-e-movimentacao": "Robôs para Logística e Movimentação",
    "robos-para-atendimento-e-entrega": "Robôs para Atendimento e Entrega de Alta Performance",
}

DESCRIPTIONS = {
    "locacao-de-notebooks": "Locação e outsourcing de notebooks corporativos de alta performance com suporte técnico dedicado.",
    "locacao-de-dispositivos-moveis": "Outsourcing e locação de smartphones, tablets e coletores de dados corporativos.",
    "robos-para-limpeza": "Robôs autônomos para limpeza e higienização de grandes áreas comerciais e industriais.",
    "robos-para-logistica-e-movimentacao": "Robôs autônomos para logística, movimentação de cargas e otimização de operações.",
    "robos-para-atendimento-e-entrega": "Robôs de atendimento e entrega para hotelaria, restaurantes e recepção corporativa.",
}

# Hosts cujo conteúdo NUNCA é embutido no build auto-contido (serviços/CDNs de
# terceiros de verdade, não assets desta página).
EXTERNAL_HOSTS_ALWAYS_REMOTE = ("js.hsforms.net",)

# robos-para-limpeza.html repete 3 fotos da Keenon (thumb + slide), o que
# sozinho estoura o limite de 5MB por arquivo pedido para o build
# auto-contido. Mantemos essas 3 fotos (CDN do fabricante) externas só nessa
# página para caber no limite; todo o resto continua embutido.
PER_PAGE_EXTRA_REMOTE_HOSTS = {
    "robos-para-limpeza": ("www.keenon.com",),
}

MAX_STANDALONE_BYTES = 5 * 1024 * 1024

STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.S)
LDJSON_RE = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', re.S)
SRC_RE = re.compile(r'(src=["\'])(https?://[^"\']+)(["\'])')


def cache_path(url):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", url.split("://", 1)[1])
    return os.path.join(CACHE_DIR, safe)


def download(url):
    """Download url once, cache to disk, return (ok, local_path, size, mime)."""
    dst = cache_path(url)
    if os.path.exists(dst):
        return True, dst, os.path.getsize(dst)
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        # WP media filenames can contain literal non-ASCII chars (e.g. an
        # ellipsis from a truncated auto-generated name); percent-encode the
        # path so urllib can build a valid request.
        safe_url = urllib.parse.quote(url, safe=":/?=&%")
        req = urllib.request.Request(safe_url, headers={"User-Agent": "Mozilla/5.0 (lp-build-script)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dst, "wb") as f:
            f.write(data)
        return True, dst, len(data)
    except Exception as e:
        print(f"  AVISO: falha ao baixar {url}: {e}", file=sys.stderr)
        return False, None, 0


def extract_head_blocks(content):
    blocks = []
    for m in STYLE_RE.finditer(content):
        blocks.append((m.start(), m.group(0)))
    for m in LDJSON_RE.finditer(content):
        blocks.append((m.start(), m.group(0)))
    blocks.sort(key=lambda b: b[0])
    head_blocks = [b[1] for b in blocks]
    body = content
    for start, text in sorted(blocks, key=lambda b: -b[0]):
        body = body[:start] + body[start + len(text):]
    return body.strip(), head_blocks


def strip_trailing_hsforms_script(body):
    return re.sub(
        r'\s*<script src="https://js\.hsforms\.net/forms/embed/developer/114501\.js"[^>]*>\s*</script>',
        "",
        body,
    )


def sanitize_filename(name):
    return name.replace("…", "-")


def wrap_document(title, description, head_extra, body_inner, extra_head_comment=""):
    head_extra_str = "\n    ".join(head_extra)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | MGI</title>
    <meta name="description" content="{description}">
{extra_head_comment}    {head_extra_str}
</head>
<body>
{body_inner}
    <script src="https://js.hsforms.net/forms/embed/developer/114501.js" defer></script>
</body>
</html>
"""


def build():
    os.makedirs(STANDALONE_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)
    if os.path.exists(f"{WEB_DIR}/assets/img"):
        shutil.rmtree(f"{WEB_DIR}/assets/img")
    os.makedirs(f"{WEB_DIR}/assets/img", exist_ok=True)

    report = {}

    for slug, title in PAGES.items():
        src_path = os.path.join(SRC_DIR, f"{slug}.html")
        with open(src_path, encoding="utf-8") as f:
            raw = f.read()
        raw = raw.replace("<!-- wp:html -->", "").replace("<!-- /wp:html -->", "").strip()

        body, head_blocks = extract_head_blocks(raw)
        body = strip_trailing_hsforms_script(body)

        extra_remote_hosts = PER_PAGE_EXTRA_REMOTE_HOSTS.get(slug, ())
        standalone_remote_hosts = EXTERNAL_HOSTS_ALWAYS_REMOTE + extra_remote_hosts

        all_text = body + "\n" + "\n".join(head_blocks)
        urls_in_page = sorted(set(m.group(2) for m in SRC_RE.finditer(all_text)))

        images, videos, external_cdn = [], [], set()
        for u in urls_in_page:
            if u.endswith(".mp4"):
                videos.append(u)
            elif any(h in u for h in EXTERNAL_HOSTS_ALWAYS_REMOTE):
                external_cdn.add(u)
            else:
                images.append(u)
        if "fonts.googleapis.com" in "\n".join(head_blocks):
            external_cdn.add("https://fonts.googleapis.com/css2?family=DM+Sans...")

        print(f"[{slug}] baixando {len(images)} imagem(ns)...")
        fetched = {}
        for u in images:
            ok, path, size = download(u)
            fetched[u] = (ok, path, size)

        # ---------------- dist-standalone ----------------
        def to_data_uri(match):
            prefix, url, suffix = match.group(1), match.group(2), match.group(3)
            if url.endswith(".mp4") or any(h in url for h in standalone_remote_hosts):
                return match.group(0)
            ok, path, size = fetched.get(url, (False, None, 0))
            if not ok:
                return match.group(0)
            with open(path, "rb") as imgf:
                raw_bytes = imgf.read()
            mime = "image/avif" if url.endswith(".avif") else (mimetypes.guess_type(url.split("?")[0])[0] or "application/octet-stream")
            b64 = base64.b64encode(raw_bytes).decode("ascii")
            return f'{prefix}data:{mime};base64,{b64}{suffix}'

        standalone_body = SRC_RE.sub(to_data_uri, body)
        standalone_head_blocks = [SRC_RE.sub(to_data_uri, h) for h in head_blocks]

        extra_note = (
            f", fotos de produto de terceiros ({', '.join(extra_remote_hosts)}, mantidas externas para o arquivo ficar abaixo de 5MB)"
            if extra_remote_hosts else ""
        )
        standalone_html = wrap_document(
            title, DESCRIPTIONS[slug], standalone_head_blocks, standalone_body,
            extra_head_comment=(
                "    <!-- Build auto-contido: imagens embutidas em base64. Dependem de internet: "
                "Google Fonts (DM Sans), formulário HubSpot (js.hsforms.net)"
                + (", vídeos demo (cdn.pudutech.com)" if videos else "")
                + extra_note + ". -->\n"
            ),
        )
        standalone_bytes = len(standalone_html.encode("utf-8"))
        skipped = standalone_bytes > MAX_STANDALONE_BYTES
        if skipped:
            print(f"AVISO [{slug}] standalone ficaria com {standalone_bytes/1024/1024:.2f}MB (> 5MB) — NAO gerado.", file=sys.stderr)
        else:
            with open(os.path.join(STANDALONE_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
                f.write(standalone_html)

        # ---------------- dist-web ----------------
        asset_dir = os.path.join(WEB_DIR, "assets", "img", slug)
        os.makedirs(asset_dir, exist_ok=True)

        def to_relative(match):
            prefix, url, suffix = match.group(1), match.group(2), match.group(3)
            if url.endswith(".mp4") or any(h in url for h in EXTERNAL_HOSTS_ALWAYS_REMOTE):
                return match.group(0)
            ok, path, size = fetched.get(url, (False, None, 0))
            if not ok:
                return match.group(0)
            basename = sanitize_filename(os.path.basename(url.split("?")[0]))
            dst = os.path.join(asset_dir, basename)
            if not os.path.exists(dst):
                shutil.copyfile(path, dst)
            return f'{prefix}./assets/img/{slug}/{basename}{suffix}'

        web_body = SRC_RE.sub(to_relative, body)
        web_head_blocks = [SRC_RE.sub(to_relative, h) for h in head_blocks]
        web_html = wrap_document(title, DESCRIPTIONS[slug], web_head_blocks, web_body)
        with open(os.path.join(WEB_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(web_html)

        report[slug] = {
            "n_images": len(images),
            "n_videos": len(videos),
            "external_cdn": sorted(external_cdn),
            "videos": videos,
            "standalone_size_bytes": None if skipped else standalone_bytes,
            "standalone_skipped_over_5mb": skipped,
            "web_size_bytes": os.path.getsize(os.path.join(WEB_DIR, f"{slug}.html")),
        }

    build_hosting_extras()

    with open(os.path.join(HERE, "build_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))


def build_hosting_extras():
    cards = "\n".join(
        f'''      <a class="card" href="./{slug}.html">
        <h2>{title}</h2>
        <p>{DESCRIPTIONS[slug]}</p>
      </a>'''
        for slug, title in PAGES.items()
    )
    index_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MGI — LPs de SEO (modelos)</title>
    <meta name="description" content="Índice das landing pages modelo da MGI para revisão.">
    <meta name="robots" content="noindex, nofollow">
    <style>
        body {{ margin:0; font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif; background:#f4f7fb; color:#1c2733; }}
        header {{ padding:48px 24px 24px; text-align:center; }}
        header h1 {{ margin:0 0 8px; font-size:1.8rem; }}
        header p {{ color:#5b6b7b; margin:0; }}
        .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:20px; max-width:1100px; margin:0 auto; padding:24px; }}
        .card {{ display:block; background:#fff; border:1px solid #e3e9f0; border-radius:14px; padding:20px; text-decoration:none; color:inherit; box-shadow:0 10px 30px rgba(11,36,64,.06); transition:transform .15s ease; }}
        .card:hover {{ transform:translateY(-3px); }}
        .card h2 {{ margin:0 0 8px; font-size:1.1rem; color:#123a63; }}
        .card p {{ margin:0; color:#5b6b7b; font-size:.92rem; line-height:1.5; }}
    </style>
</head>
<body>
    <header>
        <h1>LPs de SEO — MGI (modelos)</h1>
        <p>Templates em HTML para as páginas canônicas. Formulários de exemplo, não oficiais.</p>
    </header>
    <div class="grid">
{cards}
    </div>
</body>
</html>
"""
    with open(os.path.join(WEB_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    not_found_html = index_html.replace(
        "<h1>LPs de SEO — MGI (modelos)</h1>", "<h1>Página não encontrada</h1>"
    ).replace(
        "<p>Templates em HTML para as páginas canônicas. Formulários de exemplo, não oficiais.</p>",
        "<p>O endereço acessado não existe. Veja as páginas disponíveis abaixo.</p>",
    )
    with open(os.path.join(WEB_DIR, "404.html"), "w", encoding="utf-8") as f:
        f.write(not_found_html)

    with open(os.path.join(WEB_DIR, "_headers"), "w", encoding="utf-8") as f:
        f.write(
            "/assets/*\n"
            "  Cache-Control: public, max-age=31536000, immutable\n"
            "\n"
            "/*.html\n"
            "  Cache-Control: public, max-age=3600, must-revalidate\n"
            "\n"
            "/\n"
            "  Cache-Control: public, max-age=3600, must-revalidate\n"
        )

    with open(os.path.join(WEB_DIR, "_redirects"), "w", encoding="utf-8") as f:
        f.write("/*  /404.html  404\n")

    with open(os.path.join(WEB_DIR, "wrangler.toml"), "w", encoding="utf-8") as f:
        f.write(
            'name = "mgi-lps-preview"\n'
            'compatibility_date = "2026-09-01"\n'
            'pages_build_output_dir = "."\n'
        )

    readme = """# MGI — LPs de SEO (preview para clientes)

Pasta pronta para deploy no **Cloudflare Pages**. Cada página é um HTML completo,
com as imagens em `./assets/img/<pagina>/` (caminhos relativos — não dependem
mais da biblioteca de mídia do WordPress). Fontes (Google Fonts), o script do
formulário (HubSpot) e os vídeos de demonstração (Pudu Tech) continuam
carregando via CDN, então o visitante precisa de internet para ver tudo
perfeito — igual à página real no site.

## Páginas

- `index.html` — hub com link para todas as LPs (não indexado: `noindex`).
- `locacao-de-notebooks.html`
- `locacao-de-dispositivos-moveis.html`
- `robos-para-limpeza.html`
- `robos-para-logistica-e-movimentacao.html`
- `robos-para-atendimento-e-entrega.html`
- `404.html` — página de fallback (ver `_redirects`).

## Deploy (primeira vez)

```bash
npm install -g wrangler        # se ainda não tiver
cd lps-mgi/dist-web
wrangler login                 # autentica sua conta Cloudflare
wrangler pages project create mgi-lps-preview
wrangler pages deploy . --project-name=mgi-lps-preview
```

Isso gera uma URL pública do tipo `https://mgi-lps-preview.pages.dev` para
mandar ao cliente.

## Publicar uma nova versão

Depois de qualquer alteração nos arquivos desta pasta (ou depois de rodar de
novo `scripts/build.py` na raiz do projeto):

```bash
cd lps-mgi/dist-web
wrangler pages deploy . --project-name=mgi-lps-preview
```

Cada deploy cria uma URL de preview própria e atualiza a URL de produção do
projeto. Não precisa recriar o projeto nem mudar o `wrangler.toml`.

### Uma URL por cliente

Para dar uma URL fixa e separada por cliente em vez de mandar a mesma pasta
inteira, duplique este `dist-web/` num projeto Cloudflare Pages novo por
cliente (`wrangler pages project create <slug-do-cliente>`), ou use os
"preview deployments" do Cloudflare Pages, que já geram uma URL única por
deploy automaticamente (sem precisar de projetos separados).

## Regerar esta pasta a partir do HTML original

Este build é gerado por script a partir de `lps-mgi/source/*.html` — **não
edite os arquivos aqui (nem os de `dist-standalone/`) diretamente**, pois
qualquer alteração se perde na próxima rodada. Para atualizar:

1. Substitua o arquivo correspondente em `lps-mgi/source/`.
2. Rode `python3 lps-mgi/scripts/build.py` a partir da raiz do repositório.

O script baixa as imagens uma vez para `lps-mgi/.cache/` e reaproveita nas
próximas execuções (apague essa pasta para forçar um novo download).
"""
    with open(os.path.join(WEB_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    build()
