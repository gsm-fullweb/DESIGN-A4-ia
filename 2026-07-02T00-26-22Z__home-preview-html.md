---
target: home-preview.html
total_score: 32
p0_count: 0
p1_count: 3
timestamp: 2026-07-02T00-26-22Z
slug: home-preview-html
---
# Critique — home-preview.html (SmartCompany)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Hover/active states presentes; sem feedback de formulário (é landing) |
| 2 | Match System / Real World | 4 | PT-BR natural, linguagem do empresário |
| 3 | User Control and Freedom | 3 | Sem menu no mobile (<1080px) — só logo + CTA |
| 4 | Consistency and Standards | 3 | CAPS do H1 contraria a própria "Regra do CAPS Contido"; cards repetidos |
| 5 | Error Prevention | 3 | n/a em landing; CTAs claros |
| 6 | Recognition Rather Than Recall | 3 | Navegação some no mobile; resto discoverable |
| 7 | Flexibility and Efficiency | 3 | Âncoras funcionam; sem atalhos (ok p/ landing) |
| 8 | Aesthetic and Minimalist Design | 3 | Identidade forte, mas eyebrow em toda seção + grades de card iguais |
| 9 | Error Recovery | 3 | n/a |
| 10 | Help and Documentation | 3 | WhatsApp + Contato visíveis |
| **Total** | | **32/40** | **Good** |

## Anti-Patterns Verdict

**LLM:** Não parece "IA genérica" à primeira vista — a identidade navy+dourado é distinta e on-brand. Mas há tells de gramática-IA acumulados: eyebrow tracked uppercase em quase toda seção, numeração decorativa 01/02/03 no "Por que escolhem", e várias fileiras de cards idênticos (jornadas, why, formações, ebooks). Zero motion de entrada num hero de marca.

**Detector:** 11 achados — border-accent-on-rounded (pilar topo dourado, documentado), overused-font (Inter/Outfit — identidade herdada do React), 5× cor fora do DESIGN.md (#f8fafc, #062b16), radius 12px fora da escala, em-dash overuse (11), numbered-section-markers (01–05).

## Overall Impression
Visual premium e coeso, claramente melhor que o Divi atual. O maior risco não é feio — é **repetição**: card atrás de card com eyebrow atrás de eyebrow achata o ritmo e sinaliza template. E o **menu some no mobile**, um furo funcional real.

## What's Working
1. Identidade de marca forte (navy profundo + dourado raro + esmeralda de apoio) — a "Sala de Estratégia" aparece.
2. Ritmo de seções claras/escuras alternadas dá respiração e hierarquia.
3. CTAs objetivos e prova real (100 empresas, depoimentos) — autoridade sem grito.

## Priority Issues

- **[P1] Menu inexistente no mobile.** `.nav ul{display:none}` abaixo de 1080px, sem drawer/hambúrguer. No celular o visitante só vê logo + "AUTO DIAGNÓSTICO" — não navega. Fix: menu hambúrguer com `<dialog>`/painel. → `/impeccable adapt`
- **[P1] Eyebrow em toda seção.** Kicker tracked uppercase em ~8 seções é gramática-IA. Fix: manter 2-3 nomeados de propósito, cortar o resto; variar cadência. → `/impeccable typeset`
- **[P1] Grades de card idênticas.** Jornadas (4) + Why (3) + Formações (2) + Ebooks (2) — tudo card icon/título/texto. Fix: diferenciar (uma lista, um layout editorial, tamanhos variados). → `/impeccable layout`
- **[P2] H1/headings em CAIXA ALTA** contrariam a "Regra do CAPS Contido" do próprio DESIGN.md. Fix: caixa normal com `text-wrap:balance`; CAPS só em labels. → `/impeccable typeset`
- **[P2] Zero motion de entrada.** Register brand pede um page-load orquestrado. Fix: reveal do hero + stagger contido nos cards, respeitando `prefers-reduced-motion`. → `/impeccable animate`

## Persona Red Flags
**Casey (mobile):** menu some no mobile — navegação quebrada de fato; CTAs no topo, longe do polegar. **Jordan (first-timer):** primeira ação clara (diagnóstico), ok; muitos CTAs concorrentes na home podem dispersar. **Antonio-persona (empresário 45+):** corpo legível, mas alguns `#64748b` em cards ficam no limite AA — reforçar para leitura confortável.

## Minor Observations
- Cores fora do DESIGN.md (#f8fafc, #062b16) e radius 12px: adotar como token ou documentar.
- Em-dashes demais no copy — trocar por vírgula/ponto.
- Numeração 01/02/03 no "Why" é decorativa, não sequência real.
- border-top dourado no pilar: intencional e documentado (não é side-stripe lateral).

## Questions to Consider
- E se metade das seções abandonasse o card e usasse layout editorial (imagem + texto assimétrico)?
- O hero precisa de 2 CTAs competindo com o "AUTO DIAGNÓSTICO" do header?
- Qual seria a versão da home com 3 eyebrows no lugar de 8?
