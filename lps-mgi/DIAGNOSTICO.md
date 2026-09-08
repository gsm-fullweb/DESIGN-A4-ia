# Diagnóstico — LPs de SEO (MGI)

## O problema real (por que o Drive quebrava o layout)

A pasta do Google Drive que você mandou **não continha mais os arquivos
`.html` originais**. O Drive tem a opção "converter uploads para o formato
do Google Docs" ativada nessa conta — assim que cada `.html` foi enviado,
o Drive o transformou num Google Doc e **descartou o arquivo original**
(HTML, CSS, tudo). O que sobrou lá é uma reinterpretação do Docs (fontes
Arial genéricas, sem CSS, sem classes, `<img>` sem `src`), não o site.

Isso não tem conserto "empacotando melhor" — o dado de origem já foi
perdido no Drive. Para recuperar os arquivos de verdade, usei uma pista que
estava na própria pasta: dentro dela havia uma cópia sincronizada de uma
pasta `.git/`, cujo `config` apontava para
`https://github.com/gsm-fullweb/mgi`. Clonei esse repositório (leitura) e
os 5 HTMLs pedidos estavam lá, intactos, no commit
`885acd8` ("Adiciona LPs padronizadas..."). **Recomendação prática:**
desative a conversão automática no Drive (Configurações → Geral →
desmarcar "Converter uploads") antes de subir HTML por lá de novo — ou,
mais simples ainda, mande a pasta zipada.

## O que os arquivos realmente são

Os 5 arquivos não são páginas HTML completas — são **fragmentos de bloco
"HTML customizado" do WordPress** (`<!-- wp:html --> ... <!-- /wp:html -->`),
pensados para colar dentro do Gutenberg. Por isso:

- Não têm `<!DOCTYPE>`, `<html>`, `<head>`, `<body>` nem `<title>`.
- O CSS já vem **inline**, em dois blocos `<style>` no topo de cada arquivo
  (não é um `.css` externo quebrado — é só que sem `<head>` ele fica solto
  no meio do `<body>`).
- Não há nenhum `<script>` local nem fonte (`@font-face`) local.
- **Nenhum caminho relativo quebrado.** Todas as imagens usam URL absoluta,
  apontando para a biblioteca de mídia do WordPress em produção
  (`mgi.com.br`, `grupomgitech.com.br`) ou para CDNs de fabricante
  (`www.keenon.com`, `cdn.pudutech.com`).

## Dependências externas (precisam de internet mesmo no build final)

| Recurso | Domínio | Uso |
|---|---|---|
| Fonte DM Sans | `fonts.googleapis.com` | `@import` dentro do `<style>`, em todas as 5 páginas |
| Formulário de contato | `js.hsforms.net` | script do HubSpot, embutido no fim do `<body>` (o formulário do template **não é o oficial**, é placeholder) |
| Vídeos demo do robô Keenon | `cdn.pudutech.com` | 3 arquivos `.mp4` em `robos-para-atendimento-e-entrega.html` — grandes demais para base64, mantidos como link |
| 3 fotos de produto Keenon | `www.keenon.com` | só em `robos-para-limpeza.html`; mantidas externas nesse arquivo específico porque aparecem 2x na página (miniatura + slide) e, embutidas, estourariam o limite de 5MB pedido |

## Assets soltos no repositório, sem uso nas 5 páginas

O repositório `gsm-fullweb/mgi` também tem imagens soltas na raiz
(`hero-banner-fundo.jpg/webp`, `woman_crop*.png`,
`robos-locacao-movimentacao.jpg`, `hero-banner-dispositivos-moveis.jpg`,
`hero-banner-clean-bg.jpg`) e em `backups/` (fotos de notebook em `.avif`).
Nenhuma delas é referenciada pelos 5 arquivos pedidos — parecem material
de apoio de uma versão anterior. Não foram usadas neste build.

## Resumo

- ✅ Sem caminho relativo quebrado, sem asset local ausente.
- ⚠️ Os "arquivos originais" não são páginas completas — são fragmentos
  WordPress. O build embrulha cada um num HTML5 completo (isso é o único
  ponto onde adiciono algo: `<!DOCTYPE>`/`<head>`/`<body>`/`<title>`; nenhuma
  classe, id ou regra CSS foi alterada).
- ⚠️ Todas as imagens dependem hoje do site WordPress em produção — se
  alguém apagar/mover um arquivo de mídia lá, a LP quebra mesmo estando
  "pronta". O build `dist-web` resolve isso baixando as imagens para dentro
  do projeto.
