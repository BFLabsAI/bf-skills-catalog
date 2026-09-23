# Checklist de entrega — Design System Ramon Pessoa / IC

Rodar **antes** de exportar. Todo P0 precisa passar.

---

## P0 — bloqueia a entrega

**Estrutura**
- [ ] `.canvas` com as dimensões exatas da linha em `surfaces.md`.
- [ ] `--scale` correspondente à largura do canvas.
- [ ] Nada de conteúdo fora da safe area.
- [ ] Zero overflow: tudo cabe no canvas sem corte.
- [ ] Nenhuma sobreposição acidental.

**Cor**
- [ ] Nenhum literal de cor fora de `tokens.css`.
- [ ] Zero azul. Zero ouro. Zero terceira cor.
- [ ] `--accent` em no máximo **2 aparições**. Faixa de marquee vermelha e
      `.eyebrow--hot` contam como uma delas.
- [ ] Texto branco sobre `--accent` só a partir de 24px/600.
- [ ] Contraste: 4.5:1 no corpo, 3:1 em texto grande.

**Tipografia**
- [ ] Manchete em Archivo condensada, caixa alta.
- [ ] Corpo em Poppins. Mono só em eyebrow, número e tag.
- [ ] Ênfase feita pela quebra branca/vermelha — não por negrito ou caixa.
- [ ] Fonte acima do mínimo da superfície.
- [ ] Nenhuma linha final com 1–2 palavras órfãs.

**Conteúdo**
- [ ] Zero placeholder, lorem ou seção vazia.
- [ ] Números **canônicos**: +5.000 empresas · 110 turmas · +100 mil alunos ·
      408 mentorias · 14 anos. Nenhum número inventado.
- [ ] Formato pt-BR: `1.284` · `31,2%` · `R$ 12,4 mil`.
- [ ] Um único CTA primário.
- [ ] Limite de palavras: ads 7 · quote card 18 · thumbnail 4.

**Marca e imagem**
- [ ] Só a logo Inteligência Comercial. Variante correta para o fundo.
- [ ] Logo sobre foto sempre dentro de `.plate`.
- [ ] Foto com `.photo-grade`; `.veil` sob todo texto sobre imagem.
- [ ] Caminho relativo para `assets/`. Nenhum hotlink.
- [ ] Proporção intrínseca preservada; `width`/`height` declarados.
- [ ] `object-fit: cover` só em fundo decorativo.
- [ ] **Nada de `assets/_descartadas/`.**

---

## P1

- [ ] A peça abre com eyebrow.
- [ ] Espaçamento vindo da escala 4px.
- [ ] Card com borda + highlight, nunca sombra preta.
- [ ] No máximo um `.glow-blob`.
- [ ] Marquee com repetição calculada — nunca palavra cortada.
- [ ] Rosto não fica atrás do texto.
- [ ] Alinhamento óptico conferido acima de 60px.

---

## P2

- [ ] Nome de arquivo semântico: `<categoria>-<variação>-<assunto>.html`.
- [ ] Ritmo vertical consistente entre peças da mesma campanha.
- [ ] Versão em fundo claro conferida, se for impressa.

---

## Verificações por superfície

- **Ads 9:16 / Story** — 250px do topo e da base só com fundo.
- **Reels cover** — texto legível dentro do crop central 1080×1440.
- **One-pager** — quebra de página correta; sem `.glow-blob` no impresso.
- **Infográfico** — gráfico preenchido; máximo 7 etapas.
- **Quote card** — máximo 18 palavras; crédito presente.
- **WhatsApp profile/group** — conteúdo no círculo inscrito; reconhecível a 48px.
- **YouTube thumb** — canto inferior direito 140×60px livre; legível a 210px;
  máximo 4 palavras; fonte mínima 54px.

---

## The Ramon Test

Do guia canônico. Se qualquer item falhar, a peça não sai.

1. **Soa como Ramon Pessoa?** Direto, imperativo, de empresário para
   empresário, sem enrolação.
2. **Respeita a economia real?** Fala de vendas, caixa, equipe e lucro — não de
   fórmula mágica.
3. **Os números são os canônicos?**
4. **O PIC é protagonista?** 4 Bases, P3P3, Modelo Olímpico e RMV grafados
   corretamente.
5. **As diretrizes visuais estão preservadas?** Preto quente, um vermelho,
   Archivo + Poppins, logo em cápsula.
