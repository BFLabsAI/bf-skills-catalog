---
name: ic-design-system
description: >
  Design system da Inteligência Comercial / Ramon Pessoa / R7 Treinamentos.
  Produz peças de marca em canvas fixo — ads (1:1, 4:5, 9:16, 16:9), stories e
  covers de Reels, one-pagers A4, infográficos, quote cards, mídia de WhatsApp e
  thumbnails de YouTube. Use sempre que o pedido envolver criativo, post,
  carrossel, anúncio, story, capa, banner, thumbnail, relatório, proposta ou
  qualquer peça visual da IC, do PIC, da R7 ou do Ramon Pessoa. Também use
  quando o usuário pedir para aplicar "a marca", "o design system" ou "a
  identidade" em qualquer artefato.
---

# Design System — Inteligência Comercial

Sistema de peças em canvas fixo. Cada template é um arquivo HTML que exporta
para PNG ou PDF. **Não escreva CSS do zero e não invente tokens.**

## Ordem obrigatória

1. **Ler `DESIGN.md`** — regras de decisão, cor, tipografia, voz e as 12 regras duras.
2. **Ler `surfaces.md`** — achar a linha da superfície pedida: canvas, safe area, `--scale`, fonte mínima.
3. **Copiar o template mais próximo** de `templates/`. Se nenhum servir, copiar `templates/_seed.html`.
4. **Preencher com conteúdo real.** Nunca lorem, nunca métrica inventada.
5. **Rodar `checklist.md`.** Todo item P0 precisa passar, incluindo o "The Ramon Test".
6. **Exportar:** `node scripts/export.mjs <nome-do-template>`.

Precedência: **pedido do usuário > `surfaces.md` > `DESIGN.md` > `tokens.css`**.

## Não negociável

- **Preto e vermelho.** Só a paleta de `tokens.css`. Zero azul, zero ouro, zero terceira cor.
- **Acento em no máximo 2 aparições por peça.** Faixa de marquee vermelha, `.eyebrow--hot`, `.hairline--hot` e elemento de viz em vermelho contam como uma cada.
- **Um CTA primário.** Qualquer outra ação é `.cta-ghost` ou link de texto.
- **Texto nunca sobre o rosto.** Use `.split` (foto em banda, texto em banda sólida) ou `.split-h`. Foto sempre dentro de `.tint`; fundo claro exige `.tint--deep`.
- **Logo só a da Inteligência Comercial**, sempre dentro de `.plate` quando estiver sobre foto. A R7 não entra nas peças por padrão.
- **Viz é SVG escrito à mão**, preenchido. Zero biblioteca de gráfico.
- **Números canônicos:** +5.000 empresas · 110 turmas · +100 mil alunos · 408 mentorias · 14 anos. Nenhum outro.
- **Formato pt-BR:** `1.284` · `31,2%` · `R$ 12,4 mil`.
- **Limite de palavras:** ads 7 · quote card 18 · thumbnail 4.
- **Imagem local**, caminho relativo, proporção preservada. Nunca hotlink, nunca imagem gerada por IA para representar o Ramon.

## Camadas de atmosfera

São o que separa "limpo" de "caro". Nenhuma consome o orçamento do acento:
`.grain` (grão de impressão) · `.vignette` · `.frame` (moldura editorial com
marcas de canto) · `.meta-line` (carimbo de índice em mono) · `.tint`
(preto e branco com o vermelho por `mix-blend-mode`).

Aplicar as quatro primeiras em toda peça social. Documento impresso não usa
`.glow-blob`.

## Catálogo

| Categoria | Templates |
|---|---|
| Ads | `ad-1x1-metas` · `ad-4x5-follow-up` · `ad-9x16-rmv` · `ad-16x9-sic-ic` |
| Stories / Reels | `story-diagnostico` · `story-bastidor-imersao` · `reels-cover-follow-up` · `reels-cover-4-bases` |
| One-pagers | `onepager-a4-diagnostico` · `onepager-a4-proposta` · `onepager-a4-land-sumario` · `onepager-a4-relatorio-turma` |
| Infográficos | `info-processo-4-bases` · `info-funil-ampulheta` · `info-planejamento-modelo-olimpico` · `info-report-follow-up` |
| Quote cards | `quote-1x1-caixa-e-rei` · `quote-4x5-metas` · `quote-1x1-checklist-cadencias` · `quote-4x5-checklist-p3p3` |
| WhatsApp | `wa-profile-ramon` · `wa-profile-vendedor` · `wa-group-turma` · `wa-banner-1x1-turma` |
| YouTube | `yt-thumb-comercial-travou` · `yt-thumb-texto-puro-meta` · `yt-thumb-rico-follow-up` · `yt-thumb-rico-rmv` |

Vocabulário do método e números canônicos: `docs/guia-identidade.md`.
