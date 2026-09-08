# MGI — LPs de SEO (preview para clientes)

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
