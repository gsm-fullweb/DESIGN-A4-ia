# DESIGN-A4-ia

Repositório destinado à criação e armazenamento de modelos base de design (Portabilidade) e integrações de componentes para as landing pages e sites.

## 📦 O que temos aqui?

### 1. Modelo Base Divi (`divi/layout-modelo-base.json`)

Este arquivo contém o **Layout de Portabilidade do Divi (Divi Builder)**, criado para evitar a montagem repetitiva, módulo por módulo. Ele já traz o nosso padrão de design (padrão React) com todas as fontes, cores, espaçamentos, bordas e cantos pré-configurados.

Ele conta com 3 seções completas prontas para importação (via menu `⋯` → `Portabilidade` → `Import`):

*   **Hero da Home:** 
    *   Badge dourada (`#D4AF37`)
    *   Título Principal (H1) utilizando a tipografia **Outfit 800 Caixa Alta** (48px no desktop / 30px no mobile)
    *   Subtítulo descritivo
    *   Dois botões lado a lado (Botão principal Dourado + Botão secundário Outline)
    *   Linha de Confiança (Trust line)
*   **Grade de 3 Cards Numerados:**
    *   Cards (01, 02 e 03) intitulados *"Por que os empresários escolhem"*
    *   Efeito de hover configurado na cor dourada e leve sombra (Box Shadow).
*   **CTA Auto Diagnóstico:**
    *   Seção de Call to Action isolada, pronta para ser salva como um **item global** da Divi Library para reutilização através de todo o site.

## 🚀 Como utilizar

1. No WordPress, abra a página com o **Divi Builder**.
2. Clique no ícone de opções (três pontinhos roxos `⋯` no centro inferior).
3. Selecione o ícone de **Portabilidade** (setas bidirecionais).
4. Vá até a aba **Importar** e selecione o arquivo `layout-modelo-base.json`.
5. O Divi 5 importará automaticamente o formato clássico e fará a conversão estrutural logo na primeira edição.

## 🛠️ Tecnologias / Especificações Visuais
*   **Fontes:** Outfit (Google Fonts)
*   **Cores Primárias:** Dourado (`#D4AF37`), Dark (`#1e1e1e`), Light (`#ffffff`, `#f9f9f9`)
