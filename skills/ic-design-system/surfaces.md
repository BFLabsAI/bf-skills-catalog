# Superfícies — Design System Ramon Pessoa

Cada superfície declara: **canvas**, **safe area**, **`--scale`**, **fonte mínima**,
**densidade máxima** e **primitivos permitidos**. O agente não improvisa dimensão:
ele lê a linha da tabela e aplica.

Regra geral: `1 template = 1 arquivo HTML = 1 canvas = 1 export`.
Arquivo em `templates/<categoria>-<variação>.html`.

---

## 1. Ads

Peça de tráfego pago. Uma promessa, um CTA, zero decoração.

| Variação | Canvas | `--scale` | Safe area | Fonte mín. | Uso |
|---|---|---|---|---|---|
| `ad-1x1`  | 1080 × 1080 | 1.00 | 80px | 32px | Feed IG/FB, display |
| `ad-4x5`  | 1080 × 1350 | 1.00 | 88px | 32px | Feed IG (maior área) |
| `ad-9x16` | 1080 × 1920 | 1.00 | 96px topo/base 220px | 36px | Stories, Reels ad |
| `ad-16x9` | 1920 × 1080 | 1.60 | 120px | 32px | YouTube, display web |

Restrições:
- Máximo **7 palavras** na headline. Se não cabe, o conceito está errado, não a fonte.
- **1 CTA**, sempre no mesmo canto por variação (inferior esquerdo).
- Em `9:16`, os 220px do topo e da base são zona morta (UI do app cobre) — só fundo.
- Texto sobre foto exige `.veil`. Nunca texto direto sobre imagem crua.
- Acento: 2 aparições no máximo (ex.: CTA + um destaque na headline).

---

## 2. Stories & Reels covers

| Variação | Canvas | `--scale` | Safe area | Fonte mín. | Observação |
|---|---|---|---|---|---|
| `story` | 1080 × 1920 | 1.00 | 96px / 250px topo e base | 36px | Sticker, enquete e link ficam nas bordas |
| `reels-cover` | 1080 × 1920 | 1.00 | 96px | 40px | **Crop do grid: 1080 × 1440 centralizado** |

Restrições:
- Em `reels-cover`, todo o texto legível **precisa caber no crop central 1080×1440**.
  Fora dele só entra fundo e extensão de imagem.
- Cover é camada estática sobre vídeo: exporta PNG. O design system **não gera vídeo**.
- Título de cover: máximo 4 palavras, peso display, alto contraste — é lido em 120px de largura na grade do perfil.

---

## 3. One-pagers (PDF, impresso, documento)

| Variação | Canvas | `--scale` | Margem | Fonte mín. | Uso |
|---|---|---|---|---|---|
| `onepager-a4`      | 794 × 1123 px (A4 @96dpi) | 0.34 | 18mm ≈ 68px | 12pt ≈ 16px | Proposta, relatório |
| `onepager-a4-land` | 1123 × 794 px | 0.34 | 18mm | 12pt | Sumário executivo |
| `onepager-carta`   | 816 × 1056 px | 0.34 | 0.75in ≈ 72px | 12pt | Mercado US |

Restrições:
- Documento é **multi-página**: cada página é um `.canvas` empilhado no mesmo arquivo, com `page-break-after: always` no `@media print`.
- Cabeçalho e rodapé fixos com número de página. Rodapé nunca colide com a margem.
- Modo impressão: verificar se a versão em **fundo claro** é obrigatória (economia de tinta). Se sim, usar o token `--canvas` invertido declarado no template, não hex solto.
- Nada de `--glow` em peça impressa: não reproduz em papel.

---

## 4. Infográficos

| Variação | Canvas | `--scale` | Safe area | Uso |
|---|---|---|---|---|
| `info-social` | 1080 × altura livre (máx. 4320) | 1.00 | 88px | Lead magnet, post longo |
| `info-web`    | 1200 × altura livre | 1.10 | 96px | Blog, embed |
| `info-print`  | 794 × 1123 (A4) | 0.34 | 68px | Report em PDF |

Tipos internos: **processo** (etapas ligadas), **planejamento** (linha do tempo/grade),
**report** (métricas + evidência), **lead magnet** (framework de 1 tela).

Restrições:
- **Toda visualização é SVG escrito à mão.** Nenhuma biblioteca de gráfico.
- Gráfico tem preenchimento — nunca só contorno.
- Conexões e setas usam `--connect` (ciano). Nunca `--accent`.
- Números em `.metric`, formatação pt-BR: `1.284` · `31,2%` · `R$ 12,4 mil`.
- Máximo **7 etapas** por infográfico de processo. Acima disso, quebrar em dois.

---

## 5. Quote cards

| Variação | Canvas | `--scale` | Safe area | Fonte mín. |
|---|---|---|---|---|
| `quote-1x1` | 1080 × 1080 | 1.00 | 96px | 40px |
| `quote-4x5` | 1080 × 1350 | 1.00 | 96px | 40px |

Tipos internos: **frase de impacto** (uma sentença, tipografia dominante) e
**checklist** (3 a 6 itens curtos com marcador).

Restrições:
- Frase: máximo **18 palavras**. A tipografia é o design — sem card, sem moldura, sem aspas decorativas gigantes.
- Checklist: itens de no máximo 6 palavras, todos com a mesma estrutura gramatical.
- Crédito (nome + cargo) em `.caption`, sempre no mesmo canto.
- Zero foto de fundo por padrão. Se houver, `.veil` obrigatório.

---

## 6. WhatsApp Media

| Variação | Canvas | `--scale` | Safe area | Observação |
|---|---|---|---|---|
| `wa-profile` | 640 × 640 | 0.60 | **círculo inscrito** | Recorte circular — canto é descartado |
| `wa-group`   | 640 × 640 | 0.60 | círculo inscrito | Idem |
| `wa-banner`  | 1080 × 1920 | 1.00 | 96px / 250px | Status |
| `wa-link`    | 1200 × 630 | 1.10 | 64px | Preview de link (OG) |

Restrições:
- `wa-profile` e `wa-group` são **recortados em círculo**. Todo conteúdo deve caber
  no círculo de diâmetro 640 centralizado — na prática, num quadrado de 452px no centro.
- Foto de pessoa (time, vendedor): rosto centralizado, olhos na linha de 40% do topo,
  moldura de 1px em `--border` e fundo `--surface` uniforme para o time inteiro parecer um conjunto.
- Legibilidade real: o avatar aparece a **48px** na lista de conversas. Se o elemento não é reconhecível a 48px, não existe. Sem texto além de 1–2 iniciais.

---

## 7. Thumbnail de YouTube

Canvas único: **1280 × 720**, `--scale: 1.05`, safe area 64px.

| Variação | Composição |
|---|---|
| `yt-texto-imagem` | Foto/rosto + bloco de texto — a mais usada |
| `yt-html-puro`    | Só tipografia e formas, sem foto |
| `yt-html-rico`    | Foto + camada gráfica (SVG, métrica, moldura, elemento de UI) |

Restrições:
- **Fonte mínima 54px.** A thumb é vista a 210px de largura no mobile — teste mental: se não lê a 210px, refaça.
- Máximo **4 palavras**. Contraste alto, uma cor de acento.
- **Canto inferior direito: 140 × 60px reservado** para o timestamp do YouTube. Nada ali.
- Rosto (quando houver) ocupa 30–45% da largura, alinhado a uma das laterais, nunca centralizado atrás do texto.
- Sem borda arredondada: o YouTube aplica a dele.

---

## Tabela-resumo de `--scale`

| Largura do canvas | `--scale` |
|---|---|
| 640  | 0.60 |
| 794 (A4) | 0.34 |
| 1080 | 1.00 |
| 1200 | 1.10 |
| 1280 | 1.05 |
| 1920 | 1.60 |

O `--scale` normaliza a escala tipográfica para que a mesma hierarquia visual
apareça em qualquer canvas. O agente define `--scale` no `.canvas` e **não toca
nos valores de `--fs-*`**.

---

## Mapa dos templates

| Categoria | Arquivo | Superfície |
|---|---|---|
| Ads | `ad-1x1-metas.html` | 1080 × 1080 |
| Ads | `ad-4x5-follow-up.html` | 1080 × 1350 |
| Ads | `ad-9x16-rmv.html` | 1080 × 1920 |
| Ads | `ad-16x9-sic-ic.html` | 1920 × 1080 |
| Stories / Reels | `story-diagnostico.html` | 1080 × 1920 |
| Stories / Reels | `story-bastidor-imersao.html` | 1080 × 1920 |
| Stories / Reels | `reels-cover-follow-up.html` | 1080 × 1920 · crop 1080 × 1440 |
| Stories / Reels | `reels-cover-4-bases.html` | 1080 × 1920 · crop 1080 × 1440 |
| One-pagers | `onepager-a4-diagnostico.html` | A4 794 × 1123 |
| One-pagers | `onepager-a4-proposta.html` | A4 794 × 1123 |
| One-pagers | `onepager-a4-land-sumario.html` | A4 paisagem 1123 × 794 |
| One-pagers | `onepager-a4-relatorio-turma.html` | A4 · 2 páginas |
| Infográficos | `info-processo-4-bases.html` | 1080 × altura livre |
| Infográficos | `info-funil-ampulheta.html` | 1080 × altura livre |
| Infográficos | `info-planejamento-modelo-olimpico.html` | 1080 × altura livre |
| Infográficos | `info-report-follow-up.html` | 1080 × altura livre |
| Quote cards | `quote-1x1-caixa-e-rei.html` | 1080 × 1080 |
| Quote cards | `quote-4x5-metas.html` | 1080 × 1350 |
| Quote cards | `quote-1x1-checklist-cadencias.html` | 1080 × 1080 |
| Quote cards | `quote-4x5-checklist-p3p3.html` | 1080 × 1350 |
| WhatsApp | `wa-profile-ramon.html` | 640 × 640 circular |
| WhatsApp | `wa-profile-vendedor.html` | 640 × 640 circular |
| WhatsApp | `wa-group-turma.html` | 640 × 640 circular |
| WhatsApp | `wa-banner-1x1-turma.html` | 1080 × 1080 |
| YouTube | `yt-thumb-comercial-travou.html` | 1280 × 720 · texto + imagem |
| YouTube | `yt-thumb-texto-puro-meta.html` | 1280 × 720 · só HTML |
| YouTube | `yt-thumb-rico-follow-up.html` | 1280 × 720 · HTML rico + imagem |
| YouTube | `yt-thumb-rico-rmv.html` | 1280 × 720 · HTML rico + imagem |

Todos importam `../tokens.css`, `_layout.css` e `../assets/fonts/fonts.css`.
`index.html` na raiz lista as 28 peças com link.

Export: `npm run export` renderiza tudo com o viewport igual ao canvas.
