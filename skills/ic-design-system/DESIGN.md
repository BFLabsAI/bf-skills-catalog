# Design System Ramon Pessoa / Inteligência Comercial

Sistema operado por **agentes CLI** (Claude Code, Codex, opencode).
Este arquivo descreve **como decidir**. `tokens.css` guarda **os valores**,
`brand-spec.md` a **origem medida** deles, `surfaces.md` as **restrições por
formato** e `checklist.md` o **gate antes de entregar**.

---

## Fluxo do agente

```
1. DESIGN.md      → regras de decisão
2. surfaces.md    → linha da superfície pedida (canvas, safe area, --scale)
3. copiar templates/_seed.html
4. preencher com conteúdo real
5. checklist.md   → todo P0 precisa passar
6. exportar PNG / PDF
```

Precedência: **pedido do usuário > surfaces.md > DESIGN.md > tokens.css**.

> O `guia-design-system-identidade.md` é a fonte de estratégia, método, voz e
> números canônicos. **A seção 6 dele (paleta e tipografia) está superada** pelos
> valores medidos nos ativos reais — ver `brand-spec.md`.

---

## Estrutura

```
ic-design-system/
├── SKILL.md         ← como o agente CLI aciona o sistema
├── README.md        ← instalação, export e publicação
├── DESIGN.md        ← regras de decisão
├── brand-spec.md    ← tokens medidos dos ativos
├── tokens.css       ← valores executáveis
├── surfaces.md      ← 7 categorias e suas restrições
├── checklist.md     ← P0 / P1 / P2 + The Ramon Test
├── index.html       ← vitrine com as 28 peças
├── templates/       ← 1 arquivo por variação + _layout.css + _seed.html
├── scripts/export.mjs  ← render em viewport = canvas
├── docs/            ← guia de identidade (método, voz, números)
└── assets/
    ├── fonts/       Archivo · Poppins · JetBrains Mono (locais, sem CDN)
    ├── logos/       originais da marca
    ├── derivadas/   variantes prontas (logo clara/escura, recortes)
    └── fotos/       banco otimizado, nome por enquadramento
```

---

## Cor

Seis tokens. Preto quente, branco, um vermelho. **Sem azul, sem ouro, sem
terceira cor.**

| Papel | Token | Regra |
|---|---|---|
| Canvas | `--bg` | Fundo de toda peça |
| Superfície | `--surface` | Card, faixa, bloco elevado |
| Borda | `--border` | Sempre 1px |
| Tinta principal | `--fg` | Manchete, número |
| Tinta de apoio | `--muted` | Corpo, legenda |
| Metadado | `--ink-low` | Crédito, data |
| Acento | `--accent` | **Máximo 2 aparições por peça** |

O orçamento padrão do vermelho é **ênfase da manchete + CTA**. Se a peça não
tem CTA, o vermelho pode ir para a tag de público. Nunca as três coisas.

---

## Tipografia

- **Display** — Archivo condensada (`wdth 70`, `wght 800`), **caixa alta**.
  Manchete e título. Nunca corpo longo.
- **Corpo** — Poppins. Texto, listas, CTA.
- **Mono** — JetBrains Mono. Eyebrow, número, tag técnica.

Ênfase da marca: a manchete quebra em duas linhas, **branca e vermelha**.
Esse é o recurso — não use negrito, sublinhado nem caixa colorida para o mesmo
fim.

Números sempre em `.metric`, formato pt-BR: `1.284` · `31,2%` · `R$ 12,4 mil`.

Para ajustar a peça inteira, mexer em `--scale`. Nunca em `--fs-*`.

---

## Regras duras

1. **Um acento, duas aparições.** A terceira é erro de entrega.
2. **Um CTA primário.** Qualquer outra ação é `.cta-ghost` ou texto.
3. **Contraste:** 4.5:1 no corpo, 3:1 em texto grande e ícone. Texto branco
   sobre `--accent` só a partir de 24px/600 — abaixo disso, inverta.
4. **Manchete de ads: máximo 7 palavras.** Quote card: 18. Thumbnail: 4.
5. **Sem órfã.** Nunca 1–2 palavras sozinhas na última linha.
6. **Nada fora da safe area.**
7. **Logo sempre em `.plate` sobre foto.** Nunca direto sobre imagem complexa.
8. **Foto sempre tratada:** `.photo-grade` + `.veil` sob todo texto.
9. **Marquee nunca corta palavra.** Repetição calculada, não overflow.
10. **Viz é SVG escrito à mão.** Preenchido, nunca só contorno. Zero biblioteca.
11. **Todo template exporta imagem ou PDF.** Peça de vídeo entrega a camada
    estática (cover, título, lower third), não o vídeo.
12. **Um arquivo, um canvas.** Exceto páginas de um mesmo documento.

---

## Marca

Usar **apenas a logo Inteligência Comercial**. A R7 Treinamentos não entra nas
peças por padrão.

| Arquivo | Uso |
|---|---|
| `assets/derivadas/ic-lockup-escuro.png` (1704×342) | **Padrão** — fundo escuro |
| `assets/derivadas/ic-lockup-claro.png` (1704×342) | Fundo claro, impresso |
| `assets/derivadas/ic-simbolo-escuro.png` (614×375) | Avatar, favicon, selo |
| `assets/derivadas/ic-simbolo-claro.png` (614×375) | Fundo claro |
| `assets/derivadas/ic-seta.png` (614×376) | Grafismo isolado |

Não redesenhar a marca. Não aplicar sobre foto sem `.plate`.

---

## Fotografia

| Arquivo em `assets/fotos/` | Enquadramento | Melhor uso |
|---|---|---|
| `retrato-serio-tijolo-01/02/03` | Retrato fechado, tijolo preto, olhar direto | Thumbnail, avatar, ads de dor |
| `retrato-sorriso-colete` | Sorriso aberto, colete | Comunidade, turma nova, tom acolhedor |
| `retrato-jaqueta-vermelha` | Jaqueta vermelha, fundo preto | Peça de marca — o vermelho já está na foto |
| `retrato-jaqueta-caramelo` | Jaqueta caramelo | **Uso restrito**: cor fora da paleta |
| `conquista-bracos-erguidos` | Grito, braços erguidos (paisagem) | RMV, meta batida, conquista |
| `convocacao-apontando` | Apontando para a câmera (fundo claro) | Convocação — exige `.tint--deep` |
| `palco-bracos-erguidos` | Palco, vertical | Story, 9:16 |
| `palco-gesticulando` | Palco lateral | 16:9, capas |
| `palco-apontando` | Palco, apontando | 16:9 |
| `palco-telao-pic` | Palco com o telão do PIC | Prova social |
| `palco-terno-claro` | Palco, terno claro | Vertical alternativo |
| `prova-aluno-trofeu-rmv` | Com aluno e troféu RMV | Case, prova social |
| `mentoria-perfil`, `mentoria-sala` | Sala de mentoria | Apoio, textura de fundo |

Todas em 2400px no maior lado — 2× o maior canvas do sistema.
Recortes prontos em `assets/derivadas/`: `ramon-rosto-serio-640`,
`ramon-rosto-sorriso-640`, `ramon-rosto-vermelho-640`.

**Tratamento obrigatório:** envolver em `.tint` (preto e branco + vermelho por
`mix-blend-mode`). Foto com **fundo claro** exige `.tint--deep`, senão o
resultado fica rosa.

---

## Voz

De empresário para empresário. Imperativo, direto, com dado. Frase curta.

Bordões canônicos: `Fala, empresário!` · `#BoraPraCima` · `O follow-up é rei.`
· `Faturamento é vaidade, lucro é sanidade, caixa é rei.` · `Preparação insana.`
· `Dois caminhos, uma decisão.`

Vocabulário do método, sempre grafado assim: **Programa Inteligência Comercial
(PIC)®** · **4 Bases** (Estruturando · Construindo · Otimizando · Controlando)
· **P3P3** · **Funil Ampulheta** · **Modelo Olímpico** · **RMV — Recorde
Mundial de Vendas** · **SIC × IC** · **Fauna Comercial**.

Números canônicos — **não usar outros**:
+5.000 empresas · 110 turmas · +100 mil alunos · 408 mentorias · 14 anos.

Evitar: "revolucionário", "transforme sua empresa", "solução inovadora",
"potencialize", promessa sem número, CAPS LOCK em frase inteira.

---

## Composição e saída

| Tipo de peça | Composição | Saída |
|---|---|---|
| Tipografia pura | HTML + CSS + SVG | PNG / PDF |
| Foto + texto | `<img>` local + `.photo-grade` + `.veil` | PNG |
| Camada para vídeo | `.canvas` com fundo transparente | PNG com alpha |
| Documento | HTML multi-página + `@media print` | PDF |

```bash
"$OD_NODE_BIN" "$OD_BIN" export design-system/templates/<arquivo>.html \
  --project "$OD_PROJECT_ID" --format image --out design-system/out/<nome>.png
```
