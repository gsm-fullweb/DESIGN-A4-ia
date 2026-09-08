# Relatório final — build das LPs de SEO (MGI)

Diagnóstico completo em [`DIAGNOSTICO.md`](./DIAGNOSTICO.md). Este relatório
cobre o resultado do build e a validação (item D do pedido).

## Validação

- Servidor local (`python3 -m http.server`) rodado tanto em `dist-web/`
  quanto em `dist-standalone/`: todas as 5 páginas + `index.html` + `404.html`
  + os 103 assets locais referenciados por `dist-web` responderam **HTTP 200**
  (checagem automatizada, sem 404).
- Em cada arquivo de `dist-standalone/`, conferido que não sobra nenhuma
  referência a arquivo local — só restam `src="https://..."` para os 3
  serviços/CDNs de terceiros documentados no diagnóstico (fonte, formulário,
  vídeos, e as 3 fotos da Keenon só em `robos-para-limpeza.html`).

## Páginas processadas e tamanho final

| Página | `dist-standalone/` (auto-contido) | `dist-web/` (HTML, sem imagens) | Imagens embutidas |
|---|---|---|---|
| locacao-de-notebooks | 2,48 MB | 89 KB | 32 |
| locacao-de-dispositivos-moveis | 1,63 MB | 84 KB | 26 |
| robos-para-limpeza | 1,94 MB | 79 KB | 14 (11 embutidas + 3 externas, ver abaixo) |
| robos-para-logistica-e-movimentacao | 1,70 MB | 72 KB | 13 |
| robos-para-atendimento-e-entrega | 2,99 MB | 80 KB | 18 |

Nenhum arquivo passou de 5 MB — todos ficaram entre 1,6 e 3 MB. Ninguém
precisou ser bloqueado, mas `robos-para-limpeza.html` chegaria a **5,05 MB**
se todas as imagens fossem embutidas (3 fotos da Keenon aparecem duas vezes
na página — miniatura + slide do carrossel). Para respeitar o limite de
5 MB sem alterar o HTML/CSS, mantive só essas 3 fotos como link externo
(`www.keenon.com`) nesse arquivo específico; o resto da página (11 imagens,
inclusive o logo e as fotos "por que escolher a MGI") está embutido normal.

`dist-web/` não embute imagem nenhuma (por isso o HTML fica pequeno); as
imagens ficam em `dist-web/assets/img/<pagina>/` — ao todo **103 arquivos,
8,8 MB**.

## O que ainda depende de internet

Em **todas as 5 páginas** (nos dois builds):
- **Google Fonts** (`fonts.googleapis.com`) — carrega a fonte DM Sans.
- **HubSpot Forms** (`js.hsforms.net`) — script do formulário. Lembrete: o
  formulário do template **não é o oficial**, é só referência, como avisado
  no e-mail original.

Só em `robos-para-atendimento-e-entrega.html`:
- **3 vídeos demo** (`cdn.pudutech.com/.../*.mp4`) — não dá para embutir em
  base64 sem estourar muito o limite de 5 MB (são vídeos, não imagens).

Só em `robos-para-limpeza.html` (apenas na versão `dist-standalone`; na
versão `dist-web` essas 3 fotos foram baixadas normalmente):
- **3 fotos de produto** (`www.keenon.com/uploads/...`).

## Onde estão as coisas

```
lps-mgi/
├── source/            HTML original de cada LP (não editar — cópia fiel do
│                       repositório gsm-fullweb/mgi, commit 885acd8)
├── dist-standalone/    versão auto-contida (1 arquivo por LP, abre offline)
├── dist-web/           pasta pronta para "wrangler pages deploy ."
├── scripts/build.py    script que gera dist-standalone/ e dist-web/ a partir
│                       de source/ — rode de novo sempre que o HTML original
│                       mudar (ver DIAGNOSTICO.md e dist-web/README.md)
├── build_report.json   saída bruta do último build (tamanhos, deps externas)
├── DIAGNOSTICO.md
└── RELATORIO.md        este arquivo
```

## Como usar

- **Mostrar para cliente offline / por e-mail:** manda o arquivo de dentro de
  `dist-standalone/`. Abre em qualquer navegador, com layout, sem precisar
  de internet (exceto fonte/formulário/vídeos, que continuam remotos, como
  no site real).
- **Publicar com URL pública:** siga o `dist-web/README.md` (comando
  `wrangler pages deploy .`).
