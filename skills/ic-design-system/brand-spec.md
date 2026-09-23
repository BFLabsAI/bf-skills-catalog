# Brand Spec — Inteligência Comercial / Ramon Pessoa

Valores **medidos** dos ativos reais (logos e 12 criativos), não inferidos.

## Tokens

| Token | OKLch | Hex | Origem medida |
|---|---|---|---|
| `--bg` | `oklch(0.135 0.004 25)` | `#090707` | Fundo dos criativos 3, 12, 16 (`#080808` / `#080606` / `#030101`) — preto levemente quente |
| `--surface` | `oklch(0.215 0.008 25)` | `#151111` | Faixas e blocos elevados dos criativos |
| `--fg` | `oklch(1 0 0)` | `#FFFFFF` | Manchete e wordmark em fundo escuro |
| `--muted` | `oklch(0.745 0.007 25)` | `#B4ACAC` | Texto de apoio dos criativos |
| `--border` | `oklch(0.315 0.010 25)` | `#2E2626` | Filetes e molduras de 1px |
| `--accent` | `oklch(0.628 0.257 29.5)` | `#FF0A05` | **Vermelho exato da logo IC** (idêntico em 1.png, 3.png e 4.png) |

Sem azul. Sem ouro. Sem terceira cor.

## Tipografia

| Papel | Stack |
|---|---|
| Display | `"Archivo", "Archivo Narrow", "Helvetica Neue Condensed", Impact, sans-serif` — eixo variável `wdth 70 / wght 800–900`, caixa alta |
| Corpo | `"Poppins", system-ui, -apple-system, "Segoe UI", Arial, sans-serif` |
| Mono | `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace` |

Display e corpo são famílias diferentes. A condensada pesada em caixa alta é o
que dá a densidade das manchetes dos criativos; Poppins aparece no corpo e no
CTA, como nos criativos originais.

## Regras observadas nos ativos

1. **Fundo é preto quente, não navy nem preto puro.** As três amostras de fundo
   têm o canal vermelho acima do verde e do azul.
2. **A manchete quebra em duas cores:** linha branca + linha vermelha. É o
   recurso de ênfase padrão — substitui negrito, sublinhado e caixa colorida.
3. **O vermelho é sinal, não superfície.** Aparece na ênfase da manchete e no
   CTA. Quando aparece em três ou quatro blocos (criativo 7), a hierarquia
   colapsa — o sistema limita a duas aparições.
4. **A logo IC tem duas versões:** o "C" em preto sobre fundo claro e em branco
   sobre fundo escuro, com a seta sempre vermelha. Ambas em `assets/derivadas/`.
5. **Foto é sempre tratada:** dessaturada ou com viés vermelho, sob véu escuro,
   nunca crua sob o texto.

## Resumo

Preto quente como canvas, branco para a manchete, um único vermelho `#FF0A05`
usado no máximo duas vezes por peça, tipografia condensada pesada em caixa alta
sobre corpo geométrico.
